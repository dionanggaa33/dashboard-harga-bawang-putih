"""Data access layer untuk warehouse MySQL dan fallback dataset Excel."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from etl.extract import extract_harga, extract_jisdor  # noqa: E402
from etl.transform import transform_harga, transform_jisdor  # noqa: E402
from warehouse.loader import URL  # noqa: E402

GEOJSON_PATH = ROOT / "assets" / "jateng_kabupaten.geojson"


def _normalise_dates(data: pd.DataFrame) -> pd.DataFrame:
    """Menyeragamkan kolom tanggal pada dataframe."""

    output = data.copy()
    output["Tanggal"] = pd.to_datetime(output["Tanggal"], errors="coerce")
    return output.dropna(subset=["Tanggal"])


@st.cache_data(show_spinner=False)
def load_harga_from_warehouse(database_url: str = URL) -> pd.DataFrame:
    """Mengambil data harga terintegrasi dari MySQL warehouse."""

    engine = create_engine(database_url, pool_pre_ping=True)
    query = """
        SELECT d.Tanggal, d.Tahun, d.Bulan, d.NamaBulan,
               w.NamaKabupaten AS Kabupaten, f.Harga
        FROM Fact_Harga f
        JOIN Dim_Waktu d ON d.WaktuKey = f.WaktuKey
        JOIN Dim_Wilayah w ON w.WilayahKey = f.WilayahKey
        ORDER BY d.Tanggal, w.NamaKabupaten
    """
    with engine.connect() as connection:
        data = pd.read_sql(text(query), connection)
    return _normalise_dates(data)


@st.cache_data(show_spinner=False)
def load_jisdor_from_warehouse(database_url: str = URL) -> pd.DataFrame:
    """Mengambil data JISDOR terintegrasi dari MySQL warehouse."""

    engine = create_engine(database_url, pool_pre_ping=True)
    query = """
        SELECT d.Tanggal, d.Tahun, d.Bulan, d.NamaBulan, j.Kurs
        FROM Fact_JISDOR j
        JOIN Dim_Waktu d ON d.WaktuKey = j.WaktuKey
        ORDER BY d.Tanggal
    """
    with engine.connect() as connection:
        data = pd.read_sql(text(query), connection)
    return _normalise_dates(data)


@st.cache_data(show_spinner=False)
def load_harga_from_excel() -> pd.DataFrame:
    """Memuat data harga langsung dari Excel untuk mode demo lokal."""

    return _add_time_dimensions(_normalise_dates(transform_harga(extract_harga())).assign(Sumber="Excel"))


@st.cache_data(show_spinner=False)
def load_jisdor_from_excel() -> pd.DataFrame:
    """Memuat data JISDOR langsung dari Excel untuk mode demo lokal."""

    return _add_time_dimensions(_normalise_dates(transform_jisdor(extract_jisdor())).assign(Sumber="Excel"))


@st.cache_data(show_spinner=False)
def load_all_data() -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Memilih warehouse sebagai sumber utama dan Excel sebagai fallback."""

    try:
        harga = load_harga_from_warehouse()
        jisdor = load_jisdor_from_warehouse()
        if harga.empty:
            raise RuntimeError("Warehouse harga kosong")
        return harga, jisdor, "MySQL warehouse"
    except Exception as error:  # noqa: BLE001 - fallback UI perlu menangkap kegagalan koneksi
        try:
            harga = load_harga_from_excel()
            jisdor = load_jisdor_from_excel()
            return harga, jisdor, "Excel fallback"
        except Exception as excel_error:  # noqa: BLE001 - pesan gabungan lebih membantu pengguna
            raise RuntimeError(
                "Data tidak dapat dimuat dari MySQL maupun Excel. "
                f"MySQL: {error}. Excel: {excel_error}"
            ) from excel_error


def filter_harga(data: pd.DataFrame, wilayah: list[str], tahun: int, bulan: str) -> pd.DataFrame:
    """Menerapkan filter wilayah, tahun, dan bulan pada data harga."""

    result = data[data["Tahun"].eq(tahun)].copy()
    if wilayah:
        result = result[result["Kabupaten"].isin(wilayah)]
    if bulan != "Semua bulan":
        result = result[result["NamaBulan"].eq(bulan)]
    return result


def filter_jisdor(data: pd.DataFrame, tahun: int, bulan: str) -> pd.DataFrame:
    """Menerapkan filter waktu pada data JISDOR."""

    result = data[data["Tahun"].eq(tahun)].copy()
    if bulan != "Semua bulan":
        result = result[result["NamaBulan"].eq(bulan)]
    return result


def calculate_kpis(harga: pd.DataFrame, jisdor: pd.DataFrame) -> dict[str, Any]:
    """Menghitung KPI berdasarkan data yang sedang terlihat."""

    if harga.empty:
        return {"average": None, "maximum": None, "minimum": None, "regions": 0, "last_kurs": None}
    latest_kurs = jisdor.sort_values("Tanggal")["Kurs"].iloc[-1] if not jisdor.empty else None
    return {
        "average": float(harga["Harga"].mean()),
        "maximum": int(harga["Harga"].max()),
        "minimum": int(harga["Harga"].min()),
        "regions": int(harga["Kabupaten"].nunique()),
        "last_kurs": int(latest_kurs) if pd.notna(latest_kurs) else None,
    }


def month_options(data: pd.DataFrame) -> list[str]:
    """Menghasilkan daftar bulan Indonesia secara konsisten."""

    order = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember",
    ]
    available = set(data.get("NamaBulan", pd.Series(dtype=str)).dropna().astype(str))
    english_to_indonesian = {
        "January": "Januari", "February": "Februari", "March": "Maret", "April": "April",
        "May": "Mei", "June": "Juni", "July": "Juli", "August": "Agustus",
        "September": "September", "October": "Oktober", "November": "November", "December": "Desember",
    }
    translated = {english_to_indonesian.get(value, value) for value in available}
    return [month for month in order if month in translated]


def with_indonesian_month(data: pd.DataFrame) -> pd.DataFrame:
    """Mengganti nama bulan hasil MySQL/Excel menjadi bahasa Indonesia."""

    output = data.copy()
    mapping = {
        "January": "Januari", "February": "Februari", "March": "Maret", "April": "April",
        "May": "Mei", "June": "Juni", "July": "Juli", "August": "Agustus",
        "September": "September", "October": "Oktober", "November": "November", "December": "Desember",
    }
    output["NamaBulan"] = output["NamaBulan"].replace(mapping)
    return output


def _add_time_dimensions(data: pd.DataFrame) -> pd.DataFrame:
    """Menambahkan atribut waktu yang biasanya disediakan oleh Dim_Waktu."""

    output = data.copy()
    output["Tahun"] = output["Tanggal"].dt.year
    output["Bulan"] = output["Tanggal"].dt.month
    output["NamaBulan"] = output["Tanggal"].dt.month_name()
    return output


@st.cache_data(show_spinner=False)
def load_geojson_jateng() -> dict | None:
    """Memuat GeoJSON kabupaten/kota Jawa Tengah dari aset lokal."""

    try:
        with GEOJSON_PATH.open(encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return None


def map_price_summary(harga: pd.DataFrame) -> pd.DataFrame:
    """Agregasi rata-rata harga per kabupaten untuk peta choropleth."""

    if harga.empty:
        return pd.DataFrame(columns=["Kabupaten", "Harga"])
    return (
        harga.groupby("Kabupaten", as_index=False)["Harga"]
        .mean()
        .rename(columns={"Harga": "RataHarga"})
    )
