
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import pandas as pd
import numpy as np
from tqdm import tqdm
from datetime import datetime

from dataset_scalogram.src.data_loader import ScalogramDataset
from dataset_scalogram.src.model_scalogram import get_model

# ============================================================================
# TRAIN V6 CONFIG
# ============================================================================

class ConfigV6:
    data_dir = 'dataset_scalogram/processed_v6' 
    metadata_dir = 'dataset_scalogram/processed_v6/metadata' 
    
    # Recommendations Implementation
    backbone = 'swin_tiny_patch4_window7_224'
    batch_size = 2 # Keep 2 for 2GB VRAM stability
    lr = 5e-5       
    epochs = 30     # Full run
    
    # Recommendation 4: Cost-Sensitive Weight
    pos_weight = 3.0 
    
    save_dir = 'models/scalogram_v6_final'
    device_idx = 1 # Quadro K620 with more free VRAM

def train_v6():
    cfg = ConfigV6()
    device = torch.device(f'cuda:{cfg.device_idx}' if torch.cuda.is_available() else 'cpu')
    os.makedirs(cfg.save_dir, exist_ok=True)
    
    print(f"--- STARTING STAGE 1 V6 TRAINING (Goal: >90%) ---")
    print(f"Backbone: {cfg.backbone}")
    print(f"Cost-Sensitive Weight (Pos): {cfg.pos_weight}")
    
    # 1. Dataset with Kp-index
    # Note: Kp-index is handled inside ScalogramDataset now.
    train_ds = ScalogramDataset(cfg.data_dir, os.path.join(cfg.metadata_dir, 'split_train_v6.csv'), stage='stage1')
    val_ds = ScalogramDataset(cfg.data_dir, os.path.join(cfg.metadata_dir, 'split_val_v6.csv'), stage='stage1')
    
    # num_workers=0 is safer for Windows multi-threading issues in some envs
    train_loader = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=cfg.batch_size, shuffle=False, num_workers=0)
    
    # 2. Model (Swin + Multi-Modal Head)
    model = get_model('stage1_v6', backend=cfg.backbone).to(device)
    
    # 3. Loss (BCEWithLogitsLoss with pos_weight)
    # Target 1 (Precursor) is 3x more important than Target 0 (Normal)
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([cfg.pos_weight]).to(device))
    
    optimizer = optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=0.05)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg.epochs)
    
    best_f1 = 0
    
    for epoch in range(cfg.epochs):
        model.train()
        train_loss = 0
        
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}")
        for images, labels, kp, _ in pbar:
            images, labels, kp = images.to(device), labels.to(device).float(), kp.to(device)
            
            optimizer.zero_grad()
            outputs = model(images, kp).squeeze()
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            pbar.set_postfix({'loss': f'{loss.item():.4f}'})
            
        # Validation
        model.eval()
        val_preds = []
        val_labels = []
        
        with torch.no_grad():
            for images, labels, kp, _ in val_loader:
                images, labels, kp = images.to(device), labels.to(device).float(), kp.to(device)
                outputs = model(images, kp).squeeze()
                
                probs = torch.sigmoid(outputs)
                preds = (probs > 0.5).int()
                
                val_preds.extend(preds.cpu().numpy())
                val_labels.extend(labels.cpu().numpy())
                
        # Calculate Metrics
        from sklearn.metrics import f1_score, accuracy_score, recall_score
        f1 = f1_score(val_labels, val_preds)
        acc = accuracy_score(val_labels, val_preds)
        rec = recall_score(val_labels, val_preds)
        
        print(f"  Val Acc: {acc:.4f}, Val F1: {f1:.4f}, Val Recall (Precursor): {rec:.4f}")
        
        scheduler.step()
        
        if f1 > best_f1:
            best_f1 = f1
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'metrics': {'f1': f1, 'acc': acc, 'recall': rec}
            }, os.path.join(cfg.save_dir, 'best_model_v6.pth'))
            print(f"  [SAVED] New Best F1: {f1:.4f}")

if __name__ == '__main__':
    train_v6()
