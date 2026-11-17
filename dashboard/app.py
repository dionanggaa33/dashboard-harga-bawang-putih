"""Entry point Streamlit untuk Executive Dashboard Harga Bawang Putih."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.auth import current_user, login_form, logout  # noqa: E402
from dashboard.components import render_footer, render_sidebar_brand  # noqa: E402
from dashboard.config import load_config  # noqa: E402
from dashboard.data import filter_harga, filter_jisdor, load_all_data, month_options, with_indonesian_month  # noqa: E402
from dashboard.pages_admin import render_admin_page  # noqa: E402
from dashboard.pages_dashboard import (  # noqa: E402
    render_clustering_page,
    render_header,
    render_insight_page,
    render_jisdor_page,
    render_kpi_strip,
    render_monitoring_page,
    render_overview,
)
from dashboard.styles import inject_global_styles  # noqa: E402


st.set_page_config(page_title="Executive Dashboard · Harga Bawang Putih Jateng", page_icon="", layout="wide", initial_sidebar_state="expanded")
inject_global_styles()


def render_filters(harga, month_values: list[str], default_year: int) -> tuple[list[str], int, str, int]:
    """Merender strip filter horizontal di atas konten utama."""

    regions = sorted(harga["Kabupaten"].dropna().unique().tolist())
    years = sorted(harga["Tahun"].dropna().astype(int).unique().tolist())
    year_index = years.index(default_year) if default_year in years else max(0, len(years) - 1)
    with st.container(key="filter_panel"):
        st.markdown('<div class="filter-title">Filter monitoring</div>', unsafe_allow_html=True)
        col_region, col_year, col_month, col_reset = st.columns(
            [2.25, 1, 1, 0.72], gap="small", vertical_alignment="bottom"
        )
        with col_region:
            selected_regions = st.multiselect("Kabupaten / Kota", regions, key="filter_regions", placeholder="Semua wilayah")
        with col_year:
            selected_year = st.selectbox("Tahun", years, index=year_index, key="filter_year")
        with col_month:
            selected_month = st.selectbox("Bulan", month_values, key="filter_month")
        with col_reset:
            reset = st.button("Reset filter", width="stretch")
    if reset:
        st.session_state.pop("filter_regions", None)
        st.session_state.pop("filter_month", None)
        st.rerun()
    active_filters = int(bool(selected_regions)) + int(selected_month != "Semua bulan")
    return selected_regions, selected_year, selected_month, active_filters


def render_date_filter(harga: pd.DataFrame) -> datetime.date | None:
    """Merender filter tanggal spesifik (opsional)."""

    if harga.empty:
        min_date = datetime(2017, 1, 1).date()
        max_date = datetime(2025, 12, 31).date()
    else:
        min_date = harga["Tanggal"].min().date()
        max_date = harga["Tanggal"].max().date()

    with st.container(key="date_filter_panel"):
        selected_date = st.date_input(
            "Tanggal spesifik",
            value=None,
            min_value=min_date,
            max_value=max_date,
            format="DD/MM/YYYY",
            help="Kosongkan untuk melihat semua tanggal dalam periode terpilih",
        )
    return selected_date


def make_sidebar(harga, config, user) -> str:
    """Merender branding dan navigasi sidebar."""

    visibility = config["visibility"]
    pages = [("", "Executive Dashboard")]
    page_map = [
        ("", "Pemantauan Harga", "monitoring"),
        ("", "K-Means Clustering", "kmeans"),
        ("", "Business Insight", "insight"),
        ("", "Informasi JISDOR", "jisdor"),
    ]
    pages.extend((icon, label) for icon, label, key in page_map if visibility.get(key, True))
    if user.role == "admin":
        pages.append(("", "Konfigurasi Dashboard"))
    current_page = st.session_state.get("page", "Executive Dashboard")
    page_names = [label for _, label in pages]
    if current_page not in page_names:
        current_page = "Executive Dashboard"
    with st.sidebar:
        st.markdown('<div class="side-label">Menu utama</div>', unsafe_allow_html=True)
        page = current_page
        for icon, label in pages[:1]:
            if st.button(label, key=f"nav_{label}", type="primary" if current_page == label else "secondary", use_container_width=True):
                page = label
        if len(pages) > 1:
            st.markdown('<div class="side-label side-label-spaced">Analisis & informasi</div>', unsafe_allow_html=True)
            for icon, label in pages[1:]:
                if st.button(label, key=f"nav_{label}", type="primary" if current_page == label else "secondary", use_container_width=True):
                    page = label
        st.session_state.page = page
        st.markdown('<div class="sidebar-spacer"></div><div class="side-rule"></div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        f"""
        <div class="sidebar-note">
          <div class="sidebar-note-title">Cakupan data</div>
          <p>29 kabupaten · 2017-2025</p>
          <p>Harga harian SIHATI dan kurs JISDOR Bank Indonesia.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_sidebar_brand(user)
    if st.sidebar.button("Keluar dari sesi", width="stretch"):
        logout()
    return page


def main() -> None:
    """Menjalankan alur login dan dashboard."""

    user = current_user()
    if user is None:
        login_form()
        st.markdown('<div class="login-meta">Sumber data: SIHATI Provinsi Jawa Tengah · Bank Indonesia (JISDOR)</div>', unsafe_allow_html=True)
        return
    try:
        harga, jisdor, source = load_all_data()
    except RuntimeError as error:
        st.error(str(error))
        st.info("Pastikan file Excel berada di folder utama atau jalankan ETL setelah MySQL aktif.")
        return
    harga = with_indonesian_month(harga)
    jisdor = with_indonesian_month(jisdor)
    config = load_config()
    page = make_sidebar(harga, config, user)
    months = month_options(harga)
    regions, year, month, active_filters = render_filters(harga, ["Semua bulan", *months], int(config.get("default_year", 2025)))
    selected_date = render_date_filter(harga)
    filtered_harga = filter_harga(harga, regions, year, month)
    filtered_jisdor = filter_jisdor(jisdor, year, month)

    # Filter tanggal spesifik jika dipilih
    if selected_date:
        filtered_harga = filtered_harga[filtered_harga["Tanggal"].dt.date == selected_date]
        filtered_jisdor = filtered_jisdor[filtered_jisdor["Tanggal"].dt.date == selected_date]

    if page == "Konfigurasi Dashboard":
        if user.role == "admin":
            render_admin_page()
        else:
            st.error("Akses ditolak. Halaman konfigurasi hanya tersedia untuk administrator.")
        return

    render_header(year, source, month)
    if page == "Executive Dashboard":
        visibility = config["visibility"]
        if visibility.get("kpi", True):
            render_kpi_strip(filtered_harga, filtered_jisdor, month, year, harga)
        render_overview(
            filtered_harga,
            filtered_jisdor,
            month,
            year,
            harga,
            show_kpi=False,
            show_map=visibility.get("peta", True),
            show_trend=visibility.get("tren", True),
            show_comparison=visibility.get("perbandingan", True),
            show_kmeans=visibility.get("kmeans", True),
            show_insight=visibility.get("insight", True),
            show_jisdor=visibility.get("jisdor", True),
        )
    elif page == "Pemantauan Harga":
        render_monitoring_page(filtered_harga)
    elif page == "K-Means Clustering":
        render_clustering_page(harga)
    elif page == "Business Insight":
        render_insight_page(harga)
    elif page == "Informasi JISDOR":
        render_jisdor_page(filtered_jisdor)
    render_footer(("SIHATI Provinsi Jawa Tengah", "Bank Indonesia JISDOR"))


if __name__ == "__main__":
    main()
