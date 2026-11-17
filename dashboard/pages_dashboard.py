"""Halaman user untuk monitoring, analitik, dan insight."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st
from sklearn.metrics import davies_bouldin_score, silhouette_score

from analytics.elbow import calculate_elbow
from analytics.insight import summarize
from analytics.kmeans_model import fit_model
from analytics.normalize import zscore
from dashboard.charts import (
    PALETTE,
    analisis_outlier_pihps,
    cluster_boxplot,
    cluster_boxplot_by_month,
    clustering_scatter,
    comparison_chart,
    elbow_chart,
    jisdor_chart,
    price_choropleth,
    silhouette_plot,
    trend_chart,
)
from dashboard.components import (
    render_cluster_table,
    render_empty,
    render_insight_card,
    render_jisdor_note,
    render_kpi,
    render_section_head,
)
from dashboard.data import load_geojson_jateng, map_price_summary


def rupiah(value: float | int | None) -> str:
    """Memformat nominal rupiah tanpa desimal."""

    if value is None or pd.isna(value):
        return "—"
    return f"Rp {float(value):,.0f}".replace(",", ".")


def integer(value: int | None) -> str:
    """Memformat bilangan dengan pemisah ribuan Indonesia."""

    if value is None:
        return "—"
    return f"{value:,}".replace(",", ".")


def period_label(harga: pd.DataFrame, month: str, year: int) -> str:
    """Menghasilkan label periode ringkas untuk konteks kartu."""

    if harga.empty:
        return f"{month} {year}" if month != "Semua bulan" else f"Tahun {year}"
    dates = harga["Tanggal"].dropna()
    if month != "Semua bulan":
        return f"{month} {year}"
    return f"01 Jan - 31 Des {year}" if not dates.empty else f"Tahun {year}"


@st.cache_data(show_spinner=False)
def calculate_clustering(harga: pd.DataFrame) -> dict[str, Any]:
    """Menghasilkan fitur, elbow, model, evaluasi, dan insight clustering.

    Analisis memakai seluruh histori harga yang tersedia, bukan hasil filter
    tampilan, sehingga hasil cluster stabil untuk kebutuhan monitoring.
    """

    features = harga.groupby("Kabupaten")["Harga"].agg(
        Mean_Harga="mean", Std_Harga="std", N_Observasi="count"
    ).reset_index()
    normalized, params = zscore(features)
    valid = normalized.dropna(subset=["Mean_Harga", "Std_Harga"]).copy()
    elbow = calculate_elbow(normalized)
    if len(valid) < 2:
        raise ValueError("Jumlah wilayah valid untuk clustering belum mencukupi.")
    k = next(
        (
            row["K"]
            for index, row in enumerate(elbow[1:], 1)
            if row["WCSS"] <= elbow[index - 1]["WCSS"] * 0.5
        ),
        min(3, len(valid)),
    )
    k = max(2, min(int(k), len(valid)))
    labels, centroids = fit_model(normalized, k)
    matrix = normalized[["Mean_Harga", "Std_Harga"]].dropna()
    labels_for_evaluation = labels.loc[matrix.index, "Cluster"]
    silhouette = float(silhouette_score(matrix, labels_for_evaluation))
    dbi = float(davies_bouldin_score(matrix, labels_for_evaluation))
    summary, insight = summarize(features, labels)
    return {
        "features": features,
        "normalized": normalized,
        "params": params,
        "elbow": elbow,
        "k": k,
        "labels": labels,
        "centroids": centroids,
        "silhouette": silhouette,
        "dbi": dbi,
        "summary": summary,
        "insight": insight,
    }


def _pct_change(current: float | None, previous: float | None) -> str:
    """Menghitung perubahan relatif sederhana untuk catatan KPI."""

    if not current or not previous:
        return ""
    change = (current - previous) / previous * 100
    return f"{change:+.1f}% vs tahun lalu"


def cluster_label(value: Any) -> int:
    """Menormalkan label cluster menjadi bilangan bulat."""

    return int(value)


def render_header(year: int, source: str, month: str) -> None:
    """Merender hero header mengikuti referensi dashboard."""

    period = "01 Jan - 31 Des" if month == "Semua bulan" else f"01 - 31 {month}"
    source_label = "SIHATI · MySQL warehouse" if "MySQL" in source else "SIHATI · Excel fallback"
    st.markdown(
        f"""
        <div class="hero-band">
          <div>
            <div><span class="eyebrow" style="display:inline;">PEMANTAUAN KOMODITAS · JAWA TENGAH</span></div>
            <h1>Dashboard Pemantauan Harga Bawang Putih</h1>
            <p>Monitoring Harga Harian Bawang Putih Jawa Tengah · <b>Sumber: {source_label}</b></p>
          </div>
          <div class="header-chips">
            <span class="header-chip"><span class="status-dot"></span>{period} {year}</span>
            <span class="header-chip">Provinsi Jawa Tengah</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_strip(harga: pd.DataFrame, jisdor: pd.DataFrame, month: str, year: int, full_harga: pd.DataFrame) -> None:
    """Merender lima KPI proposal dengan konteks periode."""

    if harga.empty:
        render_empty("Belum ada data harga untuk filter yang dipilih.")
        return
    previous_year = full_harga[full_harga["Tahun"].eq(year - 1)]
    if month != "Semua bulan":
        previous_year = previous_year[previous_year["NamaBulan"].eq(month)]
    if not previous_year.empty:
        previous_year = previous_year[previous_year["Kabupaten"].isin(harga["Kabupaten"].unique())]
    kpi = {
        "average": float(harga["Harga"].mean()),
        "maximum": int(harga["Harga"].max()),
        "minimum": int(harga["Harga"].min()),
        "regions": int(harga["Kabupaten"].nunique()),
        "last_kurs": int(jisdor.sort_values("Tanggal")["Kurs"].iloc[-1]) if not jisdor.empty else None,
    }
    previous_average = float(previous_year["Harga"].mean()) if not previous_year.empty else None
    columns = st.columns(5, gap="small")
    movement = _pct_change(kpi["average"], previous_average) or "Data terfilter"
    cards = [
        ("Harga rata-rata", rupiah(kpi["average"]), "<small>/kg</small>", "badge-cool", "Rata-rata", movement, "Rp", "#2F6BE4"),
        ("Harga tertinggi", rupiah(kpi["maximum"]), "<small>/kg</small>", "badge-warm", "Maks", "Periode terfilter", "↗", "#C24D4D"),
        ("Harga terendah", rupiah(kpi["minimum"]), "<small>/kg</small>", "badge-safe", "Min", "Periode terfilter", "↘", "#0F8A7E"),
        ("Jumlah kabupaten", integer(kpi["regions"]), "<small>wilayah</small>", "badge-cool", "Data", "Memiliki observasi", "⌖", "#8B5CF6"),
        ("JISDOR terakhir", rupiah(kpi["last_kurs"]), "<small>/ USD</small>", "badge-warm", "Kurs", "Data pendukung", "$", "#B7791F"),
    ]
    for column, card in zip(columns, cards):
        label, value, suffix, badge, badge_text, note, icon, accent = card
        with column:
            st.markdown(
                f"""
                <div class="kpi-card" style="--accent:{accent}">
                  <div class="kpi-head"><span class="kpi-label">{label}</span><span class="kpi-icon">{icon}</span></div>
                  <div class="kpi-value">{value}&nbsp;{suffix}</div>
                  <div class="kpi-note"><span class="kpi-badge {badge}">{badge_text}</span><span class="kpi-detail">{note}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_overview(
    harga: pd.DataFrame,
    jisdor: pd.DataFrame,
    month: str,
    year: int,
    full_harga: pd.DataFrame,
    *,
    show_kpi: bool = True,
    show_map: bool = True,
    show_trend: bool = True,
    show_comparison: bool = True,
    show_kmeans: bool = True,
    show_insight: bool = True,
    show_jisdor: bool = True,
) -> None:
    """Merender tampilan utama lengkap mengikuti referensi."""

    if show_kpi:
        render_kpi_strip(harga, jisdor, month, year, full_harga)
    if harga.empty:
        render_empty("Belum ada data harga untuk filter yang dipilih.")
        return

    total_average = float(harga["Harga"].mean())
    region_average = harga.groupby("Kabupaten")["Harga"].mean()
    top_region = region_average.idxmax() if not region_average.empty else "—"
    top_value = float(region_average.max()) if not region_average.empty else 0.0
    bottom_value = float(region_average.min()) if not region_average.empty else 0.0
    spread = top_value - bottom_value
    peak = harga.sort_values("Harga", ascending=False).iloc[0]
    region_count = int(harga["Kabupaten"].nunique())
    lowest_region = region_average.idxmin() if not region_average.empty else "—"

    # Peta choropleth harga (memakai histori penuh agar seluruh kabupaten terisi)
    if show_map:
        geojson = load_geojson_jateng()
        if geojson is not None:
            with st.container(key="map_card"):
                render_section_head("Peta Sebaran Harga Jawa Tengah", "Rata-rata harga historis per kabupaten (seluruh periode data)", "Histori penuh")
                summary_map = map_price_summary(full_harga)
                if summary_map.empty:
                    render_empty("Belum ada data harga untuk peta.")
                else:
                    st.plotly_chart(price_choropleth(geojson, summary_map), width="stretch", config={"displaylogo": False})

    # Tren dan perbandingan
    if show_trend or show_comparison:
        left, right = st.columns([1.42, 1], gap="medium")
        if show_trend:
            with left:
                with st.container(key="trend_card"):
                    render_section_head("Tren Harga Bawang Putih", "Fluktuasi harga harian rata-rata se-Jawa Tengah", f"{month} {year}" if month != "Semua bulan" else f"Tahun {year}")
                    st.plotly_chart(trend_chart(harga), width="stretch", config={"displaylogo": False})
                    st.markdown(
                        f'<div class="trend-foot"><span>Rerata se-Jateng: <b>{rupiah(total_average)}</b> /kg</span><span>Puncak: <b>{rupiah(peak["Harga"])}</b> · {peak["NamaBulan"]} {int(peak["Tahun"])}</span></div>',
                        unsafe_allow_html=True,
                    )
        if show_comparison:
            with right:
                with st.container(key="comparison_card"):
                    render_section_head("Perbandingan Harga Antarwilayah", "Kabupaten dengan harga rata-rata tertinggi", "8 wilayah")
                    st.plotly_chart(comparison_chart(harga), width="stretch", config={"displaylogo": False})
                    st.markdown(
                        f'<div class="comparison-foot"><div><span>Tertinggi</span><b>{top_region}</b></div><div><span>Terendah</span><b>{lowest_region}</b></div><div><span>Selisih</span><b>{rupiah(spread)}</b></div></div>',
                        unsafe_allow_html=True,
                    )

    # TAMBAHAN: Tabel Top 10 Kabupaten dengan Harga Tertinggi (full width di bawah)
    if show_comparison and not harga.empty:
        with st.container(key="top10_card"):
            st.markdown("**Top 10 Kabupaten/Kota dengan Harga Tertinggi**")
            top_regions = harga.groupby("Kabupaten")["Harga"].agg(["mean", "max", "count"]).reset_index()
            top_regions = top_regions.sort_values("mean", ascending=False).head(10)
            top_regions["mean"] = top_regions["mean"].apply(lambda x: f"Rp {x:,.0f}")
            top_regions["max"] = top_regions["max"].apply(lambda x: f"Rp {x:,.0f}")
            top_regions.columns = ["Kabupaten/Kota", "Rata-rata Harga", "Harga Tertinggi", "Jumlah Data"]
            
            # Tampilkan sebagai tabel vertikal dengan hide_index
            st.dataframe(
                top_regions,
                width="stretch",
                hide_index=True,
            )

    # K-Means dan insight
    if show_kmeans or show_insight:
        try:
            result = calculate_clustering(full_harga)
        except (ValueError, KeyError) as error:
            st.error(f"Analisis clustering belum dapat ditampilkan: {error}")
            return
        if show_kmeans:
            render_cluster_section(result)
        if show_insight:
            render_insight_section(result)

    # JISDOR
    if show_jisdor:
        render_jisdor_section(jisdor)


def cluster_characteristic(row: Any, mean_values: pd.Series, std_values: pd.Series) -> str:
    """Menyusun karakteristik cluster dari posisi relatif centroid."""

    mean_level = "tinggi" if row.Mean_Harga >= mean_values.median() else "rendah"
    std_level = "tinggi" if row.Std_Harga >= std_values.median() else "rendah"
    return f"Harga {mean_level}, variasi {std_level}"


def render_cluster_section(result: dict[str, Any]) -> None:
    """Merender blok K-Means pada dashboard utama."""

    render_section_head("K-Means Clustering", "Pengelompokan kabupaten/kota berdasarkan karakteristik harga bawang putih")
    left, right = st.columns([1.05, 1.15], gap="medium")
    with left:
        with st.container(key="cluster_chart_card"):
            st.markdown('<div class="surface-title">Visualisasi Cluster</div><div class="surface-note">Dimensi: rata-rata harga vs standar deviasi</div>', unsafe_allow_html=True)
            st.plotly_chart(clustering_scatter(result["features"], result["labels"]), width="stretch", config={"displaylogo": False})
            st.caption("Sumbu X: rata-rata harga (Rp/kg) · Sumbu Y: standar deviasi harga")
    with right:
        rows = []
        summary = result["summary"]
        for _, row in summary.sort_values("Mean_Harga", ascending=False).iterrows():
            rows.append({
                "cluster": cluster_label(row.Cluster),
                "members": f"{int(row.Jumlah)} kab/kota",
                "mean": rupiah(row.Mean_Harga),
                "std": rupiah(row.Std_Harga),
                "characteristic": cluster_characteristic(row, summary["Mean_Harga"], summary["Std_Harga"]),
            })
        render_cluster_table(rows, PALETTE)
        st.markdown('<div class="callout" style="margin-top:.6rem;"><b>Metode:</b> K-Means dengan fitur rata-rata harga dan standar deviasi historis. Jumlah cluster dipilih melalui Elbow Method.</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="metric-strip"><span>Silhouette Score <b>{result["silhouette"]:.3f}</b></span><span>Davies-Bouldin Index <b>{result["dbi"]:.3f}</b></span><span>K optimal <b>{result["k"]}</b></span></div>',
            unsafe_allow_html=True,
        )


def render_insight_section(result: dict[str, Any]) -> None:
    """Merender kartu business insight per cluster."""

    render_section_head("Business Insight", "Interpretasi karakteristik cluster untuk kebutuhan monitoring")
    summary = result["summary"].sort_values("Cluster").reset_index(drop=True)
    mean_rank = summary["Mean_Harga"].rank(ascending=False)
    std_rank = summary["Std_Harga"].rank(ascending=False)

    columns = st.columns(len(summary), gap="small")
    for position, (column, row) in enumerate(zip(columns, summary.itertuples(index=False))):
        members = str(row.Anggota).split(", ")
        if mean_rank.loc[position] == 1:
            monitoring = "Rata-rata harga tertinggi. Prioritaskan pemantauan pasokan dan stabilitas harga antarkabupaten."
        elif std_rank.loc[position] == 1:
            monitoring = "Variasi harga paling besar. Pantau kesenjangan harga dan pergerakan antarwilayah."
        else:
            monitoring = "Rata-rata harga relatif rendah. Gunakan sebagai pembanding dalam evaluasi distribusi harga."
        with column:
            render_insight_card(
                cluster_label(row.Cluster), int(row.Jumlah), rupiah(row.Mean_Harga), rupiah(row.Std_Harga),
                ", ".join(members[:5]) + (", dll." if len(members) > 5 else ""),
                monitoring, PALETTE[position % len(PALETTE)],
            )


def render_jisdor_section(jisdor: pd.DataFrame) -> None:
    """Merender blok JISDOR pada dashboard utama."""

    render_section_head("Informasi JISDOR", "Data pendukung nilai tukar USD/IDR")
    if jisdor.empty:
        render_empty("Belum ada data JISDOR untuk periode yang dipilih.")
        return
    latest = jisdor.sort_values("Tanggal").iloc[-1]
    left, right = st.columns([1.15, 1], gap="medium")
    with left:
        render_jisdor_note(rupiah(latest["Kurs"]), latest["Tanggal"].strftime("%d %B %Y"))
    with right:
        with st.container(key="jisdor_chart_card"):
            st.markdown('<div class="surface-title">Pergerakan Kurs</div><div class="surface-note">Nilai tukar referensi Bank Indonesia pada periode terfilter</div>', unsafe_allow_html=True)
            st.plotly_chart(jisdor_chart(jisdor), width="stretch", config={"displaylogo": False})


def render_trend_page(harga: pd.DataFrame) -> None:
    """Merender halaman detail tren harga."""

    render_section_head("Tren harga harian", "Gunakan zoom untuk membaca periode tertentu")
    if harga.empty:
        render_empty()
        return
    show_average = st.toggle("Tampilkan rata-rata bergerak 30 hari", value=False)
    st.plotly_chart(trend_chart(harga, show_average), width="stretch", config={"displaylogo": False})
    st.caption("Rata-rata bergerak bersifat deskriptif; dashboard tidak melakukan forecasting.")


def render_comparison_page(harga: pd.DataFrame) -> None:
    """Merender halaman perbandingan antarwilayah."""

    if harga.empty:
        render_empty()
        return
    render_section_head("Perbandingan antarwilayah", "Posisi relatif rata-rata harga setiap kabupaten", f"{harga['Kabupaten'].nunique()} wilayah")
    st.plotly_chart(comparison_chart(harga), width="stretch", config={"displaylogo": False})


def render_monitoring_page(harga: pd.DataFrame) -> None:
    """Merender halaman pemantauan harga harian detail."""

    render_section_head("Pemantauan Harga Harian", "Detail harga bawang putih per kabupaten/kota dan tanggal")

    if harga.empty:
        render_empty("Belum ada data harga untuk filter yang dipilih.")
        return

    # Statistik ringkas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Observasi", integer(len(harga)))
    with col2:
        st.metric("Kabupaten/Kota", integer(harga["Kabupaten"].nunique()))
    with col3:
        rentang = f"{harga['Tanggal'].min().strftime('%d/%m/%Y')} - {harga['Tanggal'].max().strftime('%d/%m/%Y')}"
        st.metric("Rentang Tanggal", rentang)

    # Tabel harga harian
    display_data = harga[["Tanggal", "Kabupaten", "Harga"]].copy()
    display_data = display_data.sort_values(["Tanggal", "Kabupaten"], ascending=[False, True])
    display_data["Harga"] = display_data["Harga"].apply(rupiah)
    display_data["Tanggal"] = display_data["Tanggal"].dt.strftime("%d %B %Y")

    st.dataframe(
        display_data,
        width="stretch",
        hide_index=True,
        column_config={
            "Tanggal": "Tanggal",
            "Kabupaten": "Kabupaten/Kota",
            "Harga": "Harga (Rp/kg)",
        },
    )

    # Analisis outlier dengan validasi PIHPS
    render_section_head("Analisis Outlier dengan Validasi PIHPS", "Deteksi harga ekstrem (IQR) dan pembandingan dengan PIHPS Bank Indonesia")
    try:
        outliers = analisis_outlier_pihps(harga)
    except Exception as error:  # noqa: BLE001 - fallback UI
        st.error(f"Analisis outlier belum dapat ditampilkan: {error}")
        outliers = pd.DataFrame()

    if outliers.empty:
        render_empty("Tidak ditemukan outlier pada data yang tersedia.")
    else:
        n_ekstrem = int(outliers["Status"].eq("Outlier ekstrem").sum())
        n_selisih_tinggi = int(outliers["Status"].eq("Selisih tinggi").sum())
        col_o1, col_o2, col_o3 = st.columns(3)
        with col_o1:
            st.metric("Outlier Teratas", integer(len(outliers)))
        with col_o2:
            st.metric("Outlier Ekstrem (>100%)", integer(n_ekstrem))
        with col_o3:
            st.metric("Selisih Tinggi (20-100%)", integer(n_selisih_tinggi))

        st.dataframe(
            outliers,
            width="stretch",
            hide_index=True,
            column_config={
                "Tanggal": "Tanggal",
                "Kabupaten": "Kabupaten/Kota",
                "Harga": "Harga SIHATI (Rp/kg)",
                "Referensi PIHPS": "Referensi PIHPS (Rp/kg)",
                "Selisih (%)": "Selisih (%)",
                "Status": "Status",
                "Level": "Level Pembanding",
            },
        )
        st.caption(
            "Outlier diidentifikasi per kabupaten/kota menggunakan metode Interquartile Range (IQR) "
            "terhadap distribusi harga wilayah tersebut. Selisih dihitung terhadap rata-rata PIHPS "
            "kabupaten/kota bila tersedia, atau rata-rata PIHPS Provinsi Jawa Tengah pada periode yang "
            "sama untuk kabupaten yang tidak tercakup dalam PIHPS. Tabel menampilkan 20 outlier dengan "
            "harga tertinggi. Sumber referensi: PIHPS Bank Indonesia (https://www.bi.go.id/hargapangan)."
        )


def render_clustering_page(harga: pd.DataFrame) -> None:
    """Merender halaman analisis K-Means lengkap."""

    if harga.empty:
        render_empty()
        return
    try:
        result = calculate_clustering(harga)
    except (ValueError, KeyError) as error:
        st.error(f"Analisis clustering belum dapat ditampilkan: {error}")
        return

    # Section 1: Scatter Plot Cluster
    render_cluster_section(result)

    # Section 2: Evaluasi Cluster (Silhouette Plot + Metrik)
    render_section_head("Evaluasi Hasil Clustering", "Silhouette Plot dan metrik evaluasi cluster")
    col_plot, col_metrics = st.columns([2, 1])
    with col_plot:
        st.plotly_chart(
            silhouette_plot(result["features"], result["labels"], result["k"]),
            width="stretch",
            config={"displaylogo": False},
        )
    with col_metrics:
        st.metric("Silhouette Score", f"{result['silhouette']:.3f}")
        st.metric("Davies-Bouldin Index", f"{result['dbi']:.3f}")
        st.metric("Jumlah Cluster Optimal", result["k"])

    # Section 3: Box Plot Profiling Cluster
    render_section_head("Profil Distribusi Harga per Cluster", "Box plot menunjukkan distribusi harga pada setiap cluster")

    # Filter tahun untuk box plot per bulan
    tahun_tersedia = sorted(harga["Tahun"].unique(), reverse=True)
    tahun_dipilih = st.selectbox("Pilih Tahun untuk Analisis per Bulan", tahun_tersedia, index=0, key="boxplot_tahun")

    col_box1, col_box2 = st.columns(2)
    with col_box1:
        st.markdown("**Distribusi Harga per Cluster (Keseluruhan)**")
        st.plotly_chart(
            cluster_boxplot(harga, result["labels"]),
            width="stretch",
            config={"displaylogo": False},
        )
    with col_box2:
        st.markdown(f"**Distribusi Harga per Cluster per Bulan ({tahun_dipilih})**")
        st.plotly_chart(
            cluster_boxplot_by_month(harga, result["labels"], tahun_dipilih),
            width="stretch",
            config={"displaylogo": False},
        )

    # Section 4: Elbow Method
    render_section_head("Elbow Method", "Penentuan jumlah cluster dari penurunan WCSS")
    st.plotly_chart(elbow_chart(result["elbow"], result["k"]), width="stretch", config={"displaylogo": False})
    st.caption("Cluster memakai data historis penuh. Filter halaman hanya memengaruhi monitoring deskriptif.")


def render_insight_page(harga: pd.DataFrame) -> None:
    """Merender halaman business insight."""

    if harga.empty:
        render_empty()
        return
    try:
        result = calculate_clustering(harga)
    except (ValueError, KeyError) as error:
        st.error(f"Insight belum dapat ditampilkan: {error}")
        return
    render_insight_section(result)
    st.markdown('<div class="callout" style="margin-top:1rem;"><b>Cara membaca:</b> cluster menunjukkan kemiripan pola statistik harga, bukan hubungan sebab-akibat dan bukan rekomendasi kebijakan otomatis.</div>', unsafe_allow_html=True)


def render_jisdor_page(jisdor: pd.DataFrame) -> None:
    """Merender halaman informasi JISDOR."""

    if jisdor.empty:
        render_empty("Belum ada data JISDOR untuk filter waktu yang dipilih.")
        return
    render_jisdor_section(jisdor)

