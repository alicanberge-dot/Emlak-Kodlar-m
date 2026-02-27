import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from fpdf import FPDF

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Elite Emlak Cloud AI", page_icon="🏢", layout="wide")

# --- YARDIMCI FONKSİYONLAR (HATA ÖNLEYİCİLER) ---
def tutar_temizle(tutar):
    """Her türlü tutar formatını (str veya int) sayıya çevirir."""
    if isinstance(tutar, (int, float)):
        return float(tutar)
    if isinstance(tutar, str):
        # "2.000.000 TL" gibi metinleri temizler
        t = tutar.replace(" TL", "").replace(".", "").replace(",", "").strip()
        try:
            return float(t)
        except:
            return 0.0
    return 0.0

# --- VERİ YÖNETİMİ ---
USERS_FILE = "kullanicilar.json"
def kullanicilari_yukle():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return {}

# --- GİRİŞ SİSTEMİ ---
if 'user' not in st.session_state: st.session_state.user = None
if st.session_state.user is None:
    st.title("🔐 Elite Emlak Cloud AI Login")
    u = st.text_input("Kullanıcı Adı:").lower().strip()
    p = st.text_input("Şifre:", type="password")
    if st.button("Sisteme Bağlan"):
        db = kullanicilari_yukle()
        if u in db and db[u] == p:
            st.session_state.user = u
            st.rerun()
        else: st.error("Hatalı Bilgi")
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
st.title(f"🏢 {st.session_state.user.upper()} - Profesyonel Emlak Yönetimi")

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Portföy Yönetimi", "🔍 Müşteri Talepleri", "🤖 Akıllı Eşleştirme", "📜 Elite Sözleşme & Analiz"])

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
            yeni = {
                "Mülk": p_ad, "Müşteri": p_ad, "Tür": p_tur, "Oda": p_oda, 
                "Tutar": float(p_tutar), "Konum": p_konum, "Tarih": datetime.now().strftime("%d-%m-%Y")
            }
            st.session_state.kayitlar.append(yeni)
            with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(st.session_state.kayitlar, f, ensure_ascii=False, indent=4)
            st.success("Kayıt Başarılı!")
            st.rerun()
    with col_t:
        st.subheader("Aktif Portföy Listesi")
        if st.session_state.kayitlar:
            st.dataframe(pd.DataFrame(st.session_state.kayitlar), use_container_width=True)
            if st.button("Tüm Listeyi Temizle (Hata Alıyorsanız Deneyin)"):
                st.session_state.kayitlar = []
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.rerun()

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
            yeni_t = {"Müşteri": t_ad, "Tür": t_tur, "Oda": t_oda, "Butce": float(t_max)}
            st.session_state.talepler.append(yeni_t)
            with open(TALEPLER_FILE, "w", encoding="utf-8") as f: json.dump(st.session_state.talepler, f, ensure_ascii=False, indent=4)
            st.rerun()
    with col_tt:
        if st.session_state.talepler:
            st.dataframe(pd.DataFrame(st.session_state.talepler), use_container_width=True)

# --- TAB 3: AKILLI EŞLEŞTİRME ---
with tab3:
    st.subheader("🤖 Algoritmik Eşleştirme Sistemi")
    if st.session_state.kayitlar and st.session_state.talepler:
        bulunan = False
        for t in st.session_state.talepler:
            for p in st.session_state.kayitlar:
                p_tutar_val = tutar_temizle(p.get('Tutar', 0))
                t_butce_val = tutar_temizle(t.get('Butce', 0))
                if t.get('Tür') == p.get('Tür') and t.get('Oda') == p.get('Oda') and p_tutar_val <= t_butce_val:
                    st.success(f"🌟 **EŞLEŞME:** {t.get('Müşteri')} -> {p.get('Mülk')} ({p.get('Konum')})")
                    bulunan = True
        if not bulunan: st.info("Şu an kriterleri uyuşan kayıt yok.")

# --- TAB 4: SÖZLEŞME & ANALİZ ---
with tab4:
    st.subheader("📜 Elite Yer Gösterme Belgesi & Yatırım Analizi")
    if st.session_state.kayitlar:
        s_idx = st.selectbox("İşlem Seçin:", range(len(st.session_state.kayitlar)), 
                             format_func=lambda x: f"{st.session_state.kayitlar[x].get('Mülk', 'İsimsiz')}")
        m_sel = st.session_state.kayitlar[s_idx]
        
        tc = st.text_input("Müşteri TC/Vergi No:")
        ap = st.text_input("Ada/Parsel Bilgisi:")

        def elite_pdf(d, tc_no, ada_p):
            pdf = FPDF()
            pdf.add_font("Roboto", style="", fname="Roboto_Condensed-Light.ttf")
            pdf.add_font("Roboto", style="B", fname="Roboto_Condensed-Bold.ttf")
            pdf.add_page()
            pdf.rect(5, 5, 200, 287)
            pdf.set_font("Roboto", "B", 16)
            pdf.cell(0, 15, "TAŞINMAZ GÖSTERME VE YETKİ BELGESİ", align='C', ln=True)
            pdf.set_font("Roboto", "", 10)
            pdf.cell(0, 5, "Bu belge Taşınmaz Ticareti Hakkında Yönetmelik Madde 19 uyarınca tanzim edilmiştir.", align='C', ln=True)
            pdf.ln(10)
            pdf.set_font("Roboto", "B", 11)
            pdf.cell(0, 8, " 1. TARAFLAR VE TAŞINMAZ BİLGİLERİ", ln=True, fill=False)
            pdf.set_font("Roboto", "", 10)
            t_bedel = tutar_temizle(d.get('Tutar', 0))
            pdf.multi_cell(0, 7, f"DANIŞMAN: {st.session_state.user.upper()} \nMÜŞTERİ: {d.get('Mülk', '').upper()} \nTC/VERGİ NO: {tc_no} \nADA/PARSEL: {ada_p} \nTAŞINMAZ BEDELİ: {t_bedel:,.0f} TL")
            pdf.ln(5)
            pdf.set_font("Roboto", "B", 11)
            pdf.cell(0, 8, " 2. HUKUKİ ŞARTLAR", ln=True)
            pdf.set_font("Roboto", "", 10)
            hukuk = ("1- Müşteri, gösterilen taşınmazı satın alması durumunda %2 + KDV hizmet bedeli ödemeyi kabul eder.\n"
                     "2- CEZAİ ŞART: Müşteri, danışmanı devre dışı bırakarak mal sahibi ile doğrudan işlem yaparsa, "
                     "hizmet bedelinin 2 katını cezai şart olarak ödemeyi taahhüt eder.\n"
                     "3- Bu belge imza tarihinden itibaren 1 (bir) yıl geçerlidir.")
            pdf.multi_cell(0, 6, hukuk)
            pdf.ln(30)
            pdf.cell(90, 10, "MÜŞTERİ İMZA", align='L')
            pdf.cell(0, 10, "DANIŞMAN İMZA", align='R')
            return pdf.output()

        if st.button("🚀 Elite PDF Üret"):
            pdf_raw = elite_pdf(m_sel, tc, ap)
            st.download_button("📥 İndir", data=bytes(pdf_raw), file_name="Elite_Sozlesme.pdf")

        st.divider()
        st.subheader("🧮 Amortisman Analizi")
        k_getiri = st.number_input("Tahmini Aylık Kira (TL):", value=20000)
        t_val = tutar_temizle(m_sel.get('Tutar', 0))
        if k_getiri > 0 and t_val > 0:
            yil = t_val / (k_getiri * 12)
            st.metric("Amortisman Süresi", f"{yil:.1f} Yıl")