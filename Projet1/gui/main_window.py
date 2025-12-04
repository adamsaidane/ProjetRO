from PyQt6.QtWidgets import (QMainWindow,QSplitter, QMessageBox, QDialog, QTableWidgetItem,
                             QPushButton, QWidget, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from Projet1.models.process import Process
from Projet1.models.system_config import SystemConfiguration
from Projet1.gui.dialogs.dependency_dialog import DependencyDialog
from Projet1.gui.dialogs.incompatibility_dialog import IncompatibilityDialog
from Projet1.gui.threads.optimization_thread import OptimizationThread
from Projet1.utils.example_data import create_example_processes

from Projet1.gui.components.left_panel import LeftPanel
from Projet1.gui.components.right_panel import RightPanel

class ProcessAllocationGUI(QMainWindow):
    """Interface principale de l'application"""
    PRIORITY_NAMES = {1: "Critique", 2: "Haute", 3: "Normale", 4: "Basse"}

    def __init__(self):
        super().__init__()
        self.processes = []
        self.optimization_thread = None
        self.results = None
        # Références pour results UI (déplacées vers RightPanel, mais accessibles via self.right_panel si needed)
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("Allocation Optimale de Processus - Recherche Opérationnelle")
        self.setGeometry(100, 100, 1600, 900)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Splitter pour diviser l'interface
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panneaux extraits
        left_panel = LeftPanel(self)
        right_panel = RightPanel(self)
        self.right_panel = right_panel

        # Ajouter au splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 1200])

        main_layout.addWidget(splitter)

    def add_process(self):
        """Ajoute un processus à la liste"""
        name = self.name_input.currentText().strip()
        if not name:
            QMessageBox.warning(self, "Erreur", "Le nom du processus ne peut pas être vide")
            return

        # Vérifier si le nom existe déjà
        if any(p.name == name for p in self.processes):
            QMessageBox.warning(self, "Erreur", f"Un processus nommé '{name}' existe déjà")
            return

        # Créer le processus
        process = Process(
            name=name,
            value=self.value_spin.value(),
            cpu=self.cpu_proc_spin.value(),
            ram=self.ram_proc_spin.value(),
            threads=self.threads_proc_spin.value(),
            priority=self.priority_combo.currentIndex() + 1,
            duration=self.duration_spin.value()
        )

        self.processes.append(process)
        self.update_process_table()

    def update_process_table(self):
        """Met à jour la table des processus"""
        self.process_table.setRowCount(len(self.processes))

        for i, proc in enumerate(self.processes):
            # Colonnes de base
            items = [
                QTableWidgetItem(proc.name),
                QTableWidgetItem(str(proc.value)),
                QTableWidgetItem(f"{proc.cpu:.1f}"),
                QTableWidgetItem(f"{proc.ram:.1f}"),
                QTableWidgetItem(str(proc.threads)),
                QTableWidgetItem(self.PRIORITY_NAMES[proc.priority]),
                QTableWidgetItem(str(proc.duration))
            ]

            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.process_table.setItem(i, col, item)

            # Dépendances
            dep_text = ", ".join(proc.dependencies) if proc.dependencies else "Aucune"
            dep_item = QTableWidgetItem(dep_text)
            dep_item.setForeground(QColor("#2980b9"))
            dep_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.process_table.setItem(i, 7, dep_item)

            # Incompatibilités
            incomp_text = ", ".join(proc.incompatible_with) if proc.incompatible_with else "Aucune"
            incomp_item = QTableWidgetItem(incomp_text)
            incomp_item.setForeground(QColor("#f39c12"))
            incomp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.process_table.setItem(i, 8, incomp_item)

            # Widget d'actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)

            # Bouton dépendances
            dep_btn = QPushButton("🔗")
            dep_btn.setToolTip("Gérer les dépendances")
            dep_btn.setFixedWidth(30)
            dep_btn.setProperty("process_index", i)
            dep_btn.clicked.connect(self.on_dependencies_clicked)
            dep_btn.setStyleSheet("padding: 4px; border-radius: 4px; background-color: #3498db;")
            actions_layout.addWidget(dep_btn)

            # Bouton incompatibilités
            incomp_btn = QPushButton("⚠️")
            incomp_btn.setToolTip("Gérer les incompatibilités")
            incomp_btn.setFixedWidth(30)
            incomp_btn.setProperty("process_index", i)
            incomp_btn.clicked.connect(self.on_incompatibilities_clicked)
            incomp_btn.setStyleSheet("padding: 4px; border-radius: 4px; background-color: #f39c12;")
            actions_layout.addWidget(incomp_btn)

            # Bouton supprimer
            delete_btn = QPushButton("❌")
            delete_btn.setToolTip("Supprimer")
            delete_btn.setFixedWidth(30)
            delete_btn.setProperty("process_index", i)
            delete_btn.clicked.connect(self.on_delete_clicked)
            delete_btn.setStyleSheet("padding: 4px; border-radius: 4px; background-color: #e74c3c;")
            actions_layout.addWidget(delete_btn)

            self.process_table.setCellWidget(i, 9, actions_widget)

    def on_dependencies_clicked(self):
        sender = self.sender()
        if sender:
            index = sender.property("process_index")
            self.manage_dependencies(index)

    def on_incompatibilities_clicked(self):
        sender = self.sender()
        if sender:
            index = sender.property("process_index")
            self.manage_incompatibilities(index)

    def on_delete_clicked(self):
        sender = self.sender()
        if sender:
            index = sender.property("process_index")
            self.delete_process(index)

    def manage_dependencies(self, index):
        if 0 <= index < len(self.processes):
            process = self.processes[index]
            dialog = DependencyDialog(
                process.name,
                self.processes,
                process.dependencies,
                self
            )

            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_dependencies = dialog.get_selected_dependencies()
                # Détecter conflits: noms présents à la fois en dépendances et incompatibilités
                conflicts = set(new_dependencies) & set(process.incompatible_with)
                if conflicts:
                    # Supprimer automatiquement les incompatibilités conflictuelles
                    for name in conflicts:
                        if name in process.incompatible_with:
                            process.incompatible_with.remove(name)
                        # Retirer la relation inverse
                        for other_proc in self.processes:
                            if other_proc.name == name and process.name in other_proc.incompatible_with:
                                other_proc.incompatible_with.remove(process.name)

                    QMessageBox.information(
                        self, "Résolution de conflit",
                        "Les incompatibilités suivantes ont été supprimées car vous avez défini une dépendance:\n"
                        + ", ".join(sorted(conflicts))
                    )

                process.dependencies = new_dependencies
                self.update_process_table()

    def manage_incompatibilities(self, index):
        if 0 <= index < len(self.processes):
            process = self.processes[index]
            dialog = IncompatibilityDialog(
                process.name,
                self.processes,
                process.incompatible_with,
                self
            )

            if dialog.exec() == QDialog.DialogCode.Accepted:
                old_incompatibilities = set(process.incompatible_with)
                new_incompatibilities = set(dialog.get_selected_incompatibilities())

                # Nouveaux ajoutés
                to_add = new_incompatibilities - old_incompatibilities
                # À retirer
                to_remove = old_incompatibilities - new_incompatibilities

                # Gérer ajouts: ajouter relation inverse et supprimer dépendances conflictuelles
                removed_dependencies = set()
                for incomp_name in to_add:
                    process.add_incompatibility(incomp_name)
                    for other_proc in self.processes:
                        if other_proc.name == incomp_name:
                            # Ajouter la relation inverse
                            other_proc.add_incompatibility(process.name)
                            # Si 'process' dépend de 'other_proc', supprimer cette dépendance
                            if incomp_name in process.dependencies:
                                process.dependencies.remove(incomp_name)
                                removed_dependencies.add(incomp_name)
                            # Si 'other_proc' dépend de 'process', supprimer cette dépendance
                            if process.name in other_proc.dependencies:
                                other_proc.dependencies.remove(process.name)
                                removed_dependencies.add(other_proc.name)

                # Gérer suppressions d'incompatibilités (retirer relation inverse)
                for incomp_name in to_remove:
                    if incomp_name in process.incompatible_with:
                        process.incompatible_with.remove(incomp_name)
                    for other_proc in self.processes:
                        if other_proc.name == incomp_name and process.name in other_proc.incompatible_with:
                            other_proc.incompatible_with.remove(process.name)

                if removed_dependencies:
                    QMessageBox.information(
                        self, "Résolution de conflit",
                        "Les dépendances conflictuelles suivantes ont été supprimées car vous avez défini une incompatibilité:\n"
                        + ", ".join(sorted(removed_dependencies))
                    )

                self.update_process_table()

    def delete_process(self, index):
        if 0 <= index < len(self.processes):
            process_to_delete = self.processes[index]

            # Supprimer les références dans les dépendances et incompatibilités des autres processus
            for proc in self.processes:
                if process_to_delete.name in proc.dependencies:
                    proc.dependencies.remove(process_to_delete.name)
                if process_to_delete.name in proc.incompatible_with:
                    proc.incompatible_with.remove(process_to_delete.name)

            del self.processes[index]
            self.update_process_table()

    def clear_all(self):
        reply = QMessageBox.question(
            self, 'Confirmation',
            'Voulez-vous vraiment effacer tous les processus ?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.processes.clear()
            self.update_process_table()

            # Nettoyer les cards résultats
            while self.right_panel.process_cards_layout.count():
                child = self.right_panel.process_cards_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Réinitialiser KPI et summary
            self.right_panel.kpi_cpu.setText("--")
            self.right_panel.kpi_ram.setText("--")
            self.right_panel.kpi_threads.setText("--")
            self.right_panel.kpi_value.setText("--")
            self.right_panel.results_summary.setText("")

    def load_example_data(self):
        self.processes = create_example_processes()
        self.update_process_table()
        QMessageBox.information(self, "Succès", "Données exemple chargées avec succès!")

    def optimize(self):
        if not self.processes:
            QMessageBox.warning(self, "Erreur", "Aucun processus à optimiser")
            return

        # Créer la configuration
        config = SystemConfiguration(
            cpu_max=self.cpu_max_spin.value(),
            ram_max=self.ram_max_spin.value(),
            threads_max=self.threads_max_spin.value(),
            time_max=self.time_max_spin.value() if self.time_max_spin.value() > 0 else None,
            min_critical=self.min_critical_spin.value(),
            max_low=self.max_low_spin.value() if self.max_low_spin.value() > 0 else None
        )

        # Créer et lancer le thread
        self.right_panel.progress_bar.setVisible(True)
        self.right_panel.progress_bar.setRange(0, 0)  # Mode indéterminé

        self.optimization_thread = OptimizationThread(self.processes, config)
        self.optimization_thread.finished.connect(self.on_optimization_finished)
        self.optimization_thread.error.connect(self.on_optimization_error)
        self.optimization_thread.start()

    def on_optimization_finished(self, results):
        """Callback quand l'optimisation est terminée"""
        self.right_panel.progress_bar.setVisible(False)
        self.results = results
        # Mettre à jour le résumé et KPI
        self.right_panel.display_results(results)

        # Mettre à jour les graphiques
        config = SystemConfiguration(
            cpu_max=self.cpu_max_spin.value(),
            ram_max=self.ram_max_spin.value(),
            threads_max=self.threads_max_spin.value()
        )
        self.right_panel.matplotlib_widget.plot_resource_usage(results, config)

        # Nettoyer et ajouter les cards de processus
        while self.right_panel.process_cards_layout.count():
            child = self.right_panel.process_cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if results.status == 'Optimal':
            for proc in results.selected_processes:
                card = self.right_panel.create_process_card(proc)
                self.right_panel.process_cards_layout.addWidget(card)
            self.right_panel.process_cards_layout.addStretch()

    def on_optimization_error(self, error_msg):
        """Callback en cas d'erreur"""
        self.right_panel.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Erreur d'optimisation", error_msg)