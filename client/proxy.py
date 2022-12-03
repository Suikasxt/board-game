import socket
import json
import sys
import time
sys.path.append('..')
import settings

class ClientProxy:
    def __init__(self, player_id):
        self.socket_recv = socket.socket()
        self.socket_send = socket.socket()
        self.player_id = player_id
        self.host = settings.HOST
        self.port_recv = settings.PORT_LIST_SERVER[player_id]
        self.port_send = settings.PORT_LIST_CLIENT[player_id]
    
    def connect(self):
        self.socket_recv.connect((self.host, self.port_recv))
        self.socket_send.connect((self.host, self.port_send))
    
    def send(self, data):
        self.socket_send.send(json.dumps(data).encode('utf-8'))
        print("****Send data")
        print(data)
        
    
    def sendGameInfo(self, gameInfo):
        data = {
            'type': 'start',
            'info': gameInfo
        }
        self.send(data)
        
    def sendStep(self, action):
        data = {
            'type': 'step',
            'action': action
        }
        self.send(data)
        
    def recv(self):
        while True:
            try:
                data = self.socket_recv.recv(1024)
                data = data.decode('utf-8')
            except socket.timeout:
                continue
            time.sleep(0.2)
            if data:
                break
        data = json.loads(data)
        print("****Receive data")
        print(data)
        return data