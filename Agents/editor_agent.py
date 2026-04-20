from Agents.base_agent import BaseAgent


class EditorAgent(BaseAgent):
    def run(self, state):
        draft = state.get("draft_script", "")
        style_profile = state.get("style_profile", {})
        #naming convention update
        prompt = f"""
        You are a professional script editor specializing in *style-preserving editing*.

        Your job:
        - Improve clarity, pacing, emotional flow, and narrative structure.
        - DO NOT change the influencer’s tone, persona, or signature style.

        --- Influencer Style Profile (must preserve) ---
        {style_profile}

        STRICT STYLE PRESERVATION RULES:
        1. Keep vocabulary patterns consistent with the influencer.
        2. Maintain original sentence rhythm and flow (short vs long patterns).
        3. Retain emotional tone markers.
        4. Preserve signature phrasing — enhance but never replace.
        5. Do not remove stylistic quirks; refine them.
        6. Maintain the persona’s voice and worldview.
        7. Fix grammar or transitions WITHOUT altering stylistic identity.

        Edit the following script while maintaining ALL style constraints:

        --- Script to Edit ---
        {draft}

        Return ONLY the polished script with the influencer’s style preserved.
        """

        print("🧹 EditorAgent → polishing ...")
        state["edited_script"] = self.call_llm(prompt, temperature=0.6)
        return state