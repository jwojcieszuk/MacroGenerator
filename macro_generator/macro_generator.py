from .macro_library import Macro_Library
from .macro import Macro
from log.log import Log, Log_Library
import symbols
import sys

class Macro_Generator:

    def __init__(self):
        self.macrolib = Macro_Library()
        self.text_level = 0
        self.output_file = None
        self.log_file = None
        self.error = Log()
        self.warning = Log()
        self.log_library = Log_Library()

    def process_file(self, file):
        """
            function for processing every single line of input file
            once any special symbol is encountered, proper function is called
        """
        line_counter = 0
        mdef_line = 0
        mdef_flag = False
        self.output_file = open("output.txt", "w+")
        self.log_file = open("log.txt", "w+")

        with open(file) as f:
            lines = f.readlines()

        for line in lines:
            mend_flag = False
            mcall_flag = False
            line = line.strip()

            if line[0:6] == symbols.MACRO_DEFINITION:
                if self.text_level == 0:
                    mdef_line = line_counter
                    mdef_flag = True
                self.text_level += 1

            elif line[0:5] == symbols.MACRO_END:
                mend_flag = True
                if self.text_level > 1:
                    self.text_level -= 1
                elif mdef_line != 0:
                    self.__handle_mend(lines, mdef_line, line_counter)

            elif line[0:6] == symbols.MACRO_CALL and self.text_level == 0:
                mcall_flag = True
                self.__handle_mcall(line[6:], line_counter)
            elif self.text_level == 0:
                for char in line:
                    if char == '#':
                        self.warning_to_log(line_counter+1, self.log_library.incorrect_hash_usage())

            if self.text_level == 0 and mend_flag == False and mcall_flag == False:
                self.output_file.write(line+"\n")

            line_counter += 1

        self.output_file.close()
        self.log_file.close()

    def __handle_mdef(self, mdef_line, macro_text):
        """
            function as a parameter gets:
            #MDEF name
            body
            #MEND
            as a result adds macro to macro library, with name, 
            body without parameters and number of parameters
        """
        splitted_line = macro_text[0].split(' ')

        name = splitted_line[1]
        """checking whether name consists only of letters [Aa-Zz]"""
        if name.strip().isalpha() == True and self.name_is_available(mdef_line, name.strip()) == True:
            body, no_of_params = self.__handle_mdef_body(macro_text[1:-1])
            self.macrolib.insert(Macro(name.strip(), body, no_of_params))
            
        elif name == symbols.MACRO_CALL:
            concat = ' '+' '.join(splitted_line[2:])
            mcall_flag = True
            name = self.__handle_mcall(concat.replace('\n', ''), mdef_line, mcall_flag)
            body, no_of_params = self.__handle_mdef_body(macro_text[1:-1])
            self.macrolib.insert(Macro(name.strip(), body, no_of_params))
            mcall_flag = False

        elif name.strip().isalpha() == False:
            self.warning_to_log(mdef_line+1, self.log_library.incorrect_macro_name())

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

            if line[0:6] == symbols.MACRO_DEFINITION:
                self.text_level += 1
                line_counter += 1
                continue

            elif line[0:5] == symbols.MACRO_END:
                self.text_level -= 1
                line_counter += 1
                continue

            if self.text_level == 0:
                for char_index in range(len(line)):
                    """if char is '$' then it is a parameter"""
                    if line[char_index] == symbols.PARAMETER:
                        char_index += 1
                        """check whether correct digit is provided after '$' symbol"""
                        if int(line[char_index]) != parameters_counter:
                            self.warning_to_log(line_counter+1, self.log_library.incorrect_parameter_number())
                        parameters_counter += 1
            line_counter += 1

        return body, parameters_counter

    def __handle_mcall(self, line, mcall_line, mcall_flag=False):
        """
            as a input function takes line where '#MCALL ' was found.
            if macro wasn't found in library, prints an error on this line
            else executes a macro 
        """
        self.macrolib.print_library()
        splitted_line = line.split(' ')
        output = ""
        macro = self.macrolib.get_macro(splitted_line[1])
        if macro != None:
            if len(splitted_line) > 2:
                actual_parameters = line[len(splitted_line[1])+2:]
                if symbols.MACRO_CALL in actual_parameters:
                    for index, char in enumerate(actual_parameters):
                        if char == '#':
                            hash_index = index
                        if char == ';':
                            semicolon_index = index
                            nested_mcall = actual_parameters[hash_index+6:semicolon_index]
                            nested_mcall_output = self.__handle_mcall(nested_mcall, mcall_line, True)
                            substring_to_replace = actual_parameters[hash_index:semicolon_index+1]
                    actual_parameters = actual_parameters.replace(substring_to_replace, nested_mcall_output)
                actual_parameters = actual_parameters.split(',')        
                for param in actual_parameters:
                    if param.isalpha() == False:
                        self.warning_to_log(mcall_line+1, self.log_library.actual_parameter_isnotalpha())
                        return
                output = self.__execute_macro(macro, actual_parameters, mcall_line, mcall_flag)
            else:
                output = self.__execute_macro(macro, [], mcall_line, mcall_flag)
        else:
            self.warning_to_log(mcall_line+1, self.log_library.macro_not_found(splitted_line[1]))
        return output

    def __execute_macro(self, macro, actual_parameters, mcall_line, mcall_flag = False):
        """
            parameters: macro to be executed
            executing macro means remove #MCALL line and in its place add macro body with parameters placed 
            as a result writes macro body to output file
        """
        if macro.num_of_params > len(actual_parameters):
            self.warning_to_log(mcall_line+1, self.log_library.not_enough_actual_parameters(macro.name, macro.num_of_params))
            return
        counter = 0
        line_counter = 0
        nested = False
        output = ""
        for line in macro.body:
            to_replace = line
            mend_flag = False
            mcall_flag = False
            if line[0:6] == symbols.MACRO_DEFINITION:
                nested = True
                if self.text_level == 0:
                    mdef_line = line_counter
                self.text_level += 1
                line_counter +=1
                continue

            elif line[0:5] == symbols.MACRO_END:
                mend_flag = True
                if self.text_level > 1:
                    self.text_level -= 1
                else:
                    self.__handle_mend(macro.body, mdef_line, line_counter)
                    nested = False
                    line_counter +=1
                    continue

            elif line[0:6] == symbols.MACRO_CALL:
                if self.text_level > 0:
                    line_counter += 1
                    continue
                mcall_flag = True
                temp = line.split(' ')
                if temp[1] == macro.name:
                    self.error_to_log(mcall_line, self.log_library.infinite_loop())
                else:
                    self.__handle_mcall(line[6:], line_counter)
                    line_counter +=1
                continue

            if len(actual_parameters) > 0 and nested == False:
                for char in line:
                    if char == symbols.PARAMETER:
                        to_replace = to_replace.replace(
                            symbols.PARAMETER+str(counter), actual_parameters[counter])
                        counter += 1
            if nested == False and mend_flag == False:
                output += to_replace
                if mcall_flag == False:
                    self.output_file.write(to_replace+'\n')
            line_counter += 1
        return output

    def __handle_mend(self, lines, mdef_line, line_counter):
        if self.text_level < 1:
            self.warning_to_log(line_counter+1, self.log_library.incorrect_mend_usage())
        else:
            self.text_level -= 1
            self.__handle_mdef(mdef_line, lines[mdef_line:line_counter+1])
            
    def name_is_available(self, mdef_line, name):
        if self.macrolib.get_macro(name) == None:
            return True
        else:
            self.warning_to_log(mdef_line+1, self.log_library.already_defined(name))

    def warning_to_log(self, line, case):
        warn = self.warning.write_warning(line, case)
        self.log_file.write(warn) 

    def error_to_log(self, line, case):
        err = self.error.write_error(line, case)
        self.log_file.write(err)
        sys.exit()
