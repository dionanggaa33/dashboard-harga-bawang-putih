"""Ekstraksi sumber data Excel."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HARGA_FILE = ROOT / "Dataset Harga Harian Bawang Putih di Kabupaten Jawa Tengah.xlsx"
JISDOR_FILE = ROOT / "Dataset Informasi Kurs Jisdor.xlsx"

def extract_harga(path=HARGA_FILE):
    return pd.read_excel(path, sheet_name="My Worksheet", header=3)

def extract_jisdor(path=JISDOR_FILE):
    return pd.read_excel(path, sheet_name="Informasi Kurs Jisdor", header=4, usecols=["Tanggal", "Kurs"])
