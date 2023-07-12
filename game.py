import pygame, sys
import random
from files.get_path import path
from files.debug import debug
from files.read_write_data import read_file, update_file

pygame.init()
WIDTH, HEIGHT = 900, 800

# print(path)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
pygame.display.set_icon(pygame.image.load(f"{path}assets/images/icon.ico"))
clock = pygame.time.Clock()
enemy_n = 0
enemy_die_time = 0
enemy_delay_after_die = 500

enemy_bullet_timer = pygame.USEREVENT + 1
enemy_bullet_time = 500
pygame.time.set_timer(enemy_bullet_timer, enemy_bullet_time)

boss_alien_primary_bullet_timer = pygame.USEREVENT + 1
boss_alien_primary_bullet_time = 1000
pygame.time.set_timer(boss_alien_primary_bullet_timer, boss_alien_primary_bullet_time)

boss_alien_secondary_bullet_timer = pygame.USEREVENT + 1
boss_alien_secondary_bullet_time = 600
pygame.time.set_timer(boss_alien_secondary_bullet_timer, boss_alien_secondary_bullet_time)


def levelEntranceTextCreate(text, currentLevel):
    global level_entrance_text, level_entrance_text_name, text_delay_timer, counter
    level_entrance_text = Text(f"Level {currentLevel}/{game.levels_n}", WIDTH + 40, HEIGHT / 2 - 50, 40)
    level_entrance_text_name = Text(text, WIDTH + 40, HEIGHT / 2, 90, game.colors["primary"])
    text_delay_timer = 110
    counter = 0

    player.rect.x = WIDTH / 2 - player.rect.width / 2
    game.currentLevel += 1

def levelEntranceTextUpdate():
    global text_delay_timer
    global counter

    if text_delay_timer > 0:
        text_delay_timer -= 1

    level_entrance_text.update()
    level_entrance_text_name.update()

    level_entrance_text.x -= 5
    level_entrance_text_name.x -= 5

    if text_delay_timer <= 0:
        level_entrance_text.x -= 1
        level_entrance_text_name.x -= 1
    else:
        if level_entrance_text.x <= WIDTH / 2:
            level_entrance_text.x = WIDTH / 2
        if level_entrance_text_name.x <= WIDTH / 2:
            level_entrance_text_name.x = WIDTH / 2

    # If the Level Entrance Text goes off the screen
    if level_entrance_text_name.x <= -200:
        counter += 1
        if counter == 2:
            game.resume()
    else:
        game.pause()

def playsound(src, volume=1, times=0):
    sound = pygame.mixer.Sound(f"{path}assets/sounds/{src}")
    sound.set_volume(volume)
    pygame.mixer.find_channel().play(sound, times)

def playBgMusic(src, times=-1, volume=0.6):
    pygame.mixer.music.load(f"{path}assets/sounds/{src}")
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(times)

def reposition_enemies():
    global enemies, enemy_bullets
    enemy_bullets = []
    enemies = []
    enemy_x = 0
    enemy_y = 96
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
        obstacle_x += 160

def reposition_asteroids():
    global asteroids

    asteroids_n = 5
    for i in range(asteroids_n):
        new_asteroid = MovingObject(False, 0.2, f"{path}assets/images/asteroids/asteroid-{random.randint(1, 2)}.png",
                                    "explosion.mp3", 100, 200, 600, game.speeds["Asteroid"]["Min"],
                                    game.speeds["Asteroid"]["Max"], 1.5, 3)
        asteroids.append(new_asteroid)

def reposition_boss_aliens_primary():
    global boss_aliens_primary_arr, boss_aliens_primary_bullets_arr
    boss_aliens_primary_arr = [[200, -170], [200, -30], [WIDTH - 80, -170], [WIDTH - 80, -30]]
    boss_aliens_primary_bullets_arr = []
    scaleSize = 0.5
    for i in range(len(boss_aliens_primary_arr)):
        boss_aliens_primary_arr[i] = BossAlienHelper(boss_aliens_primary_arr[i][0], boss_aliens_primary_arr[i][1],
                                                     scaleSize)
        boss_aliens_primary_bullets_arr.append(BossAlienBullet("primary_alien"))

def reposition_boss_aliens_secondary():
    global boss_aliens_secondary_arr, boss_aliens_secondary_bullets_arr
    boss_aliens_secondary_arr = []
    boss_aliens_secondary_bullets_arr = []

    boss_alien_secondary_n = 11
    x = 125
    for i in range(boss_alien_secondary_n):
        x += 65
        boss_aliens_secondary_arr.append(BossAlienHelper(x, 0, 0.3))  # y = 470
        boss_aliens_secondary_bullets_arr.append(BossAlienBullet("secondary_alien"))

def reposition_boss_aliens_primary_hp_bars():
    global boss_aliens_primary_hp_bars_arr
    boss_aliens_primary_hp_bars_arr = []
    for i in range(len(boss_aliens_primary_arr)):
        new_hp_bar = HealthBar(10, 100, 100, 15, boss_aliens_primary_arr[i].rect.x - 20,
                               boss_aliens_primary_arr[i].rect.y - 20)
        boss_aliens_primary_hp_bars_arr.append(new_hp_bar)

def reposition_boss_aliens_secondary_hp_bars():
    global boss_aliens_secondary_hp_bars_arr
    boss_aliens_secondary_hp_bars_arr = []
    for i in range(len(boss_aliens_secondary_arr)):
        new_hp_bar = HealthBar(1, 3, 45, 10, boss_aliens_secondary_arr[i].rect.x - 5,
                               boss_aliens_secondary_arr[i].rect.y - 20, 2, 30)
        boss_aliens_secondary_hp_bars_arr.append(new_hp_bar)

class Game:
    def __init__(self):
        self.isActive = False
        self.isPaused = True
        self.speeds = {
            "BackgroundCircle": random.uniform(0.3, 0.7),
            "Player": 3,
            "PlayerBullet": 6,
            "Enemy": 1,
            "EnemyBullet": 5,
            "Heart": {"Min": 1, "Max": 2},
            "Asteroid": {"Min": 1, "Max": 3.5},
            "BossLevelAlien": 2,
            "BossLevelAlienBullet": 6,
        }
        self.levels_n = 2
        self.currentLevel = 1
        self.score = 0
        self.high_score = read_file(f"{path}data.json", "high_score")
        self.enemy_die_time = 0
        self.currentSelectedEnemy = ""
        self.attempts = 0
        self.over_count = 0
        self.timeAfterKillingEnemies1 = 0
        self.colors = {
            "primary": "#00B3F2",
            "green": "#32a852",
            "yellow": "#cfca38",
            "red": "#cf3838",
            "player_blue": "#00B3F2"
        }
        self.boss_alien_secondary_max_y = 410

    def restart(self):
        self.score = 0
        reposition_enemies()
        player.restart()
        player_bullet.restart()
        reposition_obstacles()
        heart.restart()

        # playBgMusic("background-music.mp3")
        playBgMusic("boss_level.mp3")

        self.over_count = 0
        self.timeAfterKillingEnemies1 = 0
        self.currentLevel = 1

        # Level Entrance Texts
        levelEntranceTextCreate("CASUAL", 1)

    def over(self):
        self.isActive = False
        self.attempts += 1
        self.over_count += 1

    def boss_level(self):
        global bound1, bound2, obstacles
        levelEntranceTextCreate("BOSS LEVEL", 2)
        playBgMusic("boss_level.mp3", 1)
        reposition_obstacles()
        for obstRow in obstacles:
            for obstacle in obstRow:
                obstacle.health = 15

        player.health += 2

    def pause(self):
        global enemy_bullet_time, boss_alien_bullet, boss_alien_primary_bullet_time, boss_alien_secondary_bullet_time, boss_aliens_primary_arr, boss_aliens_secondary_arr
        self.isPaused = True

        player.speed = 0
        player_bullet.speed = 0
        player_bullet.rect.x = 1000

        for enemy in enemies:
            enemy.speed = 0
        for bullet in enemy_bullets:
            bullet.speed = 0
            bullet.rect.x = 1000
        heart.speed = 0

        boss_alien.speed = 0
        boss_alien_bullet.speed = 0

        for boss_aliens_primary in boss_aliens_primary_arr:
            boss_aliens_primary.speed = 0

        for boss_aliens_secondary in boss_aliens_secondary_arr:
            boss_aliens_secondary.speed = 0

        for boss_aliens_primary_bullet in boss_aliens_primary_bullets_arr:
            boss_aliens_primary_bullet.speed = 0

        for boss_aliens_secondary_bullet in boss_aliens_secondary_bullets_arr:
            boss_aliens_secondary_bullet.speed = 0

        enemy_bullet_time = 0
        pygame.time.set_timer(enemy_bullet_timer, enemy_bullet_time)

        boss_alien_primary_bullet_time = 0
        boss_alien_secondary_bullet_time = 0
        pygame.time.set_timer(boss_alien_primary_bullet_timer, boss_alien_primary_bullet_time)
        pygame.time.set_timer(boss_alien_secondary_bullet_timer, boss_alien_secondary_bullet_time)

    def resume(self):
        global enemy_bullet_time, boss_alien_bullet, boss_alien_primary_bullet_time, boss_alien_secondary_bullet_time, boss_aliens_primary_arr, boss_aliens_secondary_arr
        self.isPaused = False

        player.speed = game.speeds["Player"]
        player_bullet.speed = game.speeds["PlayerBullet"]
        for enemy in enemies:
            enemy.speed = game.speeds["Enemy"]
        for bullet in enemy_bullets:
            bullet.speed = game.speeds["EnemyBullet"]
        heart.speed = random.choice([random.uniform(-heart.limits["speed"]["max"], -heart.limits["speed"]["min"]),
                                     random.uniform(heart.limits["speed"]["min"], heart.limits["speed"]["max"])])

        boss_alien.speed = game.speeds["BossLevelAlien"]
        boss_alien_bullet.speed = game.speeds["BossLevelAlienBullet"]

        for boss_aliens_primary in boss_aliens_primary_arr:
            boss_aliens_primary.speed = game.speeds['BossLevelAlien']

        for boss_aliens_secondary in boss_aliens_secondary_arr:
            boss_aliens_secondary.speed = game.speeds['BossLevelAlien']

        for boss_aliens_primary_bullet in boss_aliens_primary_bullets_arr:
            boss_aliens_primary_bullet.speed = game.speeds['BossLevelAlienBullet']

        for boss_aliens_secondary_bullet in boss_aliens_secondary_bullets_arr:
            boss_aliens_secondary_bullet.speed = game.speeds['BossLevelAlienBullet']

        enemy_bullet_time = 500
        pygame.time.set_timer(enemy_bullet_timer, enemy_bullet_time)

        boss_alien_primary_bullet_time = 1000
        boss_alien_secondary_bullet_time = 600
        pygame.time.set_timer(boss_alien_primary_bullet_timer, boss_alien_primary_bullet_time)
        pygame.time.set_timer(boss_alien_secondary_bullet_timer, boss_alien_secondary_bullet_time)

    def updateGameScore(self, score = 10):
        self.score += score

        # High score
        if self.score > self.high_score:
            update_file(f"{path}data.json", "high_score", self.score)
            self.high_score = self.score

class Text:
    def __init__(self, text, x, y, size, color="white"):
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
    def __init__(self, x, y, image, speed=0):
        self.image = image
        self.sprite_surf = pygame.image.load(self.image).convert_alpha()
        self.rect = self.sprite_surf.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        screen.blit(self.sprite_surf, self.rect)

    def transform(self, scaleSize=0, rotateDegree=0):
        self.sprite_surf = pygame.transform.rotozoom(self.sprite_surf, rotateDegree, scaleSize)
        self.rect = self.sprite_surf.get_rect(center=(self.rect.x, self.rect.y))

class Rectangle:
    def __init__(self, x, y, width, height, color="white"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def update(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Player(Sprite):
    def __init__(self, x, y):
        self.speed = 0
        self.image = f"{path}assets/images/player/player.png"
        self.health = 1
        super().__init__(x, y, self.image, self.speed)

    def update(self):
        super().update()

        self.movement()
        self.check_health()

        # Collision with walls
        if self.rect.left <= 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

    def check_health(self):
        for i in range(self.health):
            heart_sprite = Sprite(80 + i * 50, HEIGHT + 14, f"{path}assets/images/heart.png")
            heart_sprite.transform(0.4)
            heart_sprite.update()

    def restart(self):
        self.rect.centerx = WIDTH / 2
        self.health = 1

class Obstacle(Sprite):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.transform(0.3)
        self.health = 5
        self.healthText = Text(f"{self.health}", self.rect.centerx, self.rect.centery, 35, game.colors["primary"])

    def update(self):
        super().update()
        self.healthText.text = f"{self.health}"
        self.healthText.update()

        if self.health >= 3:
            self.healthText.color = game.colors["primary"]
        elif self.health == 2:
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

        else:
            self.rect.x = 0
            self.rect.y = 0

        if self.__class__.__name__ == "EnemyBullet" or self.__class__.__name__ == "BossAlienBullet":
            if self.isShooting:
                self.rect.y += self.speed
            else:
                self.rect.x = 0
                self.rect.y = 0

            # Enemy Bullet or BossAlien Bullet hits the Player
            if self.rect.colliderect(player.rect):
                player.health -= 1
                self.rect.x = -100
                self.rect.y = 0
                if player.health == 0:
                    game.over()
                else:
                    playsound("hurt.mp3")

            if self.rect.y >= HEIGHT:
                self.isShooting = False

        # If enemy and player bullet hits the obstacle
        for obstRow in obstacles:
            for obstacle in obstRow:
                if self.rect.colliderect(obstacle.rect):
                    self.isShooting = False

                    if self.__class__.__name__ == "EnemyBullet" or self.__class__.__name__ == "BossAlienBullet":
                        obstacle.health -= 1

        # If player bullet hits boss alien and his helpers
        if self.__class__.__name__ == "PlayerBullet":

            if self.rect.colliderect(boss_alien.rect):
                boss_alien_hp_bar.get_damage()
                self.isShooting = False

            for i in range(len(boss_aliens_primary_arr)):
                i=i-1
                if self.rect.colliderect(boss_aliens_primary_arr[i].rect):
                    boss_aliens_primary_hp_bars_arr[i].get_damage()
                    self.isShooting = False

                    if boss_aliens_primary_hp_bars_arr[i].current_health <= 0:
                        boss_aliens_primary_arr.remove(boss_aliens_primary_arr[i])
                        boss_aliens_primary_hp_bars_arr[i].current_health = 0
                        boss_aliens_primary_hp_bars_arr.remove(boss_aliens_primary_hp_bars_arr[i])
                        boss_aliens_primary_arr[i].die()

            for i in range(len(boss_aliens_secondary_arr)):
                i=i-1
                if self.rect.colliderect(boss_aliens_secondary_arr[i].rect):
                    boss_aliens_secondary_hp_bars_arr[i].get_damage()
                    self.isShooting = False
                    print(i)


                    if boss_aliens_secondary_hp_bars_arr[i].current_health <= 0:
                        boss_aliens_secondary_arr.remove(boss_aliens_secondary_arr[i])
                        boss_aliens_secondary_hp_bars_arr[i].current_health = 0
                        boss_aliens_secondary_hp_bars_arr.remove(boss_aliens_secondary_hp_bars_arr[i])
                        boss_aliens_secondary_arr[i].die()


    def shoot(self):
        self.isShooting = True

class PlayerBullet(Bullet):
    def __init__(self):
        self.speed = 0
        self.image = f"{path}assets/images/player/bullet.png"
        super().__init__()

    def update(self):
        if self.isShooting:
            super().update()
            self.rect.y -= self.speed

        if self.rect.y <= 0:
            self.isShooting = False

    def shoot(self):
        if not self.isShooting:
            super().shoot()
            self.restart()
            playsound("laser.mp3", 0.6)

    def restart(self):
        self.rect.centerx = player.rect.centerx
        self.rect.y = player.rect.top - 5

class EnemyBullet(Bullet):
    def __init__(self):
        self.speed = 0
        self.image = f"{path}assets/images/enemy/bullet.png"
        super().__init__()
        self.sprite_surf = pygame.transform.rotate(self.sprite_surf, 180)

    def shoot(self):
        if not self.isShooting:
            super().shoot()

            random_enemy = random.choice(enemies)
            self.rect.centerx = random_enemy.rect.centerx
            self.rect.y = random_enemy.rect.bottom
            playsound("laser.mp3", 0.4)

class Enemy(Sprite):    
    def __init__(self, x, y):
        self.go_down_pixels = 30
        self.decreaseBulletTimerAtY = 400
        self.bulletTimerDecreased = False
        self.image = f"{path}assets/images/enemy/enemy.png"
        self.status = "alive"
        self.current_frame = 0
        self.speed = 0

        super().__init__(x, y, self.image, self.speed)

    def update(self):
        global enemy_bullet_time, enemy_die_time, enemies
        super().update()

        # Do not shoot any bullet if enemy reaches certain Y coordinate
        if game.isPaused == False and self.rect.y > self.decreaseBulletTimerAtY and self.bulletTimerDecreased == False:
            enemy_bullet_time = 0
            pygame.time.set_timer(enemy_bullet_timer, enemy_bullet_time)
            self.bulletTimerDecreased = True

        # If player kills enemy
        if self.status != "dead" and self.rect.colliderect(player_bullet.rect) and player_bullet.isShooting:
            player_bullet.isShooting = False
            player_bullet.restart()
            game.updateGameScore()

            playsound("explosion.mp3", 1)

            # Explosion
            self.image = f"{path}assets/images/explosion/7.png"
            self.sprite_surf = pygame.image.load(self.image).convert_alpha()
            self.transform(0.15)

            self.speed = 0
            self.rect.x += 20
            self.rect.y += 20
            enemy_die_time = pygame.time.get_ticks()
            self.status = "dead"
            game.currentSelectedEnemy = self
        else:
            self.rect.x += self.speed

        if enemy_die_time and pygame.time.get_ticks() - enemy_die_time > enemy_delay_after_die:
            enemies.remove(game.currentSelectedEnemy)
            enemy_die_time = 0

            # Player kills all enemies:
            if len(enemies) == 0:
                game.boss_level()

        # Game Over (collide with player)
        if self.rect.colliderect(player.rect) or self.rect.top >= player.rect.bottom:
            game.over()

class MovingObject(Sprite):
    def __init__(self, isHealth, scaleSize, image, hitSoundEffect, xMax, yMin, yMax, speedMin, speedMax, rotSpeedMin,
                 rotSpeedMax):
        self.isHealth = isHealth
        self.hitSoundEffect = hitSoundEffect
        self.limits = {
            "x": {"max": xMax},
            "y": {"min": yMin, "max": yMax},
            "speed": {"min": speedMin, "max": speedMax},
            "rotSpeed": {"min": rotSpeedMin, "max": rotSpeedMax}
        }
        self.x = random.choice([-self.limits["x"]["max"], WIDTH + self.limits["x"]["max"]])
        self.y = random.uniform(self.limits["y"]["min"], self.limits["y"]["max"])
        self.image = image
        self.speed = random.choice([random.uniform(-self.limits["speed"]["max"], -self.limits["speed"]["min"]),
                                    random.uniform(self.limits["speed"]["min"], self.limits["speed"]["max"])])
        self.angle = 0
        self.rotSpeed = random.choice([random.uniform(-self.limits["rotSpeed"]["max"], -self.limits["rotSpeed"]["min"]),
                                       random.uniform(self.limits["rotSpeed"]["min"], self.limits["rotSpeed"]["max"])])
        super().__init__(self.x, self.y, self.image, self.speed)
        self.transform(scaleSize)

    def update(self):
        # Check if Moving Object doesn't get out of boundaries to return back to the playing screen
        if self.rect.x > self.limits["x"]["max"] + WIDTH or self.rect.x < -self.limits["x"]["max"]:
            self.speed = -self.speed

        # Movement
        self.rect.x += self.speed

        # Rotating and drawing an image
        self.angle += self.rotSpeed
        img_copy = pygame.transform.rotate(self.sprite_surf, self.angle)
        screen.blit(img_copy,
                    (self.rect.x - int(img_copy.get_width() / 2), self.rect.y - int(img_copy.get_height() / 2)))

        # When player shoots at the Object
        if pygame.sprite.collide_circle(self, player_bullet):
            player_bullet.isShooting = False
            player_bullet.restart()
            self.restart()
            playsound(self.hitSoundEffect, 0.6)
            if self.isHealth:
                player.health += 1

    def restart(self):
        self.rect.x = random.choice([-self.limits["x"]["max"], WIDTH + self.limits["x"]["max"]])
        self.rect.y = random.uniform(self.limits["y"]["min"], self.limits["y"]["max"])
        self.speed = random.choice([random.uniform(-self.limits["speed"]["max"], -self.limits["speed"]["min"]),
                                    random.uniform(self.limits["speed"]["min"], self.limits["speed"]["max"])])
        self.rotSpeed = random.choice([random.uniform(-self.limits["rotSpeed"]["max"], -self.limits["rotSpeed"]["min"]),
                                       random.uniform(self.limits["rotSpeed"]["min"], self.limits["rotSpeed"]["max"])])

class BackgroundCircle:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.radius = ""
        self.speed = ""
        self.restart()

    def update(self):
        self.y += self.speed

        if self.y > HEIGHT + self.radius:
            self.restart()
            self.y = -self.radius

        pygame.draw.circle(screen, "white", (self.x, self.y), self.radius)

    def restart(self):
        self.radius = random.randint(1, 2)
        self.speed = game.speeds["BackgroundCircle"]
        self.x = random.uniform(self.radius, WIDTH - self.radius)
        self.y = random.uniform(self.radius, HEIGHT - self.radius)

class HealthBar:
    def __init__(self, damage_amount, current_health, health_bar_length, hp_bar_height, x_pos, y_pos, border_size=3, text_size=35):
        self.damage_amount = damage_amount
        self.current_health = current_health
        self.health_bar_length = health_bar_length
        self.health_ratio = self.current_health / self.health_bar_length
        self.x_pos, self.y_pos = x_pos, y_pos
        self.health_bar_height = hp_bar_height
        self.text = ""
        self.max_health = self.current_health // self.damage_amount
        self.border_size = border_size
        self.text_size = text_size

    def get_damage(self, amount=1):
        self.current_health -= amount * self.damage_amount
        playsound("hurt.mp3", 0.6)

    def basic_health(self):
        # First stage
        if self.current_health // self.damage_amount > (self.max_health // 3) * 2:
            pygame.draw.rect(screen, (48, 199, 48),
                             (self.x_pos, self.y_pos, self.current_health / self.health_ratio, self.health_bar_height))
        # Second stage
        elif self.current_health // self.damage_amount > (self.max_health // 3):
            pygame.draw.rect(screen, (255, 106, 0),
                             (self.x_pos, self.y_pos, self.current_health / self.health_ratio, self.health_bar_height))
        # Third stage
        else:
            pygame.draw.rect(screen, (255, 0, 0),
                             (self.x_pos, self.y_pos, self.current_health / self.health_ratio, self.health_bar_height))

        # pygame.draw.rect(screen, (255, 106, 0), (self.x_pos, self.y_pos, self.current_health / self.health_ratio, self.health_bar_height))
        pygame.draw.rect(screen, (255, 255, 255)
                         , (self.x_pos, self.y_pos, self.health_bar_length, self.health_bar_height), self.border_size)

    def update(self):
        self.basic_health()
        self.text = Text(f"{self.current_health // self.damage_amount}/{self.max_health}", self.x_pos + 20,
                         self.y_pos - 10, self.text_size)
        self.text.update()

class BossAlien(Sprite):
    def __init__(self):
        self.image = f"{path}assets/images/boss-level/boss.png"
        super().__init__(WIDTH - 140, -20, self.image)
        self.transform(0.5)
        self.speed = 0
        self.status = "alive"

    def update(self):
        global boss_alien_hp_bar, boss_alien_bullet
        super().update()

        # Going downwards animation at the beginning (level 2)
        self.rect.y += self.speed
        if self.rect.y >= 120:
            self.speed = 0
        else:
            boss_alien_hp_bar = HealthBar(4, 240, 200, 25, boss_alien.rect.x + 50, boss_alien.rect.y - 40)

        if boss_alien_hp_bar.current_health <= 0:
            self.status = "dead"

class BossAlienHelper(Sprite):
    def __init__(self, x, y, scale):
        self.image = f"{path}assets/images/boss-level/boss_alien_primary.png"
        super().__init__(x, y, self.image)
        self.transform(scale)
        self.speed = 0
        self.status = "alive"

    def update(self):
        super().update()
        self.rect.y += self.speed

    def die(self):
        playsound("explosion.mp3")
        game.updateGameScore()

class BossAlienBullet(Bullet):
    def __init__(self, type):
        self.speed = 0
        self.image = f"{path}assets/images/boss-level/laser.png"
        super().__init__()
        self.type = type
        if self.type == "boss_alien":
            self.transform(7)
        elif self.type == "primary_alien":
            self.transform(4)
        elif self.type == "secondary_alien":
            self.transform(3)

    def shoot(self):
        if not self.isShooting:
            super().shoot()

            if self.type == "boss_alien":
                possible_coordinates = [boss_alien.rect.centerx - boss_alien.rect.width / 2 + 25,
                                        boss_alien.rect.centerx + boss_alien.rect.width / 2 - 25]
                self.rect.centerx = random.choice(possible_coordinates)
                self.rect.y = boss_alien.rect.bottom
                playsound("laser.mp3", 1)
            elif self.type == "primary_alien":
                random_boss_alien_primary = random.choice(boss_aliens_primary_arr)
                self.rect.centerx = random_boss_alien_primary.rect.centerx
                self.rect.y = random_boss_alien_primary.rect.bottom
                playsound("laser.mp3", 0.5)
            elif self.type == "secondary_alien":
                random_boss_alien_secondary = random.choice(boss_aliens_secondary_arr)
                self.rect.centerx = random_boss_alien_secondary.rect.centerx
                self.rect.y = random_boss_alien_secondary.rect.bottom
                playsound("laser.mp3", 0.3)

# Game
game = Game()

# Background
background_surf = pygame.image.load(f"{path}assets/images/background.jpg").convert()
# background_surf = pygame.transform.rotozoom(background_surf, 0, 0.7)

backgroundCircles = []
for i in range(60):
    backgroundCircles.append(BackgroundCircle())

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
bound1 = Rectangle(0, player.rect.bottom, 30, 5, "red")
bound2 = Rectangle(WIDTH - 30, player.rect.bottom, 30, 5, "red")

# Enemy Bullets
enemy_bullets = []

# Enemies
enemies = []
reposition_enemies()

# Power Up Heart
heart = MovingObject(True, 0.3, f"{path}assets/images/heart.png", "powerup.mp3", 4000, 400, 600, game.speeds["Heart"]["Min"], game.speeds["Heart"]["Max"], 1.5, 5)

# Asteroid
asteroids = []
reposition_asteroids()

# Boss Alien
boss_alien = BossAlien()
boss_alien_bullet = BossAlienBullet("boss_alien")
boss_alien_hp_bar = HealthBar(4, 240, 200, 25, 1000, 1000)
reposition_boss_aliens_primary()
reposition_boss_aliens_primary_hp_bars()
reposition_boss_aliens_secondary()
reposition_boss_aliens_secondary_hp_bars()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game.isActive:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player_bullet.shoot()
                if event.key == pygame.K_DOWN:
                    boss_alien_hp_bar.get_damage()
                if event.key == pygame.K_UP:
                    boss_aliens_primary_hp_bars_arr[0].get_damage()
            if event.type == enemy_bullet_timer and enemies:
                random.choice(enemy_bullets).shoot()
            if event.type == boss_alien_primary_bullet_timer and boss_aliens_primary_bullets_arr:
                random.choice(boss_aliens_primary_bullets_arr).shoot()
            if event.type == boss_alien_secondary_bullet_timer and boss_aliens_secondary_bullets_arr:
                random.choice(boss_aliens_secondary_bullets_arr).shoot()
        else:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game.isActive = True
                game.restart()

    # Background
    screen.blit(background_surf, (0, 0))
    for circle in backgroundCircles:
        circle.update()

    if game.isActive:
        debug(f"Level: {game.currentLevel}")

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

        # Pick Up Heart
        heart.update()

        # debug(f"Player_bullet x: {player_bullet.rect.x}, y: {player_bullet.rect.y}", 10, 80)
        debug(f"Heart x: {heart.rect.x} | {boss_aliens_secondary_arr[3].status}", 60, 750)
        # debug(f"Player speed: {player.speed}", 10, 80)
        # debug(f"Boss Alien: {boss_alien.rect.y}", 10, 160)
        # debug(f"Boss Primary 1: {boss_aliens_primary_arr[0].rect.y}", 10, 260)
        # debug(f"Boss Primary 1 speed: {boss_aliens_primary_arr[0].speed}", 10, 300)
        # debug(f"Boss Alien speed: {boss_alien.speed}", 10, 340)

        # Asteroids
        for i in range(len(asteroids)):
            asteroids[i].update()
            # debug(f"Asteroid {i}: x: {asteroids[i].rect.x}, Asteroid {i} speed: {asteroids[i].speed}", 10, 100 + i * 20)

        if game.currentLevel == 1:
            # Enemy
            for enemy in enemies:
                enemy.update()

                # Check if went off the screen then move down the army
                if enemy.status != "dead" and enemy.rect.right >= WIDTH or enemy.rect.left <= 0:
                    for enemy in enemies:
                        enemy.speed = -enemy.speed
                        enemy.rect.y += enemy.go_down_pixels

            # Death Borders
            bound1.update()
            bound2.update()

        elif game.currentLevel == 2:
            boss_alien.update()
            boss_alien_bullet.update()
            boss_alien_hp_bar.update()

            if not boss_alien_bullet.isShooting:
                boss_alien_bullet.shoot()

            # Boss Alien PRIMARY going downwards animation
            for i in range(len(boss_aliens_primary_arr)):
                if boss_aliens_primary_arr[i].status == "alive":
                    boss_aliens_primary_arr[i].update()
                    boss_aliens_primary_bullets_arr[i].update()
                    boss_aliens_primary_hp_bars_arr[i].update()

                    coords = [[200, 120], [200, 270], [WIDTH - 80, 120], [WIDTH - 80, 270]]

                    if boss_aliens_primary_arr[i].rect.y >= coords[i][1]:
                        boss_aliens_primary_arr[i].speed = 0
                    else:
                        reposition_boss_aliens_primary_hp_bars()

            # Boss Alien SECONDARY going downwards animation
            for i in range(len(boss_aliens_secondary_arr)):
                  boss_aliens_secondary_arr[i].update()
                  boss_aliens_secondary_bullets_arr[i].update()
                  boss_aliens_secondary_hp_bars_arr[i].update()

                  if boss_aliens_secondary_arr[i].rect.y >= game.boss_alien_secondary_max_y:
                      boss_aliens_secondary_arr[i].speed = 0
                  else:
                      reposition_boss_aliens_secondary_hp_bars()

        # Level entrance text
        levelEntranceTextUpdate()
    else:
        title_text = Text("", WIDTH / 2, HEIGHT / 2 - 100, 70, game.colors["player_blue"])

        invader_img = Sprite(WIDTH / 2 + 30, HEIGHT / 2 + 30, f"{path}assets/images/player/player.png")
        invader_img.transform(1.5)

        press_space_text = Text("Press \"space\" bar to start the game", WIDTH / 2, HEIGHT / 2 + 100, 40,
                                game.colors["player_blue"])
        press_space_text.update()

        score_text_number = Text("", WIDTH / 2, HEIGHT / 2 + 150, 50, game.colors["player_blue"])
        high_score_text_number = Text(f"High Score: {game.high_score}", WIDTH / 2, HEIGHT / 2 + 190, 50,
                                      game.colors["player_blue"])

        if game.attempts == 0:
            title_text.text = "Space Invaders"
        else:
            # Game Over Screen
            game.over_count += 1

            if (game.over_count == 2):
                print("lose")
                playBgMusic("lose.mp3")

            title_text.text = "Game Over"
            score_text_number.text = f"Score: {game.score}"

        score_text_number.update()
        high_score_text_number.update()
        invader_img.update()
        title_text.update()

    pygame.display.update()
    screen.fill("black")
    clock.tick(60)
