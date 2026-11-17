import pandas as pd
FEATURES = ["Mean_Harga", "Std_Harga"]
def zscore(features):
    params = {c: {"mean": features[c].mean(), "std": features[c].std()} for c in FEATURES}
    out = features.copy()
    for c in FEATURES: out[c] = (out[c]-params[c]["mean"])/params[c]["std"]
    return out, params
