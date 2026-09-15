import math
import random
import socket
import database
import pygame
from russian_names import RussianNames


pygame.init()


SERVER_W, SERVER_H = 4000, 4000
W, H = 300, 300
FPS = 100
colors = ['Maroon', 'DarkRed', 'FireBrick', 'Red', 'Salmon', 'Tomato', 'Coral', 'OrangeRed', 'Chocolate', 'SandyBrown', 'DarkOrange', 'Orange', 'DarkGoldenrod', 'Goldenrod', 'Gold', 'Olive', 'Yellow', 'YellowGreen', 'GreenYellow','Chartreuse', 'LawnGreen', 'Green', 'Lime', 'SpringGreen', 'MediumSpringGreen', 'Turquoise',  'LightSeaGreen', 'MediumTurquoise', 'Teal', 'DarkCyan', 'Aqua', 'Cyan', 'DeepSkyBlue',        'DodgerBlue', 'RoyalBlue', 'Navy', 'DarkBlue', 'MediumBlue']
MOBS_COUNT = 25
FOOD_SIZE = 10
FOOD_COUNT = SERVER_W * SERVER_H // 40000000
visible_bacteries = {}
tick = -1

class Food:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = FOOD_SIZE


class LocalPlayer:
    def __init__(self, id, name, color, socket, adress):
        self.w_vision = 800
        self.h_vision = 600
        self.id = id
        self.name = name
        self.socket = socket
        self.adress = adress
        self.x = 500
        self.y = 500
        self.size = 50
        self.errors = 0
        self.abf = 2
        self.speedx = 2
        self.speedy = 2
        self.color = color

    def update(self):
        if self.x-self.size <= 0:
            if self.speedx > 0:
                self.x += self.speedx
        elif self.x+self.size >= SERVER_W:
            if self.speedx < 0:
                self.x += self.speedx
        else:
            self.x += self.speedx

        if self.y-self.size <= 0:
            if self.speedy > 0:
                self.y += self.speedy
        elif self.y+self.size >= SERVER_H:
            if self.speedy < 0:
                self.y += self.speedy
        else:
            self.y += self.speedy

        database.s.query(database.Player).filter(database.Player.id == self.id).update({
            "x":self.x,
            "y":self.y
        })
        database.s.commit()

    def changed_speed(self, vector):
        vector = find(vector)
        if vector[0] == 0 and vector[1] == 0:
            self.speedx, self.speedy = 0,0
        else:
            self.speedx, self.speedy = vector[0] * self.abf, vector[1] * self.abf


    



def find(vector:str):
    first = vector.find('<')
    second = vector.find('>')

    if first < second and first>=0 :
        result = vector[first+1:second]
        result = result.split(",")
        result = list(map(float, result))
        return result
    return ""



def accept_new_clients(main_socket, players):
    try:
        client_socket, addr = main_socket.accept()
        print('подключился', addr)
        client_socket.setblocking(False)
        login = client_socket.recv(1024).decode()
        if login.startswith("color"):
            name, r,g,b = login[6:].replace("<", "").replace(">", "").split(",")
            r, g, b = int(r), int(g), int(b)
        else:
            name = "player1"
            r, g, b = 255, 0, 0
        player = database.Player(name, addr)
        database.s.merge(player)
        database.s.commit()
        addr_str = f'({addr[0]},{addr[1]})'
        data = database.s.query(database.Player).filter(database.Player.adress == addr_str)
        for user in data:
            player = LocalPlayer(user.id, user.name, (r, g, b), client_socket, addr_str)
            players[user.id] = player
    except BlockingIOError:
        pass


def handle_player_messages(players):
    for player_id in list(players):
        visible_bacteries[player_id] = []
        
        if players[player_id].socket is None:
            if tick % 400 == 0:
                vector = f"<{random.randint(-1, 1)},{random.randint(-1, 1)}>"
                players[player_id].changed_speed(vector)
            continue
        player = players[player_id]
        try:
            data = player.socket.recv(1024).decode()
            print(f'получено: {data}')
            players[player_id].changed_speed(data)
        except BlockingIOError:
            pass
        except (ConnectionResetError, OSError):
            player.socket.close()
            del players[player_id]
            database.s.query(database.Player).filter(database.Player.id == player_id).delete()
            database.s.commit()
            print('сокет закрыт')

def create_mobs(players):
    names = RussianNames(count=MOBS_COUNT*2, patronymic=False, surname=False, rare=True)
    names = list(set(names))
    for mobs in range(MOBS_COUNT):
        mob = database.Player(names[mobs], None)
        mob.color = random.choice(colors)
        mob.x, mob.y = random.randint(0, SERVER_W), random.randint(0, SERVER_H)
        mob.size = random.randint(10, 100)
        mob.x_speed = random.randint(-1, 1)
        mob.y_speed = random.randint(-1, 1)
        database.s.add(mob)
        database.s.commit()
        local_player = LocalPlayer(mob.id, mob.name, mob.color, None, None)
        local_player.size = mob.size
        local_player.x = mob.x
        local_player.y = mob.y
        local_player.speedx = mob.x_speed
        local_player.speedy = mob.y_speed
        players[mob.id] = local_player

def create_food(foods):
    for i in range(FOOD_COUNT):
        food = Food(random.randint(0, SERVER_W), random.randint(0, SERVER_H), random.choice(colors))
        foods.append(food)


def main():
    global tick
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
    main_socket.bind(("localhost", 22867))
    main_socket.setblocking(False)
    main_socket.listen(5)
    print('сокет создан')

    players = {}
    foods = []
    create_food(foods)
    create_mobs(players)

    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption('сервер')
    clock = pygame.time.Clock()
    server_run = True
    font = pygame.font.Font(None, 18) 

    while server_run:
        tick += 1
        clock.tick(FPS)

        accept_new_clients(main_socket, players)
        handle_player_messages(players)
        for id in list(players):
            visible_bacteries[id] = []
        payers = list(players.items())
        for i in range(len(payers)):
            for food in foods:
                hero : LocalPlayer = payers[i][1]
                dist_x = food.x - hero.x
                dist_y = food.y - hero.y
                if abs(dist_x) <= hero.w_vision//2+food.size and abs(dist_y) <= hero.h_vision//2+food.size:
                    distance = math.sqrt(dist_x**2 + dist_y**2)
                    if distance <= hero.size and food.size*1.1 <= hero.size:
                        hero.size = math.sqrt(hero.size**2 + food.size**2)
                        food.size = 0
                        foods.remove(food)
                    if hero.socket is not None and food.size > 0:
                        x, y = round(dist_x), round(dist_y)
                        size = round(food.size)
                        color = food.color
                        visible_bacteries[hero.id].append(f"{x} {y} {size} {color}")

            for j in range(i+1, len(payers)):
                hero1 : LocalPlayer = payers[i][1]
                hero2 : LocalPlayer = payers[j][1]
                dist_x = hero2.x - hero1.x
                dist_y = hero2.y - hero1.y
                if abs(dist_x) <= hero1.w_vision//2+hero2.size and abs(dist_y) <= hero1.h_vision//2+hero2.size:
                    distance = math.sqrt(dist_x**2 + dist_y**2)
                    if distance <= hero1.size and hero2.size*1.1 <= hero1.size:
                        pass 
                    x_ = round(dist_x)
                    y_ = round(dist_y)
                    size_ = round(hero2.size)
                    color_ = hero2.color
                    nickname_ = hero2.name
                    data = f"{x_} {y_} {size_} {color_} {nickname_}"
                    visible_bacteries[hero1.id].append(data)

                if abs(dist_x) <= hero2.w_vision//2+hero1.size and abs(dist_y) <= hero2.h_vision//2+hero1.size:
                    distance = math.sqrt(dist_x**2 + dist_y**2)
                    if distance <= hero2.size and hero1.size*1.1 <= hero2.size:
                        pass 
                    x_ = round(-dist_x)
                    y_ = round(-dist_y)
                    size_ = round(hero1.size)
                    color_ = hero1.color
                    nickname_ = hero1.name
                    data = f"{x_} {y_} {size_} {color_} {nickname_}"
                    visible_bacteries[hero2.id].append(data)

        for id in list(players):
            if players[id].socket is None:
                continue
            visible_bacteries[id] = f"<{round(players[id].size)},{','.join(visible_bacteries[id])}>"
            try: 
                players[id].socket.send(visible_bacteries[id].encode())
            except ConnectionResetError:
                pass
                

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                server_run = False

        screen.fill("black")
        for id in players:
            
            player = players[id]
            x = player.x * W//SERVER_W
            y = player.y * H//SERVER_H
            size = player.size * W//SERVER_W
            pygame.draw.circle(screen, player.color, (x, y), size)
            nickname = font.render(player.name, True, "white")
            nickname_rect = nickname.get_rect(center = (x, y - size - 10))
            screen.blit(nickname, nickname_rect)
            players[id].update()
        pygame.display.flip()
        
    pygame.quit()
    main_socket.close()
    database.s.query(database.Player).delete() 
    database.s.commit()


if __name__ == "__main__":
    main()
