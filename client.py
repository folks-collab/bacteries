import socket
import pygame
import time
import math
import menu

class Grid:
    def __init__(self, screen, color):
        self.screen = screen
        self.color = color
        self.x = 0
        self.y = 0 
        self.start_size = 200
        self.size = self.start_size

    def update(self, params:list[int]):
        x, y, l = params
        self.size = self.start_size//l
        self.x = -self.size + (-x) % self.size
        self.y = -self.size + (-y) % self.size
        

    def draw(self):
        for i in range(WEIGHT // self.size + 2):
            pygame.draw.line(
                self.screen, 
                self.color,
                (self.x + i * self.size, 0),
                (self.x + i * self.size, HEIGHT),
                1
            )
        for i in range(HEIGHT // self.size + 2):
            pygame.draw.line(
                self.screen, 
                self.color,
                (0, self.y + i * self.size),
                (WEIGHT, self.y + i * self.size),
                1
            )


def connect_to_server():
    global main_socket, buffer
    buffer = 1024
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
    main_socket.connect(("localhost", 22867))
    print(color)
    main_socket.send((f"color:<{name},{color[0]},{color[1]},{color[2]}>").encode())

    
def disable():
    global state
    state = "game"
    connect_to_server()
    main_menu.disable()

def set_name(value):
    global name
    name = value

def set_color(value):
    global color
    color = value

pygame.init()

HEIGHT = 600
WEIGHT = 800
CC = (WEIGHT//2, HEIGHT//2)
old = (0,0)
radius = 30
fps = 100
ck = pygame.time.Clock()
buffer = 1024


name = "player1"
color = (255, 0, 0)
main_socket = None
screen = pygame.display.set_mode((WEIGHT, HEIGHT))
main_menu = menu.Menu(screen, "Меню")
main_menu.add.text_input("Имя: ", default="player1", onchange=set_name)
main_menu.add.color_input("Цвет: ", default=(255, 0, 0), color_type='rgb', onchange=set_color)
button1 = main_menu.add.button("Играть", disable)
button2 = main_menu.add.button("Выход", exit)
state = "menu"
pygame.display.set_caption('бактерии')
run = True


def created_msg(text, x, y):
    font = pygame.font.SysFont("comic sans", 32)
    msg = font.render(text, True, '#000000')
    screen.blit(msg, (x,y))

def find(vector:str):
    global buffer
    l_index = vector.find('<')
    r_index = vector.find('>')
    if l_index < r_index and l_index>=0 :
        result = vector[l_index+1:r_index]
        if result:
            result = result.split(",")
            return result
    buffer = int(buffer*1.5)
    return []

def draw_enemies(enemies:list):
    for enemy in enemies:
        try:
            data= enemy.split(" ")
            x = int(data[0])
            y = int(data[1])
            size = int(data[2])
            color = data[3]
            pygame.draw.circle(screen, color, (CC[0]+x, CC[1]+y), size)
            if len(data) > 4:
                created_msg(data[4], CC[0]+x, CC[1]+y)
        except:
            pass

grid = Grid(screen, "#5C4822")


while run:
    events = pygame.event.get()
    ck.tick(fps)
    print(buffer)
    for event in events:
        if pygame.mouse.get_focused() and state == "game":
            pos = pygame.mouse.get_pos()
            
            vector = (pos[0]-CC[0], pos[1]-CC[1])
            lenv = math.sqrt(vector[0]**2 + vector[1]**2)
            vector = (vector[0]/lenv, vector[1]/lenv)
            if lenv <= radius:
                vector = (0,0)
                
            if vector != old:
                main_socket.send(f"<{vector[0]},{vector[1]}>".encode())
                old = vector
        
        if event.type == pygame.QUIT:
            run = False
            main_socket.close()
            main_socket = None
    if state == "game":
        screen.fill("#726C6B")
        grid.draw()
        created_msg("player1", WEIGHT//2, HEIGHT//2 - radius - 30)
        try: 
            raw_data = main_socket.recv(buffer)
            print(len(raw_data))
        except (ConnectionResetError, ConnectionAbortedError):
            main_socket.close()
            main_socket = None
            state = "menu"
            main_menu.enable()
            continue
        

        data = find(raw_data.decode())

        if not data:
            continue

        bacteries = data[1:]
        data = list(map(int, data[0].split()))
        radius = data[0]
        params = data[1:]
        grid.update(params)
        
        
        pygame.draw.circle(screen, '#ff0000', (WEIGHT//2, HEIGHT//2), radius)
        pygame.draw.line(screen, '#ff0000', (WEIGHT//2, HEIGHT//2), pygame.mouse.get_pos(), 3)
        draw_enemies(bacteries)

    main_menu.flip(events)
    pygame.display.flip()
    
pygame.quit()
