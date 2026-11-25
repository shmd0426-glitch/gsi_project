# Partie 3 - Q1 : classe qui ouvre un fichier en ecriture, acces unique
import threading


class FileWriterSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, filename="output.txt"):
        with cls._lock:
            if cls._instance is None:
                inst = super().__new__(cls)
                inst._file = open(filename, "w", encoding="utf-8")
                inst._write_lock = threading.Lock()
                cls._instance = inst
                print("Fichier ouvert :", filename)
            else:
                print("Instance existante reutilisee (fichier deja ouvert)")
        return cls._instance

    def write(self, text):
        with self._write_lock:
            self._file.write(text + "\n")
            self._file.flush()

    def close(self):
        with self._write_lock:
            self._file.close()
        FileWriterSingleton._instance = None
        print("Fichier ferme")


if __name__ == "__main__":
    f1 = FileWriterSingleton("output.txt")
    f2 = FileWriterSingleton("autre.txt")   # ignore : meme instance
    print("f1 is f2 :", f1 is f2)
    f1.write("Ligne 1 ecrite par f1")
    f2.write("Ligne 2 ecrite par f2")
    f1.close()
    print("--- Contenu de output.txt ---")
    print(open("output.txt", encoding="utf-8").read())