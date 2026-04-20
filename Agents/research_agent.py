from Agents.base_agent import BaseAgent

#Verified facts
#Recent statistics with sources
#2023–2024 trend insights
#Common misconceptions in the niche

class ResearchAgent(BaseAgent):
    def run(self, state):
        topic = state["topic"]
        prompt = f"""
        You are an expert research assistant for professional YouTube and Instagram creators.
        Your job is to produce accurate, recent, and actionable research notes on:
        "{topic}"

        Follow these rules strictly:
        - Keep the output concise but information-dense.
        - Use bullet points, not paragraphs.
        - If a fact or statistic is uncertain, write: "⚠️ Data unclear / varies by source."
        - Prioritize information from 2023–2024.
        - Avoid filler, motivational lines, or generic advice.
        - Keep everything script-ready.

        Provide the research in the following structured format:

        1. **Verified Facts**
        - Provide factual statements that are widely accepted.
        - Keep language simple and clear.

        2. **Recent Statistics (2023–2024-2025)**
        - Include numbers WITH attribution (e.g., “Source: WHO, 2023”).
        - If exact statistics are unavailable, write: “⚠️ No reliable stat available.”

        3. **Latest Trends & Insights**
        - Identify macro-trends related to the topic.
        - Identify micro-trends (niche or early-stage developments).
        - Include platform-specific patterns (e.g., short-form trends, consumer behavior shifts).

        4. **Common Misconceptions**
        - List misunderstandings audiences typically have about this topic.
        - Correct them briefly.

        5. **Opportunities / Angles for Scriptwriting**
        - Provide 3–5 angles or talking points that would make a strong narrative.
        - This section helps the writer build a more engaging script.

        Keep it factual, recent, and structured exactly in the format above.
        """

        print(f"🔍 ResearchAgent → researching '{topic}' ...")
        state["research_notes"] = self.call_llm(prompt, temperature=0.9)
        return state
