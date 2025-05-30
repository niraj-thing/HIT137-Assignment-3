import pygame
import random
import sys

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Mario of Darwin")
clock = pygame.time.Clock()

GROUND_LEVEL = HEIGHT - 85


# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Load and play background music
pygame.mixer.music.load("assets/sounds/background_music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1) 

shoot_sound = pygame.mixer.Sound("assets/sounds/hit.mp3")
shoot_sound.set_volume(0.3)


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW= (255, 255, 0)
BLUE  = (0, 100, 255)

background_img = pygame.image.load("assets/images/background.jpg").convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
player_img = pygame.image.load("assets/images/player.png").convert_alpha()
enemy_img = pygame.image.load("assets/images/enemy.png").convert_alpha()
boss_img = pygame.image.load("assets/images/boss.png").convert_alpha()
bullet_img = pygame.image.load("assets/images/bullet.png").convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (20, 10))


# Fonts
font_name = pygame.font.match_font('arial')

def draw_text(text, size, color, x, y):
    font = pygame.font.Font(font_name, size)
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(player_img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (100, HEIGHT - 300)
        self.speed = 5
        self.vel_y = 0
        self.gravity = 0.8
        self.on_ground = True
        self.health = 100
        self.lives = 3

    def update(self, keys):
        dx = 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed

        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = -15
            self.on_ground = False

        self.vel_y += self.gravity
        dy = self.vel_y

        self.rect.x += dx
        self.rect.y += dy

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        if self.rect.bottom >= GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL

            self.vel_y = 0
            self.on_ground = True

    def damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.lives -= 1
            self.health = 100
            if self.lives <= 0:
                return True
        return False

# Projectile class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        self.damage = 2

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH:
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, level=1):
        super().__init__()
        self.image = pygame.transform.scale(enemy_img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + 10
        self.rect.y = GROUND_LEVEL - 50
        
        self.speed = random.randint(2 + level, 4 + level)
        self.health = 1  # Regular enemies take 1 hit to die



    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


# Boss enemy class
class BossEnemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(boss_img, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + 10
        self.rect.y = GROUND_LEVEL - 100


        self.speed = 2
        self.health = 20  # Boss takes 10 hits


    def update(self):
        self.rect.x -= self.speed


# Collectible class
class Collectible(pygame.sprite.Sprite):
    def __init__(self, kind):
        super().__init__()
        self.kind = kind
        self.image = pygame.Surface((20, 20))
        if kind == 'health':
            self.image.fill(BLUE)
        else:
            self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(WIDTH + 20, WIDTH + 200)
        self.rect.y = random.randint(HEIGHT - 200, HEIGHT - 120)


        self.speed = 3

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

def game_over_screen(win=False):
    screen.fill(BLACK)
    
    if win:
        font = pygame.font.Font(font_name, 36)
        text_surface = font.render("Congratulations! You defeated the Boss!", True, GREEN)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        screen.blit(text_surface, text_rect)
    else:
        font = pygame.font.Font(font_name, 48)
        text_surface = font.render("Game Over!", True, RED)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        screen.blit(text_surface, text_rect)

    font = pygame.font.Font(font_name, 30)
    instruction_surface = font.render("Press R to Restart or Q to Quit", True, WHITE)
    instruction_rect = instruction_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    screen.blit(instruction_surface, instruction_rect)

    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def main_game():
    all_sprites = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    score = 0
    boss_spawned = False
    boss = None

    enemy_spawn_event = pygame.USEREVENT + 1
    collectible_spawn_event = pygame.USEREVENT + 2

    enemy_spawn_delay = 1000
    collectible_spawn_delay = 5000

    pygame.time.set_timer(enemy_spawn_event, enemy_spawn_delay)
    pygame.time.set_timer(collectible_spawn_event, collectible_spawn_delay)

    level = 1
    level_score_thresholds = {1: 5, 2: 10, 3: 15}
    level_transition_timer = 0
    show_level_message = True

    running = True
    while running:
        clock.tick(60)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == enemy_spawn_event and not boss_spawned and not show_level_message:
                if level == 3:
                    if len(enemies) < 3:
                        enemies.add(Enemy(level))
                        all_sprites.add(enemies)
                else:
                    enemies.add(Enemy(level))
                    all_sprites.add(enemies)

            if event.type == collectible_spawn_event and not show_level_message:
                kind = random.choice(['health', 'life'])
                c = Collectible(kind)
                collectibles.add(c)
                all_sprites.add(c)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet_y = player.rect.top + 20
                    bullet = Projectile(player.rect.right, bullet_y)
                    projectiles.add(bullet)
                    all_sprites.add(bullet)
                    shoot_sound.play()


        player.update(keys)
        projectiles.update()
        enemies.update()
        collectibles.update()
        if boss_spawned and boss and boss.alive():
            boss.update()

        for bullet in projectiles.copy():

            enemy_hit = pygame.sprite.spritecollideany(bullet, enemies)
            if enemy_hit:
                enemy_hit.health -= bullet.damage
                bullet.kill()
                if enemy_hit.health <= 0:
                    enemy_hit.kill()
                    score += 1
                continue

            if boss_spawned and boss and boss.alive():
                if boss.rect.colliderect(bullet.rect):
                    boss.health -= bullet.damage
                    bullet.kill()
                    print(f"Boss health now: {boss.health}") 
                    if boss.health <= 0:
                        boss.kill()
                        game_over_screen(win=True)
                        return
                    
        enemy_hit = pygame.sprite.spritecollideany(player, enemies)
        if enemy_hit:
            if player.damage(20):
                game_over_screen()
                return
            enemy_hit.kill()

        collect_hit = pygame.sprite.spritecollideany(player, collectibles)
        if collect_hit:
            if collect_hit.kind == 'health':
                player.health = min(player.health + 30, 100)
            else:
                player.lives += 1
            collect_hit.kill()

        if boss_spawned and boss and boss.alive() and player.rect.colliderect(boss.rect):
            game_over_screen()
            return

        if show_level_message and pygame.time.get_ticks() - level_transition_timer > 2000:
            show_level_message = False

        if not show_level_message and level < 3 and score >= level_score_thresholds[level]:
            level += 1
            show_level_message = True
            level_transition_timer = pygame.time.get_ticks()

            if level == 2:
                enemy_spawn_delay = 800
            elif level == 3:
                enemy_spawn_delay = 1500
            pygame.time.set_timer(enemy_spawn_event, enemy_spawn_delay)

        if level == 3 and score >= level_score_thresholds[3] and not boss_spawned:
            boss = BossEnemy()
            all_sprites.add(boss)
            boss_spawned = True
            pygame.time.set_timer(enemy_spawn_event, 0)

        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        draw_text(f"Score: {score}", 22, BLACK, 10, 10)
        draw_text(f"Health: {player.health}", 22, GREEN, 10, 40)
        draw_text(f"Lives: {player.lives}", 22, BLUE, 10, 70)
        draw_text(f"Level: {level}", 22, BLACK, WIDTH - 120, 10)

        if show_level_message:
            draw_text(f"Level {level}", 48, BLACK, WIDTH // 2 - 60, HEIGHT // 2 - 40)

        draw_text("Use arrow keys to move and jump", 20, WHITE, WIDTH // 2 - 140, HEIGHT - 60)
        draw_text("Press SPACE to shoot", 20, WHITE, WIDTH // 2 - 100, HEIGHT - 30)


        pygame.display.flip()

if __name__ == "__main__":
    while True:
        main_game()
