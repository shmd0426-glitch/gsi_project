from model_file import model_file
# -*- coding: utf-8 -*-

# A directory in format of list [] of dictionaries {}




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
     self.data_model = model_file()
     self.myview = view()
 

   def controller(self):
      persons = self.data_model.get_all()
      self.myview.output(persons)
      name = self.myview.input()
      persons = self.data_model.search(name)
      self.myview.output(persons)
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
       self.data_model.save()  
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