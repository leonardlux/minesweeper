


class Cell():
    def __init__(self,position=(None,None)):
        self.bomb = False
        self.value = None #benachbarteBomben
        self.position = position #relevant?

        #Überdenken ?
        self.visible = False
        self.flaged = False
        self.tested = False

    def setNachbarn(self,nachbarn):
        #Liste mit Nachbarn Zellen
        self.nachbarn = nachbarn

        if self.bomb == False:
            self.value = 0
            for cell in self.nachbarn:
                if cell.bomb:
                    self.value +=1
    
    def setValue(self,value):
        #wird nur von temporären Zellen gebraucht
        self.value = value


    #get Methoden
    def visibleNachbarn(self):
        visibleNachbarn = 0
        for cell in self.nachbarn:
            if cell.visible:
                visibleNachbarn += 1
        return visibleNachbarn
                

    def flagedNachbarn(self):
        flagedNachbarn = 0
        for cell in self.nachbarn:
            if cell.flaged:
                flagedNachbarn += 1
        return flagedNachbarn

    
    def checkConnections(self,connections):
        complete = []
        partly = []
        for connection in connections:
            if all((x in [nachbar.position for nachbar in self.nachbarn]) for x in connection.getPositions()):
                complete.append(connection)
            elif True in [(x in [nachbar.position for nachbar in self.nachbarn]) for x in connection.getPositions()]:
                partly.append(connection)
        return complete, partly
    
