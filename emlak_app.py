import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from fpdf import FPDF

# Sayfa Ayarları
st.set_page_config(page_title="Emlak CRM Elite", page_icon="🏛️", layout="wide")

# --- VERİ YÖNETİMİ ---
USERS_FILE = "kullanicilar.json"
def kullanicilari_yukle():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {}

def kullanici_kaydet(username, password):
    db = kullanicilari_yukle()
    db[username] = password
    with open(USERS_FILE, "w", encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False, indent=4)

# --- GİRİŞ SİSTEMİ ---
if 'user' not in st.session_state: st.session_state.user = None

if st.session_state.user is None:
    st.title("🏛️ Emlak CRM Elite Girişi")
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

# --- ANA PANEL ---
st.title(f"💼 Hoş geldin, {st.session_state.user.upper()}")

if st.session_state.kayitlar:
    df_stat = pd.DataFrame(st.session_state.kayitlar)
    df_stat['Sayısal'] = df_stat['Tutar'].str.replace(' TL','').str.replace(',','').astype(float)
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Portföy", len(df_stat))
    c2.metric("İşlem Hacmi", f"{df_stat['Sayısal'].sum():,.0f} TL")
    c3.metric("Kazanç Potansiyeli", f"{df_stat['Sayısal'].sum()*0.02:,.0f} TL")

tab1, tab2 = st.tabs(["🗂️ Portföy Yönetimi", "📜 Kurumsal Sözleşme Hazırla"])

with tab1:
    col_f, col_l = st.columns([1, 2])
    with col_f:
        st.subheader("Yeni İşlem")
        m_ad = st.text_input("Müşteri Ad Soyad:")
        m_islem = st.selectbox("İşlem Tipi:", ["Konut Satışı", "Ticari Satış", "Kiralama"])
        m_tutar = st.number_input("İşlem Tutarı (TL):", value=2000000, step=100000)
        if st.button("Kaydet"):
            hizmet = m_tutar * 0.02
            yeni = {
                "Tarih": datetime.now().strftime("%d-%m-%Y"),
                "Müşteri": m_ad, "İşlem": m_islem, 
                "Tutar": f"{m_tutar:,.2f} TL",
                "Hizmet Bedeli": f"{hizmet:,.2f} TL"
            }
            st.session_state.kayitlar.append(yeni)
            with open(DB_FILE, "w", encoding="utf-8") as f: 
                json.dump(st.session_state.kayitlar, f, ensure_ascii=False, indent=4)
            st.rerun()

    with col_l:
        st.subheader("Müşteri Listesi")
        if st.session_state.kayitlar:
            st.dataframe(pd.DataFrame(st.session_state.kayitlar), use_container_width=True)
            st.divider()
            idx = st.selectbox("İşlem Seçin:", range(len(st.session_state.kayitlar)), format_func=lambda x: st.session_state.kayitlar[x]['Müşteri'])
            if st.button("Seçili Kaydı Sil"):
                st.session_state.kayitlar.pop(idx)
                with open(DB_FILE, "w", encoding="utf-8") as f: 
                    json.dump(st.session_state.kayitlar, f, ensure_ascii=False, indent=4)
                st.rerun()

with tab2:
    st.subheader("📜 Elite Sözleşme Oluşturucu")
    if st.session_state.kayitlar:
        secim = st.selectbox("Sözleşme yapılacak müşteriyi seçin:", range(len(st.session_state.kayitlar)),
                             format_func=lambda x: f"{st.session_state.kayitlar[x]['Müşteri']} ({st.session_state.kayitlar[x]['Tarih']})")
        m = st.session_state.kayitlar[secim]
        
        def pro_pdf_elite(data):
            pdf = FPDF()
            pdf.add_font("Roboto", style="", fname="Roboto_Condensed-Light.ttf")
            pdf.add_font("Roboto", style="B", fname="Roboto_Condensed-Bold.ttf")
            pdf.add_page()
            
            # --- PROFESYONEL TASARIM ---
            pdf.set_draw_color(30, 30, 30)
            pdf.rect(5, 5, 200, 287) # Çerçeve
            
            # Başlık Bloğu
            pdf.set_font("Roboto", "B", 20)
            pdf.cell(0, 20, "TAŞINMAZ YER GÖSTERME BELGESİ", align='C', ln=True)
            pdf.set_font("Roboto", "", 9)
            pdf.cell(0, 5, "Bu belge Taşınmaz Ticareti Hakkında Yönetmelik Madde 19 uyarınca tanzim edilmiştir.", align='C', ln=True)
            pdf.ln(10)

            # 1. Bölüm: Bilgiler
            pdf.set_fill_color(245, 245, 245)
            pdf.set_font("Roboto", "B", 12)
            pdf.cell(0, 10, " 1. TARAFLAR VE TAŞINMAZ BİLGİSİ", ln=True, fill=True)
            pdf.set_font("Roboto", "", 10)
            pdf.ln(2)
            pdf.cell(0, 7, f"DANIŞMAN : {st.session_state.user.upper()}", ln=True)
            pdf.cell(0, 7, f"MÜŞTERİ  : {data['Müşteri'].upper()}", ln=True)
            pdf.cell(0, 7, f"TARİH    : {data['Tarih']}", ln=True)
            pdf.ln(5)

            # 2. Bölüm: Hukuki Şartlar
            pdf.set_font("Roboto", "B", 12)
            pdf.cell(0, 10, " 2. HİZMET BEDELİ VE YASAL YÜKÜMLÜLÜKLER", ln=True, fill=True)
            pdf.set_font("Roboto", "", 10)
            pdf.ln(2)
            metin = (
                f"1- Müşteri, danışman tarafından kendisine gösterilen taşınmazı satın alması/kiralaması durumunda "
                f"taşınmaz bedeli olan {data['Tutar']} üzerinden %2 + KDV oranında hizmet bedeli ödemeyi kabul eder.\n\n"
                f"2- CEZAİ ŞART: Müşteri, gösterilen taşınmazı danışmanı devre dışı bırakarak mal sahibinden doğrudan "
                f"satın alması veya kiralaması durumunda, yukarıda belirtilen hizmet bedelinin 2 (iki) katı tutarında "
                f"cezai şartı itirazsız ödemeyi taahhüt eder.\n\n"
                f"3- Bu belge, taşınmazın gösterildiği tarihten itibaren 12 (on iki) ay süreyle geçerlidir."
            )
            pdf.multi_cell(0, 6, metin)

            # İmza Alanı
            pdf.ln(40)
            pdf.set_font("Roboto", "B", 11)
            pdf.cell(90, 10, "MÜŞTERİ İMZA", align='L')
            pdf.cell(0, 10, "DANIŞMAN / OFİS İMZA", align='R')
            
            return pdf.output()

        if st.button("🚀 Elite Sözleşme PDF'i Oluştur"):
            raw_pdf = pro_pdf_elite(m)
            st.download_button(f"📥 {m['Müşteri']}_Sozlesme.pdf İndir", data=bytes(raw_pdf), file_name=f"Elite_Sozlesme_{m['Müşteri']}.pdf")
    else:
        st.info("Kayıtlı müşteri bulunamadı.")

if st.sidebar.button("🚪 Güvenli Çıkış"):
    st.session_state.user = None
    st.rerun()