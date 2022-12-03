from proxy import ServerProxy
from rule import RuleFactory

class GameServer:
    def __init__(self) -> None:
        self.proxy = ServerProxy()
        pass
    
    def gameLoop(self):
        gameInfo = self.proxy.sendGameStart()
        rule = RuleFactory.create(gameInfo['gameType'], gameInfo['height'], gameInfo['width'])
        rule.reset()
        self.proxy.sendState(rule.state, rule.turn)
        while True:
            player_id, data = self.proxy.recv()
            if data['type'] == 'step':
                action = {
                    'coord': data['action'],
                    'player_id': player_id
                }
                vaild, message = rule.step(action)
                if vaild:
                    self.proxy.sendState(rule.state, rule.turn)
                else:
                    self.proxy.sendMessage(message, player_id)
                    
            else:
                raise ValueError('Invaild action type {}'.format(data['type']))
            finish, winner = rule.judgeFinish()
            if finish:
                break
            
        self.proxy.sendGameOver(winner)
        result = {
            'winner': winner,
            'exit': False
        }
        return result
        
    
    def mainLoop(self):
        self.proxy.connect()
        while True:
            result = self.gameLoop()
            print('Game over', result)
            if result['exit']:
                break
        self.proxy.close()
    
if __name__ == "__main__":
    game = GameServer()
    game.mainLoop()