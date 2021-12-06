from gamefield import Gamefield


from rich.console import Console
from rich import print
console = Console()


x = Gamefield()
x.check((10,10))

print(x.convertToStr())
