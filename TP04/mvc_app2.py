
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
    
    #adding a method for add persons
    def add(self, name, firstname, tel):
     """ Add a person """
     person ={}
     person["familyname"] = name

     person["firstname"] = firstname
     person["tel"] = tel
     self.directory.append(person)

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
    #adding view to display it on user interface         
    def input_add(self):
     """get name to add"""
     print("Add a person")
     print("Give a name")
     name = input()
     print("Give a firstname")
     firstname = input()
     print("Give a telephone")
     tel = input()
     return (name, firstname, tel)  
     #adding more peoples we add this method     
    def ask_continue(self):
     """Ask if the user wants to add another person"""
     answer = input("Add another person? (y/n): ")
     return answer.lower() == "y"

# =========================
# CONTROLLER
# =========================
# sir i modified it to be a class 
class controller:
   def __init__(self):
     self.data_model = model()
     self.myview = view()
 
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
   def add(self):
     """ Add a new name """
     #there was error when you write affichage
     name, firstname, tel = self.myview.input_add()
     self.data_model.add(name, firstname, tel)
     persons = self.data_model.get_all()
     self.myview.output(persons)
     #tel = input()
     #return name, firstname, tel
   # adding this method for many people and delting  tel and return name.....
   def add_many(self):
     """ Add several persons """
     while True:
       self.add()
       if not self.myview.ask_continue():
         break
     # display the directory once, at the end
     self.myview.output(self.data_model.get_all())

# =========================
# MAIN
# =========================

if __name__ == "__main__":
    contro=controller()
   # contro.add()
   #for many peoples
    contro.add_many()