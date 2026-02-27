import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from fpdf import FPDF

# Sayfa Ayarları
st.set_page_config(page_title="Emlak CRM Pro", page_icon="🏛️", layout="wide")

# --- VERİ YÖNETİMİ ---
USERS_FILE = "kullanicilar.json"
def kullanicilari_yukle():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {}

def kullanici_kaydet(username, password):
    db = kullanicilari_yukle()
    db[username] = password
    with open(USERS_FILE, "w", encoding="utf-8") as f: json.dump(db, f)

# --- GİRİŞ SİSTEMİ ---
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.title("🏛️ Emlak CRM Pro Girişi")
    t1, t2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    with t1:
        u = st.text_input("Kullanıcı Adı:").lower().strip()
        p = st.text_input("Şifre:", type="password")
        if st.button("Giriş"):
            db = kullanicilari_yukle()
            if u in db and db[u] == p:
                st.session_state.user = u
                st.rerun()
            else: st.error("Hatalı giriş!")
    with t2:
        nu = st.text_input("Yeni K. Adı:").lower().strip()
        np = st.text_input("Yeni Şifre:", type="password")
        if st.button("Kayıt Ol"):
            if nu and np:
                kullanici_kaydet(nu, np)
                st.success("Kayıt başarılı, giriş yapabilirsiniz.")
    st.stop()

# --- VERİ TABANI ---
DB_FILE = f"db_{st.session_state.user}.json"
def verileri_yukle():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return []

if 'kayitlar' not in st.session_state:
    st.session_state.kayitlar = verileri_yukle()

# --- PROFESYONEL PANEL ---
st.title(f"💼 Hoş geldin, {st.session_state.user.upper()}")

if st.session_state.kayitlar:
    df_stat = pd.DataFrame(st.session_state.kayitlar)
    df_stat['Sayısal'] = df_stat['Tutar'].str.replace(' TL','').str.replace(',','').astype(float)
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Portföy", len(df_stat))
    c2.metric("Toplam İşlem Hacmi", f"{df_stat['Sayısal'].sum():,.0f} TL")
    c3.metric("Tahmini Kazanç (%2)", f"{df_stat['Sayısal'].sum()*0.02:,.0f} TL")

tab1, tab2 = st.tabs(["🗂️ Portföy & İşlem", "📄 Kurumsal Sözleşme Üret"])

with tab1: # HATALI YER BURASIYDI, DÜZELTİLDİ
    col_form, col_list = st.columns([1, 2])
    with col_form:
        st.subheader("Yeni İşlem Kaydı")
        m_ad = st.text_input("Müşteri Ad Soyad:")
        m_islem = st.selectbox("İşlem Tipi:", ["Konut Satışı", "Kiralama", "Arsa Satışı"])
        m_tutar = st.number_input("İşlem Tutarı (TL):", value=1000000, step=50000)
        if st.button("Sisteme İşle"):
            hizmet_bedeli_hesap = m_tutar * 0.02
            yeni = {
                "Tarih": datetime.now().strftime("%d-%m-%Y"),
                "Müşteri": m_ad, "İşlem": m_islem, 
                "Tutar": f"{m_tutar:,.2f} TL",
                "Hizmet Bedeli": f"{hizmet_bedeli_hesap:,.2f} TL"
            }
            st.session_state.kayitlar.append(yeni)
            with open(DB_FILE, "w", encoding="utf-8") as f: 
                json.dump(st.session_state.kayitlar, f, ensure_ascii=False, indent=4)
            st.rerun()

    with col_list:
        st.subheader("Mevcut Kayıtlar")
        if st.session_state.kayitlar:
            st.dataframe(pd.DataFrame(st.session_state.kayitlar), use_container_width=True)
            st.divider()
            st.write("🗑️ **Kayıt Silme Paneli**")
            silme_listesi = [f"{i}: {k['Müşteri']}" for i, k in enumerate(st.session_state.kayitlar)]
            secilen_silme = st.selectbox("Silinecek kaydı seçin:", options=range(len(silme_listesi)), format_func=lambda x: silme_listesi[x])
            if st.button("Seçili Kaydı Tamamen Sil"):
                st.session_state.kayitlar.pop(secilen_silme)
                with open(DB_FILE, "w", encoding="utf-8") as f: 
                    json.dump(st.session_state.kayitlar, f, ensure_ascii=False, indent=4)
                st.rerun()

with tab2:
    st.subheader("📜 Sözleşme Hazırlama Merkezi")
    if st.session_state.kayitlar:
        secim = st.selectbox("Müşteri seçin:", range(len(st.session_state.kayitlar)),
                             format_func=lambda x: f"{st.session_state.kayitlar[x]['Müşteri']}")
        m = st.session_state.kayitlar[secim]
        
        def pro_pdf(data):
            pdf = FPDF()
            pdf.add_font("Roboto", style="", fname="Roboto_Condensed-Light.ttf")
            pdf.add_font("Roboto", style="B", fname="Roboto_Condensed-Bold.ttf")
            pdf.add_page()
            pdf.rect(5, 5, 200, 287)
            pdf.set_font("Roboto", "B", 18)
            pdf.cell(0, 15, "TAŞINMAZ GÖSTERME VE YETKİ BELGESİ", align='C', ln=True)
            pdf.set_font("Roboto", "", 11)
            pdf.ln(10)
            text = f"İşbu belge, danışman {st.session_state.user.upper()} ile müşteri {data['Müşteri']} arasında düzenlenmiştir."
            pdf.multi_cell(0, 10, text)
            pdf.ln(20)
            pdf.cell(90, 10, "MÜŞTERİ İMZA", align='L')
            pdf.cell(0, 10, "DANIŞMAN İMZA", align='R')
            return pdf.output()

        if st.button("🚀 Profesyonel Sözleşmeyi Oluştur"):
            raw_pdf = pro_pdf(m)
            st.download_button("📥 İndir", data=bytes(raw_pdf), file_name=f"Sozlesme_{m['Müşteri']}.pdf")

if st.sidebar.button("🚪 Çıkış Yap"):
    st.session_state.user = None
    st.rerun()