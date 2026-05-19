import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.functional as F_nn
from torchvision import models
from torch.utils.checkpoint import checkpoint
try:
    from .layers import ConditionalBatchNorm2d, PhysicsSidecarMLP
except (ImportError, ValueError):
    from layers import ConditionalBatchNorm2d, PhysicsSidecarMLP


class SpatialGNNModule(nn.Module):
    """Simplified GAT-based fusion for multi-station scalograms."""
    def __init__(self, in_features=512, hidden=256, out_features=512):
        super().__init__()
        self.gat1 = nn.Linear(in_features, hidden)
        self.gat2 = nn.Linear(hidden, out_features)
        self.attention = nn.Parameter(torch.ones(24))
        
        # Geographical Adjacency Injection (SOTA localization bias)
        self.num_stations = 24
        self.geo_bias = nn.Parameter(torch.zeros(self.num_stations, self.num_stations))

    def forward(self, x):
        # x: (B, N, in_features)
        B, N, Feat = x.shape
        h = F.relu(self.gat1(x))
        h = self.gat2(h)
        
        # Geographical Adjacency Injection: Apply spatial topology directly to hidden features
        if N != self.num_stations:
            bias = self.geo_bias[:N, :N]
        else:
            bias = self.geo_bias
        h = h + torch.matmul(bias, h)
        
        # Ensure attention weights match current N
        if N != self.attention.shape[0]:
            # This is a fallback for debugging with fewer stations
            weights = F.softmax(self.attention[:N], dim=0)
        else:
            weights = F.softmax(self.attention, dim=0)
            
        consensus = torch.sum(h * weights.view(1, N, 1), dim=1)
        return consensus, weights

class ScalogramV4_ResilientSTGAT(nn.Module):
    """
    STGAT V2 with Strategy 1 (Conditional BN) and Strategy 3 (Autoencoder) capabilities.
    """
    def __init__(self, n_regions=6, use_cbn=True, is_autoencoder=False, chunk_size=4):
        super().__init__()
        # Limit threads for stability on shared/restricted systems
        if torch.get_num_threads() > 4:
            torch.set_num_threads(4)
            
        self.use_cbn = use_cbn
        self.is_autoencoder = is_autoencoder
        self.chunk_size = chunk_size
        
        # 1. Physics Sidecar (Strategy 1)
        self.physics_sidecar = PhysicsSidecarMLP(input_dim=2, embedding_dim=128)
        
        # 2. Spatial Encoder (EfficientNet-B1)
        efficientnet = models.efficientnet_b1(weights=None)
        self.spatial_encoder = efficientnet.features
        
        if use_cbn:
            self._replace_bn_with_cbn(self.spatial_encoder, 128)
            # Pre-collect all CBN layers to avoid searching them in forward()
            self.cbn_layers = [m for m in self.spatial_encoder.modules() if isinstance(m, ConditionalBatchNorm2d)]
        else:
            self.cbn_layers = []
            
        self.pool = nn.AdaptiveAvgPool2d((1, None))
        
        # 3. Temporal Encoder (BiGRU)
        self.temporal_encoder = nn.GRU(
            input_size=1280,
            hidden_size=256,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=0.2
        )
        
        # 4. GNN Layer
        self.gat_layer = SpatialGNNModule(in_features=512, hidden=256, out_features=512)
        
        # 5. Cosmic Gate (Deterministic Behavior)
        self.cosmic_gate = nn.Sequential(
            nn.Linear(2, 32), nn.ReLU(),
            nn.Linear(32, 512), nn.Sigmoid()
        )
        
        # 6. Task Heads
        self.head_detect = nn.Sequential(
            nn.Linear(512, 128), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(128, 1)
        )
        self.head_mag = nn.Sequential(
            nn.Linear(512, 128), nn.ReLU(),
            nn.Linear(128, 1)
        )
        self.head_azm = nn.Sequential(
            nn.Linear(512, 128), nn.ReLU(),
            nn.Linear(128, 2)
        )
        
        # 7. Reconstruction Head (Strategy 3: Autoencoder)
        if is_autoencoder:
            # Simple decoder to reconstruct scalogram (3, 128, 1440)
            self.decoder_final = nn.Sequential(
                nn.Linear(512, 128 * 45), nn.ReLU(),
                nn.Unflatten(1, (1, 128, 45)),
                nn.Upsample(size=(128, 1440), mode='bilinear', align_corners=False),
                nn.Conv2d(1, 3, kernel_size=3, padding=1)
            )

        # 8. Physics Parameters
        self.alpha_regions = nn.Parameter(torch.randn(n_regions))

    def _replace_bn_with_cbn(self, module, embedding_dim):
        """Recursively replace BatchNorm2d with ConditionalBatchNorm2d."""
        for name, child in module.named_children():
            if isinstance(child, nn.BatchNorm2d):
                # Replace with ConditionalBatchNorm2d
                cbn = ConditionalBatchNorm2d(child.num_features, embedding_dim)
                setattr(module, name, cbn)
            else:
                self._replace_bn_with_cbn(child, embedding_dim)

    def forward(self, x_img, x_cosmic):
        # x_img: (B, 24, 3, 128, 1440)
        # x_cosmic: (B, 2)
        B, N, C, H, W = x_img.shape
        
        # 1. Generate Physics Embedding
        phys_embed = self.physics_sidecar(x_cosmic) # (B, 128)
        
        # --- EXTREME MEMORY SURGERY START ---
        # Asumsi x shape: [B, N, C, H, W] -> misal: [1, 24, 3, 128, 1440]
        B, N, C, H, W_time = x_img.size()
        
        # 1. TEMPORAL DECIMATION (Downsampling 1440 -> 144)
        # Menyatukan B dan N agar bisa di-pooling oleh PyTorch
        x_reshaped = x_img.view(B * N, C, H, W_time)
        
        # Max Pooling mempertahankan puncak gelombang (peak phase) yang krusial untuk Stage 3
        x_pooled = F_nn.max_pool2d(x_reshaped, kernel_size=(1, 10), stride=(1, 10))
        
        # Kembalikan ke shape [B, N, C, H, W_baru]
        x_lightweight = x_pooled.view(B, N, C, H, W_time // 10)
        
        spatial_features_list = []
        
        # Set physics embedding for CBN layers
        for m in self.cbn_layers:
            m.current_embedding = phys_embed
            
        # 2. ABSOLUTE NO-GRAD (Mencegah PyTorch menyimpan graf memori)
        # Karena di Fase 1 kita freeze EfficientNet, kita WAJIB menggunakan blok ini
        with torch.no_grad():
            for i in range(N):
                # Feed stasiun satu per satu dari tensor yang sudah 90% lebih ringan
                station_input = x_lightweight[:, i, :, :, :]
                station_feat = self.spatial_encoder(station_input)
                
                # Apply pooling and permute for Temporal Encoder
                station_feat = self.pool(station_feat).squeeze(2).permute(0, 2, 1) # (B, Seq, 1280)
                spatial_features_list.append(station_feat)
                
        # Tumpuk kembali hasil ekstraksi fitur
        spatial_features = torch.cat(spatial_features_list, dim=0)
        # PENTING: Aktifkan kembali gradient flow untuk layer selanjutnya (GAT/BiGRU)
        spatial_features.requires_grad_(True)
        feat = spatial_features
        # --- EXTREME MEMORY SURGERY END ---
        
        # 4. Temporal Encoding
        self.temporal_encoder.flatten_parameters()
        gru_out, _ = self.temporal_encoder(feat)
        v_img = torch.mean(gru_out, dim=1) # (B*N, 512)
        v_img = v_img.view(B, N, 512)
        
        # 5. Graph Attention Fusion
        v_consensus, att_weights = self.gat_layer(v_img)
        
        # 6. Heads
        raw_pred_event = self.head_detect(v_consensus).squeeze(-1)
        gate_val = self.cosmic_gate(x_cosmic)
        v_fusion = v_consensus * gate_val
        
        out_mag = self.head_mag(v_fusion).squeeze(-1)
        out_azm = self.head_azm(v_fusion)
        
        # 7. Reconstruction (Autoencoder)
        reconstruction = None
        if self.is_autoencoder:
            reconstruction = self.decoder_final(v_consensus) # (B, 3, 128, 1440)
            
        return raw_pred_event, out_mag, out_azm, self.alpha_regions, gate_val, reconstruction
