from langgraph.graph import StateGraph
from Agents.research_agent import ResearchAgent
from Agents.script_writer_agent import ScriptWriterAgent
from Agents.editor_agent import EditorAgent
from Agents.quality_agent import QualityAgent
from Agents.state_schema import ScriptState
from Agents.shortform_agent import ShortFormAgent
from Agents.postprocessor_agent import PostProcessorAgent

research = ResearchAgent()
writer = ScriptWriterAgent()
editor = EditorAgent()
quality = QualityAgent()
postprocessor = PostProcessorAgent()
shortform = ShortFormAgent()

def build_script_graph():
    # graph = StateGraph[ScriptState]()
    graph = StateGraph(ScriptState)

    graph.add_node(
        "research",
        research.run,
        input_keys=["topic"],
        output_keys=["research_notes"],
    )

    graph.add_node(
        "write_script",
        writer.run,
        input_keys=["topic", "research_notes"],
        output_keys=["draft_script"],
    )

    graph.add_node(
        "edit_script",
        editor.run,
        input_keys=["draft_script"],
        output_keys=["edited_script"],
    )

    graph.add_node(
        "shortform_script",
        shortform.run,
        input_keys=["topic", "style_profile", "duration"],
        output_keys=["draft_script"],
    )
    graph.add_node(
        "post_process",
        postprocessor.run,
        input_keys=["edited_script"],
        output_keys=["processed_script"],
    )

    graph.add_node(
        "evaluate_quality",
        quality.run,
        input_keys=["processed_script", "style_profile"],
        output_keys=["quality_report"],
    )

    #new node
    graph.add_node(
        "revise_script",
        writer.run,   # WriterAgent refines script
        input_keys=["edited_script", "revision_feedback", "style_profile"],
        output_keys=["draft_script"],
)

    def choose_writer(state):
        content_type = (state.get("content_type") or "youtube").lower()

        if content_type == "instagram":
            print("➡️ Routing to ShortFormAgent (Instagram mode)")
            return "shortform"   # branch label
        else:
            print("➡️ Routing to ScriptWriterAgent (YouTube mode)")
            return "writer"      # branch label
        
    def quality_check(state):
        report = state.get("quality_report", {})
        score = report.get("style_match_score", 1)
        # Prevent infinite loops
        revision_count = state.get("revision_count", 0)
        if revision_count >= 2:  # Max 2 revisions
            print(f"⚠️ Max revisions reached. Accepting output (score={score}).")
            return "finish"

        if score < 0.85:
            print(f"🔁 Quality low (score={score}). Sending back for refinement...")
            state["revision_feedback"] = report.get("feedback", "")
            state["revision_count"] = revision_count + 1
            return "revise"
        else:
            print(f"✅ Quality good (score={score}). Finishing pipeline.")
            return "finish"
        
    graph.set_entry_point("research")
    graph.add_conditional_edges(
        "research",
        choose_writer,
        {
            "shortform": "shortform_script",
            "writer": "write_script",
        },
    )
    graph.add_edge("write_script", "edit_script")
    graph.add_edge("shortform_script", "edit_script")
    graph.add_edge("edit_script", "post_process")
    graph.add_edge("post_process", "evaluate_quality")
    graph.add_edge("revise_script", "edit_script")
    # graph.set_finish_point("evaluate_quality")
    graph.add_conditional_edges(
    "evaluate_quality",
    quality_check,
    {
        "revise": "revise_script",
        "finish": "__end__"
    }
)
    return graph.compile()

#refine cycle will be: revise_script → edit_script → post_process → evaluate_quality → maybe revise again
