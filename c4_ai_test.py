import random
import numpy as np

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.backend import reshape
from tensorflow.keras.utils import to_categorical

def getModel():
    outcomes = 3
    model = Sequential()
    model.add(Dense(200, activation='relu', input_shape=((BOARD_ROWS * BOARD_COLUMNS), )))
    model.add(Dropout(0.2))
    model.add(Dense(125, activation='relu'))
    model.add(Dense(75, activation='relu'))
    model.add(Dropout(0.1))
    model.add(Dense(25, activation='relu'))
    model.add(Dense(outcomes, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['acc'])
    return model

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

# BOARD_COLUMNS must be higher than or equal to BOARD_ROWS
BOARD_ROWS = 6
BOARD_COLUMNS = 7
AMOUNT_SIMULATED_GAMES = 10_000
AMOUNT_SIMULATED_GAMES_VALIDATION = 1000
PIECES_IN_ROW_TO_WIN = 4

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
    
    # Check rows
    for row in range(BOARD_ROWS):
        candidate = 0
        pieces_in_row = 0

        for column in range(BOARD_COLUMNS):
            if candidate == 0:
                candidate = board[row][column]
                if candidate != 0:
                    pieces_in_row = 1
                continue
            
            if board[row][column] == candidate:
                pieces_in_row += 1

                if pieces_in_row == PIECES_IN_ROW_TO_WIN:
                    return candidate
            else:
                candidate = board[row][column]
                if candidate == 0:
                    pieces_in_row = 1
    
    # Check columns
    for column in range(BOARD_COLUMNS):
        candidate = 0
        pieces_in_row = 0

        for row in range(BOARD_ROWS):
            if candidate == 0:
                candidate = board[row][column]
                if candidate != 0:
                    pieces_in_row = 1
                continue
            
            if board[row][column] == candidate:
                pieces_in_row += 1

                if pieces_in_row == PIECES_IN_ROW_TO_WIN:
                    return candidate
            else:
                candidate = board[row][column]
                pieces_in_row = 1

    # Check diagonals: left to right
    for diagonal_offset in range(-BOARD_ROWS+1, BOARD_COLUMNS):
        diagonal = board.diagonal(diagonal_offset)
        candidate = 0
        pieces_in_row = 0
        
        # Just calculate if diagonal is long enough for someone to win on
        # to avoid unnecessary calculations
        if len(diagonal) >= PIECES_IN_ROW_TO_WIN:
            for piece in diagonal:
                if candidate == 0:
                    candidate = piece
                    if candidate != 0:
                        pieces_in_row = 1
                    continue
            
                if piece == candidate:
                    pieces_in_row += 1

                    if pieces_in_row == PIECES_IN_ROW_TO_WIN:
                        return candidate
                else:
                    candidate = piece
                    pieces_in_row = 1

    # Check diagonals: right to left
    board = np.flip(board, axis=1)
    for diagonal_offset in range(-BOARD_ROWS+1, BOARD_COLUMNS):
        diagonal = board.diagonal(diagonal_offset)
        candidate = 0
        pieces_in_row = 0
        
        # Just calculate if diagonal is long enough for someone to win on
        # to avoid unnecessary calculations
        if len(diagonal) >= PIECES_IN_ROW_TO_WIN:
            for piece in diagonal:
                if candidate == 0:
                    candidate = piece
                    if candidate != 0:
                        pieces_in_row = 1
                    continue
            
                if piece == candidate:
                    pieces_in_row += 1

                    if pieces_in_row == PIECES_IN_ROW_TO_WIN:
                        return candidate
                else:
                    candidate = piece
                    pieces_in_row = 1


                
    # Still more moves to make?
    if (len(getMoves(board)) == 0):
        # It's a draw
        return 0
    else:
        # Still more moves to make
        return -1

def simulateGame(p1=None, p2=None, rnd=0):
    history = []
    board = initBoard()
    playerToMove = 1
    
    while getWinner(board) == -1:
        # Chose a move (random or use a player model if provided)
        move = None
        if playerToMove == 1 and p1 != None:
            move = bestMove(board, p1, playerToMove, rnd)
        elif playerToMove == 2 and p2 != None:
            move = bestMove(board, p2, playerToMove, rnd)
        else:
            moves = getMoves(board)
            move = moves[random.randint(0, len(moves) - 1)]
        
        # Make the move
        board[move[1]][move[0]] = playerToMove
        
        # Add the move to the history
        history.append((playerToMove, move))
        
        # Switch the active player
        playerToMove = 1 if playerToMove == 2 else 2
    
    return history

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
    
    winPct = stats["win"] / len(games) * 100
    lossPct = stats["loss"] / len(games) * 100
    drawPct = stats["draw"] / len(games) * 100

    print("Results for player %d:" % (player))
    print("Wins: %d (%.1f%%)" % (stats["win"], winPct))
    print("Loss: %d (%.1f%%)" % (stats["loss"], lossPct))
    print("Draw: %d (%.1f%%)" % (stats["draw"], drawPct))

'''
board = np.array(
   [[0, 0, 2, 2, 0, 1, 2],
    [1, 0, 2, 2, 1, 2, 2],
    [1, 2, 1, 1, 0, 0, 0],
    [0, 0, 1, 2, 0, 2, 0],
    [0, 1, 0, 1, 0, 2, 0],
    [1, 0, 1, 1, 2, 0, 0]]
)
'''

games = [simulateGame() for _ in range(AMOUNT_SIMULATED_GAMES)]

model = getModel()
X_train, X_test, y_train, y_test = gamesToWinLossData(games)
history = model.fit(X_train, y_train, validation_data=(X_test,
    y_test), epochs=100, batch_size=100)
print("\nMODEL FITMENT DONE")

games2 = [simulateGame(p1=model) for _ in range(AMOUNT_SIMULATED_GAMES_VALIDATION)]
gameStats(games2)
