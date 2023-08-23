import pygame
import sys
import random
import os
from PIL import Image
import pygame_gui

pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(8)


game_dir = os.path.dirname(__file__)
assets_dir = os.path.join(game_dir, "assets")
entity_dir = os.path.join(assets_dir, "entity")
sound_dir = os.path.join(assets_dir, "sound")

screen_width = 800
screen_height = 500
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Astro Blaster Game")

#gui_man = pygame_gui.UIManager((screen_width, screen_height))

#label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, 10, 200, 30), text="Score:", manager=gui_man)
#button_rect = pygame.Rect(10, 50, 100, 30)
#button = pygame_gui.elements.UIButton(relative_rect=button_rect, text="Click Me", manager=gui_man)
white = (255, 255, 255)
yellow = (255,255,0)
red = (255,0,0)


player_width = 40
player_height = 40
player_x = (screen_width - player_width) / 2
player_y = screen_height - player_height - 20
player_speed = 8

bullet_width = 10
bullet_height = 25
bullet_speed = 25
bullets = []

enemy_width = 50
enemy_height = 50
enemies = []

player_image = pygame.image.load(os.path.join(entity_dir, "player.png"))
enemy_image = pygame.image.load(os.path.join(entity_dir, "enemy.png"))
bullet_image = pygame.image.load(os.path.join(entity_dir, "bullet.png"))
explosion_sheet = pygame.image.load(os.path.join(entity_dir, "explosion.png"))

frame_size = explosion_sheet.get_rect().size
frame_width = 50
frame_height = 50
frames_per_row = 5
frames_per_column = 2

def get_frame(row, col):
    x = col*frame_width
    y = row*frame_height
    frame = explosion_sheet.subsurface(pygame.Rect(x,y,frame_width, frame_height))
    return frame

explosion_frames = []
for row in range(frames_per_column):
    for col in range(frames_per_row):
        frame = get_frame(row, col)
        explosion_frames.append(frame)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = explosion_frames[:]
        self.image = self.frames.pop(0)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.frame_delay = 5  
        self.frame_timer = self.frame_delay

    def update(self):
        if self.frame_timer <= 0:
            if self.frames:
                self.image = self.frames.pop(0)
                self.frame_timer = self.frame_delay
            else:
                self.kill()
        else:
            self.frame_timer -= 1

player_image = pygame.transform.scale(player_image, (player_width, player_height))
enemy_image = pygame.transform.scale(enemy_image, (enemy_width, enemy_height))
bullet_image_original = pygame.transform.scale(bullet_image, (bullet_width, bullet_height))

background_image = pygame.image.load(os.path.join(assets_dir, "background.jpg"))
background_y = 0
background_scroll_speed = 0

high_score = 0
score = 0
font = pygame.font.Font(None, 36)

def draw_score():
    score_text = font.render("Score: " + str(score), True, white)
    screen.blit(score_text, (10,10))

def draw_high_score():
    score_text = font.render("High Score: " + str(high_score), True, white)
    screen.blit(score_text, (10,80))

def draw_lives():
    score_text = font.render("Lives: " + str(player_lives), True, white)
    screen.blit(score_text, (10, 40))

def create_enemy():
    enemy_x = random.randint(0, screen_width - enemy_width)
    enemy_y = 0
    enemies.append(pygame.Rect(enemy_x, enemy_y, enemy_width, enemy_height))

hit_sound = pygame.mixer.Sound(os.path.join(sound_dir, "hit.wav"))

pygame.mixer.music.load(os.path.join(sound_dir, "backmusic.wav"))
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1)

power_ups = []
power_up_width = 40
power_up_height = 40

player_rect = pygame.Rect(player_x, player_y, player_width, player_height)  

def create_power_up():
    power_up_x = random.randint(0, screen_width - power_up_width)
    power_up_y = 0
    power_ups.append(pygame.Rect(power_up_x, power_up_y, power_up_width, power_up_height))

for enemy in enemies:
    for power_up in power_ups:
        if player_rect.colliderect(power_up):
            power_ups.remove(power_up)

clock = pygame.time.Clock()
while True:
    player_lives = 3
    game_over = False
    explosion_group = pygame.sprite.Group()
    while not game_over:
        dt = clock.tick(60)/1200.0 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            """
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == button:
                        print("Button Clicked!")
            gui_man.process_events(event)
            """
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet_x = player_x + player_width / 2 - bullet_width / 2
                    bullet_y = player_y
                    hit_sound.play()
                    bullets.append(pygame.Rect(bullet_x, bullet_y, bullet_width, bullet_height))

        #gui_man.update(dt)
        background_y += background_scroll_speed
        if background_y >= screen_height:
            background_y = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
            player_x += player_speed

        bullets_to_remove = []
        for bullet in bullets:
            bullet.y -= bullet_speed
            if bullet.y < 0:
                bullets_to_remove.append(bullet)
        for bullet in bullets_to_remove:
            bullets.remove(bullet)

        if random.randint(0,100) < 2:
            create_enemy()

        enemy_speed = 500


        enemies_to_remove = []
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy_width, enemy_height)
            if player_rect.colliderect(enemy_rect):
                player_lives -= 1
                enemies.remove(enemy)

            enemy.y += enemy_speed * dt  # Move enemy down
            if enemy.y > screen_height:
                enemies_to_remove.append(enemy)

        for bullet in bullets:
            for enemy in enemies:
                if bullet.colliderect(enemy):
                    bullets.remove(bullet)
                    enemies_to_remove.append(enemy)
                    explosion = Explosion(enemy.x, enemy.y)
                    explosion_group.add(explosion)
                    explosion_sound = pygame.mixer.Sound(os.path.join(sound_dir, "explosionsound.wav"))
                    explosion_sound.set_volume(0.7)
                    explosion_sound.play()
                    score += 10

        for enemy in enemies_to_remove:
            enemies.remove(enemy)

        screen.fill((0, 0, 0))
        screen.blit(background_image, (0, background_y)) 
    
        screen.blit(player_image, (player_x, player_y))
        
        for bullet in bullets:
            screen.blit(bullet_image, (bullet.x, bullet.y))


        for enemy in enemies:
            screen.blit(enemy_image, (enemy.x, enemy.y))

        explosion_group.update()
        explosion_group.draw(screen)

       
        draw_score()
        draw_lives()
        draw_high_score()
        #gui_man.draw_ui(screen)

        pygame.display.flip()

        if player_lives <= 0:
            game_over = True
            if score > high_score:
                high_score = score
    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Restart the game when Enter is pressed
                    player_x = (screen_width - player_width) / 2
                    player_y = screen_height - player_height - 20
                    bullets = []
                    enemies = []
                    score = 0
                    player_lives = 3  # Reset player lives
                    game_over = False

        screen.fill((0, 0, 0))
        game_over_text = font.render("Game Over", True, white)
        restart_text = font.render("Press Enter to Restart", True, white)
        screen.blit(game_over_text, (screen_width // 2 - 100, screen_height // 2 - 50))
        screen.blit(restart_text, (screen_width // 2 - 150, screen_height // 2 + 50))
        
        pygame.display.flip()