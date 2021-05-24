
import optparse
import sys
from macro_generator.macro_generator import Macro_Generator

if __name__ == '__main__':
    test = Macro_Generator("input.txt")
    test.process_file()