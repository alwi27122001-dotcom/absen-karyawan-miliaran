import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import json

# Setup tampilan layar HP
st.set_page_config(page_title="Absen & Pendapatan Harian", layout="wide")
st.title("💼 Sistem Absen Pulang & Input Pendapatan Harian")
st.write("Karyawan wajib mengisi nama dan total pendapatan harian sebelum pulang.")

# =========================================================================
# ⚠️ URL UTAMA DATABASE APPS SCRIPT (ID PENERAPAN ANDA)
# =========================================================================
URL_API = "https://google.com"
# =========================================================================

# Ambil data secara real-time dari Google Sheets via API Apps Script
db_karyawan = pd.DataFrame(columns=["Waktu Lengkap", "Tahun", "Bulan", "Tanggal", "Nama Karyawan", "Pendapatan (Rupiah)"])

try:
    response = requests.get(URL_API, timeout=10)
    if response.status_code == 200:
        raw_data = response.json()
        
        # Saring jika sheet baru berisi judul kolom saja (panjang baris <= 1)
        if isinstance(raw_data, list) and len(raw_data) > 1:
            headers = raw_data[0]
            records = raw_data[1:]
            
            # Jika Google Apps Script mengembalikan baris kosong atau timestamp
            db_karyawan = pd.DataFrame(records, columns=headers)
            
            # Bersihkan kolom hantu atau nama kolom berhuruf kecil bawaan sistem
            db_karyawan = db_karyawan.loc[:, ~db_karyawan.columns.str.contains('^Unnamed|^Timestamp')]
            db_karyawan = db_karyawan.rename(columns={
                "waktu lengkap": "Waktu Lengkap", "tahun": "Tahun", "bulan": "Bulan", 
                "tanggal": "Tanggal", "nama karyawan": "Nama Karyawan", "pendapatan (rupiah)": "Pendapatan (Rupiah)"
            })
except Exception as e:
    # Bypass silent jika database pusat masih kosong, agar tombol input tidak terkunci
    pass

# Ambil waktu otomatis hari ini
waktu_skrg = datetime.now()
waktu_teks = waktu_skrg.strftime("%d-%m-%Y %H:%M:%S")
tanggal_hari_ini = waktu_skrg.strftime("%d-%m-%Y")
tahun_ini = waktu_skrg.strftime("%Y")

bulan_indo_nama = {
    "January": "Januari", "February": "Februari", "March": "Maret", "April": "April",
    "May": "Mei", "June": "Juni", "July": "Juli", "August": "Agustus",
    "September": "September", "October": "Oktober", "November": "November", "December": "Desember"
}

# Form Input Karyawan
st.subheader("📝 Form Absen Pulang")
col1, col2 = st.columns(2)
with col1:
    nama_karyawan = st.text_input("Nama Karyawan:", placeholder="Masukkan nama lengkap Anda")
with col2:
    st.text_input("Waktu Absen (Otomatis):", value=waktu_teks, disabled=True)

pendapatan_hari_ini = st.number_input(
    "Pendapatan yang Dihasilkan Hari Ini (Rp):", 
    min_value=1000.0, value=50000.0, step=500.0, format="%.2f"
)

def format_rupiah(angka):
    try:
        if pd.isna(angka) or angka == "" or angka == "None": return "Rp 0"
        teks_rupiah = f"{int(float(angka)):,}"
        return "Rp " + teks_rupiah.replace(",", ".")
    except:
        return "Rp " + str(angka)

st.caption(f"Format Terbaca: **{format_rupiah(pendapatan_hari_ini)}**")

# Tombol Simpan
if st.button("📥 Simpan Absen & Pendapatan", type="primary", use_container_width=True):
    if nama_karyawan.strip() == "":
        st.error("❌ Nama karyawan tidak boleh kosong!")
    else:
        bulan_inggris = waktu_skrg.strftime("%B")
        nama_bulan_indo = bulan_indo_nama.get(bulan_inggris, "Juni")
        
        # Payload data rapi dikirim sebagai string JSON terarah
        payload = {
            "waktu": waktu_teks,
            "tahun": tahun_ini,
            "bulan": nama_bulan_indo,
            "tanggal": tanggal_hari_ini,
            "nama": nama_karyawan,
            "pendapatan": float(pendapatan_hari_ini)
        }
        
        try:
            # Mengirim data langsung ke database pusat via API POST
            res = requests.post(URL_API, data=json.dumps(payload), headers={"Content-Type": "application/json"})
            st.success(f"✅ Data absen {nama_karyawan} berhasil masuk ke Google Sheets pusat!")
            st.balloons()
            st.rerun()
        except Exception as err:
            st.error(f"Gagal mengirim data ke server. Error: {str(err)}")

st.markdown("---")

# Menampilkan Tabel Riwayat Master (TETAP ADA & BERSIH TOTAL)
st.subheader("📋 Seluruh Riwayat Absen & Pendapatan Master")
if not db_karyawan.empty and len(db_karyawan) > 0:
    df_visual_master = db_karyawan.copy()
    if "Pendapatan (Rupiah)" in df_visual_master.columns:
        df_visual_master["Pendapatan (Rupiah)"] = df_visual_master["Pendapatan (Rupiah)"].apply(format_rupiah)
    st.dataframe(df_visual_master, use_container_width=True)
    
    st.write("### 🔒 Panel Hapus Absen (Khusus Editor)")
    pin_input = st.text_input("Masukkan PIN Editor untuk Menghapus Data:", type="password", placeholder="Masukkan 4 digit PIN")
    
    if pin_input == "1234":
        st.success("🔓 PIN Benar. Akses terbuka.")
        st.info("💡 **Petunjuk Editor:** Silakan buka file Google Sheets Anda untuk mengedit atau menghapus baris data. Aplikasi web/HP otomatis sinkron mendeteksi perubahan tersebut secara instan!")
    elif pin_input != "":
        st.error("❌ PIN Salah!")
else:
    st.info("Belum ada data karyawan yang tersimpan di dalam database pusat.")

st.markdown("---")

# Filter Grafik & Analisis Data Berdasarkan Waktu
st.subheader("📊 Filter Grafik & Analisis Data Berdasarkan Waktu")
list_tahun = ["2024", "2025", "2026", "2027", "2028"]
if tahun_ini not in list_tahun: list_tahun.append(tahun_ini)
list_tahun = sorted(list(set(list_tahun)))

if not db_karyawan.empty and 'Tahun' in db_karyawan.columns:
    db_karyawan['Tahun'] = db_karyawan['Tahun'].astype(str)

indeks_default_tahun = list_tahun.index(tahun_ini)

col_filter1, col_filter2 = st.columns(2)
with col_filter1:
    tahun_terpilih = st.selectbox("📅 Pilih Tahun Analisis:", options=list_tahun, index=indeks_default_tahun)
    df_filter_tahun = db_karyawan[db_karyawan['Tahun'] == tahun_terpilih] if not db_karyawan.empty and 'Tahun' in db_karyawan.columns else db_karyawan

with col_filter2:
    list_semua_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    bulan_sekarang_teks = bulan_indo_nama.get(waktu_skrg.strftime("%B"), "Juni")
    indeks_default_bulan = list_semua_bulan.index(bulan_sekarang_teks)
    bulan_terpilih = st.selectbox("📅 Pilih Bulan Analisis:", options=list_semua_bulan, index=indeks_default_bulan)
    df_bulan_terpilih = df_filter_tahun[df_filter_tahun['Bulan'] == bulan_terpilih] if not df_filter_tahun.empty and 'Bulan' in df_filter_tahun.columns else df_filter_tahun

st.write("### 📅 Pilih Tanggal Spesifik")
tanggal_input_kalender = st.date_input("Klik ikon kalender untuk memilih tanggal:", value=waktu_skrg)
tanggal_terpilih_teks = tanggal_input_kalender.strftime("%d-%m-%Y")
df_tanggal_aktif = df_bulan_terpilih[df_bulan_terpilih['Tanggal'] == tanggal_terpilih_teks] if not df_bulan_terpilih.empty and 'Tanggal' in df_bulan_terpilih.columns else df_bulan_terpilih

st.markdown("---")
st.write(f"#### 📊 Hasil Analisis Data untuk Tanggal: **{tanggal_terpilih_teks}**")

if not df_tanggal_aktif.empty and 'Pendapatan (Rupiah)' in df_tanggal_aktif.columns and len(df_tanggal_aktif) > 0:
    total_hari = pd.to_numeric(df_tanggal_aktif["Pendapatan (Rupiah)"], errors='coerce').sum()
    rata_hari = pd.to_numeric(df_tanggal_aktif["Pendapatan (Rupiah)"], errors='coerce').mean()
    
    col_box1, col_box2 = st.columns(2)
    with col_box1: st.metric(label=f"Total Pendapatan", value=format_rupiah(total_hari))
    with col_box2: st.metric(label=f"Rata-rata Pendapatan", value=format_rupiah(rata_hari))
        
    st.write(f"### 📈 Grafik Tren Pendapatan Tanggal {tanggal_terpilih_teks}")
    df_grafik_garis = df_tanggal_aktif[['Nama Karyawan', 'Pendapatan (Rupiah)']].copy()
    df_grafik_garis['Pendapatan (Rupiah)'] = pd.to_numeric(df_grafik_garis['Pendapatan (Rupiah)'], errors='coerce')
    df_grafik_garis = df_grafik_garis.set_index('Nama Karyawan')
    st.line_chart(df_grafik_garis)
else:
    st.warning(f"Belum ada data karyawan pada tanggal **{tanggal_terpilih_teks}**.")
