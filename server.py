import socket
import database
import pygame


pygame.init()


SERVER_W, SERVER_H = 4000, 4000
W, H = 300, 300
FPS = 100


class LocalPlayer:
    def __init__(self, id, name, socket, adress):
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

    def update(self):
        self.y += self.speedy
        self.x += self.speedx
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
        else:
            name = "player1"
            r, g, b = 255, 0, 0
        player = database.Player(name, addr)
        database.s.merge(player)
        database.s.commit()
        addr_str = f'({addr[0]},{addr[1]})'
        data = database.s.query(database.Player).filter(database.Player.adress == addr_str)
        for user in data:
            player = LocalPlayer(user.id, user.name, client_socket, addr_str)
            players[user.id] = player
    except BlockingIOError:
        pass


def handle_player_messages(players):
    for player_id in list(players):
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


def main():
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
    main_socket.bind(("localhost", 22867))
    main_socket.setblocking(False)
    main_socket.listen(5)
    print('сокет создан')

    players = {}

    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption('сервер')
    clock = pygame.time.Clock()
    server_run = True
    font = pygame.font.Font(None, 18) 

    while server_run:
        clock.tick(FPS)
        accept_new_clients(main_socket, players)
        handle_player_messages(players)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                server_run = False

        screen.fill("black")
        for id in players:
            player = players[id]
            x = player.x * W//SERVER_W
            y = player.y * H//SERVER_H
            size = player.size * W//SERVER_W
            pygame.draw.circle(screen, "orange", (x,y), size)
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
