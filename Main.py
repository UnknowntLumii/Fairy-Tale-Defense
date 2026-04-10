import pygame
import math
import random
import os

pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Fairy Tale Defense")
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPHICS_DIR = os.path.join(BASE_DIR, 'game', 'graphics')
AUDIO_DIR = os.path.join(BASE_DIR, 'game', 'audio')

def extract_frame(sheet, col, row, width, height, scale=2):
    frame = pygame.Surface((width, height), pygame.SRCALPHA)
    
    frame.blit(sheet, (0, 0), (col * width, row * height, width, height))
    
    frame = pygame.transform.scale(frame, (width * scale, height * scale))
    return frame

raw_bg = pygame.image.load(os.path.join(GRAPHICS_DIR, 'Helsa_Desert.png')).convert()

center_x = raw_bg.get_width() // 2
center_y = raw_bg.get_height() // 2

bg_image = raw_bg.subsurface((center_x - 400, center_y - 300, 600, 400))

bullet_img = pygame.image.load(os.path.join(GRAPHICS_DIR, 'Red Light.png')).convert_alpha()

heart_img = pygame.image.load(os.path.join(GRAPHICS_DIR, 'Black_Soul.png')).convert_alpha()

grimm_sheet = pygame.image.load(os.path.join(GRAPHICS_DIR, 'Grimm.png')).convert_alpha()
g_w = grimm_sheet.get_width() // 3
g_h = grimm_sheet.get_height() // 4
player_img = extract_frame(grimm_sheet, 1, 0, g_w, g_h, scale=2)

zombie_sheet = pygame.image.load(os.path.join(GRAPHICS_DIR, 'Zombie.png')).convert_alpha()
z_w = zombie_sheet.get_width() // 3
z_h = zombie_sheet.get_height() // 4

fairy_sheet = pygame.image.load(os.path.join(GRAPHICS_DIR, 'Fairy.png')).convert_alpha()
f_w = fairy_sheet.get_width() // 12
f_h = fairy_sheet.get_height() // 8

ogre_sheet = pygame.image.load(os.path.join(GRAPHICS_DIR, 'Ogre.png')).convert_alpha()
o_w = ogre_sheet.get_width() // 3
o_h = ogre_sheet.get_height() // 4

dragon_sheet = pygame.image.load(os.path.join(GRAPHICS_DIR, 'Dragon.png')).convert_alpha()
d_w = dragon_sheet.get_width() // 3
d_h = dragon_sheet.get_height() // 4

pygame.mixer.init()

shoot_sound = pygame.mixer.Sound(os.path.join(AUDIO_DIR, 'fire.ogg'))
kill_sound = pygame.mixer.Sound(os.path.join(AUDIO_DIR, 'kill.wav'))

shoot_sound.set_volume(0.1)
kill_sound.set_volume(0.05)

try:
    pygame.mixer.music.load(os.path.join(AUDIO_DIR, 'WonderlandBattle.mp3'))
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Could not load BGM: {e}")

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.frames = {
            "down": extract_frame(grimm_sheet, 1, 0, g_w, g_h, scale=2),
            "left": extract_frame(grimm_sheet, 1, 1, g_w, g_h, scale=2),
            "right": extract_frame(grimm_sheet, 1, 2, g_w, g_h, scale=2),
            "up": extract_frame(grimm_sheet, 1, 3, g_w, g_h, scale=2)
        }
        
        self.image = self.frames["down"]
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.pos = pygame.math.Vector2(WIDTH//2, HEIGHT//2)

    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        angle_rads = math.atan2(-(mouse_y - self.pos.y), mouse_x - self.pos.x)
        angle_degs = math.degrees(angle_rads)
        
        if -45 <= angle_degs <= 45:
            self.image = self.frames["right"]
        elif 45 < angle_degs < 135:
            self.image = self.frames["up"]
        elif -135 < angle_degs < -45:
            self.image = self.frames["down"]
        else:
            self.image = self.frames["left"]
            
        self.rect = self.image.get_rect(center=self.pos)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.transform.scale(bullet_img, (20, 20)) 
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        
        target = pygame.math.Vector2(target_x, target_y)
        self.direction = (target - self.pos)
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
            
        self.speed = 20

    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = self.pos
        
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animation_frames = []
        for col in range(3):
            frame = extract_frame(zombie_sheet, col, 0, z_w, z_h, scale=2)
            
            frame = pygame.transform.scale(frame, (100, 100))
            
            self.animation_frames.append(frame)
            
        self.current_frame = 0
        self.image = self.animation_frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 150 
        self.speed = 5
        self.health = 40
        self.target = pygame.math.Vector2(WIDTH//2, HEIGHT//2)
        
    def update(self):
        direction = self.target - self.pos
        if direction.length() > 0:
            direction = direction.normalize()
        self.pos += direction * self.speed
        self.rect.center = self.pos
        now = pygame.time.get_ticks() 
        
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.current_frame]


class FastEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y) 
        self.animation_frames = []
        for col in range(3):
            frame = extract_frame(fairy_sheet, col, 0, f_w, f_h, scale=2)
            
            frame = pygame.transform.scale(frame, (70, 70))
            
            self.animation_frames.append(frame)
            
        self.image = self.animation_frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        
        self.speed = 9                
        self.health = 40        

class TankyEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y) 
        self.animation_frames = []
        for col in range(3):
            frame = extract_frame(ogre_sheet, col, 0, o_w, o_h, scale=1)
            
            frame = pygame.transform.scale(frame, (150, 150))
            
            self.animation_frames.append(frame)
            
        self.image = self.animation_frames[0]
        
        self.rect = self.image.get_rect(center=(x, y))
        
        self.speed = 3                
        self.health = 120        

class BossEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.animation_frames = []
        for col in range(3):
            frame = extract_frame(dragon_sheet, col, 0, d_w, d_h, scale=1)
            
            frame = pygame.transform.scale(frame, (200, 200)) 
            
            self.animation_frames.append(frame)
            
        self.image = self.animation_frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        
        self.speed = 1                
        self.health = 400

def spawn_enemy():
    edge = random.randint(0, 3)
    
    if edge == 0:
        x = random.randint(0, WIDTH)
        y = -30
    elif edge == 1:
        x = WIDTH + 30
        y = random.randint(0, HEIGHT)
    elif edge == 2:
        x = random.randint(0, WIDTH)
        y = HEIGHT + 30
    else:
        x = -30
        y = random.randint(0, HEIGHT)

    spawn_chance = random.random() 
    
    if spawn_chance < 0.25:
        new_enemy = FastEnemy(x, y)
    elif spawn_chance > 0.75:
        new_enemy = TankyEnemy(x, y)
    else:
        new_enemy = Enemy(x, y)
        
    return new_enemy

def spawn_boss():
    edge = random.randint(0, 3)
    if edge == 0:
        x, y = random.randint(0, WIDTH), -100
    elif edge == 1:
        x, y = WIDTH + 100, random.randint(0, HEIGHT)
    elif edge == 2:
        x, y = random.randint(0, WIDTH), HEIGHT + 100
    else:
        x, y = -100, random.randint(0, HEIGHT)
        
    boss = BossEnemy(x, y)
    all_sprites.add(boss)
    enemies.add(boss)

def reset_game():
    global score, health, game_over, player, bosses_spawned, boss_warning_timer
    
    score = 0
    health = 3
    game_over = False
    bosses_spawned = 0
    boss_warning_timer = -9999
    
    all_sprites.empty()
    enemies.empty()
    bullets.empty()
    
    player = Player()
    all_sprites.add(player)

player = Player()
all_sprites = pygame.sprite.Group() 
enemies = pygame.sprite.Group()     
bullets = pygame.sprite.Group()     

all_sprites.add(player)

SPAWN_ENEMY = pygame.USEREVENT + 1

pygame.time.set_timer(SPAWN_ENEMY, 800)

pygame.font.init()
font = pygame.font.SysFont(None, 36)
large_font = pygame.font.SysFont(None, 72)

score = 0
health = 3
game_over = False
bosses_spawned = 0
boss_warning_timer = -9999
last_shot_time = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            
            if not game_over:
                player.pos.x = WIDTH // 2
                player.pos.y = HEIGHT // 2
         
        elif event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r:
                reset_game()
        
        if not game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    new_bullet = Bullet(player.pos.x, player.pos.y, mouse_x, mouse_y)
                    all_sprites.add(new_bullet)
                    bullets.add(new_bullet)
                    
            elif event.type == SPAWN_ENEMY:
                enemy = spawn_enemy()
                all_sprites.add(enemy)
                enemies.add(enemy)

    if not game_over:
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            now = pygame.time.get_ticks()
            if now - last_shot_time > 150: 
                last_shot_time = now
                shoot_sound.play()
                mouse_x, mouse_y = pygame.mouse.get_pos()
                new_bullet = Bullet(player.pos.x, player.pos.y, mouse_x, mouse_y)
                all_sprites.add(new_bullet)
                bullets.add(new_bullet)
        
        all_sprites.update()

        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        
        for enemy, hitting_bullets in hits.items():
            for bullet in hitting_bullets:
                enemy.health -= 40
            
            if enemy.health <= 0:
                enemy.kill()
                kill_sound.play()
                
                if isinstance(enemy, FastEnemy): 
                    score += 20
                elif isinstance(enemy, TankyEnemy):
                    score += 25
                elif isinstance(enemy, BossEnemy):
                    score += 100
                    if health < 3:
                        health += 1
                else:
                    score += 10
                
                expected_bosses = score // 1000
                if expected_bosses > bosses_spawned:
                    spawn_boss()
                    bosses_spawned += 1
                    boss_warning_timer = pygame.time.get_ticks()
                    

        damage_hits = pygame.sprite.spritecollide(player, enemies, True)
        for hit in damage_hits:
            health -= 1
            if health <= 0:
                game_over = True
                player.kill()

    screen.fill((30, 30, 30))
    scaled_bg = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    screen.blit(scaled_bg, (0, 0))

    all_sprites.draw(screen)
    
    if not game_over:
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        for i in range(health):
            x_pos = WIDTH - 40 - (i * 40)
            scaled_heart = pygame.transform.scale(heart_img, (30, 30))
            screen.blit(scaled_heart, (x_pos, 10))
        
        if pygame.time.get_ticks() - boss_warning_timer < 3000:
            warning_text = large_font.render("WARNING: DRAGON APPROACHING!", True, (255, 50, 50))
            screen.blit(warning_text, (WIDTH//2 - warning_text.get_width()//2, HEIGHT//2 - 150))
            
    else:
        game_over_text = large_font.render("GAME OVER", True, (255, 0, 0))
        final_score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        restart_text = font.render("Press 'R' to Restart", True, (200, 200, 200))
        
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2 + 20))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()