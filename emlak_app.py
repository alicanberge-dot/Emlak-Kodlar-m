import streamlit as st
import pandas as pd
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="Emlak Pro Asistan", page_icon="🏢", layout="wide")

# Hafıza
if 'kayitlar' not in st.session_state:
    st.session_state.kayitlar = []

st.title("🏢 Emlak Yönetim ve Sözleşme Paneli")

# Sol Menü
with st.sidebar:
    st.header("📋 İşlem Formu")
    isim = st.text_input("Müşteri Ad Soyad:")
    islem_tipi = st.selectbox("İşlem Türü:", ["Konut Satış", "Ticari Satış", "Kiralama"])
    tutar = st.number_input("İşlem Bedeli (TL):", min_value=0, value=2000000)
    st.divider()
    hesapla_ve_ekle = st.button("Sisteme Kaydet ve Hesapla")

# Hesaplama Mantığı
if hesapla_ve_ekle:
    # Standart %2 + %20 KDV
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
    st.success(f"✅ {isim} sisteme başarıyla kaydedildi.")

# Ana Ekran Sekmeleri
tab1, tab2 = st.tabs(["📊 İşlem Takibi", "📜 Sözleşme Hazırlama"])

with tab1:
    st.subheader("Günlük İşlem Listesi")
    if st.session_state.kayitlar:
        df = pd.DataFrame(st.session_state.kayitlar)
        st.dataframe(df, use_container_width=True)
        
        # Excel Dostu İndirme
        csv = df.to_csv(index=False, sep=';').encode('utf-8-sig')
        st.download_button("Excel Listesini İndir", data=csv, file_name='gunluk_emlak_ozeti.csv', mime='text/csv')
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
        st.info("💡 Bu metni kopyalayıp dijital imza uygulamasına veya Word dosyasına yapıştırabilirsiniz.")
    else:
        st.warning("⚠️ Sözleşme oluşturmak için lütfen sol taraftan müşteri adı girin.")