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

# --- FINANSAL OZET PANELI ---
st.title(f"🏢 {st.session_state.user.upper()} - Profesyonel Yönetim Paneli")

c_stat1, c_stat2, c_stat3, c_stat4 = st.columns(4)
toplam_portfoy_degeri = sum([tutar_temizle(p.get('Biçilen Değer', 0)) for p in st.session_state.kayitlar])
beklenen_komisyon = toplam_portfoy_degeri * 0.02
c_stat1.metric("Toplam Portföy Değeri", f"{toplam_portfoy_degeri:,.0f} TL")
c_stat2.metric("Potansiyel Komisyon (%2)", f"{beklenen_komisyon:,.0f} TL")
c_stat3.metric("Aktif Portföy", len(st.session_state.kayitlar))
c_stat4.metric("Bekleyen Müşteri", len(st.session_state.talepler))

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Portföy Yönetimi", "🔍 Müşteri Talepleri", "🤖 Akıllı Eşleştirme %", "📜 Sözleşme & Excel"])

TUR_SECENEKLERI = ["Daire", "Villa", "Dublex", "Triplex", "Arsa", "İşyeri"]
ODA_SECENEKLERI = ["1+1", "2+1", "3+1", "4+1", "5+1", "Dubleks", "Arsa/Diğer"]

# --- TAB 1: PORTFÖY YÖNETİMİ ---
with tab1:
    col_f, col_t = st.columns([1, 2.5])
    with col_f:
        st.subheader("Yeni Portföy Kaydı")
        p_sahibi = st.text_input("Mülk Sahibi:")
        p_tel = st.text_input("Telefon:", key="p_tel_in")
        p_tur = st.selectbox("Tür:", TUR_SECENEKLERI, key="p_tur_in")
        p_oda = st.selectbox("Oda:", ODA_SECENEKLERI, key="p_oda_in")
        p_konum = st.text_input("Konum:", key="p_kon_in")
        p_bic = st.number_input("Biçilen Değer (TL):", value=0, step=50000)
        p_tek = st.number_input("Teklif Edilen (TL):", value=0, step=50000)
        p_link = st.text_input("İlan Linki / Fotoğraf Yolu:")
        p_not = st.text_area("Özel Notlar:")
        
        if st.button("Kaydet", use_container_width=True):
            yeni = {
                "Mülk Sahibi": p_sahibi, "Telefon": p_tel, "Tür": p_tur, "Oda": p_oda,
                "Konum": p_konum, "Biçilen Değer": float(p_bic), "Teklif Edilen": float(p_tek),
                "Link": p_link, "Not": p_not, "Tarih": datetime.now().strftime("%d-%m-%Y")
            }
            st.session_state.kayitlar.append(yeni)
            veri_kaydet(DB_FILE, st.session_state.kayitlar)
            st.rerun()

    with col_t:
        st.subheader("📋 Aktif Portföy Listesi & Pazarlık Güncelleme")
        for i, p in enumerate(st.session_state.kayitlar):
            with st.expander(f"📍 {p.get('Mülk Sahibi')} - {p.get('Konum')} ({p.get('Tür')})"):
                c_edit1, c_edit2 = st.columns(2)
                # DEĞER GÜNCELLEME ALANLARI
                yeni_bic = c_edit1.number_input(f"Biçilen Değer", value=float(p.get('Biçilen Değer', 0)), key=f"ebic_{i}")
                yeni_tek = c_edit2.number_input(f"Teklif Edilen", value=float(p.get('Teklif Edilen', 0)), key=f"etek_{i}")
                
                if st.button(f"Fiyatları Güncelle", key=f"upd_{i}"):
                    st.session_state.kayitlar[i]['Biçilen Değer'] = yeni_bic
                    st.session_state.kayitlar[i]['Teklif Edilen'] = yeni_tek
                    veri_kaydet(DB_FILE, st.session_state.kayitlar)
                    st.toast("Fiyatlar güncellendi!", icon="✅")
                
                st.write(f"📞 {p.get('Telefon')} | 🛏️ {p.get('Oda')} | 📝 {p.get('Not','')}")
                if p.get('Link'): st.info(f"🔗 [İlanı Görüntüle]({p.get('Link')})")
                
                if st.button("🗑️ Sil", key=f"del_p_{i}"):
                    st.session_state.kayitlar.pop(i)
                    veri_kaydet(DB_FILE, st.session_state.kayitlar); st.rerun()

# --- TAB 2: MÜŞTERİ TALEPLERİ ---
with tab2:
    col_tf, col_tt = st.columns([1, 2.5])
    with col_tf:
        st.subheader("Yeni Müşteri Talebi")
        t_ad = st.text_input("Müşteri Ad Soyad:")
        t_tel = st.text_input("Telefon:", key="t_tel_in")
        t_mes = st.text_input("Meslek:")
        t_tur = st.selectbox("Tür:", TUR_SECENEKLERI, key="t_tur_in")
        t_oda = st.selectbox("İstediği Oda:", ODA_SECENEKLERI, key="t_oda_in")
        t_butce = st.number_input("Maksimum Bütçe (TL):", value=0, step=50000)
        t_hatirlatici = st.date_input("Geri Dönüş Tarihi")
        
        if st.button("Talebi Kaydet", use_container_width=True):
            yeni_t = {
                "Müşteri Adı": t_ad, "Telefon": t_tel, "Meslek": t_mes, "Tür": t_tur,
                "Oda": t_oda, "Bütçe Aralığı": float(t_butce), "Hatirlatici": str(t_hatirlatici),
                "Tarih": datetime.now().strftime("%d-%m-%Y")
            }
            st.session_state.talepler.append(yeni_t)
            veri_kaydet(TALEPLER_FILE, st.session_state.talepler)
            st.rerun()

    with col_tt:
        st.subheader("📋 Bekleyen Müşteri Talepleri")
        for i, t in enumerate(st.session_state.talepler):
            with st.expander(f"👤 {t.get('Müşteri Adı')} - {t.get('Tür')}"):
                st.write(f"📞 {t.get('Telefon')} | 💼 {t.get('Meslek')}")
                st.write(f"💰 Bütçe: {t.get('Bütçe Aralığı',0):,.0f} TL | 📅 Hatırlatıcı: {t.get('Hatirlatici')}")
                if st.button(f"🗑️ Talebi Sil", key=f"del_t_{i}"):
                    st.session_state.talepler.pop(i)
                    veri_kaydet(TALEPLER_FILE, st.session_state.talepler); st.rerun()

# --- TAB 3: AKILLI EŞLEŞTİRME % ---
with tab3:
    st.subheader("🤖 Hibrit Akıllı Eşleştirme (Yüzdelik Analiz)")
    if st.session_state.kayitlar and st.session_state.talepler:
        for t in st.session_state.talepler:
            for p in st.session_state.kayitlar:
                skor = 0
                if t.get('Tür') == p.get('Tür'): skor += 50
                if t.get('Oda') == p.get('Oda'): skor += 30
                p_fiyat = tutar_temizle(p.get('Biçilen Değer', 0))
                t_butce = tutar_temizle(t.get('Bütçe Aralığı', 0))
                if p_fiyat <= t_butce: skor += 20
                elif p_fiyat <= t_butce * 1.15: skor += 10 # %15 bütçe esnemesi
                
                if skor >= 60:
                    st.success(f"💎 **UYUM ORANI: %{skor}**")
                    st.write(f"🤝 **{t.get('Müşteri Adı')}** için uygun: **{p.get('Mülk Sahibi')} / {p.get('Konum')}**")
                    st.divider()
    else: st.info("Veri girişi bekleniyor.")

# --- TAB 4: SÖZLEŞME & RAPORLAMA ---
with tab4:
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.subheader("📜 Resmi Sözleşme Üret")
        if st.session_state.kayitlar:
            s_idx = st.selectbox("Mülk Seç:", range(len(st.session_state.kayitlar)), format_func=lambda x: st.session_state.kayitlar[x].get('Mülk Sahibi'))
            tc = st.text_input("Müşteri TC:")
            if st.button("PDF Oluştur"):
                # (PDF fonksiyonu yukarıdaki sürümlerle aynı, alan daralmaması için kısa geçilmiştir)
                st.write("PDF Hazırlanıyor...")
    with col_r2:
        st.subheader("📈 Veri Aktarımı")
        if st.session_state.kayitlar:
            df_export = pd.DataFrame(st.session_state.kayitlar)
            csv = df_export.to_csv(index=False).encode('utf-8-sig')
            st.download_button("Excel/CSV Olarak İndir", data=csv, file_name="Portfoy_Listesi.csv", mime="text/csv")

if st.sidebar.button("🚪 Güvenli Çıkış"):
    st.session_state.user = None; st.rerun()