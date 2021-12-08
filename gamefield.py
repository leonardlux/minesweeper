
from rich import console
from cell import Cell
from rich import print

import random

#random.seed(18)
class Gamefield():
    
    def allNachbarn(self,position,func,*args):
        for i in [position[0]-1, position[0], position[0]+1]:
            for j in [position[1]-1, position[1], position[1]+1]:
                if (j>= 0 and i >= 0) and (i < self.dimension[0] and j < self.dimension[1]):
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


    def __init__(self,dimension=(30,28), bombs=100):
        self.dimension = dimension
        self.bombs = bombs
        self.firstCheck = True
        self.field = [[Cell((i,j)) for j in range(dimension[1])] for i in range(dimension[0])]

        #Zufällige Bombenpostionen auswählen
        possibilePositions = [item for inner_list in [[[i,j] for j in range(dimension[1])] for i in range(dimension[0])] for item in inner_list]
    
        for i in range(self.bombs):
            bombPosition = random.choice(possibilePositions)
            possibilePositions.remove(bombPosition)
            self.plantBomb(bombPosition)

        #Für solving:
        self.border = []
        self.usedBorderCells = []

    def makeVisible(self,position):
        if self.field[position[0]][position[1]].visible == False:
            self.field[position[0]][position[1]].visible = True
            self.allNachbarn(position,"changeVisibleNachbarn",+1)
            return True
        else:
            print("Warnung: Zelle schon sichbar!")
            print(position)
            return False


    def zeroCell(self,position,liste=[]):
        #Hier sollten nur 0 positionen übergeben werden
        for i in [position[0]-1, position[0], position[0]+1]:
            for j in [position[1]-1, position[1], position[1]+1]:
                if j>= 0 and i>= 0  and i < self.dimension[0] and j < self.dimension[1]:
                    if (i== position[0] and j==position[1]) and self.field[i][j].visible==False:
                        self.makeVisible((i,j))
                        self.field[i][j].tested = True
                    elif self.field[i][j].nachbarn == 0 and self.field[i][j].tested == False:
                        self.field[i][j].tested = True
                        liste.append((i,j))
                    elif self.field[i][j].tested == False and self.field[i][j].visible == False:
                        self.makeVisible((i,j))
                        self.border.append((i,j))
        
        if len(liste) > 0:
            self.zeroCell(liste[0],liste[1:]) 
    
    def checkForZeroes(self,position):
        #falls 0 an das gecheckte Feld angrenzen, dann wird make Visible aufgerufen
        for i in [position[0]-1, position[0], position[0]+1]:
            for j in [position[1]-1, position[1], position[1]+1]:
                if j>= 0 and i>= 0  and i < self.dimension[0] and j < self.dimension[1] and self.field[i][j].nachbarn == 0 and self.field[i][j].tested == False:
                    self.field[i][j].tested = True
                    self.zeroCell((i,j))
                    return True
        
        return False

        
    def check(self,position):
        if position[0]>= self.dimension[0] or position[1]>= self.dimension[1]:
            print("Außerhlab des Spielfelds!")
            return True
        
        if self.field[position[0]][position[1]].visible == True:
            print("already visible!")
            return

        #erster Check
        while self.firstCheck == True:
            self.makeVisible(position)
            if self.field[position[0]][position[1]].nachbarn != 0:
                self.border.append(position) 
            if not self.checkForZeroes(position):
                self.__init__(self.dimension,self.bombs)
            else:
                self.firstCheck = False
                return True
        
        if self.firstCheck == False and self.field[position[0]][position[1]].flaged==False:
            self.makeVisible(position)
            self.border.append(position)
            self.checkForZeroes(position)
            if self.field[position[0]][position[1]].bomb:
                print(self.convertToStr())
                print("Boooooom! You hit a Bomb! ")
                return False
            return True
        
        
    def flag(self,position):
        if position[0]>= self.dimension[0] or position[1]>= self.dimension[1]:
            print("Außerhlab des Spielfelds!")

        if self.field[position[0]][position[1]].visible == False and self.field[position[0]][position[1]].flaged == False:
            self.field[position[0]][position[1]].flaged = True
            self.allNachbarn(position,"changeFlagedNachbarn",+1)
        else:
            print("Feld schon offen oder flaged")
    

    def unflaged(self,position):
        if position[0]>= self.dimension[0] or position[1]>= self.dimension[1]:
            print("Außerhlab des Spielfelds!")

        if self.field[position[0]][position[1]].flaged == True:
            self.field[position[0]][position[1]].flaged = False
            self.allNachbarn(position,"changeFlagedNachbarn",-1)
        else:
            print("Feld schon offen oder nicht flaged")


    def updateBorder(self):
        self.usedBorderCells = []
        #entfernen wenn alle nachbarfelder bekannt sind
        for x in self.border:

            #Cellen am Rand haben weniger Nachbarn
            randOrdnung = 0
            maxNachbarn = [8,5,3]
            if x[0]==0 or x[0]==(self.dimension[0]-1):
                randOrdnung +=1
            if x[1]==0 or x[1]==(self.dimension[1]-1):
                randOrdnung +=1

            if self.field[x[0]][x[1]].visibleNachbarn + self.field[x[0]][x[1]].flagedNachbarn == maxNachbarn[randOrdnung]:
                self.usedBorderCells.append(x)
        if len(x)!=0:
            for x in self.usedBorderCells:
                self.border.remove(x)


    def solve(self):
        for i in range(len(self.border)):
            cell = self.field[self.border[i][0]][self.border[i][1]]
            position = self.border[i]
            
            #Cellen am Rand haben weniger Nachbarn
            randOrdnung = 0
            maxNachbarn = [8,5,3]
            if position[0]==0 or position[0]==(self.dimension[0]-1):
                randOrdnung +=1
            if position[1]==0 or position[1]==(self.dimension[1]-1):
                randOrdnung +=1

            #Beginn des Solven
            if (cell.nachbarn - cell.flagedNachbarn) == 0:
                #alle anliegenden Felder, die nicht geflaged sind, sind ohne Bomben
                for i in [position[0]-1, position[0], position[0]+1]:
                    for j in [position[1]-1, position[1], position[1]+1]:
                        if j>= 0 and i>= 0  and i < self.dimension[0] and j < self.dimension[1] and self.field[i][j].visible==False:
                            self.check((i,j))

            elif (maxNachbarn[randOrdnung]-cell.visibleNachbarn - cell.nachbarn) == 0:
                #alle anliegenden Felder sind Bomben
                for i in [position[0]-1, position[0], position[0]+1]:
                    for j in [position[1]-1, position[1], position[1]+1]:
                        if j>= 0 and i>= 0  and i < self.dimension[0] and j < self.dimension[1] and self.field[i][j].visible==False and self.field[i][j].flaged==False:
                            self.flag((i,j))
        self.updateBorder()


    def convertToStr(self,clear=False):
        liste = [[None for j in range(self.dimension[1])] for i in range(self.dimension[0])]
        colors = ["[cyan1]","[cyan2]","[medium_spring_green]","[spring_green1]","[spring_green2]","[green1]","[blue_violet]","[purple3]","[white]","[white]"]
        bomb = "X"
        flag = "F"
        color_side = "[green_yellow]"

        rows = ""
        row = " X "
        for i in range(self.dimension[1]):
            if i%10==0:
                row += "[red]{:1}[/red] ".format(int(i/10))
            else:
                row += color_side + "{:1} [/]".format(i%10)
        rows = 3*row + "\n"

        for i in range(self.dimension[0]):
            row = ""
            #Normaler Spielmodus
            row += color_side + "{:2} [/]".format(i)
            for j in range(self.dimension[1]):
                if clear or self.field[i][j].visible: 
                    if not self.field[i][j].bomb:
                        row += colors[self.field[i][j].nachbarn] + str(self.field[i][j].nachbarn) + "[/] "  
                    else:
                        row += "[red]" + bomb + "[/] "
                elif self.field[i][j].flaged == True: 
                    row += "[yellow]" + flag + "[/] "
                else:
                    row +=  "[bright_white]■ [/]"

            #flaged Nachbarn
            row += color_side + "{:2} [/]".format(i)
            for j in range(self.dimension[1]):
                if clear or self.field[i][j].visible:
                    if (i,j) in self.border:
                        row +=  "[purple]" + str(self.field[i][j].flagedNachbarn) + "[/] " 
                    elif (i,j) in self.usedBorderCells:
                        row +=  "[red]" + str(self.field[i][j].flagedNachbarn) + "[/] " 
                    elif not self.field[i][j].bomb:
                        row += str(self.field[i][j].flagedNachbarn) + " " 
                    else:
                        row += "[red]" + bomb + "[/] "
                elif self.field[i][j].flaged == True: 
                    row += "[yellow]" + flag + "[/] "
                else:
                    row +=  "[bright_white]■ [/]"
            
            #visible Nachbarn
            row += color_side + "{:2} [/]".format(i)
            for j in range(self.dimension[1]):
                if clear or self.field[i][j].visible:
                    if (i,j) in self.border:
                        row +=  "[purple]" + str(self.field[i][j].visibleNachbarn) + "[/] " 
                    elif (i,j) in self.usedBorderCells:
                        row +=  "[red]" + str(self.field[i][j].visibleNachbarn) + "[/] " 
                    elif not self.field[i][j].bomb:
                        row += str(self.field[i][j].visibleNachbarn)  + " " 
                    else:
                        row += "[red]" + bomb + "[/] "
                elif self.field[i][j].flaged == True: 
                    row += "[yellow]" + flag + "[/] "
                else:
                    row +=  "[bright_white]■ [/]"

            rows += row + "\n"


        return rows