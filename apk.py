import streamlit as st
import pandas as pd
from datetime import datetime

# Setup tampilan layar HP
st.set_page_config(page_title="Absen & Pendapatan Harian", layout="wide")
st.title("💼 Sistem Absen Pulang & Input Pendapatan Harian")
st.write("Karyawan wajib mengisi nama dan total pendapatan harian sebelum pulang.")

# =========================================================================
# ⚠️ LINK PUSAT DATABASE FORM RESPONSES 1
# =========================================================================
# Kita tambahkan parameter gid=0 untuk memastikan Python membaca tab Form Responses 1 dengan tepat
URL_SHEET_CSV = "https://google.com"
# =========================================================================

# Baca data dari Google Sheets secara real-time untuk Grafik & Tabel
try:
    st.cache_data.clear()
    db_karyawan = pd.read_csv(URL_SHEET_CSV)
    
    # Bersihkan kolom hantu Unnamed dan baris kosong
    db_karyawan = db_karyawan.loc[:, ~db_karyawan.columns.str.contains('^Unnamed')]
    db_karyawan = db_karyawan.dropna(how='all')
    
    # Jika Google menyisipkan kolom Timestamp bawaan, sesuaikan pemetaan nama kolom
    if "waktu lengkap" in db_karyawan.columns:
        db_karyawan = db_karyawan.rename(columns={"waktu lengkap": "Waktu Lengkap"})
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
        if pd.isna(angka): return "Rp 0"
        teks_rupiah = f"{int(float(angka)):,}"
        return "Rp " + teks_rupiah.replace(",", ".")
    except:
        return "Rp 0"

st.caption(f"Format Terbaca: **{format_rupiah(pendapatan_hari_ini)}**")

# Tombol Simpan (Kirim Terarah Menggunakan Sistem Form)
if st.button("📥 Simpan Absen & Pendapatan", type="primary", use_container_width=True):
    if nama_karyawan.strip() == "":
        st.error("❌ Nama karyawan tidak boleh kosong!")
    else:
        bulan_inggris = waktu_skrg.strftime("%B")
        nama_bulan_indo = bulan_indo_nama.get(bulan_inggris, "Juni")
        
        # Menggunakan format submit mandiri terarah langsung ke formulir publik
        FORM_LINK_SEND = (
            f"https://google.com?"
            f"entry.1000001={waktu_teks}&"
            f"entry.1000002={tahun_ini}&"
            f"entry.1000003={nama_bulan_indo}&"
            f"entry.1000004={tanggal_hari_ini}&"
            f"entry.1000005={nama_karyawan}&"
            f"entry.1000006={float(pendapatan_hari_ini)}"
        )
        
        # Append data lokal agar grafik di HP karyawan langsung ter-update seketika
        data_baru = pd.DataFrame([{
            "Waktu Lengkap": waktu_teks, "Tahun": tahun_ini, "Bulan": nama_bulan_indo,
            "Tanggal": tanggal_hari_ini, "Nama Karyawan": nama_karyawan, "Pendapatan (Rupiah)": float(pendapatan_hari_ini)
        }])
        db_karyawan = pd.concat([db_karyawan, data_baru], ignore_index=True)
        
        # Tembak form via iframe HTML background
        st.markdown(f'<iframe src="{FORM_LINK_SEND}" style="display:none;"></iframe>', unsafe_allow_html=True)
        
        st.success(f"✅ Data absen {nama_karyawan} berhasil dimasukkan ke dalam sistem!")
        st.balloons()
        st.rerun()

st.markdown("---")

# Menampilkan Tabel Riwayat Master (SUDAH DISINKRONKAN DENGAN TIMESTAMP FORM)
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
        st.info("💡 **Petunjuk Editor:** Silakan buka file Google Sheets Anda pada tab 'Form Responses 1' untuk menghapus data. Grafik otomatis ter-update seketika!")
    elif pin_input != "":
        st.error("❌ PIN Salah!")
else:
    st.info("Belum ada data karyawan yang tersimpan di dalam database.")

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
