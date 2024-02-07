import re


class Assembler:
	def __init__(self, file_path: str):
		self.main_asm_file = file_path
		self.text_lines: list[str] = []

	def assemble(self):

		self.preprocess_lines()
		print("Called assemble!")
		print(self.text_lines)

	def preprocess_lines(self) -> None:
		with open(self.main_asm_file) as infile:
			file_content = infile.read()
		file_content = file_content.replace(":", ":\n")
		out_lines = []
		for line in file_content.split("\n"):
			re_match = re.fullmatch(r"(.*?);.*|(.+)", line)
			if re_match is None:
				continue
			processed_line = re_match.group(1) or re_match.group(2)  # One of these is always None
			if processed_line not in ("", None):
				out_lines.append(processed_line)
		self.text_lines = out_lines
