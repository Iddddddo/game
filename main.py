import arcade
import math
import os

# Константы
WIDTH, HEIGHT = 1280, 768
TITLE = "Mini Adventure"
PLAYER_SPEED = 5
JUMP_FORCE = 21
GRAVITY = 0.9

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
        
        # Состояние монеток
        self.coin_positions = {
            1: [(300, 400), (600, 500), (900, 450)],
            2: [(350, 300), (700, 400), (950, 350)],
            3: [(400, 200), (750, 300), (1000, 250)]  # Монетки для 3 уровня
        }
        self.collected_coins = {1: set(), 2: set(), 3: set()}
        
        # Звуки
        self.game_music = None
        self.music_player = None
        self.jump_sound = None
        self.coin_sound = None
        
        # Предзагруженные текстуры
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
        self.death_count = 0
        self.initial_scale = 0.02
        self.coins_collected = 0
        self.total_coins = 3
        
        # Предзагрузка ресурсов
        self.preload_resources()
        
        # Параметры меню
        self.game_state = "MENU"
        self.current_level = 1
        self.animation_time = 0
        self.held_keys = set()
        self.physics_engine = None
        
        # Параметры кнопки
        self.button_x = WIDTH // 2
        self.button_y = HEIGHT // 2
        self.button_width = 300
        self.button_height = 100
        self.button_angle = 0
        
        self.setup_menu()
        self.start_music()

    def preload_resources(self):
        """Предзагрузка всех необходимых ресурсов"""
        try:
            self.game_music = arcade.load_sound("sounds/menu.wav")
            self.jump_sound = arcade.load_sound("sounds/jump.wav")
            self.coin_sound = arcade.load_sound("sounds/coin.wav")
        except Exception as e:
            print(f"Ошибка загрузки звуков: {e}")

        try:
            self.preloaded_textures['player_right'] = arcade.load_texture("images/big2.png")
            self.preloaded_textures['player_left'] = arcade.load_texture("images/big2z.png")
            self.preloaded_textures['lilypad'] = arcade.load_texture("images/lilypad.png")
            self.preloaded_textures['coin'] = arcade.load_texture("images/coin.png")
            self.preloaded_textures['portal'] = arcade.load_texture("images/portal.png")  # Текстура портала
        except Exception as e:
            print(f"Ошибка загрузки текстур: {e}")

        for level in [1, 2, 3]:  # Добавлен 3 уровень
            path = f"images/loc{level}.png"
            if os.path.exists(path):
                try:
                    self.preloaded_textures['backgrounds'][level] = arcade.load_texture(path)
                except Exception as e:
                    print(f"Ошибка загрузки фона уровня {level}: {e}")

        try:
            self.preloaded_textures['menu_bg'] = arcade.load_texture("images/menu.png")
        except Exception as e:
            print(f"Ошибка загрузки фона меню: {e}")

    def create_lilypads(self):
        """Создание платформ-лилий для второго уровня"""
        lily_positions = [
            (400, 250),
            (650, 350),
            (900, 300)
        ]
        
        for x, y in lily_positions:
            lilypad = arcade.Sprite()
            lilypad.texture = self.preloaded_textures['lilypad']
            lilypad.center_x = x
            lilypad.center_y = y
            lilypad.scale = 0.1
            self.lilypads_list.append(lilypad)
        
        self.platforms_list.extend(self.lilypads_list)

    def create_portal(self, x, y):
        """Создание портала на уровне"""
        portal = arcade.Sprite()
        portal.texture = self.preloaded_textures['portal']
        portal.center_x = x
        portal.center_y = y
        portal.scale = 0.5
        self.portal_list.append(portal)

    def create_coins(self, reset_coins=False):
        """Создание монеток для уровня с учетом уже собранных"""
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
                coin.scale = 0.05
                coin.index = i
                self.coins_list.append(coin)

    def start_music(self):
        """Запуск музыки"""
        if self.game_music and not self.music_player:
            self.music_player = arcade.play_sound(self.game_music, loop=True)

    def setup_menu(self):
        """Инициализация меню"""
        self.game_state = "MENU"
        self.menu_background_list.clear()
        
        # Полный сброс при возврате в меню
        self.player_scale = self.initial_scale
        self.death_count = 0
        self.coins_collected = 0
        self.collected_coins = {1: set(), 2: set(), 3: set()}
        self.current_level = 1
        
        if self.preloaded_textures['menu_bg']:
            bg = arcade.Sprite()
            bg.texture = self.preloaded_textures['menu_bg']
            bg.width = WIDTH
            bg.height = HEIGHT
            bg.center_x = WIDTH//2
            bg.center_y = HEIGHT//2
            self.menu_background_list.append(bg)

    def load_level(self, level_num, reset_coins=False):
        """Загрузка уровня"""
        self.game_state = "GAME"
        self.current_level = level_num
        
        # Очистка списков
        self.background_list = arcade.SpriteList()
        self.back_decor_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.platforms_list = arcade.SpriteList()
        self.portal_list = arcade.SpriteList()
        self.spikes_list = arcade.SpriteList()
        self.water_list = arcade.SpriteList()
        self.lilypads_list = arcade.SpriteList()
        self.coins_list = arcade.SpriteList()

        # Загрузка фона
        if level_num in self.preloaded_textures['backgrounds']:
            bg = arcade.Sprite()
            bg.texture = self.preloaded_textures['backgrounds'][level_num]
            bg.width = WIDTH
            bg.height = HEIGHT
            bg.center_x = WIDTH//2
            bg.center_y = HEIGHT//2
            self.background_list.append(bg)

        # Загрузка карты
        map_path = f"maps/map{level_num}.json"
        if os.path.exists(map_path):
            try:
                # Настройки слоев для разных уровней
                if level_num == 3:
                    layer_options = {
                        "Platforms": {"use_spatial_hash": True},
                        "platforms": {"use_spatial_hash": True},
                        "Spikes": {"use_spatial_hash": True},
                        "spikes": {"use_spatial_hash": True},
                        "Back": {"use_spatial_hash": False},
                        "back": {"use_spatial_hash": False}
                    }
                else:
                    layer_options = {
                        "Platforms": {"use_spatial_hash": True},
                        "platforms": {"use_spatial_hash": True},
                        "Back": {"use_spatial_hash": False},
                        "back": {"use_spatial_hash": False},
                        "Spikes": {"use_spatial_hash": True},
                        "spikes": {"use_spatial_hash": True},
                        "Portal": {"use_spatial_hash": True} if level_num == 1 else {},
                        "portal": {"use_spatial_hash": True} if level_num == 1 else {},
                        "Water": {"use_spatial_hash": True} if level_num == 2 else {},
                        "water": {"use_spatial_hash": True} if level_num == 2 else {}
                    }
                
                tilemap = arcade.load_tilemap(map_path, scaling=1.0, layer_options=layer_options)
                
                for layer in tilemap.sprite_lists:
                    lower_layer = layer.lower()
                    if "platform" in lower_layer:
                        self.platforms_list = tilemap.sprite_lists[layer]
                    elif "back" in lower_layer:
                        self.back_decor_list = tilemap.sprite_lists[layer]
                    elif "spike" in lower_layer:
                        self.spikes_list = tilemap.sprite_lists[layer]
                    elif "portal" in lower_layer and level_num in [1, 2]:  # Портал на 1 и 2 уровнях
                        self.portal_list = tilemap.sprite_lists[layer]
                    elif "water" in lower_layer and level_num == 2:
                        self.water_list = tilemap.sprite_lists[layer]
            except Exception as e:
                print(f"Ошибка загрузки карты: {e}")

        # Создание лилий для второго уровня
        if level_num == 2:
            self.create_lilypads()
            
        # Создание портала на втором уровне (если нет в тайлмапе)
        if level_num == 2 and not self.portal_list:
            self.create_portal(1100, 400)

        # Создание монеток
        self.create_coins(reset_coins)

        # Создание игрока
        if self.preloaded_textures['player_right']:
            player = arcade.Sprite()
            player.texture = self.preloaded_textures['player_right']
            player.scale = self.player_scale
            
            # Стартовые позиции для разных уровней
            if level_num == 1:
                player.center_x = 100
                player.center_y = 400
            elif level_num == 2:
                player.center_x = 50
                player.center_y = 380
            else:  # Уровень 3
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
        """Отрисовка"""
        self.clear()
        
        if self.game_state == "MENU":
            if self.menu_background_list:
                self.menu_background_list.draw()
            
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
            
        elif self.game_state == "GAME":
            if self.background_list:
                self.background_list.draw()
            
            if self.back_decor_list:
                self.back_decor_list.draw()
            
            if self.platforms_list:
                self.platforms_list.draw()
            
            if self.spikes_list:
                self.spikes_list.draw()
            
            if self.current_level == 2:
                if self.water_list:
                    self.water_list.draw()
                if self.lilypads_list:
                    self.lilypads_list.draw()
            
            if self.portal_list:
                self.portal_list.draw()
            
            self.coins_list.draw()
            
            if self.player_list:
                self.player_list.draw()
            
            debug_info = [
                f"Уровень: {self.current_level}",
                f"Размер: {self.player_scale:.3f}",
                f"Смерти: {self.death_count}/3",
                f"Монетки: {len(self.collected_coins[self.current_level])}/{self.total_coins}"
            ]
            
            for i, text in enumerate(debug_info):
                arcade.draw_text(text, 10, HEIGHT - 30 - i*30, arcade.color.WHITE, 16)

    def on_update(self, delta_time):
        if self.game_state == "MENU":
            self.animation_time += delta_time
            self.button_angle = math.sin(self.animation_time * 2) * 5
        
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
            if player.right > WIDTH:
                player.right = WIDTH
            
            if self.physics_engine:
                self.physics_engine.update()
                player.can_jump = self.physics_engine.can_jump()
            
            self.handle_collisions()

    def handle_collisions(self):
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
            
            self.player_scale += 0.015
            player.scale = self.player_scale
            
            if self.coin_sound:
                arcade.play_sound(self.coin_sound)
            
            if self.player_scale > self.initial_scale:
                self.player_scale = self.initial_scale
                player.scale = self.initial_scale
        
        # Переход на уровень 2 при сборе всех монеток на уровне 1
        if (self.current_level == 1 and 
            len(self.collected_coins[1]) == self.total_coins and 
            self.portal_list and 
            arcade.check_for_collision_with_list(player, self.portal_list)):
            self.load_level(2)
            return
            
        # Переход на уровень 3 через портал на уровне 2
        if (self.current_level == 2 and 
            self.portal_list and 
            arcade.check_for_collision_with_list(player, self.portal_list)):
            self.load_level(3)
            return
                
        # Столкновение с опасностями
        if self.spikes_list and arcade.check_for_collision_with_list(player, self.spikes_list):
            self.death_count += 1
            self.player_scale -= 0.001
            player.scale = self.player_scale
            
            if self.death_count >= 3:
                self.setup_menu()
            else:
                self.load_level(self.current_level, reset_coins=False)
            return
        
        if self.current_level == 2 and self.water_list:
            if arcade.check_for_collision_with_list(player, self.water_list):
                self.death_count += 1
                self.player_scale -= 0.001
                player.scale = self.player_scale
                
                if self.death_count >= 3:
                    self.setup_menu()
                else:
                    self.load_level(2, reset_coins=False)
                return

    def on_mouse_press(self, x, y, button, modifiers):
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
                self.load_level(1, reset_coins=True)

    def on_key_press(self, key, modifiers):
        self.held_keys.add(key)
        
        if (key == arcade.key.SPACE and 
            self.game_state == "GAME" and 
            self.player_list and 
            hasattr(self.player_list[0], 'can_jump') and 
            self.player_list[0].can_jump):
            
            self.player_list[0].change_y = JUMP_FORCE
            self.player_list[0].can_jump = False
            if self.jump_sound:
                arcade.play_sound(self.jump_sound)

    def on_key_release(self, key, modifiers):
        if key in self.held_keys:
            self.held_keys.remove(key)

if __name__ == "__main__":
    game = MyGame(WIDTH, HEIGHT, TITLE)
    arcade.run()