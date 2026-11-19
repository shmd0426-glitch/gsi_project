import sys
import os
from model import model

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "directory.txt")
class model_file(model):
    """Data model class (stored in a text file)"""

    def __init__(self):
        self.directory = []
        try:
            with open(DATA_FILE, encoding="utf-8") as myfile:
                for line in myfile:
                    line = line.strip("\n")
                    if not line:          # skip empty lines
                        continue
                    fields = line.split("\t")
                    person = {}
                    person["familyname"] = fields[0]
                    person["firstname"] = fields[1]
                    person["tel"] = fields[2]
                    self.directory.append(person)
        except FileNotFoundError:
            print("Can't open DataFile")
            sys.exit()

    def save(self):
        """Save the data in the file"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as myfile:
                for person in self.directory:
                    line = "\t".join([person["familyname"],
                                      person["firstname"],
                                      person["tel"]])
                    myfile.write(line + "\n")
        except OSError:
            print("Can't open DataFile")
