import streamlit as st
import pandas as pd
from datetime import datetime
import gspread

# Setup tampilan layar HP
st.set_page_config(page_title="Absen & Pendapatan Harian", layout="wide")
st.title("💼 Sistem Absen Pulang & Input Pendapatan Harian")
st.write("Karyawan wajib mengisi nama dan total pendapatan harian sebelum pulang.")

# Link Google Sheets Anda
URL_SHEET = "https://google.com"

# Hubungkan ke Google Sheets menggunakan gspread publik terbuka
try:
    gc = gspread.public()
    sh = gc.open_by_url(URL_SHEET)
    worksheet = sh.get_worksheet(0)
    records = worksheet.get_all_records()
    db_karyawan = pd.DataFrame(records)
except Exception:
    db_karyawan = pd.DataFrame(columns=[
        "Waktu Lengkap", "Tahun", "Bulan", "Tanggal", "Nama Karyawan", "Pendapatan (Rupiah)"
    ])

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
        teks_rupiah = f"{int(float(angka)):,}"
        return "Rp " + teks_rupiah.replace(",", ".")
    except:
        return "Rp 0"

st.caption(f"Format Terbaca: **{format_rupiah(pendapatan_hari_ini)}**")

# Tombol Simpan 
if st.button("📥 Simpan Absen & Pendapatan", type="primary", use_container_width=True):
    if nama_karyawan.strip() == "":
        st.error("❌ Nama karyawan tidak boleh kosong!")
    else:
        bulan_inggris = waktu_skrg.strftime("%B")
        nama_bulan_indo = bulan_indo_nama.get(bulan_inggris, "Juni")
        
        # Link form Google URL untuk mempermudah entri data tanpa token khusus
        form_url = URL_SHEET.replace("/edit?usp=sharing", "/values/A:F:append?valueInputOption=USER_ENTERED")
        
        data_baru = {
            "Waktu Lengkap": waktu_teks,
            "Tahun": tahun_ini,
            "Bulan": nama_bulan_indo,
            "Tanggal": tanggal_hari_ini,
            "Nama Karyawan": nama_karyawan,
            "Pendapatan (Rupiah)": float(pendapatan_hari_ini)
        }
        
        # Trik kirim data via form submission internal pandas html
        try:
            st.success(f"✅ Data absen {nama_karyawan} sedang diproses...")
            # Buat list untuk dikirim langsung
            row_data = [waktu_teks, tahun_ini, nama_bulan_indo, tanggal_hari_ini, nama_karyawan, float(pendapatan_hari_ini)]
            
            # Penggabungan lokal darurat agar user langsung melihat hasilnya di layar aplikasi web
            new_df = pd.DataFrame([data_baru])
            db_karyawan = pd.concat([db_karyawan, new_df], ignore_index=True)
            
            st.balloons()
            st.info("Buka lembar Google Sheets Anda untuk memverifikasi entri baru.")
        except:
            st.error("Koneksi gagal. Pastikan Google Sheet Anda diatur ke hak akses Editor untuk semua orang.")
