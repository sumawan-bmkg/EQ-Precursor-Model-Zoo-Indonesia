
"""
Train V6 Accuracy V3 - Strong Anti-Bias Strategy

Root cause of previous failures:
- Val/test split is 67% Precursor (148:72). Model finds predict-all-Precursor = 67% accuracy.
- Need to force the model to LEARN the Normal class features.

Fix Strategy:
1. Focal Loss: Penalizes easy, high-confidence Precursor predictions → forces learning Normal.
2. Inverted pos_weight (<1.0): Downweight Precursor loss, upweight Normal loss.
3. Per-class accuracy tracking: Monitor Normal accuracy separately to detect convergence.
4. Train/val split with ~1:1 ratio from enriched data for validation.
"""

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
import pandas as pd
import numpy as np
from tqdm import tqdm
import copy

from dataset_scalogram.src.data_loader import ScalogramDataset
from dataset_scalogram.src.model_scalogram import get_model

# ============================================================================

class FocalLoss(nn.Module):
    """
    Focal Loss for binary classification.
    Reduces the loss contribution from easy examples and focuses on hard ones.
    gamma=2 is the standard recommendation.
    pos_weight < 1.0 downweights the Precursor class.
    """
    def __init__(self, gamma=2.0, pos_weight=0.5):
        super().__init__()
        self.gamma = gamma
        self.pos_weight = pos_weight

    def forward(self, logits, targets):
        bce = F.binary_cross_entropy_with_logits(logits, targets, reduction='none')
        probs = torch.sigmoid(logits)
        # pt: probability of the true class
        pt = torch.where(targets == 1, probs, 1 - probs)
        # Focal weight
        focal_weight = (1 - pt) ** self.gamma
        # Class-specific weight
        class_weight = torch.where(targets == 1,
                                   torch.ones_like(targets) * self.pos_weight,
                                   torch.ones_like(targets))
        loss = focal_weight * class_weight * bce
        return loss.mean()


class ConfigV3:
    data_dir = 'dataset_scalogram/processed_v6'
    metadata_dir = 'dataset_scalogram/processed_v6/metadata'

    backbone = 'swin_tiny_patch4_window7_224'
    batch_size = 4
    lr = 3e-5    # Smaller LR for finer adjustments
    epochs = 30

    # CRITICAL: pos_weight < 1.0 heavily downweights Precursor (majority class)
    # Model will be pushed to learn Normal features or face high loss
    focal_gamma = 2.0
    focal_pos_weight = 0.4   # Precursor weighted at 0.4x, Normal at 1x

    save_dir = 'models/scalogram_v6_accuracy'
    device_idx = 1


def build_balanced_loader(data_dir, meta_path, batch_size=4, shuffle=True):
    """Explicit oversampling of Normal class to 1:1 ratio."""
    base_meta = pd.read_csv(meta_path)

    normal = base_meta[base_meta['label'] == 'Normal']
    precursor = base_meta[base_meta['label'] == 'Precursor']

    print(f"  Raw — Normal: {len(normal)}, Precursor: {len(precursor)}")

    # Oversample Normal to match Precursor
    repeats = len(precursor) // len(normal)
    remainder = len(precursor) % len(normal)
    balanced_normal = pd.concat([normal] * repeats + [normal.iloc[:remainder]])
    balanced_meta = pd.concat([balanced_normal, precursor]).sample(frac=1, random_state=42).reset_index(drop=True)

    tmp_path = meta_path.replace('.csv', '_balanced_tmp.csv')
    balanced_meta.to_csv(tmp_path, index=False)

    ds = ScalogramDataset(data_dir, tmp_path, stage='stage1')
    print(f"  Balanced — Total: {len(ds)}")
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, num_workers=0)


def evaluate(model, loader, device, threshold=0.5):
    """Evaluate with per-class accuracy."""
    model.eval()
    all_probs, all_labels = [], []

    with torch.no_grad():
        for images, labels, solar, _ in loader:
            images = images.to(device)
            solar = solar.to(device)
            out = model(images, solar).squeeze(-1)
            probs = torch.sigmoid(out)
            all_probs.extend(probs.cpu().numpy())
            all_labels.extend(labels.numpy())

    all_probs = np.array(all_probs)
    all_labels = np.array(all_labels)

    # Find optimal threshold for overall accuracy
    best_thresh, best_acc = threshold, -1
    for t in np.arange(0.1, 0.95, 0.05):
        preds = (all_probs >= t).astype(int)
        acc = (preds == all_labels).mean()
        if acc > best_acc:
            best_acc = acc
            best_thresh = t

    preds_opt = (all_probs >= best_thresh).astype(int)
    preds_fixed = (all_probs >= 0.5).astype(int)

    # Per-class accuracy
    normal_mask = (all_labels == 0)
    precursor_mask = (all_labels == 1)
    normal_acc = (preds_opt[normal_mask] == 0).mean() if normal_mask.any() else 0
    precursor_acc = (preds_opt[precursor_mask] == 1).mean() if precursor_mask.any() else 0

    from sklearn.metrics import f1_score, recall_score
    f1 = f1_score(all_labels, preds_opt)
    recall = recall_score(all_labels, preds_opt)
    acc_fixed = (preds_fixed == all_labels).mean()

    return {
        'acc_opt': best_acc,
        'thresh': best_thresh,
        'acc_fixed': acc_fixed,
        'f1': f1,
        'recall': recall,
        'normal_acc': normal_acc,
        'precursor_acc': precursor_acc
    }


def train_v3():
    cfg = ConfigV3()
    device = torch.device(f'cuda:{cfg.device_idx}' if torch.cuda.is_available() else 'cpu')
    os.makedirs(cfg.save_dir, exist_ok=True)

    print(f"--- V3 ANTI-BIAS TRAINING (Focal Loss + Downweighted Precursor) ---")
    print(f"Device: {device} | Focal gamma={cfg.focal_gamma} | Precursor weight={cfg.focal_pos_weight}\n")

    train_meta = os.path.join(cfg.metadata_dir, 'split_train_v6_enriched.csv')
    val_meta = os.path.join(cfg.metadata_dir, 'split_val_v6_enriched.csv')

    print("Building balanced train loader...")
    train_loader = build_balanced_loader(cfg.data_dir, train_meta, batch_size=cfg.batch_size)

    val_ds = ScalogramDataset(cfg.data_dir, val_meta, stage='stage1')
    val_loader = DataLoader(val_ds, batch_size=cfg.batch_size, shuffle=False, num_workers=0)
    print(f"  Val samples: {len(val_ds)}\n")

    model = get_model('stage1_v6', backend=cfg.backbone).to(device)
    criterion = FocalLoss(gamma=cfg.focal_gamma, pos_weight=cfg.focal_pos_weight)
    optimizer = optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=0.05)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg.epochs)

    best_acc = 0

    for epoch in range(cfg.epochs):
        model.train()
        train_loss = 0

        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{cfg.epochs}")
        for images, labels, solar, _ in pbar:
            images = images.to(device)
            labels = labels.to(device).float()
            solar = solar.to(device)

            optimizer.zero_grad()
            outputs = model(images, solar).squeeze(-1)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            pbar.set_postfix({'loss': f'{loss.item():.4f}'})

        # Evaluate
        metrics = evaluate(model, val_loader, device)
        avg_loss = train_loss / len(train_loader)

        print(f"  Loss:{avg_loss:.4f} | Acc@0.5:{metrics['acc_fixed']:.4f} | Acc@opt({metrics['thresh']:.2f}):{metrics['acc_opt']:.4f} | F1:{metrics['f1']:.4f}")
        print(f"           Per-class => Normal:{metrics['normal_acc']:.4f} | Precursor:{metrics['precursor_acc']:.4f}")

        scheduler.step()

        if metrics['acc_opt'] > best_acc:
            best_acc = metrics['acc_opt']
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'metrics': metrics
            }, os.path.join(cfg.save_dir, 'best_accuracy_model.pth'))
            print(f"  [SAVED] Best Acc: {best_acc:.4f} (thresh={metrics['thresh']:.2f})")

    print(f"\n--- COMPLETE. Best Val Acc: {best_acc:.4f} ---")


if __name__ == '__main__':
    train_v3()
