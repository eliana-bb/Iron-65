from number_reader import read
from iron_token import Token
import re


class Parser:
	_ADDR_MODE_LENGTHS = {
		"IMPLIED": 1, "ACCUMULATOR": 1, "ZERO_PAGE": 2, "ZERO_PAGE_X": 2, "ZERO_PAGE_Y": 2, "RELATIVE": 2,
		"IMMEDIATE": 2, "ABSOLUTE": 3, "ABSOLUTE_X": 3, "ABSOLUTE_Y": 3, "INDIRECT": 3, "X_INDIRECT": 3, "INDIRECT_Y": 3
	}

	def __init__(self, token_list: list[Token]):
		self.sym_lib = Symbol_Library()
		self.token_list: list[Token] = token_list
		self.byte_obj_list: list[bytes] = []

		self.parse_symbols()

	def parse_symbols(self):
		sym_dec_list = [token.content for token in self.token_list if token.type == "SYMBOL"]
		self.sym_lib.add_symbols(sym_dec_list)
		self.sym_lib = [token for token in self.token_list if token.type != "SYMBOL"]

	def parse_addr_mode(self, opcode: str) -> str:
		split_code = opcode.split(" ")
		if len(split_code) == 1:
			return "IMPLIED"
		if split_code[0] in ("BCC", "BCS", "BEQ", "BMI", "BNE", "BPL", "BVC", "BVS"):
			return "RELATIVE"
		arg = split_code[1].strip().upper()
		if arg == "A":
			return "ACCUMULATOR"
		if arg[0] == "#":
			return "IMMEDIATE"
		if re.fullmatch(r"\(.+,X\)", arg):
			return "X_INDIRECT"
		if re.fullmatch(r"\(.+\),Y", arg):
			return "INDIRECT_Y"
		if re.fullmatch(r"\(.+\)", arg):
			return "INDIRECT"
		if arg[-2:] == ",X":
			val = self.sym_lib.get_value(arg[:-2])
			if 0 <= val <= 0xFF:
				return "ZERO_PAGE_X"
			return "ABSOLUTE_X"
		if arg[-2:] == ",Y":
			val = self.sym_lib.get_value(arg[:-2])
			if 0 <= val <= 0xFF:
				return "ZERO_PAGE_Y"
			return "ABSOLUTE_Y"
		val = self.sym_lib.get_value(arg)
		if 0 <= val <= 0xFF:
			return "ZERO_PAGE"
		return "ABSOLUTE"

	def parse_labels(self):
		cursor_pos = 0


class Symbol_Library:
	def __init__(self):
		self.symbols: dict[str, Symbol] = {}
		self.labels: dict[str, Label] = {}
		self.anon_labels: list[Label] = []

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


class Symbol:
	def __init__(self, declare_str: str) -> None:
		self.name, val_tmp = declare_str.split("=")
		self.value = read(val_tmp)
		self.name = self.name.strip()


class Label:
	def __init__(self, declare_str: str, pos: int) -> None:
		self.name = declare_str[:-1]
		self.short_addr = pos
		self.absolute_addr = 0x8000 + (self.short_addr & 0x7FFF)
