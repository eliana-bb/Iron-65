"""
This is the end-user file to run.
Development started: 5 Feb 2024
"""
from iron_assembler import Assembler
import os

def main():
    with open("target.txt") as targ:
        in_fp = "input/" + targ.read().strip().lower()
    assembler = Assembler(in_fp)
    assembler.assemble()


if __name__ == "__main__":
    main()
