from macro_generator.macro_library import Macro_Library
from .macro import Macro
import symbols

class Macro_Generator:
    def __init__(self, file):
        self.macrolib = Macro_Library()
        self.text_level = 0
        with open(file) as f:
            self.lines = f.readlines()
            

    def process_file(self):
        counter = 0
        for line in self.lines:
            line = line.strip()
            if line[0:5] == symbols.MACRO_DEFINITION:
                mdef_line = counter
                self.text_level += 1
            if line[0:5] == symbols.MACRO_END:
                if self.text_level < 1:
                    print("Incorrect #MEND symbol.")
                else:
                    mend_line = counter
                    self.__handle_mdef_text(self.lines[mdef_line:mend_line+1])
            if line[0:5] == symbols.MACRO_CALL:
                self.handle_mcall(line[6:])
            counter += 1
            

            
    """function used to handle macro definitions """
    def __handle_mdef_text(self, macro_text):
        splitted_line = macro_text[0].split(' ')

        """checking whether name consists only of letters [Aa-Zz]"""
        if splitted_line[1].isalpha() == False:
            name = splitted_line[1]

        body, parameters_positions = self.__handle_mdef_body(macro_text[1:-1])
        self.macrolib.insert(Macro(name, body, parameters_positions))


                            
    def __handle_mdef_body(self, macro_body):
        """
            function used to handle macro body text
            returns body with parameters symbol removed and parameters positions
            
        """
        parameters_counter = 1
        line_counter = 0
        parameters_positions = {}
        body = []
        """iterating over macro body lines"""
        for line in macro_body:
            line = line.strip()
            """iterating over chars in line"""
            for char_index in range(len(line)):
                """if char is '$' then it is a parameter"""
                if line[char_index] == symbols.PARAMETER:
                    char_index+=1
                    
                    """check whether correct digit is provided after '$' symbl"""
                    if int(line[char_index]) == parameters_counter:
                        parameter_value = symbols.PARAMETER+line[char_index]
                        parameters_positions[line_counter] = char_index-1 #add line number and char position to dictionary
                        parameters_counter += 1
                    else:
                        print("Incorrect parameter number.")
                else:
                    continue
            body.append(line.replace(parameter_value, ''))
            line_counter += 1

        return body, parameters_positions

    def __handle_mcall(self, line):
        for macro in self.macrolib:
            if line[0] == macro.name:
                pass

    def __execute_macro(self, macro):
            pass


    def __add_macro(self):
        pass

    

    def __call_macro(self, name, args):
        pass

