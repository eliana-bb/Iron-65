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
starting with a letter. They may not share a name with a symbol, and are case-insensitive.

# Virtual Cartridge Configuration

More details about the NES 2.0 Header can be found [here](https://www.nesdev.org/wiki/NES_2.0).

## `!OUT_FILE`

Configure the final name of the assembled file. If left unspecified, it is inferred based on the input file.

Syntax: `!OUT_FILE <name>`

`name` is the final name of the file. It should usually end in `.nes`.
It will be placed in `/output/`.

## `!PRG_SIZE`

Configure the size of the PRG-ROM. Defaults to `!PRG_SIZE 2`.

Syntax: `!PRG_SIZE <units>` or `.PRG_SIZE <multiplier> <shifts>`

### Linear Mode

If one argument is passed, `!PRG_SIZE` is in linear mode; the number `units` is any number between `0x00` and `0x0EFF`.
The size of the PRG-ROM is 16 KiB × `units`.

### Exponential Mode

If two arguments are passed, `!PRG_SIZE` is in exponential mode; the number `multiplier` is any of `1 3 5 7` (expressed
in any base) and the number `shifts` is any number between `0x00` and `0x3F`.

The size of the PRG-ROM is `multiplier << shifts` bytes. Exponential mode should only be used for values that cannot be
expressed in linear mode.

## `!CHR_SIZE`

Configure the size of the CHR-ROM. Defaults to `!CHR_SIZE 1`.

Syntax: `!CHR_SIZE <units>` or `.CHR_SIZE <multiplier> <shifts>`

### Linear Mode

If one argument is passed, `!CHR_SIZE` is in linear mode; the number `units` is any number between `0x00` and `0x0EFF`.
The size of the CHR-ROM is 8 KiB × `units`.

### Exponential Mode

If two arguments are passed, `!CHR_SIZE` is in exponential mode; the number `multiplier` is any of `1 3 5 7` (expressed
in any base) and the number `shifts` is any number between `0x00` and `0x3F`.

The size of the CHR-ROM is `multiplier << shifts` bytes. Exponential mode should only be used for values that cannot be
expressed in linear mode.

## `!CHR_FILE`

Configure the location of the input CHR-ROM. If left unspecified, a `.chr` file will be searched for within `/input/`.
Size should match `!CHR_SIZE`.

Syntax: `!CHR_FILE <path>`

`path` is the path to a file, relative to `/input/`.

## `!MIRROR_MODE`

Configure the hard-wired nametable mirroring mode. Defaults to `!MIRROR_MODE VERTICAL`.

Syntax: `!MIRROR_MODE <mode>`

`mode` is one of `VERTICAL`, `HORIZONTAL`, or `MAPPER`.

`VERTICAL` means vertical mirroring, creating horizontally-arranged nametables. This is used by Super Mario Bros. 1.

`HORIZONTAL` means horizontal mirroring, creating vertically-arranged nametables. This is used by Super Marior Bros. 3.

`MAPPER` means the nametable mirroring can be controlled and changed by the mapper. Select this if your mapper allows
it.

Read more [here](https://www.nesdev.org/wiki/Mirroring#Nametable_Mirroring).

## `!BATTERY`

Whether the cartridge has battery-backed (or other non-volatile) memory. Defaults to `!BATTERY FALSE`.

Syntax: `!BATTERY <bool>`

`bool` is one of `TRUE` or `FALSE`.

## `!TRAINER`

Whether to insert a 512-byte trainer between the header and PRG-ROM. Defaults to `!TRAINER FALSE`.

Syntax: `!TRAINER <path>`

`path` is either the path to a 512-byte file (relative to `/input/`) or `FALSE`.

## `!CONSOLE_TYPE`

What type of console this game is for. Defaults to `!CONSOLE_TYPE NES`.

Syntax: `!CONSOLE_TYPE <type>` or `!CONSOLE_TYPE VS_SYSTEM <ppu> <hardware>`.

`type` is any of `NES`, `FAMICOM`, `DENDY`, `VS_SYSTEM`, `PLAYCHOICE_10`, `FAMICLONE_DECIMAL`, `NES_EPSM`,
`FAMICOM_EPSM`, `VT01`, `VT02`, `VT03`, `VT09`, `VT32`, `VT369`, `UM6578`, or `FAMICOM_NETWORK`.

Read more [here](https://www.nesdev.org/wiki/NES_2.0#Extended_Console_Type).

### Vs. System configuration

If `!CONSOLE_TYPE` is `VS_SYSTEM`, two more parameters are required.

`ppu` is one of `RP2C03B`, `RP2C03G`, `RP2C04-0001`, `RP2C04-0002`, `RP2C04-0003`, `RP2C04-0004`, `RC2C03B`, `RC2C03C`,
`RC2C05-01`, `RC2C05-02`, `RC2C05-03`, `RC2C05-04`, or `RC2C05-05`.

`hardwaretype` is one of `NORMAL`, `RBI_BASEBALL`, `TKO_BOXING`, `SUPER_XEVIOUS`, `VS_ICE_CLIMBER`, `DUAL`, or
`DUAL_BUNGELING`.

Read more about these [here](https://www.nesdev.org/wiki/NES_2.0#Vs._System_Type).

## `!MAPPER`

What type of cartridge the game is on. Defaults to `!MAPPER 0`.

Syntax: `!MAPPER <mapper> [submapper]`

`mapper` is any number between `0x00` and `0x0FFF` (although only mappers through ~`0x02FF` are documented and
implemented in most emulators.)

`submapper` is an optional number between `0x00` and `0x0F`.

Read more about [mappers](https://www.nesdev.org/wiki/Mapper)
and [submappers](https://www.nesdev.org/wiki/NES_2.0_submappers).

## `!PRG_RAM_SIZE`, `!PRG_NVRAM_SIZE`, `!CHR_RAM_SIZE`, `!CHR_NVRAM_SIZE`

Determines the size of PRG-RAM, PRG-NVRAM, CHR-RAM, and CHR-NVRAM. All four default to zero, ex. `!PRG_RAM_SIZE 0`.

Syntax: ex. `!PRG_RAM_SIZE <shifts>`

`shifts` is a number between `0x00` and `0x0F`. The total size of the given type of memory is `64 << shifts`.

Read more [here](https://www.nesdev.org/wiki/NES_2.0#PRG-(NV)RAM/EEPROM).

## `!REGION`

Determines the region (timing mode) of the console. Defaults to `!REGION NTSC`.

Syntax: `!REGION <region>`

`region` is one of `NTSC`, `PAL`, `DENDY`, or `MULTI`. `MULTI` should be used when the cart can detect and change timing
modes dynamically.

## `!MISC_ROMS`

Whether to insert between 1 and 4 ROMs at the end of the file. Defaults to `!MISC_ROMS FALSE`

Syntax: `!MISC_ROMS <path1> [path2] ...`

`path#` is a path to a binary file (relative to `/input/`) or `FALSE`. Between 1 and 4 paths may be specified.

Read more [here](https://www.nesdev.org/wiki/NES_2.0#Miscellaneous_ROM_Area).

## `!DEFAULT_DEVICE`

The default expansion device (i.e. controller) used by this game. Defaults to `!DEFAULT_DEVICE 1`.

Syntax: `!DEFAULT_DEVICE <id>`

`<id>` is a number between `0x00` and `0x3A`. A list of controllers and their IDs can be found
[here](https://www.nesdev.org/wiki/NES_2.0#Default_Expansion_Device).