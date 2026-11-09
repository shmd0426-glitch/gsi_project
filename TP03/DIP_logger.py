from abc import ABC, abstractmethod

# 1) Abstraction
class ILogger(ABC):
    @abstractmethod
    def log(self, message): ...

# 2) Implémentations concrètes
class FileLogger(ILogger):
    def log(self, message):
        print(f"Logging to file: {message}")

class DatabaseLogger(ILogger):
    def log(self, message):
        print(f"Logging to database: {message}")

# 3) Module de haut niveau : dépend de ILogger (injection de dépendance)
class Application:
    def __init__(self, logger: ILogger):
        self.logger = logger

    def start(self):
        self.logger.log("Application started")

# Code client
if __name__ == '__main__':
    Application(FileLogger()).start()
    Application(DatabaseLogger()).start()
