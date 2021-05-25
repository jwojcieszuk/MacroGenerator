from .macro import Macro

class Macro_Library:
    def __init__(self):
        self.library = []

    def insert(self, element: Macro):
        for macro in self.library:
            if macro.name == element.name:
                print("Macro already defined")
                return
        self.library.append(element)

    def get_macro(self, name):
        for macro in self.library:
            if macro.name == name:
                return macro
        return None
            
        