from number_reader import read
from iron_token import Token
import re


class Parser:
    _ADDR_MODE_LENGTHS = {
        "IMPLIED": 1, "ACCUMULATOR": 1, "ZERO_PAGE": 2, "ZERO_PAGE_X": 2, "ZERO_PAGE_Y": 2, "RELATIVE": 2,
        "IMMEDIATE": 2, "ABSOLUTE": 3, "ABSOLUTE_X": 3, "ABSOLUTE_Y": 3, "INDIRECT": 3, "X_INDIRECT": 3, "INDIRECT_Y": 3
    }
    _INSTRUCTIONS = {
        "ADC": {
            "IMMEDIATE": 0x69, "ZERO_PAGE": 0x65, "ZERO_PAGE_X": 0x75, "ABSOLUTE": 0x6D, "ABSOLUTE_X": 0x7D,
            "ABSOLUTE_Y": 0x79, "X_INDIRECT": 0x61, "INDIRECT_Y": 0x71
        },
        "AND": {
            "IMMEDIATE": 0x29, "ZERO_PAGE": 0x25, "ZERO_PAGE_X": 0x35, "ABSOLUTE": 0x2D, "ABSOLUTE_X": 0x3D,
            "ABSOLUTE_Y": 0x39, "X_INDIRECT": 0x21, "INDIRECT_Y": 0x31
        },
        "ASL": {"ACCUMULATOR": 0x0A, "ZERO_PAGE": 0x6, "ZERO_PAGE_X": 0x16, "ABSOLUTE": 0x0E, "ABSOLUTE_X": 0x1E},
        "BCC": {"RELATIVE": 0x90},
        "BCS": {"RELATIVE": 0xB0},
        "BEQ": {"RELATIVE": 0xF0},
        "BIT": {"ZERO_PAGE": 0x24, "ABSOLUTE": 0x2C},
        "BMI": {"RELATIVE": 0x30},
        "BNE": {"RELATIVE": 0xD0},
        "BPL": {"RELATIVE": 0x10},
        "BRK": {"IMPLIED": 0x00},
        "BVC": {"RELATIVE": 0x50},
        "BVS": {"RELATIVE": 0x70},
        "CLC": {"IMPLIED": 0x18},
        "CLD": {"IMPLIED": 0xD8},
        "CLI": {"IMPLIED": 0x58},
        "CLV": {"IMPLIED": 0xB8},
        "CMP": {
            "IMMEDIATE": 0xC9, "ZERO_PAGE": 0xC5, "ZERO_PAGE_X": 0xD5, "ABSOLUTE": 0xCD, "ABSOLUTE_X": 0xDD,
            "ABSOLUTE_Y": 0xD9, "X_INDIRECT": 0xC1, "INDIRECT_Y": 0xD1
        },
        "CPX": {"IMMEDIATE": 0xE0, "ZERO_PAGE": 0xE4, "ABSOLUTE": 0xEC},
        "CPY": {"IMMEDIATE": 0xC0, "ZERO_PAGE": 0xC4, "ABSOLUTE": 0xCC},
        "DEC": {"ZERO_PAGE": 0xC6, "ZERO_PAGE_X": 0xD6, "ABSOLUTE": 0xCE, "ABSOLUTE_X": 0xDE},
        "DEX": {"IMPLIED": 0xCA},
        "DEY": {"IMPLIED": 0x88},
        "EOR": {
            "IMMEDIATE": 0x49, "ZERO_PAGE": 0x45, "ZERO_PAGE_X": 0x55, "ABSOLUTE": 0x4D, "ABSOLUTE_X": 0x5D,
            "ABSOLUTE_Y": 0x59, "X_INDIRECT": 0x41, "INDIRECT_Y": 0x51
        },
        "INC": {"ZERO_PAGE": 0xE6, "ZERO_PAGE_X": 0xF6, "ABSOLUTE": 0xEE, "ABSOLUTE_X": 0xFE},
        "INX": {"IMPLIED": 0xE8},
        "INY": {"IMPLIED": 0xC8},
        "JMP": {"ABSOLUTE": 0x4C, "INDIRECT": 0x6C},
        "JSR": {"ABSOLUTE": 0x20},
        "LDA": {
            "IMMEDIATE": 0xA9, "ZERO_PAGE": 0xA5, "ZERO_PAGE_X": 0xB5, "ABSOLUTE": 0xAD, "ABSOLUTE_X": 0xBD,
            "ABSOLUTE_Y": 0xB9, "X_INDIRECT": 0xA1, "INDIRECT_Y": 0xB1
        },
        "LDX": {"IMMEDIATE": 0xA2, "ZERO_PAGE": 0xA6, "ZERO_PAGE_Y": 0xB6, "ABSOLUTE": 0xAE, "ABSOLUTE_Y": 0xBE},
        "LDY": {"IMMEDIATE": 0xA0, "ZERO_PAGE": 0xA4, "ZERO_PAGE_X": 0xB4, "ABSOLUTE": 0xAC, "ABSOLUTE_X": 0xBC},
        "LSR": {"ACCUMULATOR": 0x4A, "ZERO_PAGE": 0x46, "ZERO_PAGE_X": 0x56, "ABSOLUTE": 0x4E, "ABSOLUTE_X": 0x5E},
        "NOP": {"IMPLIED": 0xEA},
        "ORA": {
            "IMMEDIATE": 0x9, "ZERO_PAGE": 0x5, "ZERO_PAGE_X": 0x15, "ABSOLUTE": 0x0D, "ABSOLUTE_X": 0x1D,
            "ABSOLUTE_Y": 0x19, "X_INDIRECT": 0x1, "INDIRECT_Y": 0x11
        },
        "PHA": {"IMPLIED": 0x48},
        "PHP": {"IMPLIED": 0x8},
        "PLA": {"IMPLIED": 0x68},
        "PLP": {"IMPLIED": 0x28},
        "ROL": {"ACCUMULATOR": 0x2A, "ZERO_PAGE": 0x26, "ZERO_PAGE_X": 0x36, "ABSOLUTE": 0x2E, "ABSOLUTE_X": 0x3E},
        "ROR": {"ACCUMULATOR": 0x6A, "ZERO_PAGE": 0x66, "ZERO_PAGE_X": 0x76, "ABSOLUTE": 0x6E, "ABSOLUTE_X": 0x7E},
        "RTI": {"IMPLIED": 0x40},
        "RTS": {"IMPLIED": 0x60},
        "SBC": {
            "IMMEDIATE": 0xE9, "ZERO_PAGE": 0xE5, "ZERO_PAGE_X": 0xF5, "ABSOLUTE": 0xED, "ABSOLUTE_X": 0xFD,
            "ABSOLUTE_Y": 0xF9, "X_INDIRECT": 0xE1, "INDIRECT_Y": 0xF1
        },
        "SEC": {"IMPLIED": 0x38},
        "SED": {"IMPLIED": 0xF8},
        "SEI": {"IMPLIED": 0x78},
        "STA": {
            "ZERO_PAGE": 0x85, "ZERO_PAGE_X": 0x95, "ABSOLUTE": 0x8D, "ABSOLUTE_X": 0x9D, "ABSOLUTE_Y": 0x99,
            "X_INDIRECT": 0x81, "INDIRECT_Y": 0x91
        },
        "STX": {"ZERO_PAGE": 0x86, "ZERO_PAGE_Y": 0x96, "ABSOLUTE": 0x8E},
        "STY": {"ZERO_PAGE": 0x84, "ZERO_PAGE_X": 0x94, "ABSOLUTE": 0x8C},
        "TAX": {"IMPLIED": 0xAA},
        "TAY": {"IMPLIED": 0xA8},
        "TSX": {"IMPLIED": 0xBA},
        "TXA": {"IMPLIED": 0x8A},
        "TYA": {"IMPLIED": 0x98},
    }

    def __init__(self, token_list: list[Token]):
        self.sym_lib = Symbol_Library()
        self.token_list: list[Token] = token_list
        self.byte_obj_list: list[bytes] = []

        self.parse_symbols()
        self.parse_labels()
        self.parse_opcodes_and_raws()

    def parse_symbols(self) -> None:
        sym_dec_list = [token.content for token in self.token_list if token.type == "SYMBOL"]
        self.sym_lib.add_symbols(sym_dec_list)
        self.token_list = [token for token in self.token_list if token.type != "SYMBOL"]

    def parse_addr_mode(self, opcode: str) -> tuple[str, str]:
        split_code = opcode.split(" ")
        if len(split_code) == 1:
            return "IMPLIED", ""
        if split_code[0] in ("BCC", "BCS", "BEQ", "BMI", "BNE", "BPL", "BVC", "BVS"):
            return "RELATIVE", split_code[1]
        arg = split_code[1].strip().upper()
        if arg == "A":
            return "ACCUMULATOR", "A"
        if arg[0] == "#":
            return "IMMEDIATE", arg[1:]
        if re.fullmatch(r"\(.+,X\)", arg):
            return "X_INDIRECT", arg[1:-3]
        if re.fullmatch(r"\(.+\),Y", arg):
            return "INDIRECT_Y", arg[1:-3]
        if re.fullmatch(r"\(.+\)", arg):
            return "INDIRECT", arg[1:-1]
        if arg[-2:] == ",X":
            val = self.sym_lib.get_value(arg[:-2])
            if 0 <= val <= 0xFF:
                return "ZERO_PAGE_X", arg[:-2]
            return "ABSOLUTE_X", arg[:-2]
        if arg[-2:] == ",Y":
            val = self.sym_lib.get_value(arg[:-2])
            if 0 <= val <= 0xFF:
                return "ZERO_PAGE_Y", arg[:-2]
            return "ABSOLUTE_Y", arg[:-2]
        val = self.sym_lib.get_value(arg)
        if 0 <= val <= 0xFF:
            return "ZERO_PAGE", arg
        return "ABSOLUTE", arg

    def parse_labels(self) -> None:
        cursor_pos = 0
        for token in self.token_list:
            match token.type:
                case "LABEL":
                    self.sym_lib.add_label(token.content, cursor_pos)
                case "RAW_DATA":
                    args = token.content.split(" ")
                    if args[0] in [".B", ".BYTE", ".BYTES"]:
                        cursor_pos += len(args) - 1
                    elif args[0] in [".W", ".WORD", ".WORDS"]:
                        cursor_pos += 2 * (len(args) - 1)
                    elif args[0] == ".PAD":
                        cursor_pos = read(args[1])
                case "OPCODE":
                    addr_mode = self.parse_addr_mode(token.content)[0]
                    cursor_pos += self._ADDR_MODE_LENGTHS[addr_mode]
        self.token_list = [token for token in self.token_list if token.type != "LABEL"]

    def parse_opcodes_and_raws(self) -> None:
        cursor_pos = 0
        for token in self.token_list:
            if token.type == "RAW_DATA":
                raw_args = token.content.split(" ")
                if raw_args[0] in [".B", ".BYTE", ".BYTES"]:
                    for byte_reference in raw_args[1:]:
                        cursor_pos += 1
                        byte = self.sym_lib.get_bytes(byte_reference)
                        if len(byte) > 1:
                            raise ValueError(f"Reference {byte_reference} value {int(byte)} too large for BYTE call!")
                        self.byte_obj_list.append(byte)
                elif raw_args[0] in [".W", ".WORD", ".WORDS"]:
                    for word_reference in raw_args[1:]:
                        cursor_pos += 2
                        word = self.sym_lib.get_bytes(word_reference)
                        if len(word) == 1:
                            word = word + b"\x00"
                        self.byte_obj_list.append(word)
                elif raw_args[0] == ".PAD":
                    target_pos = self.sym_lib.get_value(raw_args[1])
                    these_bytes = bytes(target_pos - cursor_pos)
                    self.byte_obj_list.append(these_bytes)
                    cursor_pos = target_pos
            elif token.type == "OPCODE":
                instruction = token.content.split(" ")[0]
                addr_mode, argument = self.parse_addr_mode(token.content)
                instruction_byte = self._INSTRUCTIONS[instruction][addr_mode].to_bytes(1)
                arg_bytes = b""
                if addr_mode == "RELATIVE":
                    try:
                        arg_val = read(token.content.split(" ")[1])
                        arg_bytes = arg_val.to_bytes(length=1, signed=True)
                    except ValueError:
                        arg_bytes = self.sym_lib.get_relative(cursor_pos + 2, token.content.split(" ")[1])
                elif addr_mode not in ["IMPLIED", "ACCUMULATOR"]:
                    arg_bytes = self.sym_lib.get_bytes(argument)
                opc_bytes = instruction_byte + arg_bytes
                while len(opc_bytes) < self._ADDR_MODE_LENGTHS[addr_mode]:
                    opc_bytes = opc_bytes + b"\x00"
                self.byte_obj_list.append(opc_bytes)
                cursor_pos += len(opc_bytes)
            else:
                raise NotImplementedError(
                    "This state should be unreachable! Contact Eliana because something's broken.")


class Symbol_Library:
    def __init__(self):
        self.symbols: dict[str, Symbol] = {}
        self.labels: dict[str, Label] = {}
        self.anon_labels: list[Label] = []

    def get_relative(self, current_pos: int, label_name: str) -> bytes:
        if label_name[0] == ":":
            anon_offset = 0
            for char in label_name[1:]:
                if char == "-":
                    anon_offset -= 1
                elif char == "+":
                    anon_offset += 1
                else:
                    raise ValueError(f"Disallowed character {char} in anonymous label reference!")
            if anon_offset > 0:
                anon_offset -= 1
            current_anon_region = 0
            while current_pos > self.anon_labels[current_anon_region].short_addr:
                current_anon_region += 1
                if current_anon_region >= len(self.anon_labels):
                    break
            target_label = self.anon_labels[current_anon_region + anon_offset]
        else:
            target_label = self.labels[label_name]
        return (target_label.short_addr - current_pos).to_bytes(length=1, signed=True)

    def get_value(self, name: str) -> int:
        try:
            return read(name)
        except ValueError:
            pass
        if name in self.symbols:
            return self.symbols[name].value
        if name in self.labels:
            return self.labels[name].absolute_addr
        raise NameError(f"Unknown name {name}")

    def add_symbols(self, decl_list: list[str]) -> None:
        for i in decl_list:
            self._add_symbol(i)

    def _add_symbol(self, declaration: str) -> None:
        this_symbol = Symbol(declaration)
        self.symbols[this_symbol.name] = this_symbol

    def add_label(self, declaration: str, pos: int) -> None:
        this_label = Label(declaration, pos)
        if this_label.name == "":
            self.anon_labels.append(this_label)
        else:
            self.labels[this_label.name] = this_label

    def get_bytes(self, string_val: str) -> bytes:
        string_val = string_val.strip().upper()
        if string_val[0] == "<":
            if string_val[1:] in self.symbols:
                return self.symbols[string_val[1:]].get_low_byte()
            elif string_val[1:] in self.labels:
                return self.labels[string_val[1:]].get_low_byte()
            else:
                raise NameError(f"Unknown reference {string_val[1:]}")
        elif string_val[0] == ">":
            if string_val[1:] in self.symbols:
                return self.symbols[string_val[1:]].get_high_byte()
            elif string_val[1:] in self.labels:
                return self.labels[string_val[1:]].get_high_byte()
            else:
                raise NameError(f"Unknown reference {string_val[1:]}")
        elif string_val in self.symbols:
            this_sym = self.symbols[string_val]
            if this_sym.byte_sized():
                return this_sym.get_byte()
            return this_sym.get_word()
        elif string_val in self.labels:
            this_label = self.labels[string_val]
            return this_label.get_word()
        else:
            val = read(string_val)
            if val >= 0xFF:
                return val.to_bytes(2, "little")
            return val.to_bytes()


class Symbol:
    def __init__(self, declare_str: str) -> None:
        self.name, val_tmp = declare_str.split("=")
        self.value = read(val_tmp)
        self.name = self.name.strip()

    def get_low_byte(self) -> bytes:
        return (self.value & 0xff).to_bytes(1)

    def get_high_byte(self) -> bytes:
        return (self.value >> 8).to_bytes(1)

    def get_byte(self) -> bytes:
        return self.value.to_bytes(1)

    def get_word(self) -> bytes:
        return self.value.to_bytes(2, "little")

    def byte_sized(self) -> bool:
        return self.value <= 0xff


class Label:
    def __init__(self, declare_str: str, pos: int) -> None:
        self.name = declare_str.split(":")[0]
        self.short_addr = pos
        self.absolute_addr = 0x8000 + (self.short_addr & 0x7FFF)

    def get_low_byte(self) -> bytes:
        return (self.absolute_addr & 0xFF).to_bytes(1)

    def get_high_byte(self) -> bytes:
        return (self.absolute_addr >> 8).to_bytes(1)

    def get_word(self) -> bytes:
        return self.absolute_addr.to_bytes(2, "little")
