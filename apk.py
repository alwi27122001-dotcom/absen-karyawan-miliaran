import streamlit as st
import pandas as pd
from datetime import datetime

# Setup tampilan layar HP
st.set_page_config(page_title="Absen & Pendapatan Harian", layout="wide")

st.title("💼 Sistem Absen Pulang & Input Pendapatan Harian")
st.write("Karyawan wajib mengisi nama dan total pendapatan harian sebelum pulang.")

# 1. Membuat Database Sementara di Memori Laptop
if "db_karyawan" not in st.session_state:
    st.session_state.db_karyawan = pd.DataFrame(columns=[
        "Waktu Lengkap", "Tahun", "Bulan", "Tanggal", "Nama Karyawan", "Pendapatan (Rupiah)"
    ])

# Ambil waktu, tahun, bulan, dan tanggal hari ini secara otomatis
waktu_skrg = datetime.now()
waktu_teks = waktu_skrg.strftime("%d-%m-%Y %H:%M:%S")
tanggal_hari_ini = waktu_skrg.strftime("%d-%m-%Y")
tahun_ini = waktu_skrg.strftime("%Y")

# Kamus nama bulan ke Bahasa Indonesia
bulan_indo_nama = {
    "January": "Januari", "February": "Februari", "March": "Maret",
    "April": "April", "May": "Mei", "June": "Juni",
    "July": "Juli", "August": "Agustus", "September": "September",
    "October": "Oktober", "November": "November", "December": "Desember"
}

# 2. Komponen Input Karyawan
st.subheader("📝 Form Absen Pulang")
col1, col2 = st.columns(2)

with col1:
    nama_karyawan = st.text_input("Nama Karyawan:", placeholder="Masukkan nama lengkap Anda")
    
with col2:
    st.text_input("Waktu Absen (Otomatis):", value=waktu_teks, disabled=True)

# Input pendapatan harian (kita pakai step 500 agar kelipatan Rp 500 perak)
pendapatan_hari_ini = st.number_input(
    "Pendapatan yang Dihasilkan Hari Ini (Rp):", 
    min_value=1000.0, 
    value=50000.0, 
    step=500.0,
    format="%.2f"
)

# --- PERBAIKAN TOTAL: FORMAT INDONESIA ASLI (TANPA BONUS NOL) ---
def format_rupiah(angka):
    # Mengubah float menjadi string dengan format ribuan internasional: 450500.00 -> 450,500
    # Kita buang desimal murni di belakang koma dengan int() jika tidak ada pecahan perak di bawah Rp 1
    teks_rupiah = f"{int(angka):,}"
    # Ganti koma menjadi titik untuk standar Indonesia: 450,500 -> 450.500
    return "Rp " + teks_rupiah.replace(",", ".")

# Menampilkan teks bantuan real-time tepat di bawah kotak input
st.caption(f"Format Terbaca: **{format_rupiah(pendapatan_hari_ini)}**")

# Tombol untuk Simpan Absen
if st.button("📥 Simpan Absen & Pendapatan", type="primary", use_container_width=True):
    if nama_karyawan.strip() == "":
        st.error("❌ Nama karyawan tidak boleh kosong!")
    else:
        bulan_inggris = waktu_skrg.strftime("%B")
        nama_bulan_indo = bulan_indo_nama.get(bulan_inggris, "Juni")
        
        data_baru = {
            "Waktu Lengkap": waktu_teks,
            "Tahun": tahun_ini,
            "Bulan": nama_bulan_indo,
            "Tanggal": tanggal_hari_ini,
            "Nama Karyawan": nama_karyawan,
            "Pendapatan (Rupiah)": float(pendapatan_hari_ini)
        }
        
        st.session_state.db_karyawan = pd.concat(
            [st.session_state.db_karyawan, pd.DataFrame([data_baru])], 
            ignore_index=True
        )
        st.success(f"✅ Data absen {nama_karyawan} berhasil dimasukkan!")
        st.rerun()

st.markdown("---")

# 3. Menampilkan Seluruh Data Master & Panel Hapus
st.subheader("📋 Seluruh Riwayat Absen & Pendapatan Master")

if not st.session_state.db_karyawan.empty:
    df_visual_master = st.session_state.db_karyawan.copy()
    df_visual_master["Pendapatan (Rupiah)"] = df_visual_master["Pendapatan (Rupiah)"].apply(format_rupiah)
    
    st.dataframe(df_visual_master, width="stretch")
    
    st.write("### 🗑️ Panel Hapus Absen")
    col_hapus1, col_hapus2 = st.columns()
    
    with col_hapus1:
        pilihan_hapus = st.selectbox(
            "Pilih data karyawan yang ingin dihapus:",
            options=st.session_state.db_karyawan.index,
            format_func=lambda x: f"Baris {x} - {st.session_state.db_karyawan.loc[x, 'Nama Karyawan']} ({st.session_state.db_karyawan.loc[x, 'Waktu Lengkap']})"
        )
        
    with col_hapus2:
        st.write("##") 
        if st.button("❌ Hapus Data", type="secondary", use_container_width=True):
            nama_terhapus = st.session_state.db_karyawan.loc[pilihan_hapus, "Nama Karyawan"]
            st.session_state.db_karyawan = st.session_state.db_karyawan.drop(pilihan_hapus).reset_index(drop=True)
            st.success(f"🗑️ Data absen atas nama {nama_terhapus} berhasil dihapus!")
            st.rerun()
else:
    st.info("Belum ada karyawan yang absen hari ini.")

st.markdown("---")

# 4. Filter Tingkat 1 & 2 (Tahun & Bulan)
st.subheader("📊 Filter Grafik & Analisis Data Berdasarkan Waktu")

list_tahun = ["2024", "2025", "2026", "2027", "2028"]
if tahun_ini not in list_tahun:
    list_tahun.append(tahun_ini)
    list_tahun = sorted(list(set(list_tahun)))

indeks_default_tahun = list_tahun.index(tahun_ini)

col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    tahun_terpilih = st.selectbox("📅 Pilih Tahun Analisis:", options=list_tahun, index=indeks_default_tahun)

df_filter_tahun = st.session_state.db_karyawan[st.session_state.db_karyawan['Tahun'] == tahun_terpilih]

with col_filter2:
    list_semua_bulan = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni", 
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    bulan_sekarang_teks = bulan_indo_nama.get(waktu_skrg.strftime("%B"), "Juni")
    indeks_default_bulan = list_semua_bulan.index(bulan_sekarang_teks)
    
    bulan_terpilih = st.selectbox("📅 Pilih Bulan Analisis:", options=list_semua_bulan, index=indeks_default_bulan)

df_bulan_terpilih = df_filter_tahun[df_filter_tahun['Bulan'] == bulan_terpilih]

st.write("### 📅 Pilih Tanggal Spesifik")
tanggal_input_kalender = st.date_input("Klik ikon kalender untuk memilih tanggal:", value=waktu_skrg)
tanggal_terpilih_teks = tanggal_input_kalender.strftime("%d-%m-%Y")

df_tanggal_aktif = df_bulan_terpilih[df_bulan_terpilih['Tanggal'] == tanggal_terpilih_teks]

st.markdown("---")
st.write(f"#### 📊 Hasil Analisis Data untuk Tanggal: **{tanggal_terpilih_teks}**")

if not df_tanggal_aktif.empty:
    total_hari = df_tanggal_aktif["Pendapatan (Rupiah)"].sum()
    rata_hari = df_tanggal_aktif["Pendapatan (Rupiah)"].mean()
    
    col_box1, col_box2 = st.columns(2)
    with col_box1:
        st.metric(label=f"Total Pendapatan (Tanggal {tanggal_terpilih_teks})", value=format_rupiah(total_hari))
    with col_box2:
        st.metric(label=f"Rata-rata Pendapatan (Tanggal {tanggal_terpilih_teks})", value=format_rupiah(rata_hari))
    
    # Grafik Garis Naik Turun khusus tanggal terpilih
    st.write(f"### 📈 Grafik Tren Pendapatan Tanggal {tanggal_terpilih_teks}")
    df_grafik_garis = df_tanggal_aktif[['Nama Karyawan', 'Pendapatan (Rupiah)']].set_index('Nama Karyawan')
    st.line_chart(df_grafik_garis)
    
    # Tabel Riwayat Tanggal diletakkan paling bawah
    st.write(f"### 📅 Riwayat Data Absen Tanggal {tanggal_terpilih_teks}")
    df_visual_tanggal = df_tanggal_aktif[['Waktu Lengkap', 'Nama Karyawan', 'Pendapatan (Rupiah)']].copy()
    df_visual_tanggal["Pendapatan (Rupiah)"] = df_visual_tanggal["Pendapatan (Rupiah)"].apply(format_rupiah)
    
    st.dataframe(df_visual_tanggal, width="stretch")
else:
    st.warning(f"Belum ada data karyawan yang menginput absen pada tanggal **{tanggal_terpilih_teks}** di bulan **{bulan_terpilih} {tahun_terpilih}**.")
