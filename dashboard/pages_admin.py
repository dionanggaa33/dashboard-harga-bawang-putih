"""Halaman konfigurasi admin."""

from __future__ import annotations

import streamlit as st

from dashboard.config import load_config, save_config


VISIBILITY_LABELS = {
    "kpi": "Kartu KPI",
    "peta": "Peta sebaran harga",
    "tren": "Tren harga",
    "perbandingan": "Perbandingan antarwilayah",
    "kmeans": "K-Means clustering",
    "insight": "Business insight",
    "jisdor": "Informasi JISDOR",
}


def render_admin_page() -> None:
    """Merender kontrol konfigurasi yang hanya tersedia untuk admin."""

    st.markdown('<div class="eyebrow">Administrator</div>', unsafe_allow_html=True)
    st.markdown("# Konfigurasi dashboard")
    st.markdown('<p class="page-lead">Atur tampilan modul dan tahun awal yang digunakan saat dashboard dibuka.</p>', unsafe_allow_html=True)
    config = load_config()
    with st.form("dashboard_config_form"):
        default_year = st.number_input("Tahun default", min_value=2017, max_value=2100, value=int(config.get("default_year", 2025)), step=1)
        st.markdown("### Modul yang ditampilkan")
        visibility = config.get("visibility", {})
        updated_visibility: dict[str, bool] = {}
        for key, label in VISIBILITY_LABELS.items():
            updated_visibility[key] = st.checkbox(label, value=bool(visibility.get(key, True)))
        submitted = st.form_submit_button("Simpan konfigurasi", width="stretch")
    if submitted:
        config["default_year"] = int(default_year)
        config["visibility"] = updated_visibility
        save_config(config)
        st.success("Konfigurasi berhasil disimpan.")
        st.rerun()
    st.markdown('<div class="callout" style="margin-top:1rem;"><b>Akses:</b> Halaman ini hanya tersedia untuk role administrator. Pengguna biasa akan diarahkan kembali ke ringkasan dashboard.<br><b>Catatan:</b> Peta sebaran harga memakai rata-rata historis penuh, bukan periode terfilter.</div>', unsafe_allow_html=True)
