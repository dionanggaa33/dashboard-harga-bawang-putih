import os
import pandas as pd
from sqlalchemy import create_engine, text

URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3309/dw_bawang_putih_test")
def load_warehouse(harga, jisdor, url=URL):
    # Database dibuat terlebih dahulu melalui koneksi server (bukan koneksi DB).
    server_url = url.rsplit("/", 1)[0] + "/"
    create_engine(server_url).connect().execute(text("CREATE DATABASE IF NOT EXISTS dw_bawang_putih_test"))
    engine = create_engine(url)
    with engine.begin() as c:
        # Hapus tabel lama agar perubahan struktur skema tidak menyisakan kolom lama.
        c.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        for table in ("Fact_Harga", "Fact_JISDOR", "Dim_Wilayah", "Dim_Waktu", "fact_harga", "fact_jisdor", "dim_wilayah", "dim_waktu"):
            c.execute(text(f"DROP TABLE IF EXISTS `{table}`"))
        c.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        for sql in open(os.path.join(os.path.dirname(__file__), "schema.sql"), encoding="utf-8").read().split(';'):
            if sql.strip(): c.execute(text(sql))
    all_dates = pd.concat([harga[["Tanggal"]], jisdor[["Tanggal"]]]).drop_duplicates()
    waktu = pd.DataFrame({"Tanggal": pd.to_datetime(all_dates["Tanggal"]).dt.date})
    waktu["WaktuKey"] = pd.to_datetime(waktu.Tanggal).dt.strftime("%Y%m%d").astype(int)
    dt = pd.to_datetime(waktu.Tanggal); waktu["Hari"]=dt.dt.day; waktu["Bulan"]=dt.dt.month; waktu["NamaBulan"]=dt.dt.month_name(locale="id_ID") if False else dt.dt.strftime("%B"); waktu["Kuartal"]=dt.dt.quarter; waktu["Tahun"]=dt.dt.year
    wilayah = pd.DataFrame({"NamaKabupaten": sorted(harga.Kabupaten.unique()), "Provinsi":"Jawa Tengah"})
    waktu.to_sql("Dim_Waktu", engine, if_exists="append", index=False); wilayah.to_sql("Dim_Wilayah", engine, if_exists="append", index=False)
    w = pd.read_sql("SELECT WaktuKey,Tanggal FROM Dim_Waktu", engine); r = pd.read_sql("SELECT WilayahKey,NamaKabupaten FROM Dim_Wilayah", engine)
    fh=harga.merge(w,on="Tanggal").merge(r,left_on="Kabupaten",right_on="NamaKabupaten")[['WaktuKey','WilayahKey','Harga']]
    fj=jisdor.merge(w,on="Tanggal")[['WaktuKey','Kurs']]
    fh.to_sql("Fact_Harga",engine,if_exists="append",index=False); fj.to_sql("Fact_JISDOR",engine,if_exists="append",index=False)
    print("Warehouse berhasil diisi.")
