from gamefield import Gamefield


from rich.console import Console
from rich import print
console = Console()

#import sys
#print(sys.getrecursionlimit())

x = Gamefield()
playing = True
while playing:
    print(x.convertToStr())
    try:
        input_ = input().replace(' ', '')
        if "c" in input_:
            [i,j] = input_.replace('c', '').split(",") 
            playing = x.check((int(i),int(j)))
        elif "f" in input_:
            [i,j] = input_.replace("f","").split(",")
            x.flag((int(i),int(j)))
        elif "ende" in input_:
            break
    except:
        print("failed")

