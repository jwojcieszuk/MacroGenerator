from .macro import Macro

class Macro_Library:
    def __init__(self):
        self.library = []

    def insert(self, element: Macro):
        self.library.append(element)

    def get_macro(self, name):
        for macro in self.library:
            if macro.name == name:
                return macro
        return None

    def print_library(self):
        print("Macros available in library:")
        for macro in self.library:
            print(macro.name)
            
        