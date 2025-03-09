import os
import pandas as pd
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
    hour_filter = st.slider("Pilih Rentang Jam", min_value=0, max_value=23, value=(0, 23))

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

# Grafik Tren Penyewaan per Hari
st.subheader("📈 Tren Penyewaan Sepeda per Hari")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(filtered_df['dteday'], filtered_df['cnt'], marker='o', linewidth=2, color="#90CAF9")
ax.set_xlabel("Tanggal")
ax.set_ylabel("Total Penyewaan")
st.pyplot(fig)

# Grafik Penyewaan Berdasarkan Musim
st.subheader("🍂 Penyewaan Sepeda Berdasarkan Musim")
fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x=filtered_df['season'].map({1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}), 
            y=filtered_df['cnt'], estimator=sum, palette='coolwarm', ax=ax)
ax.set_xlabel("Musim")
ax.set_ylabel("Total Penyewaan")
st.pyplot(fig)

# Grafik Penyewaan Berdasarkan Hari
st.subheader("📅 Penyewaan Sepeda Berdasarkan Hari")
fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(x=filtered_df['weekday'].map({0: "Minggu", 1: "Senin", 2: "Selasa", 3: "Rabu", 
                                          4: "Kamis", 5: "Jumat", 6: "Sabtu"}), 
            y=filtered_df['cnt'], estimator=sum, palette='viridis', ax=ax)
ax.set_xlabel("Hari")
ax.set_ylabel("Total Penyewaan")
st.pyplot(fig)

# Grafik Penyewaan Sepeda per Jam
st.subheader("⏰ Penyewaan Sepeda per Jam")
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=filtered_df['hr'], y=filtered_df['cnt'], palette="coolwarm", ax=ax)
ax.set_xlabel("Jam")
ax.set_ylabel("Total Penyewaan")
st.pyplot(fig)

# Grafik Penyewaan Berdasarkan Bulan
st.subheader("📆 Penyewaan Berdasarkan Bulan")
monthly_avg = filtered_df.groupby("mnth")["cnt"].mean().reset_index()
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x="mnth", y="cnt", data=monthly_avg, ax=ax, palette="Set2")
ax.set_xlabel("Bulan")
ax.set_ylabel("Rata-rata Penyewaan")
st.pyplot(fig)

# Distribusi Casual vs Registered
st.subheader("👥 Distribusi Casual vs Registered Users")
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=filtered_df, x="mnth", y="casual", ax=ax, color='blue', label='Casual')
sns.boxplot(data=filtered_df, x="mnth", y="registered", ax=ax, color='orange', label='Registered')
plt.legend()
st.pyplot(fig)

# Grafik Penyewaan Hari Kerja vs Hari Libur
st.subheader("🏢 Penyewaan di Hari Kerja vs. Libur")
fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(x=['Hari Kerja', 'Hari Libur'], 
            y=[filtered_df['workingday'].sum(), filtered_df['holiday'].sum()], 
            palette=["#90CAF9", "#D3D3D3"], ax=ax)
ax.set_ylabel("Total Penyewaan")
st.pyplot(fig)

# Grafik Perbandingan Tren Penyewaan antara Tahun
st.subheader("📅 Perbandingan Tren Penyewaan antara Tahun")
fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(data=filtered_df, x="dteday", y="cnt", hue="yr", ax=ax)
plt.xticks(rotation=45)
st.pyplot(fig)

# Tampilkan Data
st.subheader("📜 Data Bike Sharing")
st.dataframe(filtered_df)
