# TID encoder V2.0, 5th of march 2025 (if changed, please search for "TID encoder" and change the value for the window name as well )
# Freya Mutschler
# Following TDS 2.2
#
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QCheckBox, QLineEdit, QScrollArea, QGroupBox, QHBoxLayout, QPlainTextEdit, QComboBox, QLabel)
from PyQt5.QtCore import QRegExp # type: ignore
from PyQt5.QtGui import QRegExpValidator # type: ignore
import sys
import re
import json  # for loading JSON options

################################################################################################################################################################################
########    This code is meant to generate TIDs and XTIDS that strictly follow TDS specs as written by GS1. the version it follows is numbered at line3 in this code.   ######## 
########    It is worth noting that this code is not meant to output TIDs and XTIDs as they are done by all manufacturers, as some chips kinda do their own things      ########
########    with regards to TDS specs. G2iM from NXP fpr example does not have the X bit (bit 9) enabled despite having an XTID header, and uses a bit at adress 14h to ########
########    inform on a config word. this is *far* from the only example. Some chips write data in RFU spaces. Some chips have actual short TIDs, but a load of config  ########
########    data after the short TID unrelated to the short or XTID info (alien chips for exmple).                                                                      ########
########                                                                                                                                                                ########
########    ----------------------------    BE WARNED AND AWARE OF WHAT YOU'RE DOING / USING THIS SOFTWARE FOR.     ------------------------------------------------    ########
########                                                                                                                                                                ########
########    For compliance with GS1 TDS specs, all RFU fields that might exist are hardset to all 0s, or any value specified in the TDS, and any field/bits that need   ########
########    to be set at certain values are (E2(h) prefix for example -- which denotes an EPC TID. others exist such as ISO's E0(h) and E3(h). )                        ########
################################################################################################################################################################################


#### JSON file opening and removal of non-printable characters
# Remove non-printable characters except spaces, newlines, and tabs
def clean_json_data(raw_data):
    return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', raw_data)

# Load cleaned-up JSON data
def load_json_data():
    try:
        with open("Digits'_mdid_list.json", "r", encoding="utf-8") as file:
            raw_data = file.read()
            cleaned_data = clean_json_data(raw_data)
            data = json.loads(cleaned_data)
            print("Data loaded successfully")
            return data
    except Exception as e:
        print(f"ERROR decoding the JSON data: {e}")
        return None


class TID_encoder(QWidget):

    def __init__(self):
        super().__init__()
        self.XTID_output = ""  # This variable will hold the complete binary output string.
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 100, 2000, 800)     # Set window position (x,y) and size (width, height) in pixels 
        layout = QVBoxLayout()

        scroll_area = QScrollArea()             # Create a scrollable area for input groups.
        scroll_area.setWidgetResizable(True)
        checkboxes_widget = QWidget()
        checkboxes_layout = QHBoxLayout()

    ######## --- GroupBox 1: Short TID ----------
        groupbox_1 = QGroupBox("Short TID")
        groupbox_1_layout = QVBoxLayout()

        # Create checkboxes for Group 1
        self.checkbox1 = QCheckBox("XTID bit")
        self.checkbox2 = QCheckBox("S")
        self.checkbox3 = QCheckBox("F")
        
        # --- New: Add dropdown for MDID options ---
        self.mdid_dropdown = QComboBox()
        self.mdid_dropdown.setToolTip("Select a manufacturer")
        mdid_label = QLabel("Chip Manufacturer:")

        # MDID input
        self.mdid_input = QLineEdit()
        self.mdid_input.setMaxLength(9)
        self.mdid_input.setPlaceholderText("MDID")
        binary_regex = QRegExp("^[01]{1,9}$")
        binary_validator = QRegExpValidator(binary_regex)
        self.mdid_input.setValidator(binary_validator)
        self.mdid_input.setFixedWidth(self.mdid_input.fontMetrics().horizontalAdvance(" 123456789 "))

        # --- New: Add dropdown for TMN options ---
        self.tmn_dropdown = QComboBox()
        self.tmn_dropdown.setToolTip("Select a chip model")
        tmn_label = QLabel("chip model:")

        # TMN input
        self.tmn_input = QLineEdit()
        self.tmn_input.setMaxLength(3)
        self.tmn_input.setPlaceholderText("TMN")
        hex_regex = QRegExp("^[0-9A-Fa-f]{1,3}$")
        hex_validator = QRegExpValidator(hex_regex)
        self.tmn_input.setValidator(hex_validator)
        self.tmn_input.setFixedWidth(self.tmn_input.fontMetrics().horizontalAdvance(" 123456789 "))

        # Load dropdown options from the JSON file
        self.load_options()

        # Add widgets to GroupBox 1 layout
        groupbox_1_layout.addWidget(self.checkbox1)
        groupbox_1_layout.addWidget(self.checkbox2)
        groupbox_1_layout.addWidget(self.checkbox3)
        groupbox_1_layout.addWidget(mdid_label)
        groupbox_1_layout.addWidget(self.mdid_dropdown)
        groupbox_1_layout.addWidget(self.mdid_input)
        groupbox_1_layout.addWidget(tmn_label)
        groupbox_1_layout.addWidget(self.tmn_dropdown)
        groupbox_1_layout.addWidget(self.tmn_input)
        groupbox_1.setLayout(groupbox_1_layout)

    ######## --- GroupBox 2: XTID Header and Serial Number ---
        groupbox_2 = QGroupBox("XTID Header and Serial Number")
        groupbox_2_layout = QVBoxLayout()

        # Create checkboxes for Group 2 as instance variables
        self.checkbox6 = QCheckBox("Extended Header Present")
        self.checkbox7 = QCheckBox("Lock bit segment")
        self.checkbox8 = QCheckBox("Optional Command Support Segment Present")
        self.checkbox9 = QCheckBox("BlockWrite and BlockErase Segment Present")
        self.checkbox10 = QCheckBox("User Memory and Block Perma Lock Segment Present")
        
        self.group2_checkboxes = [self.checkbox6, self.checkbox7, self.checkbox8, self.checkbox9, self.checkbox10]
        
        # Serial Number fields
        self.Serial_length_input = QLineEdit()
        self.Serial_length_input.setMaxLength(3)
        self.Serial_length_input.setPlaceholderText("serial number length")
        hex_regex = QRegExp("^[01]{1,3}$")
        hex_validator = QRegExpValidator(hex_regex)
        self.Serial_length_input.setValidator(hex_validator)
        self.Serial_length_input.setFixedWidth(self.Serial_length_input.fontMetrics().horizontalAdvance(" serial number length "))

        self.Serial_value_input = QLineEdit()
        self.Serial_value_input.setMaxLength(0)  # Will be updated dynamically
        self.Serial_value_input.setPlaceholderText("Serial number data")
        hex_regex = QRegExp("^[0-9A-Fa-f]+$")
        hex_validator = QRegExpValidator(hex_regex)
        self.Serial_value_input.setValidator(hex_validator)
        self.Serial_value_input.setFixedWidth(self.Serial_value_input.fontMetrics().horizontalAdvance(" 00112233445566778899AABBCCDDEEFF0011 "))
        self.Serial_value_input.setEnabled(False)

        groupbox_2_layout.addWidget(self.checkbox8)
        groupbox_2_layout.addWidget(self.checkbox9)
        groupbox_2_layout.addWidget(self.checkbox10)
        groupbox_2_layout.addWidget(self.checkbox7)
        groupbox_2_layout.addWidget(self.checkbox6)
        groupbox_2_layout.addWidget(self.Serial_length_input)
        groupbox_2_layout.addWidget(self.Serial_value_input)
        groupbox_2.setLayout(groupbox_2_layout)

    ######## --- GroupBox 3: OPTIONAL COMMANDS ---
        groupbox_3 = QGroupBox("Optional Commands")
        groupbox_3_layout = QVBoxLayout()

        self.EPC_length_input = QLineEdit()
        self.EPC_length_input.setMaxLength(5)
        self.EPC_length_input.setPlaceholderText("EPC number length")
        hex_regex = QRegExp("^[01]{1,5}$")
        hex_validator = QRegExpValidator(hex_regex)
        self.EPC_length_input.setValidator(hex_validator)
        self.EPC_length_input.setFixedWidth(self.EPC_length_input.fontMetrics().horizontalAdvance(" 123456789ABCDEF "))

        self.checkbox14 = QCheckBox("recom support")
        self.checkbox15 = QCheckBox("Access")
        self.checkbox16 = QCheckBox("Seperate lockbits")
        self.checkbox17 = QCheckBox("Auto UMI support")
        self.checkbox18 = QCheckBox("Phase Jitter Modulation (PJM) support")
        self.checkbox19 = QCheckBox("Block Erase support")
        self.checkbox20 = QCheckBox("Block Write support")
        self.checkbox21 = QCheckBox("Block PermaLock support")

        self.group3_checkboxes = [self.checkbox14, self.checkbox15, self.checkbox16, self.checkbox17, self.checkbox18,
                                  self.checkbox19, self.checkbox20, self.checkbox21]
        
        groupbox_3_layout.addWidget(self.EPC_length_input)
        groupbox_3_layout.addWidget(self.checkbox14)
        groupbox_3_layout.addWidget(self.checkbox15)
        groupbox_3_layout.addWidget(self.checkbox16)
        groupbox_3_layout.addWidget(self.checkbox17)
        groupbox_3_layout.addWidget(self.checkbox18)
        groupbox_3_layout.addWidget(self.checkbox19)
        groupbox_3_layout.addWidget(self.checkbox20)
        groupbox_3_layout.addWidget(self.checkbox21)
        groupbox_3.setLayout(groupbox_3_layout)

    ######## --- GroupBox 4: Block Write and Block Erase ---
        groupbox_4 = QGroupBox("Block Write and Block Erase")
        groupbox_4_layout = QVBoxLayout()
        
    ######## --- 4.1 Block Write
        groupbox_4_1 = QGroupBox("Block Write")
        groupbox_4_1_layout = QVBoxLayout()
        
        self.Block_write_length_input = QLineEdit()
        self.Block_write_length_input.setMaxLength(3)
        self.Block_write_length_input.setPlaceholderText("Block Write Size 0-255")
        hex_regex = QRegExp("^[0-9]{1,3}$")
        hex_validator = QRegExpValidator(hex_regex)
        self.Block_write_length_input.setValidator(hex_validator)
        self.Block_write_length_input.setFixedWidth(self.Block_write_length_input.fontMetrics().horizontalAdvance(" Block Write Size 0-255 "))

        self.Block_write_EPC_offset_input = QLineEdit()
        self.Block_write_EPC_offset_input.setMaxLength(2)
        self.Block_write_EPC_offset_input.setPlaceholderText("Block Write EPC offset adress (h)")
        hex_regex = QRegExp("^[0-9A-Fa-f]+$")
        hex_validator = QRegExpValidator(hex_regex)
        self.Block_write_EPC_offset_input.setValidator(hex_validator)
        self.Block_write_EPC_offset_input.setFixedWidth(self.Block_write_EPC_offset_input.fontMetrics().horizontalAdvance(" Block Write EPC offset adress (h) "))

        self.Block_write_USER_offset_input = QLineEdit()
        self.Block_write_USER_offset_input.setMaxLength(2)
        self.Block_write_USER_offset_input.setPlaceholderText("Block Write USER offset adress (h)")
        hex_regex = QRegExp("^[0-9A-Fa-f]+$")
        hex_validator = QRegExpValidator(hex_regex)
        self.Block_write_USER_offset_input.setValidator(hex_validator)
        self.Block_write_USER_offset_input.setFixedWidth(self.Block_write_USER_offset_input.fontMetrics().horizontalAdvance(" Block Write USER offset adress (h) "))

        self.checkbox22 = QCheckBox("Variable size Block Write")
        self.checkbox23 = QCheckBox("Block Write EPC address alignment")
        self.checkbox24 = QCheckBox("Block Write USER address alignment")

        self.group4_1_checkboxes = [self.checkbox22, self.checkbox23, self.checkbox24]

        groupbox_4_1_layout.addWidget(self.Block_write_length_input)
        groupbox_4_1_layout.addWidget(self.checkbox22)
        groupbox_4_1_layout.addWidget(self.Block_write_EPC_offset_input)
        groupbox_4_1_layout.addWidget(self.checkbox23)
        groupbox_4_1_layout.addWidget(self.Block_write_USER_offset_input)
        groupbox_4_1_layout.addWidget(self.checkbox24)
        groupbox_4_1.setLayout(groupbox_4_1_layout)

    ######## --- 4.2 Block Erase
        groupbox_4_2 = QGroupBox("Block Erase")
        groupbox_4_2_layout = QVBoxLayout()
        
        self.Block_erase_length_input = QLineEdit()
        self.Block_erase_length_input.setMaxLength(5)
        self.Block_erase_length_input.setPlaceholderText("Block Erase Size 0-255")
        hex_regex = QRegExp("^[0-9]{1,3}$")
        hex_validator = QRegExpValidator(hex_regex)
        self.Block_erase_length_input.setValidator(hex_validator)
        self.Block_erase_length_input.setFixedWidth(self.Block_erase_length_input.fontMetrics().horizontalAdvance(" 123456789ABCDEF "))

        self.Block_erase_EPC_offset_input = QLineEdit()
        self.Block_erase_EPC_offset_input.setMaxLength(2)
        self.Block_erase_EPC_offset_input.setPlaceholderText("Block Erase EPC offset adress (h)")
        hex_regex = QRegExp("^[0-9A-Fa-f]+$")
        hex_validator = QRegExpValidator(hex_regex)
        self.Block_erase_EPC_offset_input.setValidator(hex_validator)
        self.Block_erase_EPC_offset_input.setFixedWidth(self.Block_erase_EPC_offset_input.fontMetrics().horizontalAdvance(" 123456789ABCDEF "))

        self.Block_erase_USER_offset_input = QLineEdit()
        self.Block_erase_USER_offset_input.setMaxLength(5)
        self.Block_erase_USER_offset_input.setPlaceholderText("Block Erase USER offset adress (h)")
        hex_regex = QRegExp("^[0-9A-Fa-f]+$")
        hex_validator = QRegExpValidator(hex_regex)
        self.Block_erase_USER_offset_input.setValidator(hex_validator)
        self.Block_erase_USER_offset_input.setFixedWidth(self.Block_erase_USER_offset_input.fontMetrics().horizontalAdvance(" 123456789ABCDEF "))

        self.checkbox25 = QCheckBox("Variable size Block Erase")
        self.checkbox26 = QCheckBox("Block Erase EPC address alignment")
        self.checkbox27 = QCheckBox("Block Erase USER address alignment")

        self.group4_2_checkboxes = [self.checkbox25, self.checkbox26, self.checkbox27]
        
        groupbox_4_2_layout.addWidget(self.Block_erase_length_input)
        groupbox_4_2_layout.addWidget(self.checkbox25)
        groupbox_4_2_layout.addWidget(self.Block_erase_EPC_offset_input)
        groupbox_4_2_layout.addWidget(self.checkbox26)
        groupbox_4_2_layout.addWidget(self.Block_erase_USER_offset_input)
        groupbox_4_2_layout.addWidget(self.checkbox27)
        groupbox_4_2.setLayout(groupbox_4_2_layout)

        groupbox_4_layout.addWidget(groupbox_4_1)
        groupbox_4_layout.addWidget(groupbox_4_2)
        groupbox_4.setLayout(groupbox_4_layout)

    ######## --- Groupbox 5: USER mem and block permalock ---
        groupbox_5 = QGroupBox("USER mem and block permalock")
        groupbox_5_layout = QVBoxLayout()

        self.USER_memory_size = QLineEdit()
        self.USER_memory_size.setMaxLength(5)
        self.USER_memory_size.setPlaceholderText("USER memory size")
        hex_regex = QRegExp("^[0-9]{1,5}$")
        hex_validator = QRegExpValidator(hex_regex)
        self.USER_memory_size.setValidator(hex_validator)
        self.USER_memory_size.setFixedWidth(self.USER_memory_size.fontMetrics().horizontalAdvance(" 123456789ABCDEF "))

        self.Block_permalock_size = QLineEdit()
        self.Block_permalock_size.setMaxLength(5)
        self.Block_permalock_size.setPlaceholderText("Block permalock block size")
        hex_regex = QRegExp("^[0-9]{1,5}$")
        hex_validator = QRegExpValidator(hex_regex)
        self.Block_permalock_size.setValidator(hex_validator)
        self.Block_permalock_size.setFixedWidth(self.Block_permalock_size.fontMetrics().horizontalAdvance(" 123456789ABCDEF "))
        
        groupbox_5_layout.addWidget(self.USER_memory_size)
        groupbox_5_layout.addWidget(self.Block_permalock_size)
        groupbox_5.setLayout(groupbox_5_layout)

    ######## --- GroupBox 6: Lock bit segment ---
        groupbox_6 = QGroupBox("Lock bit segment")
        groupbox_6_layout = QVBoxLayout()

        self.checkbox28 = QCheckBox("File_0 memory (permalock)")
        self.checkbox29 = QCheckBox("File_0 memory (password write)")
        self.checkbox30 = QCheckBox("TID memory (permalock)")
        self.checkbox31 = QCheckBox("TID memory (password write)")
        self.checkbox32 = QCheckBox("EPC memory (permalock)")
        self.checkbox33 = QCheckBox("EPC memory (password write)")

        self.group6_checkboxes = [self.checkbox28, self.checkbox29, self.checkbox30, self.checkbox31, self.checkbox32, self.checkbox33]
        
        groupbox_6_layout.addWidget(self.checkbox28)
        groupbox_6_layout.addWidget(self.checkbox29)
        groupbox_6_layout.addWidget(self.checkbox30)
        groupbox_6_layout.addWidget(self.checkbox31)
        groupbox_6_layout.addWidget(self.checkbox32)
        groupbox_6_layout.addWidget(self.checkbox33)
        groupbox_6.setLayout(groupbox_6_layout)

######## ---- GroupBox formatting
        #set max width if needed
        groupbox_1.setMaximumWidth(350)
        groupbox_5.setMaximumWidth(200)
        # Additional groupbox width adjustments can be applied as needed.

        # Add all group boxes to the horizontal layout
        checkboxes_layout.addWidget(groupbox_1)
        checkboxes_layout.addWidget(groupbox_2)
        checkboxes_layout.addWidget(groupbox_3)
        checkboxes_layout.addWidget(groupbox_4)
        checkboxes_layout.addWidget(groupbox_5)
        checkboxes_layout.addWidget(groupbox_6)
        checkboxes_widget.setLayout(checkboxes_layout)
        scroll_area.setWidget(checkboxes_widget)
        layout.addWidget(scroll_area)

        ########---- Create two output fields: one binary, one hex
        self.output_field = QPlainTextEdit()
        self.output_field.setReadOnly(True)
        self.output_field.setLineWrapMode(self.output_field.WidgetWidth)
        self.output_field.setFixedHeight(100)
        layout.addWidget(self.output_field)

        self.hex_output_field = QPlainTextEdit()
        self.hex_output_field.setReadOnly(True)
        self.hex_output_field.setLineWrapMode(self.hex_output_field.WidgetWidth)
        self.hex_output_field.setFixedHeight(100)
        layout.addWidget(self.hex_output_field)

        self.setLayout(layout)
        self.setWindowTitle("TID encoder V2.0") # set window name

        ########---- Connect signals to update output ----
        # Group 1 signals
        self.checkbox1.stateChanged.connect(self.update_output)
        self.checkbox2.stateChanged.connect(self.update_output)
        self.checkbox3.stateChanged.connect(self.update_output)
        self.mdid_input.textChanged.connect(self.update_output)
        self.tmn_input.textChanged.connect(self.update_output)
        # Connect dropdown signals if they affect output:
        self.mdid_dropdown.currentIndexChanged.connect(self.update_output)
        self.tmn_dropdown.currentIndexChanged.connect(self.update_output)

        # Connect signals for group 2 checkboxes.
        for cb in self.group2_checkboxes:
            cb.stateChanged.connect(self.update_output)
        self.Serial_length_input.textChanged.connect(self.update_output)
        self.Serial_value_input.textChanged.connect(self.update_output)

        # Connect signals for group 3 checkboxes.
        for cb in self.group3_checkboxes:
            cb.stateChanged.connect(self.update_output)
        self.EPC_length_input.textChanged.connect(self.update_output)

        # Connect signals for group 4.1
        self.Block_write_length_input.textChanged.connect(self.update_output)
        self.Block_write_EPC_offset_input.textChanged.connect(self.update_output)
        self.Block_write_USER_offset_input.textChanged.connect(self.update_output)
        for cb in self.group4_1_checkboxes:
            cb.stateChanged.connect(self.update_output)

        # Connect signals for group 4.2
        self.Block_erase_length_input.textChanged.connect(self.update_output)
        self.Block_erase_EPC_offset_input.textChanged.connect(self.update_output)
        self.Block_erase_USER_offset_input.textChanged.connect(self.update_output)
        for cb in self.group4_2_checkboxes:
            cb.stateChanged.connect(self.update_output)

        self.Block_write_length_input.textChanged.connect(lambda: self.check_and_cap_length_255(self.Block_write_length_input))
        self.Block_erase_length_input.textChanged.connect(lambda: self.check_and_cap_length_255(self.Block_erase_length_input))

        # Connect signals for group 5 fields
        self.USER_memory_size.textChanged.connect(self.update_output)
        self.Block_permalock_size.textChanged.connect(self.update_output)
        self.USER_memory_size.textChanged.connect(lambda: self.check_and_cap_length_65535(self.USER_memory_size))
        self.Block_permalock_size.textChanged.connect(lambda: self.check_and_cap_length_65535(self.Block_permalock_size))

        # Connect signals for group 6 checkboxes.
        for cb in self.group6_checkboxes:
            cb.stateChanged.connect(self.update_output)

        ######## ---- Lock and set checkboxes as needed
        self.checkbox6.setChecked(False)
        self.checkbox6.setEnabled(False)

        # Connect signals to update output and TMN options.
        self.mdid_input.textChanged.connect(self.update_output)
        self.tmn_input.textChanged.connect(self.update_output)
        self.mdid_dropdown.currentIndexChanged.connect(lambda index: self.update_tmn_options())
        self.tmn_dropdown.currentIndexChanged.connect(self.update_output)
        self.mdid_dropdown.currentIndexChanged.connect(self.update_mdid_input)
        self.tmn_dropdown.currentIndexChanged.connect(self.update_tmn_input)
        # (Other signal connections remain unchanged)

        self.update_output()


######## ---- JSON file item fetching
########
    def load_options(self):
        """
        Load dropdown options from the JSON file "Digits'_mdid_list.json".
        For the MDID combo box, display the designer's 'manufacturer' and return its 'mdid binary'.
        """
        data = load_json_data()
        self.mdid_dropdown.addItem("")      # Blank option at the top
        if data is None:
            return

        self.json_data = data               # Store the JSON data for later use.
        designers = data.get("registeredMaskDesigners", [])
        
        for designer in designers:          # Populate MDID dropdown
            manufacturer = designer.get("manufacturer", "Unknown Manufacturer")
            mdid = designer.get("mdid", "")
            self.mdid_dropdown.addItem(manufacturer, mdid)
        
        self.update_tmn_options()           # Update TMN options based on the currently selected MDID.


    def update_mdid_input(self):
        selected_mdid = self.mdid_dropdown.currentData()  # Get MDID binary
        if selected_mdid:
            self.mdid_input.setText(selected_mdid)
            self.mdid_input.setDisabled(True)  # Disable input field
        else:
            self.mdid_input.clear()  # Clear if no manufacturer selected
            self.mdid_input.setDisabled(False)  # Enable input field


    def update_tmn_options(self):
        """
        Update the TMN dropdown to display only chip models for the manufacturer currently selected.
        """
        self.tmn_dropdown.clear()
        self.tmn_dropdown.addItem("User Input")  # Blank option at the top
        if not self.json_data:
            return
        designers = self.json_data.get("registeredMaskDesigners", [])
        # Get the mdid value of the currently selected manufacturer.
        current_index = self.mdid_dropdown.currentIndex()
        current_mdid = self.mdid_dropdown.itemData(current_index)


        for designer in designers:
            if designer.get("mdid") == current_mdid:
                chips = designer.get("chips", [])
                if chips:
                    for chip in chips:
                        modelName = chip.get("modelName", "Unknown Model")
                        tmnHex = chip.get("tmnHex", "")
                        self.tmn_dropdown.addItem(modelName, tmnHex)
                else:
                    self.tmn_dropdown.addItem("No chips available", "")
                break
    

    def update_tmn_input(self):
        selected_tmn = self.tmn_dropdown.currentData()  # Get TMN hex from JSON
        if selected_tmn:
            self.tmn_input.setText(selected_tmn)
            self.tmn_input.setDisabled(True)  # Disable input field
        else:
            self.tmn_input.clear()  # Clear if no chip selected
            self.tmn_input.setDisabled(False)  # Enable input field




######### ---- max value caps for certain inputs
#########
    def check_and_cap_length_255(self, line_edit):
        # If the text is not empty, convert it to an integer and cap at 255. 255(10) = 1111 1111 (2) = FF(h)
        text = line_edit.text()
        if text:
            value = int(text)
            if value > 255:
                # Temporarily block signals to avoid recursion.
                line_edit.blockSignals(True)
                line_edit.setText("255")
                line_edit.blockSignals(False)
    
    def check_and_cap_length_65535(self, line_edit):
        # If the text is not empty, convert it to an integer and cap at 65535. 65535(10) = 1111 1111 1111 1111(2) = FFFF(h)
        text = line_edit.text()
        if text:
            value = int(text)
            if value > 65535:
                # Temporarily block signals to avoid recursion.
                line_edit.blockSignals(True)
                line_edit.setText("65535")
                line_edit.blockSignals(False)




#############################################################################################################################################
#########    OUTPUT ENCODING   ##############################################################################################################
#############################################################################################################################################

    def update_output(self):
        # 0. Start with a fixed prefix "11100010" (indicates GS1 spec) see EM4325 datasheet for an exmple of other prefixes out there tht are not GS1 spec
        final_output = "11100010"
        XTID_length = 8

        # 1. Group 1 bits: for each checkbox in group 1, "1" if checked, "0" if not.
        group1_bits = (
            ("1" if self.checkbox1.isChecked() else "0") +  # Xtid bit
            ("1" if self.checkbox2.isChecked() else "0") +  # F bit
            ("1" if self.checkbox3.isChecked() else "0")    # S bit
        )
        final_output += group1_bits
        XTID_length += 3    # keep track of the amount of bits that are added throughout the operations to make sure there aren't any mistakes, and to inform the user at the end

        # 2. MDID: pad its contents to 9 characters and add to the output.
        mdid_text = self.mdid_input.text()
        mdid_padded = mdid_text.ljust(9, '0')
        final_output += mdid_padded
        XTID_length += 9

        # 3. TMN: pad to 3 characters, convert from hex to a 12-bit binary string, and add to output.
        tmn_text = self.tmn_input.text().ljust(3, '0')
        tmn_binary = format(int(tmn_text, 16), '012b')
        final_output += tmn_binary
        XTID_length += 12

        # 4. Process Group 2 and Serial fields only if []XTID (checkbox1) is checked. if it's not checked, none of the following groups will be processed. note that some XTIDs (EM4325)
        if self.checkbox1.isChecked():
            # 4.1 Add Serial Number fields.   Serial number length: if empty, default to "0". Then pad to 3 characters.
            serial_length_text = self.Serial_length_input.text()
            if serial_length_text == "":
                serial_length_text = "0"
            serial_length_text = serial_length_text.ljust(3, '0')
            final_output += serial_length_text
            XTID_length += 3

            # 4.2 Group 2 bits: for each checkbox in group 2, "1" if checked, "0" if not.
            group2_bits = (
                ("1" if self.checkbox10.isChecked() else "0") + # User Memory and Block Perma Lock Segment Present
                ("1" if self.checkbox9.isChecked() else "0") +  # BlockWrite and BlockErase Segment Present
                ("1" if self.checkbox8.isChecked() else "0") +  # Optional Command Support Segment Present
                ("1" if self.checkbox7.isChecked() else "0")    # Lock bit segment
            )
            final_output += group2_bits
            final_output += ("00000000")  # XTID HEADER RFU, 8 bits
            final_output += ("1" if self.checkbox6.isChecked() else "0") # Extended header present. see at the bottom of `def __init__(self):` why this checkbox is set to 0 and locked by default.

            XTID_length += 13

            # 5 check if serial number should be present, and add it if it should.
            N = int("{}".format(serial_length_text), 2)
            if N != 0:      # calculate serial number length in bits relative to the serial length text field
                serial_number_length = 48 + (16 * (N - 1))
                self.Serial_value_input.setMaxLength(serial_number_length// 4)
                XTID_length += serial_number_length
                # Convert the serial number data to binary: 
                serial_value_text = self.Serial_value_input.text().ljust(serial_number_length // 4 , '0')
                serial_value_binary = format(int(serial_value_text, 16), '0{}b'.format(serial_number_length))
                final_output += serial_value_binary
                self.Serial_value_input.setEnabled(True)
            else:           # if serial length text field is 0, don't add a serial number to the TID, and block the serial number field
                serial_number_length = 0
                self.Serial_value_input.setMaxLength(serial_number_length)
                self.Serial_value_input.clear()
                self.Serial_value_input.setEnabled(False)
            

            # 6. Process Group 3 only if []extended header present(checkbox6) is checked.
            if self.checkbox8.isChecked(): #### OPTIONAL COMMANDS ####
                final_output += ("000")     # Optional Commands RFU
                group3_bits = (
                ("1" if self.checkbox21.isChecked() else "0") + # Block PermaLock support
                ("1" if self.checkbox20.isChecked() else "0") + # Block Write support
                ("1" if self.checkbox19.isChecked() else "0") + # Block Erase support
                ("1" if self.checkbox18.isChecked() else "0") + # Phase Jitter Modulation (PJM) support
                ("1" if self.checkbox17.isChecked() else "0") + # Auto UMI support
                ("1" if self.checkbox16.isChecked() else "0") + # Seperate lockbits
                ("1" if self.checkbox15.isChecked() else "0") + # Access
                ("1" if self.checkbox14.isChecked() else "0")   # recom support
                )
                final_output += group3_bits
                final_output += self.EPC_length_input.text().ljust(5, '0')


                # 7. Process group 4.2 only if []block erase support(checkbox20) is checked
            if self.checkbox9.isChecked():

                final_output += ("00000") # Block erase RFU

                final_output += ("1" if self.checkbox27.isChecked() else "0") # Block erase USER address alignment

                Block_erase_USER_offset = self.Block_erase_USER_offset_input.text().ljust(2 , '0') #hex
                if Block_erase_USER_offset == "":
                    Block_erase_USER_offset = "00"
                final_output += format(int(Block_erase_USER_offset, 16), '08b')

                final_output += ("1" if self.checkbox26.isChecked() else "0") # Block erase EPC address alignment

                Block_erase_EPC_offset = self.Block_erase_EPC_offset_input.text().ljust(2 , '0') #hex
                final_output += format(int(Block_erase_EPC_offset, 16), '08b')

                final_output += ("1" if self.checkbox25.isChecked() else "0") # Variable size Block erase

                Block_erase_length= self.Block_erase_length_input.text().rjust(3, '0')  #decimal

                final_output += format(int(Block_erase_length, 10), '08b')

            # 8. Process group 4.1 only if []block write support(checkbox20) is checked
                final_output += ("00000") # Block Write RFU

                final_output += ("1" if self.checkbox24.isChecked() else "0") # Block Write USER address alignment

                Block_write_USER_offset = self.Block_write_USER_offset_input.text().ljust(2 , '0') #hex
                final_output += format(int(Block_write_USER_offset, 16), '08b')

                final_output += ("1" if self.checkbox23.isChecked() else "0") # Block Write EPC address alignment

                Block_write_EPC_offset = self.Block_write_EPC_offset_input.text().ljust(2 , '0') #hex
                final_output += format(int(Block_write_EPC_offset, 16), '08b')

                final_output += ("1" if self.checkbox22.isChecked() else "0") # Variable size Block Write
                
                Block_write_length= self.Block_write_length_input.text().ljust(3 , '0')  #decimal
                final_output += format(int(Block_write_length, 10), '08b')
                    

            # 9. Process group 5 only if []User Memory and Block Perma Lock Segment Present (checkbox10) is checked
            if self.checkbox10.isChecked():
                USER_memory_size = self.USER_memory_size.text().rjust(5 , '0') # decimal; USER memory size : number of 16 bit words in USER memory
                if int(USER_memory_size) > 65535 :
                    USER_memory_size = "65535"
                final_output += format(int(USER_memory_size, 10), '016b')

                if self.checkbox8.isChecked() and (not self.checkbox21.isChecked()):
                    final_output += "0000000000000000"
                else:
                    Block_permalock_size = self.Block_permalock_size.text().rjust(5 , '0') # decimal; If non-zero, the size in words of each block that may be block permalocked. zero does not mean it isn't supported, just not described in here.
                    if int(Block_permalock_size) > 65535 :
                        Block_permalock_size = "65535"
                    final_output += format(int(Block_permalock_size, 10), '016b')
        # 10. Process group 6 only if []S (checkbox2) is checked
        if self.checkbox2.isChecked():
            final_output += ("1" if self.checkbox28.isChecked() else "0") # File_0 memory (permalock)
            final_output += ("1" if self.checkbox29.isChecked() else "0") # File_0 memory (password write)
            final_output += ("1" if self.checkbox30.isChecked() else "0") # TID memory (permalock)
            final_output += ("1" if self.checkbox31.isChecked() else "0") # TID memory (password write)
            final_output += ("1" if self.checkbox32.isChecked() else "0") # EPC memory (permalock)
            final_output += ("1" if self.checkbox33.isChecked() else "0") # EPC memory (password write)
            final_output += "0000000000"


######### --- Update outputs
#########
        #update binary ouptut
        self.XTID_output = final_output
        self.output_field.setPlainText(f"{self.XTID_output}\n"
                                       f"amount of bits: {len(final_output)}\n") # add info on the amount of bits in the output

        # Convert the complete binary output to hexadecimal.
        hex_width = (len(final_output)) // 4
        hex_output = format(int(final_output, 2), '0{}X'.format(hex_width))
        self.hex_output_field.setPlainText(f"{hex_output}\n"
                                           f"number of bytes: {len(hex_output)}\n"          # add info on the amount of bytes in the output
                                           f"number of words: {int(len(hex_output)/2)}\n")  # add info on the amount of words (2 bytes) in the output

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TID_encoder()
    window.show()
    sys.exit(app.exec_())
