import os
import sys
import re
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import warnings

warnings.filterwarnings('ignore')

# Add paths
sys.path.insert(0, str(Path(__file__).parent / 'dataset_scalogram' / 'src'))
sys.path.append(str(Path(__file__).parent))

try:
    from scalogram_generator_v6 import ScalogramGeneratorV6
except ImportError:
    print("ERROR: Cannot import ScalogramGeneratorV6 from dataset_scalogram/src")
    sys.exit(1)

try:
    from generate_scalogram_from_dataset import read_binary_scn
except ImportError:
    print("ERROR: Cannot import read_binary_scn from generate_scalogram_from_dataset.py")
    sys.exit(1)

try:
    from intial.geomagnetic_fetcher_dual_format import GeomagneticDataFetcherDual
except ImportError:
    print("WARNING: Cannot import GeomagneticDataFetcherDual. SSH fallback will be disabled.")
    GeomagneticDataFetcherDual = None

# SSH Configuration
SSH_CONFIG = {
    'host': '202.90.198.224',
    'port': 4343,
    'username': 'precursor',
    'password': 'otomatismon',
    'data_path': '/home/precursor/SEISMO/DATA'
}

class PreprocessorV6:
    def __init__(self, output_dir='dataset_scalogram/processed_v6', local_path='mdata2'):
        self.output_dir = Path(output_dir)
        self.local_path = Path(local_path)
        self.generator = ScalogramGeneratorV6()
        
        # SSH Fetcher
        self.ssh_fetcher = None
        if GeomagneticDataFetcherDual:
            self.ssh_fetcher = GeomagneticDataFetcherDual(ssh_config=SSH_CONFIG)
            self.ssh_connected = False
        
        # Structure for Stage 1 Training (Standard subfolders)
        self.subdirs = {
            'train': 'stage1_train',
            'val': 'val_test',
            'test': 'val_test'
        }
        for sub in self.subdirs.values():
            for cls in ['Event', 'Normal']:
                (self.output_dir / sub / cls).mkdir(parents=True, exist_ok=True)
                
        self.report_path = self.output_dir / 'v6_processing_report.csv'
        print(f"PreprocessorV6 Initialized. Output: {output_dir}")

    def parse_v5_filename(self, filename):
        """Extract station, date, hour from V5 filenames."""
        clean_name = filename.replace('.png', '').replace('.npy', '')
        
        # Remove standard prefixes
        prefixes = ['AUG_ROT_E_', 'AUG_ROT_NW_', 'AUG_ROT_N_', 'AUG_ROT_SW_', 'AUG_ROT_S_', 'AUG_ROT_W_', 'SMOTE_AUG_', 'SMOTE_', 'AUG_']
        for p in prefixes:
            if clean_name.startswith(p):
                clean_name = clean_name[len(p):]
        
        parts = clean_name.split('_')
        if len(parts) < 3: return None
        
        station = parts[0]
        date_str = parts[1]
        
        # Hour extraction (Hnn)
        hour_match = re.search(r'H(\d+)', parts[2])
        if hour_match:
            hour = int(hour_match.group(1))
        else:
            # Fallback for old formats like station_YYYYMMDD_HH
            try: hour = int(parts[2])
            except: return None
            
        return {'station': station, 'date': date_str, 'hour': hour}

    def fetch_raw_data(self, station, date, hour):
        """Fetch raw 1-hour slice from local SCN.gz files or SSH fallback."""
        data = self._fetch_local(station, date, hour)
        if data:
            return data
            
        return self._fetch_ssh(station, date, hour)

    def _fetch_local(self, station, date, hour):
        try:
            d_obj = pd.to_datetime(date)
            yymmdd = d_obj.strftime('%y%m%d')
            scn_file = self.local_path / station / f"S{yymmdd}.{station}.gz"
            if not scn_file.exists(): return None
            
            full_day_data = read_binary_scn(str(scn_file), station)
            if not full_day_data: return None
            
            start, end = hour * 3600, (hour + 1) * 3600
            if len(full_day_data['h']) < end: return None
                
            return {
                'h': full_day_data['h'][start:end],
                'd': full_day_data['d'][start:end],
                'z': full_day_data['z'][start:end]
            }
        except: return None

    def _fetch_ssh(self, station, date, hour):
        if not self.ssh_fetcher: return None
        if not self.ssh_connected:
            print(f"Connecting to SSH {SSH_CONFIG['host']}...")
            if self.ssh_fetcher.connect(): 
                self.ssh_connected = True
                print("SSH Connected Success.")
            else: 
                print("SSH Connection FAILED.")
                return None
            
        try:
            # Convert YYYYMMDD to YYYY-MM-DD for SSH fetcher
            if len(str(date)) == 8 and '-' not in str(date):
                date_iso = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
            else:
                date_iso = date
                
            data = self.ssh_fetcher.fetch_data(date_iso, station)
            if data:
                start, end = hour * 3600, (hour + 1) * 3600
                return {
                    'h': data['Hcomp'][start:end],
                    'd': data['Dcomp'][start:end],
                    'z': data['Zcomp'][start:end]
                }
            else:
                print(f"SSH: Data not found for {station} on {date}")
            return None
        except Exception as e:
            print(f"SSH Error fetching {station} {date}: {str(e)}")
            return None

    def process_split(self, metadata_path, split_name, limit=None):
        df = pd.read_csv(metadata_path)
        if limit: df = df.head(limit)
        
        print(f"\nProcessing {split_name} split ({len(df)} samples)...")
        results = []
        
        for i, row in tqdm(df.iterrows(), total=len(df)):
            filename = row['file']
            label = row['label'] # 'Precursor' or 'Normal'
            cls_folder = 'Event' if label == 'Precursor' else 'Normal'
            
            meta = self.parse_v5_filename(filename)
            if not meta:
                results.append({'file': filename, 'status': 'failed', 'reason': 'parse_error'})
                continue
                
            raw_data = self.fetch_raw_data(meta['station'], meta['date'], meta['hour'])
            if not raw_data:
                results.append({'file': filename, 'status': 'failed', 'reason': 'data_not_found'})
                continue
                
            # Generate V6
            try:
                rgb = self.generator.generate_rgb(raw_data['h'], raw_data['d'], raw_data['z'])
                
                # Save as .npy in standardized subfolder
                out_name = filename.replace('.png', '').replace('.npy', '') + '.npy'
                standard_sub = self.subdirs.get(split_name, 'val_test')
                out_path = self.output_dir / standard_sub / cls_folder / out_name
                np.save(out_path, rgb)
                
                results.append({'file': filename, 'status': 'success', 'v6_path': str(out_path)})
            except Exception as e:
                results.append({'file': filename, 'status': 'failed', 'reason': str(e)})
                
        return pd.DataFrame(results)

    def run_full_migration(self, limit_per_split=None):
        meta_base = Path('dataset_scalogram/v5_hierarchical/metadata')
        splits = {
            'train': meta_base / 'split_train.csv',
            'val': meta_base / 'split_val.csv',
            'test': meta_base / 'split_test.csv'
        }
        
        all_reports = []
        for name, path in splits.items():
            if path.exists():
                report = self.process_split(path, name, limit=limit_per_split)
                all_reports.append(report)
        
        final_report = pd.concat(all_reports)
        final_report.to_csv(self.report_path, index=False)
        print(f"\nMigration Complete. Report saved to {self.report_path}")
        print(final_report['status'].value_counts())

if __name__ == "__main__":
    pre = PreprocessorV6()
    # Run full migration (no limit)
    pre.run_full_migration()
