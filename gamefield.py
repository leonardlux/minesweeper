
from os import error
from rich import console
from rich import print

from connection import Connection
from cell import Cell

import random

#random.seed(18)
class Gamefield:
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
            self.field[bombPosition[0]][bombPosition[1]].bomb = True

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


    def makeVisible(self,cell):
        if cell.visible == False:
            cell.visible = True
            return True
        else:
            print("Warnung: Zelle schon sichbar!")
            print(cell.position)
            return False


    def zeroCell(self,liste):
        #Hier sollten nur 0 positionen übergeben werden
        
        while len(liste)!=0:
            cell = liste[0]
            liste = liste[1:]
            if cell.visible==False:
                self.makeVisible(cell)
                cell.tested = True

            for nachbar in cell.nachbarn:  
                if nachbar.tested == False and nachbar.value == 0:
                    nachbar.tested = True
                    liste.append(nachbar)
                elif nachbar.tested == False and nachbar.visible == False:
                    self.makeVisible(nachbar)
                    self.border.append(nachbar)
    
    
    def checkForZeroes(self,cell):
        #falls 0 an das gecheckte Feld angrenzen, dann wird make Visible aufgerufen
        for nachbar in cell.nachbarn:
            if nachbar.value == 0 and nachbar.tested == False:
                nachbar.tested = True
                self.zeroCell([nachbar])
                return True
        return False

        
    def check(self,position):
        #Falls manueller Input
        if type(position)==tuple or type(position)==list:
            if position[0]>= self.dimension[0] or position[1]>= self.dimension[1]:
                print("Außerhlab des Spielfelds!")
                return True
            cell = self.field[position[0]][position[1]]
        else:
            cell = position

        if cell.visible == True:
            print("Schon sichtbar!")
            return True
        elif cell.flaged == True:
            print("Flaged!")
            return True

        #erster Check
        while self.firstCheck == True:
            self.makeVisible(cell)
            if cell.value != 0:
                self.border.append(cell) 
            if not self.checkForZeroes(cell):
                print("Reshuffel")
                self.__init__(self.dimension,self.bombs)
                cell = self.field[cell.position[0]][cell.position[1]]
                
            else:
                self.firstCheck = False
                return True
        
        if self.firstCheck == False and cell.flaged==False:
            self.makeVisible(cell)
            self.border.append(cell)
            self.checkForZeroes(cell)
            if cell.bomb:
                print(self.convertToStr(1))
                print("Boooooom! You hit a Bomb! ")
                return False
            return True
        
        
    def flag(self,position):
        #Falls manueller Input
        if type(position)==tuple or type(position)==list:
            if position[0]>= self.dimension[0] or position[1]>= self.dimension[1]:
                print("Außerhlab des Spielfelds!")
                return True
            cell = self.field[position[0]][position[1]]
        else:
            cell = position

        if cell.visible == False and cell.flaged == False:
            cell.flaged = True
            self.flags += 1

            for i in range(len(self.connections)):
                if self.connections[i].checkConnection(cell.position):
                    self.connections.remove(self.connections[i])
                    break           
            
        else:
            print("Feld schon offen oder flaged")
        

    def unflag(self,position):
        #Nur für manuellen Input
        if position[0]>= self.dimension[0] or position[1]>= self.dimension[1]:
            print("Außerhlab des Spielfelds!")

        if self.field[position[0]][position[1]].flaged == True:
            self.field[position[0]][position[1]].flaged = False
        else:
            print("Feld schon offen oder nicht flaged")


    def updateBorder(self):
        self.usedBorderCells = []
        #entfernen wenn alle nachbarfelder bekannt sind
        for cell in self.border:
            if cell.visibleNachbarn() + cell.flagedNachbarn() == len(cell.nachbarn):
                self.usedBorderCells.append(cell)
        for cell in self.usedBorderCells:
            self.border.remove(cell)


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
        
        for cell in self.border:
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


        for cell in self.border:
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

        
        for i, cells in enumerate(self.field):
            row = ""
            #Normaler Spielmodus
            row += color_side + "{:2} [/]".format(i)
            for cell in cells:
                if cell.visible: 
                    if  cell.bomb:
                        row += "[red]" + bomb + "[/] "
                    elif cell in self.border:
                        row +=  "[purple]" + str(cell.value) + "[/] " 
                    elif cell in self.usedBorderCells:
                        row +=  "[red]" + str(cell.value) + "[/] " 
                    else:
                        row += colors[cell.value] + str(cell.value) + "[/] "  
                elif cell.flaged == True: 
                    row += "[yellow]" + flag + "[/] "
                else:
                    row +=  "[bright_white]■ [/]"
            if plots >=2:
                #Automatismus 1
                row += color_side + "{:2} [/]".format(i)
                for cell in cells:
                    if cell.visible and not cell.bomb:
                        if cell in self.border :
                            row +=  "[purple]" + str(cell.value - cell.flagedNachbarn()) + "[/] " 
                        elif cell in self.usedBorderCells:
                            row +=  "[red]" + str(cell.value - cell.flagedNachbarn()) + "[/] " 
                        elif not cell.bomb:
                            row += str(cell.value - cell.flagedNachbarn()) + " " 
                    elif cell.visible and cell.bomb:
                            row += "[red]" + bomb + "[/] "
                    elif cell.flaged == True: 
                        row += "[yellow]" + flag + "[/] "
                    else:
                        row +=  "[bright_white]■ [/]"
            if plots >=3:
                #Automatismus 2
                row += color_side + "{:2} [/]".format(i)
                for cell in cells:
                    if cell.visible and not cell.bomb:
                        relValue = len(cell.nachbarn) - cell.visibleNachbarn() - cell.value
                        if cell in self.border:
                            row +=  "[purple]" + str(relValue) + "[/] " 
                        elif cell in self.usedBorderCells:
                            row +=  "[red]" + str(relValue) + "[/] " 
                        else:
                            row += str(relValue)  + " " 
                    elif cell.visible and cell.bomb:
                        row += "[red]" + bomb + "[/] "
                    elif cell.flaged == True: 
                        row += "[yellow]" + flag + "[/] "
                    elif cell in [connectionCell for connection in self.connections for connectionCell in connection.cells]:
                        row +=  "[red]■ [/]"
                    else:
                        row +=  "[bright_white]■ [/]"

            rows += row + "\n"


        return rows