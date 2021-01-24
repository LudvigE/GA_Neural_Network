import c4_functions as c4
import pickle
from time import strftime

SIMULATED_GAMES = 100000
COLUMNS = 7
ROWS = 6
ROW_TO_WIN = 4

def simlutatespel(antal = 10000, p1=None, p2=None):
    SIMULATED_GAMES = antal
    games = [c4.simulateGame(p1,p2) for _ in range(SIMULATED_GAMES)]
    #c4.gameStats(games)
    """
    time = strftime("%Y%m%d_%H%M%S")#+strftime("%H%M%")
    pickle.dump(games, 
    open(
        f"games/{SIMULATED_GAMES}_random_games" +
        f"{time}.pickle",
        'wb'))
    print("Fil namn: "
        f"games/{SIMULATED_GAMES}_random_games" +
        f"{time}.pickle")
    """
    return games

# time format: YEAR|MONTH|DAY_HOUR|MINUTE|SECOND

