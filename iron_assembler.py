import re
from typing import Union
import iron_token
import iron_parser
from number_reader import read


class Assembler:
    def __init__(self, file_path: str):
        self.main_asm_file = file_path

    def assemble(self):
        virtual_cart = VirtualCartridge()
        text_lines = self.preprocess_lines()  # Do things like removing comments, special-case line splitting, etc.
        tokenizer = iron_token.Tokenizer(text_lines)
        all_tokens = tokenizer.tokens
        cart_config_strings = [token.content for token in all_tokens if token.type == "CART_CONFIG"]
        virtual_cart.config_cart(cart_config_strings)
        all_tokens = [token for token in all_tokens if token.type != "CART_CONFIG"]
        parser = iron_parser.Parser(all_tokens)
        virtual_cart.initialize_prg()

    def preprocess_lines(self) -> list[str]:
        """
        Returns a list of strings, with whitespaces collapsed, comments removed, all uppercased, with no empty lines.
        """
        with open(self.main_asm_file) as infile:
            file_content = infile.read()
        file_content = re.sub(pattern=r":([^+-])", repl=r":\g<1>\n", string=file_content)
        out_lines = []
        for line in file_content.split("\n"):
            processed_line = line.upper().split(";")[0].strip()  # Removes comments, uppercases, strips whitespace
            if processed_line == "":
                continue
            processed_line = re.sub(r"[ \t]+", " ", processed_line)
            out_lines.append(processed_line)
        return out_lines


class VirtualCartridge:
    _NAMETABLE_MIRROR_MODES = {"VERTICAL": 0, "HORIZONTAL": 1, "MAPPER": 0b1000}
    _REGIONS = {"NTSC": 0, "PAL": 1, "MULTI": 2, "DENDY": 3}
    _VS_SYSTEM_PPUS = {
        "RP2C03B": 0x00, "RP2C03G": 0x10, "RP2C04-0001": 0x20, "RP2C04-0002": 0x30, "RP2C04-0003": 0x40,
        "RP2C04-0004": 0x50, "RC2C03B": 0x60, "RC2C03C": 0x70, "RC2C05-01": 0x80, "RC2C05-02": 0x90, "RC2C05-03": 0xA0,
        "RC2C05-04": 0xB0, "RC2C05-05": 0xC0
    }
    _VS_SYSTEM_HTYPES = {
        "NORMAL": 0, "RBI_BASEBALL": 1, "TKO_BOXING": 2, "SUPER_XEVIOUS": 3, "VS_ICE_CLIMBER": 4, "DUAL": 5,
        "DUAL_BUNGELING": 6
    }
    _CONSOLE_TYPES = {
        "NES": 0, "FAMICOM": 0, "DENDY": 0, "VS_SYSTEM": 1, "PLAYCHOICE_10": 2, "FAMICLONE_DECIMAL": 3, "NES_EPSM": 4,
        "FAMICOM_EPSM": 4, "VT01": 5, "VT02": 6, "VT03": 7, "VT09": 8, "VT32": 9, "VT369": 10, "UM6578": 11,
        "FAMICOM_NETWORK": 12
    }

    def __init__(self) -> None:
        self.prg_size: list[int] = [2]
        self.chr_size: list[int] = [1]
        self.mirror_mode: int = 1
        self.battery: bool = False
        self.trainer: str = ""
        self.mapper: list[int] = [0, 0]
        self.console_type_7: int = 0
        self.prg_ram_shifts: int = 0
        self.prg_nvram_shifts: int = 0
        self.chr_ram_shifts: int = 0
        self.chr_nvram_shifts: int = 0
        self.region: int = 0
        self.byte_13: int = 0
        self.misc_roms: list[str] = []
        self.default_device: int = 1

        self.out_file = ""
        self.chr_file = ""

        self.prg = bytearray(0)

    def config_cart(self, conf_list: list[str]) -> None:
        for i in conf_list:
            self._config_cartridge(i)

    def _config_cartridge(self, config_str: str) -> None:
        config_args = config_str.upper().strip().split(" ")
        match config_args[0]:
            case "!OUT_FILE":
                self.out_file = config_args[1]
            case "!CHR_FILE":
                self.chr_file = config_args[1]
            case "!PRG_SIZE":
                if len(config_args) == 2:
                    self.prg_size = [read(config_args[1])]
                else:
                    self.prg_size = [read(config_args[1]), read(config_args[2])]
            case "!CHR_SIZE":
                if len(config_args) == 2:
                    self.chr_size = [read(config_args[1])]
                else:
                    self.chr_size = [read(config_args[1]), read(config_args[2])]
            case "!MIRROR_MODE":
                self.mirror_mode = self._NAMETABLE_MIRROR_MODES[config_args[1]]
            case "!BATTERY":
                self.battery = (config_args[1] == "TRUE")
            case "!TRAINER":
                self.trainer = "" if config_args[1] == "FALSE" else config_args[1]
            case "!CONSOLE_TYPE":
                console_type = self._CONSOLE_TYPES[config_args[1]]
                if console_type == 1:
                    self.byte_13 = (
                            self._VS_SYSTEM_PPUS[config_args[2]] |
                            self._VS_SYSTEM_HTYPES[config_args[3]]
                    )
                if console_type >= 3:
                    self.console_type_7 = 3
                    self.byte_13 = console_type
                else:
                    self.console_type_7 = console_type
                    self.byte_13 = 0
            case "!MAPPER":
                self.mapper[0] = read(config_args[1])
                if len(config_args) == 3:
                    self.mapper[1] = read(config_args[2])
            case "!PRG_RAM_SIZE":
                self.prg_ram_shifts = read(config_args[1])
            case "!PRG_NVRAM_SIZE":
                self.prg_nvram_shifts = read(config_args[1])
            case "!CHR_RAM_SIZE":
                self.chr_ram_shifts = read(config_args[1])
            case "!CHR_NVRAM_SIZE":
                self.chr_nvram_shifts = read(config_args[1])
            case "!REGION":
                self.region = self._REGIONS[config_args[1]]
            case "!MISC_ROMS":
                if config_args[1] == "FALSE":
                    self.misc_roms = []
                else:
                    self.misc_roms = config_args[1:]
            case "!DEFAULT_DEVICE":
                self.default_device = read(config_args[1])

    def initialize_prg(self) -> None:
        if len(self.prg_size) == 1:
            self.prg = bytearray(self.prg_size[0] << 14)
        else:
            pass