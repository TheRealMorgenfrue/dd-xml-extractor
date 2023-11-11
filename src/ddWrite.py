import re

substitutions = 0
def writeFile(pathOptions, config):
    """Writes data from the translated input file to the specified output XML file. 
    Uses regex to insert input text between "[ and "]]" e.g. [text goes here]].

    Args:
        pathOptions (dataclass): A dataclass (struct) containing all paths and path names used in the program.

    """

    def WriteAll():
        i = 0
        for line in pathOptions.sanitizedXML:
            if(re.search(r"([^\[]+?)(?=]{2})", line) is not None):
                match_obj_sub = re.sub(r"([^\[]+?)(?=]{2})", backslashToString, line)

                if(i == len(txt_input)):
                    open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(match_obj_sub)
                else:
                    open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(match_obj_sub+"\n")
            #print(f"{i} + {i < len(txt_input)}") # For testing purposes
                i += 1
            else:
                if(i > len(txt_input)):
                    open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(line)
                else:
                    open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(line+"\n")

    def Write(line, is_substituting: bool=False):
        """Helper function for writeFile. 
        Takes a string from the txt input line and replaces 
        the equivalent string in the output XML file with this string.
        """
        if(is_substituting):
            if(re.search(r"([^\[]+?)(?=]{2})", line) is not None): # Found a string between "[" and "]]" to substitute
                match_obj_sub = re.sub(r"([^\[]+?)(?=]{2})", backslashToString, line) # Substitute found string with the equivalent, translated string
                open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(match_obj_sub + "\n")
            else:
                open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(line + "\n")
        else:
            #print(f"{line}")
            open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(line + "\n")
    
    def backslashToString(match_obj: object)->str:
        """Helper function for writeFile. 
        Simple toString function to prevent re.sub from interpretating backslashes in the replacement string as escape characters.\n
        The argument "match_obj" is a requirement for this function, although it's unused.
        To see why this is the case, view the docs: https://docs.python.org/3/library/re.html#re.sub

        Args:
            match_obj (object): The match object as returned by re.

        Returns:
            str: The string from the translated input file (casted to string to be safe)
        """
        global substitutions
        if(substitutions < len(txt_input)):
            #print(f"{substitutions}: {txt_input[substitutions]}") # For testing purposes
            string = str(txt_input[substitutions])
            substitutions += 1
            return string
        else:
            print(f"Warning: substitutions ({substitutions}) < len(txt_input) ({len(txt_input)}) is {substitutions < len(txt_input)}. This will have unintended consequences!")
            return ""
    
    txt_input = open(pathOptions.InTXTPath, "r", encoding="utf-8").read().splitlines() # splitlines() breaks each line after the newline
    lang = config.LanguageTag

    if(lang == ""): # Extract and write whole document
        WriteAll()
    else: # Extract only within XML language tag belonging to "lang"
        is_substituting = False

        for line in pathOptions.sanitizedXML:
            if(is_substituting):
                if(re.search(r"(<\/language)(?=\>)", line) is not None): # Found </language> while writing. Thus, end of language section to write is reached
                    Write(line) # Write full line to output XML
                else:
                    Write(line, is_substituting) # Write substituted line to output XML
            else:
                Write(line) # Write full line to output XML

            if(re.search(r"(<language id=\")(?!>)", line) is not None): # Found a <language id= tag. (In <language id="english"> find <language id=)
                if(re.search(f"({lang})(?=\">)", line) is not None): # The language in that tag is what we're looking for
                    is_substituting = True
                else: # 
                    is_substituting = False