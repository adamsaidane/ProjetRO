import sys
import math
import random
import gurobipy as gp
from gurobipy import GRB

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QMessageBox, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QBrush, QFont


# -----------------------------
# Utils
# -----------------------------
def dist2(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy


# -----------------------------
# Solver: Weighted Independent Set + Budget
# Conflicts (edges) generated with distance <= R
# -----------------------------
class TelecomSolver:
    def __init__(self):
        self.coords = []     # [(x,y)]
        self.w = []          # weights (throughput)
        self.c = []          # costs
        self.R = 0.0
        self.B = 0.0

        self.edges = []
        self.selected = []
        self.obj_weight = 0.0
        self.obj_cost = 0.0

    @property
    def n(self):
        return len(self.coords)

    def update_instance(self, coords, w, c, R, B):
        self.coords = coords
        self.w = w
        self.c = c
        self.R = float(R)
        self.B = float(B)
        self._build_edges()

    def _build_edges(self):
        self.edges = []
        n = self.n
        if n <= 1:
            return
        R2 = self.R * self.R
        for i in range(n):
            for j in range(i + 1, n):
                if dist2(self.coords[i], self.coords[j]) <= R2:
                    self.edges.append((i, j))

    def solve(self):
        n = self.n
        self.selected = []
        self.obj_weight = 0.0
        self.obj_cost = 0.0
        if n <= 0:
            return

        m = gp.Model("Telecom_WIS_Budget")
        m.setParam("OutputFlag", 0)

        x = m.addVars(n, vtype=GRB.BINARY, name="x")

        # Max sum weights
        m.setObjective(gp.quicksum(self.w[i] * x[i] for i in range(n)), GRB.MAXIMIZE)

        # Conflicts
        m.addConstrs((x[i] + x[j] <= 1 for (i, j) in self.edges), name="no_interference")

        # Budget
        m.addConstr(gp.quicksum(self.c[i] * x[i] for i in range(n)) <= self.B, name="budget")

        m.optimize()

        if m.Status == GRB.OPTIMAL:
            self.selected = [i for i in range(n) if x[i].X > 0.5]
            self.obj_weight = sum(self.w[i] for i in self.selected)
            self.obj_cost = sum(self.c[i] for i in self.selected)

        m.dispose()


# -----------------------------
# Canvas
# -----------------------------
class TelecomCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.coords = []
        self.edges = []
        self.selected = set()
        self.R = 0.0
        self.setMinimumHeight(440)

    def update_view(self, coords, edges, selected, R):
        self.coords = coords
        self.edges = edges
        self.selected = set(selected)
        self.R = float(R)
        self.update()

    def _map_points(self, w, h):
        if not self.coords:
            return []

        pad = 60
        xs = [p[0] for p in self.coords]
        ys = [p[1] for p in self.coords]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)

        spanx = (maxx - minx) if maxx != minx else 1.0
        spany = (maxy - miny) if maxy != miny else 1.0

        avail_w = max(1, w - 2 * pad)
        avail_h = max(1, h - 2 * pad)
        s = min(avail_w / spanx, avail_h / spany)

        mapped = []
        for (x, y) in self.coords:
            X = pad + (x - minx) * s
            Y = pad + (y - miny) * s
            mapped.append((X, Y))
        return mapped

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h, QBrush(Qt.GlobalColor.white))

        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setFont(QFont("Arial", 12))
        painter.drawText(10, 28, "Réseau télécom : arêtes si distance ≤ R (conflits/interférences)")

        if not self.coords:
            painter.drawText(10, 60, "Ajoute des nœuds (x y w c), puis Preview / Solve.")
            return

        pts = self._map_points(w, h)

        painter.setPen(QPen(Qt.GlobalColor.darkGray, 2))
        for (i, j) in self.edges:
            x1, y1 = pts[i]
            x2, y2 = pts[j]
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        node_r = 18
        painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        for i, (X, Y) in enumerate(pts):
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.setBrush(QBrush(Qt.GlobalColor.green if i in self.selected else Qt.GlobalColor.lightGray))
            painter.drawEllipse(int(X - node_r), int(Y - node_r), 2 * node_r, 2 * node_r)

            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawText(int(X - 6), int(Y + 5), str(i))


# -----------------------------
# UI
# -----------------------------
class TelecomApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Projet 3 — Sélection de Canaux (Télécom) — Gurobi + PyQt6")
        self.resize(1200, 760)

        self.setFont(QFont("Arial", 11))

        self.solver = TelecomSolver()

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Left panel
        left_panel = QWidget()
        left = QVBoxLayout(left_panel)
        left_panel.setMinimumWidth(520)
        main_layout.addWidget(left_panel, 2)

        # Canvas
        self.canvas = TelecomCanvas()
        main_layout.addWidget(self.canvas, 3)

        # Input
        box = QGroupBox("Entrées")
        box_layout = QVBoxLayout(box)

        row = QHBoxLayout()
        row.addWidget(QLabel("Rayon d'interférence R:"))
        self.r_edit = QLineEdit("25")
        self.r_edit.setMaximumWidth(120)
        row.addWidget(self.r_edit)

        row.addSpacing(16)

        row.addWidget(QLabel("Budget B:"))
        self.b_edit = QLineEdit("40")
        self.b_edit.setMaximumWidth(120)
        row.addWidget(self.b_edit)

        row.addStretch(1)
        box_layout.addLayout(row)

        self.auto_budget = QCheckBox("Auto-budget (B = 0.5 * somme des coûts)")
        self.auto_budget.setChecked(False)
        box_layout.addWidget(self.auto_budget)

        box_layout.addWidget(QLabel("Nœuds (1 ligne = x y w c) : position, poids (débit), coût"))
        self.nodes_text = QTextEdit()
        self.nodes_text.setFont(QFont("Consolas", 11))
        self.nodes_text.setMinimumHeight(260)

        self.nodes_text.setText(
            "10 10  8  6\n"
            "15 12  6  5\n"
            "22 18  7  4\n"
            "35 20 10  7\n"
            "42 22  9  6\n"
            "55 10  5  3\n"
            "60 18  6  4\n"
            "70 25  8  5\n"
            "80 15  7  5\n"
            "90 22  9  6\n"
        )
        box_layout.addWidget(self.nodes_text)

        btn_row = QHBoxLayout()
        self.btn_preview = QPushButton("Preview (générer arêtes)")
        self.btn_solve = QPushButton("Solve (Gurobi)")
        self.btn_random = QPushButton("Random instance")
        for b in (self.btn_preview, self.btn_solve, self.btn_random):
            b.setMinimumHeight(38)
        btn_row.addWidget(self.btn_preview)
        btn_row.addWidget(self.btn_solve)
        btn_row.addWidget(self.btn_random)
        box_layout.addLayout(btn_row)

        left.addWidget(box)

        # Output
        out_box = QGroupBox("Résultats")
        out_layout = QVBoxLayout(out_box)

        self.result_label = QLabel("Clique Preview puis Solve.")
        self.result_label.setWordWrap(True)
        out_layout.addWidget(self.result_label)

        self.model_label = QLabel(
            "Modèle (PLNE) :\n"
            "- x_i ∈ {0,1}\n"
            "- max Σ w_i x_i\n"
            "- interférence : x_i + x_j ≤ 1 si distance(i,j) ≤ R\n"
            "- budget : Σ c_i x_i ≤ B"
        )
        self.model_label.setWordWrap(True)
        out_layout.addWidget(self.model_label)

        left.addWidget(out_box)
        left.addStretch(1)

        # signals
        self.btn_preview.clicked.connect(self.preview)
        self.btn_solve.clicked.connect(self.solve)
        self.btn_random.clicked.connect(self.random_instance)

        self.preview()

    def parse_nodes(self):
        lines = [ln.strip() for ln in self.nodes_text.toPlainText().splitlines() if ln.strip()]
        coords, w, c = [], [], []
        for k, ln in enumerate(lines, start=1):
            parts = ln.replace(",", " ").split()
            if len(parts) != 4:
                raise ValueError(f"Ligne {k}: format invalide. Attendu: x y w c")
            x = float(parts[0]); y = float(parts[1])
            wi = float(parts[2]); ci = float(parts[3])
            if wi < 0 or ci < 0:
                raise ValueError(f"Ligne {k}: w et c doivent être ≥ 0")
            coords.append((x, y))
            w.append(wi)
            c.append(ci)
        if not coords:
            raise ValueError("Aucun nœud saisi.")
        return coords, w, c

    def parse_params(self, costs_sum):
        try:
            R = float(self.r_edit.text().strip())
            if R < 0:
                raise ValueError
        except Exception:
            raise ValueError("Rayon R invalide (nombre ≥ 0).")

        if self.auto_budget.isChecked():
            B = 0.5 * costs_sum
            self.b_edit.setText(str(round(B, 2)))
        else:
            try:
                B = float(self.b_edit.text().strip())
                if B < 0:
                    raise ValueError
            except Exception:
                raise ValueError("Budget B invalide (nombre ≥ 0).")

        return R, B

    def preview(self):
        try:
            coords, w, c = self.parse_nodes()
            R, B = self.parse_params(sum(c))
            self.solver.update_instance(coords, w, c, R, B)
            self.canvas.update_view(self.solver.coords, self.solver.edges, [], self.solver.R)

            self.result_label.setText(
                f"Preview OK ✅\n"
                f"n = {self.solver.n}\n"
                f"|E| = {len(self.solver.edges)} (arêtes générées avec R={self.solver.R})\n"
                f"Budget B = {self.solver.B}"
            )
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def solve(self):
        try:
            coords, w, c = self.parse_nodes()
            R, B = self.parse_params(sum(c))
            self.solver.update_instance(coords, w, c, R, B)
            self.solver.solve()

            sel = self.solver.selected
            self.canvas.update_view(self.solver.coords, self.solver.edges, sel, self.solver.R)

            self.result_label.setText(
                f"Solution optimale ✅\n"
                f"Canaux activés = {sel}\n"
                f"Nombre activés = {len(sel)}\n"
                f"Débit total Σw_i x_i = {round(self.solver.obj_weight, 4)}\n"
                f"Coût total Σc_i x_i = {round(self.solver.obj_cost, 4)} ≤ B={self.solver.B}\n"
                f"|E| (interférences) = {len(self.solver.edges)} (R={self.solver.R})"
            )
        except gp.GurobiError as ge:
            QMessageBox.critical(self, "Gurobi error", str(ge))
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def random_instance(self):
        try:
            n = 18
            W, H = 100, 60
            coords, w, c = [], [], []
            for _ in range(n):
                coords.append((random.uniform(0, W), random.uniform(0, H)))
                w.append(random.randint(3, 12))
                c.append(random.randint(1, 8))

            # budget ~ 45% of sum(cost)
            B = 0.45 * sum(c)
            self.auto_budget.setChecked(False)
            self.b_edit.setText(str(round(B, 2)))

            self.nodes_text.setText(
                "\n".join(f"{round(x,2)} {round(y,2)} {wi} {ci}"
                          for (x, y), wi, ci in zip(coords, w, c))
            )
            self.preview()
        except Exception as e:
            QMessageBox.warning(self, "Erreur random", str(e))


def main():
    app = QApplication(sys.argv)
    win = TelecomApp()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
