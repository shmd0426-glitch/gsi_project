from abc import ABC, abstractmethod

class NotificationService(ABC):
    @abstractmethod
    def send(self, message): ...

class EmailService(NotificationService):
    def send(self, message):
        print(f"Envoi d'un email : {message}")

class SMSService(NotificationService):
    def send(self, message):
        print(f"Envoi d'un SMS : {message}")

class PushService(NotificationService):          # nouveau service
    def send(self, message):
        print(f"Envoi d'une notification push : {message}")

class Notification:
    def __init__(self, service: NotificationService):
        self.service = service
    def send(self, message):
        self.service.send(message)
if __name__ == '__main__':
    for service, msg in [(EmailService(), "Bonjour par Email !"),
                         (SMSService(),   "Bonjour par SMS !"),
                         (PushService(),  "Bonjour par Push !")]:
        Notification(service).send(msg)
