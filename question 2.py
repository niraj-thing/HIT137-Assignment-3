import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Side Scroller Game")

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Load assets (placeholder rectangles)
font = pygame.font.SysFont("Arial", 24)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 60))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = HEIGHT - 150
        self.speed_x = 5
        self.jump_speed = -15
        self.velocity_y = 0
        self.is_jumping = False
        self.health = 100
        self.lives = 3
        self.score = 0

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed_x
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed_x
        if not self.is_jumping and keys[pygame.K_SPACE]:
            self.velocity_y = self.jump_speed
            self.is_jumping = True

        self.velocity_y += 1  # gravity
        self.rect.y += self.velocity_y

        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.is_jumping = False

    def shoot(self):
        projectile = Projectile(self.rect.right, self.rect.centery)
        all_sprites.add(projectile)
        projectiles.add(projectile)

# Projectile class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 10

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.left > WIDTH:
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 50))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 50

    def update(self):
        self.rect.x -= 2
        if self.health <= 0:
            player.score += 10
            self.kill()

# Collectible class
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = type

    def apply_effect(self, player):
        if self.type == 'health':
            player.health = min(100, player.health + 20)
        elif self.type == 'life':
            player.lives += 1
        player.score += 5
        self.kill()

# Level manager
class Level:
    def __init__(self, number):
        self.number = number
        self.spawn_enemies()
        self.spawn_collectibles()

    def spawn_enemies(self):
        for _ in range(self.number * 3):
            enemy = Enemy(WIDTH + random.randint(100, 500), HEIGHT - 100)
            all_sprites.add(enemy)
            enemies.add(enemy)

    def spawn_collectibles(self):
        for _ in range(2):
            c = Collectible(WIDTH + random.randint(200, 600), HEIGHT - 100, random.choice(['health', 'life']))
            all_sprites.add(c)
            collectibles.add(c)

# Game Over screen
def game_over_screen():
    screen.fill(WHITE)
    game_over_text = font.render("Game Over! Press R to Restart", True, RED)
    screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                waiting = False

# Game groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
collectibles = pygame.sprite.Group()

# Initialize player and level
player = Player()
all_sprites.add(player)
level = Level(1)
current_level = 1

# Main game loop
running = True
while running:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                player.shoot()

    # Update
    player.update(keys)  # Only player needs keys
    projectiles.update()
    enemies.update()
    collectibles.update()


    for projectile in projectiles:
        hits = pygame.sprite.spritecollide(projectile, enemies, False)
        for hit in hits:
            hit.health -= 25
            projectile.kill()

    hits = pygame.sprite.spritecollide(player, collectibles, False)
    for hit in hits:
        hit.apply_effect(player)

    hits = pygame.sprite.spritecollide(player, enemies, False)
    for hit in hits:
        player.health -= 1
        if player.health <= 0:
            player.lives -= 1
            player.health = 100
            if player.lives <= 0:
                game_over_screen()
                # Reset game
                all_sprites.empty()
                enemies.empty()
                projectiles.empty()
                collectibles.empty()
                player = Player()
                all_sprites.add(player)
                level = Level(1)
                current_level = 1

    # Advance level
    if not enemies:
        current_level += 1
        if current_level > 3:
            game_over_screen()  # Victory screen could be added
            running = False
        else:
            level = Level(current_level)

    # Draw
    screen.fill(WHITE)
    all_sprites.draw(screen)
    
    health_text = font.render(f"Health: {player.health}", True, RED)
    lives_text = font.render(f"Lives: {player.lives}", True, RED)
    score_text = font.render(f"Score: {player.score}", True, RED)
    screen.blit(health_text, (10, 10))
    screen.blit(lives_text, (10, 40))
    screen.blit(score_text, (10, 70))

    pygame.display.flip()

pygame.quit()
