import pygame
import random
import sys

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Side Scroller Game")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW= (255, 255, 0)
BLUE  = (0, 100, 255)

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
        self.image = pygame.Surface((40, 60))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (50, HEIGHT - 40)
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

        if self.rect.bottom >= HEIGHT - 40:
            self.rect.bottom = HEIGHT - 40
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
        self.image = pygame.Surface((10, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        self.damage = 20

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH:
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.image = pygame.Surface((40, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (WIDTH + random.randint(50, 150), HEIGHT - 40)
        self.speed = 3 + level  # Faster with higher level
        self.health = 40 + (level * 10)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# Boss enemy class
class BossEnemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((120, 120))
        self.image.fill((150, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (WIDTH + 200, HEIGHT - 40)
        self.speed = 1.5
        self.health = 200  # 10 hits * 20 damage

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

# Collectible class
class Collectible(pygame.sprite.Sprite):
    def __init__(self, kind):
        super().__init__()
        self.kind = kind  # 'health' or 'life'
        self.image = pygame.Surface((20, 20))
        if kind == 'health':
            self.image.fill(BLUE)  # More visible color
        else:
            self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(WIDTH + 20, WIDTH + 200)
        self.rect.y = random.randint(HEIGHT - 150, HEIGHT - 60)
        self.speed = 3

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

def game_over_screen(win=False):
    screen.fill(BLACK)
    if win:
        draw_text("🎉 Congratulations! You defeated the Boss! 🎉", 36, GREEN, WIDTH // 2 - 280, HEIGHT // 2 - 40)
    else:
        draw_text("Game Over!", 48, RED, WIDTH // 2 - 100, HEIGHT // 2 - 40)
    draw_text("Press R to Restart or Q to Quit", 30, WHITE, WIDTH // 2 - 160, HEIGHT // 2 + 20)
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
                # Limit enemies on screen for level 3
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
                    bullet = Projectile(player.rect.right, player.rect.centery)
                    projectiles.add(bullet)
                    all_sprites.add(bullet)

        player.update(keys)
        projectiles.update()
        enemies.update()
        collectibles.update()
        if boss_spawned and boss and boss.alive():
            boss.update()

        # Bullet hits enemy
        for bullet in projectiles:
            enemy_hit = pygame.sprite.spritecollideany(bullet, enemies)
            if enemy_hit:
                enemy_hit.health -= bullet.damage
                bullet.kill()
                if enemy_hit.health <= 0:
                    enemy_hit.kill()
                    score += 1

            if boss_spawned and boss and boss.alive():
                if boss.rect.colliderect(bullet.rect):
                    boss.health -= bullet.damage
                    bullet.kill()
                    if boss.health <= 0:
                        boss.kill()
                        game_over_screen(win=True)
                        return

        # Player collides with enemies
        enemy_hit = pygame.sprite.spritecollideany(player, enemies)
        if enemy_hit:
            if player.damage(20):
                game_over_screen()
                return
            enemy_hit.kill()

        # Player collides with collectibles
        collect_hit = pygame.sprite.spritecollideany(player, collectibles)
        if collect_hit:
            if collect_hit.kind == 'health':
                player.health = min(player.health + 30, 100)
            else:
                player.lives += 1
            collect_hit.kill()

        # Player collides with boss (instant death)
        if boss_spawned and boss and boss.alive() and player.rect.colliderect(boss.rect):
            game_over_screen()
            return

        # Level logic and capping level to max 3
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

        # Spawn boss at level 3 after score threshold
        if level == 3 and score >= level_score_thresholds[3] and not boss_spawned:
            boss = BossEnemy()
            all_sprites.add(boss)
            boss_spawned = True
            # Stop spawning normal enemies when boss appears
            pygame.time.set_timer(enemy_spawn_event, 0)

        # Drawing
        screen.fill(WHITE)
        all_sprites.draw(screen)
        draw_text(f"Score: {score}", 22, BLACK, 10, 10)
        draw_text(f"Health: {player.health}", 22, GREEN, 10, 40)
        draw_text(f"Lives: {player.lives}", 22, BLUE, 10, 70)
        draw_text(f"Level: {level}", 22, BLACK, WIDTH - 120, 10)

        if show_level_message:
            draw_text(f"Level {level}", 48, BLACK, WIDTH // 2 - 60, HEIGHT // 2 - 40)

        # Controls info
        draw_text("Use arrow keys to move and jump", 20, BLACK, WIDTH // 2 - 140, HEIGHT - 60)
        draw_text("Press SPACE to shoot", 20, BLACK, WIDTH // 2 - 100, HEIGHT - 30)

        pygame.display.flip()

if __name__ == "__main__":
    while True:
        main_game()
