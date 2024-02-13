from number_reader import read


class Tokenizer:
	def __init__(self, text_lines: list[str]):
		self.tokens: list[Token] = []
		for line in text_lines:
			self.tokens.append(Token(line))

class Token:
	def __init__(self, line: str):
		self.content = line
		if line[0] == "!":
			self.type = "CART_CONFIG"
		elif line[0] == ".":
			self.type = "RAW_DATA"
		elif line[-1] == ":":
			self.type = "LABEL"
		elif "=" in line:
			self.type = "SYMBOL"
		else:
			self.type = "OPCODE"
