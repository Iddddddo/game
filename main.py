import arcade
import math
import os
import time
from typing import Dict, List, Set, Optional

# Константы
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Mini Adventure"
PLAYER_SPEED = 5
JUMP_FORCE = 21
GRAVITY = 0.9
PLAYER_SCALE = 0.02
COIN_SCALE = 0.05
LILYPAD_SCALE = 0.1
PORTAL_SCALE = 0.5

class Lilypad(arcade.Sprite):
    def __init__(self, texture, scale=1.0):
        super().__init__(texture, scale)
        self.stand_time = 0  # Время, которое игрок стоит на кувшинке
        self.disappear_time = 0  # Время исчезновения
        self.original_y = 0  # Исходная позиция Y
        self.is_disappearing = False
        self.alpha = 255  # Прозрачность спрайта

    def update(self):
        # Анимация покачивания
        if self.stand_time > 1.0 and not self.is_disappearing and self.alpha == 255:
            # Покачивание (синусоидальное движение)
            self.center_y = self.original_y + math.sin(time.time() * 10) * 3

        # Проверка на исчезновение
        if self.stand_time > 2.0 and not self.is_disappearing and self.alpha == 255:
            self.is_disappearing = True
            self.disappear_time = time.time()

        # Процесс исчезновения
        if self.is_disappearing:
            fade_progress = (time.time() - self.disappear_time) / 1.0
            self.alpha = max(0, int(255 * (1 - fade_progress)))
            
            # Когда полностью исчезли
            if self.alpha == 0:
                self.is_disappearing = False
                self.stand_time = 0
                self.center_y = self.original_y
                # Запланировать появление через 1 секунду
                self.disappear_time = time.time() + 1.0

        # Процесс появления
        elif self.alpha < 255:
            if time.time() > self.disappear_time:
                self.alpha = min(255, self.alpha + 5)

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        
        # Установка рабочей директории
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        
        # Спрайтлисты
        self.menu_background_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.back_decor_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.platforms_list = arcade.SpriteList()
        self.portal_list = arcade.SpriteList()
        self.spikes_list = arcade.SpriteList()
        self.water_list = arcade.SpriteList()
        self.lilypads_list = arcade.SpriteList()
        self.coins_list = arcade.SpriteList()
        self.end_list = arcade.SpriteList()
        self.intro_player_list = arcade.SpriteList()

        # Состояние монеток
        self.coin_positions = {
            1: [(300, 400), (600, 500), (900, 250)],
            2: [(350, 300), (700, 400), (950, 350)],
            3: [(400, 200), (750, 300), (1000, 250)]
        }
        self.collected_coins = {1: set(), 2: set(), 3: set()}
        
        # Звуки
        self.game_music = None
        self.music_player = None
        self.jump_sound = None
        self.coin_sound = None
        self.lilypad_sound = None
        
        # Текстуры
        self.preloaded_textures = {
            'player_right': None,
            'player_left': None,
            'backgrounds': {},
            'menu_bg': None,
            'lilypad': None,
            'coin': None,
            'portal': None
        }
        
        # Направление игрока
        self.player_facing_right = True
        
        # Статистика игрока
        self.player_scale = 0.02
        self.initial_scale = 0.02
        self.min_scale = 0.005
        self.max_scale = 0.02
        self.death_count = 0
        self.coins_collected = 0
        self.total_coins = 3
        
        # Состояния игры
        self.game_state = "MENU"  # MENU, INTRO, GAME, VICTORY
        self.current_level = 1
        self.animation_time = 0
        self.fade_alpha = 0
        self.intro_time = 0
        self.victory_time = 0
        
        # Управление
        self.held_keys = set()
        self.physics_engine = None
        
        # Параметры кнопки/текста
        self.button_x = SCREEN_WIDTH // 2
        self.button_y = SCREEN_HEIGHT // 2
        self.button_width = 300
        self.button_height = 100
        self.button_angle = 0
        
        self.setup_menu()
        self.preload_resources()
        self.start_music()

    def preload_resources(self):
        """Предзагрузка всех необходимых ресурсов"""
        print("\n=== LOADING RESOURCES ===")
        
        # Создаем папки если их нет
        os.makedirs("images", exist_ok=True)
        os.makedirs("sounds", exist_ok=True)
        os.makedirs("maps", exist_ok=True)

        # Загрузка звуков
        try:
            if os.path.exists("sounds/menu.wav"):
                self.game_music = arcade.load_sound("sounds/menu.wav")
            if os.path.exists("sounds/jump.wav"):
                self.jump_sound = arcade.load_sound("sounds/jump.wav")
            if os.path.exists("sounds/coin.wav"):
                self.coin_sound = arcade.load_sound("sounds/coin.wav")
            if os.path.exists("sounds/lilypad.wav"):
                self.lilypad_sound = arcade.load_sound("sounds/lilypad.wav")
        except Exception as e:
            print(f"Ошибка загрузки звуков: {e}")

        # Загрузка текстур
        try:
            if os.path.exists("images/big2.png"):
                self.preloaded_textures['player_right'] = arcade.load_texture("images/big2.png")
            if os.path.exists("images/big2z.png"):
                self.preloaded_textures['player_left'] = arcade.load_texture("images/big2z.png")
            if os.path.exists("images/lilypad.png"):
                self.preloaded_textures['lilypad'] = arcade.load_texture("images/lilypad.png")
            if os.path.exists("images/coin.png"):
                self.preloaded_textures['coin'] = arcade.load_texture("images/coin.png")
            if os.path.exists("images/portal.png"):
                self.preloaded_textures['portal'] = arcade.load_texture("images/portal.png")
            if os.path.exists("images/menu.png"):
                self.preloaded_textures['menu_bg'] = arcade.load_texture("images/menu.png")
            
            for level in [1, 2, 3]:
                path = f"images/loc{level}.png"
                if os.path.exists(path):
                    self.preloaded_textures['backgrounds'][level] = arcade.load_texture(path)
        except Exception as e:
            print(f"Ошибка загрузки текстур: {e}")

    def create_lilypads(self):
        """Создание платформ-лилий для второго уровня"""
        if not self.preloaded_textures['lilypad']:
            print("Текстура лилии не загружена!")
            return
            
        lily_positions = [
            (480, 250),
            (600, 250),
            (900, 300)
        ]
        
        for x, y in lily_positions:
            lilypad = Lilypad(self.preloaded_textures['lilypad'], LILYPAD_SCALE)
            lilypad.center_x = x
            lilypad.center_y = y
            lilypad.original_y = y
            self.lilypads_list.append(lilypad)
        
        self.platforms_list.extend(self.lilypads_list)

    def create_portal(self, x, y):
        """Создание портала на уровне"""
        if not self.preloaded_textures['portal']:
            print("Текстура портала не загружена!")
            return
            
        portal = arcade.Sprite()
        portal.texture = self.preloaded_textures['portal']
        portal.center_x = x
        portal.center_y = y
        portal.scale = PORTAL_SCALE
        self.portal_list.append(portal)

    def create_coins(self, reset_coins=False):
        """Создание монеток для уровня"""
        if not self.preloaded_textures['coin']:
            print("Текстура монетки не загружена!")
            return
            
        self.coins_list.clear()
        
        if reset_coins:
            self.collected_coins[self.current_level] = set()
            self.coins_collected = 0
        
        for i, (x, y) in enumerate(self.coin_positions[self.current_level]):
            if i not in self.collected_coins[self.current_level]:
                coin = arcade.Sprite()
                coin.texture = self.preloaded_textures['coin']
                coin.center_x = x
                coin.center_y = y
                coin.scale = COIN_SCALE
                coin.index = i
                self.coins_list.append(coin)

    def start_music(self):
        """Запуск музыки"""
        if self.game_music and not self.music_player:
            self.music_player = arcade.play_sound(self.game_music, loop=True)
        elif self.music_player and not self.game_music:
            arcade.stop_sound(self.music_player)
            self.music_player = None

    def setup_menu(self):
        """Инициализация меню"""
        self.game_state = "MENU"
        self.menu_background_list.clear()
        self.intro_player_list.clear()
        
        # Сброс параметров
        self.player_scale = self.initial_scale
        self.death_count = 0
        self.coins_collected = 0
        self.collected_coins = {1: set(), 2: set(), 3: set()}
        self.current_level = 1
        self.fade_alpha = 0
        
        # Загрузка фона меню
        if self.preloaded_textures['menu_bg']:
            bg = arcade.Sprite()
            bg.texture = self.preloaded_textures['menu_bg']
            bg.width = SCREEN_WIDTH
            bg.height = SCREEN_HEIGHT
            bg.center_x = SCREEN_WIDTH // 2
            bg.center_y = SCREEN_HEIGHT // 2
            self.menu_background_list.append(bg)
        else:
            self.background_color = arcade.color.BLACK
        
        self.start_music()

    def show_intro(self):
        """Показать вступительную сцену"""
        self.game_state = "INTRO"
        self.intro_time = time.time()
        self.fade_alpha = 0
        
        # Создаем спрайт игрока для интро
        if self.preloaded_textures['player_right']:
            player = arcade.Sprite()
            player.texture = self.preloaded_textures['player_right']
            player.scale = 0.1
            player.center_x = SCREEN_WIDTH // 2
            player.center_y = SCREEN_HEIGHT // 2
            self.intro_player_list.append(player)

    def show_victory(self):
        """Показать сцену победы"""
        self.game_state = "VICTORY"
        self.victory_time = time.time()
        self.fade_alpha = 0

    def load_level(self, level_num, reset_coins=False):
        """Загрузка уровня"""
        self.game_state = "GAME"
        self.current_level = level_num
        
        # Очистка списков
        self.background_list.clear()
        self.back_decor_list.clear()
        self.player_list.clear()
        self.platforms_list.clear()
        self.portal_list.clear()
        self.spikes_list.clear()
        self.water_list.clear()
        self.lilypads_list.clear()
        self.coins_list.clear()
        self.end_list.clear()

        # Загрузка фона
        if level_num in self.preloaded_textures['backgrounds'] and self.preloaded_textures['backgrounds'][level_num]:
            bg = arcade.Sprite()
            bg.texture = self.preloaded_textures['backgrounds'][level_num]
            bg.width = SCREEN_WIDTH
            bg.height = SCREEN_HEIGHT
            bg.center_x = SCREEN_WIDTH // 2
            bg.center_y = SCREEN_HEIGHT // 2
            self.background_list.append(bg)
        else:
            self.background_color = arcade.color.SKY_BLUE

        # Загрузка карты
        map_path = f"maps/map{level_num}.json"
        if os.path.exists(map_path):
            try:
                layer_options = {
                    "Platforms": {"use_spatial_hash": True},
                    "platforms": {"use_spatial_hash": True},
                    "Spikes": {"use_spatial_hash": True},
                    "spikes": {"use_spatial_hash": True},
                    "Back": {"use_spatial_hash": False},
                    "back": {"use_spatial_hash": False},
                    "Portal": {"use_spatial_hash": True} if level_num in [1, 2] else {},
                    "portal": {"use_spatial_hash": True} if level_num in [1, 2] else {},
                    "Water": {"use_spatial_hash": True} if level_num == 2 else {},
                    "water": {"use_spatial_hash": True} if level_num == 2 else {},
                    "End": {"use_spatial_hash": True} if level_num == 3 else {},
                    "end": {"use_spatial_hash": True} if level_num == 3 else {}
                }
                
                tilemap = arcade.load_tilemap(map_path, scaling=1.0, layer_options=layer_options)
                
                for layer in tilemap.sprite_lists:
                    lower_layer = layer.lower()
                    if "platform" in lower_layer:
                        self.platforms_list.extend(tilemap.sprite_lists[layer])
                    elif "back" in lower_layer:
                        self.back_decor_list.extend(tilemap.sprite_lists[layer])
                    elif "spike" in lower_layer:
                        self.spikes_list.extend(tilemap.sprite_lists[layer])
                    elif "portal" in lower_layer and level_num in [1, 2]:
                        self.portal_list.extend(tilemap.sprite_lists[layer])
                    elif "water" in lower_layer and level_num == 2:
                        self.water_list.extend(tilemap.sprite_lists[layer])
                    elif "end" in lower_layer and level_num == 3:
                        self.end_list.extend(tilemap.sprite_lists[layer])
            except Exception as e:
                print(f"Ошибка загрузки карты: {e}")

        # Создание лилий для второго уровня
        if level_num == 2:
            self.create_lilypads()
            
        # Создание портала на втором уровне
        if level_num == 2 and not self.portal_list:
            self.create_portal(1100, 400)

        # Создание монеток
        self.create_coins(reset_coins)

        # Создание игрока
        if self.preloaded_textures['player_right']:
            player = arcade.Sprite()
            player.texture = self.preloaded_textures['player_right']
            player.scale = self.player_scale
            
            # Стартовые позиции
            if level_num == 1:
                player.center_x = 100
                player.center_y = 400
            elif level_num == 2:
                player.center_x = 50
                player.center_y = 380
            else:
                player.center_x = 100
                player.center_y = 400
                
            self.player_list.append(player)
            self.player_facing_right = True
        else:
            player = arcade.SpriteCircle(30, arcade.color.BLUE)
            player.center_x = 100
            player.center_y = 400
            self.player_list.append(player)

        # Физический движок
        if self.player_list and (self.platforms_list or self.lilypads_list):
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player_list[0],
                platforms=self.platforms_list,
                gravity_constant=GRAVITY
            )

    def update_player_texture(self):
        """Обновление текстуры игрока"""
        if not self.player_list:
            return
            
        player = self.player_list[0]
        
        if self.player_facing_right:
            if self.preloaded_textures['player_right']:
                player.texture = self.preloaded_textures['player_right']
        else:
            if self.preloaded_textures['player_left']:
                player.texture = self.preloaded_textures['player_left']

    def on_draw(self):
        """Отрисовка игры"""
        self.clear()
        
        if self.game_state == "MENU":
            self.menu_background_list.draw()
            
            # Отрисовка кнопки
            points = [
                (self.button_x - self.button_width/2, self.button_y - self.button_height/2),
                (self.button_x + self.button_width/2, self.button_y - self.button_height/2),
                (self.button_x + self.button_width/2, self.button_y + self.button_height/2),
                (self.button_x - self.button_width/2, self.button_y + self.button_height/2)
            ]
            
            rotated_points = []
            for point in points:
                x, y = point
                x -= self.button_x
                y -= self.button_y
                new_x = x * math.cos(math.radians(self.button_angle)) - y * math.sin(math.radians(self.button_angle))
                new_y = x * math.sin(math.radians(self.button_angle)) + y * math.cos(math.radians(self.button_angle))
                new_x += self.button_x
                new_y += self.button_y
                rotated_points.append((new_x, new_y))
            
            arcade.draw_polygon_filled(rotated_points, (144, 238, 144, 180))
            
            arcade.draw_text(
                "Играть", self.button_x, self.button_y,
                arcade.color.WHITE, 40,
                anchor_x="center", anchor_y="center",
                bold=True
            )
            
        elif self.game_state == "INTRO":
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.BLACK)
            
            self.intro_player_list.draw()
            
            arcade.draw_text(
                "Я должна собрать рассыпанные амулеты\nи отнести их домой,\nчтобы предотвратить страшное",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100,
                arcade.color.WHITE, 24,
                anchor_x="center", anchor_y="center",
                align="center",
                bold=True
            )
            
            if self.fade_alpha > 0:
                arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 0, 0, self.fade_alpha))
            
        elif self.game_state == "GAME":
            self.background_list.draw()
            self.back_decor_list.draw()
            self.spikes_list.draw()
            
            if self.current_level == 2:
                self.water_list.draw()
                self.lilypads_list.draw()  # Отрисовка кувшинок через стандартный спрайтлист
            
            self.portal_list.draw()
            self.end_list.draw()
            self.coins_list.draw()
            self.player_list.draw()
            self.platforms_list.draw()  # Платформы рисуются поверх всего
            
            # Статистика
            arcade.draw_text(
                f"Уровень: {self.current_level}", 10, SCREEN_HEIGHT - 30, 
                arcade.color.WHITE, 16
            )
            arcade.draw_text(
                f"Размер: {self.player_scale:.3f}", 10, SCREEN_HEIGHT - 60, 
                arcade.color.WHITE, 16
            )
            arcade.draw_text(
                f"Смерти: {self.death_count}/3", 10, SCREEN_HEIGHT - 90, 
                arcade.color.WHITE, 16
            )
            arcade.draw_text(
                f"Монетки: {len(self.collected_coins[self.current_level])}/{self.total_coins}", 
                10, SCREEN_HEIGHT - 120, arcade.color.WHITE, 16
            )
        
        elif self.game_state == "VICTORY":
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.BLACK)
            
            arcade.draw_text(
                "Победа, вы спасли мир!",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                arcade.color.WHITE, 40,
                anchor_x="center", anchor_y="center",
                bold=True
            )
            
            if self.fade_alpha > 0:
                arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 0, 0, self.fade_alpha))

    def on_update(self, delta_time):
        """Логика игры"""
        if self.game_state == "MENU":
            self.animation_time += delta_time
            self.button_angle = math.sin(self.animation_time * 2) * 5
        
        elif self.game_state == "INTRO":
            if time.time() - self.intro_time > 3:
                self.fade_alpha += 2
                if self.fade_alpha >= 255:
                    self.load_level(1, reset_coins=True)
        
        elif self.game_state == "GAME" and self.player_list:
            player = self.player_list[0]
            
            prev_facing = self.player_facing_right
            player.change_x = 0
            
            if arcade.key.LEFT in self.held_keys:
                player.change_x = -PLAYER_SPEED
                self.player_facing_right = False
            if arcade.key.RIGHT in self.held_keys:
                player.change_x = PLAYER_SPEED
                self.player_facing_right = True
            
            if prev_facing != self.player_facing_right:
                self.update_player_texture()
            
            if player.left < 0:
                player.left = 0
            if player.right > SCREEN_WIDTH:
                player.right = SCREEN_WIDTH
            
            if self.physics_engine:
                self.physics_engine.update()
                player.can_jump = self.physics_engine.can_jump()
            
            # Обновление кувшинок и проверка стояния на них
            for lilypad in self.lilypads_list:
                # Проверяем, стоит ли игрок на этой кувшинке
                if (arcade.check_for_collision(player, lilypad) and 
                    player.change_y == 0 and 
                    player.bottom <= lilypad.top + 5):  # Небольшой допуск
                    lilypad.stand_time += delta_time
                else:
                    lilypad.stand_time = 0
                
                lilypad.update()
            
            self.handle_collisions()
        
        elif self.game_state == "VICTORY":
            if time.time() - self.victory_time > 3:
                self.setup_menu()

    def handle_collisions(self):
        """Обработка столкновений"""
        if not self.player_list:
            return
            
        player = self.player_list[0]
    
        # Сбор монеток
        coins_hit = arcade.check_for_collision_with_list(player, self.coins_list)
        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.collected_coins[self.current_level].add(coin.index)
            self.coins_collected += 1
            
            if self.death_count > 0:
                self.death_count -= 1
            
            self.player_scale = min(self.player_scale + 0.005, self.max_scale)
            player.scale = self.player_scale
            
            if self.coin_sound:
                arcade.play_sound(self.coin_sound)
    
        # Переход на уровень 2
        if (self.current_level == 1 and 
            len(self.collected_coins[1]) == self.total_coins and 
            self.portal_list and 
            arcade.check_for_collision_with_list(player, self.portal_list)):
            self.load_level(2)
            return
            
        # Переход на уровень 3
        if (self.current_level == 2 and 
            self.portal_list and 
            arcade.check_for_collision_with_list(player, self.portal_list)):
            self.load_level(3)
            return
                
        # Столкновение с опасностями
        if self.spikes_list and arcade.check_for_collision_with_list(player, self.spikes_list):
            self.handle_hazard_collision()
            return
    
        if self.current_level == 2 and self.water_list:
            if arcade.check_for_collision_with_list(player, self.water_list):
                self.handle_hazard_collision()
                return
        
        # Проверка на завершение уровня
        if self.current_level == 3 and self.end_list:
            if arcade.check_for_collision_with_list(player, self.end_list):
                self.show_victory()

    def handle_hazard_collision(self):
        """Обработка столкновения с опасностью"""
        player = self.player_list[0]
        self.death_count += 1
        self.player_scale = max(self.player_scale - 0.005, self.min_scale)
        player.scale = self.player_scale
        
        if self.death_count >= 3:
            self.setup_menu()
        else:
            self.load_level(self.current_level, reset_coins=False)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка клика мыши"""
        if self.game_state == "MENU" and button == arcade.MOUSE_BUTTON_LEFT:
            half_width = self.button_width / 2
            half_height = self.button_height / 2
            
            rel_x = x - self.button_x
            rel_y = y - self.button_y
            
            angle_rad = -math.radians(self.button_angle)
            rotated_x = rel_x * math.cos(angle_rad) - rel_y * math.sin(angle_rad)
            rotated_y = rel_x * math.sin(angle_rad) + rel_y * math.cos(angle_rad)
            
            if (-half_width < rotated_x < half_width and 
                -half_height < rotated_y < half_height):
                self.show_intro()

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        self.held_keys.add(key)
        
        # Прыжок при нажатии SPACE или стрелки вверх
        if ((key == arcade.key.SPACE or key == arcade.key.UP) and 
            self.game_state == "GAME" and 
            self.player_list and 
            hasattr(self.player_list[0], 'can_jump') and 
            self.player_list[0].can_jump):
            
            self.player_list[0].change_y = JUMP_FORCE
            self.player_list[0].can_jump = False
            if self.jump_sound:
                arcade.play_sound(self.jump_sound)

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key in self.held_keys:
            self.held_keys.remove(key)

if __name__ == "__main__":
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()