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
        self.lines_count = 1

    def process_file(self, file):
        """
            function for processing every single line of input file
            once any special symbol is encountered, proper function is called
        """
        line_counter = 0
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
                self.text_level += 1

            elif line[0:5] == symbols.MACRO_END:
                mend_flag = True
                if self.text_level > 1:
                    self.text_level -= 1
                else:
                    self.__handle_mend(lines, mdef_line, line_counter)

            elif line[0:7] == symbols.MACRO_CALL:
                mcall_flag = True
                self.__handle_mcall(line[7:], line_counter)
            else:
                for char in line:
                    if char == '#':
                        warn = self.warning.write_warning(
                            line_counter+1, self.log_library.incorrect_hash_usage())
                        self.log_file.write(warn)

            if self.text_level == 0 and mend_flag == False and mcall_flag == False:
                self.output_file.write(line+"\n")

            self.lines_count += 1
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
        self.macrolib.print_library()
        """checking whether name consists only of letters [Aa-Zz]"""
        if name.strip().isalpha() == True and self.name_is_available(mdef_line, name.strip()) == True:
            body, no_of_params = self.__handle_mdef_body(macro_text[1:-1])
            self.macrolib.insert(Macro(name.strip(), body, no_of_params))
        elif name.strip().isalpha() == False:
            warn = self.warning.write_warning(
                mdef_line+1, self.log_library.incorrect_macro_name())
            self.log_file.write(warn)

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
                        if int(line[char_index]) == parameters_counter:
                            parameters_counter += 1
                        else:
                            print("Incorrect parameter number.")
            line_counter += 1

        return body, parameters_counter

    def __handle_mend(self, lines, mdef_line, line_counter):
        if self.text_level < 1:
            warn = self.warning.write_warning(
                line_counter+1, self.log_library.incorrect_mend_usage())
            self.log_file.write(warn)
        else:
            self.text_level -= 1
            self.__handle_mdef(mdef_line, lines[mdef_line:line_counter+1])

    def __handle_mcall(self, line, mcall_line):
        """
            as a input function takes line where '#MCALL ' was found.
            if macro wasn't found in library, prints an error on this line
            else executes a macro 
        """
        splitted_line = line.split(' ')

        macro = self.macrolib.get_macro(splitted_line[0])
        if macro != None:
            if len(splitted_line) > 1:
                actual_parameters = splitted_line[1].split(',')
                self.__execute_macro(macro, actual_parameters, mcall_line)
            else:
                self.__execute_macro(macro, [], mcall_line)
        else:
            warn = self.warning.write_warning(
                mcall_line+1, self.log_library.macro_not_found(splitted_line[0]))
            self.log_file.write(warn)

    def __execute_macro(self, macro, actual_parameters, mcall_line):
        """
            parameters: macro to be executed
            executing macro means remove #MCALL line and in its place add macro body with parameters placed 
            as a result writes macro body to output file
        """
        if macro.num_of_params > len(actual_parameters):
            warn = self.warning.write_warning(
                mcall_line+1, self.log_library.not_enough_actual_parameters(macro.name, macro.num_of_params))
            self.log_file.write(warn)
            return
        counter = 0
        line_counter = 0
        nested = False

        for line in macro.body:
            to_replace = line
            mend_flag = False
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

            elif line[0:7] == symbols.MACRO_CALL:
                mcall_flag = True
                temp = line.split(' ')
                if temp[1] == macro.name:
                    err = self.error.write_error(mcall_line, self.log_library.infinite_loop())
                    self.log_file.write(err)
                    self.exit_program()
                else:
                    self.__handle_mcall(line[7:], line_counter)
                    line_counter +=1
                continue

            if len(actual_parameters) > 0 and nested == False:
                for char in line:
                    if char == symbols.PARAMETER:
                        to_replace = to_replace.replace(
                            symbols.PARAMETER+str(counter), actual_parameters[counter])
                        counter += 1
            if nested == False and mend_flag == False:
                self.output_file.write(to_replace+'\n')
            line_counter += 1
            self.lines_count += 1

    def name_is_available(self, mdef_line, name):
        if self.macrolib.get_macro(name) == None:
            return True
        else:
            warn = self.warning.write_warning(
                mdef_line+1, self.log_library.already_defined(name))
            self.log_file.write(warn) 

    def exit_program(self):
        sys.exit()