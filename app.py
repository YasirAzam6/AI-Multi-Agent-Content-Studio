import streamlit as st
import os
import json
from Agents.director_graph import build_script_graph
from Scripts.youtube_influencer_profile import generate_influencer_style
from Scripts.instagram_influencer_profile import generate_IG_style_profile
from Agents.voice_calibration import VoiceCalibrationAgent
import re
from dotenv import load_dotenv

load_dotenv()  # <-- this loads .env from same folder as app.py

print("DEBUG API KEY:", os.getenv("OPENAI_API_KEY"))

# ---------- Configuration ----------
st.set_page_config(page_title="AI Content Studio", page_icon="🎬", layout="wide")

# ---------- Utility Functions ----------
def get_project_root():
    return os.path.dirname(os.path.abspath(__file__))

def remove_influencer(text: str) -> str:
    # \b ensures it matches 'Influencer' as a whole word
    return re.sub(r'\bInfluencer\b', '', text, flags=re.IGNORECASE).strip()

def load_influencers():
    """Lists all influencer profiles (works on both local and server)"""
    project_root = get_project_root()
    styles_path = os.path.join(project_root, "influencer_styles")

    if not os.path.exists(styles_path):
        st.error(f"❌ 'influencer_styles' folder not found.\nExpected at: {styles_path}")
        return []
    return [os.path.splitext(f)[0] for f in os.listdir(styles_path) if f.endswith(".json")]

def load_style_profile(name):
    project_root = get_project_root()
    style_path = os.path.join(project_root, "influencer_styles", f"{name}.json")
    if not os.path.exists(style_path):
        st.error(f"❌ Style file not found at: {style_path}")
        st.stop()
    with open(style_path, "r", encoding="utf-8") as f:
        return json.load(f)
    

def load_IG_influencers():
    """Lists all influencer profiles (works on both local and server)"""
    project_root = get_project_root()
    styles_path = os.path.join(project_root, "IG_influencer_styles")

    if not os.path.exists(styles_path):
        st.error(f"❌ 'IG_influencer_styles' folder not found.\nExpected at: {styles_path}")
        return []
    return [os.path.splitext(f)[0] for f in os.listdir(styles_path) if f.endswith(".json")]

def load_IG_style_profile(name):
    project_root = get_project_root()
    style_path = os.path.join(project_root, "IG_influencer_styles", f"{name}.json")
    if not os.path.exists(style_path):
        st.error(f"❌ Style file not found at: {style_path}")
        st.stop()
    with open(style_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_new_style(name, data):
    """Save a new influencer style JSON"""
    project_root = get_project_root()
    styles_path = os.path.join(project_root, "influencer_styles")
    os.makedirs(styles_path, exist_ok=True)
    path = os.path.join(styles_path, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return path

# ---------- Dummy Function (replace with your actual logic) ----------
def process_youtube_video(video_path, influencer_profile):
    """
    Process the uploaded video (generate transcript, mimic influencer style, etc.)
    """
    # Here you could:
    # 1. Transcribe video using OpenAI Whisper
    # 2. Analyze tone/style using influencer_profile
    # 3. Generate summary, insights, or rewritten content
    return {
        "transcript": "This is a sample transcript generated for demonstration.",
        "styled_output": f"Influencer '{influencer_profile['name']}' style applied successfully."
    }

# ---------- Tabs ----------
st.title("🎬 AI Multi-Agent Content Studio")
tabs = st.tabs(["🧠 Script Generator", "🎥 YouTube Influencer Profile Enhancer", "🎥 Instagram Influencer Profile Enhancer"])


# =====================================================
# 🧠 TAB 1: Script Generator
# =====================================================
with tabs[0]:
    st.caption("Generate YouTube and Instagram scripts in your favorite influencer’s style — powered by LangGraph Agents.")

    # --- Step 1: Select Content Type FIRST ---
    content_type = st.selectbox(
        "🎥 Content Type",
        ["YouTube (Long-form)", "Instagram (Short-form)"],
        key="tab1_content_type_selector"
    )

    # Determine platform key
    content_key = "youtube" if "youtube" in content_type.lower() else "instagram"

    # --- Step 2: Load influencers dynamically based on type ---
    if content_key == "youtube":
        influencer_list = load_influencers()
    else:
        influencer_list = load_IG_influencers()

    influencer_name = st.selectbox(
        f"Choose {content_key.capitalize()} Influencer Style",
        influencer_list,
        key=f"tab1_{content_key}_influencer_selector"
    )

    # --- Step 4: Duration auto adjustment ---
    if "duration_tab0" not in st.session_state:
        st.session_state["duration_tab0"] = 180

    default_duration = 60 if content_key == "instagram" else 180

    if st.session_state.get("last_content_type_tab0") != content_key:
        st.session_state["duration_tab0"] = default_duration
        st.session_state["last_content_type_tab0"] = content_key

    duration = st.number_input(
        "Video Length (seconds)",
        min_value=30,
        max_value=900,
        value=st.session_state["duration_tab0"],
        step=30,
        key="tab1_duration_input"
    )

    # --- Step 3: Enter topic ---
    topic = st.text_input(
        "Enter Topic",
        placeholder="e.g., How to build a business that scales",
        key="tab1_topic_input"
    )

   # ================================
    # OPTIONAL VOICE CALIBRATION
    # ================================
    st.subheader("📝 Optional: Upload Writing Samples for Voice Calibration")

    uploaded_samples = st.file_uploader(
        "Upload 1–3 text files (your own writing)",
        type=["txt"],
        accept_multiple_files=True,
        key="creator_samples_uploader"
    )

    creator_style = None
    vc_agent = VoiceCalibrationAgent()

    if uploaded_samples:
        sample_texts = [file.read().decode("utf-8") for file in uploaded_samples]

        if st.button("Analyze My Writing Style", use_container_width=True):
            with st.spinner("Analyzing your writing style..."):
                creator_style = vc_agent.analyze_creator_style(sample_texts)
            st.success("🎯 Your writing style has been extracted!")
            st.json(creator_style)

    # ================================
    # GENERATE SCRIPT
    # ================================
    if st.button("🚀 Generate Script", use_container_width=True, key="tab1_generate_button"):
        if not topic.strip():
            st.warning("Please enter a topic.")
            st.stop()

        # Load influencer style
        if content_key == "youtube":
            style_profile = load_style_profile(influencer_name)
        else:
            style_profile = load_IG_style_profile(influencer_name)

        # Merge with creator style (optional)
        if creator_style:
            st.info("🔀 Merging your writing style with influencer style...")
            with st.spinner("Calibrating combined writing voice..."):
                influencer_style = style_profile.get("merged_profile") or style_profile.get("style_profile") or style_profile
                style_profile = vc_agent.merge_styles(creator_style, influencer_style)
            merged_name = f"{influencer_name}_personalized"
            save_path = save_new_style(merged_name, style_profile)
            st.success(f"🎉 Voice Calibration Applied! Saved as: {merged_name}")


        st.info(f"🎯 Generating {content_key.capitalize()} script for **{influencer_name}** on topic: *{topic}* ...")

        # Build the LangGraph pipeline
        graph = build_script_graph()
        state = {
            "topic": topic,
            "influencer": influencer_name,
            "style_profile": style_profile,
            "duration": duration,
            "content_type": content_key
        }

        with st.spinner("Agents are collaborating... please wait ⏳"):
            

            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulated progress (LangGraph doesn't expose real-time progress easily)
            import time
            for i in range(100):
                progress_bar.progress(i + 1)
                if i < 20:
                    status_text.text("🔍 Researching topic...")
                elif i < 50:
                    status_text.text("✍️ Writing draft script...")
                elif i < 70:
                    status_text.text("🧹 Editing for clarity...")
                elif i < 90:
                    status_text.text("🧠 Evaluating quality...")
                else:
                    status_text.text("✅ Finalizing...")
                time.sleep(0.05)

            result = graph.invoke(state)
            

        # --- Display results ---
        st.success("✅ Script Generation Complete!")
        st.subheader("🧾 Final Script")
        st.text_area(
            "Generated Script", 
            remove_influencer(result["processed_script"]), 
            height=400, 
            key="tab1_final_script_box")
        st.subheader("💬 Quality Report")
        st.json(result["quality_report"])

# =====================================================
# 🎥 TAB 2: YouTube Analyzer
# =====================================================
with tabs[1]:
    st.caption("Upload a video to add it to a chosen influencer profile.")

    uploaded_file = st.file_uploader("📤 Upload YouTube Video (MP4)", type=["mp4", "mov", "mkv"])

    influencer_list = load_influencers()
    mode = st.radio("Select Mode", ["Use Existing Influencer", "Create New Influencer"], key="youtube_mode")

    if mode == "Use Existing Influencer":
        influencer_name = st.selectbox("Choose Influencer Style", influencer_list, key="youtube_influencer")
        style_profile = load_style_profile(influencer_name)
    else:
        new_name = st.text_input("New Influencer Name", key="youtube_new_influencer_name")
        
    if uploaded_file and st.button("🚀 Process Video", use_container_width=True):
        temp_path = os.path.join(get_project_root(), "temp_video.mp4")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())

        st.info("⚙️ Processing video with influencer style...")
        with st.spinner("Analyzing video and applying style..."):
            result = generate_influencer_style(
                influencer_name if mode == "Use Existing Influencer" else new_name,
                temp_path
                )

        st.success("✅ Video processed successfully!")
        st.subheader("🗒️ Profile Created Successfully.")
        # st.text_area("Video Transcript", result["transcript"], height=300)
        # st.subheader("🎙️ Styled Output")
        # st.text_area("Influencer Styled Output", result["styled_output"], height=200)

        # Optionally delete file
        os.remove(temp_path)

# =====================================================
# 🎥 TAB 2: Instagram Analyzer
# =====================================================
with tabs[2]:
    st.caption("Upload a video to add it to a chosen influencer profile.")

    uploaded_file = st.file_uploader("📤 Upload Instagram Video (MP4)", type=["mp4", "mov", "mkv"])

    influencer_list = load_IG_influencers()
    mode = st.radio("Select Mode", ["Use Existing Influencer", "Create New Influencer"], key="insta_mode")

    if mode == "Use Existing Influencer":
        influencer_name = st.selectbox("Choose Influencer Style", influencer_list, key="insta_influencer")
        style_profile = load_IG_style_profile(influencer_name)
    else:
        new_name = st.text_input("New Influencer Name", key="insta_new_influencer_name")
        
    if uploaded_file and st.button("🚀 Process Video", use_container_width=True):
        temp_path = os.path.join(get_project_root(), "temp_video.mp4")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())

        st.info("⚙️ Processing video with influencer style...")
        with st.spinner("Analyzing video and applying style..."):
            result = generate_IG_style_profile(
                influencer_name if mode == "Use Existing Influencer" else new_name,
                temp_path
                )

        st.success("✅ Video processed successfully!")
        st.subheader("🗒️ Profile Created Successfully.")
        # st.text_area("Video Transcript", result["transcript"], height=300)
        # st.subheader("🎙️ Styled Output")
        # st.text_area("Influencer Styled Output", result["styled_output"], height=200)

        # Optionally delete file
        os.remove(temp_path)
