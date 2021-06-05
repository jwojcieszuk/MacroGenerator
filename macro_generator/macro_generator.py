from .macro_library import Macro_Library
from .macro import Macro
from log.log import Log, Log_Library
import symbols
import sys
import os

class Macro_Generator:

    def __init__(self):
        self.macrolib = Macro_Library()
        self.text_level = 0
        self.output_file = None
        self.log_file = None
        self.log_library = Log_Library()

    """function used for testing"""
    def __init(self):
        self.macrolib = Macro_Library()
        self.text_level = 0
        self.output_file = None
        self.log_file = None

    def process_file(self, file):
        """
            function for processing every single line of input file
            once any special symbol is encountered, proper function is called
            reads from input file and writes to output and log files
        """
        if os.path.getsize(file) == 0:
            print("Error! Input file is empty.")
            return

        line_counter = 0
        mdef_line = -1
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
                elif mdef_line != -1:
                    self.__handle_mend(lines, mdef_line, line_counter)
                else:
                    self.__write_warning(
                        line_counter+1, self.log_library.mend_usage_without_mdef())

            elif line[0:6] == symbols.MACRO_CALL and self.text_level == 0:
                mcall_flag = True
                self.__handle_mcall(line[6:], line_counter)
                self.macrolib.remove_nested()

            elif symbols.MACRO_DEFINITION in line:
                self.__write_warning(
                    line_counter+1, self.log_library.incorrect_mdef_usage())

            elif symbols.MACRO_END in line:
                self.__write_warning(
                    line_counter+1, self.log_library.incorrect_mend_usage())

            elif symbols.MACRO_CALL in line and self.text_level == 0:
                self.__write_warning(
                    line_counter+1, self.log_library.incorrect_mcall_usage())

            elif '#' in line and self.text_level == 0:
                self.__write_warning(
                    line_counter+1, self.log_library.incorrect_hash_usage())

            if self.text_level == 0 and mend_flag == False and mcall_flag == False:
                self.output_file.write(line+"\n")

            line_counter += 1
        self.log_file.close()
        self.output_file.close()
        self.__print_err_to_console()
        
        
    def __print_err_to_console(self):
        read_errors = open("log.txt", "r")
        
        messages = read_errors.readlines()
        if messages:
            print("----------------------------")
            print("Warnings and errors")
            print("----------------------------")
            for msg in messages:
                print(msg)
            print("----------------------------")
        read_errors.close()

    def __handle_mdef(self, mdef_line, macro_text, nested):
        """
            function used to validate syntax
            if it is correct, inserts macro to library
        """

        splitted_line = macro_text[0].split(' ')
        name = splitted_line[1]

        # checking whether name consists only of letters [Aa-Zz]
        if name.strip().isalpha() == True and self.__is_name_available(mdef_line, name.strip()) == True:
            body, no_of_params = self.__handle_mdef_body(macro_text[1:-1])
            self.macrolib.insert(Macro(name.strip(), body, no_of_params, nested))
        
        # checking whether #MCALL was provided as macro name
        elif name == symbols.MACRO_CALL:
            concat = ' '+' '.join(splitted_line[2:])
            mcall_flag = True
            name = self.__handle_mcall(
                concat.replace('\n', ''), mdef_line, mcall_flag)
            if ' ' in name:
                self.__write_warning(
                    mdef_line+1, self.log_library.incorrect_macro_name())
                return
            body, no_of_params = self.__handle_mdef_body(macro_text[1:-1])
            self.macrolib.insert(Macro(name.strip(), body, no_of_params, nested))
            mcall_flag = False

        elif name.strip().isalpha() == False:
            self.__write_warning(
                mdef_line+1, self.log_library.incorrect_macro_name())

    def __handle_mdef_body(self, macro_body):
        """
            function used to handle macro body text
            returns body with parameters counted
        """
        parameters_counter = 0
        line_counter = 0
        body = []

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
                parameters_counter = self.__validate_positional_parameters(line, parameters_counter, line_counter)
            line_counter += 1

        return body, parameters_counter

    def __validate_positional_parameters(self, line, parameters_counter, line_counter):
        for char_index in range(len(line)):
            if line[char_index] == symbols.PARAMETER:
                char_index += 1
                """check whether correct digit is provided after '$' symbol"""
                if int(line[char_index]) != parameters_counter:
                    self.__write_warning(line_counter+1, self.log_library.incorrect_parameter_number())
                parameters_counter += 1
        return parameters_counter

    def __handle_mcall(self, line, mcall_line, mcall_flag=False):
        """
            as a input function takes line where '#MCALL ' was found.
            if macro wasn't found in library, prints an error on this line
            else executes a macro
        """
        splitted_line = line.split(' ')
        output = ""
        macro = self.macrolib.get_macro(splitted_line[1])
        if macro != None:
            if len(splitted_line) > 2:
                actual_parameters = line[len(splitted_line[1])+2:]
                actual_parameters = self.__validate_actual_parameters(actual_parameters, mcall_line)
                output = self.__execute_macro(
                    macro, actual_parameters, mcall_line, mcall_flag)
            else:
                output = self.__execute_macro(
                    macro, [], mcall_line, mcall_flag)
        else:
            self.__write_warning(
                mcall_line+1, self.log_library.macro_not_found(splitted_line[1]))
        return output

    def __validate_actual_parameters(self, actual_parameters, mcall_line):
        """
            function validates actual parameters
            if #MCALL was found as actual parameter it executes macro called
        """
        if symbols.MACRO_CALL in actual_parameters:
            actual_parameters = self.__mcall_as_actual_param(actual_parameters, mcall_line)
        actual_parameters = actual_parameters.split(',')
        for param in actual_parameters:
            if param.isalpha() == False:
                self.__write_warning(mcall_line+1, self.log_library.actual_parameter_isnotalpha())
                return
        return actual_parameters

    def __mcall_as_actual_param(self, actual_parameters, mcall_line):
        """
            function to handle mcall passed as actual parameter
            if syntax was correct, returns output of macro called in place of #MCALL
        """
        substring_to_replace = ""
        for index, char in enumerate(actual_parameters):
            if char == '#':
                hash_index = index
            if char == ';':
                semicolon_index = index
                nested_mcall = actual_parameters[hash_index + 6:semicolon_index]
                nested_mcall_output = self.__handle_mcall(nested_mcall, mcall_line, True)
                substring_to_replace = actual_parameters[hash_index:semicolon_index+1]
        if substring_to_replace != "":
            actual_parameters = actual_parameters.replace(substring_to_replace, nested_mcall_output)
        return actual_parameters

    def __execute_macro(self, macro, actual_parameters, mcall_line, mcall_flag=False):
        """
            parameters: macro to be executed
            executing macro means remove #MCALL line and in its place add macro body with parameters placed 
            as a result writes macro body to output file
        """
        if macro.num_of_params > len(actual_parameters):
            self.__write_warning(
                mcall_line+1, self.log_library.not_enough_actual_parameters(macro.name, macro.num_of_params))
            return
        counter = 0
        line_counter = 0
        nested = False
        output = ""
        to_remove = []
        for line in macro.body:
            to_replace = line
            mend_flag = False

            if line[0:6] == symbols.MACRO_DEFINITION:
                nested = True
                if self.text_level == 0:
                    mdef_line = line_counter
                self.text_level += 1
                line_counter += 1
                continue

            elif line[0:5] == symbols.MACRO_END:
                mend_flag = True
                if self.text_level > 1:
                    self.text_level -= 1
                else:
                    self.__handle_mend(macro.body, mdef_line, line_counter, nested)
                    nested = False
                    line_counter += 1
                    continue

            elif line[0:6] == symbols.MACRO_CALL:
                if self.text_level > 0:
                    line_counter += 1
                    continue

                temp = line.split(' ')

                if temp[1] == macro.name:
                    self.__write_error(
                        mcall_line, self.log_library.infinite_loop())
                else:
                    self.__handle_mcall(line[6:], line_counter)
                    line_counter += 1
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

    def __handle_mend(self, lines, mdef_line, line_counter, nested=False):
        if self.text_level < 1:
            self.__write_warning(
                line_counter+1, self.log_library.incorrect_mend_usage())
        else:
            self.text_level -= 1
            self.__handle_mdef(mdef_line, lines[mdef_line:line_counter+1], nested)

    def __is_name_available(self, mdef_line, name):
        if self.macrolib.get_macro(name) == None:
            return True
        else:
            self.__write_warning(
                mdef_line+1, self.log_library.already_defined(name))
            return False

    def __write_warning(self, line, case):
        warn = self.log_library.warning(line, case)
        self.log_file.write(warn)

    def __write_error(self, line, case):
        err = self.log_library.error(line, case)
        self.log_file.write(err)
        sys.exit()

    def __test_case(self, input_file, output_file):
        self.__init()
        self.process_file("test files/test cases/"+input_file)
        with open("output.txt") as o:
            out = o.readlines()
        with open("test files/desired_output/"+output_file) as f:
            desired_out = f.readlines()
        o.close()
        f.close()
        if (out == desired_out):
            return True
        return False

    def test(self):
        counter = 0
        test_cases = 10

        print("Performing basic test...")
        if self.__test_case("test_basic.txt", "output_basic.txt"):
            counter += 1
            print("Basic test completed correctly.")
        else:
            print("Wrong! Basic test completed incorrectly.")

        print("----------------------------")
        print("Performing redefinition test...")
        if self.__test_case("test_redefinition.txt", "output_redefinition.txt"):
            counter += 1
            print("Redefinition test completed correctly.")
        else:
            print("Wrong! Redefinition test completed incorrectly.")

        print("----------------------------")
        print("Performing MCALL passed as parameter test...")
        if self.__test_case("test_mcall_as_param.txt", "output_mcall_as_param.txt"):
            counter += 1
            print("Test for MCALL passed as parameter completed correctly.")
        else:
            print("Wrong! Test for MCALL passed as parameter completed incorrectly.")

        print("----------------------------")
        print("Performing incorrect syntax test...")
        if self.__test_case("test_incorrect_syntax.txt", "output_incorrect_syntax.txt"):
            counter += 1
            print("Test for incorrect syntax completed correctly.")
        else:
            print("Wrong! Test for incorrect syntax completed incorrectly.")

        print("----------------------------")
        print("Performing triple nested MDEF test...")
        if self.__test_case("test_triple_nested_mdef.txt", "output_triple_nested_mdef.txt"):
            counter += 1
            print("Test for triple nested mdef completed correctly.")
        else:
            print("Wrong! Test for triple nested mdef completed incorrectly.")

        print("----------------------------")
        print("Performing nested MCALL test...")
        if self.__test_case("test_nested_mcall.txt", "output_nested_mcall.txt"):
            counter += 1
            print("Test for nested mcall completed correctly.")
        else:
            print("Wrong! Test for nested mcall completed incorrectly.")

        print("----------------------------")
        print("Performing mcall as mdef name test...")
        if self.__test_case("test_mcall_as_mdef_name.txt", "output_mcall_as_mdef_name.txt"):
            counter += 1
            print("Test for MCALL as MDEF name completed correctly.")
        else:
            print("Wrong! Test for MCALL as MDEF name completed incorrectly.")

        print("----------------------------")
        print("Performing nested params test...")
        if self.__test_case("test_nested_params.txt", "output_nested_params.txt"):
            counter += 1
            print("Test for nested parameters completed correctly.")
        else:
            print("Wrong! Test for nested parameters completed incorrectly.")

        print("----------------------------")
        print("Performing mcall as param test...")
        if self.__test_case("test_mcall_as_param.txt", "output_mcall_as_param.txt"):
            counter += 1
            print("Test for MCALL passed as parameter completed correctly.")
        else:
            print("Wrong! Test for MCALL passed as parameter completed incorrectly.")

        print("----------------------------")
        print("Performing advanced nesting test...")
        if self.__test_case("test_advanced_nesting.txt", "output_advanced_nesting.txt"):
            counter += 1
            print("Test for advanced nesting completed correctly.")
        else:
            print("Wrong! Test for advanced nesting completed incorrectly.")

        print("----------------------------")
        if counter == test_cases:
            print("Success! All tests completed correctly.")
        else:
            print("Wrong! Some tests failed.")
