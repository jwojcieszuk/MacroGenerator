class Log:
    def __init__(self, line=0, message=""):
        self.line = line
        self.message = message


class Log_Library:

    def __init__(self) -> None:
        pass
    
    def incorrect_macro_name(self):
        return "Incorrect macro name.\n\t Proper name should consist only of [Aa-Zz] letters.\n\tSkipping this macro definition."

    def macro_not_found(self, name):
        return "Macro with name:'" + name + "' " + "isn't available in the library.\n\tSkipping this macro call."

    def incorrect_hash_usage(self):
        return "Incorrect '#' usage.\n\tTo use any macro operation, it has to be provided at the beggining of the line.\n\tTreating it as a free text."

    def mend_usage_without_mdef(self):
        return "'#MEND' symbol found in input file, but #MDEF haven't been used before.\n\tSkipping this symbol."

    def incorrect_mcall_usage(self):
        return "'#MCALL' symbol found not at the beggining of the line.\n\tSkipping this symbol."

    def incorrect_mend_usage(self):
        return "'#MEND' symbol found not at the beggining of the line.\n\tSkipping this symbol."

    def incorrect_mdef_usage(self):
        return "'#MDEF' symbol found not at the beggining of the line.\n\tSkipping this symbol."

    def not_enough_actual_parameters(self, name, num_of_params):
        return "Not enough actual parameters passed to macro:'" + name + "' required: " + str(num_of_params) + "\n\tSkipping this macro call."

    def already_defined(self, name):
        return "Macro with name:'" + name + "' is already defined.\n\tSkipping this macro definition."

    def infinite_loop(self):
        return "Macro definition with call to itself. Possible infinite loop.\n\tExiting program."

    def actual_parameter_isnotalpha(self):
        return "Actual parameter should consist only of [Aa-Zz] letters.\n\tSkipping this macro call."

    def incorrect_parameter_number(self):
        return "Incorrect parameter number provided after '$' symbol.\n\tSkipping this parameter."

    def error(self, line: int, message: str):
        return "error! line:"+str(line)+" "+message + "\n"

    def warning(self, line: int, message: str):
        return "warning! line:"+str(line) + " " + message + "\n"

    
