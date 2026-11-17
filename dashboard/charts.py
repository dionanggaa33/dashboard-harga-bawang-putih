"""Builder visualisasi Plotly dengan tema yang konsisten."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.metrics import silhouette_samples

PALETTE = ["#2F6BE4", "#0F8A7E", "#B7791F", "#8B5CF6", "#C24D4D"]
FONT = "DM Sans, sans-serif"


def base_layout(**overrides: object) -> dict[str, object]:
    """Menghasilkan konfigurasi layout Plotly dashboard."""

    layout: dict[str, object] = {
        "font": {"family": FONT, "color": "#475569", "size": 11},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "margin": {"l": 4, "r": 8, "t": 8, "b": 4},
        "hoverlabel": {"font": {"family": FONT, "size": 11}, "bgcolor": "#1E293B", "font_color": "#F8FAFC"},
        "legend": {"orientation": "h", "y": 1.1, "x": 0, "font": {"size": 10}},
        "xaxis": {"showgrid": False, "linecolor": "#E5EAF1", "zeroline": False, "tickfont": {"size": 9, "color": "#94A3B8"}},
        "yaxis": {"showgrid": True, "gridcolor": "#F1F4F8", "linecolor": "#E5EAF1", "zeroline": False, "tickfont": {"size": 9, "color": "#94A3B8"}},
    }
    layout.update(overrides)
    return layout


def trend_chart(data: pd.DataFrame, show_average: bool = False) -> go.Figure:
    """Membuat tren harga rata-rata harian se-Jawa Tengah dengan tema minimalist."""

    # Agregat rata-rata harian se-Jawa Tengah
    daily_avg = data.groupby("Tanggal", as_index=False)["Harga"].mean().sort_values("Tanggal")

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=daily_avg["Tanggal"],
            y=daily_avg["Harga"],
            mode="lines",
            name="Rata-rata harian",
            line={"color": "#2F6BE4", "width": 2},
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Harga: Rp %{y:,.0f}<extra></extra>",
        )
    )

    if show_average and not daily_avg.empty:
        daily_avg["MA30"] = daily_avg["Harga"].rolling(30, min_periods=1).mean()
        figure.add_trace(go.Scatter(
            x=daily_avg["Tanggal"],
            y=daily_avg["MA30"],
            mode="lines",
            name="Rata-rata bergerak 30 hari",
            line={"color": "#C24D4D", "width": 1.5, "dash": "dash"},
            hovertemplate="<b>%{x|%d %b %Y}</b><br>MA 30 hari: Rp %{y:,.0f}<extra></extra>",
        ))

    figure.update_layout(**base_layout(
        hovermode="x unified",
        height=330,
        showlegend=show_average,
        xaxis_rangeslider_visible=False,
        legend={"orientation": "h", "y": 1.1, "x": 0, "font": {"size": 10}} if show_average else {},
    ))
    figure.update_yaxes(
        tickprefix="Rp ",
        tickformat=",.0f",
        title={"text": "Harga (Rp/kg)", "font": {"size": 10}},
        nticks=5,
    )
    figure.update_xaxes(
        tickformat="%b %y",
        title={"text": "Tanggal", "font": {"size": 10}},
        nticks=6,
    )
    return figure


def comparison_chart(data: pd.DataFrame) -> go.Figure:
    """Membuat bar chart rata-rata harga per kabupaten dengan label nilai."""

    summary = data.groupby("Kabupaten", as_index=False)["Harga"].mean().sort_values("Harga", ascending=False)
    top = summary.head(8).sort_values("Harga")
    figure = go.Figure(go.Bar(
        x=top["Harga"], y=top["Kabupaten"], orientation="h",
        marker={"color": ["#2F6BE4"] * len(top), "line": {"width": 0}},
        text=[f"Rp {value:,.0f}".replace(",", ".") for value in top["Harga"]],
        textposition="outside",
        textfont={"size": 10, "color": "#334155"},
        cliponaxis=False,
        hovertemplate="%{y}<br>Rata-rata: Rp %{x:,.0f}<extra></extra>",
    ))
    figure.update_layout(**base_layout(height=330, showlegend=False, margin={"l": 4, "r": 62, "t": 6, "b": 4}))
    figure.update_xaxes(showticklabels=False, showgrid=False, title=None, range=[0, top["Harga"].max() * 1.24])
    figure.update_yaxes(showgrid=False, title=None, tickfont={"size": 10, "color": "#475569"})
    return figure


def heatmap_chart(data: pd.DataFrame) -> go.Figure:
    """Membuat heatmap rata-rata harga per bulan dan wilayah."""

    months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    pivot = data.pivot_table(index="Kabupaten", columns="NamaBulan", values="Harga", aggfunc="mean")
    pivot = pivot.reindex(columns=[month for month in months if month in pivot.columns]).sort_index()
    figure = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns, y=pivot.index,
        colorscale=[[0, "#F2F8F7"], [0.5, "#9DCFC6"], [1, "#0F625B"]],
        colorbar={"title": "Rp", "thickness": 8, "len": 0.7, "tickfont": {"size": 9}},
        hovertemplate="%{y}<br>%{x}<br>Rp %{z:,.0f}<extra></extra>",
    ))
    figure.update_layout(**base_layout(height=max(330, len(pivot) * 20), showlegend=False))
    figure.update_yaxes(showgrid=False, tickfont={"size": 8, "color": "#64748B"})
    figure.update_xaxes(tickfont={"size": 8})
    return figure


def clustering_scatter(features: pd.DataFrame, labels: pd.DataFrame) -> go.Figure:
    """Membuat scatter plot fitur clustering."""

    merged = features.merge(labels, on="Kabupaten")
    figure = go.Figure()
    for cluster, group in merged.groupby("Cluster", sort=True):
        figure.add_trace(go.Scatter(
            x=group["Mean_Harga"], y=group["Std_Harga"], mode="markers", name=f"Cluster {cluster}",
            marker={"size": 10, "color": PALETTE[int(cluster) % len(PALETTE)],
                    "line": {"width": 1.5, "color": "white"}},
            customdata=group["Kabupaten"],
            hovertemplate="%{customdata}<br>Rata-rata: Rp %{x:,.0f}<br>Std. deviasi: Rp %{y:,.0f}<extra></extra>",
        ))
    figure.update_layout(**base_layout(height=320, showlegend=True,
                                       legend={"orientation": "h", "y": 1.16, "x": 0, "font": {"size": 9}}))
    figure.update_xaxes(title={"text": "Rata-rata harga (Rp/kg)", "font": {"size": 9, "color": "#94A3B8"}},
                        tickprefix="Rp ", tickformat=",.0f", nticks=5)
    figure.update_yaxes(title={"text": "Std. deviasi (Rp/kg)", "font": {"size": 9, "color": "#94A3B8"}},
                        tickprefix="Rp ", tickformat=",.0f", nticks=5)
    return figure


def elbow_chart(elbow_data: list[dict[str, float]], optimal_k: int) -> go.Figure:
    """Membuat grafik WCSS dengan penanda k optimal."""

    data = pd.DataFrame(elbow_data)
    figure = go.Figure(go.Scatter(
        x=data["K"], y=data["WCSS"], mode="lines+markers", name="WCSS",
        line={"color": "#2F6BE4", "width": 2.2}, marker={"size": 6, "color": "#2F6BE4"},
        hovertemplate="K = %{x}<br>WCSS = %{y:,.2f}<extra></extra>",
    ))
    optimal = data[data["K"].eq(optimal_k)]
    if not optimal.empty:
        figure.add_trace(go.Scatter(
            x=optimal["K"], y=optimal["WCSS"], mode="markers", name=f"K optimal = {optimal_k}",
            marker={"size": 12, "color": "#B7791F", "line": {"width": 2.5, "color": "white"}},
        ))
    figure.update_layout(**base_layout(height=320, showlegend=False))
    figure.update_xaxes(title={"text": "Jumlah cluster (K)", "font": {"size": 9, "color": "#94A3B8"}}, dtick=1)
    figure.update_yaxes(title={"text": "WCSS", "font": {"size": 9, "color": "#94A3B8"}}, tickformat=",.0f", nticks=5)
    return figure


def silhouette_plot(features: pd.DataFrame, labels: pd.DataFrame, k: int) -> go.Figure:
    """Membuat silhouette plot untuk evaluasi cluster."""

    X = features[["Mean_Harga", "Std_Harga"]].values
    silhouette_vals = silhouette_samples(X, labels["Cluster"])

    figure = go.Figure()
    y_lower = 10
    for i in range(k):
        cluster_silhouette = silhouette_vals[labels["Cluster"] == i]
        cluster_silhouette.sort()
        y_upper = y_lower + len(cluster_silhouette)
        figure.add_trace(go.Bar(
            x=cluster_silhouette,
            y=list(range(y_lower, y_upper)),
            orientation="h",
            name=f"Cluster {i}",
            marker_color=PALETTE[i % len(PALETTE)],
            hovertemplate=f"Cluster {i}<br>Silhouette: %{{x:.3f}}<extra></extra>",
        ))
        y_lower = y_upper + 10

    avg_score = float(silhouette_vals.mean())
    figure.add_vline(
        x=avg_score,
        line_dash="dash",
        line_color="#C24D4D",
        annotation_text=f"Rata-rata: {avg_score:.3f}",
        annotation_position="top right",
    )

    figure.update_layout(**base_layout(
        height=320,
        showlegend=True,
        legend={"orientation": "h", "y": 1.1, "x": 0, "font": {"size": 10}},
        margin={"l": 60, "r": 30, "t": 40, "b": 50},
    ))
    figure.update_xaxes(
        title={"text": "Nilai Silhouette", "font": {"size": 10}},
        range=[-0.2, 1],
        showgrid=True,
        gridcolor="#F1F4F8",
    )
    figure.update_yaxes(
        title={"text": "Cluster", "font": {"size": 10}},
        showticklabels=False,
        showgrid=False,
    )
    return figure


def cluster_boxplot(harga: pd.DataFrame, labels: pd.DataFrame) -> go.Figure:
    """Membuat box plot distribusi harga per cluster."""

    data = harga.merge(labels, on="Kabupaten")

    figure = go.Figure()
    for cluster, group in data.groupby("Cluster", sort=True):
        figure.add_trace(go.Box(
            y=group["Harga"],
            name=f"Cluster {cluster}",
            marker_color=PALETTE[int(cluster) % len(PALETTE)],
            boxpoints="outliers",
            hovertemplate=f"Cluster {cluster}<br>Harga: Rp %{{y:,.0f}}<extra></extra>",
        ))

    figure.update_layout(**base_layout(
        height=320,
        showlegend=True,
        legend={"orientation": "h", "y": 1.1, "x": 0, "font": {"size": 10}},
        margin={"l": 60, "r": 30, "t": 40, "b": 50},
    ))
    figure.update_yaxes(
        title={"text": "Harga (Rp/kg)", "font": {"size": 10}},
        tickprefix="Rp ",
        tickformat=",.0f",
        nticks=5,
    )
    figure.update_xaxes(
        title={"text": "Cluster", "font": {"size": 10}},
    )
    return figure


def cluster_boxplot_by_month(harga: pd.DataFrame, labels: pd.DataFrame, tahun: int = None) -> go.Figure:
    """Membuat box plot distribusi harga per cluster per bulan."""

    data = harga.merge(labels, on="Kabupaten")

    if tahun:
        data = data[data["Tahun"] == tahun]

    bulan_order = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                   "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    bulan_tersedia = [b for b in bulan_order if b in data["NamaBulan"].unique()]

    figure = go.Figure()
    for cluster, group in data.groupby("Cluster", sort=True):
        figure.add_trace(go.Box(
            x=group["NamaBulan"],
            y=group["Harga"],
            name=f"Cluster {cluster}",
            marker_color=PALETTE[int(cluster) % len(PALETTE)],
            boxpoints="outliers",
            hovertemplate=f"Cluster {cluster}<br>Bulan: %{{x}}<br>Harga: Rp %{{y:,.0f}}<extra></extra>",
        ))

    figure.update_layout(**base_layout(
        height=400,
        showlegend=True,
        legend={"orientation": "h", "y": 1.1, "x": 0, "font": {"size": 10}},
        margin={"l": 60, "r": 30, "t": 60, "b": 60},
    ))
    figure.update_yaxes(
        title={"text": "Harga (Rp/kg)", "font": {"size": 10}},
        tickprefix="Rp ",
        tickformat=",.0f",
        nticks=5,
    )
    figure.update_xaxes(
        title={"text": "Bulan", "font": {"size": 10}},
        categoryorder="array",
        categoryarray=bulan_tersedia,
    )
    return figure


def detect_outliers_iqr(data: pd.DataFrame) -> pd.DataFrame:
    """Mendeteksi outlier harga menggunakan metode IQR."""

    Q1 = data["Harga"].quantile(0.25)
    Q3 = data["Harga"].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = data[(data["Harga"] < lower_bound) | (data["Harga"] > upper_bound)].copy()
    outliers["Batas_Bawah"] = lower_bound
    outliers["Batas_Atas"] = upper_bound
    outliers["Keterangan"] = outliers["Harga"].apply(
        lambda x: "Di atas batas atas" if x > upper_bound else "Di bawah batas bawah"
    )
    return outliers


# Referensi rata-rata PIHPS per periode (data statis dari Bank Indonesia).
# Dihitung dari rata-rata harga 12 kabupaten/kota yang tersedia di PIHPS.
PIHPS_DATA: dict[str, dict[str, object]] = {
    "2020-02": {"periode": "Februari 2020", "rata_provinsi": 48598},
    "2020-03": {"periode": "Maret 2020", "rata_provinsi": 43159},
    "2025-03": {"periode": "Maret 2025", "rata_provinsi": 43983},
}

# Pemetaan kabupaten SIHATI -> nama PIHPS yang tersedia (12 kabupaten/kota).
PIHPS_KABUPATEN_MAP: dict[str, str] = {
    "Banyumas": "Kab. Banyumas",
    "Boyolali": "Kab. Boyolali",
    "Cilacap": "Kab. Cilacap",
    "Karanganyar": "Kab. Karanganyar",
    "Klaten": "Kab. Klaten",
    "Kudus": "Kab. Kudus",
    "Semarang": "Kota Semarang",
    "Sragen": "Kab. Sragen",
    "Sukoharjo": "Kab. Sukoharjo",
    "Surakarta": "Kota Surakarta (Solo)",
    "Tegal": "Kota Tegal",
    "Wonogiri": "Kab. Wonogiri",
}


def load_pihps_data() -> dict | None:
    """Memuat data PIHPS per kabupaten dari file JSON statis."""

    import json
    from pathlib import Path

    pihps_path = Path(__file__).resolve().parents[1] / "data" / "pihps_kab.json"
    try:
        with pihps_path.open(encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return None


def analisis_outlier_pihps(data: pd.DataFrame, batas_tampil: int = 20) -> pd.DataFrame:
    """Analisis outlier IQR yang divalidasi dengan referensi PIHPS.

    Outlier diidentifikasi per kabupaten/kota menggunakan IQR terhadap
    distribusi harga wilayah tersebut sendiri. Setiap outlier kemudian
    dibandingkan dengan rata-rata PIHPS: jika kabupaten tersedia di PIHPS
    digunakan rata-rata kabupaten pada periode sama, jika tidak tersedia
    digunakan rata-rata PIHPS provinsi pada periode sama (bila ada data).
    """

    if data.empty:
        return pd.DataFrame()

    pihps_raw = load_pihps_data()
    harga = data.copy()
    harga["Tanggal"] = pd.to_datetime(harga["Tanggal"])

    pihps_period_keys: dict[tuple[int, int], str] = {(2020, 2): "2020-02", (2020, 3): "2020-03", (2025, 3): "2025-03"}

    rows = []
    for kabupaten, group in harga.groupby("Kabupaten"):
        Q1 = group["Harga"].quantile(0.25)
        Q3 = group["Harga"].quantile(0.75)
        IQR = Q3 - Q1
        upper_bound = Q3 + 1.5 * IQR
        lower_bound = Q1 - 1.5 * IQR

        outliers = group[(group["Harga"] > upper_bound) | (group["Harga"] < lower_bound)]
        nama_pihps = PIHPS_KABUPATEN_MAP.get(str(kabupaten))

        for _, row in outliers.iterrows():
            tanggal = pd.Timestamp(row["Tanggal"])
            periode_key = pihps_period_keys.get((tanggal.year, tanggal.month))
            pihps_prov = PIHPS_DATA.get(periode_key, {}).get("rata_provinsi") if periode_key else None

            pihps_kab_avg = None
            if pihps_raw is not None and nama_pihps and periode_key and nama_pihps in pihps_raw:
                prices = pihps_raw[nama_pihps].get(periode_key, {})
                vals = [float(str(v).replace(",", "")) for v in prices.values()]
                pihps_kab_avg = sum(vals) / len(vals) if vals else None

            pembanding = pihps_kab_avg if pihps_kab_avg is not None else pihps_prov
            level = "kabupaten" if pihps_kab_avg is not None else "provinsi"

            if pembanding is None:
                rows.append({
                    "Tanggal": tanggal.strftime("%d/%m/%Y"),
                    "Kabupaten": kabupaten,
                    "Harga": int(row["Harga"]),
                    "Referensi PIHPS": None,
                    "Selisih (%)": None,
                    "Status": "Tanpa referensi PIHPS",
                    "Level": level,
                })
                continue

            selisih_persen = (row["Harga"] - pembanding) / pembanding * 100
            if abs(selisih_persen) > 100:
                status = "Outlier ekstrem"
            elif abs(selisih_persen) > 20:
                status = "Selisih tinggi"
            else:
                status = "Selisih moderat"
            rows.append({
                "Tanggal": tanggal.strftime("%d/%m/%Y"),
                "Kabupaten": kabupaten,
                "Harga": int(row["Harga"]),
                "Referensi PIHPS": int(round(pembanding)),
                "Selisih (%)": round(selisih_persen, 1),
                "Status": status,
                "Level": level,
            })

    result = pd.DataFrame(rows)
    if result.empty:
        return result
    return result.sort_values("Harga", ascending=False).head(batas_tampil).reset_index(drop=True)


def validasi_outlier_pihps(data: pd.DataFrame) -> pd.DataFrame:
    """Validasi outlier dengan referensi PIHPS untuk periode Maret 2020.
    
    PIHPS memberikan data agregat Jawa Tengah, sehingga perbandingan dilakukan
    antara rata-rata SIHATI dengan rata-rata PIHPS.
    """

    # REFERENSI PIHPS: Maret 2020 (dari https://www.bi.go.id/hargapangan)
    # Data: Bawang Putih, Jawa Tengah, Semua Kabupaten/Kota
    PIHPS_MARET_2020 = {
        "02/03/2020": 43750,
        "03/03/2020": 43750,
        "04/03/2020": 43650,
        "05/03/2020": 43500,
        "06/03/2020": 43300,
        "09/03/2020": 42450,
        "10/03/2020": 42400,
    }
    
    # Rata-rata PIHPS awal Maret 2020
    rata_pihps = sum(PIHPS_MARET_2020.values()) / len(PIHPS_MARET_2020)
    
    # Filter data Maret 2020
    maret_2020 = data[
        (data["Tanggal"].dt.year == 2020) & 
        (data["Tanggal"].dt.month == 3)
    ].copy()
    
    if maret_2020.empty:
        return pd.DataFrame()
    
    # Rata-rata SIHATI Maret 2020
    rata_sihati = maret_2020["Harga"].mean()
    
    # Deteksi outlier IQR di Maret 2020
    Q1 = maret_2020["Harga"].quantile(0.25)
    Q3 = maret_2020["Harga"].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = maret_2020[maret_2020["Harga"] > upper_bound].copy()
    
    if outliers.empty:
        return outliers
    
    # Tambahkan validasi PIHPS
    outliers["Harga_Rata_SIHATI"] = rata_sihati
    outliers["Harga_PIHPS"] = rata_pihps
    outliers["Selisih_vs_PIHPS"] = outliers["Harga"] - rata_pihps
    outliers["Selisih_Persen"] = (outliers["Selisih_vs_PIHPS"] / rata_pihps) * 100
    outliers["Validasi"] = outliers["Selisih_Persen"].apply(
        lambda x: "Tidak Valid" if x > 100 else "Perlu Cek"  # Threshold 100% untuk outlier ekstrem
    )
    outliers["Sumber_Validasi"] = "PIHPS Bank Indonesia (Rata-rata Jawa Tengah)"
    outliers["Catatan"] = "PIHPS adalah agregat provinsi, SIHATI adalah per kabupaten"
    
    return outliers


def jisdor_chart(data: pd.DataFrame) -> go.Figure:
    """Membuat line chart nilai JISDOR dengan skala sumbu Y sesuai rentang data."""

    figure = go.Figure(go.Scatter(
        x=data["Tanggal"], y=data["Kurs"], mode="lines", name="JISDOR",
        line={"color": "#2F6BE4", "width": 2.0},
        hovertemplate="%{x|%d %b %Y}<br>Rp %{y:,.0f} / USD<extra></extra>",
    ))
    figure.update_layout(**base_layout(height=300, hovermode="x unified", showlegend=False))
    figure.update_yaxes(
        tickprefix="Rp ", tickformat=",.0f", nticks=5,
        # Mulai dari sedikit di bawah nilai terendah, bukan dari nol
        range=[data["Kurs"].min() * 0.97, data["Kurs"].max() * 1.02] if not data.empty else None,
    )
    figure.update_xaxes(tickformat="%b %y", nticks=6)
    return figure


def price_choropleth(geojson: dict, summary: pd.DataFrame) -> go.Figure:
    """Choropleth rata-rata harga bawang putih per kabupaten Jawa Tengah dengan legenda lengkap."""

    import plotly.express as px

    if summary.empty:
        return go.Figure()

    minimum = float(summary["RataHarga"].min())
    maximum = float(summary["RataHarga"].max())
    
    # TAMBAHAN: Kategori harga berdasarkan kuartil
    q1 = float(summary["RataHarga"].quantile(0.25))
    q2 = float(summary["RataHarga"].quantile(0.50))
    q3 = float(summary["RataHarga"].quantile(0.75))
    
    # Buat kategori untuk legenda
    def kategori_harga(harga):
        if harga < q1:
            return "Rendah"
        elif harga < q2:
            return "Sedang"
        elif harga < q3:
            return "Tinggi"
        else:
            return "Sangat Tinggi"
    
    summary["Kategori"] = summary["RataHarga"].apply(kategori_harga)
    
    # Warna sesuai kategori
    color_map = {
        "Rendah": "#9CC3E5",      # Biru muda
        "Sedang": "#4A90D9",       # Biru
        "Tinggi": "#F2C94C",       # Kuning
        "Sangat Tinggi": "#E74C3C" # Merah
    }
    
    figure = px.choropleth(
        summary,
        geojson=geojson,
        locations="Kabupaten",
        featureidkey="properties.name",
        color="Kategori",
        color_discrete_map=color_map,
        category_orders={"Kategori": ["Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]},
        labels={"Kategori": "Kategori Harga"},
        custom_data=["RataHarga"],
    )

    figure.update_geos(
        fitbounds="locations",
        visible=True,
        bgcolor="rgba(0,0,0,0)",
        showcoastlines=False,
        showland=False,
        showcountries=False,
        showsubunits=True,
        subunitcolor="#E5EAF1",
    )

    figure.update_traces(
        marker_line_color="#FFFFFF",
        marker_line_width=0.8,
        hovertemplate="<b>%{location}</b><br>Rata-rata: Rp %{customdata[0]:,.0f} /kg<extra></extra>",
    )
    
    # TAMBAHAN: Layout dengan legenda dan keterangan
    layout_override = base_layout(
        height=620,
        margin={"l": 10, "r": 10, "t": 50, "b": 80},
    )
    # Hapus legend default dari base_layout karena kita pakai custom
    layout_override.pop("legend", None)
    
    figure.update_layout(
        **layout_override,
        title=dict(
            text="Peta Sebaran Harga Bawang Putih Jawa Tengah",
            x=0.5,
            xanchor="center",
            font={"size": 13, "color": "#1E293B"},
        ),
        legend=dict(
            title=dict(
                text="Kategori Harga",
                font={"size": 11, "color": "#475569"},
            ),
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font={"size": 10, "color": "#475569"},
        ),
        annotations=[
            {
                "text": f"Rentang: Rp {minimum:,.0f} — Rp {maximum:,.0f} /kg",
                "xref": "paper", "yref": "paper", "x": 0, "y": -0.08,
                "showarrow": False, "font": {"size": 10, "color": "#64748B"}, "align": "left",
            },
            {
                "text": "Kategori berdasarkan kuartil: Q1 (25%), Q2 (50%), Q3 (75%)",
                "xref": "paper", "yref": "paper", "x": 1, "y": -0.08,
                "showarrow": False, "font": {"size": 9, "color": "#94A3B8"}, "align": "right",
                "xanchor": "right",
            },
            {
                "text": "Sumber: SIHATI Provinsi Jawa Tengah",
                "xref": "paper", "yref": "paper", "x": 0, "y": -0.12,
                "showarrow": False, "font": {"size": 9, "color": "#94A3B8"}, "align": "left",
            },
        ],
    )
    
    return figure
