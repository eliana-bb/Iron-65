"""
This is the end-user file to run.
Development started: 5 Feb 2024
"""
from iron_assembler import Assembler

def main():
    in_fp = input("Input file: ")
    if in_fp == "":
        in_fp = "test.asm"

    assembler = Assembler(in_fp)
    assembler.assemble()


if __name__ == "__main__":
    main()
