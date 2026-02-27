import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from fpdf import FPDF

# Sayfa Ayarları
st.set_page_config(page_title="Emlak CRM Pro", page_icon="🏛️", layout="wide")

# --- DOSYA YÖNETİMİ ---
USERS_FILE = "kullanicilar.json"

def kullanicilari_yukle():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def kullanici_kaydet(username, password):
    kullanicilar = kullanicilari_yukle()
    kullanicilar[username] = password
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(kullanicilar, f, ensure_ascii=False, indent=4)

# --- GİRİŞ SİSTEMİ ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🔐 Emlak CRM Pro Girişi")
    t1, t2 = st.tabs(["Giriş Yap", "Hesap Oluştur"])
    with t1:
        u = st.text_input("Kullanıcı Adı:", key="l_u").lower().strip()
        p = st.text_input("Şifre:", type="password", key="l_p")
        if st.button("Giriş"):
            m = kullanicilari_yukle()
            if u in m and m[u] == p:
                st.session_state.user = u
                st.rerun()
            else: st.error("Hatalı bilgiler!")
    with t2:
        nu = st.text_input("Yeni K. Adı:", key="r_u").lower().strip()
        np = st.text_input("Yeni Şifre:", type="password", key="r_p")
        if st.button("Kayıt Ol"):
            if nu and np:
                kullanici_kaydet(nu, np)
                st.success("Kayıt başarılı, giriş yapabilirsiniz.")
    st.stop()

# --- VERİ YÜKLEME ---
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

# --- PROFESYONEL DASHBOARD (İSTATİSTİK) ---
st.title(f"🏛️ Emlak Yönetim Paneli - {st.session_state.user.upper()}")

# İstatistikler
if st.session_state.kayitlar:
    df_stat = pd.DataFrame(st.session_state.kayitlar)
    df_stat['Sayısal Tutar'] = df_stat['Tutar'].str.replace(' TL', '').str.replace(',', '').astype(float)
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam İşlem", len(df_stat))
    col2.metric("Toplam Ciro", f"{df_stat['Sayısal Tutar'].sum():,.2f} TL")
    col3.metric("Tahmini Komisyon", f"{df_stat['Sayısal Tutar'].sum()*0.02:,.2f} TL")

# --- SEKMELER ---
tab1, tab2, tab3 = st.tabs(["📊 İşlem Yönetimi", "📜 Profesyonel Sözleşme", "⚙️ Ayarlar"])

with tab1:
    col_f, col_l = st.columns([1, 2])
    with col_f:
        st.subheader("Yeni Kayıt")
        m_isim = st.text_input("Müşteri Ad Soyad:")
        m_islem = st.selectbox("İşlem:", ["Konut Satışı", "Kiralama", "Arsa/Arazi"])
        m_tutar = st.number_input("Bedel (TL):", min_value=0, value=1000000)
        if st.button("Kaydet"):
            yeni = {
                "id": len(st.session_state.kayitlar) + 1,
                "Tarih": datetime.now().strftime("%d-%m-%Y"),
                "Müşteri": m_isim, "İşlem": m_islem, "Tutar": f"{m_tutar:,.2f} TL"
            }
            st.session_state.kayitlar.append(yeni)
            verileri_kaydet(st.session_state.kayitlar)
            st.rerun()

    with col_l:
        st.subheader("Kayıtlı Portföy")
        if st.session_state.kayitlar:
            df = pd.DataFrame(st.session_state.kayitlar)
            st.dataframe(df, use_container_width=True)
            silinecek = st.selectbox("Silmek için seçin:", range(len(st.session_state.kayitlar)), format_func=lambda x: st.session_state.kayitlar[x]['Müşteri'])
            if st.button("Seçili Kaydı Sil"):
                st.session_state.kayitlar.pop(silinecek)
                verileri_kaydet(st.session_state.kayitlar)
                st.rerun()

with tab2:
    st.subheader("📜 Sözleşme Oluşturucu")
    if st.session_state.kayitlar:
        # BURASI KRİTİK: Eski müşteriyi seçme özelliği
        secilen_musteri_idx = st.selectbox("Sözleşme yapılacak müşteriyi seçin:", 
                                            range(len(st.session_state.kayitlar)),
                                            format_func=lambda x: f"{st.session_state.kayitlar[x]['Müşteri']} ({st.session_state.kayitlar[x]['Tarih']})")
        
        m_data = st.session_state.kayitlar[secilen_musteri_idx]

        def pro_pdf_olustur(data):
            pdf = FPDF()
            pdf.add_font("Roboto", style="", fname="Roboto_Condensed-Light.ttf")
            pdf.add_font("Roboto", style="B", fname="Roboto_Condensed-Bold.ttf")
            pdf.add_page()
            
            # Başlık
            pdf.set_font("Roboto", "B", 16)
            pdf.cell(0, 10, "TAŞINMAZ GÖSTERME VE YETKİ BELGESİ", align='C', ln=True)
            pdf.ln(5)
            
            # Profesyonel Maddeler
            pdf.set_font("Roboto", "", 10)
            pdf.multi_cell(0, 7, f"İşbu belge, {data['Müşteri']} (Bundan böyle 'MÜŞTERİ' olarak anılacaktır) ile {st.session_state.user.upper()} (Bundan böyle 'DANIŞMAN' olarak anılacaktır) arasında {data['Tarih']} tarihinde düzenlenmiştir.")
            pdf.ln(3)
            
            pdf.set_font("Roboto", "B", 11)
            pdf.cell(0, 10, "1. SÖZLEŞME KONUSU VE HİZMET BEDELİ", ln=True)
            pdf.set_font("Roboto", "", 10)
            pdf.multi_cell(0, 7, f"Danışman, Müşteri'ye söz konusu taşınmazı göstermeyi; Müşteri ise bu taşınmazı satın alması/kiralaması durumunda taşınmaz bedeli olan {data['Tutar']} üzerinden %2 + KDV oranında hizmet bedeli ödemeyi kabul eder.")
            
            pdf.set_font("Roboto", "B", 11)
            pdf.cell(0, 10, "2. CEZAİ ŞART", ln=True)
            pdf.set_font("Roboto", "", 10)
            pdf.multi_cell(0, 7, "Müşteri, kendisine gösterilen taşınmazı Danışman'ı devre dışı bırakarak mal sahibinden doğrudan satın alması durumunda, hizmet bedelinin iki katı tutarında cezai şart ödemeyi taahhüt eder.")
            
            pdf.ln(20)
            pdf.cell(90, 10, "MÜŞTERİ İMZA", align='L')
            pdf.cell(0, 10, "DANIŞMAN İMZA", align='R')
            
            return pdf.output()

        if st.button("📄 Profesyonel PDF Üret"):
            pdf_raw = pro_pdf_olustur(m_data)
            st.download_button("📥 PDF Dosyasını İndir", data=bytes(pdf_raw), file_name=f"sozlesme_{m_data['Müşteri']}.pdf")
    else:
        st.info("Sözleşme oluşturmak için önce 'İşlem Yönetimi' kısmından bir kayıt eklemelisiniz.")

with tab3:
    if st.button("🚪 Güvenli Çıkış"):
        st.session_state.user = None
        st.rerun()