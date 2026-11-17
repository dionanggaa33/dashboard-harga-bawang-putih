# Dashboard Harga Harian Bawang Putih

Sistem deskriptif dan K-Means untuk monitoring harga bawang putih di Jawa Tengah. JISDOR hanya informasi pendukung dan tidak digunakan sebagai fitur clustering.

## Menjalankan

### Dari VS Code
1. Buka folder proyek di VS Code.
2. Pastikan MySQL aktif (XAMPP) dan ETL sudah dijalankan (`python etl/run_etl.py`).
3. Buka terminal (`Ctrl+` ` ` `) lalu jalankan:
   ```powershell
   streamlit run dashboard/app.py
   ```
4. Dashboard terbuka otomatis di browser, atau klik link `http://localhost:8501`.

### Dari browser langsung
Jika server sudah berjalan, cukup buka:
```
http://localhost:8501
```
### Kredensial login

Password **tidak disimpan di dalam kode**. Nilainya dibaca dari `.streamlit/secrets.toml`
(lokal) atau menu **Settings → Secrets** di Streamlit Cloud. Sebelum menjalankan pertama kali:

```powershell
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
```

lalu isi `[auth.users.*]` dengan password pilihanmu. Bila secrets belum diisi, aplikasi
berhenti dengan pesan yang menjelaskan cara memperbaikinya. File `secrets.toml` sudah
masuk `.gitignore` sehingga tidak ikut terunggah ke repositori.

## Struktur
`etl/` ekstraksi-transformasi-load; `warehouse/` skema dan loader MySQL; `analytics/` fitur, normalisasi, elbow, clustering, evaluasi, dan insight; `dashboard/` aplikasi Streamlit.

Folder pendukung di luar kode aplikasi:

- `docs/`: dokumen non-kode (Manual Book, Form UAT, catatan Last Update) dalam format `.docx`/`.pdf`.
- `tools/`: generator dokumen (`gen_uat.py`, `to_pdf.py`) beserta gambar sumbernya di `tools/manual_assets/`.
- Dua file Excel `Dataset Harga Harian ...xlsx` dan `Dataset Informasi Kurs Jisdor.xlsx` sengaja tetap di root karena dibaca langsung oleh `etl/extract.py` sebagai sumber ETL dan fallback dashboard.

Menjalankan generator dokumen (boleh dari folder mana pun, hasil selalu masuk ke `docs/`):
```powershell
python tools/gen_uat.py   # -> docs/Form UAT Dashboard Harga Bawang Putih.docx
python tools/to_pdf.py    # -> docs/Form UAT Dashboard Harga Bawang Putih.pdf (butuh Word + pywin32)
```

> `gen_uat.py` menimpa `docs/Form UAT Dashboard Harga Bawang Putih.docx`. Backup dulu bila versi cetak sudah final.

## Dashboard

Dashboard menggunakan Streamlit sebagai framework utama, Plotly untuk visualisasi interaktif, serta HTML dan CSS tersemat untuk komponen presentasi. Plotly menyediakan runtime JavaScript untuk zoom, hover, legend, dan range slider. MySQL warehouse menjadi sumber data utama. Jika MySQL belum tersedia atau tidak dapat diakses, dashboard otomatis menggunakan dua file Excel di folder utama sebagai fallback lokal sehingga login, filter, KPI, grafik, dan clustering tetap dapat diuji.

### Akses demo

- Pengguna: role `user`
- Administrator: role `admin`

Username dan password aktual berasal dari `[auth.users.*]` pada secrets (lihat bagian Kredensial login).

Administrator dapat membuka menu **Konfigurasi Admin** untuk mengatur modul yang terlihat dan tahun default. JISDOR hanya ditampilkan sebagai informasi pendukung dan tidak menjadi fitur clustering.

### Struktur dashboard

- `dashboard/app.py`: entry point, login, routing, filter global
- `dashboard/auth.py`: autentikasi dan session state
- `dashboard/data.py`: akses MySQL, fallback Excel, filtering, KPI
- `dashboard/charts.py`: builder Plotly dengan tema konsisten
- `dashboard/components.py` dan `dashboard/styles.py`: komponen HTML dan design system
- `dashboard/pages_dashboard.py`: ringkasan, peta, tren, perbandingan, K-Means, insight, JISDOR
- `dashboard/pages_admin.py`: konfigurasi visibilitas dashboard
- `assets/jateng_kabupaten.geojson`: batas 29 kabupaten Jawa Tengah (GADM 4.1)
- `scripts/fetch_geojson.py`: unduh dan proses ulang GeoJSON bila diperlukan

### Peta sebaran harga

Dashboard menampilkan **choropleth rata-rata harga historis per kabupaten** (seluruh periode data) agar 29 kabupaten terisi penuh. Filter tahun/bulan tidak memengaruhi peta; hanya KPI dan grafik tren yang berubah. Sumber geometri: [GADM 4.1](https://gadm.org) level kabupaten/kota Jawa Tengah.
