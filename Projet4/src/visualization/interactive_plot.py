from pyvis.network import Network
import webbrowser
import os
from typing import List
import networkx as nx
from ..models.lesson import Lesson

def visualize_conflict_graph_interactive(
    G: nx.Graph,
    lessons: List[Lesson],
    output_file: str = "schedule_conflicts.html"
):
    """
    Generate an interactive HTML graph using pyvis.
    Opens the file in the default browser (if possible).
    
    Parameters
    ----------
    G : nx.Graph
        Conflict graph
    lessons : List[Lesson]
        List of lessons (index matches node ID)
    output_file : str
        Output HTML filename
    """
    net = Network(
        height="750px",
        width="100%",
        bgcolor="#ffffff",
        font_color="black",
        notebook=False  # ← critical for standalone scripts
    )
    
    # Physics simulation settings
    net.barnes_hut(
        gravity=-80000,
        central_gravity=0.3,
        spring_length=100,
        spring_strength=0.05,
        damping=0.09
    )

    # Assign colors by class
    classes = sorted(set(lesson.class_name for lesson in lessons))
    palette = [
        "#FF6F61", "#6B5B95", "#88B04B", "#F7CAC9", "#92A8D1",
        "#DE5D83", "#B565A7", "#009B77", "#DD4124", "#00A8CC",
        "#F4A261", "#2A9D8F", "#E76F51", "#264653"
    ]
    class_to_color = {cls: palette[i % len(palette)] for i, cls in enumerate(classes)}

    # Add nodes with tooltips
    for i in G.nodes():
        lesson = lessons[i]
        title = (
            f"<b>Lesson ID:</b> {i}<br>"
            f"<b>Class:</b> {lesson.class_name}<br>"
            f"<b>Subject:</b> {lesson.subject}<br>"
            f"<b>Teacher:</b> {lesson.teacher_name}"
        )
        # Short label for node: "10A/Math/Ali"
        label = f"{lesson.class_name[:5]}/{lesson.subject[:6]}/{lesson.teacher_name[:5]}"
        net.add_node(
            i,
            label=label,
            title=title,
            color=class_to_color[lesson.class_name],
            size=25
        )

    # Add edges (conflicts)
    for u, v in G.edges():
        net.add_edge(u, v, color="gray", width=1, smooth={"type": "continuous"})

    # Improve readability & interaction
    net.set_options("""
    var options = {
      "nodes": {
        "font": {
          "size": 14,
          "face": "verdana"
        },
        "scaling": {
          "label": {
            "enabled": false
          }
        }
      },
      "edges": {
        "smooth": {
          "type": "continuous",
          "forceDirection": "none",
          "roundness": 0.6
        }
      },
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -80000,
          "centralGravity": 0.3,
          "springLength": 100,
          "springConstant": 0.04,
          "damping": 0.09
        }
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 200
      }
    }
    """)

    # Save and try to open
    try:
        net.write_html(output_file, open_browser=False)
        abs_path = os.path.abspath(output_file)
        print(f"✅ Interactive graph saved to: {abs_path}")

        # Attempt to open in browser (non-blocking)
        try:
            webbrowser.open("file://" + abs_path)
            print("🌐 Opening in default browser...")
        except Exception as e:
            print(f"⚠️ Could not open browser (non-critical): {e}")
            print("👉 You can open the file manually.")
    except Exception as e:
        raise RuntimeError(f"Failed to generate interactive graph: {e}")