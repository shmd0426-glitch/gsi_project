
# A directory in format of list [] of dictionaries {}

directory = [
    {"firstname": "Ahmed", "familyname": "Mahdi", "tel": "0778787887"},
    {"firstname": "Mohamed", "familyname": "Mahdi", "tel": "0778787887"},
    {"firstname": "Mounir", "familyname": "Katibi", "tel": "0778787887"},
    {"firstname": "Noui", "familyname": "Brahimi", "tel": "0778787887"},
]


def main():
    print("Finding a telephone")
    print("Give a name")

    familyname = input()

    # Number of found elements
    nb_found = 0

    # Browse names
    for person in directory:

        # Show all people with the given name
        if person['familyname'] == familyname:
            print(person['firstname'], person['familyname'], person['tel'])
            nb_found += 1

    if not nb_found:
        print("This familyname %s doesn't exist" % familyname)


if __name__ == '__main__':
    main()
