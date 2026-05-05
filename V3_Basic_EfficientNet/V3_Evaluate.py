import torch
import numpy as np
import os
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from V3_Model import MultiTaskScalogramV3

def run_blind_test_v3(checkpoint_path, data_dir, cosmic_csv, output_report):
    """
    Evaluasi ScalogramV3 pada data Blind-Test 2026.
    Injeksi Kp/Dst dilakukan secara on-the-fly untuk setiap tensor .npy.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Starting V3 Blind-Test Audit on: {device}")
    
    # 1. Load Cosmic Data
    cosmic_df = pd.read_csv(cosmic_csv)
    cosmic_df['Date_Time_UTC'] = pd.to_datetime(cosmic_df['Date_Time_UTC'])
    cosmic_df['Date_Only'] = cosmic_df['Date_Time_UTC'].dt.strftime('%Y%m%d')
    daily_cosmic = cosmic_df.groupby('Date_Only').agg({'Kp_Index': 'max', 'Dst_Index': 'min'}).to_dict('index')
    
    # 2. Load Model
    model = MultiTaskScalogramV3(pretrained=False).to(device)
    if os.path.exists(checkpoint_path):
        model.load_state_dict(torch.load(checkpoint_path, map_location=device))
        print(f"Loaded weights from {checkpoint_path}")
    else:
        print("Warning: Running with UNTRAINED weights (Dry Run)")
        
    model.eval()
    
    # 3. Process Files
    files = sorted([f for f in os.listdir(data_dir) if f.endswith('.npy')])
    results = []
    
    print(f"Evaluating {len(files)} files in {data_dir}...")
    with torch.no_grad():
        for filename in tqdm(files):
            filepath = os.path.join(data_dir, filename)
            
            # Extract Date: event_ALR_20250824.npy -> 20250824
            date_str = filename.split('_')[-1].split('.')[0]
            cos_vals = daily_cosmic.get(date_str, {'Kp_Index': 0.0, 'Dst_Index': 0.0})
            
            # Normalize cosmic
            kp_feat = cos_vals['Kp_Index'] / 9.0
            dst_feat = cos_vals['Dst_Index'] / 100.0
            cosmic_tensor = torch.tensor([[kp_feat, dst_feat]]).float().to(device)
            
            # Load Tensor
            tensor = torch.from_numpy(np.load(filepath)).float().unsqueeze(0).to(device)
            
            # Inference
            out_det, out_mag, out_azm = model(tensor, cosmic_tensor)
            
            # Results
            prob_event = torch.softmax(out_det, dim=1)[0][1].item()
            pred_mag = torch.argmax(out_mag, dim=1).item()
            pred_azm = out_azm[0].cpu().numpy() # [sin, cos]
            
            results.append({
                'filename': filename,
                'prob_seismic': prob_event,
                'kp': cos_vals['Kp_Index'],
                'dst': cos_vals['Dst_Index'],
                'pred_mag': pred_mag,
                'is_alert': 1 if prob_event > 0.85 else 0
            })
            
    # 4. Save Report
    report_df = pd.DataFrame(results)
    report_df.to_csv(output_report, index=False)
    print(f"Audit Complete. Results saved to: {output_report}")
    
    # Quick Statistics
    total_alerts = report_df['is_alert'].sum()
    print(f"Total ScalogramV3 Alerts Generated: {total_alerts}")

if __name__ == "__main__":
    WORKSPACE = r"d:\multi\scalogramv3"
    CHECKPOINT = os.path.join(WORKSPACE, "checkpoints", "v3_fusion_best.pth")
    BLIND_DATA = r"d:\multi\scalogramv2\processed_tensors_v2\val\anomali" # Using val as proxy for 2026
    COSMIC_CSV = os.path.join(WORKSPACE, "cosmic_features_v3.csv")
    
    run_blind_test_v3(CHECKPOINT, BLIND_DATA, COSMIC_CSV, "v3_blind_test_report.csv")
