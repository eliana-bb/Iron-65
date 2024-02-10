import re
from typing import Literal
from number_reader import read


class Assembler:
	def __init__(self, file_path: str):
		self.main_asm_file = file_path

	def assemble(self):
		text_lines = self.preprocess_lines()

	def preprocess_lines(self) -> list[str]:
		with open(self.main_asm_file) as infile:
			file_content = infile.read()
		file_content = file_content.replace(":", ":\n")
		out_lines = []
		for line in file_content.split("\n"):
			re_match = re.fullmatch(r"(.*?);.*|(.+)", line)
			if re_match is None:
				continue
			processed_line = re_match.group(1) or re_match.group(2) or ""  # One of these is always None
			processed_line = processed_line.strip()
			if processed_line != "":
				out_lines.append(processed_line)
		return out_lines


class VirtualCartridge:
	_NAMETABLE_MIRROR_MODES = {"VERTICAL": 0, "HORIZONTAL": 1, "MAPPER": 0b1000}
	_REGIONS = {"NTSC": 0, "PAL": 1, "MULTI": 2, "DENDY": 3}
	_VS_SYSTEM_PPUS = {
		"RP2C03B": 0, "RP2C03G": 1, "RP2C04-0001": 2, "RP2C04-0002": 3, "RP2C04-0003": 4, "RP2C04-0004": 5,
		"RC2C03B": 6, "RC2C03C": 7, "RC2C05-01": 8, "RC2C05-02": 9, "RC2C05-03": 10, "RC2C05-04": 11, "RC2C05-05": 12
	}
	_VS_SYSTEM_HTYPES = {
		"NORMAL": 0, "RBI_BASEBALL": 1, "TKO_BOXING": 2, "SUPER_XEVIOUS": 3, "VS_ICE_CLIMBER": 4, "DUAL": 5,
		"DUAL_BUNGELING": 6
	}
	_CONSOLE_TYPES = {
		"NES": 0, "FAMICOM": 0, "DENDY": 0, "VSSYSTEM": 1, "PLAYCHOICE_10": 2, "FAMICLONE_DECIMAL": 3, "NES_EPSM": 4,
		"FAMICOM_EPSM": 4, "VT01": 5, "VT02": 6, "VT03": 7, "VT09": 8, "VT32": 9, "VT369": 10, "UM6578": 11,
		"FAMICOM_NETWORK": 12
	}

	def __init__(self):
		self.prg_size: list[int] = [2]
		self.prg_size_mode: str = "LIN"
		self.chr_size: list[int] = [2]
		self.chr_size_mode: str = "LIN"
		self.mirror_mode: str = "HORIZONTAL"
		self.mapper: int = 0
		self.submapper: int = 0
		self.console_type: str = "NES"
		self.prg_ram_shifts: int = 0
		self.prg_nvram_shifts: int = 0
		self.chr_ram_shifts: int = 0
		self.chr_nvram_shifts: int = 0
		self.region: str = "NTSC"
		self.byte_13: int = 0
		self.misc_roms: int = 0
		self.default_device: int = 1
