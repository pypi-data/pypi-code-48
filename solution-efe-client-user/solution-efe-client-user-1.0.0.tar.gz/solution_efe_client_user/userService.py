import socket
import json
from solution_efe_config import configConstants

CLIENT_USER=configConstants.CLIENTS['user']

def userServiceLogin(data):
    try:
        event = {'event':'user-service-login','data': {'mail': data['mail'] , 'password' : data['password']}}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((CLIENT_USER['host'], CLIENT_USER['port']))
            sock.sendall(bytes(json.dumps(event) + "\n", "utf-8"))
            received = str(sock.recv(1024), "utf-8")
        response=json.loads(received)
        return {'status': response['status'], 'data': response['data']}  
    except Exception as e:
        return {'status': False,'data':str(e)}
