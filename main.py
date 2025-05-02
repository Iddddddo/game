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
        
        # Звуки
        self.game_music = None
        self.music_player = None
        self.jump_sound = None
        self.load_sounds()
        
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
        # Запускаем музыку при инициализации игры
        self.start_music()

    def load_sounds(self):
        """Загрузка звуков"""
        try:
            self.game_music = arcade.load_sound("sounds/menu.wav")
        except:
            print("Ошибка загрузки музыки")
            
        try:
            self.jump_sound = arcade.load_sound("sounds/jump.wav")
        except:
            print("Ошибка загрузки звука прыжка")

    def start_music(self):
        """Запуск музыки"""
        if self.game_music and not self.music_player:
            self.music_player = arcade.play_sound(self.game_music, loop=True)

    def setup_menu(self):
        """Инициализация меню"""
        self.game_state = "MENU"
        self.menu_background_list.clear()
        
        try:
            bg = arcade.Sprite("images/menu.png")
            bg.width = WIDTH
            bg.height = HEIGHT
            bg.center_x = WIDTH//2
            bg.center_y = HEIGHT//2
            self.menu_background_list.append(bg)
        except Exception as e:
            print(f"Ошибка загрузки фона меню: {e}")

    def load_level(self, level_num):
        """Полностью переработанная загрузка уровня"""
        self.game_state = "GAME"
        self.current_level = level_num
        
        print(f"\n=== Начало загрузки уровня {level_num} ===")

        # 2. Полная переинициализация списков
        self.background_list = arcade.SpriteList()
        self.back_decor_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.platforms_list = arcade.SpriteList()
        self.portal_list = arcade.SpriteList()
        self.spikes_list = arcade.SpriteList()
        self.water_list = arcade.SpriteList()

        # 3. Загрузка фона (проверяем несколько возможных путей)
        bg_loaded = False
        bg_paths = [
            f"images/loc{level_num}.png",
        ]
        
        for bg_path in bg_paths:
            try:
                if os.path.exists(bg_path):
                    bg = arcade.Sprite(bg_path)
                    bg.width = WIDTH
                    bg.height = HEIGHT
                    bg.center_x = WIDTH//2
                    bg.center_y = HEIGHT//2
                    self.background_list.append(bg)
                    print(f"Фон загружен из {bg_path}")
                    bg_loaded = True
                    break
            except Exception as e:
                print(f"Ошибка загрузки фона {bg_path}: {e}")
        
        if not bg_loaded:
            print("Не удалось загрузить фон уровня!")

        # 4. Загрузка карты (пробуем разные форматы и пути)
        map_loaded = False
        map_paths = [
            f"maps/map{level_num}.json"
        ]
        
        for map_path in map_paths:
            try:
                if os.path.exists(map_path):
                    print(f"Попытка загрузить карту из {map_path}")
                    
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
                    
                    # Универсальное получение слоев (без учета регистра)
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
                    
                    print(f"Карта загружена из {map_path}")
                    print(f"Платформы: {len(self.platforms_list)}")
                    print(f"Декорации: {len(self.back_decor_list)}")
                    print(f"Шипы: {len(self.spikes_list)}")
                    if level_num == 1:
                        print(f"Порталы: {len(self.portal_list)}")
                    if level_num == 2:
                        print(f"Вода: {len(self.water_list)}")
                    
                    map_loaded = True
                    break
                    
            except Exception as e:
                print(f"Ошибка загрузки карты {map_path}: {e}")
        
        if not map_loaded:
            print("Не удалось загрузить карту уровня!")

        # 5. Создание игрока (с несколькими попытками)
        player_loaded = False
        player_paths = [
            "images/big2.png",
            "images/player.png",
            "images/character.png"
        ]
        
        for player_path in player_paths:
            try:
                if os.path.exists(player_path):
                    player_texture = arcade.load_texture(player_path)
                    player = arcade.Sprite()
                    player.texture = player_texture
                    player.scale = 0.02
                    player.center_x = 100 if level_num == 1 else 50
                    player.center_y = 400 if level_num == 1 else 380
                    self.player_list.append(player)
                    print(f"Игрок загружен из {player_path}")
                    player_loaded = True
                    break
            except Exception as e:
                print(f"Ошибка загрузки игрока {player_path}: {e}")
        
        if not player_loaded:
            print("Не удалось загрузить текстуру игрока!")
            # Создаем простого игрока как запасной вариант
            player = arcade.SpriteCircle(30, arcade.color.BLUE)
            player.center_x = 100
            player.center_y = 400
            self.player_list.append(player)
            print("Создан простой игрок (запасной вариант)")

        # 6. Инициализация физического движка
        if len(self.platforms_list) > 0 and len(self.player_list) > 0:
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player_list[0],
                platforms=self.platforms_list,
                gravity_constant=GRAVITY
            )
            print("Физический движок инициализирован")
        else:
            print("Не удалось инициализировать физический движок!")
            print(f"Платформы: {len(self.platforms_list)}, Игрок: {len(self.player_list)}")

        print(f"=== Завершение загрузки уровня {level_num} ===\n")
        return True

    def on_draw(self):
        """Отрисовка"""
        self.clear()
        
        if self.game_state == "MENU":
            if self.menu_background_list:
                self.menu_background_list.draw()
            
            # Рисуем кнопку с помощью четырехугольника
            points = [
                (self.button_x - self.button_width/2, self.button_y - self.button_height/2),
                (self.button_x + self.button_width/2, self.button_y - self.button_height/2),
                (self.button_x + self.button_width/2, self.button_y + self.button_height/2),
                (self.button_x - self.button_width/2, self.button_y + self.button_height/2)
            ]
            
            # Применяем поворот к точкам
            rotated_points = []
            for point in points:
                x, y = point
                # Переносим в начало координат
                x -= self.button_x
                y -= self.button_y
                # Поворачиваем
                new_x = x * math.cos(math.radians(self.button_angle)) - y * math.sin(math.radians(self.button_angle))
                new_y = x * math.sin(math.radians(self.button_angle)) + y * math.cos(math.radians(self.button_angle))
                # Возвращаем на место
                new_x += self.button_x
                new_y += self.button_y
                rotated_points.append((new_x, new_y))
            
            arcade.draw_polygon_filled(rotated_points, (144, 238, 144, 180))
            
            # Рисуем текст на кнопке
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
            
            if self.current_level == 2 and self.water_list:
                self.water_list.draw()
            
            if self.current_level == 1 and self.portal_list:
                self.portal_list.draw()
            
            if self.player_list:
                self.player_list.draw()
            
            # Отладочная информация
            debug_info = [
                f"Уровень: {self.current_level}",
                f"Фон: {'есть' if self.background_list else 'нет'}",
                f"Платформы: {len(self.platforms_list)}",
                f"Шипы: {len(self.spikes_list)}",
                f"Игрок: {'есть' if self.player_list else 'нет'}"
            ]
            
            for i, text in enumerate(debug_info):
                arcade.draw_text(text, 10, HEIGHT - 30 - i*30, arcade.color.WHITE, 16)

    def on_update(self, delta_time):
        if self.game_state == "MENU":
            # Анимация покачивания кнопки
            self.animation_time += delta_time
            self.button_angle = math.sin(self.animation_time * 2) * 5
        
        elif self.game_state == "GAME" and self.player_list:
            player = self.player_list[0]
            
            # Движение
            player.change_x = 0
            if arcade.key.LEFT in self.held_keys:
                player.change_x = -PLAYER_SPEED
            if arcade.key.RIGHT in self.held_keys:
                player.change_x = PLAYER_SPEED
            
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
        """Обработка столкновений"""
        if not self.player_list:
            return
            
        player = self.player_list[0]
        
        if self.spikes_list and arcade.check_for_collision_with_list(player, self.spikes_list):
            self.load_level(self.current_level)
            return
        
        if self.current_level == 2 and self.water_list:
            if arcade.check_for_collision_with_list(player, self.water_list):
                self.load_level(2)
                return
        
        if self.current_level == 1 and self.portal_list:
            if arcade.check_for_collision_with_list(player, self.portal_list):
                self.load_level(2)
                return

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_state == "MENU" and button == arcade.MOUSE_BUTTON_LEFT:
            # Проверяем попадание в кнопку с учетом поворота
            half_width = self.button_width / 2
            half_height = self.button_height / 2
            
            # Преобразуем координаты для проверки с учетом поворота
            rel_x = x - self.button_x
            rel_y = y - self.button_y
            
            angle_rad = -math.radians(self.button_angle)
            rotated_x = rel_x * math.cos(angle_rad) - rel_y * math.sin(angle_rad)
            rotated_y = rel_x * math.sin(angle_rad) + rel_y * math.cos(angle_rad)
            
            if (-half_width < rotated_x < half_width and 
                -half_height < rotated_y < half_height):
                self.load_level(1)

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