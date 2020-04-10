import Projectiles, random

class Player():

    x = 0
    y = 0
    firing = False
    image = None
    soundEffect = "sounds/player_gun.wav"
    pygame = None
    surface = None
    width = 0
    height = 0
    bullets = []
    bulletImage = "assets/you_pellet.png"
    bulletSpeed = -10
    health = 5
    time = 0

    def loadImages(self, playerName):
        if playerName == "James":
            self.image = self.pygame.image.load("assets/james_ship_v2.png")
        elif playerName == "Florence":
            self.image = self.pygame.image.load("assets/florence_ship_v2.png")
        else:
            self.image = self.pygame.image.load("assets/you_ship_v2.png")

    def draw(self, playerName):
        self.surface.blit(self.image, (self.x, self.y))

    def setPosition(self, pos):
        self.x = pos[0] - self.width / 2

    def fire(self):
        self.bullets.append(Projectiles.Bullet(self.x + self.width / 2, self.y,
                                               self.pygame, self.surface,
                                               self.bulletSpeed, self.bulletImage))
        a = self.pygame.mixer.Sound(self.soundEffect)
        a.set_volume(0.2)
        a.play

    def drawBullets(self):
        for b in self.bullets:
            b.move()
            b.draw()

    def registerHit(self):
        self.health -= 1

    def checkForHit(self, thingToCheckAgainst):
        bulletsToRemove = []

        for idx, b in enumerate(self.bullets):
            if b.x > thingToCheckAgainst.x and b.x < thingToCheckAgainst.x + thingToCheckAgainst.width:
                if b.y > thingToCheckAgainst.y and b.y < thingToCheckAgainst.y + thingToCheckAgainst.height:
                    thingToCheckAgainst.registerHit()
                    bulletsToRemove.append(idx)

        for usedBullet in bulletsToRemove:
            del self.bullets[usedBullet]

        if thingToCheckAgainst.health <= 0:
            return True

    def __init__(self, x, y, pygame, surface, playerName):
        self.x = x
        self.y = y
        self.pygame = pygame
        self.surface = surface
        self.playerName = playerName
        self.loadImages(playerName)

        dimensions = self.image.get_rect().size
        self.width = dimensions[0]
        self.height = dimensions[1]

        self.x -= self.width / 2
        self.y -= self.height + 10

class Enemy(Player):

    x = 0
    y = 0
    firing = False
    image = None
    soundEffect = "sounds/enemy_laser.wav"
    bulletImage = "assets/them_pellet.png"
    bulletSpeed = 10
    speed = 2

    def move(self):
        self.y += self.speed

    def tryToFire(self):
        shouldFire = random.random()

        if shouldFire <= 0.01:
            self.fire()

    def loadImages(self, number):
        if  number >= 9:
            self.image = self.pygame.image.load("assets/enemy_ship_2.png")
        else:
            self.image = self.pygame.image.load("assets/them_ship.png")

    def __init__(self, x, y, pygame, surface, health):
        randomNum = random.randint(1,11)
        self.x = x
        self.y = y
        self.pygame = pygame
        self.surface = surface
        self.loadImages(randomNum)
        self.bullets = []
        self.health = health

        dimensions = self.image.get_rect().size
        self.width = dimensions[0]
        self.height = dimensions[1]

        self.x -= self.width / 2
 
