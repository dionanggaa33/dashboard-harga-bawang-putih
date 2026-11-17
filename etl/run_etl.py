from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from etl.extract import extract_harga, extract_jisdor
from etl.transform import transform_harga, transform_jisdor
from etl.load import load

if __name__ == "__main__":
    harga = transform_harga(extract_harga())
    jisdor = transform_jisdor(extract_jisdor())
    print(f"Harga: valid={len(harga):,}; dibuang={29*2348-len(harga):,}")
    print(harga.groupby("Kabupaten").size().to_string())
    print(f"JISDOR: valid={len(jisdor):,}")
    load(harga, jisdor)
