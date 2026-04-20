from typing import TypedDict, Optional, Dict

class ScriptState(TypedDict, total=False):
    topic: str
    influencer: str
    style_profile: Dict
    duration: Optional[int]
    content_type: Optional[str]
    research_notes: Optional[str]
    draft_script: Optional[str]
    edited_script: Optional[str]
    quality_report: Optional[str]
    processed_script: Optional[str]
    revision_count: Optional[int]
    revision_feedback: Optional[str]
