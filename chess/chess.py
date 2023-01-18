import os
import re
import copy
import enum
import numpy as np
import anytree as at
from termcolor import cprint

###############
### Classes ###
###############

class GI(enum.Enum):

    TURN = 0
    CHECK = 1
    CHECK_MATE = 2

class Move:

    def __init__(self, _from:tuple, to:tuple, piece, take:bool=False, upgrade:bool=False, rook:bool=False, en_passant:bool=False, dir_rook:tuple=None, piece_rook=None, pot_threat:bool=True) -> None:
        self.piece:Piece = piece
        self._from = _from
        self.to = to
        self.take = take
        self.upgrade = upgrade
        self.en_passant = en_passant
        self.rook = rook
        self.dir_rook = dir_rook
        self.piece_rook:Rook = piece_rook
        self.pot_threat = pot_threat

    def __str__(self) -> str:
        tk = 'x' if self.take else ''
        up = '(up)' if self.upgrade else ''
        ro = '(rook)' if self.rook else ''
        return f'{self.piece} : {Piece._index_to_pos(self._from)}->{tk}{Piece._index_to_pos(self.to)}{up}{ro}'


class Piece:

    PAWN = 'p'
    BISHOP = 'b'
    NIGHT = 'n'
    ROOK = 'r'
    QUEEN = 'q'
    KING = 'k'

    WHITE = 'w'
    BLACK = 'b'

    def __init__(self, id:str, color:str, position:tuple) -> None:

        self._id = id
        self._color = color
        self._pos = position
        self.not_moved = True
        self.moves:list[Move] = []

    def __str__(self) -> str:
        return self._id

    @staticmethod
    def _index_to_pos(tpl:tuple[int]) -> str:
        # i -> digit backward
        # j -> letter
        return f'{chr(ASCII_LOWER_START+tpl[1])}{BOARD_SIZE-tpl[0]}'

    @staticmethod
    def _pos_to_index(pos:str) -> tuple[int]:
        return (BOARD_SIZE-int(pos[1]),ord(pos[0])-ASCII_LOWER_START)

    @staticmethod
    def _on_edge(index:tuple[int]) -> bool:
        return index[0] == 0 or index[0] == 7 or index[1] == 0 or index[1] == 7

    def _possible_moves(self, piece_dict:dict, board:np.ndarray) -> list[Move]:
        pass

class Pawn(Piece):

    def __init__(self, color:str, position:tuple=()) -> None:
        super().__init__(Piece.PAWN, color, position)
        self.dir = -1 if color == Piece.WHITE else 1
        self.straight_movements = (self.dir,0)
        self.eating_movements = [(self.dir,-1),(self.dir,1)]
        self.ep_movements = [(0,-1),(0,1)]

    def _possible_moves(self, piece_dict:dict[int,Piece], board:np.ndarray) -> list[Move]:

        psb_mv = []
        index = self._pos
        upgrade = True if ((self._color == Piece.WHITE and index[0] == 1) or (self._color == Piece.BLACK and index[0] == 6)) else False
        lim = 2 if self.not_moved else 1

        new_index = (index[0]+self.straight_movements[0],index[1]+self.straight_movements[1])
        while in_bound(new_index) and not board[new_index] and abs(new_index[0]-index[0]) <= lim:
            psb_mv.append(Move(index, new_index, self, upgrade=upgrade, pot_threat=False))
            new_index = add(new_index, self.straight_movements)

        for em, epm in zip(self.eating_movements, self.ep_movements):
            new_index = add(index, em)
            look_index = add(index, epm)
            if in_bound(new_index):
                new_case = board[new_index]; look_case = board[look_index]
                if new_case and piece_dict[new_case]._color != self._color:
                    psb_mv.append(Move(index, new_index, self, take=True, upgrade=upgrade))
                if index[0] in [3,4] and look_case and piece_dict[look_case]._id == Piece.PAWN and piece_dict[look_case]._color != self._color and len(piece_dict[look_case].moves) == 1:
                    psb_mv.append(Move(index, look_index, self, upgrade=upgrade, take=True, en_passant=True))

        return psb_mv

class FiniteMovementPiece(Piece):

    def __init__(self, id:str, color:str, position:tuple) -> None:
        super().__init__(id, color, position)
        self.movements:list[tuple] = []

    def _possible_moves(self, piece_dict:dict[int,Piece], board:np.ndarray) -> list[Move]:

        psb_mv = []
        index = self._pos

        for movement in self.movements:
            new_index = add(index, movement)
            if in_bound(new_index):
                new_case = board[new_index]
                if new_case and piece_dict[new_case]._color != self._color:
                    psb_mv.append(Move(index, new_index, self, take=True))
                elif not new_case:
                    psb_mv.append(Move(index, new_index, self))
        return psb_mv

class Night(FiniteMovementPiece):

    def __init__(self, color:str, position:tuple=()) -> None:
        super().__init__(Piece.NIGHT, color, position)
        self.movements = [(2,-1),(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2)]

class King(FiniteMovementPiece):
    
    def __init__(self, color:str, position:tuple=()) -> None:
        super().__init__(Piece.KING, color, position)
        self.movements = [(1,1),(-1,1),(-1,-1),(1,-1),(0,1),(0,-1),(1,0),(-1,0)]
        self.rook_dirs = [(0,1),(0,-1)]

    def _possible_moves(self, piece_dict:dict[int,Piece], board:np.ndarray) -> list[Move]:

        psb_mv = super()._possible_moves(piece_dict, board)
        # Check for rook possibilities
        index = self._pos
        if self.not_moved:
            for dir in self.rook_dirs:
                new_index = add(index,dir)
                while 0 < new_index[1] < 7 and not board[new_index]:
                    new_index = add(new_index,dir)
                look_case = board[new_index]
                if look_case and piece_dict[look_case]._id == Piece.ROOK and look_case.not_moved:
                    psb_mv.append(Move(index, (index[0]+2*dir[0],index[1]+2*dir[1]), self, rook=True, dir_rook=dir, piece_rook=look_case))
        
        return psb_mv

class InfiniteMovementPiece(Piece):

    def __init__(self, id:str, color:str, position:tuple) -> None:
        super().__init__(id, color, position)
        self.directions:list[tuple] = []

    def _possible_moves(self, piece_dict:dict[int,Piece], board:np.ndarray) -> list[Move]:

        psb_mv = []
        index = self._pos
        for dir in self.directions:
            new_index = add(index,dir)
            while in_bound(new_index) and not board[new_index]:
                psb_mv.append(Move(index, new_index, self))
                new_index = add(new_index,dir)
            if not self._on_edge(minus(new_index,dir)) and board[new_index] and piece_dict[board[new_index]]._color != self._color:
                psb_mv.append(Move(index, new_index, self, take=True))
        return psb_mv

class Bishop(InfiniteMovementPiece):

    def __init__(self, color:str, position:tuple=()) -> None:
        super().__init__(Piece.BISHOP, color, position)
        self.directions = [(1,1),(-1,1),(-1,-1),(1,-1)]

class Rook(InfiniteMovementPiece):

    def __init__(self, color:str, position:tuple=()) -> None:
        super().__init__(Piece.ROOK, color, position)
        self.directions = [(0,1),(0,-1),(1,0),(-1,0)]

class Queen(InfiniteMovementPiece):

    def __init__(self, color:str, position:tuple=()) -> None:
        super().__init__(Piece.QUEEN, color, position)
        self.directions = [(1,1),(-1,1),(-1,-1),(1,-1),(0,1),(0,-1),(1,0),(-1,0)]

#################
### Functions ###
#################

###########################
###### Sub functions ######
###########################

def convert(piece:Piece, new_type_piece:str) -> Piece:
#!
    """
    This function is called when a pawn arrives at the edge of the board
    
    piece : Promoted pawn
    new_type_piece : a string entered by the player to choose which piece this pawn will become
    """

    new_piece:Piece = dic_pieces[new_type_piece](piece._color)
    new_piece._pos = piece._pos
    new_piece._color = piece._color
    new_piece.not_moved = piece.not_moved
    new_piece.moves = piece.moves

    return new_piece

def initialize_position(init_board:list[list[Piece|str]]) -> tuple[dict,np.ndarray]:

    count = 1
    piece_dict = {}
    board = np.zeros((BOARD_SIZE,BOARD_SIZE), dtype='int64')

    for i, row in enumerate(init_board):
        for j, case in enumerate(row):
            if isinstance(case, Piece):
                piece_dict[count] = case
                piece_dict[count]._pos = (i,j)
                board[i,j] = count
                count += 1

    return piece_dict, board

def get_king_pos(turn:str, piece_dict:dict[int,Piece]) -> tuple:
    for piece in piece_dict.values():
        if piece._id == Piece.KING and piece._color == turn:
            return piece._pos

############################
###### Main functions ######
############################

def possible_moves(piece_dict:dict[int,Piece], board:np.ndarray, turn:str) -> tuple[list[Move],list[Move]]:

    # Create two lists, one containing the player moves and another containing the ennemy moves
    psb_mv_player:list[Move] = []
    psb_mv_holder:list[Move] = []
    rook_mv:list[Move] = []

    for piece in piece_dict.values():
        mvs = piece._possible_moves(piece_dict, board)
        rook_mv += [mv for mv in mvs if mv.rook]
        if piece._color == turn: psb_mv_player += mvs
        else: psb_mv_holder += mvs

    rm_mv:list[Move] = []
    for mv in rook_mv:
        loop_lst = psb_mv_holder if mv.piece._color == turn else psb_mv_player
        for oth_mv in loop_lst:
            if (minus(mv.to, mv.dir_rook) == oth_mv.to or mv.to == oth_mv.to) and oth_mv.pot_threat and mv not in rm_mv: 
                rm_mv.append(mv)
        
    for mv in rm_mv:
        if mv.piece._color == turn: psb_mv_player.remove(mv)
        else: psb_mv_holder.remove(mv)
                    
    return psb_mv_player, psb_mv_holder

def is_check(king_pos:str, holder_moves:list[Move]) -> bool:

    # Return if the current player is in check state
    for hd_mv in holder_moves:
        if hd_mv.to == king_pos and hd_mv.pot_threat:
            return True
    return False


def is_check_mate(board:list[list[str or Piece]], player_moves:list[Move]) -> tuple[bool,list[bool]]:
#!!
    # Return if the current player is in checkmate state
    lst_check = []
    for pl_mv in player_moves:
        next_move_board = copy.deepcopy(board)
        rea_move = copy.deepcopy(pl_mv)
        move(rea_move, next_move_board, {'turn':pl_mv.piece._color})
        king_pos = get_king_pos(pl_mv.piece._color, next_move_board)
        hld_mv = possible_moves(next_move_board, pl_mv.piece._color)[1]
        # lst_check.append(is_check(king_pos, hld_mv))
        if is_check(king_pos, hld_mv):
            lst_check.append(pl_mv)
        # lst_check.append(f'{pl_mv.piece} : {pl_mv._from}->{pl_mv.to} :: {is_check(psb_mv, hld_mv)}')
        
    for mv in lst_check: player_moves.remove(mv)  
    # check_mate = all(lst_check)
    
    return player_moves == []

def show_board(piece_dict:dict, board:np.ndarray):

    print('   * * * * * * * * * *')
    for i in range(BOARD_SIZE):
        cprint(f' {BOARD_SIZE-i} *', end=' ')
        for j in range(BOARD_SIZE):
            if board[i,j]:
                piece = piece_dict[board[i,j]]
                col = 'red' if piece._color == Piece.WHITE else 'blue'
                cprint(piece._id, col, end=' ')
            else:
                cprint(EMPTY_CASE, end=' ')
        print('*')
    print('   * * * * * * * * * *\n     a b c d e f g h')

def show(piece_dict:dict, board:np.ndarray, game_info:dict) -> None:

        clear()
        show_board(piece_dict, board)

        cprint('\nTurn : ', end='')

        ccm_string = ''
        col = 'red' if game_info[GI.TURN] == Piece.WHITE else 'blue'
        name = 'White' if game_info[GI.TURN] == Piece.WHITE else 'Black'

        cprint(f"{game_info[GI.TURN]}", col, end='\n')

        if game_info[GI.CHECK]:
            ccm_string = f'\n{name} in check'
            if game_info[GI.CHECK_MATE]:
                ccm_string += ' mate'

        cprint(ccm_string, col, end='\n')

def ask_move() -> tuple[str, str]:
#!
    ipt = input('\nNext move ("from to" format, ex: "e2 e4") : ')
    pattern = re.compile('^[a-h][1-8] [a-h][1-8]$')
    if not pattern.match(ipt):
        return (-1,-1) # return un move impossible (pas dans la liste) pour que ça reset l'affichage
    return tuple(map(lambda pos:Piece._pos_to_index(pos), ipt.split(' ')))

def find_move(_from:str, to:str, lst_mv:list[Move]) -> Move:
#!
    save_move = None
    for move in lst_mv:
        if move._from == _from and move.to == to:
                save_move = move
    return save_move

def move(move:Move, piece_dict:dict[int,Piece], board:np.ndarray, game_info:dict) -> None:
#!
        if move is not None:

            findex = move._from
            fto = move.to
            move.piece.moves.append(move)
            move.piece._pos = fto

            if move.piece.not_moved:
                move.piece.not_moved = False

            if move.upgrade:
                # print('\nNew type of piece : (n, b, r, q)')
                # ask_new = input()
                ask_new = 'q'
                board[fto[0]][fto[1]] = convert(move.piece, ask_new)
            else:
                board[fto[0]][fto[1]] = move.piece

            if move.rook:
                rook_index = move.piece_rook._pos
                new_rook_index = (fto[0]-move.dir_rook[0],fto[1]-move.dir_rook[1])
                board[rook_index[0]][rook_index[1]] = EMPTY_CASE
                board[new_rook_index[0]][new_rook_index[1]] = move.piece_rook
                move.piece_rook._pos = new_rook_index
                move.piece_rook.not_moved = False # If the rook has already moved, not rook is possible
            
            board[findex[0]][findex[1]] = EMPTY_CASE

            if move.en_passant:
                board[fto[0]-move.piece.dir][fto[1]] = EMPTY_CASE

            game_info['turn'] = Piece.BLACK if move.piece._color == Piece.WHITE else Piece.WHITE

def undo_move(move:Move, piece_dict:dict[int,Piece], board:np.ndarray, game_info:dict):
    pass

##################################
###### Evuluation functions ######
##################################

def get_score_from_board(board:list[list[Piece|str]], psb_mv:list[Move], hd_mv:list[Move], turn:str) -> int:
#!
    score = 0
    score_per_piece = {
        Piece.PAWN: 1,
        Piece.NIGHT: 3,
        Piece.BISHOP: 3,
        Piece.ROOK: 5,
        Piece.QUEEN: 9,
        Piece.KING: 20
    }

    for row in board:
        for case in row:
            if case != EMPTY_CASE:
                if case._color == Piece.WHITE:
                    score += score_per_piece[case._id] * 10
                else:
                    score -= score_per_piece[case._id] * 10
            
    if turn == Piece.WHITE:
        score = score + len(psb_mv) - len(hd_mv)
    else:
        score = score - len(psb_mv) + len(hd_mv)

    return score

def define_tree(
    board:list[list[Piece|str]], psb_mv:list[Move], game_info:dict,
    root:at.Node=None, depth=1):
#!
    # Définition de la racine de l'arbre si aucun noeud n'a été passé
    if root is None:
        root = at.Node('root')

    for index, mv in enumerate(psb_mv):

        next_gi = copy.deepcopy(game_info)
        next_board = copy.deepcopy(board)
        rea_mv = copy.deepcopy(mv)
        move(rea_mv, next_board, next_gi)
        pm, hm = possible_moves(next_board, next_gi['turn'])
        next_gi['check_mate'] = is_check_mate(next_board, pm)

        if depth:
            node = at.Node(f'm{index}', parent=root, move=mv)
            define_tree(next_board, pm, next_gi, node, depth=depth-1)
        else:
            node = at.Node(f'm{index}', parent=root, move=mv, score=get_score_from_board(next_board, pm, hm, next_gi['turn']))

    if depth == 1: return root

def min_max(board:list[list[Piece|str]], psb_mv:list[Move], game_info:dict):
#!
    tree = define_tree(board, psb_mv, game_info)

    if game_info['turn'] == Piece.WHITE:
        for fl in tree.children:
            fl.score = min(fl.children, key=lambda l:l.score).score
        return max(tree.children, key=lambda l:l.score).move
    else:
        for fl in tree.children:
            fl.score = min(fl.children, key=lambda l:-l.score).score
        return max(tree.children, key=lambda l:-l.score).move

#######################
### Other functions ###
#######################

def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def add(ftpl, stpl) -> tuple:
    return (ftpl[0] + stpl[0], ftpl[1] + stpl[1])

def minus(ftpl, stpl) -> tuple:
    return (ftpl[0] - stpl[0], ftpl[1] - stpl[1])

def in_bound(pos:tuple) -> bool:
    return -1 < pos[0] < 8 and -1 < pos[1] < 8

#######################
### CONST variables ###
#######################

dic_pieces = {
        Piece.PAWN: Pawn,
        Piece.NIGHT: Night,
        Piece.BISHOP: Bishop,
        Piece.ROOK: Rook,
        Piece.QUEEN: Queen,
        Piece.KING: King
    }

ASCII_UPPER_START = 65
ASCII_LOWER_START = 97
BOARD_SIZE = 8
EMPTY_CASE = '_'

##############################
###### INITIAL POSITION ######
##############################

_INIT_BOARD = [[Rook(Piece.BLACK),Night(Piece.BLACK),Bishop(Piece.BLACK),Queen(Piece.BLACK),King(Piece.BLACK),Bishop(Piece.BLACK),Night(Piece.BLACK),Rook(Piece.BLACK)],
            [Pawn(Piece.BLACK) for _ in range(8)],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [Pawn(Piece.WHITE) for _ in range(8)],
            [Rook(Piece.WHITE),Night(Piece.WHITE),Bishop(Piece.WHITE),Queen(Piece.WHITE),King(Piece.WHITE),Bishop(Piece.WHITE),Night(Piece.WHITE),Rook(Piece.WHITE)]]

_TEST_CHECKMATE = [[Rook(Piece.BLACK),Night(Piece.BLACK),Bishop(Piece.BLACK),Queen(Piece.BLACK),King(Piece.BLACK),EMPTY_CASE,Night(Piece.BLACK),Rook(Piece.BLACK)],
            [Pawn(Piece.BLACK) for _ in range(8)],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,Bishop(Piece.BLACK)],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,Bishop(Piece.WHITE),EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,Queen(Piece.WHITE),EMPTY_CASE,EMPTY_CASE],
            [Pawn(Piece.WHITE) for _ in range(8)],
            [Rook(Piece.WHITE),Night(Piece.WHITE),Bishop(Piece.WHITE),EMPTY_CASE,King(Piece.WHITE),EMPTY_CASE,Night(Piece.WHITE),Rook(Piece.WHITE)]]

_TEST_PIN = [[EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,King(Piece.WHITE),EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,Rook(Piece.WHITE),EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,Queen(Piece.BLACK),EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE]]

_TEST_SCORE = [[EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,Night(Piece.BLACK),EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [Pawn(Piece.WHITE),EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE],
            [EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE,EMPTY_CASE]]

############
### main ###
############

def main():

    ### Initialize board ###
    piece_dict, board = initialize_position(_INIT_BOARD)

    ### Initialize game information
    game_info = {
        GI.TURN : Piece.WHITE,
        GI.CHECK : False,
        GI.CHECK_MATE : False
    }

    psb_mv, hd_mv = possible_moves(piece_dict, board, game_info[GI.TURN])
    for mv in psb_mv:
        print(mv)

    # ### Possible moves ###
    # psb_mv, hd_mv = possible_moves(game_board, game_info['turn'])
    # king_pos = get_king_pos(game_info['turn'], game_board)
    # game_info['check'] = is_check(king_pos, hd_mv)
    # game_info['check_mate'] = is_check_mate(game_board, psb_mv)

    # ### Mainloop ###
    # while not game_info['check_mate']:

    #     show(game_board, game_info)

    #     # print('')
    #     # for mv in psb_mv: print(mv)
    #     # print(f"Current board score : {get_score_from_board(game_board, psb_mv, hd_mv, game_info['turn'])}\n")
    #     # print(f"Best move : {min_max(game_board, psb_mv, game_info)}")

    #     _from, to = ask_move()
    #     rea_move = find_move(_from, to, psb_mv)
    #     move(rea_move, game_board, game_info)

    #     psb_mv, hd_mv = possible_moves(game_board, game_info['turn'])
    #     king_pos = get_king_pos(game_info['turn'], game_board)
    #     game_info['check'] = is_check(king_pos, hd_mv)
    #     game_info['check_mate'] = is_check_mate(game_board, psb_mv)

    # ### Show final position and winner ###
    # show(game_board, game_info)

if __name__ == '__main__':
    main()