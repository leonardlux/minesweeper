from rich import console
from cell import Cell

import random


class Gamefield():
    
    def allNachbarn(self,position,func,*args):
        for i in [position[0]-1, position[0], position[0]+1]:
            for j in [position[1]-1, position[1], position[1]+1]:
                if ((j and i) >= 0) and (i < self.dimension[0] and j < self.dimension[1]):
                    if (i== position[0] and j==position[1]):
                        pass
                    else:
                        getattr(self.field[i][j],func)(*args)

    
    def plantBomb(self,position):
        if not self.field[position[0]][position[1]].bomb:
            self.field[position[0]][position[1]].bomb = True
            self.allNachbarn(position,"changeNachbarn",+1)
        else:
            print("Feld schon mit Bombe belegt!" + str(position))


    def __init__(self,dimension=(50,50), bombs=400):
        self.dimension = dimension
        self.bombs = bombs
        self.field = [[Cell() for j in range(dimension[1])] for i in range(dimension[0])]

        #Zufällige Bombenpostionen auswählen
        possibilePositions = [item for inner_list in [[[i,j] for j in range(dimension[1])] for i in range(dimension[0])] for item in inner_list]
    
        for i in range(self.bombs):
            bombPosition = random.choice(possibilePositions)
            possibilePositions.remove(bombPosition)
            self.plantBomb(bombPosition)

    
    def makeVisible(self,position,liste=[]):
        for i in [position[0]-1, position[0], position[0]+1]:
            for j in [position[1]-1, position[1], position[1]+1]:
                if j>= 0 and i>= 0  and i < self.dimension[0] and j < self.dimension[1]:
                    if (i== position[0] and j==position[1]):
                        self.field[i][j].visible = True
                        self.field[i][j].tested = True
                    elif self.field[i][j].nachbarn == 0 and self.field[i][j].tested == False:
                        self.field[i][j].tested = True
                        liste.append((i,j))
                    else:
                        self.field[i][j].visible = True
        
        if len(liste) > 0:
            self.makeVisible(liste[0],liste[1:]) 

        
    def check(self,position):
        self.makeVisible(position)


    def convertToStr(self,clear=False):
        liste = [[None for j in range(self.dimension[1])] for i in range(self.dimension[0])]
        colors = ["[cyan1]","[cyan2]","[medium_spring_green]","[spring_green1]","[spring_green2]","[green1]","[blue_violet]","[purple3]","[red]",]
        bomb = "X"

        rows = ""

        for i in range(self.dimension[0]):
            row = ""
            for j in range(self.dimension[1]):
                if clear or self.field[i][j].visible:
                    if not self.field[i][j].bomb:
                        row += colors[self.field[i][j].nachbarn] + str(self.field[i][j].nachbarn) + "[/] "  
                    else:
                        row += colors[8] + bomb + "[/] "
                else:
                    row +=  "[bright_white]■ [/]"
            rows += row + "\n"


        return rows