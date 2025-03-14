import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Load dataset dengan cache
@st.cache_data
def load_data():
    # Gunakan path relatif agar bisa berjalan di Streamlit Cloud
    file_path = os.path.join(os.path.dirname(__file__), "all_data.csv")
    
    if not os.path.exists(file_path):
        st.error(f"File {file_path} tidak ditemukan. Pastikan file telah diunggah.")
        return pd.DataFrame()  # Mengembalikan dataframe kosong jika file tidak ditemukan
    
    all_df = pd.read_csv(file_path)
    all_df['dteday'] = pd.to_datetime(all_df['dteday'])  # Konversi ke datetime
    return all_df

# Panggil fungsi load_data
all_df = load_data()

if all_df.empty:
    st.stop()  # Hentikan eksekusi jika data kosong

# Sidebar filters
with st.sidebar:
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=all_df['dteday'].min(),
        max_value=all_df['dteday'].max(),
        value=[all_df['dteday'].min(), all_df['dteday'].max()]
    )
    season_filter = st.multiselect("Pilih Musim", options=[1, 2, 3, 4], default=[1, 2, 3, 4])
    holiday_filter = st.checkbox("Hanya Hari Libur")
    workingday_filter = st.checkbox("Hanya Hari Kerja")
    hour_filter = st.slider("Pilih Rentang Jam", min_value=0, max_value=24, value=(0, 24))

# Apply filters
filtered_df = all_df[
    (all_df['dteday'] >= pd.to_datetime(start_date)) & 
    (all_df['dteday'] <= pd.to_datetime(end_date)) & 
    (all_df['season'].isin(season_filter))
]

if holiday_filter:
    filtered_df = filtered_df[filtered_df['holiday'] == 1]
if workingday_filter:
    filtered_df = filtered_df[filtered_df['workingday'] == 1]

filtered_df = filtered_df[(filtered_df['hr'] >= hour_filter[0]) & (filtered_df['hr'] <= hour_filter[1])]

# Dashboard title
st.header('Bike Sharing Dashboard 🚴')
st.write("Analisis Data Penyewaan Sepeda")
st.write("By : Naomi Sitanggang")

# Statistik utama
st.subheader('📊 Statistik Penyewaan Sepeda')
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Penyewaan", value=filtered_df['cnt'].sum())
with col2:
    st.metric("Rata-rata Penyewaan", value=round(filtered_df['cnt'].mean(), 2))
with col3:
    st.metric("Total Casual Users", value=filtered_df["casual"].sum())
with col4:
    st.metric("Total Registered Users", value=filtered_df["registered"].sum())

# Grafik Perbandingan Tren Penyewaan antar Tahun
st.subheader("📅 Tren Penyewaan Sepeda Antar Tahun")
fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(data=filtered_df, x="dteday", y="cnt", hue="yr", ax=ax)
plt.xticks(rotation=45)
st.pyplot(fig)


# Grafik Penyewaan Berdasarkan Musim
st.subheader("🍂 Penyewaan Sepeda Berdasarkan Musim")
fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x=filtered_df['season'].map({1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}), 
            y=filtered_df['cnt'], estimator=np.median, palette='coolwarm', ax=ax)
ax.set_xlabel("Musim")
ax.set_ylabel("Median Penyewaan")
st.pyplot(fig)

# Grafik Penyewaan Berdasarkan Hari
st.subheader("📅 Penyewaan Sepeda Berdasarkan Hari")
fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x=filtered_df['weekday'].map({0: "Minggu", 1: "Senin", 2: "Selasa", 3: "Rabu", 
                                          4: "Kamis", 5: "Jumat", 6: "Sabtu"}), 
            y=filtered_df['cnt'], estimator=np.median, palette='viridis', ax=ax)
ax.set_xlabel("Hari")
ax.set_ylabel("Median Penyewaan")
st.pyplot(fig)

# Grafik Penyewaan Sepeda per Jam
st.subheader("⏰ Penyewaan Sepeda per Jam")
fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(x=filtered_df['hr'], y=filtered_df['cnt'], palette="coolwarm", marker='o', linewidth=2, ax=ax)
ax.set_xlabel("Jam")
ax.set_ylabel("Total Penyewaan")
ax.set_title("Pola Penyewaan per Jam (Data Gabungan)")
ax.axvline(x=8, color='#e74c3c', linestyle='--', label='Puncak Pagi')
ax.axvline(x=17, color='#e74c3c', linestyle='--', label='Puncak Sore')
ax.legend()
st.pyplot(fig)

# Grafik Penyewaan Berdasarkan Bulan
st.subheader("📆 Penyewaan Sepeda Berdasarkan Bulan")
monthly_avg = filtered_df.groupby("mnth")["cnt"].mean().reset_index()
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x="mnth", y="cnt", data=monthly_avg, ax=ax, palette="Set2")
ax.set_xlabel("Bulan")
ax.set_ylabel("Rata-rata Penyewaan")
st.pyplot(fig)

# Grafik Penyewaan Hari Kerja vs Hari Libur
st.subheader("🏢 Penyewaan Sepeda di Hari Kerja vs. Hari Libur")
fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(x=['Hari Kerja', 'Hari Libur'], 
            y=[filtered_df['workingday'].sum(), filtered_df['holiday'].sum()], 
            palette=["#90CAF9", "#D3D3D3"], ax=ax)
ax.set_ylabel("Total Penyewaan")
st.pyplot(fig)

# Clustering berdasarkan jumlah penyewaan
all_df['cluster'] = pd.qcut(all_df['cnt'], q=2, labels=['Rendah', 'Tinggi'])

st.subheader("Distribusi Clustering Penyewaan Sepeda")
st.write(all_df['cluster'].value_counts())
fig, ax = plt.subplots(figsize=(8, 5))
sns.countplot(data=all_df, x='cluster', palette=['red', 'blue'], ax=ax)
ax.set_xlabel("Cluster")
ax.set_ylabel("Jumlah Data")
ax.set_title("Distribusi Clustering Penyewaan Sepeda")
st.pyplot(fig)
