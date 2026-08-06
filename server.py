import socket
import time
import database


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
        self.abf = 1
        self.speedx = 0
        self.speedy = 0
        


main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
main_socket.bind(("localhost", 22867))
main_socket.setblocking(False)
main_socket.listen(5)
print('сокет создан')

players = {}


while True:
    try:
        client_socket, addr = main_socket.accept()
        print('подключился', addr)
        client_socket.setblocking(False)
        player = database.Player('player1', addr)
        database.s.merge(player)
        database.s.commit()
        addr = f'({addr[0]},{addr[1]})'
        data = database.s.query(database.Player).filter(database.Player.adress==addr)
        for user in data:
            player = LocalPlayer(user.id, "player1", client_socket, addr)
            players[user.id] = player


    except BlockingIOError:
        pass

    for id in list(players):
        try:
            data = players[id].recv(1024).decode()
            print(f'получено: {data}')

        except BlockingIOError:
            pass

        except (ConnectionResetError, Exception):
            players[id].socket.close()
            del players[id]
            database.s.query(database.Player).filter(database.Player.adress==addr).delete()
            database.s.commit()
            print('сокет закрыт')
    