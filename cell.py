


class Cell():
    def __init__(self):
        self.bomb = False
        self.nachbarn = 0
        self.visible = False
        self.flagged = False
        self.tested = False
        self.flaggedNachbarn = 0 
    
    def changeNachbarn(self,change):
        if not self.bomb:
            self.nachbarn += change
    
    def changeFlaggedNachbarn(self,change):
        if not self.bomb:
            self.flaggedNachbarn += change
    
