import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

data_day = pd.read_csv("data_ready_day.csv")
data_hour = pd.read_csv("data_ready_hour.csv")

weather_mapping = {
    1: "Clear",
    2: "Mist",
    3: "Light Rain/Snow",
    4: "Heavy Rain/Snow"
}

data_day["weather_name"] = data_day["weathersit"].map(weather_mapping)

with st.sidebar:
    option = st.selectbox(
        "Choose Weather",
        ["All"] + list(set(weather_mapping.values())),
        placeholder="Weather..."
    )
    start_date = st.date_input("Start Date", datetime.datetime(2011, 1, 1))
    end_date = st.date_input("End Date", datetime.datetime(2012, 12, 31))

st.title("Dashboard")
tab1, tab2 = st.tabs(["Cuaca dengan Penyewaan", "Distribusi Penyewaan"])

with tab1:
    # st.header()
    if option != "All":
        data_filtered = data_day[data_day['weather_name'] == option]
    else:
        data_filtered = data_day
    

    if data_filtered.empty:
        st.warning("Tidak ada data yang sesuai dengan pilihan cuaca!")
    else:
        summary_data = data_filtered.groupby("weather_name")["cnt"].agg(
            ["mean", "max", "min"]
        ).reset_index()
        
        summary_df_melted = summary_data.melt(id_vars="weather_name", var_name="Statistik", value_name="Value")

        st.subheader(f"Jumlah Penyewaan Sepeda pada Cuaca: {option}" if option else "Jumlah Penyewaan Sepeda per Kondisi Cuaca")
        
        fig, ax = plt.subplots(figsize=(8,5))
        sns.barplot(data=summary_df_melted, x="weather_name", y="Value", hue="Statistik", palette="Blues", ax=ax)
        ax.set_xlabel("Kondisi Cuaca")
        ax.set_ylabel("Total Penyewaan")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

        st.pyplot(fig)

        if option:
            total_cnt = data_filtered.groupby("weather_name")["cnt"].sum().iloc[0]
        else:
            total_cnt = data_filtered["cnt"].sum()

        formatted_cnt = f"{total_cnt:,}".replace(",", ".")
        st.metric(label=f"Total {option if option else 'Semua Cuaca'}", value=formatted_cnt, delta="Penyewa")

with tab2:
    st.subheader("Distribusi Penyewaan Sepeda Berdasarkan Jam")
    data_hour_filtered = data_hour[(data_hour['dteday'] >= str(start_date)) & (data_hour['dteday'] <= str(end_date))]
    if data_hour_filtered.empty:
        st.warning("Tidak ada data untuk rentang tanggal yang dipilih!")
    else:
        fig, ax = plt.subplots(figsize=(10,6))
        sns.barplot(x='Jam', y='Rata-rata penyewa', data=data_hour_filtered, ax=ax, palette="coolwarm")
        st.pyplot(fig)

    rental_per_hour = data_hour_filtered.groupby("hr")["cnt"].sum().reset_index()

    peak_hour = data_hour_filtered.loc[rental_per_hour["cnt"].idxmax(), "hr"]
    low_hour = data_hour_filtered.loc[rental_per_hour["cnt"].idxmin(),"hr"]

    st.markdown("### Insight Penyewaan Sepeda")
    st.write(f"- Penyewaan tertinggi terjadi pada pukul **{peak_hour}:00**, kemungkinan karena jam pulang kerja atau aktivitas sore.")
    st.write(f"- Penyewaan terendah terjadi pada pukul **{low_hour}:00**, menunjukkan sedikitnya pengguna saat itu.")
    st.write("- Tren menunjukkan peningkatan penggunaan di pagi dan sore hari, mencerminkan pola aktivitas harian masyarakat.")

