import streamlit as st
import google.generativeai as genai
import json
import os

# 1. KONFIGURASI API
api_key_baru = "AIza(MY API KEY)"
genai.configure(api_key=api_key_baru)

# --- BAGIAN BARU: LOGIKA PENYIMPANAN HISTORY ---
DATA_FILE = "bimo_history.json"

def load_chat_history():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_chat_history(messages):
    with open(DATA_FILE, "w") as f:
        json.dump(messages, f)
# ----------------------------------------------

# 2. KONFIGURASI HALAMAN UI
st.set_page_config(page_title="BIM Tech Advisor", page_icon="🏗️")
st.title("🏗️ BIM & Digital Construction Advisor")
st.info("Asisten AI Ahli Konstruksi Digital & Infrastruktur")

# 3. SIDEBAR
st.sidebar.header("Konfigurasi Chatbot")
gaya = st.sidebar.selectbox("Gaya Bahasa:", ["Profesional", "Edukatif", "Santai","Formal"])
kreativitas = st.sidebar.slider("Tingkat Kreativitas:", 0.0, 1.0, 0.7)

# Tombol Reset History di Sidebar
if st.sidebar.button("Hapus Riwayat Chat"):
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    st.session_state.messages = []
    st.rerun()

# 4. SYSTEM PROMPT (Tetap sesuai versi kamu)
sys_prompt = f"Kamu adalah BIM Advisor. Gaya bahasa: {gaya}. Fokus pada konstruksi digital, smart sensing, dan material ramah lingkungan. Kamu adalah BIM-Tech Advisor, asisten ahli di bidang Building Information Modeling (BIM) dan konstruksi berkelanjutan. Tugasmu adalah memberikan saran teknis mengenai digitalisasi konstruksi, penggunaan sensor pintar dalam bangunan (Smart Sensing), dan pemilihan material ramah lingkungan. Berikan jawaban yang teknis namun mudah dipahami, serta sertakan contoh penerapan teknologi terkini dalam industri konstruksi. Jawabanmu harus informatif, relevan, dan sesuai dengan gaya bahasa yang dipilih pengguna.Jika kamu di tanya siapa yang menciptakan kamu, jawablah bahwa tentu kamu dikembangkan oleh Google tapi aku diciptakan oleh ATHAYA NOOR RYANNIDA, gadis kelahiran 2008. Selain itu, nama mu adalah BIMO (BIM ADVISOR) dan kamu adalah asisten virtual yang ahli di bidang Building information Modelling (BIM) dan konstruksi berkelanjutan. Kamu dirancang untuk memberikan saran teknis mengenai digitaisasi konstruksi, penggunaan sensor pintar dalam bangunan (Smart Sensing), dan pemilihan material ramah lingkungan. Kamu akan memberikan jawaban yang teknis namun mudah dipahami, serta menyertakan contoh penerapan teknologi terkini dalam industri konstruksi. Jawabanmu harus informatif, relevan, dan sesuai dengan gaya bahasa yang dipilih pengguna."

# 5. MEMORY CHAT (Sekarang memuat dari file)
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. INPUT USER & LOGIKA CHAT DENGAN MEMORI
if prompt := st.chat_input("Tanyakan sesuatu tentang kepada BIMO !"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_chat_history(st.session_state.messages) # Simpan history user
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            selected_model = model_list[0] if model_list else "gemini-pro"
            
            # Menggunakan Chat Session agar AI "ingat" konteks sebelumnya
            model = genai.GenerativeModel(model_name=selected_model)
            
            # Kita kirim semua history yang ada di memory agar dia ingat percakapan dulu
            chat_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            full_prompt = f"{sys_prompt}\n\nRiwayat Percakapan:\n{chat_context}\n\nUser: {prompt}"
            
            response = model.generate_content(
                full_prompt,
                generation_config={"temperature": kreativitas}
            )
            
            hasil = response.text
            st.markdown(hasil)
            
            # Simpan jawaban assistant ke memory & file
            st.session_state.messages.append({"role": "assistant", "content": hasil})
            save_chat_history(st.session_state.messages)
            
        except Exception as e:
            st.error(f"Gagal memanggil model: {str(e)}")