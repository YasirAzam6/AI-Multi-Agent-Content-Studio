from Agents.base_agent import BaseAgent

class PostProcessorAgent(BaseAgent):
    """
    Cleans the final script: removes stage directions, redundant markers, etc.
    """
    def run(self, state):
        script = state.get("edited_script", "")
        prompt = f"""
        Clean the following script by removing all stage directions or descriptions
        like [Opening shot:], [Cut to:], [Closing shot:], etc.
        Keep only the spoken lines. Return the cleaned script text only.
        Not to add this type of text:
        Example:
        Sure! Here’s a polished version of your script that maintains the influencer's tone while enhancing pacing, clarity, and emotional flow:
        Only i need is the script.
        Script:
        {script}
        """
        cleaned = self.call_llm(prompt, temperature=0.0)
        state["processed_script"] = cleaned.strip()
        return state