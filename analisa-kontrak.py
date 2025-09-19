import streamlit as st
import openai
from PyPDF2 import PdfReader
import io
import os
from dotenv import load_dotenv

# Muat variabel lingkungan dari file .env (opsional)
load_dotenv()

st.set_page_config(page_title="Penganalisis Kontrak PDF")
st.title("Penganalisis Kontrak PDF dengan OpenAI")

# Sidebar untuk API Key dan instruksi
with st.sidebar:
    st.header("Konfigurasi")
    openai_api_key = st.text_input("Masukkan OpenAI API Key", type="password")
    st.write("Dapatkan API Key Anda dari [OpenAI Platform](https://platform.openai.com/account/api-keys)")
    
    st.markdown("---")
    st.header("Cara Penggunaan")
    st.write("1. Masukkan OpenAI API Key Anda di atas.")
    st.write("2. Unggah dokumen kontrak PDF Anda.")
    st.write("3. Masukkan pertanyaan atau instruksi untuk analisis.")
    st.write("4. Klik 'Analisis Kontrak' untuk mendapatkan hasilnya.")

# Fungsi untuk mengekstrak teks dari PDF
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or "" # Handle potential None if page is empty
    return text

# Fungsi untuk mendapatkan analisis dari OpenAI
def get_contract_analysis(api_key, contract_text, query):
    if not api_key:
        st.error("Silakan masukkan OpenAI API Key Anda.")
        return None

    openai.api_key = api_key
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo", # Anda bisa mengganti dengan model yang lebih baru jika tersedia dan sesuai
            messages=[
                {"role": "system", "content": "Anda adalah asisten AI yang ahli dalam menganalisis dokumen hukum dan kontrak. Berikan analisis yang akurat, ringkas, dan relevan."},
                {"role": "user", "content": f"Berikut adalah teks dari dokumen kontrak:\n\n---\n{contract_text}\n---\n\nBerdasarkan dokumen kontrak di atas, {query}"}
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except openai.APIError as e:
        st.error(f"Terjadi kesalahan API OpenAI: {e}")
        return None
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        return None

# Bagian utama aplikasi
uploaded_file = st.file_uploader("Unggah Dokumen Kontrak PDF Anda", type="pdf")

if uploaded_file:
    st.success("Dokumen PDF berhasil diunggah!")
    
    # Ekstrak teks dari PDF
    contract_text = extract_text_from_pdf(uploaded_file)
    # st.subheader("Pratinjau Teks Kontrak:")
    # st.text_area("Teks yang diekstrak", contract_text[:1000] + "..." if len(contract_text) > 1000 else contract_text, height=200, disabled=True)

    st.markdown("---")
    st.subheader("Ajukan Pertanyaan atau Instruksi Analisis")
    user_query = st.text_area(
        "Misalnya: 'Apa saja kewajiban pihak pertama?', 'Ringkas poin-poin utama kontrak ini.', 'Adakah klausul tentang penghentian kontrak?'",
        height=150
    )

    if st.button("Analisis Kontrak"):
        if not openai_api_key:
            st.warning("Mohon masukkan OpenAI API Key Anda di sidebar.")
        elif not user_query:
            st.warning("Mohon masukkan pertanyaan atau instruksi analisis.")
        else:
            with st.spinner("Menganalisis dokumen..."):
                analysis_result = get_contract_analysis(openai_api_key, contract_text, user_query)
                if analysis_result:
                    st.success("Analisis Selesai!")
                    st.subheader("Hasil Analisis:")
                    st.write(analysis_result)
