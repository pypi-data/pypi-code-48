from abc import ABC

class AbstractApplication(ABC):

    def __init__(self, service):
        self.service = service
    
    def create(self, object):
        self.service.create (object)
