import random
import numpy as np
import pickle, datetime, os
import c4_functions as c4
import simulate_c4games as simc4
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.backend import reshape
from tensorflow.keras.utils import to_categorical
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
GAMES_PATH = ".\\games\\1000epochs.pickle"
Model_GAMES_PATH = ".\\model_games\\1000epochs.pickle"
BOARD_ROWS = 6
BOARD_COLUMNS=7
PIECES_IN_ROW_TO_WIN = 4
done = ""
AMOUNT_SIMULATED_GAMES = 10_000
AMOUNT_SIMULATED_GAMES_VALIDATION = 500
droupoutf =0.1
def getModel(l=0,c=0):
    outcomes = 3
    #d=0.1
    model = Sequential()
    model.add(Dense(200, activation='relu', input_shape=((BOARD_ROWS * BOARD_COLUMNS), )))
    model.add(Dropout(droupoutf))
    #Tillägning av lager och celler
    for i in range(l):
        model.add(Dense(c, activation='relu'))
    model.add(Dropout(droupoutf))
    
    model.add(Dense(outcomes, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['acc'])
    return model
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
    #Here the A.I is on work trying to make the best move by predicting Win or Loss or draw by different moves
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
    #If there is no bestMove then choose randomly
    # Choose a move completely at random
    return moves[random.randint(0, len(moves) - 1)]

def movesToBoard(moves):
    #Function that makes the move onto the board 
    board = initBoard()
    for move in moves:
        player = move[0]
        coords = move[1]
        board[coords[1]][coords[0]] = player
    return board

def gameStats(games, player=1):
    #This funtction was used to get the stats of the simulated games
    stats = {"win": 0, "loss": 0, "draw": 0}
    for game in games:
        result = c4.getWinner(c4.movesToBoard(game))
        if result == -1:
            continue
        elif result == player:
            stats["win"] += 1
        elif result == 0:
            stats["draw"] += 1
        else:
            stats["loss"] += 1
    if stats["win"] > 0 and stats["loss"] > 0 and stats["draw"] > 0:
        winPct = stats["win"] / len(games) * 100
        lossPct = stats["loss"] / len(games) * 100
        drawPct = stats["draw"] / len(games) * 100

        print("Results for player %d:" % (player))
        print("Wins: %d (%.1f%%)" % (stats["win"], winPct))
        print("Loss: %d (%.1f%%)" % (stats["loss"], lossPct))
        print("Draw: %d (%.1f%%)" % (stats["draw"], drawPct))
    print((stats["win"]))
    print((stats["loss"]))
    print((stats["draw"]))

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


#Here is the loop for the creation of all the models, Note this will take a long while.
layers = [2,3,4]
celler = [100, 125, 150]
epochs = [10,1000]
layersss=[4]
celllss = [100, 125,150]
e= 10
for e in epochs:
    for d in range(1,6,1):
        droupoutf = d/10
        for l in layers:
            for c in celler:
                model = getModel(l,c)
                name_model=str(l)
                name_model+="_"
                name_model+=str(c)
                name_model+="_" + str(e)
                d = (droupoutf*10)
                d = int(d)
                d = str(d)
                name_model+="_" + d
                print(name_model)
                print("doing stuff")
                games = pickle.load(open(GAMES_PATH, 'rb'))
                X_train, X_test, y_train, y_test = gamesToWinLossData(games)
                history = model.fit(X_train, y_train, validation_data=(X_test,y_test)
                ,epochs=e, batch_size=100)
                MODEL_DIRRR ="models\\"+name_model
                model.save(MODEL_DIRRR)
               
