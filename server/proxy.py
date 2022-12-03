import socket
import json
import sys
import threading
import queue
import time
sys.path.append('..')
import settings

class SingleServerProxy(threading.Thread):
    def __init__(self, player_id, queue) -> None:
        super().__init__()
        self.player_id = player_id
        self.connected = False
        self.queue = queue
        
    def connect(self):
        self.socket_send = socket.socket()
        self.socket_recv = socket.socket()
        host = settings.HOST
        self.socket_send.bind((host, settings.PORT_LIST_SERVER[self.player_id]))
        self.socket_send.listen(5)
        self.socket_recv.bind((host, settings.PORT_LIST_CLIENT[self.player_id]))
        self.socket_recv.listen(5)
        
        self.socket_send.accept()
        self.socket_recv.accept()
        self.connected = True
        print("****Player {} connected.".format(self.player_id))
        
    def send(self, data):
        self.socket_send.send(json.dumps(data).encode('utf-8'))
        
    def recv(self):
        data = ''
        while not data:
            time.sleep(0.1)
            data = self.socket_recv.recv(1024).decode('utf-8')
        data = json.loads(data)
        return data

    def run(self):
        self.connect()
        while True:
            data = self.recv()
            self.queue.put((self.player_id, data))
            
    def close(self):
        self.socket_recv.close()
        self.socket_send.close()

class ServerProxy:
    def __init__(self) -> None:
        self.queue = queue.Queue()
        self.proxy = [SingleServerProxy(0, self.queue), SingleServerProxy(1, self.queue)]

    def connect(self):
        self.proxy[0].start()
        self.proxy[1].start()
        
        while not (self.proxy[0].connected and self.proxy[1].connected):
            time.sleep(0.1)
    
    def send(self, data, player_id = [0,1]):
        if not (type(player_id) == list):
            player_id = [player_id]
        
        for p in player_id:
            self.proxy[p].send(data)
            
        print("****Send data to {}".format(player_id))
        print(data)
            
    def sendGameStart(self):
        while True:
            player_id, action = self.recv()
            if action['type'] == 'start':
                break
            self.sendMessage(player_id, 'Game not start.')
        game_info = action['info']
        print(game_info)
        game_info_message = {
            'type': 'start',
            'info': game_info
        }
        self.send(game_info_message)
        
        return game_info

    def sendGameOver(self, winner):
        over_order = {
            'type': 'over',
            'winner': winner
        }
        self.send(over_order)


    def sendState(self, state, turn):
        data = {
            'type': 'state',
            'state': state,
            'turn': turn
        }
        self.send(data)

    def sendMessage(self, message, player_id=[0, 1]):
        data = {
            'type': 'message',
            'message': message
        }
        self.send(data, player_id)
    
    def recv(self):
        while self.queue.empty():
            time.sleep(0.1)
        return self.queue.get()

    def close(self):
        for p in self.proxy:
            p.close()