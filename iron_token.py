from number_reader import read


class Tokenizer:
	def __init__(self):
		self.tokens: list[Token] = []
		self.symbols: dict[str, Symbol] = {}
		self.labels: dict[str, Label] = {}
		self.anon_labels: list[Label] = []


class Token:
	pass

class Symbol:
	def __init__(self, declaration: str):
		self.value = read(declaration)

	def is_byte_sized(self) -> bool:
		return self.value <= 0xFF

	def get_byte(self) -> bytes:
		return self.value.to_bytes(1)

	def get_word(self) -> bytes:
		return self.value.to_bytes(2, "little")

	def get_high_byte(self) -> bytes:
		return (self.value >> 8).to_bytes(1)

	def get_low_byte(self) -> bytes:
		return (self.value & 0xFF).to_bytes(1)

class Label:
	pass