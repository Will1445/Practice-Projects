import sys
import os
import subprocess
import tempfile
import platform
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QLineEdit, QVBoxLayout, QGridLayout, QTextEdit, QCheckBox, QDialog, QFormLayout, QFileDialog, QRadioButton, QDialogButtonBox, QVBoxLayout
)
from PyQt6.QtCore import Qt
import ipaddress




def is_valid_ip(ip_str):
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

import subprocess
import os

def make_exe(py_file_path, timestamp, hide_console=True):
    """
    Builds a standalone .exe from a Python file using PyInstaller.
    Drops the .exe in the same directory as the Python file.
    All intermediate build files go into a 'build files' folder.
    
    Args:
        py_file_path (str): Full path to the Python file.
        hide_console (bool): If True, hides console window (for GUI apps).
    
    Returns:
        str: Path to the generated .exe file.
    """
    base = os.path.dirname(py_file_path)
    name = os.path.splitext(os.path.basename(py_file_path))[0]
    exe_path = os.path.join(base, f"{name}.exe")
    
    # Folder for intermediate build files
    build_folder = os.path.join(base, f"build files {timestamp}")
    os.makedirs(build_folder, exist_ok=True)

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        f"--distpath={base}",      # .exe goes here
        f"--workpath={build_folder}",
        f"--specpath={build_folder}"
    ]
    if hide_console:
        cmd.append("--noconsole")
    cmd.append(py_file_path)

    # Run PyInstaller
    subprocess.run(cmd, cwd=base)

    return exe_path




class Indicator(QLabel):
    def __init__(self, text="", color="red"):
        super().__init__(text)
        self.setFixedSize(60, 25)
        self.setAutoFillBackground(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"background-color: {color}; color: white; border-radius: 5px;")
    
    def set_color(self, color):
        """Update the indicator color"""
        self.setStyleSheet(f"background-color: {color}; color: white; border-radius: 5px;")

class ConfigDialog(QDialog):
    def __init__(self, title, fields):
        super().__init__()
        self.setWindowTitle(title)
        layout = QFormLayout()
        self.inputs = {}

        for field in fields:
            inp = QLineEdit()
            layout.addRow(QLabel(field+":"), inp)
            self.inputs[field] = inp

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)

        self.setLayout(layout)

    def get_values(self):
        return {field: inp.text() for field, inp in self.inputs.items()}

class PresetDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Preset")

        layout = QVBoxLayout()

        self.bpsk = QRadioButton("BPSK")
        self.cw = QRadioButton("CW")
        self.awgn = QRadioButton("AWGN")

        layout.addWidget(self.bpsk)
        layout.addWidget(self.cw)
        layout.addWidget(self.awgn)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_selected(self):
        if self.bpsk.isChecked():
            return "BPSK"
        elif self.cw.isChecked():
            return "CW"
        elif self.awgn.isChecked():
            return "AWGN"
        return None

class NavSensorsGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.ip_status_lights = []  # Store references to individual IP status lights
        self.main_status_light = None  # Store reference to main status light
        self.ready_light = None  # Store reference to ready light
        self.output_dir_input = None  # Store reference to output directory input
        self.l1_checkbox = None  # Store reference to L1 checkbox
        self.l2_checkbox = None  # Store reference to L2 checkbox
        self.custom_checkbox = None  # Store reference to custom checkbox
        self.custom_input = None  # Store reference to custom input
        self.waveform_loaded = False  # Track if waveform is loaded
        self.init_ui()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Title (smaller and clearer)
        title = QLabel("Navigation Sensors")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 5px;")
        main_layout.addWidget(title)

        # Grid layout
        grid = QGridLayout()

        # Left side: unit checkboxes + IP inputs + status lights
        self.ip_checkboxes = []
        self.ip_inputs = []
        for i in range(8):
            num_label = QLabel(str(i+1))
            checkbox = QCheckBox()
            ip_input = QLineEdit()
            ip_input.setPlaceholderText("Enter IP")
            status_light = Indicator(color="gray")

            checkbox.stateChanged.connect(lambda state, idx=i: self.on_ip_checkbox_toggled(idx, state))
            ip_input.textChanged.connect(lambda text, idx=i: self.on_ip_input_changed(idx, text))

            grid.addWidget(num_label, i, 0)
            grid.addWidget(checkbox, i, 1)
            grid.addWidget(ip_input, i, 2)
            grid.addWidget(status_light, i, 3)

            self.ip_checkboxes.append(checkbox)
            self.ip_inputs.append(ip_input)
            self.ip_status_lights.append(status_light)

        # Middle section
        add_ramp_btn = QPushButton("Add Ramp")
        add_ramp_btn.clicked.connect(self.on_add_ramp)
        grid.addWidget(add_ramp_btn, 0, 4, 1, 2)

        add_hold_btn = QPushButton("Add Hold")
        add_hold_btn.clicked.connect(self.on_add_hold)
        grid.addWidget(add_hold_btn, 1, 4, 1, 2)

        add_onoff_btn = QPushButton("Add On/Off")
        add_onoff_btn.clicked.connect(self.on_add_onoff)
        grid.addWidget(add_onoff_btn, 2, 4, 1, 2)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.on_remove_profile)
        grid.addWidget(remove_btn, 3, 4, 1, 2)

        # Profile summary
        self.profile_summary = QTextEdit()
        self.profile_summary.setReadOnly(True)
        self.profile_summary.setPlaceholderText("Profile Summary")
        grid.addWidget(self.profile_summary, 4, 4, 4, 2)

        # Right side
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.on_browse)
        grid.addWidget(QLabel("Load Waveform:"), 0, 6)
        grid.addWidget(browse_btn, 0, 7)

        preset_btn = QPushButton("Preset")
        preset_btn.clicked.connect(self.on_preset)
        grid.addWidget(preset_btn, 0, 8)

        self.loaded_file = QLineEdit("Loaded file")
        self.loaded_file.setReadOnly(True)
        grid.addWidget(self.loaded_file, 1, 6, 1, 3)

        self.l1_checkbox = QCheckBox("L1")
        self.l2_checkbox = QCheckBox("L2")
        self.custom_checkbox = QCheckBox("Custom")
        self.custom_input = QLineEdit()

        self.l1_checkbox.stateChanged.connect(lambda state: self.on_waveform_checkbox("L1", state))
        self.l2_checkbox.stateChanged.connect(lambda state: self.on_waveform_checkbox("L2", state))
        self.custom_checkbox.stateChanged.connect(lambda state: self.on_waveform_checkbox("Custom", state))
        self.custom_input.textChanged.connect(self.on_custom_waveform_input)

        grid.addWidget(self.l1_checkbox, 2, 6)
        grid.addWidget(self.l2_checkbox, 3, 6)
        grid.addWidget(self.custom_checkbox, 4, 6)
        grid.addWidget(self.custom_input, 4, 7, 1, 2)

        grid.addWidget(QLabel("Output Dir:"), 5, 6)
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setReadOnly(True)
        output_dir_browse_btn = QPushButton("Browse")
        output_dir_browse_btn.clicked.connect(self.on_browse_output_dir)
        grid.addWidget(self.output_dir_input, 5, 7)
        grid.addWidget(output_dir_browse_btn, 5, 8)

        self.main_status_light = Indicator("Status", "red")
        self.ready_light = Indicator("Ready", "red")
        grid.addWidget(self.main_status_light, 6, 6)
        grid.addWidget(self.ready_light, 6, 7)

        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(self.on_generate)
        grid.addWidget(generate_btn, 7, 6, 1, 3)

        # Add grid to layout
        main_layout.addLayout(grid)

        # Set layout
        self.setLayout(main_layout)
        self.setWindowTitle("Navigation Sensors GUI")
        self.setGeometry(200, 200, 900, 500)

    def update_status_lights(self):
        """Update all status lights based on current IP validation state"""
        all_selected_valid = True
        any_selected = False
        
        for i in range(8):
            checkbox = self.ip_checkboxes[i]
            ip_input = self.ip_inputs[i]
            status_light = self.ip_status_lights[i]
            
            is_checked = checkbox.isChecked()
            ip_text = ip_input.text().strip()
            is_valid = is_valid_ip(ip_text) if ip_text else False
            
            # Update individual status light
            if is_checked:
                any_selected = True
                if is_valid:
                    status_light.set_color("green")
                else:
                    status_light.set_color("red")
                    all_selected_valid = False
            else:
                # Not selected - show gray/inactive
                status_light.set_color("gray")
        
        # Update main status light
        if any_selected and all_selected_valid:
            self.main_status_light.set_color("green")
        else:
            self.main_status_light.set_color("red")
        
        # Update ready light
        self.update_ready_light()

    def update_ready_light(self):
        """Update ready light based on all system requirements"""
        # Check if main status is green (all selected IPs valid)
        main_status_green = self.main_status_light.styleSheet().find("background-color: green") != -1
        
        # Check if profile summary has entries
        profile_has_entries = bool(self.profile_summary.toPlainText().strip())
        
        # Check if waveform is loaded (file or preset)
        waveform_loaded = self.waveform_loaded or (self.loaded_file.text() not in ["", "Loaded file"])
        
        # Check if one of L1, L2, or Custom is selected
        waveform_type_selected = (self.l1_checkbox.isChecked() or 
                                 self.l2_checkbox.isChecked() or 
                                 self.custom_checkbox.isChecked())
        
        # Check if output directory is set
        output_dir_set = bool(self.output_dir_input.text().strip())
        
        # Ready light is green only if ALL conditions are met
        if (main_status_green and profile_has_entries and 
            waveform_loaded and waveform_type_selected and output_dir_set):
            self.ready_light.set_color("green")
        else:
            self.ready_light.set_color("red")

    # Methods for signals
    def on_ip_checkbox_toggled(self, idx, state):
        print(f"IP tickbox {idx+1} {'ticked' if state else 'unticked'}")
        self.update_status_lights()

    def on_ip_input_changed(self, idx, text):
        print(f"IP input {idx+1} changed to: {text}")
        self.update_status_lights()

    def on_add_ramp(self):
        dlg = ConfigDialog("Configure Ramp", ["Min Value", "Max Value", "Step Size", "Dwell Time"])
        if dlg.exec():
            values = dlg.get_values()
            summary = f"Ramp: {values['Step Size']}db/{values['Dwell Time']}s {values['Min Value']}-{values['Max Value']}"
            self.profile_summary.append(summary)
            print("Ramp configured:", values)
            self.update_ready_light()

    def on_add_hold(self):
        dlg = ConfigDialog("Configure Hold", ["Power", "Duration"])
        if dlg.exec():
            values = dlg.get_values()
            summary = f"Hold: {values['Power']}db {values['Duration']}s"
            self.profile_summary.append(summary)
            print("Hold configured:", values)
            self.update_ready_light()

    def on_add_onoff(self):
        dlg = ConfigDialog("Configure On/Off", ["Duration"])
        if dlg.exec():
            values = dlg.get_values()
            summary = f"On/Off: {values['Duration']}s"
            self.profile_summary.append(summary)
            print("On/Off configured:", values)
            self.update_ready_light()

    def on_remove_profile(self):
        """Remove the last entry from the profile summary"""
        current_text = self.profile_summary.toPlainText()
        if current_text.strip():
            lines = current_text.strip().split('\n')
            if lines:
                lines.pop()  # Remove the last line
                new_text = '\n'.join(lines)
                self.profile_summary.clear()
                if new_text:
                    self.profile_summary.setPlainText(new_text)
                print("Removed last profile entry")
                self.update_ready_light()

    def on_browse(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Waveform File", "", "All Files (*)")
        if file_path:
            self.loaded_file.setText(file_path)
            self.waveform_loaded = True
            print(f"Loaded file: {file_path}")
            self.update_ready_light()

    def on_browse_output_dir(self):
        file_dialog = QFileDialog()
        dir_path = file_dialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir_input.setText(dir_path)
            print(f"Selected output directory: {dir_path}")
            self.update_ready_light()

    def on_preset(self):
        dlg = PresetDialog()
        if dlg.exec():
            choice = dlg.get_selected()
            if choice:
                self.loaded_file.setText(f"Preset: {choice}")
                self.waveform_loaded = True
                print(f"Preset selected: {choice}")
                self.update_ready_light()

    def on_waveform_checkbox(self, name, state):
        print(f"Waveform {name} {'ticked' if state else 'unticked'}")
        
        # Make L1, L2, and Custom mutually exclusive
        if state:  # If this checkbox was just checked
            if name == "L1":
                self.l2_checkbox.setChecked(False)
                self.custom_checkbox.setChecked(False)
            elif name == "L2":
                self.l1_checkbox.setChecked(False)
                self.custom_checkbox.setChecked(False)
            elif name == "Custom":
                self.l1_checkbox.setChecked(False)
                self.l2_checkbox.setChecked(False)
        
        self.update_ready_light()

    def on_custom_waveform_input(self, text):
        print(f"Custom waveform input: {text}")

    def on_output_dir_changed(self, text):
        print(f"Output directory changed: {text}")
        self.update_ready_light()

    def on_generate(self):
        print("Generate button clicked")
        self.generate_python_file()

    def generate_python_file(self):
        """Generate a Python file with current GUI state as comments"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nav_sensors_config_{timestamp}.py"
        
        # Use output directory if set, otherwise use current directory
        output_dir = self.output_dir_input.text().strip()
        if output_dir:
            filepath = os.path.join(output_dir, filename)
        else:
            filepath = filename
        
        try:
            with open(filepath, 'w') as f:
                f.write("# Navigation Sensors Configuration\n")
                f.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # IP Configuration
                f.write("# IP Configuration:\n")
                selected_ips = []
                for i in range(8):
                    checkbox = self.ip_checkboxes[i]
                    ip_input = self.ip_inputs[i]
                    is_checked = checkbox.isChecked()
                    ip_text = ip_input.text().strip()
                    is_valid = is_valid_ip(ip_text) if ip_text else False
                    
                    status = "SELECTED" if is_checked else "NOT SELECTED"
                    validity = "VALID" if is_valid else "INVALID" if ip_text else "EMPTY"
                    
                    f.write(f"# IP {i+1}: {status}, IP='{ip_text}', Status={validity}\n")
                    
                    if is_checked and is_valid:
                        selected_ips.append(ip_text)
                
                f.write(f"# Total selected valid IPs: {len(selected_ips)}\n\n")
                
                # Profile Summary
                profile_text = self.profile_summary.toPlainText().strip()
                f.write("# Profile Summary:\n")
                if profile_text:
                    for line in profile_text.split('\n'):
                        if line.strip():
                            f.write(f"# {line}\n")
                else:
                    f.write("# No profile configured\n")
                f.write("\n")
                
                # Waveform Configuration
                f.write("# Waveform Configuration:\n")
                f.write(f"# Loaded File: '{self.loaded_file.text()}'\n")
                f.write(f"# L1 Selected: {self.l1_checkbox.isChecked()}\n")
                f.write(f"# L2 Selected: {self.l2_checkbox.isChecked()}\n")
                f.write(f"# Custom Selected: {self.custom_checkbox.isChecked()}\n")
                f.write(f"# Custom Value: '{self.custom_input.text().strip()}'\n\n")
                
                # Output Directory
                f.write(f"# Output Directory: '{output_dir}'\n\n")
                
                # Status Summary
                f.write("# Status Summary:\n")
                main_status = "GREEN" if len(selected_ips) > 0 else "RED"
                f.write(f"# Main Status Light: {main_status}\n")
                f.write(f"# All selected IPs valid: {len(selected_ips) > 0}\n\n")
                
                # Placeholder for actual code
                f.write("# Generated Python code will go here\n")
                f.write("print('Navigation Sensors Configuration Loaded')\n")
                
            print(f"Generated Python file: {filepath}")
            
            # exe_path = make_exe(filepath, timestamp=timestamp)
            # print(f"Converted Python file to .exe: {exe_path}")
            
        except Exception as e:
            print(f"Error generating Python file: {e}")


def main():
    app = QApplication(sys.argv)
    window = NavSensorsGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()