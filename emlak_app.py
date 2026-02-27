import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from fpdf import FPDF

# Sayfa Ayarları
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
        p_ad = st.text_input("Mülk Sahibi/Başlık:")
        p_tur = st.selectbox("Tür:", ["Daire", "Arsa", "Ticari"], key="ptur")
        p_oda = st.selectbox("Oda Sayısı:", ["1+1", "2+1", "3+1", "4+1", "Arsa/Diğer"])
        p_tutar = st.number_input("Satış Bedeli (TL):", value=2000000)
        p_konum = st.text_input("Konum (İlçe/Semt):")
        if st.button("Portföyü Kaydet"):
            yeni = {"Mülk": p_ad, "Tür": p_tur, "Oda": p_oda, "Tutar": p_tutar, "Konum": p_konum, "Tarih": datetime.now().strftime("%d-%m-%Y")}
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
        t_ad = st.text_input("Arayan Müşteri:")
        t_tur = st.selectbox("Aradığı Tür:", ["Daire", "Arsa", "Ticari"], key="ttur")
        t_oda = st.selectbox("İstediği Oda:", ["1+1", "2+1", "3+1", "4+1", "Arsa/Diğer"], key="toda")
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

# --- TAB 3: AKILLI EŞLEŞTİRME (AI ENGINE) ---
with tab3:
    st.subheader("🤖 Algoritmik Portföy-Talep Eşleşmesi")
    if not st.session_state.kayitlar or not st.session_state.talepler:
        st.info("Eşleştirme yapabilmek için hem 'Portföy' hem de 'Talep' kaydı olmalıdır.")
    else:
        bulunan_eslesme = False
        for talep in st.session_state.talepler:
            for portfoy in st.session_state.kayitlar:
                # Eşleşme Mantığı: Tür aynı, Oda aynı ve Fiyat bütçeye uygunsa
                if talep['Tür'] == portfoy['Tür'] and talep['Oda'] == portfoy['Oda'] and portfoy['Tutar'] <= talep['Butce']:
                    st.success(f"🌟 **EŞLEŞME BULDUM!**")
                    st.write(f"👉 **Müşteri:** {talep['Müşteri']} | **Uygun Mülk:** {portfoy['Mülk']} ({portfoy['Konum']})")
                    st.write(f"💰 **Bütçe:** {talep['Butce']:,} TL | **Mülk Fiyatı:** {portfoy['Tutar']:,} TL")
                    st.divider()
                    bulunan_eslesme = True
        if not bulunan_eslesme:
            st.warning("Şu an kriterleri tam uyuşan bir eşleşme bulunamadı.")

# --- TAB 4: SÖZLEŞME & ANALİZ ---
with tab4:
    st.subheader("📜 Elite Sözleşme & 🧮 Amortisman")
    # (Önceki profesyonel PDF ve analiz kodlarını buraya dahil ediyoruz)
    st.write("Buradan daha önce kaydettiğiniz mülkler için Elite PDF üretebilir ve ROI analizi yapabilirsiniz.")
    # ... (PDF kodları buraya gelecek - Alan tasarrufu için kısa kesilmiştir)

if st.sidebar.button("🚪 Güvenli Çıkış"):
    st.session_state.user = None
    st.rerun()