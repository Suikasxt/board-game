from copy import deepcopy
import numpy as np

DIRECTION_4 = np.array([[0, 1], [1, 0], [0, -1], [-1, 0]])
DIRECTION_8 = np.array([[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]])
class BaseRule:
    def __init__(self, height, width) -> None:
        self.height = height
        self.width = width
        self.shape = (self.height, self.width)
        self.state = None
        self.turn = 0
        pass
    
    def reset(self):
        self.state = (np.zeros(self.shape)-1).tolist()
        self.turn = 0

    def vaildCoordinate(self, coord):
        if any(coord < 0) or any(coord >= self.shape):
            return False
        return True

    def step(self, action):
        coord, player_id = np.array(action['coord']), action['player_id']
        if not self.vaildCoordinate(coord):
            return False, "Invaild action"
        return True, "Successfully"
    
    def judgeFinish(self, state):
        pass
        

class GobangRule(BaseRule):
    def step(self, action):
        vaild, message =  super().step(action)
        if not vaild:
            return False, message
        
        coord, player_id = action['coord'], action['player_id']
        if player_id != self.turn:
            return False, "Not the turn of player {}".format(player_id)
        if not self.state[coord[0]][coord[1]] == -1:
            return False, "Invaild action"

        self.state[coord[0]][coord[1]] = player_id
        self.turn ^= 1
        return True, "Successfully"
    
    def judgeFinish(self):
        state = self.state
        assert(np.min(state) >= -1)
        assert(np.max(state) <= 2)
        
        win = [False, False]
        space_count = 0
        
        for dir in DIRECTION_8[:4]:
            count = np.zeros(self.shape, dtype=np.uint8)
            for x in range(self.height):
                for y in range(self.width):
                    if state[x][y] == -1:
                        space_count += 1
                        continue
                    last_pos = np.array([x, y]) - dir
                    if self.vaildCoordinate(last_pos) and state[x][y] == state[last_pos[0]][last_pos[1]]:
                        count[x][y] = count[last_pos[0]][last_pos[1]] + 1
                        if count[x][y] == 5:
                            win[state[x][y]] = True
                    else:
                        count[x][y] = 1
        
        if all(win):
            return True, -1
        for p in [0, 1]:
            if win[p]:
                return True, p
        if space_count == 0:
            return True, -1
        return False, None
                    
        
class RuleFactory:
    def create(gameType, *argv):
        if gameType == 'Gobang':
            return GobangRule(*argv)
        else:
            raise ValueError("Invaild product name.")