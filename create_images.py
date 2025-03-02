import pygame
import os
import random
import math

# Initialize Pygame
pygame.init()

# Create assets directory if it doesn't exist
if not os.path.exists('assets'):
    os.makedirs('assets')

# Player plane (larger size)
player_surface = pygame.Surface((60, 48), pygame.SRCALPHA)
pygame.draw.polygon(player_surface, (0, 255, 0), [(30, 0), (60, 48), (0, 48)])  # Green triangle
pygame.draw.polygon(player_surface, (200, 255, 200), [(30, 10), (50, 48), (10, 48)])  # Light green detail
pygame.image.save(player_surface, os.path.join('assets', 'player.png'))

# Enemy plane (larger size)
enemy_surface = pygame.Surface((50, 40), pygame.SRCALPHA)
pygame.draw.polygon(enemy_surface, (255, 0, 0), [(25, 40), (0, 0), (50, 0)])  # Red triangle
pygame.draw.polygon(enemy_surface, (255, 200, 200), [(25, 30), (10, 0), (40, 0)])  # Light red detail
pygame.image.save(enemy_surface, os.path.join('assets', 'enemy.png'))

# Bullet (larger and more visible)
bullet_surface = pygame.Surface((8, 16), pygame.SRCALPHA)
pygame.draw.rect(bullet_surface, (255, 255, 0), (0, 0, 8, 16))  # Yellow rectangle
pygame.draw.rect(bullet_surface, (255, 255, 200), (2, 2, 4, 12))  # Light yellow detail
pygame.image.save(bullet_surface, os.path.join('assets', 'bullet.png'))

# Space background
background = pygame.Surface((800, 600))
background.fill((0, 0, 20))  # Dark blue

# Add stars
for _ in range(200):
    x = random.randint(0, 799)
    y = random.randint(0, 599)
    brightness = random.randint(100, 255)
    pygame.draw.circle(background, (brightness, brightness, brightness), (x, y), random.randint(1, 2))

pygame.image.save(background, os.path.join('assets', 'background.png'))

# Power-up 1: Triple Shot (Blue diamond)
powerup1_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.polygon(powerup1_surface, (0, 100, 255), [(15, 0), (30, 15), (15, 30), (0, 15)])  # Blue diamond
pygame.draw.polygon(powerup1_surface, (100, 200, 255), [(15, 5), (25, 15), (15, 25), (5, 15)])  # Light blue detail
pygame.image.save(powerup1_surface, os.path.join('assets', 'powerup_triple.png'))

# Power-up 2: Rapid Fire (Purple star)
powerup2_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
points = []
for i in range(10):
    angle = (i * 36 - 90) * math.pi / 180
    radius = 15 if i % 2 == 0 else 7
    points.append((15 + radius * math.cos(angle), 15 + radius * math.sin(angle)))
pygame.draw.polygon(powerup2_surface, (255, 0, 255), points)  # Purple star
pygame.image.save(powerup2_surface, os.path.join('assets', 'powerup_rapid.png'))

# Power-up 3: Big Shot (Orange circle)
powerup3_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
pygame.draw.circle(powerup3_surface, (255, 165, 0), (15, 15), 15)  # Orange circle
pygame.draw.circle(powerup3_surface, (255, 200, 100), (15, 15), 10)  # Light orange detail
pygame.image.save(powerup3_surface, os.path.join('assets', 'powerup_big.png'))

print("Created placeholder images in assets directory") 