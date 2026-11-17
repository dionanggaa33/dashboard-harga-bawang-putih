def summarize(features, labels):
    d=features.merge(labels,on="Kabupaten"); s=d.groupby("Cluster").agg(Mean_Harga=("Mean_Harga","mean"),Std_Harga=("Std_Harga","mean"),Jumlah=("Kabupaten","count"),Anggota=("Kabupaten",lambda x:", ".join(sorted(x)))).reset_index()
    texts=[f"Cluster {r.Cluster} terdiri atas {r.Jumlah} kabupaten dengan rata-rata harga Rp{r.Mean_Harga:,.0f} dan variasi rata-rata Rp{r.Std_Harga:,.0f}. Anggota: {r.Anggota}." for r in s.itertuples()]
    return s,texts
