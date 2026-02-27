import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from fpdf import FPDF

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Elite Emlak Cloud AI", page_icon="🏢", layout="wide")

# --- YARDIMCI FONKSİYONLAR ---
def tutar_temizle(tutar):
    if isinstance(tutar, (int, float)): return float(tutar)
    if isinstance(tutar, str):
        t = tutar.replace(" TL", "").replace(".", "").replace(",", "").strip()
        try: return float(t)
        except: return 0.0
    return 0.0

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
    t_giris, t_kayit = st.tabs(["Giriş Yap", "Hesap Oluştur"])
    with t_giris:
        u = st.text_input("Kullanıcı Adı:").lower().strip()
        p = st.text_input("Şifre:", type="password")
        if st.button("Sisteme Bağlan"):
            db = kullanicilari_yukle()
            if u in db and db[u] == p:
                st.session_state.user = u
                st.rerun()
            else: st.error("Hatalı Bilgi")
    with t_kayit:
        nu = st.text_input("Yeni Kayıt Adı:").lower().strip()
        np = st.text_input("Şifre Belirle:", type="password")
        if st.button("Hesabı Oluştur"):
            if nu and np:
                kullanici_kaydet(nu, np)
                st.success("Hesap Hazır!")
    st.stop()

# --- VERİ TABANI ---
DB_FILE = f"db_{st.session_state.user}.json"
TALEPLER_FILE = f"talepler_{st.session_state.user}.json"

def veri_yukle(dosya):
    if os.path.exists(dosya):
        with open(dosya, "r", encoding="utf-8") as f: return json.load(f)
    return []

def veri_kaydet(dosya, veri):
    with open(dosya, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

if 'kayitlar' not in st.session_state: st.session_state.kayitlar = veri_yukle(DB_FILE)
if 'talepler' not in st.session_state: st.session_state.talepler = veri_yukle(TALEPLER_FILE)

# --- ANA PANEL ---
st.title(f"🏢 {st.session_state.user.upper()} - Profesyonel Emlak Yönetimi")

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Portföy Yönetimi", "🔍 Müşteri Talepleri", "🤖 Akıllı Eşleştirme", "📜 Elite Sözleşme & Analiz"])

TUR_SECENEKLERI = ["Daire", "Villa", "Dublex", "Triplex", "Arsa", "İşyeri"]
ODA_SECENEKLERI = ["1+1", "2+1", "3+1", "4+1", "5+1", "Dubleks", "Arsa/Diğer"]

# --- TAB 1: PORTFÖY YÖNETİMİ ---
with tab1:
    col_f, col_t = st.columns([1, 2.5])
    with col_f:
        st.subheader("Yeni Portföy Kaydı")
        p_sahibi = st.text_input("Mülk Sahibi (Ad Soyad):")
        p_tel = st.text_input("Telefon Numarası:", key="p_tel_input")
        p_tur = st.selectbox("Tür:", TUR_SECENEKLERI, key="p_tur_sel")
        p_oda = st.selectbox("Oda Sayısı:", ODA_SECENEKLERI, key="p_oda_sel")
        p_konum = st.text_input("Konum (İlçe/Semt):", key="p_konum_input")
        
        c1, c2 = st.columns(2)
        p_bicilen = c1.number_input("Biçilen Değer (TL):", value=0, key="p_bic_val")
        p_teklif = c2.number_input("Teklif Edilen (TL):", value=0, key="p_tek_val")
        
        if st.button("Portföyü Kaydet", use_container_width=True):
            if p_sahibi:
                yeni = {
                    "Mülk Sahibi": p_sahibi, "Telefon": p_tel, "Tür": p_tur, "Oda": p_oda,
                    "Konum": p_konum, "Biçilen Değer": float(p_bicilen),
                    "Teklif Edilen": float(p_teklif), "Tarih": datetime.now().strftime("%d-%m-%Y")
                }
                st.session_state.kayitlar.append(yeni)
                veri_kaydet(DB_FILE, st.session_state.kayitlar)
                st.success("Portföy Kaydedildi!")
                st.rerun()

    with col_t:
        st.subheader("📋 Aktif Portföy Listesi")
        if st.session_state.kayitlar:
            for i, p in enumerate(st.session_state.kayitlar):
                with st.expander(f"📍 {p.get('Mülk Sahibi')} - {p.get('Konum')} ({p.get('Tür')})"):
                    st.write(f"📞 **Tel:** {p.get('Telefon')} | 🛏️ **Oda:** {p.get('Oda')}")
                    st.write(f"💰 **Biçilen:** {p.get('Biçilen Değer',0):,.0f} TL | 🤝 **Teklif:** {p.get('Teklif Edilen',0):,.0f} TL")
                    if st.button(f"🗑️ Bu Portföyü Sil", key=f"del_port_{i}"):
                        st.session_state.kayitlar.pop(i)
                        veri_kaydet(DB_FILE, st.session_state.kayitlar)
                        st.rerun()
        else: st.info("Henüz portföy kaydı yok.")

# --- TAB 2: MÜŞTERİ TALEPLERİ ---
with tab2:
    col_tf, col_tt = st.columns([1, 2.5])
    with col_tf:
        st.subheader("Yeni Müşteri Arayışı")
        t_ad = st.text_input("Müşteri Adı Soyadı:", key="t_ad_input")
        t_tel = st.text_input("Telefon Numarası:", key="t_tel_input")
        t_meslek = st.text_input("Meslek:", key="t_mes_input")
        t_ilan = st.text_input("Aranılan İlan / Başlık:", key="t_ilan_input")
        t_tur = st.selectbox("Tür:", TUR_SECENEKLERI, key="t_tur_sel")
        t_oda = st.selectbox("İstediği Oda:", ODA_SECENEKLERI, key="t_oda_sel")
        t_konum = st.text_input("Aranılan Konum:", key="t_konum_input")
        t_max = st.number_input("Bütçe Aralığı (Maksimum TL):", value=0, key="t_butce_input")
        
        if st.button("Talebi Kaydet", use_container_width=True):
            if t_ad:
                yeni_t = {
                    "Müşteri Adı": t_ad, "Telefon": t_tel, "Meslek": t_meslek,
                    "Aranılan İlan": t_ilan, "Tür": t_tur, "Oda": t_oda,
                    "Konum": t_konum, "Bütçe Aralığı": float(t_max),
                    "Tarih": datetime.now().strftime("%d-%m-%Y")
                }
                st.session_state.talepler.append(yeni_t)
                veri_kaydet(TALEPLER_FILE, st.session_state.talepler)
                st.success("Müşteri Talebi Kaydedildi!")
                st.rerun()

    with col_tt:
        st.subheader("📋 Bekleyen Müşteri Talepleri")
        if st.session_state.talepler:
            for i, t in enumerate(st.session_state.talepler):
                with st.expander(f"👤 {t.get('Müşteri Adı')} - {t.get('Aranılan İlan')}"):
                    st.write(f"📞 **Tel:** {t.get('Telefon')} | 💼 **Meslek:** {t.get('Meslek')}")
                    st.write(f"🏠 **Tür:** {t.get('Tür')} | 🛏️ **Oda:** {t.get('Oda')} | 📍 **Konum:** {t.get('Konum')}")
                    st.write(f"💰 **Bütçe:** {t.get('Bütçe Aralığı',0):,.0f} TL")
                    if st.button(f"🗑️ Bu Müşteriyi Sil", key=f"del_talep_{i}"):
                        st.session_state.talepler.pop(i)
                        veri_kaydet(TALEPLER_FILE, st.session_state.talepler)
                        st.rerun()
        else: st.info("Bekleyen müşteri talebi yok.")

# --- TAB 3: AKILLI EŞLEŞTİRME ---
with tab3:
    st.subheader("🤖 Akıllı Portföy-Talep Eşleştirme Motoru")
    if st.session_state.kayitlar and st.session_state.talepler:
        match_found = False
        for t in st.session_state.talepler:
            for p in st.session_state.kayitlar:
                p_val = tutar_temizle(p.get('Biçilen Değer', 0))
                t_val = tutar_temizle(t.get('Bütçe Aralığı', 0))
                
                if t.get('Tür') == p.get('Tür') and t.get('Oda') == p.get('Oda') and p_val <= t_val:
                    st.success(f"🌟 **MÜKEMMEL EŞLEŞME BULUNDU!**")
                    c_match1, c_match2 = st.columns(2)
                    with c_match1:
                        st.info(f"👤 **Arayan Müşteri:**\n\n**İsim:** {t.get('Müşteri Adı')}\n\n**Telefon:** {t.get('Telefon')}")
                    with c_match2:
                        st.warning(f"🏠 **Uygun Mülk:**\n\n**Sahibi:** {p.get('Mülk Sahibi')}\n\n**Konum:** {p.get('Konum')}\n\n**Fiyat:** {p_val:,.0f} TL")
                    st.divider()
                    match_found = True
        if not match_found: st.info("Şu an kriterleri birbiriyle eşleşen mülk ve müşteri bulunmuyor.")
    else: st.info("Eşleştirme yapabilmek için veri girişi gereklidir.")

# --- TAB 4: SÖZLEŞME & ANALİZ ---
with tab4:
    st.subheader("📜 Profesyonel Yer Gösterme Belgesi (Resmi Format)")
    if st.session_state.kayitlar:
        s_idx = st.selectbox("Belge Hazırlanacak Mülkü Seçin:", range(len(st.session_state.kayitlar)), 
                             format_func=lambda x: f"{st.session_state.kayitlar[x].get('Mülk Sahibi')} - {st.session_state.kayitlar[x].get('Konum')}")
        m_sel = st.session_state.kayitlar[s_idx]
        
        col_pdf1, col_pdf2 = st.columns(2)
        m_tc = col_pdf1.text_input("Müşteri TC / Vergi No:", key="tc_input_pdf")
        m_ada = col_pdf2.text_input("Ada / Parsel Bilgisi:", key="ada_input_pdf")

        def elite_pdf(d, tc, ada):
            pdf = FPDF()
            pdf.add_font("Roboto", style="", fname="Roboto_Condensed-Light.ttf")
            pdf.add_font("Roboto", style="B", fname="Roboto_Condensed-Bold.ttf")
            pdf.add_page()
            pdf.rect(5, 5, 200, 287)
            pdf.set_font("Roboto", "B", 18)
            pdf.cell(0, 15, "TAŞINMAZ GÖSTERME VE YETKİ BELGESİ", align='C', ln=True)
            pdf.set_font("Roboto", "", 10)
            pdf.cell(0, 5, "Bu belge 05.06.2018 tarihli Taşınmaz Ticareti Hakkında Yönetmelik gereğince düzenlenmiştir.", align='C', ln=True)
            pdf.ln(10)
            
            pdf.set_font("Roboto", "B", 12); pdf.cell(0, 8, "1. TARAFLAR VE TAŞINMAZ", ln=True)
            pdf.set_font("Roboto", "", 11)
            pdf.multi_cell(0, 8, f"DANIŞMAN OFİS: {st.session_state.user.upper()}\n"
                                 f"MÜLK SAHİBİ: {d.get('Mülk Sahibi').upper()}\n"
                                 f"TC / VERGİ NO: {tc}\n"
                                 f"TAŞINMAZ KONUMU: {d.get('Konum')}\n"
                                 f"ADA / PARSEL: {ada}\n"
                                 f"TAŞINMAZ BEDELİ: {tutar_temizle(d.get('Biçilen Değer', 0)):,.0f} TL")
            pdf.ln(5)
            
            pdf.set_font("Roboto", "B", 12); pdf.cell(0, 8, "2. HUKUKİ ŞARTLAR VE HİZMET BEDELİ", ln=True)
            pdf.set_font("Roboto", "", 11)
            hukuk = ("1- Müşteri, kendisine gösterilen taşınmazı satın alması/kiralaması durumunda satış bedelinin %2 + KDV oranında hizmet bedeli ödemeyi kabul eder.\n"
                     "2- CEZAİ ŞART: Müşteri, danışmanı devre dışı bırakarak taşınmazı doğrudan mal sahibinden satın alması durumunda, hizmet bedelinin iki katı tutarında cezai şart ödemeyi taahhüt eder.\n"
                     "3- İşbu belge imza tarihinden itibaren 1 (bir) yıl süreyle geçerlidir.")
            pdf.multi_cell(0, 7, hukuk)
            pdf.ln(35)
            pdf.cell(90, 10, "MÜŞTERİ İMZA", align='L')
            pdf.cell(0, 10, "DANIŞMAN İMZA", align='R')
            return pdf.output()

        if st.button("🚀 Elite Yer Gösterme Belgesi (PDF) Oluştur", use_container_width=True):
            pdf_out = elite_pdf(m_sel, m_tc, m_ada)
            st.download_button("📥 Belgeyi Şimdi İndir", data=bytes(pdf_out), file_name=f"Sozlesme_{m_sel.get('Mülk Sahibi')}.pdf")
    else:
        st.info("Sözleşme oluşturmak için önce bir Portföy kaydı yapmalısınız.")

# --- SIDEBAR ---
with st.sidebar:
    st.divider()
    if st.button("🚪 Güvenli Çıkış", use_container_width=True):
        st.session_state.user = None
        st.rerun()