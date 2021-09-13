from tkinter import Canvas, NW, NE, Tk
import numpy as np
import math
import re

STEP = 10                   # Шаг перемещения
STEP_DEG = 10               # Шаг поворота
STEP_SCALE = 0.125          # Шаг масштаба
WIDTH = 1200                 # Ширина рендера
HEIGHT = 600                # Высота рендера
K = (math.pi / 180) * 45    # Градус проецирования
BLACK = '#000000'
WHITE = '#fffafa'
SILVER = '#c0c0c0'

class model:
    #Класс, описывающий модель и и ее поведение

    def __init__(self, name, type):
        self.node = []
        self.edge = []

        if type == 'txt':
            self.node = self.readFile(name + '/node.txt')   #Вершины
            self.edge = self.readFile(name + '/edge.txt')   #Ребра
        elif type == 'obj':
            self.readObj(name + '.obj')

        #Параметры объекта
        self.coordinates = np.array([0, 0, 0, 1])   # x y z
        self.degrees = np.array([0, 0, 0, 0])       # 0x 0y 0z
        self.size = np.array([1, 1, 1, 1])          # 0x 0y 0z
        self.coordinates_copy = np.array([0, 0, 0, 1])   # x y z
        self.degrees_copy = np.array([0, 0, 0, 0])       # 0x 0y 0z
        self.size_copy = np.array([1, 1, 1, 1])          # 0x 0y 0z

    def readObj(self, name):
        f = open(name, 'r')
        node = []
        edge = []

        for l in f:
            if l[0] == 'v':
                temp = (re.sub('\s+', ' ', l[2:]) + '1').split(' ')
                for i in range(len(temp)):
                    temp[i] = float(temp[i])
                node.append(temp)
            if l[0] == 'f':
                temp = (re.sub('\s+', ' ', l[2:-1])).split(' ')
                for i in range(len(temp)):
                    temp[i] = int(temp[i])
                edge.append([temp[0], temp[1]])
                edge.append([temp[0], temp[2]])
                edge.append([temp[1], temp[2]])
        
        #оставляем только уникальные ребра
        unique = []
        for item in edge:
            if sorted(item) not in unique:
                unique.append(sorted(item))

        self.node = np.array(node)
        self.edge = np.array(unique) - 1
        #print(f'{self.edge}\n')

    def readFile(self, name):
        array = []
        f = open(name, 'r')
        for l in f:
            temp = l.rstrip().split(' ')
            for i in range(len(temp)):
                temp[i] = int(temp[i])
            array.append(temp)
        return np.array(array)

    def c(self, shifter):
        self.coordinates = self.coordinates + shifter
        self.coordinates_copy = self.coordinates_copy + shifter

    def d(self, shifter):
        self.degrees = (self.degrees + shifter) % 360
        self.degrees_copy = (self.degrees_copy + shifter) % 360

    def s(self, shifter):
        
        tempor = self.size_copy + shifter
        for i in tempor:
            if i < STEP_SCALE:
                return
        
        self.size = self.size + shifter
        self.size_copy = self.size_copy + shifter
    
    def translate(self, node):
        matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [self.coordinates[0], self.coordinates[1], self.coordinates[2], self.coordinates[3]]
        ])

        temp = []
        for e in node:
            temp.append(np.matmul(e, matrix))
        A.node = np.array(temp)
        self.coordinates = np.array([0, 0, 0, 1])

        return np.array(temp)
    
    def rotate(self, node):
        deg = self.degrees * (math.pi / 180)

        matrix0x = np.array([
            [1, 0, 0, 0],
            [0, math.cos(deg[0]), math.sin(deg[0]), 0],
            [0, -math.sin(deg[0]), math.cos(deg[0]), 0],
            [0, 0, 0, 1]
        ])

        matrix0y = np.array([
            [math.cos(deg[1]), 0, -math.sin(deg[1]), 0],
            [0, 1, 0, 0],
            [math.sin(deg[1]), 0, math.cos(deg[1]), 0],
            [0, 0, 0, 1]
        ])

        matrix0z = np.array([
            [math.cos(deg[2]), math.sin(deg[2]), 0, 0],
            [-math.sin(deg[2]), math.cos(deg[2]), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        temp = []
        for e in node:
            temp.append(np.matmul(np.matmul(np.matmul(e, matrix0x), matrix0y), matrix0z))
        
        A.node = np.array(temp)
        self.degrees = np.array([0, 0, 0, 0])
        
        return np.array(temp)
    
    def scale(self, node):
        matrix = np.array([
            [self.size[0], 0, 0, 0],
            [0, self.size[1], 0, 0],
            [0, 0, self.size[2], 0],
            [0, 0, 0, 1]
        ])

        temp = []
        for e in node:
            temp.append(np.matmul(e, matrix))
        
        A.node = np.array(temp)
        self.size = np.array([1, 1, 1, 1])
            
        return np.array(temp)

# Объект
A = model('tinker', 'obj')
chooser = 1 #режим работы
directioner = 'q'#выбор направления
jst = []

# Проецирование
def proect(node):
    # Косоугольное
    matrix = []
    matrix.append(np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [-math.cos(K), -math.sin(K), 0, 0],
        [0, 0, 0, 1]
    ]))

    # Перспективное
    matrix.append(np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, -0.01],
        [0, 0, 0, 1]
    ]))


    request = []
    for e in node:
        temp = np.matmul(e, matrix[0])
        #temp = temp / (temp[3])
        #print(temp)
        request.append(temp)

    #print(np.array(request))
    return np.array(request)

# Обновление экрана
def update(c):
    global chooser, directioner, jst
    
    node = proect(A.scale(A.rotate(A.translate(A.node))))
    
    jst = []
    
    c.delete("all")
    for e in A.edge:
        jst.append(c.create_line(node[e[0]][0] + WIDTH/2, -node[e[0]][1] + HEIGHT/2, 
                      node[e[1]][0] + WIDTH/2, -node[e[1]][1] + HEIGHT/2, 
                      fill=WHITE))

    axes = [
        [0, 0, 0, 1],
        [WIDTH / 3, 0, 0, 1],
        [0, WIDTH / 3, 0, 1],
        [0, 0, WIDTH / 3, 1]
    ]

    directions = [
        [0, 1],
        [0, 2],
        [0, 3]
    ]

    axes = proect(axes)

    for e in directions:
        c.create_line(axes[e[0]][0] + WIDTH / 2, -axes[e[0]][1] + HEIGHT / 2,
                      axes[e[1]][0] + WIDTH / 2, -axes[e[1]][1] + HEIGHT / 2,
                      fill=SILVER)

    c.create_text(5, 5, anchor=NW, fill=SILVER,
                  text="coordinates: ({}, {}, {})\n".format(A.coordinates_copy[0], A.coordinates_copy[1], A.coordinates_copy[2]) +
                  "degrees: ({}, {}, {})\n".format(A.degrees_copy[0], A.degrees_copy[1], A.degrees_copy[2]) +
                  "size: ({}, {}, {})".format(A.size_copy[0], A.size_copy[1], A.size_copy[2])
                  )
    if chooser == 1:
        c.create_text(WIDTH - 5, 5, anchor=NE, fill=SILVER, text='mode (1, 2, 3): shift')
    elif chooser == 2:
        c.create_text(WIDTH - 5, 5, anchor=NE, fill=SILVER, text='mode (1, 2, 3): rotate')
    elif chooser == 3:
        c.create_text(WIDTH - 5, 5, anchor=NE, fill=SILVER, text='mode (1, 2, 3): scale')
    elif chooser == 4:
        c.create_text(WIDTH - 5, 5, anchor=NE, fill=SILVER, text='mode (1, 2, 3): mirror')
    
    if directioner == 'q':
        c.create_text(WIDTH - 5, 15, anchor=NE, fill=SILVER, text='direction (q, w, e): x')
    elif directioner == 'w':
        c.create_text(WIDTH - 5, 15, anchor=NE, fill=SILVER, text='direction (q, w, e): y')
    elif directioner == 'e':
        c.create_text(WIDTH - 5, 15, anchor=NE, fill=SILVER, text='direction (q, w, e): z')
    #return node
    return jst

def mirror(variant, c):
    matrix = []

    matrix.append(np.array([
        [-1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]))

    matrix.append(np.array([
        [1, 0, 0, 0],
        [0, -1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]))

    matrix.append(np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, -1, 0],
        [0, 0, 0, 1]
    ]))

    temp = A.scale(A.translate(A.rotate(A.node)))
    node = []
    for e in temp:
        node.append(np.matmul(e, matrix[variant]))

    node = proect(node)

    for e in A.edge:
        c.create_line(node[e[0]][0] + WIDTH/2, -node[e[0]][1]+HEIGHT/2, 
                      node[e[1]][0]+WIDTH/2, -node[e[1]][1]+HEIGHT/2, 
                      fill=SILVER)

def mode(event, c):
    global chooser, directioner
    if event.keysym.isdigit():
        chooser = int(event.keysym)
    else:
        directioner = event.keysym
    update(c)

def changer(event, c):
    global chooser, directioner
    if event.keysym == 'Up':
        if chooser == 1:
            if directioner == 'q':
                A.c([STEP, 0, 0, 0])
            elif directioner == 'w':
                A.c([0, STEP, 0, 0])
            elif directioner == 'e':
                A.c([0, 0, STEP, 0])
        elif chooser == 2:
            if directioner == 'q':
                A.d([STEP_DEG, 0, 0, 0])
            elif directioner == 'w':
                A.d([0, STEP_DEG, 0, 0])
            elif directioner == 'e':
                A.d([0, 0, STEP_DEG, 0])
        elif chooser == 3:
            if directioner == 'q':
                A.s([STEP_SCALE, 0, 0, 0])
            elif directioner == 'w':
                A.s([0, STEP_SCALE, 0, 0])
            elif directioner == 'e':
                A.s([0, 0, STEP_SCALE, 0])
        elif chooser == 4:
            if directioner == 'q':
                mirror(0, c)
            elif directioner == 'w':
                mirror(1, c)
            elif directioner == 'e':
                mirror(2, c)
    elif event.keysym == 'Down':
        if chooser == 1:
            if directioner == 'q':
                A.c([-STEP, 0, 0, 0])
            elif directioner == 'w':
                A.c([0, -STEP, 0, 0])
            elif directioner == 'e':
                A.c([0, 0, -STEP, 0])
        elif chooser == 2:
            if directioner == 'q':
                A.d([-STEP_DEG, 0, 0, 0])
            elif directioner == 'w':
                A.d([0, -STEP_DEG, 0, 0])
            elif directioner == 'e':
                A.d([0, 0, -STEP_DEG, 0])
        elif chooser == 3:
            if directioner == 'q':
                A.s([-STEP_SCALE, 0, 0, 0])
            elif directioner == 'w':
                A.s([0, -STEP_SCALE, 0, 0])
            elif directioner == 'e':
                A.s([0, 0, -STEP_SCALE, 0])
        elif chooser == 4:
            if directioner == 'q':
                mirror(0, c)
            elif directioner == 'w':
                mirror(1, c)
            elif directioner == 'e':
                mirror(2, c)
    if chooser != 4:
        update(c)  

def anim(root, event, c, i = 0):
    global jst
    if i == 2:
        #call_anim(root, event, c)
        return
    A.c([0, STEP * (i + 1), 0, 0])
    node = proect(A.scale(A.rotate(A.translate(A.node))))
    for e in range(len(jst)):
        c.coords(jst[e], node[A.edge[e][0]][0] + WIDTH/2, -node[A.edge[e][0]][1] + HEIGHT/2, 
                 node[A.edge[e][1]][0] + WIDTH/2, -node[A.edge[e][1]][1] + HEIGHT/2)
    root.after(500, anim(root, event, c, i + 1))

def call_anim(root, event, c, i = 0):
    global jst
    if i == 2:
        return
    A.c([0, -STEP * (i + 1), 0, 0])
    node = proect(A.scale(A.rotate(A.translate(A.node))))
    for e in range(len(jst)):
        c.coords(jst[e], node[A.edge[e][0]][0] + WIDTH/2, -node[A.edge[e][0]][1] + HEIGHT/2, 
                 node[A.edge[e][1]][0] + WIDTH/2, -node[A.edge[e][1]][1] + HEIGHT/2)
    root.after(500, call_anim(root, event, c, i + 1))



root = Tk()
root.geometry(str(WIDTH) + 'x' + str(HEIGHT) + f'+100+50')
root.resizable(width=False, height=False)
    
c = Canvas(root, width=WIDTH, height=HEIGHT, bg='black', highlightthickness=0)
c.place(x=0, y=0)
update(c)

root.bind('<KeyPress-1>', lambda event: mode(event, c))
root.bind('<KeyPress-2>', lambda event:  mode(event, c))
root.bind('<KeyPress-3>', lambda event: mode(event, c))
root.bind('<KeyPress-4>', lambda event: mode(event, c))
root.bind('<KeyPress-q>', lambda event: mode(event, c))
root.bind('<KeyPress-w>', lambda event: mode(event, c))
root.bind('<KeyPress-e>', lambda event: mode(event, c))
root.bind('<KeyPress-Up>', lambda event: changer(event, c))
root.bind('<KeyPress-Down>', lambda event: changer(event, c))
root.bind('<KeyPress-space>', lambda event: anim(root, event, c))

root.mainloop()
