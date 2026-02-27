import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from fpdf import FPDF

# Sayfa Ayarları
st.set_page_config(page_title="Emlak Pro Asistan", page_icon="🏢", layout="wide")

# --- KULLANICI & ŞİFRE YÖNETİMİ ---
USERS_FILE = "kullanicilar.json"

def kullanicilari_yukle():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def kullanici_kaydet(username, password):
    kullanicilar = kullanicilari_yukle()
    kullanicilar[username] = password
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(kullanicilar, f, ensure_ascii=False, indent=4)

# Uygulama başladığında kullanıcıyı kontrol et
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🔐 Emlak Paneli Girişi")
    
    tab_giris, tab_kayit = st.tabs(["Giriş Yap", "Yeni Hesap Oluştur"])
    
    with tab_giris:
        k_adi = st.text_input("Kullanıcı Adı:", key="login_user").lower().strip()
        sifre = st.text_input("Şifre:", type="password", key="login_pass")
        
        if st.button("Sisteme Gir"):
            mevcut_kullanicilar = kullanicilari_yukle()
            if k_adi in mevcut_kullanicilar and mevcut_kullanicilar[k_adi] == sifre:
                st.session_state.user = k_adi
                st.rerun()
            else:
                st.error("❌ Kullanıcı adı veya şifre hatalı!")

    with tab_kayit:
        yeni_k_adi = st.text_input("Yeni Kullanıcı Adı:", key="reg_user").lower().strip()
        yeni_sifre = st.text_input("Yeni Şifre Belirleyin:", type="password", key="reg_pass")
        
        if st.button("Kayıt Ol ve Kullanıcı Oluştur"):
            if yeni_k_adi and yeni_sifre:
                mevcutlar = kullanicilari_yukle()
                if yeni_k_adi in mevcutlar:
                    st.warning("⚠️ Bu kullanıcı adı zaten alınmış!")
                else:
                    kullanici_kaydet(yeni_k_adi, yeni_sifre)
                    st.success("✅ Hesabınız oluşturuldu! Şimdi 'Giriş Yap' sekmesinden girebilirsiniz.")
            else:
                st.warning("Lütfen tüm alanları doldurun.")
    st.stop()

# Giriş yapıldıktan sonraki veritabanı dosyası
DB_FILE = f"db_{st.session_state.user}.json"
# ... (Kodun geri kalanı - verileri_yukle, verileri_kaydet vb. aynı kalacak)

def verileri_yukle():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def verileri_kaydet(veriler):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(veriler, f, ensure_ascii=False, indent=4)

if 'kayitlar' not in st.session_state:
    st.session_state.kayitlar = verileri_yukle()

# --- ANA PANEL ---
st.title(f"🏢 Emlak Yönetim Paneli - Hoş geldin, {st.session_state.user.capitalize()}")

with st.sidebar:
    st.header("📋 İşlem Formu")
    isim = st.text_input("Müşteri Ad Soyad:")
    islem_tipi = st.selectbox("İşlem Türü:", ["Konut Satışı", "Ticari Satış", "Kiralama"])
    tutar = st.number_input("İşlem Bedeli (TL):", min_value=0, value=2000000)
    st.divider()
    hesapla_ve_ekle = st.button("Sisteme Kaydet ve Hesapla")
    
    if st.button("🚪 Çıkış Yap"):
        st.session_state.user = None
        st.session_state.kayitlar = []
        st.rerun()

if hesapla_ve_ekle and isim:
    hizmet_bedeli = tutar * 0.02
    kdv = hizmet_bedeli * 0.20
    toplam = hizmet_bedeli + kdv
    tarih = datetime.now().strftime("%d-%m-%Y %H:%M")

    yeni_kayit = {
        "Tarih": tarih, "Müşteri": isim, "İşlem": islem_tipi,
        "Tutar": f"{tutar:,.2f} TL", "Hizmet Bedeli": f"{hizmet_bedeli:,.2f} TL", "KDV Dahil": f"{toplam:,.2f} TL"
    }
    st.session_state.kayitlar.append(yeni_kayit)
    verileri_kaydet(st.session_state.kayitlar)
    st.success(f"✅ {isim} kaydedildi.")

tab1, tab2 = st.tabs(["📊 İşlem Takibi", "📜 Sözleşme Hazırlama"])
with tab1:
    if st.session_state.kayitlar:
        df = pd.DataFrame(st.session_state.kayitlar)
        st.dataframe(df, use_container_width=True)
        
        # --- SİLME BÖLÜMÜ ---
        st.divider()
        st.subheader("🗑️ Kayıt Yönetimi")
        
        # Silinecek kaydı seçmek için bir liste oluşturuyoruz
        silinecek_index = st.selectbox(
            "Silmek istediğiniz kaydı seçin (Sıra No):", 
            range(len(st.session_state.kayitlar)),
            format_func=lambda x: f"{x}: {st.session_state.kayitlar[x]['Müşteri']} - {st.session_state.kayitlar[x]['Tarih']}"
        )
        
        if st.button("Seçili Kaydı Kalıcı Olarak Sil"):
            # Listeden çıkar
            silinen_isim = st.session_state.kayitlar[silinecek_index]['Müşteri']
            st.session_state.kayitlar.pop(silinecek_index)
            
            # Güncel halini kullanıcının kendi dosyasına (db_user.json) kaydet
            verileri_kaydet(st.session_state.kayitlar)
            
            st.success(f"❌ {silinen_isim} kişisine ait kayıt başarıyla silindi.")
            st.rerun() # Sayfayı yenileyerek tabloyu güncelle
    else:
        st.info("Henüz bir kaydınız bulunmuyor.")


with tab2:
    if isim:
        tarih_str = datetime.now().strftime("%d/%m/%Y")
        
        def pdf_olustur():
            pdf = FPDF()
            # Senin sistemindeki font isimleriyle eşleştirdik:
            pdf.add_font("Roboto", style="", fname="Roboto_Condensed-Light.ttf")
            pdf.add_font("Roboto", style="B", fname="Roboto_Condensed-Bold.ttf")
            pdf.add_page()
            
            pdf.set_font("Roboto", "B", 16)
            pdf.cell(0, 10, "TAŞINMAZ GÖSTERME VE YETKİ BELGESİ", align='C', new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)
            
            pdf.set_font("Roboto", "", 12)
            pdf.cell(0, 10, f"TARİH: {tarih_str}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"MÜŞTERİ: {isim.upper()}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"DANIŞMAN: {st.session_state.user.upper()}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)
            
            metin = "Bu belge taşınmaz ticareti yönetmeliği uyarınca düzenlenmiştir..."
            pdf.multi_cell(0, 10, metin)
            return pdf.output()

        try:
            pdf_out = pdf_olustur()
            st.download_button("📄 PDF İndir", data=bytes(pdf_out), file_name=f"sozlesme_{isim}.pdf")
        except Exception as e:
            st.error(f"Hata: {e}")