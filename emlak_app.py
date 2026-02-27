import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Sayfa Ayarları
st.set_page_config(page_title="Emlak Pro Asistan", page_icon="🏢", layout="wide")

# VERİTABANI DOSYASI AYARI
DB_FILE = "emlak_veritabani.json"

# Verileri Dosyadan Yükleme Fonksiyonu
def verileri_yukle():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Verileri Dosyaya Kaydetme Fonksiyonu
def verileri_kaydet(veriler):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(veriler, f, ensure_ascii=False, indent=4)

# Uygulama Hafızasını Başlat
if 'kayitlar' not in st.session_state:
    st.session_state.kayitlar = verileri_yukle()

st.title("🏢 Emlak Yönetim ve Sözleşme Paneli")

# Sol Menü
with st.sidebar:
    st.header("📋 İşlem Formu")
    isim = st.text_input("Müşteri Ad Soyad:")
    islem_tipi = st.selectbox("İşlem Türü:", ["Konut Satış", "Ticari Satış", "Kiralama"])
    tutar = st.number_input("İşlem Bedeli (TL):", min_value=0, value=2000000)
    st.divider()
    hesapla_ve_ekle = st.button("Sisteme Kaydet ve Hesapla")
    
    # Veritabanını Temizleme Butonu (Dikkatli Kullanım İçin)
    if st.button("🔴 Tüm Listeyi Sıfırla"):
        st.session_state.kayitlar = []
        verileri_kaydet([])
        st.rerun()

# Hesaplama Mantığı
if hesapla_ve_ekle and isim:
    hizmet_bedeli = tutar * 0.02
    kdv = hizmet_bedeli * 0.20
    toplam = hizmet_bedeli + kdv
    tarih = datetime.now().strftime("%d-%m-%Y %H:%M")

    yeni_kayit = {
        "Tarih": tarih,
        "Müşteri": isim,
        "İşlem": islem_tipi,
        "Tutar": f"{tutar:,.2f} TL",
        "Hizmet Bedeli": f"{hizmet_bedeli:,.2f} TL",
        "KDV Dahil": f"{toplam:,.2f} TL"
    }
    st.session_state.kayitlar.append(yeni_kayit)
    verileri_kaydet(st.session_state.kayitlar) # DOSYAYA YAZ
    st.success(f"✅ {isim} kalıcı olarak kaydedildi.")

# Ana Ekran Sekmeleri
tab1, tab2 = st.tabs(["📊 İşlem Takibi", "📜 Sözleşme Hazırlama"])

with tab1:
    st.subheader("Günlük İşlem Listesi")
    if st.session_state.kayitlar:
        df = pd.DataFrame(st.session_state.kayitlar)
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False, sep=';').encode('utf-8-sig')
        st.download_button("Excel Listesini İndir", data=csv, file_name='emlak_kayitlari.csv', mime='text/csv')
    else:
        st.info("Henüz bir işlem kaydı bulunmuyor.")

with tab2:
    st.subheader("Otomatik Yetki Belgesi Taslağı")
    if isim:
        sozlesme_metni = f"""
        TAŞINMAZ GÖSTERME VE YETKİ BELGESİ
        
        TARİH: {datetime.now().strftime("%d/%m/%Y")}
        MÜŞTERİ: {isim.upper()}
        İŞLEM TÜRÜ: {islem_tipi}
        TAŞINMAZ BEDELİ: {tutar:,.2f} TL
        
        Yukarıda bilgileri yer alan taşınmazın gösterilmesi ve aracılık hizmetleri karşılığında, 
        Taşınmaz Ticareti Hakkında Yönetmelik gereğince; %2 + KDV oranında hizmet bedeli 
        ödenmesini taraflar kabul ve taahhüt eder.
        
        MÜŞTERİ İMZA:                        EMLAK DANIŞMANI İMZA:
        ____________________                 ____________________
        """
        st.text_area("Kopyalamaya Hazır Metin:", sozlesme_metni, height=350)
    else:
        st.warning("⚠️ Sözleşme oluşturmak için lütfen sol taraftan müşteri adı girin.")