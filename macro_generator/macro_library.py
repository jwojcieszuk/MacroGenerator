from .macro import Macro

class Macro_Library:
    def __init__(self):
        self.library = []

    def append(self, element: Macro):
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
    
    def remove_nested(self):
        #self.library[:] = [macro for macro in self.library if macro.nested]
        #self.print_library()
        for macro in reversed(self.library):
            if macro.nested:
                self.library.remove(macro)
        # library_size = len(self.library)
        # refreshed_lib = self.library
        # for macro in range(library_size):
            # if self.library[macro].nested:
                # refreshed_lib.remove(self.library[macro])
            
        