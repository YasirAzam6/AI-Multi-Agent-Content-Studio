import openai
from pathlib import Path
import json
from openai import OpenAI
from dotenv import load_dotenv
from llm_client import llm_client
import os
import re

load_dotenv()

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

def clean_transcript(raw_text: str) -> str:
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"""
    Clean the transcript by:
    - removing filler words
    - fixing broken/incomplete sentences
    - normalizing punctuation
    - removing repeated or duplicated segments
    - keeping ONLY what the speaker actually says

    Return clean text only.
    Transcript:
    {raw_text}
    """
    cleaned = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    ).choices[0].message.content
    return cleaned.strip()

def generate_transcript_from_video(video_path: str, model: str = "gpt-4o-mini-transcribe") -> str:
    """
    Generates a transcript from a local video file using OpenAI's Whisper model.

    Parameters:
    -----------
    video_path : str
        Path to the local video file (e.g., 'video.mp4').
    model : str, optional
        The OpenAI model to use for transcription. Default is 'gpt-4o-mini-transcribe'.
        You can also use 'whisper-1' for the classic Whisper model.

    Returns:
    --------
    str
        The full transcribed text from the video.
    """
    # client = openai.OpenAI()

    # Ensure file exists
    file_path = Path(video_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Open and send the file to OpenAI
    with open(file_path, "rb") as video_file:
        response = llm_client.audio.transcriptions.create(
            model=model,
            file=video_file,
            response_format="text"  # returns plain text
        )
    return response


def generate_style_profile(influencer_name: str, transcript_text: str):
    """
    Generate or append style analysis for an influencer.
    Saves JSON inside the influencer_styles/ folder located next to app.py.
    """
    prompt = f"""
    You are an expert linguistic profiler analyzing an Instagram/YouTube influencer’s communication style.
    Extract a DEEP persona style profile.
    Respond in pure JSON (no markdown).

    Keep the output concise JSON with only these keys:

    {{
    "tone": "",
    "energy_level": "",
    "delivery_style": {{
        "pacing": "",
        "sentence_variation": "",
        "story_usage": "",
        "analogy_usage": "",
        "directive_strength": ""
    }},
    "linguistic_fingerprint": {{
        "average_sentence_length": "",
        "common_sentence_types": [],
        "rhetorical_devices": [],
        "transition_patterns": []
    }},
    "hook_style": {{
        "dominant_types": [],
        "examples": []
    }},
    "signature_phrases": [],
    "forbidden_phrases": [],
    "persona": "",
    "content_archetype": "",
    "strength_indicators": [],
    "emotional_beats": []
    }}

    Transcript sample:
    {transcript_text[:7000]}
    """

    print("🧠 Analyzing style with OpenAI...")
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    style_json = response.choices[0].message.content
    new_style = safe_json_loads(style_json)

    # ✅ Detect project root (one level up from Scripts/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, os.pardir))

    # ✅ Ensure influencer_styles exists inside root
    influencer_dir = os.path.join(project_root, "influencer_styles")
    os.makedirs(influencer_dir, exist_ok=True)

    # ✅ Build file path inside influencer_styles
    influencer_file = os.path.join(
        influencer_dir,
        f"{influencer_name.lower().replace(' ', '_')}.json"
    )

    # ✅ Load existing or create new
    if os.path.exists(influencer_file):
        with open(influencer_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    else:
        existing_data = {"name": influencer_name, "analyses": []}

    # ✅ Append new analysis
    existing_data["analyses"].append(new_style)

    # ✅ Merge multiple analyses if exist
    if len(existing_data["analyses"]) > 1:
        merge_prompt = f"""
       You are an expert style profiler. Merge multiple deep style analyses into one unified style profile.

        Your tasks:
        - Preserve ALL deep attributes from each sample.
        - Identify traits consistent across most samples.
        - Down-weight traits that appear only once.
        - Extract averaged or representative values where relevant.
        - Produce a SINGLE merged profile that fully reflects the influencer's communication style.

        Return JSON ONLY in this structure:

        {{
        "style_profile": {{
            "tone": "",
            "energy_level": "",
            "delivery_style": {{
            "pacing": "",
            "sentence_variation": "",
            "story_usage": "",
            "analogy_usage": "",
            "directive_strength": ""
            }},
            "linguistic_fingerprint": {{
            "average_sentence_length": "",
            "common_sentence_types": [],
            "rhetorical_devices": [],
            "transition_patterns": []
            }},
            "hook_style": {{
            "dominant_types": [],
            "examples": []
            }},
            "signature_phrases": [],
            "forbidden_phrases": [],
            "persona": "",
            "content_archetype": "",
            "strength_indicators": [],
            "emotional_beats": []
        }},
        "consistency_score": {{
            "tone": 0.0,
            "energy_level": 0.0,
            "delivery_style": 0.0,
            "linguistic_fingerprint": 0.0,
            "persona": 0.0
        }}
        }}

        Here are the analyses to merge:
        {json.dumps(existing_data["analyses"])}
        """
        merged = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": merge_prompt}],
            temperature=0.7
        ).choices[0].message.content

        existing_data["merged_profile"] = safe_json_loads(merged)

    # ✅ Save file in correct influencer_styles directory
    with open(influencer_file, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Updated style profile saved at: {influencer_file}")
    return existing_data


def generate_influencer_style(influencer_name: str, video_path: str):
    
    print(f"🎥 Generating style for {influencer_name} from {video_path}")

    # Step 1: Generate transcript
    transcript_text = generate_transcript_from_video(video_path)

    if not transcript_text:
        print("❌ No transcript found, skipping style generation.")
        return None
    # 🔹 NEW
    transcript_text = clean_transcript(transcript_text)

    # Step 2: Generate style profile
    style_data = generate_style_profile(influencer_name, transcript_text)

    print("\n🎯 Generated Style Summary:")
    print(json.dumps(style_data, indent=2, ensure_ascii=False))

    return style_data