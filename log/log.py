class Log:
    def __init__(self, line=0, message=""):
        self.line = line
        self.message = message

    def write_error(self, line: int, message: str):
        return "error! line:"+str(line)+" "+message + "\n"

    def write_warning(self, line: int, message: str):
        return "warning! line:"+str(line)+ " " + message + "\n"

class Log_Library:
    def __init__(self) -> None:
        pass

    def incorrect_macro_name(self):
        return "Incorrect macro name.\n\t Proper name should consist only of [Aa-Zz] letters.\n\t Skipping this macro definition."
                
    def macro_not_found(self, name):
        return "Macro with name:'" + name +"' "+ "isn't available in the library.\n\t Skipping this macro call."

    def incorrect_hash_usage(self):
        return "Incorrect '#' usage.\n\t To use any macro operation, it has to be provided at the beggining of the line.\n\t Treating it as a free text."
    
    def incorrect_mend_usage(self):
        return "'#MEND' symbol found in input file, but #MDEF haven't been used before.\n\t Skipping this symbol."

        