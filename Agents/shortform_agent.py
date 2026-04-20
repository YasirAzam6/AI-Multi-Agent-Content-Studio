import json
from Agents.base_agent import BaseAgent

class ShortFormAgent(BaseAgent):
    """
    Generates short Instagram-style scripts (value-focused, hook-first, fast delivery) using retention psychology.
    """
    def run(self, state):
        topic = state["topic"]
        style_profile = json.dumps(state["style_profile"], indent=2)
        duration = state.get("duration", 60)  # typical short-form 30–90s

        # Aim for ~2.5 words/sec
        target_words = int(duration * 2.5)

#changed system prompt
        system_message =  """
        You are an elite short-form scriptwriter trained in high retention psychology.

        RULES FOR SHORT-FORM CONTENT:
        - Start with a strong micro-hook in the FIRST line (curiosity, emotion, surprise).
        - Use OPEN LOOPS (hint at something coming later).
        - Use PATTERN INTERRUPTS every 2–4 lines (unexpected statements, shifts).
        - Keep pacing extremely punchy. No filler.
        - Use emotional micro-hooks (shock, tension, aha moment).
        - Deliver 1 powerful insight, not many.
        - End with a punchline or a cliffhanger—not a CTA.
        """

        user_message = f"""
        Write a {duration}-second short-form script on "{topic}" 
        using approximately {target_words} words.

        Use this influencer's tone and phrasing style:
        {style_profile}

        STRUCTURE:
        1. Micro-hook (1 sentence)
        2. Open loop (hint that something bigger is coming)
        3. Fast-paced insight or story
        4. Pattern interrupt (new angle or unexpected twist)
        5. Emotional payoff / punchline

        STRICT RULES:
        - No greetings.
        - Keep sentences tight and rhythmic.
        - Do NOT close all loops—leave mild tension.
        - Refer to influencer as “Influencer”.
        """
        print(f"⚡ ShortFormAgent → generating {duration}s short-form script ...")
        state["draft_script"] = self.call_llm(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            
            temperature=1.0
        )
        return state
