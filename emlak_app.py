import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from fpdf import FPDF

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Elite Emlak Cloud AI", page_icon="🏢", layout="wide")

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
    st.title("🔐 Elite Emlak Cloud AI Login")
    t1, t2 = st.tabs(["Giriş Yap", "Hesap Oluştur"])
    with t1:
        u = st.text_input("Kullanıcı Adı:").lower().strip()
        p = st.text_input("Şifre:", type="password")
        if st.button("Sisteme Bağlan"):
            db = kullanicilari_yukle()
            if u in db and db[u] == p:
                st.session_state.user = u
                st.rerun()
            else: st.error("Hatalı Bilgi")
    with t2:
        nu = st.text_input("Yeni Kayıt Adı:").lower().strip()
        np = st.text_input("Şifre Belirle:", type="password")
        if st.button("Hesabı Oluştur"):
            if nu and np:
                kullanici_kaydet(nu, np)
                st.success("Hesap Hazır! Giriş sekmesine geçebilirsiniz.")
    st.stop()

# --- VERİ TABANI ---
DB_FILE = f"db_{st.session_state.user}.json"
TALEPLER_FILE = f"talepler_{st.session_state.user}.json"

def veri_yukle(dosya):
    if os.path.exists(dosya):
        with open(dosya, "r", encoding="utf-8") as f: return json.load(f)
    return []

if 'kayitlar' not in st.session_state: st.session_state.kayitlar = veri_yukle(DB_FILE)
if 'talepler' not in st.session_state: st.session_state.talepler = veri_yukle(TALEPLER_FILE)

# --- ANA PANEL ---
st.title(f"🏢 {st.session_state.user.upper()} - Akıllı Dijital Ofis")

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Portföy Yönetimi", "🔍 Müşteri Talepleri", "🤖 Akıllı Eşleştirme", "📜 Sözleşme & Analiz"])

# --- TAB 1: PORTFÖY YÖNETİMİ ---
with tab1:
    col_f, col_t = st.columns([1, 2])
    with col_f:
        st.subheader("Yeni Portföy Ekle")
        p_ad = st.text_input("Mülk Sahibi / İlan Başlığı:")
        p_tur = st.selectbox("Tür:", ["Daire", "Arsa", "Ticari"], key="ptur_reg")
        p_oda = st.selectbox("Oda Sayısı:", ["1+1", "2+1", "3+1", "4+1", "Arsa/Diğer"], key="poda_reg")
        p_tutar = st.number_input("Satış Bedeli (TL):", value=2000000)
        p_konum = st.text_input("Konum (İlçe/Semt):")
        if st.button("Portföyü Kaydet"):
            # Hem 'Mülk' hem 'Müşteri' adıyla kaydediyoruz ki eski/yeni kod karmaşası bitsin
            yeni = {
                "Mülk": p_ad, 
                "Müşteri": p_ad, 
                "Tür": p_tur, 
                "Oda": p_oda, 
                "Tutar": p_tutar, 
                "Konum": p_konum, 
                "Tarih": datetime.now().strftime("%d-%m-%Y")
            }
            st.session_state.kayitlar.append(yeni)
            with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(st.session_state.kayitlar, f, ensure_ascii=False, indent=4)
            st.success("Portföy eklendi!")
            st.rerun()
    with col_t:
        st.subheader("Aktif Portföy Listesi")
        if st.session_state.kayitlar:
            st.dataframe(pd.DataFrame(st.session_state.kayitlar), use_container_width=True)

# --- TAB 2: MÜŞTERİ TALEPLERİ ---
with tab2:
    col_tf, col_tt = st.columns([1, 2])
    with col_tf:
        st.subheader("Yeni Müşteri Arayışı")
        t_ad = st.text_input("Arayan Müşteri Adı:")
        t_tur = st.selectbox("Aradığı Tür:", ["Daire", "Arsa", "Ticari"], key="ttur_req")
        t_oda = st.selectbox("İstediği Oda:", ["1+1", "2+1", "3+1", "4+1", "Arsa/Diğer"], key="toda_req")
        t_max = st.number_input("Maksimum Bütçe (TL):", value=3000000)
        if st.button("Talebi Kaydet"):
            yeni_t = {"Müşteri": t_ad, "Tür": t_tur, "Oda": t_oda, "Butce": t_max}
            st.session_state.talepler.append(yeni_t)
            with open(TALEPLER_FILE, "w", encoding="utf-8") as f: json.dump(st.session_state.talepler, f, ensure_ascii=False, indent=4)
            st.success("Talep havuzuna eklendi!")
            st.rerun()
    with col_tt:
        st.subheader("Bekleyen Talepler")
        if st.session_state.talepler:
            st.dataframe(pd.DataFrame(st.session_state.talepler), use_container_width=True)

# --- TAB 3: AKILLI EŞLEŞTİRME ---
with tab3:
    st.subheader("🤖 Algoritmik Portföy-Talep Eşleşmesi")
    if not st.session_state.kayitlar or not st.session_state.talepler:
        st.info("Eşleştirme yapabilmek için veri girişi yapmalısınız.")
    else:
        bulunan = False
        for t in st.session_state.talepler:
            for p in st.session_state.kayitlar:
                if t.get('Tür') == p.get('Tür') and t.get('Oda') == p.get('Oda') and p.get('Tutar', 0) <= t.get('Butce', 0):
                    st.success(f"🌟 **MÜKEMMEL EŞLEŞME!**")
                    st.write(f"👤 **Arayan:** {t.get('Müşteri')} | 🏠 **Mülk:** {p.get('Mülk', p.get('Müşteri'))}")
                    st.write(f"💰 **Fiyat:** {p.get('Tutar'):,} TL (Bütçe: {t.get('Butce'):,} TL)")
                    st.divider()
                    bulunan = True
        if not bulunan: st.warning("Tam eşleşme bulunamadı.")

# --- TAB 4: SÖZLEŞME & ANALİZ (HATA DÜZELTİLMİŞ) ---
with tab4:
    st.subheader("📜 Elite Sözleşme & 🧮 Amortisman")
    if st.session_state.kayitlar:
        # HATA BURADAYDI: get() ile güvenli hale getirildi
        s_idx = st.selectbox(
            "İşlem Seçin:", 
            range(len(st.session_state.kayitlar)), 
            format_func=lambda x: f"{st.session_state.kayitlar[x].get('Mülk', st.session_state.kayitlar[x].get('Müşteri', 'İsimsiz'))}"
        )
        m_sel = st.session_state.kayitlar[s_idx]
        
        col_pdf1, col_pdf2 = st.columns(2)
        tc = col_pdf1.text_input("Müşteri TC/Vergi No:")
        ap = col_pdf2.text_input("Ada/Parsel Bilgisi:")

        def elite_pdf(d, tc_no, ada_p):
            pdf = FPDF()
            pdf.add_font("Roboto", style="", fname="Roboto_Condensed-Light.ttf")
            pdf.add_font("Roboto", style="B", fname="Roboto_Condensed-Bold.ttf")
            pdf.add_page()
            pdf.rect(5, 5, 200, 287)
            pdf.set_font("Roboto", "B", 18)
            pdf.cell(0, 15, "TAŞINMAZ YER GÖSTERME SÖZLEŞMESİ", align='C', ln=True)
            pdf.ln(10)
            pdf.set_font("Roboto", "", 11)
            isim = d.get('Mülk', d.get('Müşteri', 'Belirtilmedi'))
            tutar = d.get('Tutar', 0)
            pdf.multi_cell(0, 8, f"MÜŞTERİ: {isim.upper()} \nTC: {tc_no} \nADA/PARSEL: {ada_p} \nTUTAR: {tutar:,} TL")
            pdf.ln(10)
            pdf.multi_cell(0, 8, "Müşteri, kendisine gösterilen bu taşınmazı satın alması durumunda %2+KDV hizmet bedeli ödemeyi ve danışmanı devre dışı bırakması halinde cezai şart ödemeyi kabul eder.")
            pdf.ln(40)
            pdf.cell(90, 10, "MÜŞTERİ İMZA", align='L')
            pdf.cell(0, 10, "DANIŞMAN İMZA", align='R')
            return pdf.output()

        if st.button("🚀 Elite Sözleşme PDF İndir"):
            pdf_out = elite_pdf(m_sel, tc, ap)
            st.download_button("📥 Dosyayı İndir", data=bytes(pdf_out), file_name=f"Elite_Sozlesme.pdf")
        
        st.divider()
        st.subheader("🧮 Yatırım Analizi")
        k_getiri = st.number_input("Tahmini Aylık Kira (TL):", value=20000)
        tutar_val = m_sel.get('Tutar', 0)
        if k_getiri > 0 and tutar_val > 0:
            yil = tutar_val / (k_getiri * 12)
            st.metric("Amortisman Süresi", f"{yil:.1f} Yıl")
    else:
        st.info("Kayıtlı mülk bulunamadı.")

if st.sidebar.button("🚪 Güvenli Çıkış"):
    st.session_state.user = None
    st.rerun()