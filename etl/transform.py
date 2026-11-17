"""Transformasi dan validasi data; nilai nol sengaja dihapus."""
import pandas as pd

def transform_harga(raw):
    wilayah_col = raw.columns[0]
    data = raw.rename(columns={wilayah_col: "Kabupaten"}).copy()
    data["Kabupaten"] = data["Kabupaten"].astype(str).str.replace(r"^Kabupaten\s+", "", regex=True).str.strip()
    long = data.melt(id_vars="Kabupaten", var_name="Tanggal", value_name="Harga")
    long["Tanggal"] = pd.to_datetime(long["Tanggal"], errors="coerce").dt.date
    long["Harga"] = pd.to_numeric(long["Harga"], errors="coerce").replace(0, pd.NA)
    return long.dropna(subset=["Tanggal", "Harga"]).assign(Harga=lambda x: x["Harga"].astype(int))

def transform_jisdor(raw):
    out = raw[["Tanggal", "Kurs"]].copy()
    out["Tanggal"] = pd.to_datetime(out["Tanggal"], format="%m/%d/%Y %I:%M:%S %p", errors="coerce").dt.date
    out["Kurs"] = pd.to_numeric(out["Kurs"], errors="coerce")
    return out.dropna().assign(Kurs=lambda x: x["Kurs"].astype(int)).drop_duplicates("Tanggal")
