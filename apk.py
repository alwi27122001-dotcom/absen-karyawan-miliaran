import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Setup tampilan layar HP
st.set_page_config(page_title="Absen & Pendapatan Harian", layout="wide")
st.title("💼 Sistem Absen Pulang & Input Pendapatan Harian")
st.write("Karyawan wajib mengisi nama dan total pendapatan harian sebelum pulang.")

# Masukkan LINK GOOGLE SHEETS ANDA di bawah ini!
URL_SHEET = "PASTE_LINK_GOOGLE_SHEETS_ANDA_DI_SINI"

# Hubungkan ke Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    db_karyawan = conn.read(spreadsheet=URL_SHEET, ttl="0")
except Exception:
    db_karyawan = pd.DataFrame(columns=[
        "Waktu Lengkap", "Tahun", "Bulan", "Tanggal", "Nama Karyawan", "Pendapatan (Rupiah)"
    ])

# Ambil waktu otomatis
waktu_skrg = datetime.now()
waktu_teks = waktu_skrg.strftime("%d-%m-%Y %H:%M:%S")
tanggal_hari_ini = waktu_skrg.strftime("%d-%m-%Y")
tahun_ini = waktu_skrg.strftime("%Y")

bulan_indo_nama = {
    "January": "Januari", "February": "Februari", "March": "Maret", "April": "April",
    "May": "Mei", "June": "Juni", "July": "Juli", "August": "Agustus",
    "September": "September", "October": "Oktober", "November": "November", "December": "Desember"
}

# Form Input
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

# Tombol Simpan (Langsung Push ke Google Sheets)
if st.button("📥 Simpan Absen & Pendapatan", type="primary", use_container_width=True):
    if nama_karyawan.strip() == "":
        st.error("❌ Nama karyawan tidak boleh kosong!")
    elif URL_SHEET == "PASTE_LINK_GOOGLE_SHEETS_ANDA_DI_SINI":
        st.error("❌ Anda belum memasukkan link Google Sheets di baris kode nomor 12!")
    else:
        bulan_inggris = waktu_skrg.strftime("%B")
        nama_bulan_indo = bulan_indo_nama.get(bulan_inggris, "Juni")
        
        data_baru = pd.DataFrame([{
            "Waktu Lengkap": waktu_teks,
            "Tahun": tahun_ini,
            "Bulan": nama_bulan_indo,
            "Tanggal": tanggal_hari_ini,
            "Nama Karyawan": nama_karyawan,
            "Pendapatan (Rupiah)": float(pendapatan_hari_ini)
        }])
        
        # Gabungkan data lama dan baru, lalu update spreadsheet
        df_update = pd.concat([db_karyawan, data_baru], ignore_index=True)
        conn.update(spreadsheet=URL_SHEET, data=df_update)
        st.success(f"✅ Data absen {nama_karyawan} berhasil tersimpan secara permanen!")
        st.rerun()

st.markdown("---")

# Tampilkan Riwayat Master
st.subheader("📋 Seluruh Riwayat Absen & Pendapatan Master")
if not db_karyawan.empty and db_karyawan.dropna(how='all').shape[0] > 0:
    df_visual_master = db_karyawan.copy()
    df_visual_master["Pendapatan (Rupiah)"] = df_visual_master["Pendapatan (Rupiah)"].apply(format_rupiah)
    st.dataframe(df_visual_master, use_container_width=True)
    
    st.write("### 🗑️ Panel Hapus Absen")
    col_hapus1, col_hapus2 = st.columns(2)
    with col_hapus1:
        pilihan_hapus = st.selectbox(
            "Pilih data karyawan yang ingin dihapus:",
            options=db_karyawan.index,
            format_func=lambda x: f"Baris {x} - {db_karyawan.loc[x, 'Nama Karyawan']} ({db_karyawan.loc[x, 'Waktu Lengkap']})"
        )
    with col_hapus2:
        st.write("##")
        if st.button("❌ Hapus Data", type="secondary", use_container_width=True):
            df_update = db_karyawan.drop(pilihan_hapus).reset_index(drop=True)
            conn.update(spreadsheet=URL_SHEET, data=df_update)
            st.success("🗑️ Data absen berhasil dihapus dari pusat data!")
            st.rerun()
else:
    st.info("Belum ada karyawan yang absen hari ini.")

st.markdown("---")

# Analisis Waktu
st.subheader("📊 Filter Grafik & Analisis Data Berdasarkan Waktu")
list_tahun = ["2024", "2025", "2026", "2027", "2028"]
if tahun_ini not in list_tahun: list_tahun.append(tahun_ini)
list_tahun = sorted(list(set(list_tahun)))
indeks_default_tahun = list_tahun.index(tahun_ini)

col_filter1, col_filter2 = st.columns(2)
with col_filter1:
    tahun_terpilih = st.selectbox("📅 Pilih Tahun Analisis:", options=list_tahun, index=indeks_default_tahun)
    df_filter_tahun = db_karyawan[db_karyawan['Tahun'] == tahun_terpilih] if not db_karyawan.empty else db_karyawan

with col_filter2:
    list_semua_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    bulan_sekarang_teks = bulan_indo_nama.get(waktu_skrg.strftime("%B"), "Juni")
    indeks_default_bulan = list_semua_bulan.index(bulan_sekarang_teks)
    bulan_terpilih = st.selectbox("📅 Pilih Bulan Analisis:", options=list_semua_bulan, index=indeks_default_bulan)
    df_bulan_terpilih = df_filter_tahun[df_filter_tahun['Bulan'] == bulan_terpilih] if not df_filter_tahun.empty else df_filter_tahun

st.write("### 📅 Pilih Tanggal Spesifik")
tanggal_input_kalender = st.date_input("Klik ikon kalender untuk memilih tanggal:", value=waktu_skrg)
tanggal_terpilih_teks = tanggal_input_kalender.strftime("%d-%m-%Y")
df_tanggal_aktif = df_bulan_terpilih[df_bulan_terpilih['Tanggal'] == tanggal_terpilih_teks] if not df_bulan_terpilih.empty else df_bulan_terpilih

st.markdown("---")
st.write(f"#### 📊 Hasil Analisis Data untuk Tanggal: **{tanggal_terpilih_teks}**")

if not df_tanggal_aktif.empty and df_tanggal_aktif.dropna(how='all').shape[0] > 0:
    total_hari = pd.to_numeric(df_tanggal_aktif["Pendapatan (Rupiah)"]).sum()
    rata_hari = pd.to_numeric(df_tanggal_aktif["Pendapatan (Rupiah)"]).mean()
    
    col_box1, col_box2 = st.columns(2)
    with col_box1: st.metric(label=f"Total Pendapatan", value=format_rupiah(total_hari))
    with col_box2: st.metric(label=f"Rata-rata Pendapatan", value=format_rupiah(rata_hari))
        
    st.write(f"### 📈 Grafik Tren Pendapatan Tanggal {tanggal_terpilih_teks}")
    df_grafik_garis = df_tanggal_aktif[['Nama Karyawan', 'Pendapatan (Rupiah)']].copy()
    df_grafik_garis['Pendapatan (Rupiah)'] = pd.to_numeric(df_grafik_garis['Pendapatan (Rupiah)'])
    df_grafik_garis = df_grafik_garis.set_index('Nama Karyawan')
    st.line_chart(df_grafik_garis)
else:
    st.warning(f"Belum ada data karyawan pada tanggal **{tanggal_terpilih_teks}**.")
