import h5py, json
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'saved_models' / 'm2' / 'candidates' / 'captraj_fruitveg' / 'rottenvsfresh98pval.h5'
print('h5 path:', p)
with h5py.File(p,'r') as f:
    cfg = f.attrs.get('model_config')
    if cfg is None:
        print('no model_config')
    else:
        s = cfg.decode() if isinstance(cfg, bytes) else cfg
        from tensorflow.keras.models import model_from_json
        import sys
        from pathlib import Path as _P
        # Ensure backend/ is on sys.path
        repo_root = _P(__file__).resolve().parents[3]
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from app.ml.m2_candidates.keras_compat import CompatDepthwiseConv2D
        from tensorflow.keras.utils import get_custom_objects
        get_custom_objects()['DepthwiseConv2D'] = CompatDepthwiseConv2D
        try:
            print('model_config (trunc):', repr(s)[:1000])
            # model_config can be a dict with top-level 'class_name' and 'config'.
            # model_from_json expects the inner config or a proper JSON string.
            # If s is a full wrapper, extract the inner 'config'.
            j = json.loads(s)
            if isinstance(j, dict) and 'config' in j and 'class_name' in j:
                inner = json.dumps(j['config'])
                model = model_from_json(inner)
            else:
                model = model_from_json(s)
            print('model_from_json success, input_shape=', model.input_shape)
            # load weights
            model.load_weights(str(p))
            print('weights loaded')
            import numpy as np
            dummy = np.zeros((1,100,100,3), dtype=np.float32)
            out = model.predict(dummy)
            print('predict_ok, out shape=', getattr(out,'shape', None))
        except Exception as e:
            import traceback
            print('fallback error:', e)
            traceback.print_exc()
