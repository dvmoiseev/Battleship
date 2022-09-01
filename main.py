import random

class BoardOutException(Exception):
    def __str__(self):
        return "Вводите числа от 1 до 6"

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, dot):
        return (self.x == dot.x) and (self.y == dot.y)

class Ship:
    def __init__(self, position, length, orientation):
        self.position=Dot(position.x, position.y)
        self.length = length
        self.orientation = orientation  # 0 - горизонтально вправо, 1 - вертикально вниз
        self.health_points = length

    @property
    def dots(self):
        ship_points = []
        for i in range(self.length):
            start = self.position
            if self.orientation == 1:  # вниз
                ship_points.append(Dot(start.x+i, start.y))
            if self.orientation == 0:  # вправо
                ship_points.append(Dot(start.x, start.y+i))
        return ship_points

    @property
    def contour(self): #свойство - список точек по контуру корабля
        contour_points = []
        for pnt in self.dots:
            temp = [Dot(pnt.x-1, pnt.y-1), Dot(pnt.x, pnt.y-1), Dot(pnt.x+1, pnt.y-1),
                    Dot(pnt.x-1, pnt.y),                        Dot(pnt.x+1, pnt.y),
                    Dot(pnt.x-1, pnt.y+1), Dot(pnt.x, pnt.y+1), Dot(pnt.x+1, pnt.y+1)]
            for temp_pnt in temp:
                if (-1 < temp_pnt.x < 6) and (-1 < temp_pnt.y < 6):
                    if not(temp_pnt in self.dots):
                        contour_points.append(temp_pnt)
        return contour_points


class Board:
    def __init__(self, hid):
        self.game_board = [['□', '□', '□', '□', '□', '□'],
                           ['□', '□', '□', '□', '□', '□'],
                           ['□', '□', '□', '□', '□', '□'],
                           ['□', '□', '□', '□', '□', '□'],
                           ['□', '□', '□', '□', '□', '□'],
                           ['□', '□', '□', '□', '□', '□']]
        self.ships = []
        self.hid = hid
        self.liveship_count = 7  # в начале игры семь кораблей

    def add_ship(self, ship) -> bool: #возвращает True, если удалось поставить корабль, и False в противном случае
        res = True
        for temp_ship in self.ships:  #для каждого уже установленного корабля
            for temp_dot in temp_ship.dots:  #каждую его точку
                for cur_dot in ship.dots:  #сравним с каждой точкой нового устанавливаемого корабля
                    res = res and (cur_dot != temp_dot)
        for temp_ship in self.ships:  #для каждого уже установленного корабля
            for temp_dot in temp_ship.contour:  #каждую точку его границы
                for cur_dot in ship.dots:  #сравним с каждой точкой нового устанавливаемого корабля
                    res = res and (cur_dot != temp_dot)
        if res:
            for pnt in ship.dots:
                if not self.hid: self.game_board[pnt.x][pnt.y] = "■"
            self.ships.append(ship)
        return res

    def out(self, dot):
        return not ((-1 < dot.x < 6) and (-1 < dot.y < 6))

    def contour(self, ship):
        for temp_pnt in ship.contour:
            self.game_board[temp_pnt.x][temp_pnt.y] = "·"

    # Функция возвращает: 1 - мимо, 2 - ранен, 3 - убит
    def shot(self, move: Dot) -> int:
        if self.out(move):
            raise BoardOutException()

        for ship in self.ships:
            if move in ship.dots:
                self.game_board[move.x][move.y] = "×"
                ship.health_points -= 1
                if ship.health_points == 0:
                    self.liveship_count -= 1
                    self.contour(ship)  #обвести сбитый корабль точками
                    return 3
                else:
                    return 2
        self.game_board[move.x][move.y] = "·"
        return 1

    def __str__(self):
        result = "  │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │\n1 │"
        for i in range(6):
            for j in range(6):
                result+=" "+self.game_board[i][j]+" │"
            if i!=5: result+="\n"+str(i+2)+" │"
        return result


class Player:  #игрок-человек
    def __init__(self, board, moves=[Dot(-1, -1)]):
        self.moves = moves  #Ходы игрока, чтобы предупредить его о стрельбе в ту же клетку
        self.board = board

    def ask(self) -> Dot:
        pnt=[]
        move=Dot(-1, -1)
        while move in self.moves:
            while len(pnt) != 2 or not(pnt[0].isdigit()) or not(pnt[1].isdigit()):
                pnt = input("Ваш ход: ").split()
                if len(pnt)!=2: print("Попробуйте ещё раз. Введите ДВА числа (через пробел).")
                if not(pnt[0].isdigit()) or not(pnt[1].isdigit()): print("Попробуйте ещё раз. Введите два ЧИСЛА (через пробел).")
            move=Dot(int(pnt[0])-1, int(pnt[1])-1)
            if move in self.moves:
                print("Вы уже били в эту клетку. Сделайте другой ход.")
                pnt=[]
        self.moves.append(move)
        return move

class Computer:  #игрок-компьютер
    def __init__(self, board, moves=[Dot(-1, -1)]):
        self.moves = moves  # Ходы компьютера, чтобы не стрелять в ту же клетку
        self.board = board

    def ask(self) -> Dot:
        move = Dot(-1, -1)
        k = 0
        while move in self.moves and k < 1000:
            move = Dot(random.randint(0, 5), random.randint(0, 5))
            k += 1
        self.moves.append(move)
        print ("Мой ход: ("+str(move.x+1)+", "+str(move.y+1)+")")
        return move

class Game:
    def __init__(self):
        self.human = Player(self.random_board(False)) #Свои корабли видны
        self.comp = Computer(self.random_board(False)) #Поставить False чтобы видеть корабли противника

    def random_board(self, hid) -> Board:
        max_attempt = 1000
        ship_length = [3, 2, 2, 1, 1, 1, 1]
        n = 0
        board = None
        while board == None and n < 50:
            board = Board(hid)
            for len in ship_length:
                res = False
                k = 0
                while not res and k < max_attempt: #max_attempt попыток поставить корабль
                    orientation = random.randint(0, 1) # 1 - вертикально, 0 - горизонтально
                    if orientation == 0:
                        start_x = random.randint(0, 5)
                        start_y = random.randint(0, 5 - len + 1)
                    if orientation == 1:
                        start_x = random.randint(0, 5 - len + 1)
                        start_y = random.randint(0, 5)
                    res = board.add_ship(Ship(Dot(start_x, start_y), len, orientation))
                    k+=1
                if k == max_attempt:
                    n += 1
                    board = None
                    break
        return board

    def greet(self):
        print("┌──────────────────┐")
        print("│    МОРСКОЙ БОЙ   │")
        print("└──────────────────┘")

    def loop(self):
        comp_messages = ["     Я промахнулся :-(", "     Я попал в ваш корабль, он ранен. :-P",
                         "     Я сбил ваш корабль. :-)"]
        human_messages = ["     Мимо! :-P", "     Вы попали (ранен)", "     Вы сбили кораблик :-("]

        print("\nПервый ход - ваш. Введите номер строки и столбца (от 1 до 6) клетки, в которую стреляете.")

        game_over = False

        while not game_over:
            print("\nМоя доска:")
            print(self.comp.board)
            print("\nВаши корабли:")
            print(self.human.board)
            print("")

            result = 10
            while result > 1 and self.comp.board.liveship_count > 0:
                try:
                    result = self.comp.board.shot(self.human.ask())
                    print(human_messages[result-1])
                except BoardOutException as msg:
                    print(msg)
            print("")
            if self.comp.board.liveship_count==0:
                print("~~~ Вы выиграли ~~~")
                game_over = True
                continue

            result = 10
            while result > 1 and self.human.board.liveship_count > 0:
                result = self.human.board.shot(self.comp.ask())
                print(comp_messages[result-1])
            print("")
            if self.human.board.liveship_count==0:
                print("!!! Я выиграл !!!")
                game_over = True

    def start(self):
        self.greet()
        self.loop()

game = Game()
game.start()