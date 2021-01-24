import random
import numpy as np

class Board:
    def __init__(self, board_columns=7, board_rows=6, pieces_in_row_to_win=4):
        if board_rows > board_columns:
            raise Exception(f"self.board_rows ({board_columns}) cannot be higher than self.board_columns ({board_columns})")

        if pieces_in_row_to_win > board_rows and pieces_in_row_to_win > board_columns:
            raise Exception(f"pieces_in_row_to_win ({pieces_in_row_to_win}) cannot be higher than the dimensions \
        of the board ({board_columns}x{board_rows})")

        self.board = np.zeros((board_rows, board_columns))
        self.board_columns = board_columns
        self.board_rows = board_rows
        self.pieces_in_row_to_win = pieces_in_row_to_win

    def __str__(self):
        board = str(self.board)
        
        # Format board to look more like a real board
        board = board[1:-1]
        board = board.replace('],', '\n')
        board = board.replace(' [', '[')
        board = board.replace('.]', ']')
        board = board.replace('.', ' ')
        
        return board

    def getMoves(self):
        moves = []
        # Flips the board vertically so it goes through it down-up and not the other way around
        board = np.flip(self.board, axis=0)
        # Keeps track of columns where a possible move has already been appended (so you can't place floating pieces)
        columns_possible_move_appended = [] 

        for row in range(self.board_rows):
            for column in range(self.board_columns):
                if board[row][column] == 0 and not column in columns_possible_move_appended:
                    moves.append((column, (self.board_rows-row-1)))
                    columns_possible_move_appended.append(column)
        
        return moves

    def getWinner(self):
        piece = 1
        MAXKOLUMB=7
        MAXRAD=6
        board = self.board
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
        if (len(self.getMoves()) == 0):
            # It's a draw
            return 0
        else:
            # Still more moves to make
            return -1

    def getBoard(self):
        return self.board

    def placePiece(self, column, row, piece):
        self.board[row][column] = piece

    def setBoard(self, newBoard):
        if len(newBoard) == self.board_rows and len(newBoard[0]) == self.board_columns:
            self.board = np.array(newBoard)
        else:
            raise Exception(f"New board ({len(newBoard[0])}x{len(newBoard)}) is not the same size as old board ({self.board_columns}x{self.board_rows})")

def simulateGame(p1=None, p2=None, rnd=0, board_columns=7, board_rows=6, pieces_in_row_to_win=4):
    history = []
    board = Board(board_columns, board_rows, pieces_in_row_to_win)
    playerToMove = 1
   
    while board.getWinner() == -1:
        # Choose a move (random or use a player model if provided)
        move = None
        if playerToMove == 1 and p1 != None:
            move = bestMove(board, p1, playerToMove, rnd, board_rows, board_columns)
        elif playerToMove == 2 and p2 != None and p2 != "Player":
            move = bestMove(board, p2, playerToMove, rnd, board_rows, board_columns)
        elif playerToMove == 2 and p2 == "Player":
            print(board)
            #print(Board.getMoves(board))
            moved =False
            while moved == False:
                val=int(input("Välj en Move"))
                possible = []
                posible = Board.getMoves(board)
                print(posible)
                for i in range(len(posible)):
                    pos =posible[i]
                    if val == pos[0]:
                        move = pos
                        moved= True
                        print(move)
                #print(board.getWinner())
        else:
            moves = board.getMoves()
            move = moves[random.randint(0, len(moves) - 1)]
        
      
        board.placePiece(move[0], move[1], playerToMove)
    
        history.append((playerToMove, move))
        # Switch the active player
        playerToMove = 1 if playerToMove == 2 else 2
        #print("playing games")
    return history

def bestMove(board, model, player, rnd=0, board_columns=7, board_rows=6):
    scores = []
    moves = board.getMoves()
    
    # Make predictions for each possible move
    for i in range(len(moves)):
        future = np.array(board.getBoard())
        future[moves[i][1]][moves[i][0]] = player
        prediction = model.predict(future.reshape((-1, (board_columns*board_rows))))[0]
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

def movesToBoard(moves, board_columns=7, board_rows=6, pieces_in_row_to_win=4):
    board = Board(board_columns, board_rows, pieces_in_row_to_win)

    for move in moves:
        player = move[0]
        coords = move[1]
        board.placePiece(coords[0], coords[1], player)

    return board

def gameStats(games, player=1, board_columns=7, board_rows=6, pieces_in_row_to_win=4):
    stats = {"win": 0, "loss": 0, "draw": 0}
    for game in games:
        board = movesToBoard(game, board_columns, board_rows, pieces_in_row_to_win)
        result = board.getWinner()

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

    print(f"Results for player {player}:")
    print(f"Wins: {stats['win']} ({winPct}%)")
    print(f"Loss: {stats['loss']} ({lossPct}%)")
    print(f"Draw: {stats['draw']} ({drawPct}%)")


