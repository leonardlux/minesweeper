


class Cell():
    def __init__(self):
        self.bomb = False
        self.nachbarn = 0
        self.visible = False
        self.tested = False
    
    def changeNachbarn(self,change):
        if not self.bomb:
            self.nachbarn += change
