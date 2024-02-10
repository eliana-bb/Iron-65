from number_reader import read
from iron_token import Token


class Parser:
	def __init__(self, token_list: list[Token]):
		self.sym_lib = Symbol_Library()
		self.token_list: list[Token] = token_list
		self.byte_obj_list: list[bytes] = []

		self.parse_symbols()

	def parse_symbols(self):
		sym_dec_list = [token.content for token in self.token_list if token.type == "SYMBOL"]
		self.sym_lib.add_symbols(sym_dec_list)
		self.sym_lib = [token for token in self.token_list if token.type != "SYMBOL"]

	def parse_labels(self):
		cursor_pos = 0



class Symbol_Library:
	def __init__(self):
		self.symbols: dict[str, Symbol] = {}
		self.labels: dict[str, Label] = {}
		self.anon_labels: list[Label] = []

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
