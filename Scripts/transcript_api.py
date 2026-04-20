import os
import json
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from openai import OpenAI
from dotenv import load_dotenv
from llm_client import llm_client
import re

load_dotenv()

# Initialize OpenAI client
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def safe_json_loads(text):
    """Extract JSON even if model returns extra text."""
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



def extract_video_id(url: str) -> str:
    """
    Extract YouTube video ID from any valid YouTube URL.
    """
    parsed = urlparse(url)
    if parsed.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed.query)["v"][0]
    elif parsed.hostname == "youtu.be":
        return parsed.path[1:]
    else:
        raise ValueError("Invalid YouTube URL provided.")


def get_youtube_transcript(video_url: str) -> str:
    """
    Fetch the transcript text from a YouTube video URL.
    """
    video_id = extract_video_id(video_url)
    print(f"🎬 Fetching transcript for video ID: {video_id}")

    try:
        youtube_transcript = YouTubeTranscriptApi()
        transcript_list = youtube_transcript.fetch(video_id)
        full_text = " ".join([t.text for t in transcript_list if t.text.strip()])
        print(f"✅ Transcript fetched successfully ({len(full_text)} chars).")
        return full_text
    except Exception as e:
        print(f"❌ Error fetching transcript: {e}")
        return ""

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

def generate_style_profile(influencer_name: str, transcript_text: str):
    """
    Generate or append style analysis for an influencer.
    """
    prompt = f"""
    You are an expert linguistic profiler analyzing a YouTube/Instagram influencer.

    Extract a DEEP style profile JSON ONLY in this structure:

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

    # influencer_file = f"../influencer_styles/{influencer_name.lower().replace(' ', '_')}.json"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
    influencer_dir = os.path.join(project_root, "influencer_styles")
    os.makedirs(influencer_dir, exist_ok=True)
    influencer_file = os.path.join(
        influencer_dir, 
        f"{influencer_name.lower().replace(' ', '_')}.json")
    os.makedirs(os.path.dirname(influencer_file), exist_ok=True)

    # ✅ Check if file already exists
    if os.path.exists(influencer_file):
        with open(influencer_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    else:
        existing_data = {"name": influencer_name, "analyses": []}

    # ✅ Append new analysis
    existing_data["analyses"].append(new_style)

    # ✅ (Optional) Generate merged summary using GPT
    if len(existing_data["analyses"]) > 1:
        merge_prompt = f"""
        You are a summarizer agent.

        Combine these analyses into ONE deep persona style summary.

        Return JSON ONLY:

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
            "sentence_pattern": 0.0,
            "persona": 0.0
          }}
        }}

    ANALYSES TO MERGE:
        {json.dumps(existing_data["analyses"])}
        """
        merged = llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": merge_prompt}],
            temperature=0.3
        ).choices[0].message.content

        existing_data["merged_profile"] = safe_json_loads(merged)

    # ✅ Save file
    with open(influencer_file, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Updated style profile saved at: {influencer_file}")
    return existing_data


def main():
    print("🎥 === YouTube Style Profile Generator ===")
    influencer_name = input("Enter influencer name (e.g., Alex Hormozi): ").strip()
    youtube_url = input("Paste YouTube video URL: ").strip()

    transcript_text = get_youtube_transcript(youtube_url)

    if transcript_text:
        transcript_text = clean_transcript(transcript_text)
        style_data = generate_style_profile(influencer_name, transcript_text)

        print("\n🎯 Generated Style Summary:\n")
        print(json.dumps(style_data, indent=2, ensure_ascii=False))
    else:
        print("❌ No transcript found, skipping style generation.")


if __name__ == "__main__":
    main()

