from .macro_library import Macro_Library
from .macro import Macro
import symbols

class Macro_Generator:

    def __init__(self, file):
        self.macrolib = Macro_Library()
        self.text_level = 0
        with open(file) as f:
            self.lines = f.readlines()

    def process_file(self):
        """
            function for processing every single line of input file
            once any special symbol is encountered, proper function is called
        """
        line_counter = 0
        self.output_file = open("output.txt", "w+")
            
        for line in self.lines:
            line = line.strip()

            if line[0:6] == symbols.MACRO_DEFINITION:
                mdef_line = line_counter
                self.text_level += 1

            elif line[0:5] == symbols.MACRO_END:
               self.__handle_mend(mdef_line, line_counter)
               self.text_level -=1

            elif line[0:7] == symbols.MACRO_CALL:
                self.__handle_mcall(line[7:])
            elif self.text_level == 0:
                self.output_file.write(line+"\n")
            line_counter += 1
        self.output_file.close()

    def __handle_mdef(self, macro_text):
        """
            function as a parameter gets:
            #MDEF name
            body
            #MEND
            as a result adds macro to macro library, with name, 
            body without parameters and number of parameters
        """
        splitted_line = macro_text[0].split(' ')

        """checking whether name consists only of letters [Aa-Zz]"""
        if splitted_line[1].isalpha() == False:
            name = splitted_line[1]

        body, no_of_params = self.__handle_mdef_body(macro_text[1:-1])
        self.macrolib.insert(Macro(name.strip(), body, no_of_params))


                            
    def __handle_mdef_body(self, macro_body):
        """
            function used to handle macro body text
            returns body with parameters symbol removed and parameters positions
        """
        parameters_counter = 0
        line_counter = 0
        body = []

        """iterating over macro body lines"""
        for line in macro_body:
            line = line.strip()
            body.append(line)
            """iterating over every char in line"""
            for char_index in range(len(line)):
                """if char is '$' then it is a parameter"""
                if line[char_index] == symbols.PARAMETER:
                    char_index+=1
                    """check whether correct digit is provided after '$' symbol"""
                    if int(line[char_index]) == parameters_counter:
                        parameters_counter += 1
                    else:
                        print("Incorrect parameter number.")
            line_counter += 1

        return body, parameters_counter

    def __handle_mend(self, mdef_line, line_counter):
        if self.text_level < 1:
            print("Incorrect #MEND symbol.")
        else:
            self.__handle_mdef(self.lines[mdef_line:line_counter+1])

    def __handle_mcall(self, line):
        """
            as a input function takes line where '#MCALL ' was found.
            if macro wasn't found in library, prints an error on this line
            else executes a macro 
        """
        
        splitted_line = line.split(' ')
        
        macro = self.macrolib.get_macro(splitted_line[0])
        if macro != None:
            actual_parameters = splitted_line[1].split(',')
            self.__execute_macro(macro, actual_parameters)

    def __execute_macro(self, macro, actual_parameters):
        """
            parameters: macro to be executed
            executing macro means remove #MCALL line and in its place add macro body with parameters placed 
            as a result writes macro body to output file
        """
        if macro.num_of_params > len(actual_parameters):
            print("There wasn't enough actual_parameters passed!")
            return
        counter = 0
        output = []
        for line in macro.body:
            to_replace = line
            for char in line:
                if char == symbols.PARAMETER:
                    to_replace = to_replace.replace(symbols.PARAMETER+str(counter), actual_parameters[counter])
                    counter+=1
            self.output_file.write(to_replace+'\n')
                    