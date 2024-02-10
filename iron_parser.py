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

	def parse_labels(self):
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

	def add_label(self, declaration: str, pos: int) -> None:
		this_label = Label(declaration, pos)
		if this_label.name == "":
			self.anon_labels.append(this_label)
		self.labels[this_label.name] = this_label


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
