from sspo_db.service.artifact.service import EpicService
from sspo_db.service.artifact.service import ProductBacklogService

class ApplicationEpic():
    
    def __init__(self):
        self.service = EpicService()
    
    def create (self, epic):
        self.service.create (epic)
        return epic
        
class ApplicationProductBacklog():

    def __init__ (self):
        self.service = ProductBacklogService()
    
    def retrive_by_project_name(self, project_name):
        return self.service.retrive_by_project_name(project_name)