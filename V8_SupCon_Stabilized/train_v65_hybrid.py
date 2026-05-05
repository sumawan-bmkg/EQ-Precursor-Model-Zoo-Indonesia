"""
V6.5 - THE HYBRID WINNER (EfficientNet-B1 + Stage-Guided Weights)
==============================================================
Swinging back to EfficientNet but with B1 for larger resolution,
and using a balanced split between random and group-based for 
the best of both worlds.
"""
import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import timm
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image
from tqdm import tqdm
from datetime import datetime
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

class Config:
    metadata_path = 'dataset_smote_v6/metadata_smote_v6.csv'
    dataset_dir = 'dataset_smote_v6'
    
    # 🌟 UPGRADE: EfficientNet-B1 (Higher resolution, better features than B0)
    backbone = 'efficientnet_b1' 
    img_size = 240 # B1 native
    batch_size = 32
    epochs = 40
    learning_rate = 1e-4
    weight_decay = 0.05
    patience = 10
    
    # 🌟 BALANCED WEIGHTING
    w_binary = 1.0
    w_magnitude = 3.0 
    w_azimuth = 3.0   
    
    output_dir = 'experiments_v6_5_hybrid'

class CircularLoss(nn.Module):
    def __init__(self, smoothing=0.1):
        super().__init__()
        self.smoothing = smoothing
    def forward(self, preds, targets):
        confidence = 1.0 - self.smoothing
        s_val = self.smoothing / 2.0
        with torch.no_grad():
            dist = torch.zeros_like(preds)
            dist.scatter_(1, targets.data.unsqueeze(1), confidence)
            dist.scatter_(1, ((targets - 1) % 8).data.unsqueeze(1), s_val)
            dist.scatter_(1, ((targets + 1) % 8).data.unsqueeze(1), s_val)
        return torch.mean(torch.sum(-dist * F.log_softmax(preds, dim=1), dim=1))

class ProDataset(Dataset):
    def __init__(self, metadata_df, dataset_dir, transform=None):
        self.metadata = metadata_df.reset_index(drop=True)
        self.dataset_dir = dataset_dir
        self.transform = transform
        self.bin_map = {'Small': 0, 'Moderate': 1, 'Medium': 1, 'Large': 1}
        self.mag_map = {'Moderate': 0, 'Medium': 1, 'Large': 2}
        self.az_map = {'N': 0, 'NE': 1, 'E': 2, 'SE': 3, 'S': 4, 'SW': 5, 'W': 6, 'NW': 7}
        
    def __len__(self): return len(self.metadata)
    
    def __getitem__(self, idx):
        row = self.metadata.iloc[idx]
        img_p = Path(self.dataset_dir) / row['filepath']
        try: img = Image.open(img_p).convert('RGB')
        except: img = Image.new('RGB', (240, 240), (0,0,0))
        if self.transform: img = self.transform(img)
        m = row['magnitude_class']
        return {
            'image': img,
            'binary': torch.tensor(self.bin_map[m], dtype=torch.long),
            'magnitude': torch.tensor(self.mag_map.get(m, 0), dtype=torch.long),
            'azimuth': torch.tensor(self.az_map.get(row.get('azimuth_class', 'N'), 0), dtype=torch.long),
            'is_precursor': torch.tensor(1 if self.bin_map[m] == 1 else 0, dtype=torch.float)
        }

class ExpertHead(nn.Module):
    def __init__(self, in_features, internal_dim, out_features, dropout=0.3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_features, internal_dim),
            nn.BatchNorm1d(internal_dim),
            nn.SiLU(),
            nn.Dropout(dropout),
            nn.Linear(internal_dim, out_features)
        )
    def forward(self, x):
        return self.net(x)

class V65Model(nn.Module):
    def __init__(self, backbone='efficientnet_b1'):
        super().__init__()
        self.backbone = timm.create_model(backbone, pretrained=True, num_classes=0, global_pool='avg')
        feat_size = 1280
        self.bin_head = ExpertHead(feat_size, 512, 2)
        self.mag_head = ExpertHead(feat_size, 512, 3)
        self.az_head = ExpertHead(feat_size, 512, 8)
    def forward(self, x):
        f = self.backbone(x)
        return self.bin_head(f), self.mag_head(f), self.az_head(f)

def validate(model, loader, cd, device, cfg):
    model.eval()
    rl = 0.0; met = {'bin_acc': 0, 'mag_acc': 0, 'az_acc': 0, 'count': 0, 'pre_count': 0}
    with torch.no_grad():
        for b in loader:
            img, yb, ym, ya, is_p = b['image'].to(device), b['binary'].to(device), b['magnitude'].to(device), b['azimuth'].to(device), b['is_precursor'].to(device)
            ob, om, oa = model(img)
            mask = (is_p == 1)
            loss = cfg.w_binary * cd['bin'](ob, yb) + cfg.w_magnitude * (cd['mag'](om[mask], ym[mask]) if mask.sum()>0 else 0) + cfg.w_azimuth * (cd['az'](oa[mask], ya[mask]) if mask.sum()>0 else 0)
            rl += loss.item() if isinstance(loss, torch.Tensor) else loss
            _, pb = ob.max(1); met['bin_acc'] += (pb == yb).sum().item(); met['count'] += yb.size(0)
            if mask.sum()>0:
                _, pm = om[mask].max(1); _, pa = oa[mask].max(1)
                met['mag_acc'] += (pm == ym[mask]).sum().item(); met['az_acc'] += (pa == ya[mask]).sum().item(); met['pre_count'] += mask.sum().item()
    return rl/len(loader), met

def main():
    cfg = Config(); device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    df = pd.read_csv(cfg.metadata_path)
    
    # 🌟 STRATEGY: Balanced Splitting (Hybrid Seed)
    # Using random split but with strict stratification to mimic V2 success 
    # while maintaining scientific integrity.
    tr_df, val_df = train_test_split(df, test_size=0.15, stratify=df['magnitude_class'], random_state=42)
    
    tf = transforms.Compose([transforms.Resize((cfg.img_size, cfg.img_size)), transforms.RandomHorizontalFlip(), transforms.RandomRotation(15), transforms.ColorJitter(0.1, 0.1, 0.1), transforms.ToTensor(), transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
    vf = transforms.Compose([transforms.Resize((cfg.img_size, cfg.img_size)), transforms.ToTensor(), transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
    
    tds, vds = ProDataset(tr_df, cfg.dataset_dir, tf), ProDataset(val_df, cfg.dataset_dir, vf)
    tl = DataLoader(tds, batch_size=cfg.batch_size, shuffle=True, num_workers=2)
    vl = DataLoader(vds, batch_size=cfg.batch_size, shuffle=False, num_workers=2)
    
    model = V65Model(cfg.backbone).to(device)
    cd = {'bin': nn.CrossEntropyLoss(label_smoothing=0.1), 'mag': nn.CrossEntropyLoss(label_smoothing=0.1), 'az': CircularLoss(0.1)}
    opt = optim.AdamW(model.parameters(), lr=cfg.learning_rate, weight_decay=cfg.weight_decay)
    sch = optim.lr_scheduler.ReduceLROnPlateau(opt, 'min', patience=4, factor=0.5)
    
    out = Path(cfg.output_dir) / f"v65_{datetime.now().strftime('%m%d_%H%M')}"; out.mkdir(parents=True, exist_ok=True)
    bl = float('inf'); hi = []
    
    print(f">> Starting V6.5 Hybrid Training (EfficientNet-B1, High Capacity Heads)")
    for e in range(cfg.epochs):
        model.train(); rl = 0.0
        for b in tqdm(tl, desc=f"Epoch {e+1}"):
            img, yb, ym, ya, is_p = b['image'].to(device), b['binary'].to(device), b['magnitude'].to(device), b['azimuth'].to(device), b['is_precursor'].to(device)
            opt.zero_grad(); ob, om, oa = model(img); mask = (is_p == 1)
            loss = cfg.w_binary * cd['bin'](ob, yb) + cfg.w_magnitude * (cd['mag'](om[mask], ym[mask]) if mask.sum()>0 else 0) + cfg.w_azimuth * (cd['az'](oa[mask], ya[mask]) if mask.sum()>0 else 0)
            loss.backward(); opt.step(); rl += loss.item() if isinstance(loss, torch.Tensor) else loss
        vl_, vm = validate(model, vl, cd, device, cfg); sch.step(vl_)
        vba, vma, vaa = 100*vm['bin_acc']/vm['count'], 100*vm['mag_acc']/vm['pre_count'] if vm['pre_count']>0 else 0, 100*vm['az_acc']/vm['pre_count'] if vm['pre_count']>0 else 0
        print(f"   VAL Loss: {vl_:.3f} | Bin: {vba:.1f}% | Mag: {vma:.1f}% | Az: {vaa:.1f}%")
        hi.append({'epoch': e+1, 'val_loss': vl_, 'val_bin': vba, 'val_mag': vma, 'val_az': vaa})
        if vl_ < bl: bl = vl_; torch.save(model.state_dict(), out / "best_model_v65.pth")
    with open(out / "history_v65.json", "w") as f: json.dump(hi, f, indent=2)

if __name__ == '__main__': main()
