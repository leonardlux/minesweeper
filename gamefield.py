from rich import console
from cell import Cell
from rich import print

import random

#random.seed(18)
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
            self.field[position[0]][position[1]].nachbarn = None
            self.allNachbarn(position,"changeNachbarn",+1)
        else:
            print("Feld schon mit Bombe belegt!" + str(position))


    def __init__(self,dimension=(30,30), bombs=100):
        self.dimension = dimension
        self.bombs = bombs
        self.firstCheck = True
        self.field = [[Cell() for j in range(dimension[1])] for i in range(dimension[0])]

        #Zufällige Bombenpostionen auswählen
        possibilePositions = [item for inner_list in [[[i,j] for j in range(dimension[1])] for i in range(dimension[0])] for item in inner_list]
    
        for i in range(self.bombs):
            bombPosition = random.choice(possibilePositions)
            possibilePositions.remove(bombPosition)
            self.plantBomb(bombPosition)

    
    def makeVisible(self,position,liste=[]):
        #Hier sollten nur 0 positionen übergeben werden
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
    
    def checkForZeroes(self,position):
        #falls 0 an das gecheckte Feld angrenzen, dann wird make Visible aufgerufen
        for i in [position[0]-1, position[0], position[0]+1]:
            for j in [position[1]-1, position[1], position[1]+1]:
                if j>= 0 and i>= 0  and i < self.dimension[0] and j < self.dimension[1] and self.field[i][j].nachbarn == 0 and self.field[i][j].tested == False:
                    self.field[i][j].tested = True
                    self.makeVisible((i,j))
                    return True
        
        return False

        
    def check(self,position):
        #Erster Check
        if position[0]>= self.dimension[0] or position[1]>= self.dimension[1]:
            print("Außerhlab des Spielfelds!")
            return True

        while self.firstCheck == True:
            self.field[position[0]][position[1]].visible = True
            if not self.checkForZeroes(position):
                self.__init__(self.dimension,self.bombs)
            else:
                self.firstCheck = False
                return True
        
        if self.firstCheck == False and self.field[position[0]][position[1]].flagged==False:
            self.field[position[0]][position[1]].visible = True
            self.checkForZeroes(position)
            if self.field[position[0]][position[1]].bomb:
                print(self.convertToStr())
                print("Boooooom! You hit a Bomb! ")
                return False
            return True
        
        
    def flag(self,position):
        if position[0]>= self.dimension[0] or position[1]>= self.dimension[1]:
            print("Außerhlab des Spielfelds!")

        if self.field[position[0]][position[1]].visible == False and self.field[position[0]][position[1]].flagged == False:
            self.field[position[0]][position[1]].flagged = True
            self.allNachbarn(position,"changeFlaggedNachbarn",+1)
        elif self.field[position[0]][position[1]].flagged == True:
            self.field[position[0]][position[1]].flagged = False
            self.allNachbarn(position,"changeFlaggedNachbarn",-1)
        else:
            print("Feld schon offen oder flagged")



    def convertToStr(self,clear=False):
        liste = [[None for j in range(self.dimension[1])] for i in range(self.dimension[0])]
        colors = ["[cyan1]","[cyan2]","[medium_spring_green]","[spring_green1]","[spring_green2]","[green1]","[blue_violet]","[purple3]"]
        bomb = "X"
        flag = "F"
        rows = ""
        row = " X "
        for i in range(self.dimension[0]):
            if i%10==0:
                row += "[red]{:1}[/red] ".format(int(i/10))
            else:
                row += "[purple]{:1} [/]".format(i%10)
        rows = 2*row + "\n"

        for i in range(self.dimension[0]):
            row = "[purple]{:2} [/]".format(i)
            for j in range(self.dimension[1]):
                if clear or self.field[i][j].visible:
                    if not self.field[i][j].bomb:
                        row += colors[self.field[i][j].nachbarn] + str(self.field[i][j].nachbarn) + "[/] "  
                    else:
                        row += "[red]" + bomb + "[/] "
                elif self.field[i][j].flagged == True: 
                    row += "[yellow]" + flag + "[/] "
                else:
                    row +=  "[bright_white]■ [/]"

            row += "[purple]{:2} [/]".format(i)
            for j in range(self.dimension[1]):
                if clear or self.field[i][j].visible:
                    if not self.field[i][j].bomb:
                        row += colors[self.field[i][j].nachbarn - self.field[i][j].flaggedNachbarn] + str(self.field[i][j].nachbarn - self.field[i][j].flaggedNachbarn) + "[/] "  
                    else:
                        row += "[red]" + bomb + "[/] "
                elif self.field[i][j].flagged == True: 
                    row += "[yellow]" + flag + "[/] "
                else:
                    row +=  "[bright_white]■ [/]"
            

            rows += row + "\n"


        return rows