import sys
import json
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QRegularExpressionValidator

# Remove non-printable characters except spaces, newlines, and tabs
def clean_json_data(raw_data):
    return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', raw_data)

# Load JSON data
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

# Decode the XTID
def extract_values(xtid):
    if len(xtid) < 8:
        return "Error: Input must be at least 8 hex characters.", ""

    xtid_info = ""
    # Convert entire input to binary while preserving leading zeros
    bin_xtid = bin(int(xtid, 16))[2:].zfill(len(xtid) * 4)

    # Extract short TID components
    X = bin_xtid[8]  # XTID presence bit
    S = bin_xtid[9]
    F = bin_xtid[10]
    MDID_binary = bin_xtid[11:20]
    MDID_hex = hex(int(MDID_binary, 2))[2:].zfill(3)
    TMN_binary = bin_xtid[20:32]
    TMN_hex = hex(int(TMN_binary, 2))[2:].zfill(3)

    decoded_info = (f"XTID bit: {X}, Security bit: {S}, File bit: {F}\n"
                    f"MDID: {MDID_binary} (binary), {MDID_hex} (hex)\n"
                    f"TMN: {TMN_binary} (binary), {TMN_hex} (hex)\n")

    # Check if XTID is present based on X bit
    if X == '0':
        return decoded_info, "XTID bit set to 0, no XTID present / XTID data ignored."

    # If XTID is 8 or fewer characters (short TID) but X = 1, indicating presence of an XTID, display a message
    if len(xtid) <= 8 and X == '1':
        return decoded_info, "XTID bit is set to 1, but no XTID input provided."

    # Decode XTID header components -- 20(h) to 2F(h)
    extended_header_present = bin_xtid[int("20", 16)+16] == '1'
    rfu_XTID_HEADER = bin_xtid[int("20", 16)+6:int("20", 16)+16]
    user_memory_present = bin_xtid[int("20", 16)+5] == '1'
    block_write_present = bin_xtid[int("20", 16)+4] == '1'
    optional_command_present = bin_xtid[int("20", 16)+3] == '1'
    serialization_bits = bin_xtid[int("20", 16):int("20", 16)+3]

    
    xtid_info += (f"Extended Header Present: {extended_header_present}\n"
                 f"RFU: {rfu_XTID_HEADER}\n"
                 f"User Memory Segment Present: {user_memory_present}\n"
                 f"BlockWrite and BlockErase Segment Present: {block_write_present}\n"
                 f"Optional Command Support Segment Present: {optional_command_present}\n")


    # Calculate serialization info -- 30(h) to 30(h)+48+16*(N - 1) (( or 30(h)+serial_number_length ))
    if serialization_bits != '000':
        N = int(serialization_bits, 2)
        serial_number_length = 48 + 16 * (N - 1)
        serial_number_bin = bin_xtid[int("30", 16):int("30", 16)+ serial_number_length].zfill(serial_number_length)
        serial_number_hex = hex(int(serial_number_bin, 2))[2:].zfill(serial_number_length // 4).upper()
        serial_number_info = f"Serialization length: {serial_number_length} bits"
        serial_number_output = f"Serial Number: {serial_number_hex}"
    else:
        serial_number_length = 0
        serial_number_info = "XTID does not include a unique serial number."
        serial_number_output = ""


    xtid_info += (f"Serialization Bits: {serialization_bits}\n" #add the outputs to the display variable
                  f"{serial_number_info}\n{serial_number_output}\n")

    if len(xtid)>= 48 and bin_xtid[8] == '1' and serialization_bits != '000':
        xtid_info +=(f"\n STID URI:  urn:epc:stid:x{MDID_hex}.x{TMN_hex}.x{serial_number_hex}\n\n")# print STID-URI


    # Optional commands 30(h)+serial_number_length to 3F(h)+serial_number_length
    if optional_command_present == 1:
        bin_max_epc_size = bin_xtid[int("3F", 16)+serial_number_length-4:int("3F", 16)+serial_number_length+1]
        max_epc_size = int(bin_xtid[int("3F", 16)+serial_number_length-4:int("3F", 16)+serial_number_length+1] ,2) * 16
        recom_support = bin_xtid[int("3F", 16)+serial_number_length-5]          # If this bit is set, the tag supports recommissioning as specified in [UHFC1G2].
        access = bin_xtid[int("3F", 16)+serial_number_length-6]
        seperate_lockbits = bin_xtid[int("3F", 16)+serial_number_length-7]
        auto_UMI_support = bin_xtid[int("3F", 16)+serial_number_length-8]       # UMI: User Memory Indicator
        PJM_support = bin_xtid[int("3F", 16)+serial_number_length-9]
        blockErase_supported = bin_xtid[int("3F", 16)+serial_number_length-10]
        blockWrite_supported = bin_xtid[int("3F", 16)+serial_number_length-11]
        blockPermaLock_supported = bin_xtid[int("3F", 16)+serial_number_length-12]
        rfu_optional_commands = bin_xtid[int("3F", 16)+serial_number_length-15:int("3F", 16)+serial_number_length-12]
        
        xtid_info +=(f"\n" #add the outputs to the display variable
                     f" OPTIONAL COMMANDS \n"
                     f"max EPC size bits: {bin_max_epc_size}\n"
                     f"max EPC size: {max_epc_size} bits\n"
                     f"recomissioning support: {recom_support}\n"
                     f"access: {access} bits\n"
                     f"seperate_lockbits: {seperate_lockbits}\n"
                     f"auto UMI support: {auto_UMI_support}\n"
                     f"PJM support: {PJM_support}\n"
                     f"Block Erase support: {blockErase_supported}\n"
                     f"Block Write support: {blockWrite_supported}\n"
                     f"Block Perma-lock support: {blockPermaLock_supported}\n"
                     f"RFU: {rfu_optional_commands}\n")
    else:
        xtid_info +=(f"\n"
                     f"no optional commands\n")


    # Block Erase Support 40(h)+serial_number_length to 5F(h)+serial_number_length
    if blockErase_supported == 1:
        Block_erase_size = bin_xtid[int("5F",16)+serial_number_length-7:int("5F",16)+serial_number_length+1]
        Block_erase_variable_size = bin_xtid[int("5F",16)+serial_number_length-8]
        Block_erase_EPC_offset = bin_xtid[int("5F",16)+serial_number_length-16:int("5F",16)+serial_number_length-8]
        Block_erase_no_EPC_alignement = bin_xtid[int("5F",16)+serial_number_length-17]
        Block_erase_User_offset = bin_xtid[int("5F",16)+serial_number_length-25:int("5F",16)+serial_number_length-17]
        Block_erase_no_User_alignement = bin_xtid[int("5F",16)+serial_number_length-26]
        Block_erase_RFU = bin_xtid[int("5F",16)+serial_number_length-31:int("5F",16)+serial_number_length-26]

        xtid_info +=(f"\n"
                     f"Size of Block Erase: {Block_erase_size}\n"
                     f"Variable size Block Erase bit: {Block_erase_variable_size}\n"
                     f"Block Erase EPC address offset: {Block_erase_EPC_offset}\n"
                     f"No Block Erase EPC address alignement: {Block_erase_no_EPC_alignement}\n"
                     f"Block Erase USER address offset: {Block_erase_User_offset}\n"
                     f"No Block Erase USER address alignement: {Block_erase_no_User_alignement}\n"
                     f"RFU: {Block_erase_RFU}\n")

    else:
        xtid_info +=(f"\n"
                     f"no Block Erase support\n")


    # Block Write Support 60(h)+serial_number_length to 7F(h)+serial_number_length
    if blockWrite_supported == 1:
        Block_write_size = bin_xtid[int("7F",16)+serial_number_length-7:int("7F",16)+serial_number_length+1]
        Block_write_variable_size = bin_xtid[int("7F",16)+serial_number_length-8]
        Block_write_EPC_offset = bin_xtid[int("7F",16)+serial_number_length-16:int("7F",16)+serial_number_length-8]
        Block_write_no_EPC_alignement = bin_xtid[int("7F",16)+serial_number_length-17]
        Block_write_User_offset = bin_xtid[int("7F",16)+serial_number_length-25:int("7F",16)+serial_number_length-17]
        Block_write_no_User_alignement = bin_xtid[int("7F",16)+serial_number_length-26]
        Block_write_RFU = bin_xtid[int("7F",16)+serial_number_length-31:int("7F",16)+serial_number_length-26]

        xtid_info +=(f"\n"
                     f"Size of Block Write: {Block_write_size}\n"
                     f"Variable size Block Write bit: {Block_write_variable_size}\n"
                     f"Block Write EPC address offset: {Block_write_EPC_offset}\n"
                     f"No Block Write EPC address alignement: {Block_write_no_EPC_alignement}\n"
                     f"Block Write USER address offset: {Block_write_User_offset}\n"
                     f"No Block Write USER address alignement: {Block_write_no_User_alignement}\n"
                     f"RFU: {Block_write_RFU}\n")

    else:
        xtid_info +=(f"\n"
                     f"no Block Write support\n")


    # User Memory info 80(h)+serial_number_length to 8F(h)+serial_number_length
    if user_memory_present == 1:
        user_memory_size = bin_xtid[int("80",16)+serial_number_length:int("8F",16)+serial_number_length+1]
        
        xtid_info +=(f"\n"
                     f"USER memory size: {user_memory_size}\n")

    else:
        xtid_info +=(f"\n"
                     f"no USER memory present\n")


    # Permalock info 90(h)+serial_number_length to 9F(h)+serial_number_length
    if blockPermaLock_supported == 1:
        blockPermaLock_size = bin_xtid[int("90",16)+serial_number_length:int("9F",16)+serial_number_length+1]
        
        xtid_info +=(f"\n"
                     f"BlockPermaLock block size: {user_memory_size}\n")

    else:
        xtid_info +=(f"\n"
                     f"no BlockPermaLock size described\n")


    # Lock bit segment A0(h)+serial_number_length to AF(h)+serial_number_length
    if S == 1:
        File0_permalock = bin_xtid[int("AF",16)+serial_number_length-0]
        File0_PWD_Write = bin_xtid[int("AF",16)+serial_number_length-1]
        TID_memory_permalock = bin_xtid[int("AF",16)+serial_number_length-2]
        TID_memory_PWD_Write = bin_xtid[int("AF",16)+serial_number_length-3]
        EPC_memory_permalock = bin_xtid[int("AF",16)+serial_number_length-4]
        EPC_memory_PWD_Write = bin_xtid[int("AF",16)+serial_number_length-5]
        Lock_bit_RFU = bin_xtid[int("AF",16)+serial_number_length-15:int("AF",16)+serial_number_length-5]

        xtid_info +=(f"File_0 memory permalock: {File0_permalock}\n"
                     f"File_0 memory password write: {File0_PWD_Write}\n"
                     f"TID memory permalock: {TID_memory_permalock}\n"
                     f"TID memory password write: {TID_memory_PWD_Write}\n"
                     f"EPC memory permalock: {EPC_memory_permalock}\n"
                     f"EPC memory password write: {EPC_memory_PWD_Write}\n"
                     f"RFU: {Lock_bit_RFU}\n")

    else:
        xtid_info +=(f"\n"
                     f"no optional lock bit segment\n")

    return decoded_info, xtid_info

# Main window
class SearchWindow(QWidget):
    def __init__(self, data):
        super().__init__()

        self.setWindowTitle("XTID Search Engine")
        self.setGeometry(100, 100, 600, 750)
        
        self.data = data
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Single Input Field for XTID
        input_label = QLabel("Enter the XTID (8+ hex characters):")
        self.xtid_input = QLineEdit(self)
        self.xtid_input.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9A-Fa-f\\s]*"), self))
        self.xtid_input.textChanged.connect(self.to_uppercase)
        main_layout.addWidget(input_label)
        main_layout.addWidget(self.xtid_input)

        # Search Button
        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.on_search)
        main_layout.addWidget(self.search_button)

        # Chip Information Label
        chip_info_label = QLabel("Chip Information:")
        main_layout.addWidget(chip_info_label)

        # Output Display
        self.result_display_left = QTextEdit(self)
        self.result_display_left.setReadOnly(True)
        self.result_display_right = QTextEdit(self)
        self.result_display_right.setReadOnly(True)
        main_layout.addWidget(self.result_display_left)
        main_layout.addWidget(self.result_display_right)

        self.setLayout(main_layout)
        self.xtid_input.returnPressed.connect(self.on_search)

    def to_uppercase(self):
        sender = self.sender()
        cursor_pos = sender.cursorPosition()  # Save cursor position
        sender.setText(sender.text().upper())  # Modify text
        sender.setCursorPosition(cursor_pos)  # Restore cursor position


    def on_search(self):
        xtid = self.xtid_input.text().strip().replace(" ", "")  # Remove spaces

        if len(xtid) < 8:
            self.result_display_left.setText("XTID must be at least 8 hex characters.")
            self.result_display_right.setText("")
            return

        result, resultXTID = self.search_xtid(xtid)
        self.result_display_left.setText(result)
        self.result_display_right.setText(resultXTID)

    def search_xtid(self, xtid):
        if self.data is None:
            return "Error: No data available to search.", ""

        decoded_info, xtid_info = extract_values(xtid)
        result = decoded_info + "\n\n"
        resultXTID = xtid_info

        # Extract MDID and TMN from decoded values
        MDID_binary = decoded_info.split("\n")[1].split(": ")[1].split(" ")[0]
        TMN_binary = decoded_info.split("\n")[2].split(": ")[1].split(" ")[0]

        try:
            for designer in self.data.get('registeredMaskDesigners', []):
                if designer['mdid'] == MDID_binary:
                    result += (f"Manufacturer: {designer['manufacturer']}\n"
                               f"Manufacturer URL: {designer['manufacturerUrl']}\n\n")

                    for chip in designer.get('chips', []):
                        if chip['tmnBinary'] == TMN_binary:
                            result += (f"Model Name: {chip.get('modelName', 'N/A')}\n\n"
                                       f"Product URL: {chip.get('productUrl', 'N/A')}\n\n"
                                       f"Notes: {chip.get('note', 'N/A')}")
                            return result, resultXTID

            return result + "No matching MDID found.", resultXTID
        except KeyError as e:
            return f"Error: Missing key - {e}", ""

def main():
    app = QApplication(sys.argv)
    data = load_json_data()
    window = SearchWindow(data)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
