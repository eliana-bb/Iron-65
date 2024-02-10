from number_reader import read


class Tokenizer:
	def __init__(self):
		self.prog_tokens: list[Token] = []
		self.symbols: dict[str, Symbol] = {}
		self.labels: dict[str, Label] = {}
		self.anon_labels: list[Label] = []
		self.cart_config: list[Token] = []
		self.cursor = 0

	def tokenize(self, text_lines: list[str]):
		for line in text_lines:
			line = line.strip().upper()
			this_token = Token(line)
			if this_token.token_type == "CART_CONFIG":
				self.cart_config.append(this_token)
			else:
				self.prog_tokens.append(this_token)


class Token:
	def __init__(self, line: str):
		if line.startswith("!"):
			self.token_type = "CART_CONFIG"
		elif line.startswith("."):
			self.token_type = "DATA_RAW"
		elif line.endswith(":"):
			self.token_type = "LABEL_DEF"
		elif "=" in line:
			self.token_type = "SYMBOL_DEF"
		else:
			self.token_type = "OPCODE"
		self.content = line


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
