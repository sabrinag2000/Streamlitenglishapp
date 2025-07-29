import streamlit as st
import openai
from io import BytesIO

#  ——— Configuration ———
# Put your key under [general] in secrets.toml:
# OPENAI_API_KEY="sk-..."
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Aprenda Inglês com Áudio", layout="centered")
st.title("Aprenda Inglês com Áudio")

#  ——— Section 1: Traduzir PT → EN + TTS ———
st.header("1. Traduzir e Ouvir")
pt_text = st.text_area("Digite algo em português", height=100)

if st.button("🔊 Traduzir e Falar"):
    if not pt_text.strip():
        st.warning("Digite algo em português primeiro!")
    else:
        # Tradução via Chat Completions v1
        trans = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f'Traduza para inglês: "{pt_text.strip()}"'}]
        )  # :contentReference[oaicite:0]{index=0}
        en_text = trans.choices[0].message.content.strip()
        st.write("**Tradução:**", en_text)

        # TTS via Audio.speech.create → returns HttpxBinaryResponseContent
        tts = openai.audio.speech.create(
            model="tts-1",
            input=en_text,
            voice="nova"
        )  # :contentReference[oaicite:1]{index=1}

        # Pull out the raw MP3 bytes
        audio_bytes = tts.content  # HttpxBinaryResponseContent.content → bytes :contentReference[oaicite:2]{index=2}
        st.audio(audio_bytes, format="audio/mp3")


st.markdown("---")

#  ——— Section 2: Upload de áudio, transcrição + correção ———
st.header("2. Grave e Corrija (Upload de Áudio)")
uploaded = st.file_uploader(
    "Envie um arquivo de áudio (wav/mp3/m4a/ogg)",
    type=["wav", "mp3", "m4a", "ogg"]
)

if uploaded:
    audio_bytes = uploaded.read()
    st.audio(audio_bytes, format=f"audio/{uploaded.type.split('/')[-1]}")

    # Transcrição com Whisper
    with st.spinner("Transcrevendo áudio..."):
        transcription = openai.Audio.transcribe("whisper-1", BytesIO(audio_bytes))  # :contentReference[oaicite:3]{index=3}
        falado = transcription["text"].strip()
    st.write("**Você disse:**", falado)

    # Correção de pronúncia via Chat Completions
    with st.spinner("Corrigindo pronúncia..."):
        correction = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um professor de inglês. Corrija o texto abaixo e "
                        "responda sempre no formato: 'you meant to say... <frase corrigida>'"
                    )
                },
                {"role": "user", "content": falado}
            ]
        )  # :contentReference[oaicite:4]{index=4}
        corr_text = correction.choices[0].message.content.strip()
    st.write("**Correção:**", corr_text)

    # TTS da correção
    tts_corr = openai.audio.speech.create(
        model="tts-1",
        input=corr_text,
        voice="nova"
    )  # :contentReference[oaicite:5]{index=5}

    audio_corr_bytes = tts_corr.content
    st.audio(audio_corr_bytes, format="audio/mp3")


#  ——— Sidebar: Setup instructions ———
st.sidebar.header("Instruções de Instalação")

