import numpy as np
from config import *
from props import Bullet, IceBall
from base import Base
import time
from utils import *

class Character(Base):
    def __init__(self):

        self._lives = 0
        self.health = 0
        self.velocity_y = -1 * GRAVITY
        
        self.weapons = []
        self.right = []
        self.left = []
        self.down = []
        self.up = []

    @property
    def lives(self):
        return self._lives
    
    @lives.setter
    def lives(self, var):
        self._lives = var
    
    def check_proximity(self, board, frame):
        if self.location[1] + self.size[1] >= frame + HEIGHT*2 + 1:
            self.right = [100] * self.size[0]
        else:
            self.right = board[
                self.location[0] - self.size[0] + 1 : self.location[0] + 1,
                self.location[1] + self.size[1],
            ]

        if self.location[1] - 1 < frame:
            self.left = [100] * self.size[0]
        else:
            self.left = board[
                self.location[0] - self.size[0] + 1 : self.location[0] + 1,
                self.location[1] - 1,
            ]

        if self.location[0] - self.size[0] < 0:
            self.up = [100] * self.size[1]
        else:
            self.up = board[
                self.location[0] - self.size[0],
                self.location[1] : self.location[1] + self.size[1],
            ]

        if self.location[0] + 1 >= HEIGHT:
            self.down = [100] * self.size[1]
        else:
            self.down = board[
                self.location[0] + 1, self.location[1] : self.location[1] + self.size[1]
            ]

        # print(f"right: {self.right}")
        # print(f"left: {self.left}")
        # print(f"down: {self.down}")
        # print(f"up: {self.up}")


class Mando(Character):
    def __init__(self, board):

        Character.__init__(self)
        self.id = 5
        self.lives = M_LIVES
        self.health = M_HEALTH
        self.size = M_SIZE
        self.location = M_INIT_LOCATION
        self.place(board, self.id)
        self.shield = False
        self.stime = time.time() - 70
        self.fast = False
        self.ftime = time.time() - 5

    def pick_coin(self, board, proximity):
        return np.count_nonzero(proximity == 1)

    def powerup(self, proximity):
        if 2 in proximity:
            self.ftime = time.time()
            self.fast = True
    
    def frate(self):
        if self.fast:
            return 2
        return 1
    
    def move(
        self, board, key, frame
    ):
        self.check_proximity(board, frame)
        score_delta = 0
        if key == "d":
            self.powerup(self.right)            
            # Check if there is space on the right
            if max(self.right) <= 2 or self.shield:
                score_delta += self.pick_coin(board, self.right)
                self.place(board, 0)
                self.location[1] += 1
                self.place(board, self.id)
            elif max(self.right) in [7, 8, 9, 10, 15] and self.shield == False:
                self.lives -= 1

        if key == "a":
            self.powerup(self.left)            
            # Check if there is space on the left
            if max(self.left) <= 2 or self.shield:
                score_delta += self.pick_coin(board, self.left)
                self.place(board, 0)
                self.location[1] -= 1
                self.place(board, self.id)
            elif max(self.left) in [7, 8, 9, 10, 15]:
                self.lives -= 1

        if key == "w":
            self.velocity_y += JUMP_VEL

        if self.velocity_y > 0:
            self.powerup(self.up)            
            # Check if there is space on the top
            if max(self.up) <= 2 or self.shield:
                score_delta += self.pick_coin(board, self.up)
                self.place(board, 0)
                self.location[0] -= 1
                self.place(board, self.id)
            elif max(self.up) in [7, 8, 9, 10, 15]:
                self.lives -= 1

        elif self.velocity_y < 0:
            self.powerup(self.down)            
            # Check if there is space in the bottom
            if (max(self.down) <= 2 or self.shield) and max(self.down) != 6:
                score_delta += self.pick_coin(board, self.down)
                self.place(board, 0)
                self.location[0] += 1
                self.place(board, self.id)
            elif max(self.down) in [7, 8, 9, 10, 15]:
                self.lives -= 1

        self.velocity_y = -1
        

        if key == "e":
            bullet = Bullet(board, [self.location[0] - self.size[0] +1,self.location[1] + self.size[1]])
            self.weapons.append(bullet)
            print(self.weapons)
        
        return score_delta

    def checkmag(self, board, frame):
        if 3 in board[maxh(self.location[0] - 20): maxh(self.location[0] + 20), maxw(self.location[1] - 40): maxw(self.location[1] + 40)]:
            mag_loc = np.where(board == 3)
            if int(mag_loc[0]) > self.location[0]:
                self.move(board, "", frame)
            elif int(mag_loc[0]) < self.location[0]:
                self.move(board, "w", frame)
            if int(mag_loc[1]) > self.location[1]:
                self.move(board, "d", frame)
            elif int(mag_loc[1]) < self.location[1]:
                self.move(board, "a", frame)

    def move_relative(self, board, frame):
        score_delta = 0
        self.check_proximity(board, frame)
        self.powerup(self.right)            
        if max(self.right) <= 2 or self.shield:
            score_delta += self.pick_coin(board, self.right)
            self.place(board, 0)
            self.location[1] += 1
            self.place(board, self.id)
        elif max(self.right) in [7, 8, 9, 10, 15] and self.shield == False:
            self.lives -= 1
        return score_delta

    def upd_att(self, board, key, frame):
        for weapon in self.weapons:
            weapon.advance(board)
            if frame < WIDTH - ENEMY_OFFSET:
                weapon.advance(board)
        
        if key == "z":
            if time.time() - self.stime >= 70:
                self.stime = time.time()
                self.shield = True
                self.id = 11
                self.place(board, self.id)

        if self.fast and time.time() - self.ftime >= 5:
            self.fast = False
        if self.shield and time.time() - self.stime >= 10:
            self.shield = False
            self.id = 5

class Enemy(Character):
    def __init__(self, board):
        super().__init__()
        self.id = 14
        self.lives = E_LIVES
        self.health = E_HEALTH
        self.size = E_SIZE
        self.location = E_INIT_LOCATION
        self.place(board, self.id)
    
    def move(self, board, location):
        self.place(board, 0)
        self.location[0] = location[0]
        self.place(board, self.id)
    
    def shoot(self, board):
        ice = IceBall(board, [self.location[0] - self.size[0] +1,self.location[1] - 1])
        self.weapons.append(ice)
    
    def move_ice(self, board):
        for ice in self.weapons:
            ice.advance(board)
        self.left = board[
                self.location[0] - self.size[0] + 1 : self.location[0] + 1,
                self.location[1] - 1,
        ]
        if 4 in self.left:
            self.lives -= 1


    
