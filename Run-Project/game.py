import pygame, sys, random
from config import *

class Block(pygame.sprite.Sprite):
    def __init__(self, position:tuple[int, int]):
        super().__init__()
        self.image = pygame.image.load("blockup.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.speed = pygame.Vector2(0, 0)

    def blockMove(self): # done
        keys = pygame.key.get_pressed()
        pixel_jump = 10

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.image = pygame.image.load("blockup.png").convert_alpha()
            if self.rect.y <= 0:
                pass
            else:
                self.rect.y -= pixel_jump
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.image = pygame.image.load("blockdown.png").convert_alpha()
            if self.rect.y >= HEIGHT - self.rect.h:
                pass
            else:
                self.rect.y += pixel_jump
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.image = pygame.image.load("blockleft.png").convert_alpha()
            if self.rect.x <= 0:
                pass
            else:
                self.rect.x -= pixel_jump
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.image = pygame.image.load("blockright.png").convert_alpha()
            if self.rect.x >= WIDTH - self.rect.w:
                pass
            else:
                self.rect.x += pixel_jump

    def update(self): 
        self.rect.center += self.speed

class Enemy(pygame.sprite.Sprite):
    def __init__ (self):
        super().__init__()
        filename = Enemy.retrieveFile()
        self.image = pygame.image.load(filename).convert_alpha()
        self.rect = self.image.get_rect()
        select_direction = random.randint(0, 1)
        x_coordinate = (random.randint(100, WIDTH - 100))

        if select_direction == 0:
            y_coordinate = -1
            self.speed = pygame.Vector2(random.randint(-5, 5), random.randint(1, 5))
        else:
            y_coordinate = HEIGHT + 1
            self.speed = pygame.Vector2(random.randint(-5, 5), random.randint(-5, -1))

        self.rect.bottomright = (x_coordinate, y_coordinate)

    @staticmethod
    def retrieveFile() -> str:
        index = random.randint(0, len(enemyImgFiles) - 1)
        filename = enemyImgFiles[index]
        return filename

    def isinBounds(self):
        if (0 <= self.rect.bottomright[0] <= WIDTH) and (0 <= self.rect.bottomright[1] <= HEIGHT):
            self.inBounds = True
        else:
            self.inBounds = False

    def update(self):
        self.isinBounds()

        if self.inBounds:
            self.rect.bottomright += self.speed
            if self.rect.bottomright[0] >= WIDTH or (self.rect.bottomright[0] - self.rect.w) <= 0:
                self.kill()
        else:
            self.rect.bottomright += self.speed

class Item(pygame.sprite.Sprite):
    def __init__ (self):
        super().__init__()
        itemSpritesheet = pygame.image.load("items.png").convert_alpha()
        img = Item.getItem(itemSpritesheet, 9, random.randint(0, 15), 32, 32)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (random.randint(32, WIDTH - 32), random.randint(32, HEIGHT - 32))

    @staticmethod
    def getItem(spritesheet, row, col, width, height):
        img = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        x = col * width
        y = row * height
        img.blit((spritesheet), (0,0), (x, y, width, height))
        return img

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Run!")
        self.characterGroup = pygame.sprite.Group()
        self.character = Block(((WIDTH / 2), (HEIGHT / 2)))
        self.characterGroup.add(self.character)
        self.timer = 0
        self.enemyGroup = pygame.sprite.Group()
        self.itemGroup = pygame.sprite.Group()
        self.item = Item()
        self.itemGroup.add(self.item)
        self.font = pygame.font.SysFont(None, 40)
        self.score = 0
        self.spawning_time = 2000
        self.level = 1
        self.states = {"READY": 1, "PLAY": 2}
        self.current_state = self.states["READY"]
        self.loseEffect = pygame.mixer.Sound("lose.wav")
        filename = Game.CollectSound()
        self.collectEffect = pygame.mixer.Sound(filename)
    
    @staticmethod
    def CollectSound() -> list:
        index = random.randint(0, len(collectAudioFiles) - 1)
        filename = collectAudioFiles[index]
        return filename

    def setStates(self):
        if self.current_state == self.states["READY"]:
            colour = (255, 255, 255)
            message = self.font.render("Press the Space Bar to begin:", True, colour)
            self.screen.blit(message, (WIDTH / 3 + 25, HEIGHT / 2 + 50))
        elif self.current_state == self.states["PLAY"]:
            self.characterGroup = pygame.sprite.Group()
            self.character = Block(((WIDTH / 2), (HEIGHT / 2)))
            self.characterGroup.add(self.character)

    def checkCollisions(self):
        if self.enemyGroup:
            for enemy in self.enemyGroup:
                collided = pygame.sprite.spritecollide(enemy, self.characterGroup, True)
                if collided:
                    pygame.mixer.music.pause()
                    self.loseEffect.play()
                    self.current_state = self.states["READY"]
                    self.character = Block(((WIDTH / 2), (HEIGHT / 2)))
                    self.characterGroup.add(self.character)
                    self.enemyGroup.empty()
                    self.score = 0
                    self.level = 1
                    self.spawning_time = 2000

        if self.itemGroup:
            for item in self.itemGroup:
                collided = pygame.sprite.spritecollide(item, self.characterGroup, False)
                if collided:
                    pygame.mixer.music.pause()
                    item.kill()
                    item = Item()
                    self.itemGroup.add(item)
                    self.collectEffect.play()
                    pygame.mixer.music.unpause()
                    self.score += 1
                    if self.score % 5 == 0:
                        self.level += 1
                        self.spawning_time -= 100

    def spawnEnemy(self):
        self.timer += self.clock.get_time()
        if self.timer > self.spawning_time:
            self.enemy = Enemy()
            self.enemyGroup.add(self.enemy)
            self.timer = 0

    def draw(self): 
        self.drawScore()
        self.drawLevel()

    def drawScore(self):
        scoreStr = f"Score: {self.score}"
        colour = (255, 255, 255)
        running_score = self.font.render(scoreStr, True, colour)
        self.screen.blit(running_score, ((WIDTH - running_score.get_width()), 0))

    def drawLevel(self):
        levelStr = f"Level: {self.level}"
        colour = (255, 255, 255)
        running_level = self.font.render(levelStr, True, colour)
        self.screen.blit(running_level, (0, 0))

    def run(self):
      while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if self.current_state == self.states["READY"]:
            self.screen.fill("black")
            self.setStates()
            self.characterGroup.draw(self.screen)
            self.draw()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.current_state = self.states["PLAY"]

        if self.current_state == self.states["PLAY"]:
            self.screen.fill("black")
            self.character.blockMove()
            self.characterGroup.update()
            self.characterGroup.draw(self.screen)
            self.spawnEnemy()
            self.enemyGroup.update()
            self.enemyGroup.draw(self.screen)
            self.checkCollisions()
            self.itemGroup.draw(self.screen)
            self.draw()
        if self.current_state == self.states["READY"]:
                pygame.mixer.music.load("music.wav")
                pygame.mixer.music.play(-1)
        
        pygame.display.update()
        self.clock.tick(FPS)
    
if __name__ == "__main__":
    game = Game()
    game.run()