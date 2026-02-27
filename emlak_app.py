import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from fpdf import FPDF

# Sayfa Ayarları
st.set_page_config(page_title="Emlak Pro Asistan", page_icon="🏢", layout="wide")

DB_FILE = "emlak_veritabani.json"

def verileri_yukle():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def verileri_kaydet(veriler):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(veriler, f, ensure_ascii=False, indent=4)

if 'kayitlar' not in st.session_state:
    st.session_state.kayitlar = verileri_yukle()

st.title("🏢 Emlak Yönetim ve Sözleşme Paneli")

# Sol Menü
with st.sidebar:
    st.header("📋 İşlem Formu")
    isim = st.text_input("Müşteri Ad Soyad:")
    islem_tipi = st.selectbox("İşlem Türü:", ["Konut Satışı", "Ticari Satış", "Kiralama"])
    tutar = st.number_input("İşlem Bedeli (TL):", min_value=0, value=2000000)
    st.divider()
    hesapla_ve_ekle = st.button("Sisteme Kaydet ve Hesapla")
    
    if st.button("🔴 Tüm Listeyi Sıfırla"):
        st.session_state.kayitlar = []
        verileri_kaydet([])
        st.rerun()

# Kayıt Mantığı
if hesapla_ve_ekle and isim:
    hizmet_bedeli = tutar * 0.02
    kdv = hizmet_bedeli * 0.20
    toplam = hizmet_bedeli + kdv
    tarih = datetime.now().strftime("%d-%m-%Y %H:%M")

    yeni_kayit = {
        "Tarih": tarih, "Müşteri": isim, "İşlem": islem_tipi,
        "Tutar": f"{tutar:,.2f} TL", "Hizmet Bedeli": f"{hizmet_bedeli:,.2f} TL", "KDV Dahil": f"{toplam:,.2f} TL"
    }
    st.session_state.kayitlar.append(yeni_kayit)
    verileri_kaydet(st.session_state.kayitlar)
    st.success(f"✅ {isim} kaydedildi.")

tab1, tab2 = st.tabs(["📊 İşlem Takibi", "📜 Sözleşme Hazırlama"])

with tab1:
    if st.session_state.kayitlar:
        df = pd.DataFrame(st.session_state.kayitlar)
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False, sep=';').encode('utf-8-sig')
        st.download_button("Excel Listesini İndir", data=csv, file_name='emlak_kayitlari.csv')

with tab2:
    if isim:
        tarih_str = datetime.now().strftime("%d/%m/%Y")
        
        def pdf_olustur():
            # fpdf2 kullanımı (Karakter sorunu için en güvenli yol)
            pdf = FPDF()
            pdf.add_page()
            
            # Yerleşik fontu UTF-8 modunda başlat
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, "TAŞINMAZ GÖSTERME VE YETKİ BELGESİ", align='C', new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)
            
            pdf.set_font("helvetica", "", 12)
            pdf.cell(0, 10, f"TARİH: {tarih_str}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"MÜŞTERİ: {isim.upper()}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"İŞLEM TÜRÜ: {islem_tipi}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"TAŞINMAZ BEDELİ: {tutar:,.2f} TL", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)
            
            sozlesme_metni = (
                "Yukarıda bilgileri yer alan taşınmazın gösterilmesi ve aracılık hizmetleri karşılığında, "
                "Taşınmaz Ticareti Hakkında Yönetmelik gereğince; %2 + KDV oranında hizmet bedeli "
                "ödenmesini taraflar kabul ve taahhüt eder."
            )
            pdf.multi_cell(0, 10, sozlesme_metni)
            pdf.ln(20)
            pdf.cell(90, 10, "MÜŞTERİ İMZA", align='L')
            pdf.cell(0, 10, "EMLAK DANIŞMANI İMZA", align='R')
            
            # fpdf2'de çıktı alma yöntemi
            return pdf.output()

        try:
            pdf_data = pdf_olustur()
            st.download_button(
                label="📄 Profesyonel Türkçe PDF İndir",
                data=pdf_data, # bytes() sarmalına gerek olmayabilir, fpdf2 bunu halleder
                file_name=f"sozlesme_{isim}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Hata detayı: {e}") # Buradaki hata mesajını görmek işimizi kolaylaştırır