import numpy as np 
#game loop stop
game_over = False 
MAXRAD = 6
MAXKOLUMB = 7

def skapa_brade(): #Skapar 0 i grid med 6 rader och 7 kolumber
    board = np.zeros((MAXRAD,MAXKOLUMB)) 
    return board 
def bricka_lagg(board, rad, kolumb, piece): #Funktion för att lägga brickor i listan
    board[rad][kolumb] = piece
    

def valid(board, kolumb):
    return board[MAXRAD-1][kolumb] == 0

def get_next_rad(board, kolumb):
    for i in range(MAXRAD):
        if board[i][kolumb] == 0:
            return i
def rita_board(board):
    print(np.flip(board,0))

def vinst(board, piece):
    #Check vågrät
    for c in range(MAXKOLUMB-3):
        for r in range(MAXRAD):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    #Check Lodräta
    for r in range(MAXRAD-3):
        for c in range(MAXKOLUMB):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    #+ Digonalen 
    for c in range(MAXKOLUMB-3):
        for r in range(MAXRAD-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    #- Digonalen
    for c in range(MAXKOLUMB-3):
        for r in range(3, MAXRAD):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True
        
#intalise board state
board = skapa_brade()
turn = 0


#game loop
while not game_over:
    rita_board(board)
    if turn == 0: 
        print("Spelare 1:")
        kolumb = int(input("Valj postion för din bricka"))-1
        if valid(board, kolumb):
            rad = get_next_rad(board, kolumb)
            bricka_lagg(board, rad, kolumb, (turn+1))
            if vinst(board, (turn+1)):
                print("Spelare 1 Vann spelet")
                rita_board(board)
                game_over = True
    else:
        print("Spelare 2:")
        kolumb = int(input("Valj postion för din bricka"))-1
        if valid(board, kolumb):
            rad = get_next_rad(board, kolumb)
            bricka_lagg(board, rad, kolumb, (turn+1))
            if vinst(board, (turn+1)):
                print("Spelare: 2 Vann spelet")
                rita_board(board)
                game_over = True
    
    turn += 1
    turn = turn % 2
			
slutet = input("Stop?")
print(slutet)
