import socket
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


def accept_new_clients(main_socket, players):
    try:
        client_socket, addr = main_socket.accept()
        print('подключился', addr)
        client_socket.setblocking(False)
        player = database.Player('player1', addr)
        database.s.merge(player)
        database.s.commit()
        addr_str = f'({addr[0]},{addr[1]})'
        data = database.s.query(database.Player).filter(database.Player.adress == addr_str)
        for user in data:
            player = LocalPlayer(user.id, "player1", client_socket, addr_str)
            players[user.id] = player
    except BlockingIOError:
        pass


def handle_player_messages(players):
    for player_id in list(players):
        player = players[player_id]
        try:
            data = player.socket.recv(1024).decode()
            print(f'получено: {data}')
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

    while True:
        accept_new_clients(main_socket, players)
        handle_player_messages(players)


if __name__ == "__main__":
    main()
