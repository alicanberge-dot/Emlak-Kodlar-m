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

# Üst İstatistik Paneli
if st.session_state.kayitlar:
    df_stat = pd.DataFrame(st.session_state.kayitlar)
    # Tutar sütununu sayıya çevir
    df_stat['Sayısal'] = df_stat['Tutar'].str.replace(' TL','').str.replace(',','').astype(float)
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Portföy", len(df_stat))
    c2.metric("Toplam İşlem Hacmi", f"{df_stat['Sayısal'].sum():,.0f} TL")
    c3.metric("Tahmini Kazanç (%2)", f"{df_stat['Sayısal'].sum()*0.02:,.0f} TL")

tab1, tab2 = st.tabs(["🗂️ Portföy & İşlem", "📄 Kurumsal Sözleşme Üret"])

with tab1:
    col_form, col_list = st.columns([1, 2])
    with col_form:
        st.subheader("Yeni İşlem Kaydı")
        m_ad = st.text_input("Müşteri Ad Soyad:")
        m_islem = st.selectbox("İşlem Tipi:", ["Konut Satışı", "Kiralama", "Arsa Satışı"])
        m_tutar = st.number_input("İşlem Tutarı (TL):", value=1000000, step=50000)
        if st.button("Sisteme İşle"):
            yeni = {
                "Tarih": datetime.now().strftime("%d-%m-%Y"),
                "Müşteri": m_ad, "İşlem": m_islem, "Tutar": f"{m_tutar:,.2f} TL"
            }
            st.session_state.kayitlar.append(yeni)
            with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(st.session_state.kayitlar, f)
            st.success("Kayıt başarıyla eklendi!")
            st.rerun()

    with col_list:
        st.subheader("Mevcut Kayıtlar")
        if st.session_state.kayitlar:
            st.dataframe(pd.DataFrame(st.session_state.kayitlar), use_container_width=True)

with tab2:
    st.subheader("📜 Sözleşme Hazırlama Merkezi")
    if st.session_state.kayitlar:
        # ESKİ MÜŞTERİYİ SEÇME (İstediğin Özellik)
        secim = st.selectbox("Sözleşme basılacak müşteriyi seçin:", 
                             range(len(st.session_state.kayitlar)),
                             format_func=lambda x: f"{st.session_state.kayitlar[x]['Müşteri']} - {st.session_state.kayitlar[x]['Tarih']}")
        
        m = st.session_state.kayitlar[secim]
        
        def pro_pdf(data):
            pdf = FPDF()
            pdf.add_font("Roboto", style="", fname="Roboto_Condensed-Light.ttf")
            pdf.add_font("Roboto", style="B", fname="Roboto_Condensed-Bold.ttf")
            pdf.add_page()
            
            # Üst Başlık & Çerçeve
            pdf.set_draw_color(50, 50, 50)
            pdf.rect(5, 5, 200, 287) # Sayfa çerçevesi
            
            pdf.set_font("Roboto", "B", 18)
            pdf.cell(0, 15, "TAŞINMAZ GÖSTERME VE YETKİ BELGESİ", align='C', ln=True)
            pdf.set_font("Roboto", "", 9)
            pdf.cell(0, 5, "Bu belge 6098 Sayılı Türk Borçlar Kanunu ve Taşınmaz Ticareti Yönetmeliği'ne uygundur.", align='C', ln=True)
            pdf.ln(10)

            # İçerik
            pdf.set_font("Roboto", "B", 12)
            pdf.cell(0, 10, "1. TARAFLAR VE KONU", ln=True)
            pdf.set_font("Roboto", "", 11)
            text = (f"İşbu sözleşme, bir tarafta emlak danışmanı {st.session_state.user.upper()} ile diğer tarafta "
                    f"müşteri {data['Müşteri']} arasında, aşağıda belirtilen taşınmazın gösterilmesi ve "
                    f"aracılık hizmetleri amacıyla {data['Tarih']} tarihinde imzalanmıştır.")
            pdf.multi_cell(0, 7, text)
            
            pdf.ln(5)
            pdf.set_font("Roboto", "B", 12)
            pdf.cell(0, 10, "2. HİZMET BEDELİ VE ŞARTLAR", ln=True)
            pdf.set_font("Roboto", "", 11)
            madde = (f"- Danışman tarafından gösterilen taşınmazın bedeli {data['Tutar']} olarak beyan edilmiştir.\n"
                     f"- Taşınmazın satışı durumunda müşteri %2 + KDV tutarında hizmet bedeli ödemeyi kabul eder.\n"
                     f"- Gösterilen taşınmazın, danışman devre dışı bırakılarak doğrudan veya dolaylı yoldan satın alınması "
                     f"durumunda müşteri, hizmet bedelinin 2 katı tutarında cezai şart ödemeyi taahhüt eder.")
            pdf.multi_cell(0, 7, madde)

            pdf.ln(30)
            pdf.cell(90, 10, "MÜŞTERİ İMZA", align='L')
            pdf.cell(0, 10, "DANIŞMAN İMZA", align='R')
            return pdf.output()

        if st.button("🚀 Profesyonel Sözleşmeyi Oluştur"):
            raw_pdf = pro_pdf(m)
            st.download_button("📥 Kurumsal PDF'i İndir", data=bytes(raw_pdf), file_name=f"Sözleşme_{m['Müşteri']}.pdf")
    else:
        st.info("Henüz kayıtlı müşteriniz yok.")