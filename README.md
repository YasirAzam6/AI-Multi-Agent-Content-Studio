# 🎬 AI Multi-Agent Content Studio

Generate high-quality YouTube scripts in your favorite influencer’s style — powered by **LangGraph**, **OpenAI**, and an interactive **Streamlit** interface.

---

## 🌟 Overview

This system uses a **multi-agent architecture** to mimic a professional creative team:

| Role | Agent | Responsibility |
|------|--------|----------------|
| 🔍 Researcher | `ResearchAgent` | Gathers recent insights and ideas on the topic |
| ✍️ Scriptwriter | `ScriptWriterAgent` | Writes the YouTube script in the influencer’s tone and structure |
| 🧹 Editor | `EditorAgent` | Polishes for readability, pacing, and delivery |
| 🧠 Quality Reviewer | `QualityAgent` | Evaluates tone, clarity, and style match |
| 🧩 Director | LangGraph workflow | Connects all agents and manages state flow |

You simply:
1. Select an **influencer style** (pre-saved JSON profile)  
2. Enter a **topic**  
3. Choose a **video duration** (e.g., 120 seconds)  
4. Click **Generate** → instantly receive a complete voice-ready script ✨


