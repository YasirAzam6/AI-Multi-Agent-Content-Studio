import os
import json
from Agents.director_graph import build_script_graph

if __name__ == "__main__":
    graph = build_script_graph()
    mermaid_code = graph.get_graph().draw_mermaid()
    print(mermaid_code)
    # print("🎬 Launching Multi-Agent Script Generation System...\n")

    # topic = "Why most entrepreneurs fail to scale their business"
    # influencer_name = "alex_hormozi"

    # project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # style_path = os.path.join(project_root, "Influencer_styles", f"{influencer_name}.json")
    # if not os.path.exists(style_path):
    #     raise FileNotFoundError(f"❌ Style file not found at {style_path}")

    # style_profile = json.load(open(style_path))
    # graph = build_script_graph()

    # # Initial state
    # initial_state = {
    #     "topic": topic,
    #     "influencer": influencer_name,
    #     "style_profile": style_profile
    # }

    # # Execute the workflow
    # result = graph.invoke(initial_state)

    # print("\n✅ Workflow Complete!\n")
    # print("📝 Final Script:\n")
    # print(result["edited_script"])
    # print("\n💬 Quality Report:\n")
    # print(result["quality_report"])

    # os.makedirs("../Data/outputs", exist_ok=True)
    # out_path = f"../Data/outputs/{influencer_name}_final_script.txt"
    # with open(out_path, "w", encoding="utf-8") as f:
    #     f.write(result["edited_script"])

    # print(f"\n📁 Saved script at: {out_path}")
