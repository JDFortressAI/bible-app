import streamlit as st




def refresh_speak_html():
    """
    Build Play / Pause / Resume / Stop buttons.
    Uses the best available male voice on every platform.
    """
    # ------------------------------------------------------------------
    # 1. Escape back-ticks for JS template literals
    # ------------------------------------------------------------------
    raw = st.session_state.full_text.replace("`", "\\`")

    # ------------------------------------------------------------------
    # 2. Split into chunks + pause markers
    # ------------------------------------------------------------------
    import re
    parts = []
    pos = 0
    for m in re.finditer(r"{{pause\s+(\d+)}}", raw):
        if m.start() > pos:
            parts.append((raw[pos:m.start()].strip(), None))
        parts.append(("", int(m.group(1))))
        pos = m.end()
    if pos < len(raw):
        parts.append((raw[pos:].strip(), None))

    # ------------------------------------------------------------------
    # 3. Build JS array of chunks
    # ------------------------------------------------------------------
    js_chunks = []
    for text, pause in parts:
        if pause is not None:
            js_chunks.append(f"{{pauseSec: {pause}}}")
        elif text:
            js_chunks.append(f"{{text: `{text}`}}")
    chunks_array = "[" + ", ".join(js_chunks) + "]"

    # ------------------------------------------------------------------
    # 4. HTML + JS with robust male voice selection
    # ------------------------------------------------------------------
    speak_html = f"""
<script>
  // ---------- Global state ----------
  let isPaused = false;
  let isStopped = false;
  let currentUtt = null;
  let chunkIdx = 0;
  let chunks = null;
  let selectedVoice = null;

  // ---------- Voice selection (cross-platform, male-first) ----------
  function getBestMaleVoice() {{
    return new Promise((resolve) => {{
      let voices = window.speechSynthesis.getVoices();

      const isMale = (v) => {{
        const name = v.name.toLowerCase();
        const lang = v.lang.toLowerCase();
        return (
          name.includes('male') ||
          name.includes('david') ||
          name.includes('daniel') ||
          name.includes('guy') ||
          name.includes('mark') ||
          name.includes('paul') ||
          name.includes('james') ||
          name.includes('alex') && !name.includes('samantha') ||
          name.includes('en-us') && name.includes('standard') && !name.includes('female')
        );
      }};

      if (voices.length > 0) {{
        selectedVoice = voices.find(v => isMale(v) && v.lang.startsWith('en')) ||
                        voices.find(v => v.name === 'Alex' && v.lang === 'en-US') ||
                        voices.find(v => v.name === 'Daniel' && v.lang.startsWith('en')) ||
                        voices.find(v => v.lang.startsWith('en'));
        resolve(selectedVoice);
        return;
      }}

      const handler = () => {{
        voices = window.speechSynthesis.getVoices();
        selectedVoice = voices.find(v => isMale(v) && v.lang.startsWith('en')) ||
                        voices.find(v => v.name === 'Alex' && v.lang === 'en-US') ||
                        voices.find(v => v.name === 'Daniel' && v.lang.startsWith('en')) ||
                        voices.find(v => v.lang.startsWith('en'));
        window.speechSynthesis.removeEventListener('voiceschanged', handler);
        resolve(selectedVoice);
      }};
      window.speechSynthesis.addEventListener('voiceschanged', handler);
    }});
  }}

  // ---------- Start ----------
  async function speakNow(allChunks) {{
    if (!('speechSynthesis' in window)) {{
      alert('Speech not supported');
      return;
    }}

    if (!selectedVoice) {{
      await getBestMaleVoice();
    }}

    window.speechSynthesis.cancel();
    isPaused = false; isStopped = false;
    document.getElementById('pauseBtn').textContent = 'Pause';
    chunks = allChunks;
    chunkIdx = 0;
    nextChunk();
  }}

  // ---------- Process next chunk ----------
  function nextChunk() {{
    if (isStopped || chunkIdx >= chunks.length) return;
    if (isPaused) return;

    const chunk = chunks[chunkIdx++];
    if ('pauseSec' in chunk) {{
      const start = Date.now();
      const timer = setInterval(() => {{
        if (Date.now() - start >= chunk.pauseSec * 1000) {{
          clearInterval(timer);
          nextChunk();
        }}
      }}, 50);
      const silent = new SpeechSynthesisUtterance('');
      silent.onend = () => {{}};
      window.speechSynthesis.speak(silent);
    }} else {{
      const u = new SpeechSynthesisUtterance(chunk.text);
      u.lang = 'en-US';
      if (selectedVoice) u.voice = selectedVoice;
      currentUtt = u;
      u.onend = () => {{ currentUtt = null; nextChunk(); }};
      u.onerror = (e) => {{ console.error(e); nextChunk(); }};
      window.speechSynthesis.speak(u);
    }}
  }}

  // ---------- Pause / Resume ----------
  function togglePause() {{
    const btn = document.getElementById('pauseBtn');
    if (isStopped) return;

    if (isPaused) {{
      isPaused = false;
      btn.textContent = 'Pause';
      window.speechSynthesis.resume();
      nextChunk();
    }} else {{
      isPaused = true;
      btn.textContent = 'Resume';
      window.speechSynthesis.pause();
    }}
  }}

  // ---------- Stop ----------
  function stopSpeech() {{
    window.speechSynthesis.cancel();
    isStopped = true;
    isPaused = false;
    const btn = document.getElementById('pauseBtn');
    if (btn) btn.textContent = 'Pause';
  }}
</script>

<button onclick="speakNow({chunks_array})"
    style="padding:12px 20px; font-size:16px; background:#0066cc; color:white;
           border:none; border-radius:8px; cursor:pointer; font-weight:bold; margin-right:8px;">
  Play
</button>

<button id="pauseBtn" onclick="togglePause()"
    style="padding:12px 20px; font-size:16px; background:#ff9800; color:white;
           border:none; border-radius:8px; cursor:pointer; font-weight:bold; margin-right:8px;">
  Pause
</button>

<button onclick="stopSpeech()"
    style="padding:12px 20px; font-size:16px; background:#cc6600; color:white;
           border:none; border-radius:8px; cursor spear; font-weight:bold;">
  Stop
</button>
"""
    st.session_state.speak_html = speak_html