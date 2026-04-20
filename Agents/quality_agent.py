import json
from Agents.base_agent import BaseAgent
from Scripts.youtube_influencer_profile import safe_json_loads

class QualityAgent(BaseAgent):
    def run(self, state):
        edited_script = state.get("processed_script", "")
        style_profile = json.dumps(state["style_profile"], indent=2)

        prompt = f"""
        Evaluate how well this script matches the influencer’s style.

        Influencer style: 
        {style_profile}

        Script:
        {edited_script}

        Return JSON with:
        {{
          "style_match_score": float (0–1),
          "clarity_score": float (0–1),
          "storytelling_score": float (0–1),
          "feedback": "short qualitative notes"
        }}
        """
        print("🧠 QualityAgent → evaluating output ...")
        raw_result = self.call_llm(prompt, temperature=0.0)
        default_report = {
            "style_match_score": 0.5,
            "clarity_score": 0.5,
            "storytelling_score": 0.5,
            "feedback": "No structured feedback available.",
            "raw_output": raw_result
        }

        parsed = safe_json_loads(raw_result)

        if "raw_output" in parsed:
            # safe_json_loads indicates extraction failed
            print("⚠️ Failed to parse quality JSON. Using fallback.")
            state["quality_report"] = default_report
            return state

        # Build clean quality report with defaults for missing fields
        state["quality_report"] = {
            "style_match_score": parsed.get("style_match_score", 0.5),
            "clarity_score": parsed.get("clarity_score", 0.5),
            "storytelling_score": parsed.get("storytelling_score", 0.5),
            "feedback": parsed.get("feedback", "Unable to parse feedback."),
            "raw_output": raw_result,
        }

        return state

#changed: quality report into dictionary from a string.