


class Cell():
    def __init__(self,position):
        self.bomb = False
        self.nachbarn = 0 #benachbarteBomben
        self.position = position
        self.visible = False
        self.flaged = False
        self.tested = False

        #für solving
        self.visibleNachbarn = 0
        self.flagedNachbarn = 0


    def changeNachbarn(self,change):
        if not self.bomb:
            self.nachbarn += change
        
    def changeVisibleNachbarn(self,change):
        if not self.bomb:
            self.visibleNachbarn += change
    
    def changeFlagedNachbarn(self,change):
        if not self.bomb:
            self.flagedNachbarn += change
    
