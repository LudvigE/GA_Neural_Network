import random
import numpy as np
from time import strftime
import pickle, datetime, os
import c4_functions as c4
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.backend import reshape
from tensorflow.keras.utils import to_categorical
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
BOARD_ROWS = 6
BOARD_COLUMNS=7
PIECES_IN_ROW_TO_WIN = 4
done = ""
AMOUNT_SIMULATED_GAMES = 10_000
AMOUNT_SIMULATED_GAMES_VALIDATION = 500
droupoutf =0.1
winprocent =0
tieprocent =0
def initBoard():
    board = np.zeros((BOARD_ROWS, BOARD_COLUMNS))
    return board

def getMoves(board):
    moves = []
    # Flips the board vertically so it goes through it down-up and not the other way around
    board = np.flip(board, axis=0)
    # Keeps track of columns where a possible move has already been appended (so you can't place floating pieces)
    columns_possible_move_appended = [] 
    
    for row in range(BOARD_ROWS):
        for column in range(BOARD_COLUMNS):
            if board[row][column] == 0 and not column in columns_possible_move_appended:
                moves.append((column, (BOARD_ROWS-row-1)))
                columns_possible_move_appended.append(column)
    return moves

def getWinner(board):
   #Function that checks if anyone has won 
        # Check rows
        piece = 1
        MAXKOLUMB=7
        MAXRAD=6
        board = board
        for piece in range(1,3,1):
            for c in range(MAXKOLUMB-3):
                for r in range(MAXRAD):
                    if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                        return piece
        #Check Lodräta
            for r in range(MAXRAD-3):
                for c in range(MAXKOLUMB):
                    if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                        return piece
        #+ Digonalen 
            for c in range(MAXKOLUMB-3):
                for r in range(MAXRAD-3):
                    if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                        return piece
        #- Digonalen
            for c in range(MAXKOLUMB-3):
                for r in range(3, MAXRAD):
                    if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                        return piece                     
        
        # Still more moves to make?
        if (len(getMoves(board)) == 0):
            # It's a draw
            return 0
        else:
            # Still more moves to make
            return -1


def bestMove(board, model, player, rnd=0):
    scores = []
    moves = getMoves(board)
    
    # Make predictions for each possible move
    for i in range(len(moves)):
        future = np.array(board)
        future[moves[i][1]][moves[i][0]] = player
        prediction = model.predict(future.reshape((-1, (BOARD_ROWS*BOARD_COLUMNS))))[0]
        if player == 1:
            winPrediction = prediction[1]
            lossPrediction = prediction[2]
        else:
            winPrediction = prediction[2]
            lossPrediction = prediction[1]
        drawPrediction = prediction[0]
        if winPrediction - lossPrediction > 0:
            scores.append(winPrediction - lossPrediction)
        else:
            scores.append(drawPrediction - lossPrediction)

    # Choose the best move with a random factor
    bestMoves = np.flip(np.argsort(scores))
    for i in range(len(bestMoves)):
        if random.random() * rnd < 0.5:
            return moves[bestMoves[i]]

    # Choose a move completely at random
    return moves[random.randint(0, len(moves) - 1)]

def movesToBoard(moves):
    board = initBoard()
    for move in moves:
        player = move[0]
        coords = move[1]
        board[coords[1]][coords[0]] = player
    return board

def gameStats(games, player=1):
    stats = {"win": 0, "loss": 0, "draw": 0}
    for game in games:
        result = getWinner(movesToBoard(game))
        if result == -1:
            continue
        elif result == player:
            stats["win"] += 1
        elif result == 0:
            stats["draw"] += 1
        else:
            stats["loss"] += 1
    
    return(stats["win"],stats["draw"])

    
    

def gamesToWinLossData(games):
    X = []
    y = []
    for game in games:
        winner = getWinner(movesToBoard(game))
        for move in range(len(game)):
            X.append(movesToBoard(game[:(move + 1)]))
            y.append(winner)

    X = np.array(X).reshape((-1, (BOARD_ROWS*BOARD_COLUMNS)))
    y = to_categorical(y)
    
    # Return an appropriate train/test split
    trainNum = int(len(X) * 0.8)
    return (X[:trainNum], X[trainNum:], y[:trainNum], y[trainNum:])

modeler = os.listdir('models/')
print(modeler)
for a in modeler:
    saveee = []
    namn = "models\\"+a
    model = tf.keras.models.load_model(namn)
    print("loaded model")
    games = [c4.simulateGame(p1=model) for _ in range(100)]
    statss=gameStats(games)
    print(a)
    print(statss)
    
    saveee.append(statss)
    folder = "statsv2\\"+a
    pickle.dump(saveee, open(folder, "wb"))
