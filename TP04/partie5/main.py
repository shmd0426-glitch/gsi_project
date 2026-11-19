# -*- coding: utf-8 -*-

from tkinter import Tk, Label, Entry, Button, Text, END
from model_file import model


# =========================
# VIEW
# =========================

class view_tk:

    def __init__(self, master, model):

        self.master = master
        self.model = model

        master.title("Directory")

        # Output label
        self.output_label = Label(master, text="Output")
        self.output_label.grid(row=0, column=0)

        # Input
        self.label = Label(master, text="Input:")
        self.label.grid(row=1, column=0)

        # Family name
        self.label = Label(master, text="Family Name:")
        self.label.grid(row=2, column=0)

        self.entry = Entry(master, width=50)
        self.entry.grid(row=2, column=1)

        # First name
        self.label_firstname = Label(master, text="First Name:")
        self.label_firstname.grid(row=3, column=0)

        self.entry_firstname = Entry(master, width=50)
        self.entry_firstname.grid(row=3, column=1)

        # Telephone
        self.label_tel = Label(master, text="Tel:")
        self.label_tel.grid(row=4, column=0)

        self.entry_tel = Entry(master, width=50)
        self.entry_tel.grid(row=4, column=1)

        # Output area
        self.output = Text(master, height=10, width=50)

        # Buttons
        self.search_button = Button(
            master,
            text="Search",
            command=lambda: self.update("search")
        )

        self.add_button = Button(
            master,
            text="Add",
            command=lambda: self.update("add")
        )

        self.all_button = Button(
            master,
            text="Get All",
            command=lambda: self.update("get_all")
        )

        # Layout
        self.search_button.grid(row=5, column=0)
        self.add_button.grid(row=5, column=1)
        self.all_button.grid(row=5, column=2)

        self.output_label.grid(row=0, column=0)
        self.output.grid(row=6, column=0, columnspan=3)

    # =========================
    # UPDATE
    # =========================

    def update(self, method):

        familyname = self.entry.get().strip()
        firstname = self.entry_firstname.get().strip()
        tel = self.entry_tel.get().strip()

        if method == "search":

            result = self.search(familyname)

        elif method == "add":

            result = self.add(familyname, firstname, tel)

        elif method == "get_all":

            result = self.get_all()

        else:

            result = "Unknown method"

        self.output.delete("1.0", END)
        self.output.insert(END, str(result))

    # =========================
    # ADD
    # =========================

    def add(self, familyname, firstname, tel):

        self.model.add(familyname, firstname, tel)

        return "Person added successfully!"

    # =========================
    # SEARCH
    # =========================

    def search(self, familyname):

        result = self.model.search(familyname)

        if result:

            return result

        else:

            return "Person not found"

    # =========================
    # GET ALL
    # =========================

    def get_all(self):

        return self.model.get_all()

    # =========================
    # RUN
    # =========================

    def run(self):

        self.master.mainloop()


# =========================
# CONTROLLER
# =========================

def controller3():

    data_model = model()

    master = Tk()

    my_viewer = view_tk(master, data_model)

    my_viewer.run()


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    controller3()
