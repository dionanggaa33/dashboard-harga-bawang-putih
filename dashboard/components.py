"""Komponen presentasi HTML ringan untuk dashboard."""

from __future__ import annotations

from collections.abc import Iterable

import streamlit as st


def render_login_page() -> None:
    """Merender identitas halaman login."""

    st.markdown(
        """
        <div class="login-shell">
          <div class="login-brand">
            <div class="eyebrow">PEMANTAUAN KOMODITAS · JAWA TENGAH</div>
            <h1>Dashboard Harga Bawang Putih</h1>
            <p>Pemantauan harga harian menurut wilayah.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand(user: object) -> None:
    """Merender branding dan informasi pengguna pada sidebar."""

    username = getattr(user, "username", "user")
    role = getattr(user, "role", "user")
    role_label = "Administrator" if role == "admin" else "Pengguna"
    initial = str(username)[:1].upper()
    st.sidebar.markdown(
        f"""
        <div class="user-chip">
          <div class="user-avatar">{initial}</div>
          <div><div class="user-name">{username}</div><div class="user-role">{role_label}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi(label: str, value: str, note: str, icon: str, accent: str) -> None:
    """Merender satu kartu KPI."""

    st.markdown(
        f"""
        <div class="kpi-card" style="--accent:{accent}">
          <div class="kpi-head"><span class="kpi-label">{label}</span><span class="kpi-icon">{icon}</span></div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_head(title: str, note: str = "", meta: str = "") -> None:
    """Merender judul bagian yang konsisten."""

    meta_html = f'<span class="section-chip">{meta}</span>' if meta else ""
    st.markdown(
        f"""
        <div class="section-head">
          <div><div class="section-title">{title}</div><div class="section-note">{note}</div></div>
          {meta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty(message: str = "Tidak ada data untuk kombinasi filter ini.") -> None:
    """Merender keadaan kosong yang informatif."""

    st.markdown(
        f'<div class="empty-state"><div class="empty-icon">⌁</div><div>{message}</div></div>',
        unsafe_allow_html=True,
    )


def render_insight_card(
    cluster: int,
    members: int,
    mean_price: str,
    std_price: str,
    members_text: str,
    monitoring: str,
    accent: str,
) -> None:
    """Merender narasi insight per cluster."""

    st.markdown(
        f"""
        <div class="insight-card" style="--accent:{accent}">
          <div class="insight-top"><span class="cluster-badge">Cluster {cluster}</span><span class="insight-members">{members} kabupaten</span></div>
          <div class="insight-metric"><span>Rata-rata</span><strong>{mean_price}</strong></div>
          <div class="insight-metric"><span>Variasi</span><strong>{std_price}</strong></div>
          <div class="insight-label">Anggota</div>
          <p class="insight-members-list">{members_text}</p>
          <div class="insight-label">Insight monitoring</div>
          <p>{monitoring}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_cluster_table(rows: list[dict[str, str]], accent_colours: list[str]) -> None:
    """Merender tabel karakteristik cluster tanpa komponen tabel Streamlit."""

    body = "".join(
        f"""
        <tr>
          <td><span class="cluster-dot" style="--accent:{accent_colours[index % len(accent_colours)]}"></span><b>Cluster {row['cluster']}</b></td>
          <td>{row['members']}</td>
          <td>{row['mean']}</td>
          <td>{row['std']}</td>
          <td>{row['characteristic']}</td>
        </tr>
        """
        for index, row in enumerate(rows)
    )
    st.markdown(
        f"""
        <div class="cluster-table-wrap">
          <table class="cluster-table">
            <thead><tr><th>Cluster</th><th>Jumlah wilayah</th><th>Rata-rata harga</th><th>Std. deviasi</th><th>Karakteristik</th></tr></thead>
            <tbody>{body}</tbody>
          </table>
          <p class="table-note">Karakteristik cluster dihitung otomatis berdasarkan centroid model K-Means. Nilai fitur berasal dari histori harga penuh.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )





def render_jisdor_note(last_value: str, last_date: str) -> None:
    """Merender kartu catatan metodologis JISDOR."""

    st.markdown(
        f"""
        <div class="jisdor-panel">
          <div class="jisdor-icon">$</div>
          <div><div class="jisdor-label">Jakarta Interbank Spot Dollar Rate</div><div class="jisdor-value">{last_value} <small>USD</small></div><div class="jisdor-date">Posisi kurs terakhir · {last_date}</div></div>
        </div>
        <div class="callout jisdor-callout"><b>Catatan metodologis:</b> nilai tukar JISDOR ditampilkan sebagai data pendukung monitoring dan tidak menjadi variabel K-Means Clustering.</div>
        """,
        unsafe_allow_html=True,
    )


def render_footer(sources: Iterable[str]) -> None:
    """Merender catatan sumber data di bagian bawah halaman."""

    source_text = " dan ".join(sources)
    st.markdown(
        f'<div class="app-footer"><span>© 2026 Dashboard Pemantauan Harga Bawang Putih</span><span>Sumber data: {source_text}</span></div>',
        unsafe_allow_html=True,
    )
