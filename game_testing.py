"""
This game was created juring my first semester at college to experiment
with tkinter and keyboard input in python.
"""

from tkinter import *
import time, cmath, math

"""
The player class allows the user to control a circle and move it around
the screen.
"""
class player:
    def __init__(self, x, y, width, height, canvas):
        self.mhp = 10
        self.hp = self.mhp
        self.mx = 0
        self.my = 0
        self.press_left = 0
        self.press_right = 0
        self.press_up = 0
        self.press_down = 0
        
        self.speed = 4
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.canvas = canvas
        self.box = canvas.create_oval(x, y, x+width, y+height)
        self.hp_box = canvas.create_rectangle(x, y-5, x+width, y-2)

        self.canvas.bind('a', self.left)
        self.canvas.bind('<KeyRelease-a>', self.release_left)
        self.canvas.bind('d', self.right)
        self.canvas.bind('<KeyRelease-d>', self.release_right)
        self.canvas.bind('w', self.up)
        self.canvas.bind('<KeyRelease-w>', self.release_up)
        self.canvas.bind('s', self.down)
        self.canvas.bind('<KeyRelease-s>', self.release_down)
        self.canvas.focus_set()

    def control(self):
        """Handles the movement for the player instance."""
        speed = self.speed
        if self.mx != 0 and self.my != 0:
            speed *= .7
        self.x += self.mx* speed
        self.y += self.my* speed
        self.canvas.move(self.box, self.mx * speed, self.my * speed)

        self.canvas.coords(self.hp_box, self.x, self.y-5,
                           self.x+(self.width*self.hp/self.mhp), self.y-2)

        
    def left(self, event):
        self.press_left = 1
        self.mx = -1

    def release_left(self, event):
        self.press_left = 0
        if self.press_right == 1:
            self.mx = 1
        else:
            self.mx = 0

    def right(self, event):
        self.press_right = 1
        self.mx = 1

    def release_right(self, event):
        self.press_right = 0
        if self.press_left == 1:
            self.mx = -1
        else:
            self.mx = 0

    def up(self, event):
        self.press_up = 1
        self.my = -1

    def release_up(self, event):
        self.press_up = 0
        if self.press_down == 1:
            self.my = 1
        else:
            self.my = 0

    def down(self, event):
        self.press_down = 1
        self.my = 1

    def release_down(self, event):
        self.press_down = 0
        if self.press_up == 1:
            self.my = -1
        else:
            self.my = 0

"""
A rectangular projectile that damages the player.
"""
class danger:
    def __init__(self, x, y, width, height, speed, angle, canvas):
        x -= math.cos(math.radians(angle))*10
        y -= math.cos(math.radians(angle))*10
        self.timer = 0
        self.x = x
        self.y = y
        self.vx = x#virtual x
        self.vy = y
        self.startx = x
        self.starty = y
        self.newxy = []
        
        self.width = width
        self.height = height
        self.direction = angle
        self.speed = speed
        self.canvas = canvas
        self.angle = cmath.exp(math.radians(angle)*1j)
        self.xy = [(0, 0), (width, 0), (width, height), (0, height)]
        self.box = canvas.create_polygon(self.xy)
            
    def movement(self):
        """Moves the projectile at a set angle."""
        self.x += self.speed * math.cos(0)
        self.y += self.speed * math.sin(0)
        
        self.newxy = []
        change = complex(self.startx, self.starty)
        self.xy = [(self.x, self.y), \
                   (self.x+self.width, self.y),\
                   (self.x+self.width, self.y+self.height), \
                   (self.x, self.y+self.height)]
        for x, y in self.xy:
            v = self.angle * (complex(x,y)-change) + change
            self.newxy.append(v.real)
            self.newxy.append(v.imag)
        self.canvas.coords(self.box, *self.newxy)
        
        self.vx += self.speed * math.cos(math.radians(self.direction))
        self.vy += self.speed * math.sin(math.radians(self.direction))
        self.timer += 1
        return self.timer

    def collision(self, x, y, width, height):
        """Checks for collisions with the object."""
        for i in range(0, len(self.newxy), 2):
            if self.newxy[i] > x and self.newxy[i] < x + width and\
                self.newxy[i+1] > y and self.newxy[i+1] < y + height:
                self.timer = -50
                break

        if self.timer < 0:
            return 1
        return 0

"""
Spawns instances of danger in a choosen direction.
"""
class spawner:
    def __init__(self, x, y, width, height, often, angle, canvas):
        self.charge = 0
        self.list = []
        self.destroy = 50

        self.x = x
        self.y = y
        self.often = often
        self.angle = angle
        self.canvas = canvas
        self.box = canvas.create_rectangle(x, y, x+width, y+height)

    def spawn(self):
        """
            Creates instances of the danger class and adds them to a list.
            Also destroys individual instances of danger at set intervals.
        """ 
        if self.charge < self.often:
            self.charge += 1
        else:
            self.charge = 0
            self.list.append(danger(self.x + 22,self.y + 16,32,16,5, self.angle,
                                    self.canvas))
        for i in self.list:
            check = i.movement()
            if check > self.destroy or check < 0:
                self.list.remove(i)
                self.canvas.delete(i.box)
                del i

"""
A spiky block that moves along a given path. Deals damage to the player.
"""
class mover:
    def __init__(self, x, y, width, height, spike, speed, canvas, *path):
        self.charge = 0
        self.path = path
        self.index = 0

        self.cx = 0
        self.cy = 0
        self.mx = 0
        self.my = 0
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.canvas = canvas
        self.speed = speed
        
        self.xy = []
        # Creates tuples of x/y points to surround the rectangle with triangles.
        for i in range(0, 7):
            self.xy.append( (x+width*(i/6), y-(i%2*spike)) )
        for i in range(1, 7):
            self.xy.append( (x+width+(i%2*spike), y+height*(i/6)) )
        for i in range(1, 7):
            self.xy.append( (x+width*((6-i)/6), y+height+(i%2*spike)) )
        for i in range(1, 7):
            self.xy.append( (x-(i%2*spike), y+height*((6-i)/6)) )

        self.xy.append( (x+width, y) )
        self.xy.append( (x+width, y+height) )
        self.xy.append( (x, y+height) )
            
        self.box = canvas.create_polygon(self.xy, fill = '', outline = 'black')

    def pathing(self):
        """Moves the instance along the given path"""
        if self.cx < self.path[self.index]:
            self.mx = 1
        elif -self.cx > self.path[self.index]:
            self.mx = -1
        else:
            self.mx = 0
            
        if self.cy < self.path[self.index+1]:
            self.my = 1
        elif -self.cy > self.path[self.index+1]:
            self.my = -1
        else:
            self.my = 0
            
        if self.cx >= abs(self.path[self.index]) and\
           self.cy >= abs(self.path[self.index+1]):
            self.cx = 0
            self.cy = 0
            self.index += 2
            if self.index > len(self.path)-1:
                self.index = 0
        else:
            if self.cx < abs(self.path[self.index]):
                self.cx += 1
            if self.cy < abs(self.path[self.index+1]):
                self.cy += 1

        self.x += self.speed * self.mx
        self.y += self.speed * self.my
        self.canvas.move(self.box, self.speed * self.mx, self.speed * self.my)

    def collision(self, x, y, width, height):
        """Checks collisions"""
        if self.x + self.width > x and self.x < x + width\
           and self.y + self.height > y and self.y < y + height:
            return 1
        return 0

def main():
    window = Tk()
    canvas = Canvas(window, width = 640, height = 480)

    p1 = player(100,100,32,32, canvas)

    d = [spawner(10, 100, 32, 32, 15, 45,canvas),
         spawner(310, 300, 32, 32, 40, 180,canvas),
         spawner(10, 150, 32, 32, 32, 0,canvas)
        ]
    e = [mover(100, 420, 32, 32, 6, 4, canvas, 40, 0, 0, -15, -40, 0, 0, 15),
         mover(500, 50, 32, 32, 6, 5, canvas, 0, 70, 12, 0, 0, -70, -12, 0)
        ]
    canvas.pack()

    while(True):
        p1.control()

        #Check if player collides with objects of class danger
        for i in range(0, len(d)):
            for k in d[i].list:
                if k.collision(p1.x, p1.y, p1.width, p1.height) == 1:
                    p1.hp -= 1
                    if p1.hp <= 0:
                        canvas.delete(p1.box)
                        canvas.delete(p1.hp_box)
            d[i].spawn()

        #Check if player collides with objects of class mover
        for i in e:
            i.pathing()
            if i.collision(p1.x, p1.y, p1.width, p1.height) == 1:
                p1.hp -= .2
                if p1.hp <= 0:
                    canvas.delete(p1.box)
                    canvas.delete(p1.hp_box)
            
        time.sleep(.02)
        window.update_idletasks()
        window.update()


if __name__ == '__main__':
    main()
