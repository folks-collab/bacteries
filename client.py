import socket
import pygame
import time
import math
import menu

def connect_to_server():
    global main_socket
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
    l_index = vector.find('<')
    r_index = vector.find('>')
    if l_index < r_index and l_index>=0 :
        result = vector[l_index+1:r_index]
        if result:
            result = result.split(",")
            return result
    return []

def draw_enemies(enemies:list):
    print(enemies)
    for enemy in enemies:
        x, y, size, color = enemy.split(" ")
        x = int(x)
        y = int(y)
        size = int(size)
        pygame.draw.circle(screen, color, (CC[0]+x, CC[1]+y), size)

        

while run:
    events = pygame.event.get()
    ck.tick(fps)

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

    if state == "game":
        screen.fill('#cccccc')
        created_msg("player1", WEIGHT//2, HEIGHT//2 - radius - 30)
        data = main_socket.recv(1024).decode()
        print(data)
        data = find(data)
        print(data)
        pygame.draw.circle(screen, '#ff0000', (WEIGHT//2, HEIGHT//2), radius)
        pygame.draw.line(screen, '#ff0000', (WEIGHT//2, HEIGHT//2), pygame.mouse.get_pos(), 3)
        draw_enemies(data)

    main_menu.flip(events)
    pygame.display.flip()
    
pygame.quit()
