import pygame, sys, random, math
import pygame.locals as GAME_GLOBALS
import pygame.event as GAME_EVENTS
import pygame.time as GAME_TIME
import Ships

windowWidth = 1024
windowHeight = 614

pygame.init()
pygame.font.init()
surface = pygame.display.set_mode((windowWidth, windowHeight))

pygame.display.set_caption('Space Invaders Are Gonna Kill Me!')
textFont = pygame.font.SysFont("monospace", 50)
scoreFont = pygame.font.SysFont("monospace", 20)

gameStarted = False
gameStartedTime = GAME_TIME.get_ticks()
gameFinishedTime = 0
gameOver = False
playerName = "default"
enemyShips = []
score = 0

# Mouse variables
mousePosition = (0,0)
mouseStates = None
mouseDown = False

# Image variables
startScreen = pygame.image.load("assets/start_screen_new.png")
background = pygame.image.load("assets/background.png")
backgroundLost = pygame.image.load("assets/background_end.png")

#Colour variables
white = pygame.Color(255,255,255)

lastEnemyCreated = 0
enemyInterval = random.randint(1000, 2500)

# Sound setup
pygame.mixer.init()

def updateGame(score):
    
    global mouseDown, gameOver

    enemyDead = score
    
    if mouseStates[0] is 1 and mouseDown is False:
        ship.fire()
        mouseDown = True
    elif mouseStates[0] is 0 and mouseDown is True:
        mouseDown = False

    ship.setPosition(mousePosition)

    enemiesToRemove = []

    for idx, enemy in enumerate(enemyShips):

        if enemy.y < windowHeight:
            enemy.move()
            enemy.tryToFire()
            shipIsDestroyed = enemy.checkForHit(ship)
            enemyIsDestroyed = ship.checkForHit(enemy)

            if enemyIsDestroyed is True:
                enemyDead = enemyDead + 1
                enemiesToRemove.append(idx)

            if shipIsDestroyed is True:
                gameOver = True

        else:
            enemiesToRemove.append(idx)

    for idx in enemiesToRemove:
        del enemyShips[idx]

    return enemyDead
        
def drawGame(playerName):
    surface.blit(background, (0,0))
    ship.draw(playerName)
    ship.drawBullets()

    for enemy in enemyShips:
        enemy.draw(playerName)
        enemy.drawBullets()

def playerLost(playerName):
    surface.blit(backgroundLost, (0,0))
    lostText = textFont.render("Space Pilot " + playerName + " died in combat", 1, white)
    lostRect = lostText.get_rect()
    lostRect.center = (windowWidth / 2, windowHeight / 2)
    surface.blit(lostText, lostRect)

def quitGame():
    pygame.quit()
    sys.exit()

def setScore(score, playerName):
    scoreWords = "Space Pilot " + playerName + " has killed " + str(score) + " aliens"
    scoreText = scoreFont.render(scoreWords, 1, white)
    scoreRect = scoreText.get_rect()
    scoreRect.center = (windowWidth - (len(scoreWords) * 7), 10)
    surface.blit(scoreText, scoreRect)

# 'main' loop
while True:

    tickTime = GAME_TIME.get_ticks() - gameStartedTime
    mousePosition = pygame.mouse.get_pos()
    mouseStates = pygame.mouse.get_pressed()

    if gameStarted is True and gameOver is False:

        score = updateGame(score)
        drawGame(playerName)
        setScore(score, playerName)

    elif gameStarted is False and gameOver is False:
        surface.blit(startScreen, (0,0))
        
        if mouseStates[0] is 1:
            if mousePosition[0] > 210 and mousePosition[0] < 475 and mousePosition[1] > 400 and mousePosition[1] < 490:

                playerName = "James"
                gameStarted = True
                ship = Ships.Player(windowWidth / 2, windowHeight, pygame, surface, playerName)

            elif mousePosition[0] > 575 and mousePosition[0] < 810 and mousePosition[1] > 400 and mousePosition[1] < 510:

                playerName = "Florence"
                gameStarted = True
                ship = Ships.Player(windowWidth / 2, windowHeight, pygame, surface, playerName)
 
        elif mouseStates[0] is 0 and mouseDown is True:
            mouseDown = False

    elif gameStarted is True and gameOver is True:
        playerLost(playerName)
            
    #Handle user and system events
    for event in GAME_EVENTS.get():

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                quitGame()

    if GAME_TIME.get_ticks()-lastEnemyCreated > enemyInterval and gameStarted is True:

        enemyShips.append(Ships.Enemy(random.randint(0, windowWidth), -60, pygame, surface, 1))
        lastEnemyCreated = GAME_TIME.get_ticks()

    if event.type == GAME_GLOBALS.QUIT:
        quitGame()

    pygame.display.update()
