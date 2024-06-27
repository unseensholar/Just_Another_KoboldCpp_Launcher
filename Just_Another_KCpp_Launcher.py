from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QComboBox, QPushButton, QTextEdit, QMessageBox, QLineEdit, QFormLayout,
    QSlider, QCheckBox, QTabWidget, QGridLayout, QAction, QFileDialog, QHBoxLayout, QInputDialog
)

from PyQt5.QtCore import Qt

import sys
import os
import subprocess
import json

# Default configuration file name
CONFIG_FILE = 'config.json'

class ModelLoader(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Just Another KCpp Launcher")
        self.setGeometry(100, 100, 600, 500)

        self.setStyleSheet("background-color: #2C2F33; color: white;")

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        
        self.layout = QVBoxLayout(self.main_widget)

        self.tab_widget = QTabWidget(self)
        self.layout.addWidget(self.tab_widget)

        self.favorites_layout = QVBoxLayout()
        self.favorites_widget = QWidget()
        self.favorites_widget.setLayout(self.favorites_layout)
        self.layout.addWidget(self.favorites_widget)

        self.setup_model_tab()
        self.setup_hardware_tab()
        
        self.config = {}
        self.favorites = []  # List to store favorite models
        self.load_config()  # Load default settings from config file
        self.update_favorites_layout()  # Update the favorites layout
        self.update_model_list()  # Populate the model list when the app starts

    def setup_model_tab(self):
        self.model_tab = QWidget()
        self.tab_widget.addTab(self.model_tab, "Quick Launch")
        
        self.model_layout = QVBoxLayout(self.model_tab)

        self.model_dir_input = QLineEdit(self)
        self.model_dir_input.setPlaceholderText("Model Folder Location")
        self.model_layout.addWidget(self.model_dir_input)
        
        self.model_dir_button = QPushButton("Select Model Root Directory", self)
        self.model_dir_button.clicked.connect(self.select_model_directory)
        self.model_layout.addWidget(self.model_dir_button)
        
        self.kcpp_dir_input = QLineEdit(self)
        self.kcpp_dir_input.setPlaceholderText("KoboldCpp Location")
        self.model_layout.addWidget(self.kcpp_dir_input)
        
        self.kcpp_dir_button = QPushButton("Select KoboldCpp Executable", self)
        self.kcpp_dir_button.clicked.connect(self.select_kcpp_directory)
        self.model_layout.addWidget(self.kcpp_dir_button)
        
        self.model_combo = QComboBox(self)
        self.model_layout.addWidget(self.model_combo)

        self.update_button = QPushButton("Update Model List", self)
        self.update_button.setStyleSheet("background-color: #4A90E2; color: white;")
        self.update_button.clicked.connect(self.update_model_list)
        self.model_layout.addWidget(self.update_button)

        self.favorite_button = QPushButton("Favorite Model", self)
        self.favorite_button.setStyleSheet("background-color: #5e35b1; color: white;")
        self.favorite_button.clicked.connect(self.add_favorite)
        self.model_layout.addWidget(self.favorite_button)

        self.load_button = QPushButton("Load Model", self)
        self.load_button.setStyleSheet("background-color: #4A90E2; color: white;")
        self.load_button.clicked.connect(self.on_model_select)
        self.model_layout.addWidget(self.load_button)

        self.log_text = QTextEdit(self)
        self.log_text.setStyleSheet("background-color: #23272A; color: white;")
        self.model_layout.addWidget(self.log_text)

    def setup_hardware_tab(self):
        self.hardware_tab = QWidget()
        self.tab_widget.addTab(self.hardware_tab, "Hardware")
        
        self.hardware_layout = QGridLayout(self.hardware_tab)

        self.gpu_layers_input = QLineEdit(self)
        self.gpu_layers_input.setPlaceholderText("0")
        self.hardware_layout.addWidget(QLabel("GPU Layers:", self), 1, 0)
        self.hardware_layout.addWidget(self.gpu_layers_input, 1, 1)

        self.threads_slider = QSlider(Qt.Horizontal, self)
        self.threads_slider.setMinimum(1)
        self.threads_slider.setMaximum(4)  # Updated limit from documentation
        self.threads_slider.setValue(4)
        self.threads_slider.setTickPosition(QSlider.TicksBelow)
        self.threads_slider.setTickInterval(1)
        self.threads_slider.valueChanged.connect(self.update_threads_label)  # Connect slider to update label
        self.hardware_layout.addWidget(QLabel("Threads:", self), 2, 0)
        self.hardware_layout.addWidget(self.threads_slider, 2, 1)

        self.threads_value_label = QLabel("4", self)
        self.hardware_layout.addWidget(self.threads_value_label, 2, 2)

        # Text box for Threads slider
        self.threads_textbox = QLineEdit(self)
        self.threads_textbox.setPlaceholderText("Threads")
        self.hardware_layout.addWidget(self.threads_textbox, 2, 3)
        self.threads_textbox.returnPressed.connect(self.update_threads_from_textbox)

        self.blas_batch_size_slider = QSlider(Qt.Horizontal, self)
        self.blas_batch_size_slider.setMinimum(256)
        self.blas_batch_size_slider.setMaximum(2048)  # Updated limit from documentation
        self.blas_batch_size_slider.setValue(512)
        self.blas_batch_size_slider.setTickPosition(QSlider.TicksBelow)
        self.blas_batch_size_slider.setTickInterval(256)
        self.blas_batch_size_slider.valueChanged.connect(self.update_blas_batch_size_label)  # Connect slider to update label
        self.hardware_layout.addWidget(QLabel("BLAS Batch Size:", self), 3, 0)
        self.hardware_layout.addWidget(self.blas_batch_size_slider, 3, 1)

        self.blas_batch_size_value_label = QLabel("512", self)
        self.hardware_layout.addWidget(self.blas_batch_size_value_label, 3, 2)

        # Text box for BLAS Batch Size slider
        self.blas_batch_size_textbox = QLineEdit(self)
        self.blas_batch_size_textbox.setPlaceholderText("BLAS Batch Size")
        self.hardware_layout.addWidget(self.blas_batch_size_textbox, 3, 3)
        self.blas_batch_size_textbox.returnPressed.connect(self.update_blas_batch_size_from_textbox)

        # Contextsize slider
        self.contextsize_slider = QSlider(Qt.Horizontal, self)
        self.contextsize_slider.setMinimum(512)
        self.contextsize_slider.setMaximum(8192)  # Adjust maximum value as needed
        self.contextsize_slider.setValue(4096)  # Default value
        self.contextsize_slider.setTickPosition(QSlider.TicksBelow)
        self.contextsize_slider.setTickInterval(256)
        self.contextsize_slider.valueChanged.connect(self.update_contextsize_label)  # Connect slider to update label
        self.hardware_layout.addWidget(QLabel("Contextsize:", self), 4, 0)
        self.hardware_layout.addWidget(self.contextsize_slider, 4, 1)

        self.contextsize_value_label = QLabel("4096", self)
        self.hardware_layout.addWidget(self.contextsize_value_label, 4, 2)

        # Text box for Contextsize slider
        self.contextsize_textbox = QLineEdit(self)
        self.contextsize_textbox.setPlaceholderText("Contextsize")
        self.hardware_layout.addWidget(self.contextsize_textbox, 4, 3)
        self.contextsize_textbox.returnPressed.connect(self.update_contextsize_from_textbox)

        self.quantkv_combo = QComboBox(self)
        self.quantkv_combo.addItem("8Bit", "1")
        self.quantkv_combo.addItem("4Bit", "2")
        self.hardware_layout.addWidget(QLabel("QuantKV (8Bit/4Bit):", self), 6, 0)
        self.hardware_layout.addWidget(self.quantkv_combo, 6, 1)

        self.port_input = QLineEdit(self)
        self.port_input.setPlaceholderText("Port Number")
        self.hardware_layout.addWidget(QLabel("Port:", self), 1, 2)
        self.hardware_layout.addWidget(self.port_input, 1, 3)
        
        self.ropeconfig = QLineEdit(self)
        self.ropeconfig.setPlaceholderText("'0.0', '10000.0'")
        self.hardware_layout.addWidget(QLabel("Rope Config:", self), 6, 2)
        self.hardware_layout.addWidget(self.ropeconfig, 6, 3)

        self.multiuser = QLineEdit(self)
        self.multiuser.setPlaceholderText("1")
        self.hardware_layout.addWidget(QLabel("Multi User:", self), 7, 0)
        self.hardware_layout.addWidget(self.multiuser, 7, 1)
        
        self.usecublas = QLineEdit(self)
        self.usecublas.setPlaceholderText("'normal', '0', 'mmq'")
        self.hardware_layout.addWidget(QLabel("GPU Acceleration:", self), 7, 2)
        self.hardware_layout.addWidget(self.usecublas, 7, 3)
        
        self.password = QLineEdit(self)
        self.password.setPlaceholderText("null")
        self.hardware_layout.addWidget(QLabel("Password:", self), 8, 0)
        self.hardware_layout.addWidget(self.password, 8, 1)

        # Add checkboxes for new parameters
        self.launch_checkbox = QCheckBox("Launch", self)
        self.launch_checkbox.setChecked(True)
        self.hardware_layout.addWidget(self.launch_checkbox, 9, 0)

        self.smartcontext_checkbox = QCheckBox("Smart Context", self)
        self.smartcontext_checkbox.setChecked(True)
        self.hardware_layout.addWidget(self.smartcontext_checkbox, 9, 1)

        self.noshift_checkbox = QCheckBox("No Shift", self)
        self.noshift_checkbox.setChecked(False)
        self.hardware_layout.addWidget(self.noshift_checkbox, 9, 2)

        self.nommap_checkbox = QCheckBox("No Memory Map", self)
        self.nommap_checkbox.setChecked(False)
        self.hardware_layout.addWidget(self.nommap_checkbox, 9, 3)

        self.usemlock_checkbox = QCheckBox("Use Mlock", self)
        self.usemlock_checkbox.setChecked(False)
        self.hardware_layout.addWidget(self.usemlock_checkbox, 10, 0)

        self.flashattention_checkbox = QCheckBox("Flash Attention", self)
        self.flashattention_checkbox.setChecked(True)
        self.hardware_layout.addWidget(self.flashattention_checkbox, 10, 1)

        self.save_button = QPushButton("Save Config", self)
        self.save_button.setStyleSheet("background-color: #43B681; color: white;")
        self.save_button.clicked.connect(self.save_config)
        self.hardware_layout.addWidget(self.save_button, 11, 2, 1, 2)

        self.load_config_button = QPushButton("Load Config", self)
        self.load_config_button.setStyleSheet("background-color: #43B681; color: white;")
        self.load_config_button.clicked.connect(self.load_config)
        self.hardware_layout.addWidget(self.load_config_button, 11, 0, 1, 2)

        self.launch_button = QPushButton("Launch", self)
        self.launch_button.setStyleSheet("background-color: #4A90E2; color: white;")
        self.launch_button.clicked.connect(self.on_launch_click)
        self.hardware_layout.addWidget(self.launch_button, 12, 0, 1, 4)

    def select_model_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Model Directory")
        if directory:
            self.model_dir_input.setText(directory)
    
    def select_kcpp_directory(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Select KoboldCpp Executable", "", "Executable Files (*.exe)")
        if fileName:
            self.kcpp_dir_input.setText(fileName)    

    def update_threads_from_textbox(self):
        try:
            value = int(self.threads_textbox.text())
            if 1 <= value <= 32:
                self.threads_slider.setValue(value)
                self.threads_value_label.setText(str(value))
            else:
                QMessageBox.warning(self, "Invalid Value", "Threads value must be between 1 and 32.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Value", "Please enter a valid integer for Threads.")

    def update_blas_batch_size_from_textbox(self):
        try:
            value = int(self.blas_batch_size_textbox.text())
            if 256 <= value <= 2048:
                self.blas_batch_size_slider.setValue(value)
                self.blas_batch_size_value_label.setText(str(value))
            else:
                QMessageBox.warning(self, "Invalid Value", "BLAS Batch Size must be between 256 and 2048.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Value", "Please enter a valid integer for BLAS Batch Size.")

    def update_contextsize_from_textbox(self):
        try:
            value = int(self.contextsize_textbox.text())
            if 1 <= value <= 8192:
                self.contextsize_slider.setValue(value)
                self.contextsize_value_label.setText(str(value))
            else:
                QMessageBox.warning(self, "Invalid Value", "Contextsize must be between 1 and 8192.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Value", "Please enter a valid integer for Contextsize.")

    def update_contextsize_label(self):
        value = self.contextsize_slider.value()
        self.contextsize_value_label.setText(str(value))

    def get_model_paths(self, main_dir):
        model_paths = []
        for root, dirs, files in os.walk(main_dir):
            for file in files:
                if file.endswith(".gguf"):
                    file_size = os.path.getsize(os.path.join(root, file))
                    model_paths.append((file, file_size, os.path.join(root, file)))
        return model_paths

    def update_model_list(self):
        self.main_dir = self.model_dir_input.text()
        model_paths = self.get_model_paths(self.main_dir)
        self.model_combo.clear()
        if model_paths:
            for name, size, path in model_paths:
                self.model_combo.addItem(f"{name} ({size / (1024 * 1024):.2f} MB)", path)
        else:
            self.model_combo.addItem("No models found")
            QMessageBox.critical(self, "Error", "No models found in the specified directory!")

    def on_model_select(self):
        selected_index = self.model_combo.currentIndex()
        selected_model = self.model_combo.itemData(selected_index)
        if selected_model and selected_model != "No models found":
            self.run_koboldcpp(selected_model)
            

    def update_threads_label(self):
        value = self.threads_slider.value()
        self.threads_value_label.setText(str(value))

    def update_blas_batch_size_label(self):
        value = self.blas_batch_size_slider.value()
        self.blas_batch_size_value_label.setText(str(value))

    def save_config(self):
        config = {
            "model_path": self.model_dir_input.text(),
            "kcpp_path": self.kcpp_dir_input.text(),
            "port": self.port_input.text(),
            "threads": self.threads_slider.value(),
            "blas_batch_size": self.blas_batch_size_slider.value(),
            "context_size": self.contextsize_slider.value(),
            "gpu_layers": self.gpu_layers_input.text(),
            "quantkv_index": int(self.quantkv_combo.currentIndex()),
            "usecublas": self.usecublas.text(),
            "multiuser": self.multiuser.text(),
            "password": self.password.text(),
            "favorites": self.favorites,
            'launch': self.launch_checkbox.isChecked(),
            'smartcontext': self.smartcontext_checkbox.isChecked(),
            'noshift': self.noshift_checkbox.isChecked(),
            'nommap': self.nommap_checkbox.isChecked(),
            'usemlock': self.usemlock_checkbox.isChecked(),
            'flashattention': self.flashattention_checkbox.isChecked()
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        QMessageBox.information(self, "Success", "Configuration saved successfully.")


    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.kcpp_dir_input.setText(config.get("kcpp_path", ""))
                self.model_dir_input.setText(config.get("model_path", ""))
                self.port_input.setText(config.get("port", "5001"))
                self.threads_slider.setValue(config.get("threads", 4))
                self.blas_batch_size_slider.setValue(config.get("blas_batch_size", 512))
                self.contextsize_slider.setValue(config.get("context_size", 4096))
                self.gpu_layers_input.setText(config.get("gpu_layers", "0"))
                self.quantkv_combo.setCurrentIndex(int(config.get("quantkv_index", 0)))
                self.usecublas.setText(config.get("usecublas", ""))
                self.multiuser.setText(config.get("multiuser", "1"))
                self.password.setText(config.get("password", "null"))
                self.favorites = config.get("favorites", [])
                self.launch_checkbox.setChecked(config.get('launch', True))
                self.smartcontext_checkbox.setChecked(config.get('smartcontext', True))
                self.noshift_checkbox.setChecked(config.get('noshift', True))
                self.nommap_checkbox.setChecked(config.get('nommap', False))
                self.usemlock_checkbox.setChecked(config.get('usemlock', False))
                self.flashattention_checkbox.setChecked(config.get('flashattention', True))
                self.update_favorites_layout() 

    def run_koboldcpp(self, model_path):
        command = [
            'cmd', '/c', 'start', 'cmd', '/k', self.kcpp_dir_input.text(),
            '--model', model_path,
            '--port', self.port_input.text(),
            '--host', '',
            '--threads', str(self.threads_slider.value()),
            '--usecublas', 'normal', '0',
            '--contextsize', str(self.contextsize_slider.value()),
            '--gpulayers', self.gpu_layers_input.text(),
            '--blasbatchsize', str(self.blas_batch_size_slider.value()),
            '--multiuser', self.multiuser.text(),
            '--quantkv', str(self.quantkv_combo.currentData()),
            '--password', self.password.text(),
            '--forceversion', '0'
        ]
        # Add checkbox flags to the command
        if self.launch_checkbox.isChecked():
            command.append('--launch')
        if self.smartcontext_checkbox.isChecked():
            command.append('--smartcontext')
            command.append('--noshift')

        if self.noshift_checkbox.isChecked():
            command.append('--noshift')
        if self.nommap_checkbox.isChecked():
            command.append('--nommap')
        if self.usemlock_checkbox.isChecked():
            command.append('--usemlock')
        if self.flashattention_checkbox.isChecked():
            command.append('--flashattention')
        command_str = ' '.join(command)
        self.log_text.append(f"Launching model with default parameters: {model_path}")       
        self.log_text.append(f"\nCommandline:{command_str}")
        self.log_text.append(f"\nEndpoint at http://localhost:{self.port_input.text()}")
        process = subprocess.Popen(command)
        return process

    def on_launch_click(self):
        selected_index = self.model_combo.currentIndex()
        selected_model = self.model_combo.itemData(selected_index)
        if selected_model and selected_model != "No models found":
            self.run_koboldcpp(selected_model)
        else:
            QMessageBox.critical(self, "Error", "Please select a model to launch.")

    def add_favorite(self):
        selected_index = self.model_combo.currentIndex()
        selected_model = self.model_combo.itemData(selected_index)
        model_name = self.model_combo.currentText()
        if selected_model and selected_model != "No models found":
            favorite_name, ok = QInputDialog.getText(self, 'Favorite Model', 'Enter a name for the favorite:')
            if ok:
                if not favorite_name:
                    favorite_name = f"{model_name[:3]}...{model_name[-3:]}"
                self.favorites.append((favorite_name, selected_model))
                self.update_favorites_layout()
                self.save_config()  # Save favorites to config

    def update_favorites_layout(self):
        for i in reversed(range(self.favorites_layout.count())):
            self.favorites_layout.itemAt(i).widget().deleteLater()
        
        for name, path in self.favorites:
            button = QPushButton(name, self)
            button.setStyleSheet("background-color: #5e35b1; color: white;")
            button.clicked.connect(lambda checked, p=path: self.run_koboldcpp(p))
            self.favorites_layout.addWidget(button)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Confirm Exit',
                                     "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet("QTabWidget::pane {border: 0;}")

    window = ModelLoader()
    window.show()

    sys.exit(app.exec_())
