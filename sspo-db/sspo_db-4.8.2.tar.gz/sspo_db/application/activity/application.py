from sspo_db.service.activity.service import ScrumIntentedDevelopmentTaskService

class ApplicationScrumIntentedDevelopmentTask():
    
    def __init__(self):
        self.service = ScrumIntentedDevelopmentTaskService()
    
    def create(self, scrum_intented_development_task):
        self.service.create(scrum_intented_development_task)
    