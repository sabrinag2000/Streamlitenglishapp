import streamlit as st
import openai
from io import BytesIO
from streamlit_audio_recorder import audio_recorder

# Set your OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Aprenda Inglês com Áudio", layout="centered")

st.title("Aprenda Inglês com Áudio")

# Section 1: Translate Portuguese to English and play TTS
st.header("1. Traduzir e Ouvir")
pt_text = st.text_area("Digite algo em português", height=100)
if st.button("🔊 Traduzir e Falar"):
    if pt_text.strip() == "":
        st.warning("Digite algo em português primeiro!")
    else:
        # Translation via GPT
        translation_resp = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f'Traduza para inglês: "{pt_text.strip()}"'}]
        )
        en_text = translation_resp.choices[0].message.content.strip()
        st.write("**Tradução:**", en_text)

        # TTS via OpenAI Audio
        tts_resp = openai.Audio.speech.create(
            model="tts-1",
            input=en_text,
            voice="nova"
        )
        st.audio(tts_resp, format="audio/mp3")

st.markdown("---")

# Section 2: Record English, transcribe, correct pronunciation, and play correction TTS
st.header("2. Grave e Corrija")
st.write("Clique no botão abaixo e fale em inglês. Depois, aguarde a transcrição e correção.")

audio_bytes = audio_recorder()
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")

    # Transcription via Whisper
    with st.spinner("Transcrevendo áudio..."):
        audio_file = BytesIO(audio_bytes)
        transcription_resp = openai.Audio.transcribe("whisper-1", audio_file)
        falado = transcription_resp["text"].strip()
    st.write("**Você disse:**", falado)

    # Pronunciation correction via GPT
    with st.spinner("Corrigindo pronúncia..."):
        correction_resp = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": (
                    "Você é um professor de inglês. Corrija o texto abaixo "
                    "e responda sempre no formato: 'you meant to say... <frase corrigida>'"
                )},
                {"role": "user", "content": falado}
            ]
        )
        corr_text = correction_resp.choices[0].message.content.strip()
    st.write("**Correção:**", corr_text)

    # TTS for corrected phrase
    tts_corr_resp = openai.Audio.speech.create(
        model="tts-1",
        input=corr_text,
        voice="nova"
    )
    st.audio(tts_corr_resp, format="audio/mp3")


