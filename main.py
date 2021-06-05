import argparse
from macro_generator.macro_generator import Macro_Generator

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-input",
        action="store_true",
        help="input file",
    )
    parser.add_argument(
        "-test",
        action="store_true",
        help="test program",
    )
    args = parser.parse_args()
    #macrogen = Macro_Generator()
    #macrogen.process_file("input.txt")
    if args.test:
        macrogen = Macro_Generator()
        macrogen.test()
    elif args.input:
        macrogen = Macro_Generator()
        macrogen.process_file("input.txt")
        


    
