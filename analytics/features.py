import pandas as pd
from sqlalchemy import create_engine

def build_features(engine):
    q = """SELECT w.NamaKabupaten AS Kabupaten, f.Harga FROM Fact_Harga f JOIN Dim_Wilayah w ON f.WilayahKey=w.WilayahKey"""
    d = pd.read_sql(q, engine)
    return d.groupby("Kabupaten")["Harga"].agg(Mean_Harga="mean", Std_Harga="std", N_Observasi="count").reset_index()
