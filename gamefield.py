
from os import error
from rich import console
from rich import print

from connection import Connection
from cell import Cell

import random

#random.seed(18)
class Gamefield():

    def plantBomb(self,position):
        if not self.field[position[0]][position[1]].bomb:
            self.field[position[0]][position[1]].bomb = True
            self.field[position[0]][position[1]].value = None
        else:
            print("Feld schon mit Bombe belegt!" + str(position))


    def __init__(self,dimension=(39,25), bombs=100):
        self.dimension = dimension
        self.bombs = bombs
        self.flags = 0 
        self.firstCheck = True

        self.field = [[Cell((i,j)) for j in range(dimension[1])] for i in range(dimension[0])]
        
        #Zufällige Bombenpostionen auswählen und Bomben positionieren
        possibilePositions = [item for inner_list in [[[i,j] for j in range(dimension[1])] for i in range(dimension[0])] for item in inner_list]
    
        for i in range(self.bombs):
            bombPosition = random.choice(possibilePositions)
            possibilePositions.remove(bombPosition)
            self.plantBomb(bombPosition)

        #Nachbarn zuordnen 
        for i in range(self.dimension[0]):
            for j in range(self.dimension[1]):
                nachbarn = []
                for k in [i-1, i, i+1]:
                    for l in [j-1, j, j+1]:
                        if (k>= 0 and l >= 0) and (k < self.dimension[0] and l < self.dimension[1]) and  (k!=i or l!=j):    
                            nachbarn.append(self.field[k][l])
                
                self.field[i][j].setNachbarn(nachbarn)

        #Für solving:
        self.border = []
        self.usedBorderCells = []
        self.connections = []


    def makeVisible(self,position):
        if self.field[position[0]][position[1]].visible == False:
            self.field[position[0]][position[1]].visible = True
            
            for i in range(len(self.connections)):
                if self.connections[i].checkConnection(position):
                    self.connections.remove(self.connections[i])
                    break

            return True
        else:
            print("Warnung: Zelle schon sichbar!")
            print(position)
            return False


    def zeroCell(self,position,liste=[]):
        #Hier sollten nur 0 positionen übergeben werden
        liste = [position]
        while len(liste)!=0:
            position = liste[0]
            liste = liste[1:]
            for i in [position[0]-1, position[0], position[0]+1]:
                for j in [position[1]-1, position[1], position[1]+1]:
                    if j>= 0 and i>= 0  and i < self.dimension[0] and j < self.dimension[1]:
                        if (i== position[0] and j==position[1]) and self.field[i][j].visible==False:
                            self.makeVisible((i,j))
                            self.field[i][j].tested = True
                        elif self.field[i][j].value == 0 and self.field[i][j].tested == False:
                            self.field[i][j].tested = True
                            liste.append((i,j))
                        elif self.field[i][j].tested == False and self.field[i][j].visible == False:
                            self.makeVisible((i,j))
                            self.border.append((i,j))
    
    
    def checkForZeroes(self,position):
        #falls 0 an das gecheckte Feld angrenzen, dann wird make Visible aufgerufen
        for i in [position[0]-1, position[0], position[0]+1]:
            for j in [position[1]-1, position[1], position[1]+1]:
                if j>= 0 and i>= 0  and i < self.dimension[0] and j < self.dimension[1] and self.field[i][j].value == 0 and self.field[i][j].tested == False:
                    self.field[i][j].tested = True
                    self.zeroCell((i,j))
                    return True
        return False

        
    def check(self,position):
        if position[0]>= self.dimension[0] or position[1]>= self.dimension[1]:
            print("Außerhlab des Spielfelds!")
            return True
        
        if self.field[position[0]][position[1]].visible == True:
            print("Schon sichtbar!")
            return True

        #erster Check
        while self.firstCheck == True:
            self.makeVisible(position)
            if self.field[position[0]][position[1]].value != 0:
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
                print(self.convertToStr(1))
                print("Boooooom! You hit a Bomb! ")
                raise ValueError
                return False
            return True
        
        
    def flag(self,position):
        if position[0]>= self.dimension[0] or position[1]>= self.dimension[1]:
            print("Außerhlab des Spielfelds!")

        if self.field[position[0]][position[1]].visible == False and self.field[position[0]][position[1]].flaged == False:
            self.field[position[0]][position[1]].flaged = True
            self.flags += 1

            for i in range(len(self.connections)):
                if self.connections[i].checkConnection(position):
                    self.connections.remove(self.connections[i])
                    break           
            
        else:
            print("Feld schon offen oder flaged")
        

    def unflag(self,position):
        if position[0]>= self.dimension[0] or position[1]>= self.dimension[1]:
            print("Außerhlab des Spielfelds!")

        if self.field[position[0]][position[1]].flaged == True:
            self.field[position[0]][position[1]].flaged = False
        else:
            print("Feld schon offen oder nicht flaged")


    def updateBorder(self):
        self.usedBorderCells = []
        #entfernen wenn alle nachbarfelder bekannt sind
        for x in self.border:
            if self.field[x[0]][x[1]].visibleNachbarn() + self.field[x[0]][x[1]].flagedNachbarn() == len(self.field[x[0]][x[1]].nachbarn):
                self.usedBorderCells.append(x)
    
        for x in self.usedBorderCells:
            self.border.remove(x)


    def basicSolve(self,cell,allowedCheck=True,allowedFlag=True):
        if (cell.value - cell.flagedNachbarn()) == 0 and allowedCheck:
            #alle verdeckten anliegenden Felder, die nicht geflaged sind, sind ohne Bomben
            for nachbar in cell.nachbarn:
                if nachbar.visible==False and nachbar.flaged == False:
                    self.check(nachbar.position)
        elif (len(cell.nachbarn) - cell.visibleNachbarn() - cell.value) == 0 and allowedFlag:
            #alle anliegenden Felder sind Bomben
            for nachbar in cell.nachbarn:
                if nachbar.visible==False and nachbar.flaged==False:
                        self.flag(nachbar.position)


    def solve(self):
        if len(self.border) == 0 and not self.firstCheck:
            self.updateBorder()
            print("Solved!")
            return False
        
        self.connections = []
        
        for i in range(len(self.border)):
            cell = self.field[self.border[i][0]][self.border[i][1]]
            #Connected felder herausfinden 
            if (len(cell.nachbarn) - cell.visibleNachbarn() - cell.flagedNachbarn()) in (2,3,4,5,6,7) and (cell.value - cell.flagedNachbarn()) in  (1,2):
                connection = []
                for x in cell.nachbarn:
                    if x.visible==False and x.flaged==False:
                        connection.append(x)
                
                save = True
                for x in self.connections:
                    if x.isIdentical(connection):
                        save = False
                        break
                if save:
                    self.connections.append(Connection(connection,(cell.value - cell.flagedNachbarn())))


        for i in range(len(self.border)):
            cell = self.field[self.border[i][0]][self.border[i][1]]
            complete, partly = cell.checkConnections(self.connections)
            
            #print("complete: {0}, partly: {1}".format(len(complete), len(partly)))

            #Simple Methoden ohne Connecitons
            self.basicSolve(cell)

            #Methoden mit Conection (wir erstellen temporäre Zellen)
            for connection in complete:
                t_nachbarn = cell.nachbarn[:]
                for connectionCell in connection.cells:
                    if connectionCell in t_nachbarn:
                        t_nachbarn.remove(connectionCell)

                t_cell = Cell()
                t_cell.setNachbarn(t_nachbarn)
                t_cell.setValue(cell.value-connection.value)
                self.basicSolve(t_cell)
                del t_cell
                    
            for connection in partly:
                t_nachbarn = cell.nachbarn[:]
                for connectionCell in connection.cells:
                    if connectionCell in t_nachbarn:
                        t_nachbarn.remove(connectionCell)

                t_cell = Cell()
                t_cell.setNachbarn(t_nachbarn)
                t_cell.setValue(cell.value-connection.value)
                self.basicSolve(t_cell,allowedCheck=False)
                del t_cell

           
        self.updateBorder()
        return True


    def convertToStr(self,plots):
        colors = ["[cyan1]","[cyan2]","[medium_spring_green]","[spring_green1]","[spring_green2]","[green1]","[blue_violet]","[purple3]","[white]","[white]"]
        bomb = "X"
        flag = "F"
        color_side = "[green_yellow]"

        rows = ""
        rows += "Bombs: {0:2}| Flags: {1:2}| Bombsleft {2:2} ".format(self.bombs,self.flags,self.bombs-self.flags)
        if plots >=2:
            rows += 3*"\t"+"Bordercells: {0:2}| Connections: {1:2}".format(len(self.border),len(self.connections))
        rows += "\n"

        #header 
        row = "  "
        plot_names = ["Normal","0 => Check","0 => Flag","Connections"]
        for i in range(plots):
            row += "{names:^{y}}   ".format(names=plot_names[i],y=self.dimension[1]*2)
        
        rows += row +"\n"

        #zahlen Kopfzeile
        row = " X "
        for i in range(self.dimension[1]):
            if i%10==0:
                row += "[red]{:1}[/red] ".format(int(i/10))
            else:
                row += color_side + "{:1} [/]".format(i%10)
        rows += plots*row + "\n"

        for i in range(self.dimension[0]):
            row = ""
            #Normaler Spielmodus
            row += color_side + "{:2} [/]".format(i)
            for j in range(self.dimension[1]):
                if self.field[i][j].visible: 
                    if  self.field[i][j].bomb:
                        row += "[red]" + bomb + "[/] "
                    elif (i,j) in self.border:
                        row +=  "[purple]" + str(self.field[i][j].value) + "[/] " 
                    elif (i,j) in self.usedBorderCells:
                        row +=  "[red]" + str(self.field[i][j].value) + "[/] " 
                    else:
                        row += colors[self.field[i][j].value] + str(self.field[i][j].value) + "[/] "  
                elif self.field[i][j].flaged == True: 
                    row += "[yellow]" + flag + "[/] "
                else:
                    row +=  "[bright_white]■ [/]"
            if plots >=2:
                #Automatismus 1
                row += color_side + "{:2} [/]".format(i)
                for j in range(self.dimension[1]):
                    if self.field[i][j].visible and not self.field[i][j].bomb:
                        if (i,j) in self.border :
                            row +=  "[purple]" + str(self.field[i][j].value - self.field[i][j].flagedNachbarn()) + "[/] " 
                        elif (i,j) in self.usedBorderCells:
                            row +=  "[red]" + str(self.field[i][j].value - self.field[i][j].flagedNachbarn()) + "[/] " 
                        elif not self.field[i][j].bomb:
                            row += str(self.field[i][j].value - self.field[i][j].flagedNachbarn()) + " " 
                    elif self.field[i][j].visible and self.field[i][j].bomb:
                            row += "[red]" + bomb + "[/] "
                    elif self.field[i][j].flaged == True: 
                        row += "[yellow]" + flag + "[/] "
                    else:
                        row +=  "[bright_white]■ [/]"
            if plots >=3:
                #Automatismus 2
                row += color_side + "{:2} [/]".format(i)
                for j in range(self.dimension[1]):
                    if self.field[i][j].visible and not self.field[i][j].bomb:
                        relValue = len(self.field[i][j].nachbarn) - self.field[i][j].visibleNachbarn() - self.field[i][j].value
                        if (i,j) in self.border:
                            row +=  "[purple]" + str(relValue) + "[/] " 
                        elif (i,j) in self.usedBorderCells:
                            row +=  "[red]" + str(relValue) + "[/] " 
                        else:
                            row += str(relValue)  + " " 
                    elif self.field[i][j].visible and self.field[i][j].bomb:
                        row += "[red]" + bomb + "[/] "
                    elif self.field[i][j].flaged == True: 
                        row += "[yellow]" + flag + "[/] "
                    elif (i,j) in [positions for connection in self.connections for positions in connection.getPositions()]:
                        row +=  "[red]■ [/]"
                    else:
                        row +=  "[bright_white]■ [/]"

            rows += row + "\n"


        return rows