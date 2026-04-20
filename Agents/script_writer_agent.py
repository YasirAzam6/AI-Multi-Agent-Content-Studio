import json
from Agents.base_agent import BaseAgent

class ScriptWriterAgent(BaseAgent):
    def run(self, state):

        # Check if feedback exists → meaning this is a revision - a new prompt bran
        #only triggered when quality agent say "revise"
        feedback = state.get("revision_feedback", None)

        if feedback:
            # Refinement mode
            draft = state.get("processed_script", "")
           # draft = state.get("edited_script", "")
            prompt = f"""
            You are revising a YouTube script based on quality feedback.

            Script to improve:
            {draft}

            Feedback (must be applied):
            {feedback}

            Your goals:
            - Improve style_match with the influencer's voice.
            - Strengthen emotional tone and narrative impact.
            - Fix pacing issues (remove rambling, improve flow).
            - Improve clarity and storytelling coherence.
            - Preserve the influencer's style, tone, and persona.


            Return the improved script only.
            """
            print("✍️ ScriptWriterAgent → refining script using feedback...")
            state["draft_script"] = self.call_llm(prompt, temperature=0.9)
            return state
#  2) NORMAL: First-pass script generation
        topic = state["topic"]
        style_profile = json.dumps(state["style_profile"], indent=2)
        research = state.get("research_notes", "")
        duration = state.get("duration", 180)  # default 3 min if not provided

        # Estimate ~2.5 words/second for spoken video
        target_words = int(duration * 2.5)
#hook generation prompt for better kick start in writing
        hook_prompt = f"""
        You are a YouTube hook-generation expert.

        Create 4 strong hook options for a script on the topic:
        "{topic}"

        Follow the influencer's tone:
        {style_profile}

        Return JSON ONLY:
        {{
          "curiosity_hook": "...",
          "emotional_hook": "...",
          "story_hook": "...",
          "data_hook": "..."
        }}
        """

        hooks_raw = self.call_llm(hook_prompt, temperature=1.0)

        try:
            hooks = json.loads(hooks_raw)
        except:
            hooks = {"raw_output": hooks_raw}

        # Store them for later agents or UI if needed
        state["hooks"] = hooks

        prompt = f"""
        You are a professional YouTube scriptwriter who must EXACTLY mimic the influencer's communication style.

        Topic: "{topic}"
        Target duration: {duration} seconds (approx. {target_words} words)

        --- Influencer Style Profile (MUST FOLLOW STRICTLY) ---
        {style_profile}

        --- Research Notes (for content accuracy) ---
        {research}

        STYLE RULES — FOLLOW THESE STRICTLY:
        1. **Vocabulary Patterns:** Use phrases, word choices, and signature expressions from the influencer's style profile.
        2. **Sentence Rhythm:** 
           - Match the influencer’s cadence (short impactful lines vs long reflective lines).
           - Use sentence variation exactly as the influencer typically does.
        3. **Pacing Control:** 
           - Start strong, maintain flow, avoid rambling.
           - Place emotional or punchy lines at natural breakpoints.
        4. **Emotional Tone Markers:** 
           - If the persona is motivational, use powerful emotional beats.
           - If reflective, use introspective transitions.
        5. **Signature Phrases:** 
           - Use them sparingly but intentionally.
           - They must feel organic, not forced.
        6. **Persona Alignment:**
           - Speak as the influencer THINKS, not just as they talk.
           - Maintain consistent persona throughout.

        Script Structure:
        - Hook (high-impact, emotionally targeted)
        - Relatable story or narrative bridge
        - Framework / reasoning
        - Real-world examples or comparisons
        - Close with an emotionally resonant conclusion (avoid generic CTAs)

        CRITICAL RULE:
        - Refer to the influencer generically as "Influencer".
        - DO NOT break character or introduce generic AI tone.

        Write the full script now in the influencer’s exact style.
        """

        
        print(f"✍️ ScriptWriterAgent → generating ~{duration}s script ...")
        state["draft_script"] = self.call_llm(prompt, temperature=1.0)
        return state
