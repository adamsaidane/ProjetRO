from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSpinBox, QTableWidget, QTableWidgetItem, QGroupBox,
    QTextEdit, QFileDialog, QMessageBox, QSplitter, QProgressBar,
    QTabWidget, QCheckBox, QListWidget, QListWidgetItem, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import sys

from solver import PersonnelRoutingSolver, Solution
from data_manager import DataManager


class SolveThread(QThread):
    """Thread for running solver to keep GUI responsive"""
    finished = pyqtSignal(object)
    progress = pyqtSignal(str)

    def __init__(self, solver, distances, n_vehicles=1, service_times=None, demands=None, capacities=None):
        super().__init__()
        self.solver = solver
        self.distances = distances
        self.n_vehicles = n_vehicles
        self.service_times = service_times
        self.demands = demands
        self.capacities = capacities

    def run(self):
        try:
            self.progress.emit(f"Optimizing routes for {self.n_vehicles} sales reps...")
            solution = self.solver.solve_vrp(
                self.distances,
                n_vehicles=self.n_vehicles,
                vehicle_capacities=self.capacities,
                demands=self.demands,
                service_times=self.service_times
            )
            self.finished.emit(solution)
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")
            self.finished.emit(None)


class PlotCanvas(FigureCanvas):
    """Enhanced matplotlib canvas for plotting routes"""

    def __init__(self, parent=None, width=6, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#f8f9fa')
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#f8f9fa')
        self.data = None
        self.routes = None
        self.vehicle_colors = None

    def plot_data(self, data, routes=None):
        """Plot clients and routes with enhanced visualization"""
        self.ax.clear()
        self.ax.set_facecolor('#f8f9fa')
        self.data = data
        self.routes = routes

        # Generate distinct colors for each sales representative
        if routes:
            color_cycle = plt.cm.tab10(np.linspace(0, 1, len(routes)))
            self.vehicle_colors = color_cycle
        else:
            self.vehicle_colors = ['#4285F4']

        # Plot depot (office)
        depot = data["depot"]
        self.ax.plot(depot["x"], depot["y"], 'P', color='#000000', markersize=18,
                     label='Office (Depot)', zorder=10, markeredgewidth=2,
                     markeredgecolor='white', markerfacecolor='#4285F4')

        # Plot clients
        clients = data["clients"]
        for client in clients:
            x, y = client["x"], client["y"]
            client_id = client["id"]

            # Plot client point
            self.ax.plot(x, y, 'o', color='#EA4335', markersize=12,
                         alpha=0.9, zorder=5, markeredgecolor='white',
                         markeredgewidth=1.5)

            # Add client ID label
            self.ax.text(x, y + 2.2, f"{client_id}", fontsize=10,
                         ha='center', fontweight='bold', color='#202124',
                         bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                                   edgecolor='#DADCE0', alpha=0.9))

        # Plot routes if available
        if routes and len(routes) > 0:
            all_locations = [depot] + clients

            for vehicle_idx, route in enumerate(routes):
                if len(route) > 2:  # Not just depot->depot
                    route_coords = []
                    route_nodes = []
                    for node in route:
                        if node == 0:
                            route_coords.append((depot["x"], depot["y"]))
                            route_nodes.append("Depot")
                        else:
                            client = next(c for c in clients if c["id"] == node)
                            route_coords.append((client["x"], client["y"]))
                            route_nodes.append(f"C{node}")

                    x_coords, y_coords = zip(*route_coords)
                    color = self.vehicle_colors[vehicle_idx % len(self.vehicle_colors)]

                    # Plot route line with gradient effect
                    line = self.ax.plot(x_coords, y_coords, '-', color=color,
                                        linewidth=3, alpha=0.8,
                                        label=f'Rep {vehicle_idx + 1}', zorder=1,
                                        solid_capstyle='round')

                    # Add arrows at segments
                    arrow_length = 5
                    for i in range(len(route_coords) - 1):
                        x1, y1 = route_coords[i]
                        x2, y2 = route_coords[i + 1]
                        dx, dy = x2 - x1, y2 - y1
                        dist = np.sqrt(dx ** 2 + dy ** 2)

                        if dist > arrow_length * 2:  # Only add arrow if segment is long enough
                            # Place arrow at 70% of segment
                            arrow_x = x1 + dx * 0.7
                            arrow_y = y1 + dy * 0.7

                            # Normalize direction
                            dx_norm = dx / dist
                            dy_norm = dy / dist

                            self.ax.arrow(arrow_x, arrow_y,
                                          dx_norm * arrow_length * 0.3,
                                          dy_norm * arrow_length * 0.3,
                                          head_width=2.5, head_length=3,
                                          fc=color, ec=color, alpha=0.7,
                                          zorder=2, width=0.5)

        # Customize axes
        self.ax.set_xlabel('X Coordinate (km)', fontsize=11, fontweight='medium', color='#5F6368')
        self.ax.set_ylabel('Y Coordinate (km)', fontsize=11, fontweight='medium', color='#5F6368')
        self.ax.set_title('Sales Routes Visualization', fontsize=14, fontweight='bold',
                          color='#202124', pad=15)

        # Grid and frame
        self.ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#DADCE0')
        self.ax.spines['bottom'].set_color('#DADCE0')

        # Add legend
        if routes:
            self.ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1),
                           borderaxespad=0., framealpha=0.9,
                           facecolor='white', edgecolor='#DADCE0')

        self.fig.tight_layout(rect=[0, 0, 0.85, 1])  # Make space for legend
        self.draw()


class MainWindow(QMainWindow):
    """Main application window with modern design"""

    def __init__(self):
        super().__init__()
        self.solver = PersonnelRoutingSolver()
        self.data = None
        self.solution = None
        self.init_ui()
        self.load_sample_data()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Sales Route Optimizer")
        self.setGeometry(100, 100, 1400, 850)

        # Set window icon if available
        # self.setWindowIcon(QIcon('icon.png'))

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Left panel - Controls (Card-style)
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #DADCE0;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(12)

        # Header
        header_label = QLabel("Route Optimization")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_label.setStyleSheet("color: #1A73E8; padding-bottom: 10px;")
        left_layout.addWidget(header_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #DADCE0;")
        left_layout.addWidget(separator)

        # Problem setup card
        setup_group = QGroupBox("Problem Configuration")
        setup_group.setFont(QFont("Segoe UI", 10, QFont.Bold))
        setup_layout = QVBoxLayout()
        setup_layout.setSpacing(8)

        # Number of clients
        clients_layout = QHBoxLayout()
        clients_label = QLabel("Clients:")
        clients_label.setFont(QFont("Segoe UI", 9))
        clients_layout.addWidget(clients_label)
        self.n_clients_spin = QSpinBox()
        self.n_clients_spin.setRange(5, 40)
        self.n_clients_spin.setValue(15)
        self.n_clients_spin.setFont(QFont("Segoe UI", 9))
        self.n_clients_spin.valueChanged.connect(self.generate_new_data)
        clients_layout.addWidget(self.n_clients_spin)
        setup_layout.addLayout(clients_layout)

        # Number of sales representatives
        reps_layout = QHBoxLayout()
        reps_label = QLabel("Sales Reps:")
        reps_label.setFont(QFont("Segoe UI", 9))
        reps_layout.addWidget(reps_label)
        self.n_vehicles_spin = QSpinBox()
        self.n_vehicles_spin.setRange(1, 5)
        self.n_vehicles_spin.setValue(2)
        self.n_vehicles_spin.setFont(QFont("Segoe UI", 9))
        reps_layout.addWidget(self.n_vehicles_spin)
        setup_layout.addLayout(reps_layout)

        # Maximum clients per rep
        capacity_layout = QHBoxLayout()
        capacity_label = QLabel("Max Clients/Rep:")
        capacity_label.setFont(QFont("Segoe UI", 9))
        capacity_layout.addWidget(capacity_label)
        self.capacity_spin = QSpinBox()
        self.capacity_spin.setRange(1, 20)
        self.capacity_spin.setValue(8)
        self.capacity_spin.setFont(QFont("Segoe UI", 9))
        capacity_layout.addWidget(self.capacity_spin)
        setup_layout.addLayout(capacity_layout)

        # Checkbox for service times
        self.include_service_cb = QCheckBox("Include client service times")
        self.include_service_cb.setChecked(True)
        self.include_service_cb.setFont(QFont("Segoe UI", 9))
        setup_layout.addWidget(self.include_service_cb)

        # Solver time limit
        time_layout = QHBoxLayout()
        time_label = QLabel("Solver Time (s):")
        time_label.setFont(QFont("Segoe UI", 9))
        time_layout.addWidget(time_label)
        self.time_limit_spin = QSpinBox()
        self.time_limit_spin.setRange(5, 300)
        self.time_limit_spin.setValue(30)
        self.time_limit_spin.setFont(QFont("Segoe UI", 9))
        time_layout.addWidget(self.time_limit_spin)
        setup_layout.addLayout(time_layout)

        setup_group.setLayout(setup_layout)
        left_layout.addWidget(setup_group)

        # Action buttons
        button_style = """
            QPushButton {
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 10pt;
                border: none;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """

        self.generate_btn = QPushButton("Generate New Data")
        self.generate_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #34A853;
                color: white;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_new_data)
        left_layout.addWidget(self.generate_btn)

        self.solve_btn = QPushButton(" Optimize Routes")
        self.solve_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #1A73E8;
                color: white;
            }
        """)
        self.solve_btn.clicked.connect(self.solve_problem)
        left_layout.addWidget(self.solve_btn)

        # Data management buttons
        data_layout = QHBoxLayout()
        self.load_btn = QPushButton(" Load")
        self.load_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #5F6368;
                color: white;
            }
        """)
        self.load_btn.clicked.connect(self.load_data)
        data_layout.addWidget(self.load_btn)

        self.save_btn = QPushButton(" Save")
        self.save_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #5F6368;
                color: white;
            }
        """)
        self.save_btn.clicked.connect(self.save_data)
        data_layout.addWidget(self.save_btn)
        left_layout.addLayout(data_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #DADCE0;
                border-radius: 4px;
                text-align: center;
                background-color: #F8F9FA;
            }
            QProgressBar::chunk {
                background-color: #1A73E8;
                border-radius: 4px;
            }
        """)
        left_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready to optimize")
        self.status_label.setFont(QFont("Segoe UI", 9))
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #F8F9FA;
                border-radius: 4px;
                border: 1px solid #E8EAED;
                color: #5F6368;
            }
        """)
        left_layout.addWidget(self.status_label)

        # Solution summary card
        solution_group = QGroupBox("Solution Summary")
        solution_group.setFont(QFont("Segoe UI", 10, QFont.Bold))
        solution_layout = QVBoxLayout()

        self.solution_text = QTextEdit()
        self.solution_text.setReadOnly(True)
        self.solution_text.setMaximumHeight(180)
        self.solution_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #DADCE0;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 9pt;
            }
        """)
        solution_layout.addWidget(self.solution_text)

        self.export_btn = QPushButton(" Export Solution")
        self.export_btn.setStyleSheet(button_style + """
            QPushButton {
                background-color: #FBBC05;
                color: #202124;
            }
        """)
        self.export_btn.clicked.connect(self.export_solution)
        self.export_btn.setEnabled(False)
        solution_layout.addWidget(self.export_btn)

        solution_group.setLayout(solution_layout)
        left_layout.addWidget(solution_group)

        left_layout.addStretch()

        # Right panel - Visualization
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #DADCE0;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(10)

        # Tab widget for different views
        tabs = QTabWidget()
        tabs.setFont(QFont("Segoe UI", 9))
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #DADCE0;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 8px 16px;
                background-color: #F8F9FA;
                border: 1px solid #DADCE0;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #1A73E8;
            }
        """)

        # Route Visualization tab
        map_tab = QWidget()
        map_layout = QVBoxLayout(map_tab)
        map_layout.setContentsMargins(5, 5, 5, 5)
        self.plot_canvas = PlotCanvas(self, width=7, height=5.5)
        map_layout.addWidget(self.plot_canvas)
        tabs.addTab(map_tab, "📍 Route Map")

        # Clients Information tab
        clients_tab = QWidget()
        clients_layout = QVBoxLayout(clients_tab)
        clients_layout.setContentsMargins(5, 5, 5, 5)

        # Clients table
        self.clients_table = QTableWidget()
        self.clients_table.setAlternatingRowColors(True)
        self.clients_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #DADCE0;
                border-radius: 4px;
                gridline-color: #E8EAED;
            }
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        clients_layout.addWidget(self.clients_table)
        tabs.addTab(clients_tab, "👥 Clients")

        # Routes Details tab
        routes_tab = QWidget()
        routes_layout = QVBoxLayout(routes_tab)
        routes_layout.setContentsMargins(5, 5, 5, 5)

        self.routes_list = QListWidget()
        self.routes_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #DADCE0;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #E8EAED;
            }
            QListWidget::item:selected {
                background-color: #E8F0FE;
                color: #202124;
            }
        """)
        routes_layout.addWidget(self.routes_list)
        tabs.addTab(routes_tab, "🗺️ Route Details")

        right_layout.addWidget(tabs)

        # Add panels to main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 1050])
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E8EAED;
                width: 2px;
            }
        """)
        main_layout.addWidget(splitter)

        # Apply main window stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F9FA;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #DADCE0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: #5F6368;
            }
            QLabel {
                color: #202124;
            }
            QSpinBox {
                padding: 6px;
                border: 1px solid #DADCE0;
                border-radius: 4px;
                background-color: white;
            }
            QSpinBox:hover {
                border-color: #C4C7C5;
            }
            QCheckBox {
                spacing: 8px;
                color: #5F6368;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #1A73E8;
                border: 1px solid #1A73E8;
            }
        """)

    def load_sample_data(self):
        """Load sample data on startup"""
        n_clients = self.n_clients_spin.value()
        self.data = DataManager.generate_sample_data(n_clients)
        self.update_data_display()
        self.status_label.setText("✅ Sample data loaded")

    def generate_new_data(self):
        """Generate new random data"""
        n_clients = self.n_clients_spin.value()
        self.data = DataManager.generate_sample_data(n_clients)
        self.update_data_display()
        self.status_label.setText(f"✅ Generated data for {n_clients} clients")
        self.solution = None
        self.solution_text.clear()
        self.export_btn.setEnabled(False)

    def update_data_display(self):
        """Update all data displays"""
        if self.data:
            # Update plot
            self.plot_canvas.plot_data(self.data)

            # Update clients table
            clients = self.data["clients"]
            self.clients_table.setRowCount(len(clients))
            self.clients_table.setColumnCount(5)
            self.clients_table.setHorizontalHeaderLabels(["ID", "X (km)", "Y (km)", "Service Time", "Demand"])

            # Set column widths
            header = self.clients_table.horizontalHeader()
            header.setStretchLastSection(True)

            for i, client in enumerate(clients):
                # ID
                id_item = QTableWidgetItem(f"C{client['id']}")
                id_item.setTextAlignment(Qt.AlignCenter)
                id_item.setFont(QFont("Segoe UI", 9, QFont.Bold))
                self.clients_table.setItem(i, 0, id_item)

                # X coordinate
                x_item = QTableWidgetItem(f"{client['x']:.1f}")
                x_item.setTextAlignment(Qt.AlignCenter)
                self.clients_table.setItem(i, 1, x_item)

                # Y coordinate
                y_item = QTableWidgetItem(f"{client['y']:.1f}")
                y_item.setTextAlignment(Qt.AlignCenter)
                self.clients_table.setItem(i, 2, y_item)

                # Service time
                time_item = QTableWidgetItem(f"{client.get('service_time', 30)} min")
                time_item.setTextAlignment(Qt.AlignCenter)
                self.clients_table.setItem(i, 3, time_item)

                # Demand (always 1)
                demand_item = QTableWidgetItem("1")
                demand_item.setTextAlignment(Qt.AlignCenter)
                self.clients_table.setItem(i, 4, demand_item)

            # Clear routes list
            self.routes_list.clear()

    def solve_problem(self):
        """Solve the optimization problem"""
        if not self.data:
            QMessageBox.warning(self, "Warning", "Please load or generate data first!")
            return

        # Update solver parameters
        self.solver.time_limit = self.time_limit_spin.value()
        n_vehicles = self.n_vehicles_spin.value()

        # Prepare data
        distances = self.data["distance_matrix"]

        # Get service times if checkbox is checked
        service_times = None
        if self.include_service_cb.isChecked():
            service_times = [0]  # Depot has 0 service time
            service_times.extend([c.get("service_time", 30) for c in self.data["clients"]])

        # Get demands from clients (each client has demand = 1)
        demands = [0]  # Depot has 0 demand
        demands.extend([1 for _ in self.data["clients"]])  # Each client has demand 1

        # Set capacities (max clients per sales rep)
        capacity = self.capacity_spin.value()
        capacities = [capacity] * n_vehicles

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(20)
        self.status_label.setText("🔄 Setting up optimization problem...")
        self.solve_btn.setEnabled(False)

        # Create and start solver thread
        self.solve_thread = SolveThread(
            self.solver, distances, n_vehicles,
            service_times, demands, capacities
        )
        self.solve_thread.finished.connect(self.on_solve_finished)
        self.solve_thread.progress.connect(self.on_solve_progress)
        self.solve_thread.start()

    def on_solve_progress(self, message):
        """Update progress during solving"""
        self.status_label.setText(message)
        if "Solving" in message:
            self.progress_bar.setValue(50)
        elif "Optimizing" in message:
            self.progress_bar.setValue(75)

    def on_solve_finished(self, solution):
        """Handle solver completion"""
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        self.solve_btn.setEnabled(True)

        if solution and solution.routes:
            self.solution = solution
            self.display_solution(solution)
            self.display_routes_list(solution)
            self.export_btn.setEnabled(True)

            # Update plot with routes
            self.plot_canvas.plot_data(self.data, solution.routes)

            # Show success message
            hours = solution.total_time // 60
            minutes = solution.total_time % 60
            time_str = f"{hours}h {minutes}min" if hours > 0 else f"{minutes}min"

            self.status_label.setText(
                f"✅ Optimized! {len(solution.routes)} reps, {solution.total_distance:.1f} km, {time_str}")
        else:
            QMessageBox.critical(self, "Error", "Failed to find a solution! Try adjusting parameters.")
            self.status_label.setText("❌ Optimization failed")

    def display_solution(self, solution: Solution):
        """Display solution in text box"""
        # Calculate time breakdown
        hours = solution.total_time // 60
        minutes = solution.total_time % 60
        time_str = f"{hours}h {minutes}min" if hours > 0 else f"{minutes}min"

        travel_hours = solution.travel_time // 60
        travel_minutes = solution.travel_time % 60
        travel_str = f"{travel_hours}h {travel_minutes}min" if travel_hours > 0 else f"{travel_minutes}min"

        service_hours = solution.service_time // 60
        service_minutes = solution.service_time % 60
        service_str = f"{service_hours}h {service_minutes}min" if service_hours > 0 else f"{service_minutes}min"

        text = " SOLUTION SUMMARY\n"
        text += "══════════════════════\n\n"

        text += f"Sales Representatives: {len(solution.routes)}\n"
        text += f"Total Distance: {solution.total_distance:.1f} km\n"
        text += f"Total Time: {time_str}\n"
        text += f"  • Travel: {travel_str}\n"
        text += f"  • Service: {service_str}\n"
        text += f"Solver Time: {solution.solve_time:.1f}s\n"

        if solution.routes:
            text += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
            text += "ROUTE DETAILS\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

            for i, route in enumerate(solution.routes):
                clients_count = len(route) - 2  # Exclude depot at start and end
                text += f"Rep {i + 1}: {clients_count} clients\n"
                text += "  Route: " + " → ".join(
                    ["Office" if node == 0 else f"C{node}" for node in route]
                ) + "\n\n"

        self.solution_text.setText(text)

    def display_routes_list(self, solution: Solution):
        """Display routes in the list widget"""
        self.routes_list.clear()

        if solution.routes:
            for i, route in enumerate(solution.routes):
                # Count clients in this route
                clients_in_route = [node for node in route if node != 0]

                item_text = f"👤 Sales Representative {i + 1}\n"
                item_text += f"   📍 Clients: {len(clients_in_route)}\n"
                item_text += f"   🛣️  Route: Office → "
                item_text += " → ".join(f"C{node}" for node in route[1:-1])
                item_text += " → Office"

                item = QListWidgetItem(item_text)
                item.setFont(QFont("Segoe UI", 9))

                # Set alternating background colors
                if i % 2 == 0:
                    item.setBackground(QColor(248, 249, 250))
                else:
                    item.setBackground(QColor(255, 255, 255))

                self.routes_list.addItem(item)

    def load_data(self):
        """Load data from file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Data", "", "JSON Files (*.json)"
        )
        if filename:
            try:
                self.data = DataManager.load_from_json(filename)
                self.update_data_display()
                self.status_label.setText(f"✅ Loaded data from {filename.split('/')[-1]}")
                self.solution = None
                self.solution_text.clear()
                self.export_btn.setEnabled(False)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")

    def save_data(self):
        """Save data to file"""
        if not self.data:
            QMessageBox.warning(self, "Warning", "No data to save!")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Data", "sales_routing_data.json", "JSON Files (*.json)"
        )
        if filename:
            try:
                DataManager.save_to_json(self.data, filename)
                self.status_label.setText(f"✅ Data saved to {filename.split('/')[-1]}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")

    def export_solution(self):
        """Export solution to file"""
        if not self.solution:
            QMessageBox.warning(self, "Warning", "No solution to export!")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Solution", "solution_report.txt", "Text Files (*.txt)"
        )
        if filename:
            try:
                self.solver.save_solution(filename)
                self.status_label.setText(f"✅ Solution exported to {filename.split('/')[-1]}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")