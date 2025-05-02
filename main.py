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
        self.lilypads_list = arcade.SpriteList()  # Список для платформ-лилий
        
        # Звуки
        self.game_music = None
        self.music_player = None
        self.jump_sound = None
        
        # Предзагруженные текстуры
        self.preloaded_textures = {
            'player_right': None,
            'player_left': None,
            'backgrounds': {},
            'menu_bg': None,
            'lilypad': None  # Текстура для лилии
        }
        
        # Направление игрока
        self.player_facing_right = True
        
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
        # Загрузка звуков
        try:
            self.game_music = arcade.load_sound("sounds/menu.wav")
            self.jump_sound = arcade.load_sound("sounds/jump.wav")
        except Exception as e:
            print(f"Ошибка загрузки звуков: {e}")

        # Предзагрузка текстур игрока
        try:
            self.preloaded_textures['player_right'] = arcade.load_texture("images/big2.png")
            self.preloaded_textures['player_left'] = arcade.load_texture("images/big2z.png")
            # Загрузка текстуры лилии
            self.preloaded_textures['lilypad'] = arcade.load_texture("images/lilypad.png")
        except Exception as e:
            print(f"Ошибка загрузки текстур: {e}")

        # Предзагрузка фонов уровней
        for level in [1, 2]:
            path = f"images/loc{level}.png"
            if os.path.exists(path):
                try:
                    self.preloaded_textures['backgrounds'][level] = arcade.load_texture(path)
                except Exception as e:
                    print(f"Ошибка загрузки фона уровня {level}: {e}")

        # Предзагрузка фона меню
        try:
            self.preloaded_textures['menu_bg'] = arcade.load_texture("images/menu.png")
        except Exception as e:
            print(f"Ошибка загрузки фона меню: {e}")

    def create_lilypads(self):
        """Создание платформ-лилий для второго уровня"""
        # Координаты для трех лилий (можно изменить под свои нужды)
        lily_positions = [
            (470, 250),  # Первая лилия
            (600, 250),  # Вторая лилия
            (500, 50)   # Третья лилия
        ]
        
        for x, y in lily_positions:
            lilypad = arcade.Sprite()
            lilypad.texture = self.preloaded_textures['lilypad']
            lilypad.center_x = x
            lilypad.center_y = y
            lilypad.scale = 0.1
            self.lilypads_list.append(lilypad)
        
        # Добавляем лилии в список платформ для физики
        self.platforms_list.extend(self.lilypads_list)

    def start_music(self):
        """Запуск музыки"""
        if self.game_music and not self.music_player:
            self.music_player = arcade.play_sound(self.game_music, loop=True)

    def setup_menu(self):
        """Инициализация меню"""
        self.game_state = "MENU"
        self.menu_background_list.clear()
        
        if self.preloaded_textures['menu_bg']:
            bg = arcade.Sprite()
            bg.texture = self.preloaded_textures['menu_bg']
            bg.width = WIDTH
            bg.height = HEIGHT
            bg.center_x = WIDTH//2
            bg.center_y = HEIGHT//2
            self.menu_background_list.append(bg)

    def load_level(self, level_num):
        """Загрузка уровня с использованием предзагруженных ресурсов"""
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

        # Загрузка фона из предзагруженных текстур
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
                layer_options = {
                    "Platforms": {"use_spatial_hash": True},
                    "platforms": {"use_spatial_hash": True},
                    "Back": {"use_spatial_hash": False},
                    "back": {"use_spatial_hash": False},
                    "Spikes": {"use_spatial_hash": True},
                    "spikes": {"use_spatial_hash": True},
                    "Portal": {"use_spatial_hash": True} if level_num == 1 else {},
                    "portal": {"use_spatial_hash": True} if level_num == 1 else {},
                    "Water": {"use_spatial_hash": True},
                    "water": {"use_spatial_hash": True}
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
                    elif "portal" in lower_layer and level_num == 1:
                        self.portal_list = tilemap.sprite_lists[layer]
                    elif "water" in lower_layer and level_num == 2:
                        self.water_list = tilemap.sprite_lists[layer]
            except Exception as e:
                print(f"Ошибка загрузки карты: {e}")

        # Создание лилий для второго уровня
        if level_num == 2:
            self.create_lilypads()

        # Создание игрока из предзагруженных текстур
        if self.preloaded_textures['player_right']:
            player = arcade.Sprite()
            player.texture = self.preloaded_textures['player_right']
            player.scale = 0.02
            player.center_x = 100 if level_num == 1 else 50
            player.center_y = 400 if level_num == 1 else 380
            self.player_list.append(player)
            self.player_facing_right = True
        else:
            # Запасной вариант
            player = arcade.SpriteCircle(30, arcade.color.BLUE)
            player.center_x = 100
            player.center_y = 400
            self.player_list.append(player)

        # Инициализация физического движка
        if self.player_list and (self.platforms_list or self.lilypads_list):
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player_list[0],
                platforms=self.platforms_list,  # Включает обычные платформы и лилии
                gravity_constant=GRAVITY
            )

    def update_player_texture(self):
        """Обновление текстуры игрока в зависимости от направления"""
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
                # Отрисовываем лилии поверх воды
                if self.lilypads_list:
                    self.lilypads_list.draw()
            
            if self.current_level == 1 and self.portal_list:
                self.portal_list.draw()
            
            if self.player_list:
                self.player_list.draw()
            
            debug_info = [
                f"Уровень: {self.current_level}",
                f"Фон: {'есть' if self.background_list else 'нет'}",
                f"Платформы: {len(self.platforms_list)}",
                f"Лилии: {len(self.lilypads_list)}",
                f"Шипы: {len(self.spikes_list)}",
                f"Игрок: {'есть' if self.player_list else 'нет'}"
            ]
            
            for i, text in enumerate(debug_info):
                arcade.draw_text(text, 10, HEIGHT - 30 - i*30, arcade.color.WHITE, 16)

    def on_update(self, delta_time):
        if self.game_state == "MENU":
            self.animation_time += delta_time
            self.button_angle = math.sin(self.animation_time * 2) * 5
        
        elif self.game_state == "GAME" and self.player_list:
            player = self.player_list[0]
            
            # Сохраняем предыдущее направление
            prev_facing = self.player_facing_right
            
            # Определяем направление движения
            player.change_x = 0
            if arcade.key.LEFT in self.held_keys:
                player.change_x = -PLAYER_SPEED
                self.player_facing_right = False
            if arcade.key.RIGHT in self.held_keys:
                player.change_x = PLAYER_SPEED
                self.player_facing_right = True
            
            # Если направление изменилось - обновляем текстуру
            if prev_facing != self.player_facing_right:
                self.update_player_texture()
            
            # Границы экрана
            if player.left < 0:
                player.left = 0
            if player.right > WIDTH:
                player.right = WIDTH
            
            # Физика
            if self.physics_engine:
                self.physics_engine.update()
                player.can_jump = self.physics_engine.can_jump()
            
            # Обработка столкновений
            self.handle_collisions()

    def handle_collisions(self):
        """Обработка столкновений игрока с объектами"""
        if not self.player_list:
            return
            
        player = self.player_list[0]
        
        # Столкновение с шипами
        if self.spikes_list and arcade.check_for_collision_with_list(player, self.spikes_list):
            self.load_level(self.current_level)
            return
        
        # Столкновение с водой (на втором уровне)
        if self.current_level == 2 and self.water_list:
            if arcade.check_for_collision_with_list(player, self.water_list):
                self.load_level(2)
                return
        
        # Столкновение с порталом (на первом уровне)
        if self.current_level == 1 and self.portal_list:
            if arcade.check_for_collision_with_list(player, self.portal_list):
                self.load_level(2)
                return

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия кнопки мыши"""
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
                self.load_level(1)

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
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
        """Обработка отпускания клавиш"""
        if key in self.held_keys:
            self.held_keys.remove(key)

if __name__ == "__main__":
    game = MyGame(WIDTH, HEIGHT, TITLE)
    arcade.run()