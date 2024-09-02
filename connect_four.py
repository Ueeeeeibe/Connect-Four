import discord

number_emojis = {1:"1️⃣", 2:"2️⃣", 3:"3️⃣", 4:"4️⃣", 5:"5️⃣", 6:"6️⃣", 7:"7️⃣", 8:"8️⃣", 9:"9️⃣", 10: "🔟"}
color_emojis = {0:"🔲", 1:"🔴", 2:"🔵"}

class ConnectBoard:
    __text = ""
    msg: discord.Message = None

    def __init__(self, host: discord.Member, opponent: discord.Member, width: int, height: int, win_number: int):
        self.host_id: int = host.id
        self.opponent_id: int = opponent.id
        self.width: int = width
        self.height: int = height
        self.win_number: int = win_number
        self.turn_user_id: int = host.id
        self.game_board = [[0 for _ in range(width)] for _ in range(height)]
        self.is_started = False
        self.is_finished = False

        text = ""
        for i in range(width):
            print(number_emojis[i+1], end='')
            text += number_emojis[i+1]
        print('')
        text += "\n"
        for i in range(height):
            index = 0
            for j in range(width):
                if self.game_board[i][j] == 0:
                        index = index + 1
                        print(color_emojis[0], end='')
                        text += color_emojis[0]
                        if index == width:
                            print('')
                            text += "\n"
        self.__text = text

    # ボードをtextに加える
    def display_board(self):
        text = ""        
        for i in range(self.width):
            print(number_emojis[i+1], end='')
            text += number_emojis[i+1]
        print('')
        text += "\n"
        for i in range(self.height):
            index = 0
            for j in range(self.width):
                for color_number in range(len(color_emojis)):
                    if self.game_board[i][j] == color_number:
                        index = index + 1
                        print(color_emojis[color_number], end='')
                        text += color_emojis[color_number]
                        if index == self.width:
                            print('')
                            text += "\n"
        self.__text = text
        
    # ホストのターンの処理
    def my_turn(self, x):
        if self.game_board[0][x-1] != 0:
            print("その場所には置けません")
            self.__text = "その場所には置けません\n" + self.__text.replace("その場所には置けません\n", "")
            self.change_turn()
            return
        for i in range(1, self.height+1):
            if self.game_board[self.height-i][x-1] != 0:
                continue
            self.game_board[self.height-i][x-1] = 1
            y = self.height - i
            break
        self.check_win(y, x-1)
    
    # 相手のターンの処理
    def your_turn(self, x):
        if self.game_board[0][x-1] != 0 :
            print("その場所には置けません")
            self.__text = "その場所には置けません\n" + self.__text.replace("その場所には置けません\n", "")
            self.change_turn()
            return
        for i in range(1, self.height+1):
            if self.game_board[self.height-i][x-1] != 0:
                continue
            self.game_board[self.height - i][x-1] = 2
            y = self.height - i
            break
        self.check_win(y, x-1)

    # 勝敗判定
    def check_win(self, h, w):
        color = self.game_board[h][w]
        # 横方向の判定
        if self.check_horizontal_win(h, w, color):
            return
        # 縦方向の判定
        if self.check_vertical_win(h, w, color):
            return
        # 右斜めの判定
        if self.check_right_diagonal_win(h, w, color):
            return
        # 左斜めの判定
        if self.check_left_diagonal_win(h, w, color):
            return

        # 引き分け判定
        if self.check_draw():
            return
        

        self.display_board()

    def check_vertical_win(self, h, w, color):
        count = -1
        i = 0
        while (self.game_board[h+i][w] == color):
            count += 1
            i += 1
            if (h+i >= self.height):
                break
        i = 0
        while (self.game_board[h+i][w] == color):
            count += 1
            i -= 1
            if (h+i < 0):
                break
        return self.is_win(count)  


    def check_horizontal_win(self, h, w, color):
        count = -1
        i = 0
        while (self.game_board[h][w+i] == color):
            count += 1
            i += 1
            if (w+i >= self.width):
                break
        i = 0
        while (self.game_board[h][w+i] == color):
            count += 1
            i -= 1
            if (w+i < 0):
                break  
        return self.is_win(count)  

        
    def check_right_diagonal_win(self, h, w, color):
        count = -1
        i = 0
        while (self.game_board[h+i][w+i] == color):
            count += 1
            i += 1
            if (w+i >= self.width or h+i >= self.height):
                break
        i = 0
        while (self.game_board[h+i][w+i] == color):
            count += 1
            i -= 1
            if (h+i < 0 or w+i < 0):
                break 
        return self.is_win(count)  

    def check_left_diagonal_win(self, h, w, color):
        count = -1
        i = 0
        while (self.game_board[h-i][w+i] == color):
            count += 1
            i += 1
            if (w + i >= self.width or h - i < 0):
                break
        i = 0
        while (self.game_board[h-i][w+i] == color):
            count += 1
            i -= 1
            if (h - i >= self.height or w + i < 0):
                break     
        return self.is_win(count)
        
    # 勝者が決まったか判定する
    def is_win(self, count):
        if count >= self.win_number:
            self.display_board()
            win_player_id = self.turn_user_id
            self.__text += f"\n勝者: {self.get_color(win_player_id)}<@{win_player_id}>"
            self.is_finished = True
            return True
        return False

    # 引き分けか判定する
    def check_draw(self):
        is_draw = True
        for i in range(self.width):
            if self.game_board[0][i] == 0:
                is_draw = False
        if not is_draw:
            return False
        self.display_board()
        self.__text += "\n引き分け"
        self.is_finished = True
        return True
    
    # テキストを取得する
    def get_text(self):
        return self.__text

    # ターンを変更する
    def change_turn(self):
        self.turn_user_id = self.host_id if self.turn_user_id == self.opponent_id else self.opponent_id
    
    def get_color(self, user_id):
        if user_id == self.host_id:
            return color_emojis[1]
        else:
            return color_emojis[2]

