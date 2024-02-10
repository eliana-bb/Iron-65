import re
from typing import Literal


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
	def __init__(self):
		self.prg_size: list[int] = [2]
		self.prg_size_mode: str = "LIN"
		self.chr_size: list[int] = [2]
		self.chr_size_mode: str = "LIN"
		self.nametable_mode: str = "HORIZONTAL"
		self.mapper: int = 0
		self.submapper: int = 0
		self.console_type: str = "NES"
		self.prg_ram_shifts: int = 0
		self.prg_nvram_shifts: int = 0
		self.chr_ram_shifts: int = 0
		self.chr_nvram_shifts: int = 0
		self.region: int = 0
		self.byte_13: int = 0
		self.misc_roms: int = 0
		self.default_device: int = 1
