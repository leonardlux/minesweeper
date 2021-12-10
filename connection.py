

class Connection:
    def __init__(self,cells,value):
        self.cells = set(cells)
        self.value = value

    def isIdentical(self,connection):
        if self.cells == set(connection):
            return True
        return False
    
    def getPositions(self,value=None):
        if value==None:
            return [cell.position for cell in self.cells]
        elif value==self.value:
            return [cell.position for cell in self.cells]
        else:
            return []

    def checkConnection(self,position):
        if position in [cell.position for cell in self.cells]:
            return True
        return False 

        