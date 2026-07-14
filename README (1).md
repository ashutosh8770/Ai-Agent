# Autonomous AI Research Agent

Ye ek chhota, self-contained Python project hai jo:
1. **Collect** — kisi bhi topic par web search karke information collect karta hai
2. **Analyze** — Claude (Anthropic API) se us data ko analyze/synthesize karwata hai
3. **Report** — ek structured, actionable summary (Markdown + JSON) file mein save karta hai

---

## 📁 Folder kahan rakhein

Is poore folder (`ai_research_agent/`) ko apne computer par kahin bhi rakh sakte ho, jaise:

- **Windows**: `C:\Users\<aapka-naam>\Projects\ai_research_agent`
- **Mac/Linux**: `~/Projects/ai_research_agent`

Bas itna dhyan rakhein ki `agent.py`, `requirements.txt` aur ye `README.md` teeno **ek hi folder** mein saath rahein.

---

## ⚙️ Setup (ek baar karna hai)

1. **Python 3.10+** installed hona chahiye. Check karein:
   ```bash
   python --version
   ```

2. Terminal/CMD kholke is folder mein jaayein:
   ```bash
   cd path/to/ai_research_agent
   ```

3. (Recommended) Virtual environment banayein:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Mac/Linux
   venv\Scripts\activate         # Windows
   ```

4. Dependencies install karein:
   ```bash
   pip install -r requirements.txt
   ```

5. Apni **Google Gemini API key** set karein (Google AI Studio: https://aistudio.google.com/apikey se free milegi):
   ```bash
   export GEMINI_API_KEY="AIzaSy-yahan-apni-key-daalein"     # Mac/Linux
   setx GEMINI_API_KEY "AIzaSy-yahan-apni-key-daalein"       # Windows (naya terminal restart karein)
   ```

---

## ▶️ Chalane ka tareeka

```bash
python agent.py --topic "AI regulation in the EU"
```

Extra options:
```bash
python agent.py --topic "electric vehicle market 2026" --num-sources 10 --format both --out-dir ./reports
```

| Flag | Matlab | Default |
|---|---|---|
| `--topic` | Research karne ka topic (required) | — |
| `--num-sources` | Kitne web sources collect karne hain | 8 |
| `--format` | `md`, `json`, ya `both` | both |
| `--out-dir` | Report kahan save ho | `./reports` |
| `--model` | Kaunsa Gemini model use ho | `gemini-2.5-flash` |

---

## 📄 Output kahan milega

Report `./reports/` folder ke andar save hogi (jab tak `--out-dir` se alag na diya ho), filename mein topic + timestamp hoga. Har run se:

- `<topic>_<timestamp>.md` — human-readable structured report
- `<topic>_<timestamp>.json` — same data machine-readable form mein

Report mein ye sections honge: Executive Summary, Key Findings, Risks/Concerns, Action Items (priority ke saath), Open Questions, aur Sources list.

---

## 🧩 Isko extend kaise karein

- **Aur sources add karne ke liye**: `collect_information()` function mein RSS feeds, specific APIs, ya files se bhi data pull kar sakte ho — bas usko `sources` list ke same format (`title`, `url`, `snippet`) mein daalna hai.
- **Scheduling ke liye**: is script ko cron job (Mac/Linux) ya Task Scheduler (Windows) se daily/weekly chala sakte ho taki agent apne aap chalta rahe.
