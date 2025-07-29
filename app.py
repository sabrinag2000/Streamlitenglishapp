import streamlit as st
import openai
from io import BytesIO

# Configure your OpenAI API key in secrets.toml under [general]
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Aprenda Inglês com Áudio", layout="centered")
st.title("Aprenda Inglês com Áudio")

# Section 1: Translate Portuguese → English and TTS playback
st.header("1. Traduzir e Ouvir")
pt_text = st.text_area("Digite algo em português", height=100)
if st.button("🔊 Traduzir e Falar"):
    if not pt_text.strip():
        st.warning("Digite algo em português primeiro!")
    else:
        # 1.1 Tradução via GPT-4o
        trans = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": f'Traduza para inglês: "{pt_text.strip()}"'}
            ]
        )
        en_text = trans.choices[0].message.content.strip()
        st.write("**Tradução:**", en_text)

        # 1.2 TTS via OpenAI Audio
        tts = openai.audio.speech.create(
            model="tts-1",
            input=en_text,
            voice="nova"
        )
        # extract URL and let Streamlit fetch/play it
        audio_url = tts["url"]
        st.audio(audio_url)

st.markdown("---")

# Section 2: Upload your English audio, transcribe & correct
st.header("2. Grave e Corrija (Upload de Áudio)")
uploaded = st.file_uploader(
    "Envie um arquivo de áudio (wav/mp3/m4a/ogg)",
    type=["wav", "mp3", "m4a", "ogg"]
)
if uploaded:
    audio_bytes = uploaded.read()
    # Playback original
    st.audio(audio_bytes, format=f"audio/{uploaded.type.split('/')[-1]}")

    # 2.1 Transcrição com Whisper
    with st.spinner("Transcrevendo áudio..."):
        audio_file = BytesIO(audio_bytes)
        transcription = openai.Audio.transcribe("whisper-1", audio_file)
        falado = transcription["text"].strip()
    st.write("**Você disse:**", falado)

    # 2.2 Correção de pronúncia com GPT-4o
    with st.spinner("Corrigindo pronúncia..."):
        correction = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um professor de inglês. "
                        "Corrija o texto abaixo e responda sempre no formato: "
                        "'you meant to say... <frase corrigida>'"
                    )
                },
                {"role": "user", "content": falado}
            ]
        )
        corr_text = correction.choices[0].message.content.strip()
    st.write("**Correção:**", corr_text)

    # 2.3 TTS da frase corrigida
    tts_corr = openai.audio.speech.create(
        model="tts-1",
        input=corr_text,
        voice="nova"
    )
    audio_corr_url = tts_corr["url"]
    st.audio(audio_corr_url)

# Sidebar: Installation & run instructions
st.sidebar.header("Instruções de Instalação")

