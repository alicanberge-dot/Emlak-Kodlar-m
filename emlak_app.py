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

# TÜRKÇE KARAKTER TEMİZLEME FONKSİYONU (HATA ÖNLEYİCİ)
def tr_to_en(text):
    search = "çğışüöÇĞİŞÜÖ"
    replace = "cgisuocGISUO"
    for s, r in zip(search, replace):
        text = text.replace(s, r)
    return text

st.title("🏢 Emlak Yönetim ve Sözleşme Paneli")

# Sol Menü
with st.sidebar:
    st.header("📋 İşlem Formu")
    isim = st.text_input("Müşteri Ad Soyad:")
    islem_tipi = st.selectbox("İşlem Türü:", ["Konut Satis", "Ticari Satis", "Kiralama"])
    tutar = st.number_input("İşlem Bedeli (TL):", min_value=0, value=2000000)
    st.divider()
    hesapla_ve_ekle = st.button("Sisteme Kaydet ve Hesapla")
    
    if st.button("🔴 Tüm Listeyi Sıfırla"):
        st.session_state.kayitlar = []
        verileri_kaydet([])
        st.rerun()

# Hesaplama ve Kayıt
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
    st.subheader("Günlük İşlem Listesi")
    if st.session_state.kayitlar:
        df = pd.DataFrame(st.session_state.kayitlar)
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False, sep=';').encode('utf-8-sig')
        st.download_button("Excel Listesini İndir", data=csv, file_name='emlak_kayitlari.csv')

with tab2:
    st.subheader("Otomatik Yetki Belgesi")
    if isim:
        tarih_str = datetime.now().strftime("%d/%m/%Y")
        
        def pdf_olustur():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "TASINMAZ GOSTERME VE YETKI BELGESI", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", "", 12)
            # Metinleri Türkçe karakterlerden arındırıyoruz
            pdf.cell(200, 10, tr_to_en(f"TARIH: {tarih_str}"), ln=True)
            pdf.cell(200, 10, tr_to_en(f"MUSTERI: {isim.upper()}"), ln=True)
            pdf.cell(200, 10, tr_to_en(f"ISLEM TURU: {islem_tipi}"), ln=True)
            pdf.cell(200, 10, f"TASINMAZ BEDELI: {tutar:,.2f} TL", ln=True)
            pdf.ln(10)
            mesaj = "Yukarida bilgileri yer alan tasinmazin gosterilmesi ve aracilik hizmetleri karsiliginda, Tasinmaz Ticareti Hakkinda Yonetmelik geregince; %2 + KDV oraninda hizmet bedeli odenmesini taraflar kabul ve taahhut eder."
            pdf.multi_cell(0, 10, tr_to_en(mesaj))
            pdf.ln(20)
            pdf.cell(100, 10, "MUSTERI IMZA", align='L')
            pdf.cell(0, 10, "EMLAK DANISMANI IMZA", align='R')
            return pdf.output(dest='S').encode('latin-1')

        try:
            pdf_data = pdf_olustur()
            st.download_button(
                label="📄 Sözleşmeyi PDF Olarak İndir",
                data=pdf_data,
                file_name=f"sozlesme_{tr_to_en(isim)}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"PDF oluşturulurken bir hata oluştu. Lütfen müşteri isminde özel karakter kullanmadığınızdan emin olun.")
    else:
        st.warning("⚠️ Sözleşme için isim girin.")