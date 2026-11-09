class Printable:
    def print_document(self, document): pass

class Scannable:
    def scan_document(self, document): pass

class Faxable:
    def fax_document(self, document): pass

class BasicPrinter(Printable):
    def print_document(self, document):
        print(f"Impression : {document}")

class AdvancedPrinter(Printable, Scannable, Faxable):
    def print_document(self, document):
        print(f"Impression : {document}")
    def scan_document(self, document):
        print(f"Numérisation : {document}")
    def fax_document(self, document):
        print(f"Envoi de fax : {document}")

if __name__ == '__main__':
    basic = BasicPrinter()
    basic.print_document("Document2.pdf")

    advanced = AdvancedPrinter()
    advanced.print_document("Document2.pdf")
    advanced.scan_document("Document2.pdf")
    advanced.fax_document("Document2.pdf")
