import pgzrun
import random
import math
from pygame import Rect

# --- CONFIGURATION ---
WIDTH = 800
HEIGHT = 600

BACKGROUND_IMAGE = "background"

# Hero frames
HERO_FRAMES = {
    "idle": {
        "down": ["hero/idle/down/hero_idle_down1", "hero/idle/down/hero_idle_down2",
                 "hero/idle/down/hero_idle_down3", "hero/idle/down/hero_idle_down4"],
        "up": ["hero/idle/up/hero_idle_up1", "hero/idle/up/hero_idle_up2",
               "hero/idle/up/hero_idle_up3", "hero/idle/up/hero_idle_up4"],
        "left": ["hero/idle/left/hero_idle_left1", "hero/idle/left/hero_idle_left2",
                 "hero/idle/left/hero_idle_left3", "hero/idle/left/hero_idle_left4"],
        "right": ["hero/idle/right/hero_idle_right1", "hero/idle/right/hero_idle_right2",
                  "hero/idle/right/hero_idle_right3", "hero/idle/right/hero_idle_right4"],
    },
    "walk": {
        "down": ["hero/walk/down/hero_walk_down1", "hero/walk/down/hero_walk_down2",
                 "hero/walk/down/hero_walk_down3", "hero/walk/down/hero_walk_down4"],
        "up": ["hero/walk/up/hero_walk_up1", "hero/walk/up/hero_walk_up2",
               "hero/walk/up/hero_walk_up3", "hero/walk/up/hero_walk_up4"],
        "left": ["hero/walk/left/hero_walk_left1", "hero/walk/left/hero_walk_left2",
                 "hero/walk/left/hero_walk_left3", "hero/walk/left/hero_walk_left4"],
        "right": ["hero/walk/right/hero_walk_right1", "hero/walk/right/hero_walk_right2",
                  "hero/walk/right/hero_walk_right3", "hero/walk/right/hero_walk_right4"],
    },
    "attack": {
        "down": ["hero/attack/down/hero_attack_down1", "hero/attack/down/hero_attack_down2"],
        "up": ["hero/attack/up/hero_attack_up1", "hero/attack/up/hero_attack_up2"],
        "left": ["hero/attack/left/hero_attack_left1", "hero/attack/left/hero_attack_left2"],
        "right": ["hero/attack/right/hero_attack_right1", "hero/attack/right/hero_attack_right2"],
    }
}
HERO_DEAD_IMAGE = "hero/hero_dead"

# Enemy frames
ENEMY_FRAMES = {
    "idle": {
        "down": ["enemy/idle/down/enemy_idle_down1", "enemy/idle/down/enemy_idle_down2",
                 "enemy/idle/down/enemy_idle_down3", "enemy/idle/down/enemy_idle_down4"],
        "up": ["enemy/idle/up/enemy_idle_up1", "enemy/idle/up/enemy_idle_up2",
               "enemy/idle/up/enemy_idle_up3", "enemy/idle/up/enemy_idle_up4"],
        "left": ["enemy/idle/left/enemy_idle_left1", "enemy/idle/left/enemy_idle_left2",
                 "enemy/idle/left/enemy_idle_left3", "enemy/idle/left/enemy_idle_left4"],
        "right": ["enemy/idle/right/enemy_idle_right1", "enemy/idle/right/enemy_idle_right2",
                  "enemy/idle/right/enemy_idle_right3", "enemy/idle/right/enemy_idle_right4"],
    },
    "walk": {
        "down": ["enemy/walk/down/enemy_walk_down1", "enemy/walk/down/enemy_walk_down2",
                 "enemy/walk/down/enemy_walk_down3", "enemy/walk/down/enemy_walk_down4"],
        "up": ["enemy/walk/up/enemy_walk_up1", "enemy/walk/up/enemy_walk_up2",
               "enemy/walk/up/enemy_walk_up3", "enemy/walk/up/enemy_walk_up4"],
        "left": ["enemy/walk/left/enemy_walk_left1", "enemy/walk/left/enemy_walk_left2",
                 "enemy/walk/left/enemy_walk_left3", "enemy/walk/left/enemy_walk_left4"],
        "right": ["enemy/walk/right/enemy_walk_right1", "enemy/walk/right/enemy_walk_right2",
                  "enemy/walk/right/enemy_walk_right3", "enemy/walk/right/enemy_walk_right4"],
    },
     "attack": {
        "down": ["enemy/attack/down/enemy_attack_down1", "enemy/attack/down/enemy_attack_down2"],
        "up": ["enemy/attack/up/enemy_attack_up1", "enemy/attack/up/enemy_attack_up2"],
        "left": ["enemy/attack/left/enemy_attack_left1", "enemy/attack/left/enemy_attack_left2"],
        "right": ["enemy/attack/right/enemy_attack_right1", "enemy/attack/right/enemy_attack_right2"],
    }
}
ENEMY_DEAD_IMAGE = "enemy/enemy_dead"

# Audio names
MENU_MUSIC = "game_music"
GAME_MUSIC = "game_music"
SOUND_BUTTON = "hurt"

# --- GLOBAL STATE ---
game_running = False
music_on = True
music_playing = False
death_timer = 0.0
game_over = False

# menu buttons
buttons = [
    {"text": "Start Game", "rect": Rect(300, 200, 200, 50), "color": (255, 162, 100)},
    {"text": "Toggle Music", "rect": Rect(300, 300, 200, 50), "color": (255, 162, 100)},
    {"text": "Exit", "rect": Rect(300, 400, 200, 50), "color": (255, 162, 100)},
]

# --- CLASSES ---
class AnimatedActor:
    def __init__(self, frames, pos, dead_image=None):
        self.frames = frames
        self.dead_image = dead_image
        self.direction = "down"
        self.state = "idle"
        self.actor = Actor(frames["idle"][self.direction][0])
        self.actor.pos = pos
        self.frame_index = 0
        self.animation_timer = 0.0
        self.animation_speeds = {
            "idle": 0.40,
            "walk": 0.15,
            "attack": 0.30
        }
        self.moving = False
        self.alive = True
        self.speed = 2
        self.move_area = Rect(0, 0, WIDTH, HEIGHT)

    def update_animation(self, dt):
        if not self.alive:
            return
        self.animation_timer += dt
        current_speed = self.animation_speeds.get(self.state, 0.15)
        if self.animation_timer >= current_speed:
            self.animation_timer = 0.0
            images = self.frames[self.state][self.direction]
            self.frame_index = (self.frame_index + 1) % len(images)
            self.actor.image = images[self.frame_index]

    def move(self, dx, dy):
        if not self.alive or self.state == "attack":
            return
        new_x = self.actor.x + dx * self.speed
        new_y = self.actor.y + dy * self.speed
        if self.move_area.left <= new_x <= self.move_area.right:
            self.actor.x = new_x
        if self.move_area.top <= new_y <= self.move_area.bottom:
            self.actor.y = new_y

        self.moving = (dx != 0 or dy != 0)
        if self.moving:
            self.state = "walk"
            if abs(dx) > abs(dy):
                self.direction = "left" if dx < 0 else "right"
            else:
                self.direction = "up" if dy < 0 else "down"
        else:
            if self.state != "attack":
                self.state = "idle"
                self.frame_index = 0
                self.actor.image = self.frames["idle"][self.direction][0]

    def draw(self):
        self.actor.draw()

    def die(self):
        if not self.alive:
            return
        self.alive = False
        self.actor.image = self.dead_image if self.dead_image else self.frames["idle"][self.direction][0]
        self.moving = False

    def get_rect(self):
        return Rect(self.actor.x - self.actor.width // 2,
                    self.actor.y - self.actor.height // 2,
                    self.actor.width,
                    self.actor.height)

class Hero(AnimatedActor):
    def __init__(self, pos):
        super().__init__(HERO_FRAMES, pos, HERO_DEAD_IMAGE)
        self.speed = 3
        self.attacking = False
        self.attack_timer = 0.0
        self.attack_duration = 0.6

    def update(self, dt):
        if not self.alive:
            return
        dx = dy = 0
        if not self.attacking:
            if keyboard.left: dx = -1
            elif keyboard.right: dx = 1
            if keyboard.up: dy = -1
            elif keyboard.down: dy = 1
        self.move(dx, dy)

        if self.attacking:
            self.attack_timer += dt
            if self.attack_timer >= self.attack_duration:
                self.attacking = False
                self.state = "idle"
                self.frame_index = 0
        self.update_animation(dt)

    def attack(self):
        if not self.alive or self.attacking:
            return
        self.attacking = True
        self.attack_timer = 0.0
        self.state = "attack"
        self.frame_index = 0
        self.animation_timer = 0.0

    def get_attack_rect(self):
        rect = self.get_rect()
        size = 40  # alcance maior
        if self.direction == "up":
            return Rect(rect.x, rect.y - size, rect.width, rect.height + size)
        elif self.direction == "down":
            return Rect(rect.x, rect.y, rect.width, rect.height + size)
        elif self.direction == "left":
            return Rect(rect.x - size, rect.y, rect.width + size, rect.height)
        elif self.direction == "right":
            return Rect(rect.x, rect.y, rect.width + size, rect.height)
        return rect

class Enemy(AnimatedActor):
    def __init__(self, pos, territory_rect):
        super().__init__(ENEMY_FRAMES, pos, ENEMY_DEAD_IMAGE)
        self.move_area = territory_rect
        self.speed = 1.5
        self.move_direction = random.choice(["left", "right", "up", "down", "none"])
        self.move_timer = 0.0
        self.move_change_interval = random.uniform(1.0, 3.0)
        self.death_timer = 0.0

        # Controle de ataque
        self.attacking = False
        self.attack_timer = 0.0
        self.attack_delay = 0.5  # 0.5 segundos para atacar após se aproximar
        self.attack_range = 50  # distância para iniciar ataque

    def update(self, dt):
        if not self.alive:
            self.death_timer += dt
            if self.death_timer >= 1.0:
                if self in enemies:
                    enemies.remove(self)
                spawn_enemy(initial=False)
            return

        # Se está atacando, conta o tempo e executa ataque após delay
        if self.attacking:
            self.attack_timer += dt
            if self.attack_timer >= self.attack_delay:
                # Ataque inevitável: mata o herói independentemente da distância
                if hero.alive:
                    hero_die()
                self.attacking = False
                self.attack_timer = 0.0
            self.update_animation(dt)  # animação de ataque continua
            return

        # Verifica distância para o herói para iniciar ataque
        dist = math.dist(self.actor.pos, hero.actor.pos)
        if dist <= self.attack_range and hero.alive:
            self.attacking = True
            self.attack_timer = 0.0
            self.state = "attack"
            self.frame_index = 0
            self.animation_timer = 0.0
            self.moving = False
            self.update_animation(dt)
            return

        # Movimento normal
        self.move_timer += dt
        if self.move_timer >= self.move_change_interval:
            self.move_timer = 0.0
            self.move_change_interval = random.uniform(1.0, 3.0)
            self.move_direction = random.choice(["left", "right", "up", "down", "none"])

        dx = dy = 0
        if self.move_direction == "left": dx = -1
        elif self.move_direction == "right": dx = 1
        elif self.move_direction == "up": dy = -1
        elif self.move_direction == "down": dy = 1

        self.move(dx, dy)
        self.update_animation(dt)

# --- GAME OBJECTS ---
hero = Hero((50, 50))  # canto superior esquerdo
enemies = []

def spawn_enemy(initial=True):
    if initial:
        left = random.randint(150, WIDTH - 150)
        top = random.randint(150, HEIGHT - 150)
        territory = Rect(left, top, 100, 100)
        enemy_pos = (territory.centerx, territory.centery)
    else:
        left = random.randint(150, WIDTH - 150)
        top = random.randint(150, HEIGHT - 150)
        territory = Rect(left, top, 100, 100)
        enemy_pos = (territory.centerx, territory.centery)
    enemy = Enemy(enemy_pos, territory)
    enemies.append(enemy)

for _ in range(5):
    spawn_enemy(initial=True)

# --- MENU LOGIC ---
def draw_menu():
    screen.clear()
    try:
        screen.blit(BACKGROUND_IMAGE, (0, 0))
    except Exception:
        screen.fill((30, 30, 50))
    for btn in buttons:
        screen.draw.filled_rect(btn["rect"], btn["color"])
        screen.draw.textbox(btn["text"], btn["rect"], color="black")

def check_button_click(pos):
    for btn in buttons:
        if btn["rect"].collidepoint(pos):
            if btn["text"] == "Start Game":
                start_game()
            elif btn["text"] == "Toggle Music":
                toggle_music()
            elif btn["text"] == "Exit":
                exit_game()

def start_game():
    global game_running, game_over
    game_running = True
    game_over = False
    hero.alive = True
    hero.actor.pos = (50, 50)  # herói sempre começa no canto superior esquerdo
    enemies.clear()
    for _ in range(5):
        spawn_enemy(initial=True)

def toggle_music():
    global music_on
    music_on = not music_on
    if not music_on:
        music.stop()

def exit_game():
    import sys
    sys.exit()

# --- GAME LOOP ---
def draw():
    if game_running:
        screen.clear()
        try:
            screen.blit(BACKGROUND_IMAGE, (0, 0))
        except Exception:
            screen.fill((80, 120, 180))
        hero.draw()
        for enemy in enemies:
            enemy.draw()
        if game_over:
            screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2), fontsize=64, color="red")
            screen.draw.text("Returning to menu...", center=(WIDTH // 2, HEIGHT // 2 + 60), fontsize=28, color="white")
    else:
        draw_menu()

def update(dt):
    global music_playing, game_running, death_timer, game_over
    if game_running:
        if music_on and not music_playing:
            music_playing = True
        elif not music_on and music_playing:
            music.stop()
            music_playing = False

        if hero.alive:
            hero.update(dt)
            for enemy in enemies[:]:
                enemy.update(dt)
                if hero.attacking and hero.get_attack_rect().colliderect(enemy.get_rect()) and enemy.alive:
                    enemy.die()
                    try: sounds.enemy_hurt.play()
                    except Exception: pass
        else:
            if not game_over:
                game_over = True
                death_timer = 0.0
            if music_playing:
                music.stop()
                music_playing = False
            death_timer += dt
            if death_timer >= 3.0:
                reset_to_menu()
    else:
        if music_on and not music_playing:
            try:
                music.play(MENU_MUSIC)
            except Exception: pass
            music_playing = True
        elif not music_on and music_playing:
            music.stop()
            music_playing = False

def reset_to_menu():
    global game_running, game_over
    game_running = False
    game_over = False
    hero.actor.pos = (50, 50)
    enemies.clear()
    for _ in range(5):
        spawn_enemy(initial=True)

def on_mouse_down(pos):
    if not game_running:
        check_button_click(pos)

def on_key_down(key):
    if key == keys.SPACE:
        hero.attack()

def hero_die():
    global death_timer
    death_timer = 0.0
    hero.die()
    try: sounds.hero_hurt.play()
    except Exception: pass

# --- INIT ---
try:
    music.play(MENU_MUSIC)
    music_playing = True
except Exception:
    music_playing = False

pgzrun.go()