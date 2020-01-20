import requests
import json
from IPython.core.display import display, HTML

class Api(object):
    def create_log(self, run=1, row=None):
        if run == None:
            return
        if row == None:
            return
        
        url = 'http://localhost:3000/logs'
        headers = {
            "Authorization": "Token token=7IrIz5lmeKNUK7ZDNGrGWwtt",
            "Content-Type": "application/json; charset=utf-8"
        }
        data = {'run_id': run['id'], 'data': json.dumps(row)}
        r = requests.post(url, headers=headers, json=data)
        display(HTML('''Log: {}'''.format(r.json())))

    def create_run(self, project=None):
        if project == None:
            return

        url = 'http://localhost:3000/projects'
        headers = {
            "Authorization": "Token token=7IrIz5lmeKNUK7ZDNGrGWwtt",
            "Content-Type": "application/json; charset=utf-8"
        }
        r = requests.get(url, headers=headers)

        response = r.json()
        display(HTML('''Projects: {}'''.format(response)))
        for i in response:
            if i['name'] == project:
                url = 'http://localhost:3000/runs'
                data = {'project_id':i['id'], 'name': 'test-run-125', 'user_id': 1}
                r = requests.post(url, headers=headers, json=data)
                display(HTML('''Run: {}'''.format(r.json())))
                return r.json()