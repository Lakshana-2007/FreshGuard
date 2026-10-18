import torch
import torch.nn as nn
from pathlib import Path
from torchvision import models

p = Path(__file__).resolve().parents[1] / 'saved_models' / 'm2' / 'candidates' / 'xyphitos_fridgeai' / 'spoilage_mobilenetv3.pth'
print('PATH', p)
state = torch.load(str(p), map_location='cpu')
print('TYPE', type(state))
if isinstance(state, dict):
    keys = list(state.keys())
    print('NUM_KEYS', len(keys))
    print('FIRST_20', keys[:20])
    print('HAS_classifier_0_weight', 'classifier.0.weight' in state)
    print('HAS_features_0_0_weight', 'features.0.0.weight' in state)
    print('HAS_statelevel', any(k.startswith('classifier') for k in state.keys()) )

model = models.mobilenet_v3_small(weights=None)
model.classifier = nn.Sequential(
    nn.Linear(576, 256),
    nn.Hardswish(),
    nn.Dropout(0.2),
    nn.Linear(256, 1),
)

try:
    model.load_state_dict(state, strict=True)
    print('LOAD_OK')
    model.eval()
    x = torch.zeros((1, 3, 224, 224))
    with torch.no_grad():
        y = model(x)
    print('OUTPUT_SHAPE', tuple(y.shape))
    print('STATS', float(y.min()), float(y.max()), float(y.mean()))
except Exception as e:
    import traceback
    traceback.print_exc()
