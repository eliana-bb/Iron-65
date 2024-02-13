"""
This is the end-user file to run.
Development started: 5 Feb 2024
"""
from src.iron_assembler import Assembler
import os

def main():
    for file in os.listdir("../input"):
        if file.endswith(".asm") or file.endswith(".s"):
            in_fp = "input/" + file
            break
    else:
        raise FileNotFoundError("Can't find source file!")
    assembler = Assembler(in_fp)
    assembler.assemble()


if __name__ == "__main__":
    main()
