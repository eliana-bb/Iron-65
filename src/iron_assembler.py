import re
import iron_token
import iron_parser
from number_reader import read
import os
from typing import Union


class Assembler:
	def __init__(self, file_path: str):
		self.main_asm_file = file_path

	def assemble(self):
		virtual_cart = VirtualCartridge(self.main_asm_file)
		text_lines = self.preprocess_lines()  # Do things like removing comments, special-case line splitting, etc.
		tokenizer = iron_token.Tokenizer(text_lines)
		all_tokens = tokenizer.tokens
		cart_config_strings = [token.content for token in all_tokens if token.type == "CART_CONFIG"]
		virtual_cart.config_cart(cart_config_strings)
		all_tokens = [token for token in all_tokens if token.type != "CART_CONFIG"]
		parser = iron_parser.Parser(all_tokens)
		virtual_cart.initialize_prg()
		virtual_cart.write_all_bytes(parser.byte_obj_list)
		virtual_cart.save()

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

	def __init__(self, prg_file: str) -> None:
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

		self.prg_file = prg_file
		self.out_file = ""
		self.chr_file = ""

		self.prg = bytearray(0)
		self.prg_counter = 0

	def config_cart(self, conf_list: list[str]) -> None:
		for i in conf_list:
			self._config_cartridge(i)

	def _config_cartridge(self, config_str: str) -> None:
		config_args = config_str.upper().strip().split(" ")
		match config_args[0]:
			case "!OUT_FILE":
				self.arg_count_validate(config_args, 1)
				self.out_file = config_args[1]
			case "!CHR_FILE":
				self.arg_count_validate(config_args, 1)
				self.chr_file = config_args[1]
			case "!PRG_SIZE":
				self.arg_count_validate(config_args, 1, 2)
				if len(config_args) == 2:
					self.range_validate(config_args, 1, 0xEFF)
					self.prg_size = [read(config_args[1])]
				else:
					self.set_validate(config_args, 1, [1, 3, 5, 7])
					self.range_validate(config_args, 2, 63)
					self.prg_size = [read(config_args[1]), read(config_args[2])]
			case "!CHR_SIZE":
				self.arg_count_validate(config_args, 1, 2)
				if len(config_args) == 2:
					self.range_validate(config_args, 1, 0xEFF)
					self.chr_size = [read(config_args[1])]
				else:
					self.set_validate(config_args, 1, [1, 3, 5, 7])
					self.range_validate(config_args, 2, 63)
					self.chr_size = [read(config_args[1]), read(config_args[2])]
			case "!MIRROR_MODE":
				self.arg_count_validate(config_args, 1)
				self.set_validate(config_args, 1, self._NAMETABLE_MIRROR_MODES)
				self.mirror_mode = self._NAMETABLE_MIRROR_MODES[config_args[1]]
			case "!BATTERY":
				self.arg_count_validate(config_args, 1)
				self.set_validate(config_args, 1, ["TRUE", "FALSE"])
				self.battery = config_args[1] == "TRUE"
			case "!TRAINER":
				self.arg_count_validate(config_args, 1)
				self.trainer = "" if config_args[1] == "FALSE" else config_args[1]
			case "!CONSOLE_TYPE":
				self.arg_count_validate(config_args, 1, 3)
				self.set_validate(config_args, 1, self._CONSOLE_TYPES)
				console_type = self._CONSOLE_TYPES[config_args[1]]
				if console_type == 1:
					self.arg_count_validate(config_args, 3)
					self.set_validate(config_args, 2, self._VS_SYSTEM_PPUS)
					self.set_validate(config_args, 3, self._VS_SYSTEM_HTYPES)
					self.byte_13 = (
							self._VS_SYSTEM_PPUS[config_args[2]] | self._VS_SYSTEM_HTYPES[config_args[3]]
					)
				else:
					self.arg_count_validate(config_args, 1)
				if console_type >= 3:
					self.console_type_7 = 3
					self.byte_13 = console_type
				else:
					self.console_type_7 = console_type
					self.byte_13 = 0
			case "!MAPPER":
				self.arg_count_validate(config_args, 1, 2)
				self.range_validate(config_args, 1, 0xFFF)
				self.mapper[0] = read(config_args[1])
				if len(config_args) == 3:
					self.range_validate(config_args, 2, 15)
					self.mapper[1] = read(config_args[2])
			case "!PRG_RAM_SIZE":
				self.arg_count_validate(config_args, 1)
				self.range_validate(config_args, 1, 15)
				self.prg_ram_shifts = read(config_args[1])
			case "!PRG_NVRAM_SIZE":
				self.arg_count_validate(config_args, 1)
				self.range_validate(config_args, 1, 15)
				self.prg_nvram_shifts = read(config_args[1])
			case "!CHR_RAM_SIZE":
				self.arg_count_validate(config_args, 1)
				self.range_validate(config_args, 1, 15)
				self.chr_ram_shifts = read(config_args[1])
			case "!CHR_NVRAM_SIZE":
				self.arg_count_validate(config_args, 1)
				self.range_validate(config_args, 1, 15)
				self.chr_nvram_shifts = read(config_args[1])
			case "!REGION":
				self.arg_count_validate(config_args, 1)
				self.set_validate(config_args, 1, self._REGIONS)
				self.region = self._REGIONS[config_args[1]]
			case "!MISC_ROMS":
				self.arg_count_validate(config_args, 1, 4)
				if config_args[1] == "FALSE":
					self.misc_roms = []
				else:
					self.misc_roms = config_args[1:]
			case "!DEFAULT_DEVICE":
				self.arg_count_validate(config_args, 1)
				self.range_validate(config_args, 1, 0x3A)
				self.default_device = read(config_args[1])

	def initialize_prg(self) -> None:
		if len(self.prg_size) == 1:
			prg_size = self.prg_size[0] << 14
		else:
			prg_size = self.prg_size[0] << self.prg_size[1]
		self.prg = bytearray(prg_size)

	def write_bytes_progressive(self, raw_bytes: bytes) -> None:
		bytes_len = len(raw_bytes)
		self.prg[self.prg_counter:self.prg_counter + bytes_len] = raw_bytes
		self.prg_counter += bytes_len

	def write_all_bytes(self, bytes_list: list[bytes]) -> None:
		for obj in bytes_list:
			self.write_bytes_progressive(obj)

	def header(self) -> bytes:
		header_bytes = bytearray(b"NES\x1A\x00\x00\x00\x08" + b"\x00" * 8)
		if len(self.prg_size) == 1:
			header_bytes[4] = self.prg_size[0] & 0xFF
			header_bytes[9] |= self.prg_size[0] >> 8
		else:
			header_bytes[4] = (self.prg_size[0] - 1) // 2
			header_bytes[4] |= self.prg_size[1] << 2
			header_bytes[9] |= 0x0F
		if len(self.chr_size) == 1:
			header_bytes[5] = self.chr_size[0] & 0xFF
			header_bytes[9] |= (self.chr_size[0] & 0x0F00) >> 4
		else:
			header_bytes[5] = (self.chr_size[0] - 1) // 2
			header_bytes[5] |= self.chr_size[1] << 2
			header_bytes[9] |= 0xF0
		header_bytes[6] |= self.mirror_mode
		header_bytes[6] |= self.battery << 1
		header_bytes[6] |= (self.trainer != "") << 2
		header_bytes[6] |= (self.mapper[0] & 0xF) << 4
		header_bytes[7] |= self.console_type_7
		header_bytes[7] |= self.mapper[0] & 0xF0
		header_bytes[8] = self.mapper[1] << 4
		header_bytes[8] |= (self.mapper[0] & 0xF00) >> 8
		header_bytes[10] = self.prg_ram_shifts
		header_bytes[10] |= self.prg_nvram_shifts << 4
		header_bytes[11] = self.chr_ram_shifts
		header_bytes[11] |= self.chr_nvram_shifts
		header_bytes[12] = self.region
		header_bytes[13] = self.byte_13
		header_bytes[14] = len(self.misc_roms)
		header_bytes[15] = self.default_device
		return bytes(header_bytes)

	def save(self) -> None:
		if self.out_file == "":
			self.out_file = "".join(self.prg_file.removeprefix("input/").split(".")[:-1]) + ".nes"
		self.out_file = self.out_file.lower()
		if self.chr_file == "":
			for file in os.listdir("input"):
				if file.endswith(".chr"):
					self.chr_file = file
					break
		if self.chr_file == "":
			raise FileNotFoundError("CHR file unspecified!")
		with open("output/" + self.out_file, mode="wb") as out_file:
			out_file.write(self.header())
			if self.trainer != "":
				with open("input/" + self.trainer, mode="rb") as trainer_file:
					out_file.write(trainer_file.read())
			out_file.write(self.prg)
			with open("input/" + self.chr_file, mode="rb") as chr_file:
				out_file.write(chr_file.read())
			for misc_rom in self.misc_roms:
				with open("input/" + misc_rom, mode="rb") as misc_file:
					out_file.write(misc_file.read())

	@staticmethod
	def arg_count_validate(args: list[str], min_val: int, max_val: Union[int, None] = None) -> None:
		arg_count = len(args) - 1
		if max_val is None:
			if arg_count < min_val:
				raise ValueError(f"Not enough arguments for {args[0]}; Expects exactly {min_val}.")
			elif arg_count > min_val:
				raise ValueError(f"Too many arguments for {args[0]}; Expects exactly {min_val}.")
			else:
				return
		else:
			if arg_count < min_val:
				raise ValueError(f"Not enough arguments for {args[0]}; Expects at least {min_val}.")
			elif arg_count > max_val:
				raise ValueError(f"Too many arguments for {args[0]}; Expects at most {max_val}.")
			else:
				return

	@staticmethod
	def range_validate(args: list[str], index: int, max_val: int, min_val: int = 0) -> None:
		test_val = read(args[index])
		if test_val < min_val or test_val > max_val:
			raise ValueError(
				f"Invalid value [{args[index]}] for argument {index} of {args[0]};" +
				" should be between {min_val} and {max_val}.")
		else:
			return

	@staticmethod
	def set_validate(args: list[str], index: int, valid_values: Union[list, tuple, dict]) -> None:
		if isinstance(valid_values, dict):
			valid_values = list(valid_values.keys())
		test_val = args[index]
		if test_val not in valid_values:
			raise ValueError(
				f"Invalid value [{test_val}] for argument {index} of {args[0]}; should be one of " +
				str(valid_values)[1:-1]
			)
