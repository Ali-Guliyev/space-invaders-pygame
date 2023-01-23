import pygame, sys
import random
from files.get_path import path

pygame.init()
WIDTH, HEIGHT = 900, 800

# print(path)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
pygame.display.set_icon(pygame.image.load(f"{path}assets/images/icon.ico"))
clock = pygame.time.Clock()
enemy_die_time = 0
enemy_bullet_time = 400
enemy_bullet_timer = pygame.USEREVENT + 1
pygame.time.set_timer(enemy_bullet_timer, enemy_bullet_time)

def playsound(src, volume = 1, times = 0):
  sound = pygame.mixer.Sound(src)
  sound.set_volume(volume)
  pygame.mixer.find_channel().play(sound, times)

def playBgMusic(src, times = -1):
  pygame.mixer.music.load(src)
  pygame.mixer.music.play(times)

def reposition_enemies():
  global enemies
  global enemy_bullets
  enemy_bullets = []
  enemies = []
  enemy_n = 24
  enemy_x = 0
  enemy_y = 100
  for i in range(enemy_n):
    if enemy_x >= WIDTH - 300:
      enemy_x = 0
      enemy_y += 40
    enemy_x += 50
    newEnemy = Enemy(enemy_x, enemy_y)
    enemies.append(newEnemy)
    enemy_bullets.append(EnemyBullet())

def reposition_obstacles():
  global obstacles
  obstacles = [[], [], []]
  obstacle_n = 5
  obstacle_x = 100
  for i in range(len(obstacles)):
    for j in range(obstacle_n):
      obstacle_x += 30
      new_obstacle = Obstacle(obstacle_x, HEIGHT - 130, f"{path}assets/images/obstacle.png")
      obstacles[i].append(new_obstacle)
    obstacle_x += 130

class Game:
  def __init__(self):
    self.isActive = False
    self.score = 0
    self.high_score = 0
    self.enemy_die_time = 0
    self.currentSelectedEnemy = ""
    self.attempts = 0
    self.over_count = 0
    self.colors = {
      "primary": "#00B3F2",
      "green": "#32a852",
      "yellow": "#cfca38",
      "red": "#cf3838",
      "player_blue": "#00B3F2"
    }

  def restart(self):
    self.score = 0
    reposition_enemies()
    player.restart()
    player_bullet.restart()
    reposition_obstacles()
    playBgMusic(f"{path}assets/sounds/background-music.mp3")
    self.over_count = 0

  def over(self):
    self.isActive = False
    self.attempts += 1
    self.over_count += 1

class Text:
  def __init__(self, text, x, y, size, color = "white"):
    self.font = pygame.font.Font(f"{path}assets/font/Pixeltype.ttf", size)
    self.text = text
    self.color = color
    self.x = x
    self.y = y
    self.text_surf = ""
    self.text_rect = ""

  def update(self):
    self.text_surf = self.font.render(self.text, False, self.color)
    self.text_rect = self.text_surf.get_rect(center=(self.x, self.y))
    screen.blit(self.text_surf, self.text_rect)

class Sprite:
  def __init__(self, x, y, image, speed = 0):
    self.image = image
    self.sprite_surf = pygame.image.load(self.image).convert_alpha()
    self.sprite_rect = self.sprite_surf.get_rect(center = (x, y))
    self.speed = speed

  def update(self):
    screen.blit(self.sprite_surf, self.sprite_rect)

  def transform(self, scaleSize = 0, rotateDegree = 0):
    self.sprite_surf = pygame.transform.rotozoom(self.sprite_surf, rotateDegree, scaleSize)
    self.sprite_rect = self.sprite_surf.get_rect(center = (self.sprite_rect.x, self.sprite_rect.y))

class Rectangle:
  def __init__(self, x, y, width, height, color = "white"):
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.color = color

  def update(self):
    pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Player(Sprite):
  def __init__(self, x, y):
    self.speed = 3
    self.image = f"{path}assets/images/player/player.png"
    self.health = 1
    super().__init__(x, y, self.image, self.speed)

  def update(self):
    super().update()

    self.movement()
    self.check_health()
    if self.sprite_rect.left <= 0:
      self.sprite_rect.left = 0
    elif self.sprite_rect.right > WIDTH:
      self.sprite_rect.right = WIDTH

  def movement(self):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
      self.sprite_rect.x -= self.speed
    elif keys[pygame.K_RIGHT]:
      self.sprite_rect.x += self.speed

  def check_health(self):
    for i in range(self.health):
      heart_sprite = Sprite(80 + i * 50, HEIGHT + 14, f"{path}assets/images/heart.png")
      heart_sprite.transform(0.4)
      heart_sprite.update()

  def restart(self):
    self.sprite_rect.centerx = WIDTH / 2
    self.health = 1

class Obstacle(Sprite):
  def __init__(self, x, y, image):
    super().__init__(x, y, image)
    self.transform(0.3)
    self.health = 3
    self.healthText = Text(f"{self.health}", self.sprite_rect.centerx, self.sprite_rect.centery, 35, game.colors["primary"])

  def update(self):
    super().update()
    self.healthText.text = f"{self.health}"
    self.healthText.update()

    if self.health == 2:
      self.healthText.color = game.colors["green"]
    elif self.health == 1:
      self.healthText.color = game.colors["yellow"]
    elif self.health == 0:
      self.healthText.color = game.colors["red"]
    elif self.health < 0:
      obstRow.remove(self)

class Bullet(Sprite):
  def __init__(self):
    super().__init__(0, 0, self.image, self.speed)
    self.isShooting = False

  def update(self):
    if self.isShooting:
      super().update()

    # If enemy bullet hits the obstacle
    for obstRow in obstacles:
      for obstacle in obstRow:
        if self.sprite_rect.colliderect(obstacle.sprite_rect):
          self.isShooting = False

          if self.__class__.__name__ == "EnemyBullet":
            obstacle.health -= 1

  def shoot(self):
    self.isShooting = True

class PlayerBullet(Bullet):
  def __init__(self):
    self.speed = 6
    self.image = f"{path}assets/images/player/bullet.png"
    super().__init__()

  def update(self):
    if self.isShooting:
      super().update()
      self.sprite_rect.y -= self.speed

    if self.sprite_rect.y <= 0:
      self.isShooting = False

  def shoot(self):
    if not self.isShooting:
      super().shoot()
      self.restart()
      playsound(f"{path}assets/sounds/laser.mp3", 0.6)

  def restart(self):
    self.sprite_rect.centerx = player.sprite_rect.centerx
    self.sprite_rect.y = player.sprite_rect.top - 5

class EnemyBullet(Bullet):
  def __init__(self):
    self.speed = 5
    self.image = f"{path}assets/images/enemy/bullet.png"
    super().__init__()
    self.sprite_surf = pygame.transform.rotate(self.sprite_surf, 180)

  def update(self):
    if self.isShooting:
      super().update()
      self.sprite_rect.y += self.speed
    else:
      self.sprite_rect.x = 0
      self.sprite_rect.y = 0

    # Game over (Enemy Bullet hits the Player)
    if self.sprite_rect.colliderect(player.sprite_rect):
      player.health -= 1
      self.sprite_rect.x = 0
      self.sprite_rect.y = 0
      if player.health == 0:
        game.over()

    if self.sprite_rect.y >= HEIGHT:
      self.isShooting = False

  def shoot(self):
    if not self.isShooting:
      super().shoot()

      random_enemy = random.choice(enemies)
      self.sprite_rect.centerx = random_enemy.sprite_rect.centerx
      self.sprite_rect.y = random_enemy.sprite_rect.bottom
      playsound(f"{path}assets/sounds/laser.mp3", 0.2)

class Enemy(Sprite):
  def __init__(self, x, y):
    self.speed = 1
    self.go_down_pixels = 40
    self.image = f"{path}assets/images/enemy/enemy.png"
    self.status = "alive"
    super().__init__(x, y, self.image, self.speed)

  def update(self):
    global enemy_bullet_time
    global enemy_die_time
    super().update()

    # If player kills enemy
    if self.status != "exploded" and self.sprite_rect.colliderect(player_bullet.sprite_rect) and player_bullet.isShooting:
      player_bullet.isShooting = False
      game.score += 10
      # High score
      if game.score > game.high_score:
        game.high_score = game.score

      enemy_bullet_time += 20
      pygame.time.set_timer(enemy_bullet_timer, enemy_bullet_time)
      playsound(f"{path}assets/sounds/explosion.mp3", 0.6)
      self.image = f"{path}assets/images/explosion.png"
      self.sprite_surf = pygame.image.load(self.image).convert_alpha()
      self.transform(0.5)
      self.speed = 0
      self.sprite_rect.x += 20
      self.sprite_rect.y += 10
      enemy_die_time = pygame.time.get_ticks()
      self.status = "exploded"
      game.currentSelectedEnemy = self

    if enemy_die_time and pygame.time.get_ticks() - enemy_die_time > 200:
      enemies.remove(game.currentSelectedEnemy)
      enemy_die_time = 0

    # Game Over (collide with player)
    if self.sprite_rect.colliderect(player.sprite_rect) or self.sprite_rect.top >= player.sprite_rect.bottom:
      game.over()

    self.sprite_rect.x += self.speed

class PickUpHeart(Sprite):
  def __init__(self, x, y):
    self.image = f"{path}assets/images/heart.png"
    self.speed = 0
    self.angle = 0
    self.rotSpeed = 2
    super().__init__(x, y, self.image, self.speed)
    self.transform(0.5)

  def update(self):
    # Rotating
    self.angle += 6
    img_copy = pygame.transform.rotate(self.sprite_surf, self.angle)
    screen.blit(img_copy, (self.sprite_rect.x - int(img_copy.get_width() / 2), self.sprite_rect.y - int(img_copy.get_height() / 2)))

  # Game
game = Game()

# Surfaces
background_surf = pygame.image.load(f"{path}assets/images/background.jpg").convert()

# Player
player = Player(WIDTH / 2, 700)
player_bullet = PlayerBullet()

# Texts
score_text = Text("", 100, 50, 50, game.colors["primary"])
high_score_text = Text("", WIDTH - 150, 50, 50, game.colors["primary"])

# Obstacles
obstacles = [[], [], []]
reposition_obstacles()

# Red bottom boundaries
bound1 = Rectangle(0, player.sprite_rect.bottom, 30, 5, "red")
bound2 = Rectangle(WIDTH - 30, player.sprite_rect.bottom, 30, 5, "red")

# Enemy Bullets
enemy_bullets = []

# Enemies
enemies = []
reposition_enemies()

# Pick Up Heart
pickUpHeart = PickUpHeart(WIDTH / 2, HEIGHT / 2)

while True:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()
    if game.isActive:
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
          player_bullet.shoot()
      if event.type == enemy_bullet_timer and enemies:
        random.choice(enemy_bullets).shoot()
    else:
      if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        game.isActive = True
        game.restart()

  screen.blit(background_surf, (0, 0))

  if game.isActive:
    # Scores
    score_text.update()
    score_text.text = f"Score: {game.score}"

    high_score_text.update()
    high_score_text.text = f"High score: {game.high_score}"

    # Obstacles
    for obstRow in obstacles:
      for obstacle in obstRow:
        obstacle.update()

    # Player
    player.update()
    player_bullet.update()

    for enemy_bullet in enemy_bullets:
      enemy_bullet.update()

    # Enemy
    for enemy in enemies:
      enemy.update()

      # Check if went off the screen then move down the army
      if enemy.sprite_rect.right >= WIDTH or enemy.sprite_rect.left <= 0:
        for enemy in enemies:
          enemy.speed = -enemy.speed
          enemy.sprite_rect.y += enemy.go_down_pixels

    # Death Borders
    bound1.update()
    bound2.update()

    # Pick Up Heart
    pickUpHeart.update()

    # pickUpHeart.rotate += 1
    # pickUpHeart.transform(pickUpHeart.scale, pickUpHeart.rotate)


  else:
    title_text = Text("", WIDTH / 2, HEIGHT / 2 - 100, 70, game.colors["player_blue"])

    invader_img = Sprite(WIDTH / 2 + 30, HEIGHT / 2 + 30, f"{path}assets/images/player/player.png")
    invader_img.transform(1.5)

    press_space_text = Text("Press \"space\" bar to start the game", WIDTH / 2, HEIGHT / 2 + 100, 40, game.colors["player_blue"])
    press_space_text.update()

    score_text_number = Text("", WIDTH / 2, HEIGHT / 2 + 150, 50, game.colors["player_blue"])
    high_score_text_number = Text("", WIDTH / 2, HEIGHT / 2 + 190, 50, game.colors["player_blue"])

    if game.attempts == 0:
      title_text.text = "Space Invaders"
    else:
      # Game Over Screen
      game.over_count += 1

      if (game.over_count == 2):
        print(game.over_count)
        playBgMusic(f"{path}assets/sounds/lose.mp3");

      title_text.text = "Game Over"
      score_text_number.text = f"Score: {game.score}"
      high_score_text_number.text = f"High Score: {game.high_score}"

    score_text_number.update()
    high_score_text_number.update()
    invader_img.update()
    title_text.update()

  pygame.display.update()
  clock.tick(60)