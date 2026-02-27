import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from fpdf import FPDF

# Sayfa Ayarları
st.set_page_config(page_title="Emlak Pro Asistan", page_icon="🏢", layout="wide")

# --- KULLANICI GİRİŞ SİSTEMİ ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🔐 Emlak Paneli Girişi")
    user_input = st.text_input("Kullanıcı Adınızı Giriniz (Örn: adiniz_soyadiniz):").lower().strip()
    if st.button("Sisteme Gir"):
        if user_input:
            st.session_state.user = user_input
            st.rerun()
        else:
            st.warning("Lütfen bir kullanıcı adı belirleyin.")
    st.stop() # Giriş yapılana kadar alt tarafı çalıştırma

# Her kullanıcıya özel dosya ismi
DB_FILE = f"db_{st.session_state.user}.json"

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

# --- ANA PANEL ---
st.title(f"🏢 Emlak Yönetim Paneli - Hoş geldin, {st.session_state.user.capitalize()}")

with st.sidebar:
    st.header("📋 İşlem Formu")
    isim = st.text_input("Müşteri Ad Soyad:")
    islem_tipi = st.selectbox("İşlem Türü:", ["Konut Satışı", "Ticari Satış", "Kiralama"])
    tutar = st.number_input("İşlem Bedeli (TL):", min_value=0, value=2000000)
    st.divider()
    hesapla_ve_ekle = st.button("Sisteme Kaydet ve Hesapla")
    
    if st.button("🚪 Çıkış Yap"):
        st.session_state.user = None
        st.session_state.kayitlar = []
        st.rerun()

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
    else:
        st.info("Henüz bir kaydınız bulunmuyor.")

with tab2:
    if isim:
        tarih_str = datetime.now().strftime("%d/%m/%Y")
        
        def pdf_olustur():
            pdf = FPDF()
            # Senin sistemindeki font isimleriyle eşleştirdik:
            pdf.add_font("Roboto", style="", fname="Roboto_Condensed-Light.ttf")
            pdf.add_font("Roboto", style="B", fname="Roboto_Condensed-Bold.ttf")
            pdf.add_page()
            
            pdf.set_font("Roboto", "B", 16)
            pdf.cell(0, 10, "TAŞINMAZ GÖSTERME VE YETKİ BELGESİ", align='C', new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)
            
            pdf.set_font("Roboto", "", 12)
            pdf.cell(0, 10, f"TARİH: {tarih_str}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"MÜŞTERİ: {isim.upper()}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"DANIŞMAN: {st.session_state.user.upper()}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)
            
            metin = "Bu belge taşınmaz ticareti yönetmeliği uyarınca düzenlenmiştir..."
            pdf.multi_cell(0, 10, metin)
            return pdf.output()

        try:
            pdf_out = pdf_olustur()
            st.download_button("📄 PDF İndir", data=bytes(pdf_out), file_name=f"sozlesme_{isim}.pdf")
        except Exception as e:
            st.error(f"Hata: {e}")