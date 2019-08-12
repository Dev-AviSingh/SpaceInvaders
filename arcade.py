import tkinter as tk
from threading import Thread
from time import time,sleep
from random import randint, choice
import math
from PIL import Image, ImageTk
import Constants
import Entities

class Box(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __and__(self, r2):
        return (abs(self.x - r2.x) * 2 < (self.width + r2.width)) and (abs(self.y - r2.y) * 2 < (self.height + r2.height))
        # The above method is more efficient
        #return not (r2.x > (self.x + self.width) or (r2.x + r2.width) < self.x or r2.y > (self.y + self.height) or (r2.y + r2.height) < self.y)


class Bullet(Box):
    def __init__(self, canvas = None, x = 0, y = 0, score = None):
        self.x = x
        self.y = y

        self.width = 2
        self.height = 10

        self.canvas = canvas

        self.scoreBoard = score

        self.velocity = -10

        self.sprite = self.canvas.create_image(x, y, image = ImageTk.PhotoImage(Image.open(Constants.resourcePath('./Assets/Bullet/Bullet.png'))))

        sprite1 = ImageTk.PhotoImage(Image.open(Constants.resourcePath('./Assets/Bullet/Bullet.png')).resize((self.width, self.height), Image.ANTIALIAS))
        self.currentAnimation = Animation(canvas = self.canvas, fps = 5, initialFrame = sprite1, xpos = self.x, ypos = self.y)
        self.canvas.tag_raise(self.currentAnimation.currentFrame)
        self.dead = False

    def deleteNow(self):
        self.canvas.delete(self.sprite)
        self.currentAnimation = None

    def update(self, asteroids):
        self.y += self.velocity

        for asteroid in asteroids.getAsteroidList():
            if self.__and__(asteroid):
                asteroid.reset()
                self.scoreBoard.score += 20
                self.dead = True
                break

        self.currentAnimation.update(self.x, self.y)

    def render(self):
        self.currentAnimation.render()

class Animation(object):
    def __init__(self, canvas = None, fps = 10, initialFrame = None, xpos = 0, ypos = 0):
        self.canvas = canvas
        
        self.xpos = xpos
        self.ypos = ypos

        self.xvel = 0
        self.yvel = 0

        self.frames = []
        self.frames.append(initialFrame)

        self.frameIndex = 0
        self.currentFrame = self.canvas.create_image(xpos, ypos, image = self.frames[self.frameIndex])

        self.canvas.tag_lower(self.currentFrame)

        self.lastTime = time()
        self.maxTime = 1 / fps


    def addFrame(self, frame):
        self.frames.append(frame)

    def update(self, xpos, ypos):
        self.xpos, self.ypos = self.canvas.coords(self.currentFrame)# This helps in finding the actual position of the sprite as the animation's position and the canvas sprite's position varies after resetting an asteroid, thus this is necessary, I do not know this worked but kindly do not remove this statement.

        self.xvel = xpos - self.xpos
        self.yvel = ypos - self.ypos

        self.xpos = xpos
        self.ypos = ypos


        elapsed = time() - self.lastTime
        if elapsed >= self.maxTime:
            self.lastTime - time()
            self.frameIndex += 1

            if self.frameIndex >= len(self.frames):
                self.frameIndex = 0



    def render(self):
        self.canvas.move(self.currentFrame, self.xvel, self.yvel)
        self.canvas.itemconfig(self.currentFrame, image = self.frames[self.frameIndex])

class HealthBar(object):
    def __init__(self, canvas = None, x = 0, y = 0, initialHealth = 100, maxHealth = 100):
        self.canvas = canvas
        self.x = x
        self.y = y

        self.width = 100
        self.height = 5

        self.xvel = 0
        self.yvel = 0

        self.health = initialHealth

        self.barOutline = self.canvas.create_rectangle(self.x, self.y, self.x + self.width, self.y + self.height, outline = 'white')

        self.barFill = self.canvas.create_rectangle(self.x, self.y, self.x + self.health, self.y + self.height, outline = 'white', fill = 'red')

    def update(self, newX, newY, currentHealth):
        self.xvel = newX - self.x
        self.yvel = newY - self.y

        self.x = newX
        self.y = newY

        self.health = currentHealth

    def render(self):
        self.canvas.move(self.barFill, self.xvel, self.yvel)
        self.canvas.move(self.barOutline, self.xvel, self.yvel)
        self.canvas.coords(self.barFill, self.x, self.y, self.x + self.health, self.y + self.height)

class CrashAnimation(object):
    def __init__(self, canvas = None, x = 0, y = 0, fps = 3, toTrace = None):
        self.canvas = canvas
        self.x = x
        self.y = y

        self.fps = fps
        self.toTrace = toTrace

        self.frames = []

        self.createFrames()


    def startAnimation(self):
        Thread(target = self.start, args = ()).start()

    def createFrames(self):
        for x in range(16):
            self.frames.append(ImageTk.PhotoImage(
                Image.open(Constants.resourcePath('./Assets/Explosion/{}.png').format(x))
                ))


    def start(self):
        last = time()
        maxTime = 1 / self.fps
        self.currentSprite = self.canvas.create_image(self.x, self.y, image = self.frames[0])
        for frame in self.frames:
            elapsed = time() - last
            wait = maxTime - elapsed
            if(wait > 0):
                sleep(wait)
            self.canvas.itemconfig(self.currentSprite, image = frame)
            self.canvas.move(self.currentSprite, self.toTrace.x - self.x, self.toTrace.y - self.y)
            self.x, self.y = self.toTrace.x, self.toTrace.y
            last = time()

        if self.currentSprite != None:
                self.canvas.delete(self.currentSprite)
        del self.x, self.y, self.frames, self.currentSprite


class Player(Box):
    def __init__(self, canvas = None, xPos = 0, yPos = 0, xVel = 0, yVel = 0, asteroids = None, entities = None, scoreBoard = None):
        self.canvas = canvas
        self.x = xPos
        self.y = yPos
        
        self.width = 35
        self.height = 50

        self.xVel = xVel
        self.yVel = yVel

        self.scoreBoard = scoreBoard

        self.health = 100

        self.asteroids = asteroids
        self.entities = entities

        self.firingRate = 5

        self.shooting = False

        sprite1 = ImageTk.PhotoImage(Image.open(Constants.resourcePath('./Assets/SpaceShip/Frame0.png')).resize((self.width, self.height), Image.ANTIALIAS))
        sprite2 = ImageTk.PhotoImage(Image.open(Constants.resourcePath('./Assets/SpaceShip/Frame1.png')).resize((self.width, self.height), Image.ANTIALIAS))
        sprite3 = ImageTk.PhotoImage(Image.open(Constants.resourcePath('./Assets/SpaceShip/Frame2.png')).resize((self.width, self.height), Image.ANTIALIAS))
        sprite4 = ImageTk.PhotoImage(Image.open(Constants.resourcePath('./Assets/SpaceShip/Frame3.png')).resize((self.width, self.height), Image.ANTIALIAS))
        self.currentAnimation = Animation(canvas = self.canvas, fps = 5, initialFrame = sprite1, xpos = self.x, ypos = self.y)
        self.currentAnimation.addFrame(sprite2)
        self.currentAnimation.addFrame(sprite3)
        self.currentAnimation.addFrame(sprite4)

        self.healthBar = HealthBar(canvas = self.canvas, x = self.x - 25, y = self.y - 25, maxHealth = 50)

        self.maxInterval = 1 / self.firingRate
        self.lastShoot = time()

    def update(self):
        asteroids = self.asteroids.getAsteroidList()
        
        for asteroid in asteroids:
            if(self.__and__(asteroid)):
                asteroid.reset()
                crash = CrashAnimation(canvas = self.canvas, x = self.x, y = self.y, fps = 60, toTrace = self)
                crash.startAnimation()
                self.health -= 10
                break
        if self.xVel < 0:
            if self.x <= 15:
                self.xVel = 0
        elif self.xVel > 0:
            if self.x + 15 >= Constants.windowWidth:
                self.xVel = 0

        if self.yVel < 0:
            if self.y <= 0:
                self.yVel = 0
        elif self.yVel > 0:
            if self.y + 50 >= Constants.windowHeight:
                self.yVel = 0

        if self.shooting:
            self.shootBullet()

        self.x += self.xVel
        self.y += self.yVel

        self.currentAnimation.update(self.x, self.y)
        self.healthBar.update(self.x - 50, self.y - 40, self.health)

    def render(self):
        self.currentAnimation.render()        
        self.healthBar.render()

    def getPosition(self):
        return self.x, self.y

    def moveUp(self, stop = False):
        if not stop:
            self.vely = -3
        else:
            self.vely = 0

    def moveDown(self, stop = False):
        if not stop:
            self.vely = 3
        else:
            self.vely = 0

    def moveLeft(self, stop = False):
        if not stop:
            self.velx = -3
        else:
            self.velx = 0

    def moveRight(self, stop = False):
        if not stop:
            self.velx = 3
        else:
            self.velx = 0

    def shootBullet(self):
        elapsed = time() - self.lastShoot
        wait = self.maxInterval - elapsed
        if(wait > 0):
            return
        bullet = Bullet(canvas = self.canvas, x = self.x, y = self.y, score = self.scoreBoard)
        self.entities.addBullet(bullet)

        self.lastShoot = time()

class Asteroid(Box):
    def __init__(self, canvas = None, xpos = 0, ypos = 0, velocity = 7):
        self.canvas = canvas

        self.x = xpos
        self.y = ypos

        self.width = 30
        self.height = 30

        self.velx = 0
        self.vely = velocity

        sprite1 = ImageTk.PhotoImage(Image.open(Constants.resourcePath('./Assets/Asteroid/Frame0.png')).resize((self.width, self.height), Image.ANTIALIAS))
        self.currentAnimation = Animation(canvas = self.canvas, fps = 10, initialFrame = sprite1, xpos = self.x, ypos = self.y)

        start = randint(1, 20)
        for x in range(start, 20):
            self.currentAnimation.addFrame(ImageTk.PhotoImage(Image.open(Constants.resourcePath('./Assets/Asteroid/Frame{}.png').format(x)).resize((self.width, self.height), Image.ANTIALIAS)))

        for x in range(1, start):
            self.currentAnimation.addFrame(ImageTk.PhotoImage(Image.open(Constants.resourcePath('./Assets/Asteroid/Frame{}.png').format(x)).resize((self.width, self.height), Image.ANTIALIAS)))

    def update(self):
        self.y += self.vely

        if self.y > Constants.windowHeight:
            self.x = xpos = choice(range(30, Constants.windowWidth - 30, 30))
            self.y = ypos = choice(range(-300, 0, 30))
            self.currentAnimation.update(self.x, self.y)
        self.currentAnimation.update(self.x, self.y)

    def render(self):
        self.currentAnimation.render()

    def reset(self):
        self.y = choice(range(-300, 0, 30))
        self.x = choice(range(30, Constants.windowWidth - 30, 30))
        self.currentAnimation.update(self.x, self.y)
        self.vely = 7

    def getPosition(self):
        return self.x, self.y
class Asteroids:
    def __init__(self, canvas = None, maxNumber = 20):
        self.canvas = canvas
        self.maxNumber = maxNumber

        self.asteroids = []
        self.createObstacles()

        self.asteroidVelocity = 7

    def createObstacles(self):
        for a in range(self.maxNumber):
            xpos = choice(range(30, Constants.windowWidth - 30, 30))
            ypos = choice(range(-300, Constants.windowHeight - 200, 60))
            self.asteroids.append(Asteroid(canvas = self.canvas, xpos = xpos, ypos = ypos))

    def createNewObstacle(self):
        xpos = choice(range(30, Constants.windowWidth - 30, 30))
        ypos = -300
        asteroid = Asteroid(canvas = self.canvas, xpos = xpos, ypos = ypos)
        for x in range(10):
            self.canvas.tag_raise(asteroid)
        self.asteroids.append(asteroid)

    def increaseSpeed(self):
        for asteroid in self.asteroids:
            asteroid.vely += 1

    def getAsteroidList(self):
        return self.asteroids

    def update(self):
        for asteroid in self.asteroids:
            asteroid.update()

    def render(self):
        for asteroid in self.asteroids:
            asteroid.render()

class BackGround(object):
    def __init__(self, canvas = None, speed = 2):
        self.canvas = canvas
        self.speed = speed

        self.xpos = 200
        self.ypos = 350

        self.sprite1 = self.sprite2 = ImageTk.PhotoImage(Image.open(Constants.resourcePath('./Assets/BackGround/BackGround.png')))

        self.s1 = self.canvas.create_image(self.xpos, self.ypos, image = self.sprite1)
        self.s2 = self.canvas.create_image(self.xpos, self.ypos - 700, image = self.sprite2)

        self.canvas.tag_lower(self.s1)
        self.canvas.tag_lower(self.s1)
        self.canvas.tag_lower(self.s1)
        self.canvas.tag_lower(self.s1)

        self.canvas.tag_lower(self.s2)
        self.canvas.tag_lower(self.s2)
        self.canvas.tag_lower(self.s2)
        self.canvas.tag_lower(self.s2)

    def update(self):
        self.xpos, self.ypos = self.canvas.coords(self.s1)
        self.ypos += self.speed
        if self.ypos >= Constants.windowHeight + 350:
            self.ypos = -700
            self.canvas.move(self.s1, 0, -700)
            self.canvas.move(self.s2, 0, -700)

    def render(self):
        self.canvas.move(self.s1, 0, self.speed)
        self.canvas.move(self.s2, 0, self.speed)

class Score(object):
    def __init__(self, canvas = None, asteroids = None):
        self.canvas = canvas
        self.score = 0
        self.board = self.canvas.create_text(Constants.windowWidth / 2, 50, font = "Jokerman 20 bold italic",
                                             text = "{}".format(self.score), justify = "center", fill = 'white')
        self.lastTime = time()
        self.maxTime = 1 / 10
        self.canvas.tag_raise(self.board)
        self.canvas.tag_raise(self.board)
        self.canvas.tag_raise(self.board)
        
        self.asteroids = asteroids

    def update(self):
        elapsed = time() - self.lastTime
        self.lastTime - time()

        wait = self.maxTime - elapsed
        if(wait > 0):
            return
        else:
            self.score += 1
            if self.score % 100 == 0:
                self.asteroids.increaseSpeed()


    def render(self):
        self.canvas.itemconfig(self.board, text = "{}".format(self.score))


class MainWindow(tk.Frame):
    def __init__(self, master = None):
        super().__init__()
        self.master = master

        self.windowWidth = 400
        self.windowHeight = 700
        
        self.master.geometry("{}x{}".format(self.windowWidth, self.windowHeight))
        self.master.resizable(False, False)

        self.place(x = 0, y = 0, width = self.windowWidth, height = self.windowHeight)


        self.canvas = tk.Canvas(bg = 'black')
        self.canvas.place(x = 0, y = 0, width = self.windowWidth, height = self.windowHeight)

        self.maxFPS = 60

        self.asteroids = Asteroids(canvas = self.canvas, maxNumber = 10)

        self.scoreBoard = Score(canvas = self.canvas, asteroids = self.asteroids)
        self.player = Player(canvas = self.canvas, xPos = Constants.windowWidth / 2 - 25, yPos = Constants.windowHeight - 10 - 50, asteroids =  self.asteroids, scoreBoard = self.scoreBoard)
        
        self.entities = Entities.Entities(self.asteroids, self.player)
        self.entities.addEntity(self.scoreBoard)
        self.player.entities = self.entities

        self.backGround = BackGround(canvas = self.canvas)
        self.entities.addEntity(self.backGround)


        self.master.bind('<KeyPress>', self.keyPress)
        self.master.bind('<KeyRelease>', self.keyRelease)

        self.stop = False


        self.gameLoop()
        self.mainloop()

    def keyPress(self, event):
        keyCode = event.keycode
        if keyCode == Constants.up:
            self.player.yVel = -5
        elif keyCode == Constants.down:
            self.player.yVel = 5
        elif keyCode == Constants.left:
            self.player.xVel = -5
        elif keyCode == Constants.right:
            self.player.xVel = 5
        elif keyCode == Constants.space:
            self.player.shooting = True
        else:
            pass
    def keyRelease(self, event):
        keyCode = event.keycode
        if keyCode == Constants.up and self.player.yVel < 0:
            self.player.yVel = 0
        elif keyCode == Constants.down and self.player.yVel > 0:
            self.player.yVel = 0
        elif keyCode == Constants.left and self.player.xVel < 0:
            self.player.xVel = 0
        elif keyCode == Constants.right and self.player.xVel > 0:
            self.player.xVel = 0
        elif keyCode == Constants.space:
            self.player.shooting = False
        else:
            pass

    def gameLoop(self):
        if self.stop:self.canvas.after(15, self.gameLoop)
        maxTime = 1 / self.maxFPS - 0.015
        start = time()
        self.update()
        self.render()
        elapsed = time() - start

        wait = maxTime - elapsed
        if(wait > 0):
            sleep(wait)
        self.canvas.after(15, self.gameLoop)

    def unCrash(self):

        for asteroid in self.asteroids.getAsteroidList():
            asteroid.reset()


        self.player.x = Constants.windowWidth / 2 - 25
        self.player.y = Constants.windowHeight - 60
        self.entities.player.health = 100
        self.scoreBoard.score = 0
        self.canvas.delete(self.cover)
        self.canvas.delete(self.message)
        self.stop = False

    def sendCrashedSignal(self):
        self.stop = True
        self.cover = self.canvas.create_rectangle(0, 0, Constants.windowWidth, Constants.windowHeight, fill = "black")
        self.message = self.canvas.create_text(Constants.windowWidth / 2, Constants.windowHeight / 2, font = "Joker 30 bold",
                                text = "YOUR SHIP \nIS DESTROYED\nYOUR SCORE:{}".format(self.scoreBoard.score), fill = 'white', justify = 'center')        
        for _ in range(5):
            self.canvas.tag_raise(self.cover)
            self.canvas.tag_raise(self.message)        

        self.canvas.after(1000, self.unCrash)
        self.stop = False

    def update(self):
        if(self.entities.update()):
            self.sendCrashedSignal()
            self.entities.player.health = 100
        else:
            pass

    def render(self):
        self.entities.render()
        
root = tk.Tk()
root.title('Space Invaders')
root.iconbitmap(Constants.resourcePath('./Assets/rocket.ico'))
window = MainWindow(master = root)