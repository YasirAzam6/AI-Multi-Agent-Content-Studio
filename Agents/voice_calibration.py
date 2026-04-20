import json
from Agents.base_agent import BaseAgent
import re

def safe_json_loads(text):
        try:
            return json.loads(text)
        except:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    return {"raw_output": text}
            return {"raw_output": text}
        
class VoiceCalibrationAgent(BaseAgent):
    """
    Analyzes creator-provided writing samples and extracts a personalized style profile.
    This profile is later merged with the influencer's style to create a blended voice.
    
    Structure:
    - Influencer style = macro persona (tone, structure, pacing)
    - Creator style = micro voice fingerprint (vocabulary, rhythm, markers)
    - Final = influencer_profile + creator_voice_fingerprint
    """
    def run(self, state: dict) -> dict:
        """
        Optional integration method.

        If `state` contains a list of writing samples under 'creator_samples' or 'samples',
        this method will analyze them and attach the result as `state["creator_style"]`.

        If there are no samples, it simply returns the state unchanged.
        """
        samples = state.get("creator_samples") or state.get("samples")
        if not samples:
            return state

        profile = self.analyze_creator_style(samples)
        state["creator_style"] = profile
        return state

    def analyze_creator_style(self, samples: list[str]) -> dict:
        """
        Analyze 1-3 writing samples and extract creator's voice fingerprint.
        
        Returns a JSON profile with the SAME structure as influencer styles:
        - tone
        - structure
        - sentence_pattern
        - signature_phrases
        - persona
        
        Plus additional micro-level signals:
        - vocabulary_patterns
        - sentence_rhythm
        - emotional_markers
        - forbidden_phrases
        """
        
        # Combine samples with clear separation
        joined_samples = "\n\n--- SAMPLE BREAK ---\n\n".join(samples)

        prompt = f"""
            You are an expert writing style analyst.

            Analyze the writing samples below and extract a detailed style profile.

            YOUR TASK:
            Extract the creator's unique voice fingerprint — the subtle patterns that make their writing distinct.

            RETURN STRICT JSON with these exact keys:

            {{
            "tone": "brief description of emotional tone (e.g., casual, professional, motivational)",
            "structure": "pacing style (e.g., fast-paced with short sentences, slow build with long paragraphs)",
            "sentence_pattern": "rhythm and length patterns (e.g., mix of short punchy lines and longer explanations)",
            "signature_phrases": ["list", "of", "recurring", "expressions", "or", "transitions"],
            "persona": "identity/worldview (e.g., skeptical observer, enthusiastic teacher, pragmatic advisor)",
            "vocabulary_patterns": ["common", "word", "choices", "or", "technical", "terms"],
            "sentence_rhythm": "cadence description (e.g., staccato, flowing, conversational)",
            "emotional_markers": ["words", "or", "phrases", "that", "show", "emotion"],
            "forbidden_phrases": ["clichés", "or", "expressions", "the", "creator", "avoids"]
            }}

            RULES:
            - Be specific and concrete
            - Base everything on actual patterns in the text
            - If something is unclear, use "varies" or "mixed"
            - NO markdown, NO explanations, ONLY valid JSON

            Writing samples to analyze:
            {joined_samples}
            """

        print("🔬 VoiceCalibrationAgent → analyzing creator's writing style...")
        response = self.call_llm(prompt, temperature=0.3)

        try:
            style_profile = json.loads(response)
            print("✅ Creator style profile extracted successfully")
            return style_profile
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing failed: {e}")
            print(f"Raw response: {response[:500]}")
            # Return a minimal valid structure
            return {
                "tone": "unable to parse",
                "structure": "unable to parse",
                "sentence_pattern": "unable to parse",
                "signature_phrases": [],
                "persona": "unable to parse",
                "raw_output": response
            }

    def merge_styles(self, creator_style: dict, influencer_style: dict) -> dict:
        """
        Merge creator's voice fingerprint with influencer's macro style.
        
        PRIORITY:
        - Influencer provides: macro persona, overall structure, pacing framework
        - Creator provides: micro vocabulary, rhythm nuances, emotional markers
        
        Result: Influencer's framework + Creator's voice fingerprint
        """

        # Clean creator style (remove analysis artifacts)
        creator_clean = {k: v for k, v in creator_style.items() if k != "raw_output"}
        
        # Clean influencer style (handle both merged_profile and direct formats)
        if "merged_profile" in influencer_style:
            influencer_clean = influencer_style["merged_profile"]
        elif "analyses" in influencer_style:
            # Use the most recent analysis or merged profile
            influencer_clean = influencer_style.get("merged_profile", influencer_style["analyses"][-1])
        else:
            influencer_clean = influencer_style

        prompt = f"""
        You are a style synthesis expert.

        Your task: Merge TWO writing styles into ONE unified profile.

        PRIORITY RULES:
        1. Influencer style = PRIMARY (macro structure, tone, persona, pacing)
        2. Creator style = SECONDARY (micro vocabulary, rhythm, emotional nuances)

        THINK OF IT AS:
        - Influencer = skeleton and muscle structure
        - Creator = skin texture and fingerprints

        The result should FEEL like the influencer but have the creator's subtle voice markers.

        --- INFLUENCER STYLE (PRIMARY - MACRO) ---
        {json.dumps(influencer_clean, indent=2)}

        --- CREATOR STYLE (SECONDARY - MICRO) ---
        {json.dumps(creator_clean, indent=2)}

        MERGE STRATEGY:
        - Keep influencer's: overall tone category, structure type, persona identity
        - Blend in creator's: specific vocabulary, sentence rhythm variations, emotional markers
        - Preserve influencer's signature phrases (they define the persona)
        - Add creator's vocabulary patterns as "flavor"
        - Combine sentence patterns: influencer's structure + creator's rhythm

        RETURN STRICT JSON with these exact keys:
        {{
        "tone": "merged tone (influencer-led, creator-flavored)",
        "structure": "merged structure (influencer's pacing + creator's rhythm)",
        "sentence_pattern": "combined patterns (influencer's style + creator's cadence)",
        "signature_phrases": ["keep influencer's signature phrases"],
        "persona": "influencer's persona (preserved)",
        "vocabulary_patterns": ["blend: influencer's key terms + creator's word choices"],
        "emotional_markers": ["combine both sets"],
        "sentence_rhythm": "influencer's baseline + creator's variations"
        }}

        CRITICAL:
        - The output must sound like the INFLUENCER
        - But with the creator's subtle fingerprint woven in
        - Do NOT create a 50/50 blend — this is 70% influencer, 30% creator
        - NO markdown, NO explanations, ONLY valid JSON
        """

        print("🔀 VoiceCalibrationAgent → merging styles (70% influencer, 30% creator)...")
        response = self.call_llm(prompt, temperature=0.3)

        try:
            merged_profile = json.loads(response)
            if "signature_phrases" not in merged_profile or not isinstance(merged_profile["signature_phrases"], list):
                merged_profile["signature_phrases"] = []
            print("✅ Styles merged successfully")
            return merged_profile
        
        except json.JSONDecodeError as e:
            print(f"⚠️ Merge JSON parsing failed: {e}")
            print(f"Raw response: {response[:500]}")
            
            # Fallback: Return influencer style with creator note
            print("⚠️ Falling back to influencer style")
            fallback = influencer_clean.copy()
            fallback["merge_note"] = "Merge failed - using influencer style only"
            fallback["raw_merge_output"] = response
            return fallback
        
