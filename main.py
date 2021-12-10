from gamefield import Gamefield


from rich.console import Console
from rich import print
console = Console()

#import sys
#print(sys.getrecursionlimit())

csize = console.size
cy = csize[0]
cx = csize[1]

plots = 3

field_x = cx-5
field_y = int(cy/2/plots-1)

bombs = int(field_x*field_y/5)

x = Gamefield((field_x,field_y),bombs)

x.check((int(field_x/2),int(field_y/2)))

playing = True
while playing:
    print(x.convertToStr(plots))
    input_ = input().replace(' ', '')
    if "c" in input_:
        [i,j] = input_.replace('c', '').split(",") 
        playing = x.check((int(i),int(j)))
    
    elif "uf" in input_:
        [i,j] = input_.replace("uf","").split(",")
        x.unflag((int(i),int(j)))
    
    elif "f" in input_:
        [i,j] = input_.replace("f","").split(",")
        x.flag((int(i),int(j)))

    elif "" == input_:
        playing = x.solve()

    elif "ende" in input_:
        break



