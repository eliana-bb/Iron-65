import re

pattern_decimal = re.compile(pattern=r"^(?:0d)?(\d{1,5})$", flags=re.IGNORECASE)
pattern_binary = re.compile(pattern=r"^(?:%|0b)((?:[01]{8}){1,2})$", flags=re.IGNORECASE)
pattern_hexadecimal = re.compile(pattern=r"^(?:0x|\$)((?:[0-9a-f]{2}){1,2})$", flags=re.IGNORECASE)

def read(test_str: str) -> int:
	test_str = test_str.replace("_", "")
	dec_match = pattern_decimal.fullmatch(test_str)
	if dec_match is not None:
		return int(dec_match.group(1), 10)
	hex_match = pattern_hexadecimal.fullmatch(test_str)
	if hex_match is not None:
		return int(hex_match.group(1), 16)
	bin_match = pattern_binary.fullmatch(test_str)
	if bin_match is not None:
		return int(bin_match.group(1), 2)
	raise ValueError(f"Could not parse number {test_str}")
