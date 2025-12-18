import networkx as nx
from typing import List
from ..models.lesson import Lesson

def build_conflict_graph(lessons: List[Lesson]) -> nx.Graph:
    G = nx.Graph()
    for i, lesson in enumerate(lessons):
        G.add_node(i, lesson=lesson)

    for i in range(len(lessons)):
        for j in range(i + 1, len(lessons)):
            l1, l2 = lessons[i], lessons[j]
            if l1.class_name == l2.class_name or l1.teacher_name == l2.teacher_name:
                G.add_edge(i, j)
    return G