# -*- coding: utf-8 -*-

class model:

    def __init__(self):

        self.directory = [
            {"firstname": "Ahmed", "familyname": "Mahdi", "tel": "0778787887"},
            {"firstname": "Mohamed", "familyname": "Mahdi", "tel": "0778787887"},
            {"firstname": "Mounir", "familyname": "Katibi", "tel": "0778787887"},
            {"firstname": "Noui", "familyname": "Brahimi", "tel": "0778787887"}
        ]

    # Search for a person
    def search(self, familyname):

        persons = []

        for person in self.directory:

            if person["familyname"] == familyname:
                persons.append(person)

        return persons

    # Get all persons
    def get_all(self):

        return self.directory

    # Add a new person
    def add(self, familyname, firstname, tel):

        person = {
            "familyname": familyname,
            "firstname": firstname,
            "tel": tel
        }

        self.directory.append(person)