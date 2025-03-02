import pygame
import random
import sys
import os

# Initialize Pygame and its mixer
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_SPEED = 3
PLAYER_SCALE = 1.0
ENEMY_SCALE = 0.8
BULLET_SCALE = 0.5
GAME_DURATION = 120000  # 2 minutes in milliseconds
POWERUP_DURATION = 5000  # 5 seconds in milliseconds
POWERUP_SPAWN_RATE = 0.02  # 2% chance per frame

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Plane Shooter")

# Load images
def load_image(name, scale=1):
    try:
        image = pygame.image.load(os.path.join('assets', name))
        image = pygame.transform.scale(image, 
                                     (int(image.get_width() * scale), 
                                      int(image.get_height() * scale)))
        return image
    except pygame.error:
        # If image not found, create a default surface
        surf = pygame.Surface((40, 40))
        surf.fill(WHITE)
        return surf

# Load sounds
def load_sound(name):
    try:
        sound = pygame.mixer.Sound(os.path.join('assets', name))
        return sound
    except pygame.error:
        return None

# Load game assets
PLAYER_IMG = load_image('player.png', PLAYER_SCALE)
ENEMY_IMG = load_image('enemy.png', ENEMY_SCALE)
BULLET_IMG = load_image('bullet.png', BULLET_SCALE)
BACKGROUND_IMG = load_image('background.png', 1)
POWERUP_TRIPLE = load_image('powerup_triple.png', 1)
POWERUP_RAPID = load_image('powerup_rapid.png', 1)
POWERUP_BIG = load_image('powerup_big.png', 1)

# Load sounds
SHOOT_SOUND = load_sound('shoot.wav')
EXPLOSION_SOUND = load_sound('explosion.wav')
HIT_SOUND = load_sound('hit.wav')
GAME_MUSIC = os.path.join('assets', 'game_music.mp3')

# Power-up class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, powerup_type):
        super().__init__()
        self.type = powerup_type
        if powerup_type == "triple":
            self.image = POWERUP_TRIPLE
        elif powerup_type == "rapid":
            self.image = POWERUP_RAPID
        else:  # big
            self.image = POWERUP_BIG
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Bullet class with power-up support
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, is_big=False):
        super().__init__()
        self.image = BULLET_IMG
        if is_big:
            self.image = pygame.transform.scale(self.image, (16, 32))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.is_big = is_big

    def update(self):
        self.rect.y -= BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()

# Player class with power-ups
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.score = 0
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        
        # Power-up states
        self.triple_shot = False
        self.rapid_fire = False
        self.big_shot = False
        self.powerup_timer = 0

    def update(self):
        now = pygame.time.get_ticks()
        
        # Check power-up timers
        if now - self.powerup_timer > POWERUP_DURATION:
            self.triple_shot = False
            self.rapid_fire = False
            self.big_shot = False
        
        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += PLAYER_SPEED
        
        # Shooting
        if keys[pygame.K_SPACE]:
            current_delay = self.shoot_delay // 2 if self.rapid_fire else self.shoot_delay
            if now - self.last_shot > current_delay:
                self.shoot()
                self.last_shot = now

    def shoot(self):
        if self.triple_shot:
            # Create three bullets
            bullet1 = Bullet(self.rect.centerx - 20, self.rect.top, self.big_shot)
            bullet2 = Bullet(self.rect.centerx, self.rect.top, self.big_shot)
            bullet3 = Bullet(self.rect.centerx + 20, self.rect.top, self.big_shot)
            game.all_sprites.add(bullet1, bullet2, bullet3)
            game.bullets.add(bullet1, bullet2, bullet3)
        else:
            # Create single bullet
            bullet = Bullet(self.rect.centerx, self.rect.top, self.big_shot)
            game.all_sprites.add(bullet)
            game.bullets.add(bullet)
        
        if SHOOT_SOUND:
            SHOOT_SOUND.play()

    def activate_powerup(self, powerup_type):
        self.powerup_timer = pygame.time.get_ticks()
        if powerup_type == "triple":
            self.triple_shot = True
        elif powerup_type == "rapid":
            self.rapid_fire = True
        else:  # big
            self.big_shot = True

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ENEMY_IMG
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)

    def update(self):
        self.rect.y += ENEMY_SPEED
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)

# Game class with power-ups
class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.font = pygame.font.Font(None, 36)
        self.game_state = "start"
        self.total_lives = 3
        self.start_time = 0
        self.time_left = GAME_DURATION
        
        try:
            pygame.mixer.music.load(GAME_MUSIC)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    def spawn_enemy(self):
        if len(self.enemies) < 5:
            enemy = Enemy()
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)

    def spawn_powerup(self):
        if random.random() < POWERUP_SPAWN_RATE:
            powerup_type = random.choice(["triple", "rapid", "big"])
            powerup = PowerUp(powerup_type)
            self.all_sprites.add(powerup)
            self.powerups.add(powerup)

    def show_start_screen(self):
        screen.fill(BLACK)
        title = self.font.render("PLANE SHOOTER", True, WHITE)
        start_text = self.font.render("Press SPACE to start", True, WHITE)
        exit_text = self.font.render("Press ESC to exit", True, WHITE)
        lives_text = self.font.render(f"Lives remaining: {self.total_lives}", True, WHITE)
        
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//3))
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(exit_text, (SCREEN_WIDTH//2 - exit_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        screen.blit(lives_text, (SCREEN_WIDTH//2 - lives_text.get_width()//2, SCREEN_HEIGHT//2 + 100))
        
        pygame.display.flip()

    def show_game_over(self, won=False):
        screen.fill(BLACK)
        if won:
            result_text = self.font.render("YOU WIN!", True, WHITE)
        else:
            result_text = self.font.render("GAME OVER", True, WHITE)
        
        score_text = self.font.render(f"Final Score: {self.player.score}", True, WHITE)
        restart_text = self.font.render("Press SPACE to restart", True, WHITE)
        exit_text = self.font.render("Press ESC to exit", True, WHITE)
        
        screen.blit(result_text, (SCREEN_WIDTH//2 - result_text.get_width()//2, SCREEN_HEIGHT//3 - 50))
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//3))
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(exit_text, (SCREEN_WIDTH//2 - exit_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        
        pygame.display.flip()

    def start_new_round(self):
        self.all_sprites.empty()
        self.enemies.empty()
        self.bullets.empty()
        self.powerups.empty()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.start_time = pygame.time.get_ticks()
        self.time_left = GAME_DURATION
        self.game_state = "start"

    def run(self):
        global game
        game = self
        
        while True:
            self.clock.tick(60)
            
            if self.game_state == "start":
                self.show_start_screen()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.game_state = "playing"
                            self.start_time = pygame.time.get_ticks()
                        if event.key == pygame.K_ESCAPE:
                            return

            elif self.game_state == "playing":
                # Draw background first
                screen.blit(BACKGROUND_IMG, (0, 0))
                
                current_time = pygame.time.get_ticks()
                self.time_left = max(0, GAME_DURATION - (current_time - self.start_time))
                
                if self.time_left <= 0:
                    self.game_state = "won"
                    continue

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return

                # Update
                self.all_sprites.update()

                # Spawn enemies and power-ups
                self.spawn_enemy()
                self.spawn_powerup()

                # Check bullet-enemy collisions
                hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
                for hit in hits:
                    if EXPLOSION_SOUND:
                        EXPLOSION_SOUND.play()
                    self.player.score += 1

                # Check player-powerup collisions
                hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
                for hit in hits:
                    self.player.activate_powerup(hit.type)

                # Check player-enemy collisions
                hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
                if hits:
                    if HIT_SOUND:
                        HIT_SOUND.play()
                    self.total_lives -= 1
                    if self.total_lives <= 0:
                        self.game_state = "game_over"
                    else:
                        self.game_state = "start"

                # Draw
                self.all_sprites.draw(screen)
                
                # Draw score, lives and timer
                score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
                lives_text = self.font.render(f"Lives: {self.total_lives}", True, WHITE)
                time_text = self.font.render(f"Time: {self.time_left//1000}s", True, WHITE)
                screen.blit(score_text, (10, 10))
                screen.blit(lives_text, (10, 50))
                screen.blit(time_text, (SCREEN_WIDTH - 150, 10))
                
                pygame.display.flip()

            elif self.game_state == "game_over":
                self.show_game_over(won=False)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.total_lives = 3
                            self.start_new_round()
                        if event.key == pygame.K_ESCAPE:
                            return

            elif self.game_state == "won":
                self.show_game_over(won=True)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.total_lives = 3
                            self.start_new_round()
                        if event.key == pygame.K_ESCAPE:
                            return

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit() 