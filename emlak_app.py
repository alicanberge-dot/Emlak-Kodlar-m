import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

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
def veri_yukle(dosya):
    if os.path.exists(dosya):
        with open(dosya, "r", encoding="utf-8") as f: return json.load(f)
    return []

def veri_kaydet(dosya, veri):
    with open(dosya, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

if 'user' not in st.session_state: st.session_state.user = "Admin" # Varsayılan Admin
DB_FILE = f"db_{st.session_state.user}.json"
TALEPLER_FILE = f"talepler_{st.session_state.user}.json"

if 'kayitlar' not in st.session_state: st.session_state.kayitlar = veri_yukle(DB_FILE)
if 'talepler' not in st.session_state: st.session_state.talepler = veri_yukle(TALEPLER_FILE)

# --- ANA PANEL ---
st.title(f"🏢 {st.session_state.user.upper()} - Profesyonel Yönetim Paneli")

# Finansal Özet
c_stat1, c_stat2, c_stat3, c_stat4 = st.columns(4)
toplam_portfoy_degeri = sum([tutar_temizle(p.get('Biçilen Değer', 0)) for p in st.session_state.kayitlar])
c_stat1.metric("Toplam Portföy Değeri", f"{toplam_portfoy_degeri:,.0f} TL")
c_stat2.metric("Potansiyel Komisyon (%2)", f"{(toplam_portfoy_degeri * 0.02):,.0f} TL")
c_stat3.metric("Aktif Portföy", len(st.session_state.kayitlar))
c_stat4.metric("Bekleyen Müşteri", len(st.session_state.talepler))

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Portföy Yönetimi", "🔍 Müşteri Talepleri", "🤖 Akıllı Eşleştirme %", "📊 Excel Aktarımı"])

TUR_SECENEKLERI = ["Daire", "Villa", "Dublex", "Triplex", "Arsa", "İşyeri"]
ODA_SECENEKLERI = ["1+1", "2+1", "3+1", "4+1", "5+1", "Dubleks", "Arsa/Diğer"]
ISLEM_SECENEKLERI = ["Satılık", "Kiralık"]

# --- TAB 1: PORTFÖY YÖNETİMİ ---
with tab1:
    col_f, col_t = st.columns([1, 2.5])
    with col_f:
        st.subheader("Yeni Portföy Kaydı")
        p_sahibi = st.text_input("Mülk Sahibi:")
        p_islem = st.radio("İşlem Türü:", ISLEM_SECENEKLERI, horizontal=True)
        p_tur = st.selectbox("Mülk Türü:", TUR_SECENEKLERI)
        p_oda = st.selectbox("Oda Sayısı:", ODA_SECENEKLERI)
        p_konum = st.text_input("Konum (İlçe/Semt):").strip().lower()
        p_tel = st.text_input("Telefon:", key="p_tel_in") # "Sahibi Telefon" -> "Telefon" yapıldı.
        p_bic = st.number_input("Biçilen Değer (TL):", value=0, step=50000)
        p_tek = st.number_input("Teklif Edilen (TL):", value=0, step=50000)
        p_not = st.text_area("Özel Notlar:", key="p_not_in")
        
        if st.button("Portföyü Kaydet", use_container_width=True):
            yeni = {
                "Mülk Sahibi": p_sahibi, "İşlem": p_islem, "Tür": p_tur, "Oda": p_oda,
                "Konum": p_konum, "Telefon": p_tel, "Biçilen Değer": float(p_bic), 
                "Teklif Edilen": float(p_tek), "Not": p_not, "Tarih": datetime.now().strftime("%d-%m-%Y")
            }
            st.session_state.kayitlar.append(yeni)
            veri_kaydet(DB_FILE, st.session_state.kayitlar); st.rerun()

    with col_t:
        st.subheader("📋 Aktif Portföy Listesi & Pazarlık")
        for i, p in enumerate(st.session_state.kayitlar):
            baslik = f"🏠 [{p.get('İşlem')}] {p.get('Tür')} - {p.get('Oda')} - {p.get('Konum', '').title()}"
            with st.expander(baslik):
                st.write(f"👤 **Sahibi:** {p.get('Mülk Sahibi')} | 📞 **Tel:** {p.get('Telefon')}")
                c_edit1, c_edit2 = st.columns(2)
                yeni_bic = c_edit1.number_input(f"Biçilen Değer", value=float(p.get('Biçilen Değer', 0)), key=f"ebic_{i}")
                yeni_tek = c_edit2.number_input(f"Teklif Edilen", value=float(p.get('Teklif Edilen', 0)), key=f"etek_{i}")
                
                if st.button(f"Fiyatları Güncelle", key=f"upd_{i}"):
                    st.session_state.kayitlar[i]['Biçilen Değer'] = yeni_bic
                    st.session_state.kayitlar[i]['Teklif Edilen'] = yeni_tek
                    veri_kaydet(DB_FILE, st.session_state.kayitlar); st.toast("Güncellendi!")
                
                if st.button("🗑️ Portföyü Sil", key=f"del_p_{i}"):
                    st.session_state.kayitlar.pop(i)
                    veri_kaydet(DB_FILE, st.session_state.kayitlar); st.rerun()

# --- TAB 2: MÜŞTERİ TALEPLERİ ---
with tab2:
    col_tf, col_tt = st.columns([1, 2.5])
    with col_tf:
        st.subheader("Yeni Müşteri Talebi")
        t_ad = st.text_input("Müşteri Ad Soyad:")
        t_tel = st.text_input("Telefon:", key="t_tel_in")
        t_mes = st.text_input("Meslek:", key="t_mes_in")
        t_islem = st.radio("Aranan İşlem:", ISLEM_SECENEKLERI, horizontal=True)
        t_tur = st.selectbox("İstenen Tür:", TUR_SECENEKLERI)
        t_oda = st.selectbox("İstediği Oda:", ODA_SECENEKLERI)
        t_konum = st.text_input("Aranılan Konum (İlçe/Semt):").strip().lower() # Konum girişi
        t_butce = st.number_input("Maksimum Bütçe (TL):", value=0, step=50000)
        t_not = st.text_area("Müşteri Notları:", key="t_not_in")
        
        if st.button("Talebi Kaydet", use_container_width=True):
            yeni_t = {
                "Müşteri Adı": t_ad, "Telefon": t_tel, "Meslek": t_mes, "İşlem": t_islem,
                "Tür": t_tur, "Oda": t_oda, "Konum": t_konum, "Bütçe Aralığı": float(t_butce),
                "Not": t_not, "Tarih": datetime.now().strftime("%d-%m-%Y")
            }
            st.session_state.talepler.append(yeni_t)
            veri_kaydet(TALEPLER_FILE, st.session_state.talepler); st.rerun()

    with col_tt:
        st.subheader("📋 Bekleyen Müşteri Talepleri")
        for i, t in enumerate(st.session_state.talepler):
            with st.expander(f"👤 {t.get('Müşteri Adı')} - {t.get('İşlem')} {t.get('Tür')}"):
                c_t1, c_t2 = st.columns(2)
                c_t1.write(f"📞 **Tel:** {t.get('Telefon')} | 💼 **Meslek:** {t.get('Meslek')}")
                c_t2.write(f"📍 **Konum:** {t.get('Konum', '').title()} | 💰 **Bütçe:** {t.get('Bütçe Aralığı',0):,.0f} TL")
                st.info(f"📝 **Notlar:** {t.get('Not','')}")
                if st.button(f"🗑️ Talebi Sil", key=f"del_t_{i}"):
                    st.session_state.talepler.pop(i)
                    veri_kaydet(TALEPLER_FILE, st.session_state.talepler); st.rerun()

# --- TAB 3: AKILLI EŞLEŞTİRME (KONUM HASSASİYETİ EKLENDİ) ---
with tab3:
    st.subheader("🤖 Hibrit Akıllı Eşleştirme (Konum Hassasiyetli)")
    found = False
    if st.session_state.kayitlar and st.session_state.talepler:
        for t in st.session_state.talepler:
            for p in st.session_state.kayitlar:
                # 1. KRİTİK: Satılık/Kiralık uyumu zorunlu
                if t.get('İşlem') != p.get('İşlem'): continue
                
                skor = 0
                match_tur = t.get('Tür') == p.get('Tür')
                match_oda = t.get('Oda') == p.get('Oda')
                match_konum = (t.get('Konum', '').strip().lower() == p.get('Konum', '').strip().lower())
                p_fiyat = tutar_temizle(p.get('Biçilen Değer', 0))
                t_butce = tutar_temizle(t.get('Bütçe Aralığı', 0))
                match_fiyat = p_fiyat <= t_butce
                
                # Puanlama Mantığı (Toplam 100)
                if match_tur: skor += 30
                if match_oda: skor += 20
                if match_konum: skor += 30 # Konum artık en güçlü puanlardan biri
                if match_fiyat: skor += 20
                
                if skor >= 50: # %50 ve üstü uyumları göster
                    found = True
                    st.success(f"💎 **UYUM ORANI: %{skor}**")
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c1.markdown(f"**İşlem:** :green[{p.get('İşlem')}]")
                    c2.markdown(f"**Tür:** :{'green' if match_tur else 'red'}[{p.get('Tür')}]")
                    c3.markdown(f"**Oda:** :{'green' if match_oda else 'red'}[{p.get('Oda')}]")
                    c4.markdown(f"**Konum:** :{'green' if match_konum else 'red'}[{p.get('Konum', '').title()}]")
                    c5.markdown(f"**Fiyat:** :{'green' if match_fiyat else 'red'}[{p_fiyat:,.0f} TL]")
                    
                    st.write(f"🤝 **Müşteri:** {t.get('Müşteri Adı')} ({t.get('Telefon')}) ↔️ **Portföy:** {p.get('Mülk Sahibi')} ({p.get('Konum', '').title()})")
                    st.divider()
        if not found: st.info("Şu an kriterlere uygun bir eşleşme bulunamadı.")
    else: st.info("Eşleştirme yapabilmek için veri girişi gereklidir.")

# --- TAB 4: EXCEL AKTARIMI ---
with tab4:
    if st.session_state.kayitlar:
        df_export = pd.DataFrame(st.session_state.kayitlar)
        st.download_button("📂 Tüm Portföyü Excel Olarak İndir", data=df_export.to_csv(index=False).encode('utf-8-sig'), file_name="Portfoy_Listesi.csv")
    else: st.warning("Aktarılacak veri bulunamadı.")