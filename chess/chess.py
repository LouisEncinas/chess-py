import os
from termcolor import cprint
from time import sleep
import copy

"""
All moves that do not need to know other pieces moves in the pieces class
"""

###############
### Classes ###
###############

class Move:

    def __init__(self, _from:str, to:str, piece, take:bool=False, upgrade:bool=False, rook:bool=False, en_passant:bool=False, dir_rook:tuple=None, piece_rook=None, pot_threat:bool=True) -> None:
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
        return f'{self.piece} : {self._from}->{tk}{self.to} {up}{ro}'


class Piece:

    """
    No object of class "Piece" is supposed to be created
    """

    PAWN = 'p'
    BISHOP = 'b'
    NIGHT = 'n'
    ROOK = 'r'
    QUEEN = 'q'
    KING = 'k'

    WHITE = 'w'
    BLACK = 'b'

    def __init__(self, id:str, color:str) -> None:

        self._id = id
        self._pos = ''
        self._color = color
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

    def _possible_moves(self, board:list[list]) -> list[Move]:
        pass

class Pawn(Piece):

    def __init__(self, color: str) -> None:
        super().__init__(Piece.PAWN, color)

    def _possible_moves(self, board:list[list]) -> list[Move]:

        psb_mv = []
        index = Piece._pos_to_index(self._pos)
        self.dir = -1 if self._color == Piece.WHITE else 1
        upgrade = True if ((self._color == Piece.WHITE and index[0] == 1) or (self._color == Piece.BLACK and index[0] == 6)) else False
        lim = 2 if self.not_moved else 1

        straight_movements = (self.dir,0)
        eating_movements = [(self.dir,-1),(self.dir,1)]
        ep_movements = [(0,-1),(0,1)]

        new_index = (index[0]+straight_movements[0],index[1]+straight_movements[1])
        while (-1 < new_index[0] < 8 and -1 < new_index[1] < 8) and board[new_index[0]][new_index[1]] == _EMPTY_CASE and abs(new_index[0]-index[0]) <= lim:
            psb_mv.append(Move(Piece._index_to_pos(index), Piece._index_to_pos(new_index), self, upgrade=upgrade, pot_threat=False))
            new_index = (new_index[0]+straight_movements[0],new_index[1]+straight_movements[1])

        for em in eating_movements:
            new_index = (index[0]+em[0],index[1]+em[1])
            if -1 < new_index[0] < 8 and -1 < new_index[1] < 8:
                arrival_case = board[new_index[0]][new_index[1]]
                if isinstance(arrival_case, Piece):
                    if arrival_case._color != self._color: psb_mv.append(Move(Piece._index_to_pos(index), Piece._index_to_pos(new_index), self, take=True, upgrade=upgrade))

        for epm in ep_movements:
            look_index = (index[0]+epm[0],index[1]+epm[1])
            arrival_index = (index[0]+epm[0]+self.dir,index[1]+epm[1])
            if (-1 < arrival_index[0] < 8 and -1 < arrival_index[1] < 8):
                look_case = board[look_index[0]][look_index[1]]
                arrival_case = board[arrival_index[0]][arrival_index[1]]
                if self._pos[1] in ['4','5'] and isinstance(look_case, Pawn) and look_case._color != self._color and len(look_case.moves) == 1:
                    # Mouvement en passant à corriger -> Si le pion ne prend pas en passant directement après le mouvement du pion ennemi, il ne pourra plus prendre en passant
                    psb_mv.append(Move(Piece._index_to_pos(index), Piece._index_to_pos(arrival_index), self, upgrade=upgrade, take=True, en_passant=True))

        return psb_mv

class FiniteMovementPiece(Piece):

    def __init__(self, id: str, color: str) -> None:
        super().__init__(id, color)
        self.movements:list[tuple] = []

    def _possible_moves(self, board: list[list]) -> list[Move]:
        psb_mv = []
        index = Piece._pos_to_index(self._pos)
        for movement in self.movements:
            new_index = (index[0]+movement[0],index[1]+movement[1])
            if -1 < new_index[0] < 8 and -1 < new_index[1] < 8:
                arrival_case = board[new_index[0]][new_index[1]]
                if arrival_case == _EMPTY_CASE:
                    psb_mv.append(Move(Piece._index_to_pos(index), Piece._index_to_pos(new_index), self))
                elif isinstance(arrival_case, Piece):
                    if arrival_case._color != self._color: psb_mv.append(Move(Piece._index_to_pos(index), Piece._index_to_pos(new_index), self, take=True))
        return psb_mv

class Night(FiniteMovementPiece):

    def __init__(self, color:str) -> None:
        super().__init__(Piece.NIGHT, color)
        self.movements = [(2,-1),(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2)]

class King(FiniteMovementPiece):
    
    def __init__(self, color: str) -> None:
        super().__init__(Piece.KING, color)
        self.movements = [(1,1),(-1,1),(-1,-1),(1,-1),(0,1),(0,-1),(1,0),(-1,0)]

    def _possible_moves(self, board: list[list]) -> list[Move]:
        psb_mv = super()._possible_moves(board)
        # Check for rook possibilities
        dirs = [(0,1),(0,-1)]
        index = Piece._pos_to_index(self._pos)
        if self.not_moved:
            for dir in dirs:
                new_index = add(index,dir)
                while 0 < new_index[1] < 7 and board[new_index[0]][new_index[1]] == _EMPTY_CASE:
                    new_index = add(new_index,dir)
                look_case = board[new_index[0]][new_index[1]]
                if isinstance(look_case, Rook) and look_case.not_moved:
                    psb_mv.append(Move(Piece._index_to_pos(index), Piece._index_to_pos((index[0]+2*dir[0],index[1]+2*dir[1])), self, rook=True, dir_rook=dir, piece_rook=look_case))
        
        return psb_mv

class InfiniteMovementPiece(Piece):

    def __init__(self, id: str, color: str) -> None:
        super().__init__(id, color)
        self.directions:list[tuple] = []

    def _possible_moves(self, board: list[list]) -> list[Move]:
        psb_mv = []
        index = Piece._pos_to_index(self._pos)
        for tpl in self.directions:
            new_index = (index[0]+tpl[0],index[1]+tpl[1])
            while -1 < new_index[0] < 8 and -1 < new_index[1] < 8 and board[new_index[0]][new_index[1]] == _EMPTY_CASE:
                psb_mv.append(Move(Piece._index_to_pos(index), Piece._index_to_pos(new_index), self))
                new_index = (new_index[0]+tpl[0],new_index[1]+tpl[1])
            if not self._on_edge((new_index[0]-tpl[0],new_index[1]-tpl[1])):
                if isinstance(board[new_index[0]][new_index[1]],Piece):
                    if board[new_index[0]][new_index[1]]._color != self._color: psb_mv.append(Move(Piece._index_to_pos(index), Piece._index_to_pos(new_index), self, take=True))
        return psb_mv

class Bishop(InfiniteMovementPiece):

    def __init__(self, color:str) -> None:
        super().__init__(Piece.BISHOP, color)
        self.directions = [(1,1),(-1,1),(-1,-1),(1,-1)]

class Rook(InfiniteMovementPiece):

    def __init__(self, color: str) -> None:
        super().__init__(Piece.ROOK, color)
        self.directions = [(0,1),(0,-1),(1,0),(-1,0)]

class Queen(InfiniteMovementPiece):

    def __init__(self, color: str) -> None:
        super().__init__(Piece.QUEEN, color)
        self.directions = [(1,1),(-1,1),(-1,-1),(1,-1),(0,1),(0,-1),(1,0),(-1,0)]

#################
### Functions ###
#################

###########################
###### Sub functions ######
###########################

def convert(piece:Piece, new_type_piece:str) -> Piece:

    """
    This function is called when a pawn arrives at the edge of the board
    
    piece : Promoted pawn
    new_type_piece : a string entered by the player to choose which piece this pawn will become
    """

    dic_pieces = {
        Piece.NIGHT: Night,
        Piece.BISHOP: Bishop,
        Piece.ROOK: Rook,
        Piece.QUEEN: Queen
    }

    new_piece:Piece = dic_pieces[new_type_piece](piece._color)
    new_piece._pos = piece._pos
    new_piece._color = piece._color
    new_piece.not_moved = piece.not_moved
    new_piece.moves = piece.moves

    return new_piece

def initialize_pos(board:list[list]) -> None:

    """
    This function initialize every piece's position on the board.
    It is called right after the board's creation
    """

    for i, row in enumerate(board):
        for j, case in enumerate(row):
            if isinstance(case, Piece):
                case._pos = Piece._index_to_pos((i,j))

def get_king_pos(turn:str, board:list[list[Piece]]) -> str:

    """
    Return the position of the king of the indicated color on the board
    """

    for row in board:
        for case in row:
            if isinstance(case,King) and case._color == turn:
                return case._pos

############################
###### Main functions ######
############################

def possible_moves(board:list[list], turn:str) -> tuple[list[Move],list[Move]]:

        # Create two lists, one containing the player moves and another containing the ennemy moves
        psb_mv_player:list[Move] = []
        psb_mv_holder:list[Move] = []
        for row in board:
            for case in row:
                if isinstance(case, Piece): 
                    if case._color == turn: psb_mv_player += case._possible_moves(board)
                    else: psb_mv_holder += case._possible_moves(board)

        rm_mv:list[Move] = []
        for mv in psb_mv_player + psb_mv_holder:
            if isinstance(mv.piece, King) and mv.rook:
                loop_lst = psb_mv_holder if mv.piece._color == turn else psb_mv_player
                for oth_mv in loop_lst:
                    if ((Piece._index_to_pos((Piece._pos_to_index(mv.to)[0]-mv.dir_rook[0],Piece._pos_to_index(mv.to)[1]-mv.dir_rook[1])) == oth_mv.to or
                    Piece._index_to_pos((Piece._pos_to_index(mv.to)[0],Piece._pos_to_index(mv.to)[1])) == oth_mv.to) and
                    oth_mv.pot_threat and
                    mv not in rm_mv): 
                        rm_mv.append(mv)
            
        for mv in rm_mv:
            if mv.piece._color == turn: psb_mv_player.remove(mv)
            else: psb_mv_holder.remove(mv)
                        
        return psb_mv_player, psb_mv_holder

def is_check(king_pos:str, holder_moves:list[Move]) -> bool:

    # Return if the current player is in check state
    check = False

    for hd_mv in holder_moves:
        if hd_mv.to == king_pos and hd_mv.pot_threat:
            check = True

    return check


def is_check_mate(board:list[list[str or Piece]], player_moves:list[Move]) -> tuple[bool,list[bool]]:
    
    # Return if the current player is in check_state

    check_mate = False

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


def show_board(board:list[list[str or Piece]]):

    print('   * * * * * * * * * *')
    for index_lst, lst in enumerate(board):
        cprint(f' {BOARD_SIZE-index_lst} *', end=' ')
        for case in lst:
            if isinstance(case, Piece): 
                col = 'red' if case._color == Piece.WHITE else 'blue'
                cprint(case._id, col, end=' ')
            else:
                cprint(f'{case}', end=' ')
        print('*')
    print('   * * * * * * * * * *\n     a b c d e f g h')

def show(board:list[list[str or Piece]], game_info:dict) -> None:

        clear()
        show_board(board)

        cprint('\nTurn : ', end='')

        ccm_string = ''
        col = 'red' if game_info['turn'] == Piece.WHITE else 'blue'
        name = 'White' if game_info['turn'] == Piece.WHITE else 'Black'

        cprint(f"{game_info['turn']}", col, end='\n')

        if game_info['check']:
            ccm_string = f'\n{name} in check'
            if game_info['check_mate']:
                ccm_string += ' mate'

        cprint(ccm_string, col, end='\n')

def ask_move() -> tuple[str, str]:
    ipt = input('\nNext move ("form to" format) : ')
    if ipt:
        _from, to = tuple(ipt.split(' '))
    return _from, to

def find_move(_from:str, to:str, lst_mv:list[Move]) -> Move:
    save_move = None
    for move in lst_mv:
        if move._from == _from and move.to == to:
                save_move = move
    return save_move

def move(move:Move, board:list[list[str or Piece]], game_info:dict) -> None:

        if move is not None:
            move.piece.moves.append(move)

            findex = Piece._pos_to_index(move._from)
            fto = Piece._pos_to_index(move.to)

            move.piece._pos = move.to
            if move.piece.not_moved: move.piece.not_moved = False

            if move.upgrade:
                print('\nNew type of piece : (n, b, r, q)')
                ask_new = input()
                board[fto[0]][fto[1]] = convert(move.piece, ask_new)
            else:
                board[fto[0]][fto[1]] = move.piece

            if move.rook:
                rook_index = Piece._pos_to_index(move.piece_rook._pos)
                new_rook_index = (fto[0]-move.dir_rook[0],fto[1]-move.dir_rook[1])
                board[rook_index[0]][rook_index[1]] = _EMPTY_CASE
                board[new_rook_index[0]][new_rook_index[1]] = move.piece_rook
                move.piece_rook._pos = Piece._index_to_pos(new_rook_index)
                move.piece_rook.not_moved = False # If the rook has already moved, not rook is possible
            
            board[findex[0]][findex[1]] = _EMPTY_CASE

            if move.en_passant:
                board[fto[0]-move.piece.dir][fto[1]] = _EMPTY_CASE

            game_info['turn'] = Piece.BLACK if move.piece._color == Piece.WHITE else Piece.WHITE

#######################
### Other functions ###
#######################

def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def add(*tpls) -> tuple:
    res = (0,0)
    for tpl in tpls:
        res = (res[0] + tpl[0], res[1] + tpl[1])
    return res

def time(a, tpl):
    return (a*tpl[0], a*tpl[1])

#######################
### CONST variables ###
#######################

ASCII_UPPER_START = 65
ASCII_LOWER_START = 97
BOARD_SIZE = 8
_EMPTY_CASE = '_'

_INIT_BOARD = [[Rook(Piece.BLACK),Night(Piece.BLACK),Bishop(Piece.BLACK),Queen(Piece.BLACK),King(Piece.BLACK),Bishop(Piece.BLACK),Night(Piece.BLACK),Rook(Piece.BLACK)],
            [Pawn(Piece.BLACK) for _ in range(8)],
            [_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE],
            [_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE],
            [_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE],
            [_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE],
            [Pawn(Piece.WHITE) for _ in range(8)],
            [Rook(Piece.WHITE),Night(Piece.WHITE),Bishop(Piece.WHITE),Queen(Piece.WHITE),King(Piece.WHITE),Bishop(Piece.WHITE),Night(Piece.WHITE),Rook(Piece.WHITE)]]

_TEST_CHECKMATE = [[Rook(Piece.BLACK),Night(Piece.BLACK),Bishop(Piece.BLACK),Queen(Piece.BLACK),King(Piece.BLACK),_EMPTY_CASE,Night(Piece.BLACK),Rook(Piece.BLACK)],
            [Pawn(Piece.BLACK) for _ in range(8)],
            [_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,Bishop(Piece.BLACK)],
            [_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE],
            [_EMPTY_CASE,_EMPTY_CASE,Bishop(Piece.WHITE),_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE],
            [_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,Queen(Piece.WHITE),_EMPTY_CASE,_EMPTY_CASE],
            [Pawn(Piece.WHITE) for _ in range(8)],
            [Rook(Piece.WHITE),Night(Piece.WHITE),Bishop(Piece.WHITE),_EMPTY_CASE,King(Piece.WHITE),_EMPTY_CASE,Night(Piece.WHITE),Rook(Piece.WHITE)]]

_TEST_PIN = [[_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,King(Piece.WHITE),_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE],
            [_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE],
            [_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE],
            [_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,Rook(Piece.WHITE),_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE],
            [_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE],
            [_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE],
            [_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE],
            [_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,Queen(Piece.BLACK),_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE,_EMPTY_CASE]]

############
### main ###
############

def main():

    ### Initialize board ###
    game_board = _INIT_BOARD
    initialize_pos(game_board)
    game_info = {
        'turn' : Piece.WHITE,
        'check' : False,
        'check_mate' : False
    }

    ### Possible moves ###
    psb_mv, hd_mv = possible_moves(game_board, game_info['turn'])
    king_pos = get_king_pos(game_info['turn'], game_board)
    game_info['check'] = is_check(king_pos, hd_mv)
    game_info['check_mate'] = is_check_mate(game_board, psb_mv)

    ### Mainloop ###
    while not game_info['check_mate']:

        show(game_board, game_info)

        print('')
        for mv in psb_mv: print(mv)

        _from, to = ask_move()
        rea_move = find_move(_from, to, psb_mv)
        move(rea_move, game_board, game_info)

        psb_mv, hd_mv = possible_moves(game_board, game_info['turn'])
        king_pos = get_king_pos(game_info['turn'], game_board)
        game_info['check'] = is_check(king_pos, hd_mv)
        game_info['check_mate'] = is_check_mate(game_board, psb_mv)

    ### Show final position and winner ###
    show(game_board, game_info)

if __name__ == '__main__':
    main()