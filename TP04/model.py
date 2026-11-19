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