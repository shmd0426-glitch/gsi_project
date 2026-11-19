
# -*- coding: utf-8 -*-

# A directory in format of list [] of dictionaries {}


# =========================
# MODEL
# ========================
class model:
    """Data model class"""

    def __init__(self):
        self.directory = [
            {"firstname": "Ahmed", "familyname": "Mahdi", "tel": "0778787887"},
            {"firstname": "Mohamed", "familyname": "Mahdi", "tel": "0778787887"},
            {"firstname": "Mounir", "familyname": "Katibi", "tel": "0778787887"},
            {"firstname": "Noui", "familyname": "Brahimi", "tel": "0778787887"}
        ]

    def search(self, nom):
        """Look for a telephone by lastname"""

        persons = []

        for person in self.directory:

            # Find people with the given name
            if person["familyname"] == nom:
                persons.append(person)

        # Return a list of dictionaries
        return persons
    def get_all(self):
     """ Find a tel by name"""
     # List of found people
     persons = []
     for persn in self.directory:
      # display all people
      persons.append(persn)
     # a table with field names
     return persons

# =========================
# VIEW
# =========================

class view:

    def __init__(self):
        pass

    def input(self):
        """Retrieve the name to search for"""

        print("Finding a telephone")
        print("Give a name")

        name = input()
        return name

    def output(self, persons):
        """Display information from a list of persons"""

        print("List of found names")
        print("It found %d people(s)" % len(persons))

        for pers in persons:
            print(
                pers["familyname"],
                pers["firstname"],
                pers["tel"]
            )
            


# =========================
# CONTROLLER
# =========================
# sir i modified it to be a class 
class controller:
 def controller(self):

    # Create the model and the view
    data_model = model()
    myview = view()
    persons=data_model.get_all()
    myview.output(persons)
    # Search a name
    name = myview.input()


    # Get data from the model
    persons = data_model.search(name)

    # Display the results
    myview.output(persons)


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    contro=controller()
    contro.controller()