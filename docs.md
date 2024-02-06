# Numbers
Numbers can be expressed in either decimal, binary, or hex. The separator `_` may be inserted inside long numbers to
break up visual noise.

In decimal: `###` or `0d###`, where `#` is a decimal digit. A decimal number may be 1 to 5 digits long.

In binary: `%####_####` or `0b####_####`, where `#` is a bit. Must be either 8 or 16 bits long.

In hexadecimal: `$##` or `0x##`, where `#` is a hex digit. Must be either 2 or 4 digits long. Ex. `$2017`, `0xFF`

# Symbols
Symbols are declared in the form `SYM_NAME = number`. `SYM_NAME` can be any string of letters, numbers, and underscores,
starting with a letter. `number` is any number. Spaces around `=` are optional.

Symbol references are case-insensitive; `PPUDATA` and `ppudata` resolve to the same thing, but `PPUDATA` and `PPU_DATA`
do not.

Symbols are referenced within opcodes by inserting them directly, including any characters denoting addressing mode. 
For example, the following statements are equivalent:
```
LDA $44

Mario_xpos = $44
LDA Mario_xpos
```
```
LDA #$44

Mario_height = $44
LDA #Mario_height
```

# Labels
Labels are declared in the form `LABEL_NAME:`. `LABEL_NAME` can be any string of letters, numbers, and underscores, 
starting with a letter.