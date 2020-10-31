import c4_functions as c4
import pickle
from time import strftime, gmtime

AMOUNT_SIMULATED_GAMES = 1_000
BOARD_COLUMNS = 7
BOARD_ROWS = 6
PIECES_IN_ROW_TO_WIN = 4

games = [c4.simulateGame() for _ in range(AMOUNT_SIMULATED_GAMES)]
c4.gameStats(games)

# time format: YEAR|MONTH|DAY_HOUR|MINUTE|SECOND
time = strftime("%Y%m%d_%H%M%S")
pickle.dump(games, open(f"games/{AMOUNT_SIMULATED_GAMES}_games{BOARD_COLUMNS}x{BOARD_ROWS}_{PIECES_IN_ROW_TO_WIN}_{time}.pickle", 'wb'))