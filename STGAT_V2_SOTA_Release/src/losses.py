import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class PhysicsResilientLoss(nn.Module):
    """
    Enhanced Physics-Informed Loss with reconstruction error for Strategy 3.
    """
    def __init__(self, lambda1=2.0, lambda2=0.1, lambda3=0.05, lambda4=0.1, lambda_recon=0.5):
        super().__init__()
        self.lambda1 = lambda1 # Detection (BCE)
        self.lambda2 = lambda2 # Magnitude (MSE)
        self.lambda3 = lambda3 # Azimuth (MSE)
        self.lambda4 = lambda4 # Physics (DPINN)
        self.lambda_recon = lambda_recon # Autoencoder (Reconstruction)
        
        self.bce_loss = nn.BCEWithLogitsLoss()
        self.mse_loss = nn.MSELoss(reduction='none')

    def forward(self, preds, targets):
        # preds: raw_pred_event, pred_mag, pred_azm, pred_alpha, gate_val, reconstruction
        # targets: y_event, y_mag, y_azm, y_dist, region_idx, x_img (for reconstruction)
        raw_pred_event, pred_mag, pred_azm, pred_alpha, gate_val, reconstruction = preds
        y_event, y_mag, y_azm, y_dist, region_idx, x_img = targets

        # 1. Detection Loss
        loss_bce = self.bce_loss(raw_pred_event, y_event)

        # Mask for regression tasks
        mask = (y_event == 1.0).float()
        num_events = torch.sum(mask) + 1e-8

        # 2. Magnitude & Azimuth Loss
        loss_mag = torch.sum(self.mse_loss(pred_mag, y_mag) * mask) / num_events
        
        # Calculate predicted azimuth in degrees from sin/cos outputs
        pred_azm_rad = torch.atan2(pred_azm[:, 0], pred_azm[:, 1])
        pred_azm_deg = (pred_azm_rad * (180.0 / np.pi)) % 360.0
        
        # Circular difference in degrees (0 to 360)
        diff_azm = torch.abs(pred_azm_deg - y_azm)
        circular_diff = torch.minimum(diff_azm, 360.0 - diff_azm)
        loss_azm = torch.sum((circular_diff ** 2) * mask) / num_events

        # 3. Physics Loss (DPINN Attenuation)
        alpha_batch = F.softplus(pred_alpha[region_idx])
        # y_dist: (B, 24)
        attenuated_energy_pred = pred_mag.unsqueeze(1) * torch.exp(-alpha_batch.unsqueeze(1) * y_dist)
        attenuated_energy_true = y_mag.unsqueeze(1) * torch.exp(-alpha_batch.unsqueeze(1) * y_dist)
        loss_phys = torch.sum(torch.mean(self.mse_loss(attenuated_energy_pred, attenuated_energy_true), dim=1) * mask) / num_events

        # 4. Reconstruction Loss (Strategy 3)
        loss_recon = torch.tensor(0.0).to(y_event.device)
        if reconstruction is not None and self.lambda_recon > 0.0:
            # Reconstruction is (B, 3, 128, 1440)
            station_masks = (torch.sum(torch.abs(x_img), dim=(2, 3, 4)) > 0).float() # (B, 24)
            num_active = torch.sum(station_masks, dim=1, keepdim=True).view(-1, 1, 1, 1) + 1e-8
            target_recon = torch.sum(x_img, dim=1) / num_active
            loss_recon = F.mse_loss(reconstruction, target_recon)

        # 5. Total Loss
        total_loss = (self.lambda1 * loss_bce) + \
                     (self.lambda2 * loss_mag) + \
                     (self.lambda3 * loss_azm) + \
                     (self.lambda4 * loss_phys) + \
                     (self.lambda_recon * loss_recon)

        metrics = {
            'total': total_loss.item(),
            'bce': loss_bce.item(),
            'mag': loss_mag.item(),
            'azm': loss_azm.item(),
            'phys': loss_phys.item(),
            'recon': loss_recon.item()
        }
        
        return total_loss, metrics
