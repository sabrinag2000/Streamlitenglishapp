import streamlit as st
import streamlit.components.v1 as components

# Configure your OpenAI key in secrets.toml under [general]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Aprenda Inglês com Áudio", layout="centered")
st.title("Aprenda Inglês com Áudio")

html_code = f"""
<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <title>Aprenda Inglês com Áudio</title>
  <style>
    body {{
      max-width: 700px;
      margin: auto;
      padding: 1rem;
      font-family: sans-serif;
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }}
    textarea, button {{
      font-size: 1rem;
    }}
    textarea {{
      width: 100%;
      height: 80px;
      padding: 8px;
      box-sizing: border-box;
      resize: vertical;
    }}
    section {{
      border: 1px solid #ccc;
      border-radius: 8px;
      padding: 1rem;
    }}
    section h2 {{
      margin-top: 0;
    }}
    p {{
      background: #f9f9f9;
      padding: 8px;
      border-radius: 4px;
      min-height: 1.5em;
    }}
  </style>
</head>
<body>
  <h1>Aprenda Inglês com Áudio</h1>

  <!-- 1. Tradutor PT → EN + TTS -->
  <section>
    <h2>1. Traduzir e Ouvir</h2>
    <textarea id="inputPT" placeholder="Digite algo em português"></textarea>
    <button onclick="traduzirEReproduzir()">🔊 Traduzir e Falar</button>
    <p id="respostaPT"></p>
    <audio id="audioPT" controls style="display:none;"></audio>
  </section>

  <!-- 2. Gravar e Corrigir seu Inglês -->
  <section>
    <h2>2. Grave e Corrija</h2>
    <button onclick="corrigirPronuncia()">🎤 Grave em Inglês</button>
    <p><strong>Você disse:</strong> <span id="reconhecido"></span></p>
    <p><strong>Correção:</strong> <span id="correcao"></span></p>
    <audio id="audioEN" controls style="display:none;"></audio>
  </section>

  <script>
    const OPENAI_API_KEY = "{OPENAI_API_KEY}";

    // 1. Traduzir PT→EN + TTS
    async function traduzirEReproduzir() {{
      const pt = document.getElementById("inputPT").value.trim();
      if (!pt) return alert("Digite algo em português primeiro!");
      // tradução
      const chat = await fetch("https://api.openai.com/v1/chat/completions", {{
        method: "POST",
        headers: {{
          "Content-Type":"application/json",
          "Authorization": `Bearer ${{OPENAI_API_KEY}}`
        }},
        body: JSON.stringify({{
          model: "gpt-4o",
          messages: [{{ role: "user", content: `Traduza para inglês: "${{pt}}"` }}]
        }})
      }});
      const chatData = await chat.json();
      const en = chatData.choices[0].message.content.trim();
      document.getElementById("respostaPT").innerText = en;
      // TTS
      const tts = await fetch("https://api.openai.com/v1/audio/speech", {{
        method: "POST",
        headers: {{
          "Content-Type":"application/json",
          "Authorization": `Bearer ${{OPENAI_API_KEY}}`
        }},
        body: JSON.stringify({{ model: "tts-1", input: en, voice: "nova" }})
      }});
      const blob = await tts.blob();
      const url = URL.createObjectURL(blob);
      const audio = document.getElementById("audioPT");
      audio.src = url;
      audio.style.display = "block";
      audio.play();
    }}

    // 2. Gravar em inglês e corrigir
    function corrigirPronuncia() {{
      const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!Recognition) return alert("SpeechRecognition não suportado.");
      const rec = new Recognition();
      rec.lang = "en-US";
      rec.interimResults = false;
      rec.maxAlternatives = 1;

      rec.onresult = async e => {{
        const falado = e.results[0][0].transcript.trim();
        document.getElementById("reconhecido").innerText = falado;
        // correção no OpenAI
        const corr = await fetch("https://api.openai.com/v1/chat/completions", {{
          method: "POST",
          headers: {{
            "Content-Type":"application/json",
            "Authorization": `Bearer ${{OPENAI_API_KEY}}`
          }},
          body: JSON.stringify({{
            model: "gpt-4o",
            messages: [
              {{ role: "system", content: "Você é um professor de inglês. Corrija o texto abaixo e responda sempre: you meant to say... e diga a frase corrigida" }},
              {{ role: "user", content: falado }}
            ]
          }})
        }});
        const corrData = await corr.json();
        const fraseCorr = corrData.choices[0].message.content.trim();
        document.getElementById("correcao").innerText = fraseCorr;
        // TTS da correção
        const tts2 = await fetch("https://api.openai.com/v1/audio/speech", {{
          method: "POST",
          headers: {{
            "Content-Type":"application/json",
            "Authorization": `Bearer ${{OPENAI_API_KEY}}`
          }},
          body: JSON.stringify({{ model: "tts-1", input: fraseCorr, voice: "nova" }})
        }});
        const blob2 = await tts2.blob();
        const url2 = URL.createObjectURL(blob2);
        const audio2 = document.getElementById("audioEN");
        audio2.src = url2;
        audio2.style.display = "block";
        audio2.play();
      }};

      rec.onerror = err => alert("Erro no reconhecimento: " + err.error);
      rec.start();
    }}
  </script>
</body>
</html>
"""

components.html(html_code, height=900, scrolling=True)

st.sidebar.header("Instruções")

