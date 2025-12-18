import matplotlib.pyplot as plt
import networkx as nx
from typing import List
from ..models.lesson import Lesson

def visualize_with_solution(
    G: nx.Graph,
    lessons: List[Lesson],
    solution_lessons: List[Lesson],
    figsize=(14, 10)
):
    """
    Draw the conflict graph with the optimal schedule highlighted in green.
    
    Parameters
    ----------
    G : nx.Graph
        Conflict graph (nodes = lesson indices, edges = conflicts)
    lessons : List[Lesson]
        List of all feasible lessons (index matches node ID in G)
    solution_lessons : List[Lesson]
        Subset of lessons in the optimal independent set
    figsize : tuple, optional
        Figure size (width, height)
    """
    plt.figure(figsize=figsize)
    
    # Use consistent layout
    pos = nx.spring_layout(G, seed=42, k=2.0)

    # Map lesson → index for fast lookup
    lesson_to_idx = {lesson: i for i, lesson in enumerate(lessons)}
    solution_nodes = {lesson_to_idx[l] for l in solution_lessons if l in lesson_to_idx}

    # Assign colors by class (for visual grouping)
    classes = sorted(set(lesson.class_name for lesson in lessons))
    class_colors = plt.cm.tab10(range(len(classes)))
    class_to_color = dict(zip(classes, class_colors))

    # Build node colors: green if selected, gray otherwise
    node_colors = []
    node_edge_colors = []  # outline = class color
    for i in G.nodes():
        if i in solution_nodes:
            node_colors.append("#4CAF50")    # green — scheduled
        else:
            node_colors.append("#E0E0E0")     # light gray — not scheduled
        cls = lessons[i].class_name
        node_edge_colors.append(class_to_color[cls])

    # Draw graph elements
    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        edgecolors=node_edge_colors,
        linewidths=2.0,
        node_size=800
    )
    nx.draw_networkx_edges(G, pos, alpha=0.5, width=0.8, edge_color="gray")
    
    # Short, readable labels: "10A\nMath/\nAli"
    labels = {}
    for i, lesson in enumerate(lessons):
        lines = [
            lesson.class_name[:5],
            f"{lesson.subject[:5]}/",
            lesson.teacher_name[:5]
        ]
        labels[i] = "\n".join(lines)
    nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight="bold")

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w',
               markerfacecolor="#4CAF50", markeredgecolor='k',
               markersize=10, label="Scheduled (Optimal)"),
        Line2D([0], [0], marker='o', color='w',
               markerfacecolor="#E0E0E0", markeredgecolor='k',
               markersize=10, label="Not scheduled"),
    ]
    for cls in classes:
        legend_elements.append(
            Line2D([0], [0], marker='o', color='w',
                   markerfacecolor='white',
                   markeredgecolor=class_to_color[cls],
                   markersize=8, label=f"Class {cls}")
        )
    
    plt.legend(handles=legend_elements, loc="upper right", frameon=True)
    plt.title("Conflict Graph with Optimal Schedule (Gurobi MWIS)", fontsize=14, pad=20)
    plt.axis("off")
    plt.tight_layout()
    plt.show()