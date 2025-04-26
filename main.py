import arcade
import os

# Константы игры
WIDTH = 1280
HEIGHT = 768
TITLE = "Mini Adventure"

SCALE_PLAYER = 0.02
SCALE_LILYPAD = 0.5
SPEED = 5
GRAVITY = 1
JUMP_SPEED = 22

# Настройки кувшинок
LILYPAD_DISAPPEAR_DELAY = 2.0
LILYPAD_REAPPEAR_DELAY = 5.0

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        
        # Спрайтлисты
        self.background_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.platforms_list = arcade.SpriteList()
        self.hazards_list = arcade.SpriteList()
        self.portal_list = arcade.SpriteList()
        self.lilypads_list = arcade.SpriteList()
        self.active_lilypads = arcade.SpriteList()
        
        self.current_level = 1
        self.physics_engine = None
        self.lilypads_data = {}
        
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        
        print("Инициализация игры...")  # Отладочный вывод
        self.setup_level(1)
        
        self.left_pressed = False
        self.right_pressed = False
        self.space_pressed = False

    def setup_level(self, level_num):
        print(f"Загрузка уровня {level_num}...")  # Отладочный вывод
        self.current_level = level_num
        
        # Очистка спрайтлистов
        self.background_list.clear()
        self.player_list.clear()
        self.platforms_list.clear()
        self.hazards_list.clear()
        self.portal_list.clear()
        self.lilypads_list.clear()
        self.active_lilypads.clear()
        self.lilypads_data = {}
        
        # Загрузка фона с проверкой
        try:
            background = arcade.Sprite(f"images/loc{level_num}.png")
            background.center_x = WIDTH // 2
            background.center_y = HEIGHT // 2
            background.width = WIDTH
            background.height = HEIGHT
            self.background_list.append(background)
            print("Фон успешно загружен")  # Отладочный вывод
        except Exception as e:
            print(f"Ошибка загрузки фона: {e}")  # Отладочный вывод
        
        # Создание игрока с проверкой
        try:
            player = arcade.Sprite("images/big2.png", SCALE_PLAYER)
            start_x, start_y = (100, 300) if level_num == 1 else (50, 380)
            player.center_x = start_x
            player.center_y = start_y
            self.player_list.append(player)
            print("Игрок успешно создан")  # Отладочный вывод
        except Exception as e:
            print(f"Ошибка создания игрока: {e}")  # Отладочный вывод
        
        # Загрузка карты Tiled с проверкой
        try:
            layer_options = {
                "Platforms": {"use_spatial_hash": True},
                "Spikes": {"use_spatial_hash": True},
                "water": {"use_spatial_hash": True},
                "portal": {"use_spatial_hash": True},
                "plains": {"use_spatial_hash": True},
                "Walls": {"use_spatial_hash": True}
            }
            
            map_path = f"maps/map{level_num}.json"
            print(f"Попытка загрузки карты: {map_path}")  # Отладочный вывод
            self.tile_map = arcade.load_tilemap(map_path, scaling=1.0, layer_options=layer_options)
            print("Карта успешно загружена")  # Отладочный вывод
            
            # Распределение объектов по слоям с проверкой
            if "Platforms" in self.tile_map.sprite_lists:
                self.platforms_list.extend(self.tile_map.sprite_lists["Platforms"])
                print(f"Загружено платформ: {len(self.platforms_list)}")  # Отладочный вывод
            
            if "Spikes" in self.tile_map.sprite_lists:
                self.hazards_list.extend(self.tile_map.sprite_lists["Spikes"])
                print(f"Загружено шипов: {len(self.hazards_list)}")  # Отладочный вывод
            
            if "water" in self.tile_map.sprite_lists:
                self.hazards_list.extend(self.tile_map.sprite_lists["water"])
                print(f"Загружено воды: {len(self.hazards_list)-len(self.tile_map.sprite_lists['Spikes'])}")  # Отладочный вывод
            
            if "portal" in self.tile_map.sprite_lists:
                self.portal_list.extend(self.tile_map.sprite_lists["portal"])
                print(f"Загружено порталов: {len(self.portal_list)}")  # Отладочный вывод
            
            # Инициализация кувшинок с проверкой
            if "plains" in self.tile_map.sprite_lists:
                try:
                    lilypad_texture = arcade.load_texture("images/lilypad.png")
                    print("Текстура кувшинки загружена")  # Отладочный вывод
                    
                    for lilypad in self.tile_map.sprite_lists["plains"]:
                        new_lilypad = arcade.Sprite(lilypad_texture, SCALE_LILYPAD)
                        new_lilypad.position = lilypad.position
                        new_lilypad.width = lilypad.width
                        new_lilypad.height = lilypad.height
                        new_lilypad.alpha = 255
                        
                        self.lilypads_list.append(new_lilypad)
                        self.active_lilypads.append(new_lilypad)
                        self.lilypads_data[new_lilypad] = {
                            'active': True,
                            'touch_time': 0.0,
                            'disappear_time': 0.0
                        }
                    
                    print(f"Загружено кувшинок: {len(self.lilypads_list)}")  # Отладочный вывод
                except Exception as e:
                    print(f"Ошибка загрузки кувшинок: {e}")  # Отладочный вывод
            
        except Exception as e:
            print(f"Ошибка загрузки карты: {e}")  # Отладочный вывод
        
        self.update_physics_engine()
        print("Уровень загружен")  # Отладочный вывод

    def update_physics_engine(self):
        all_platforms = arcade.SpriteList()
        all_platforms.extend(self.platforms_list)
        
        if self.current_level == 2:
            all_platforms.extend(self.active_lilypads)
        
        try:
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player_list[0] if len(self.player_list) > 0 else None,
                platforms=all_platforms,
                gravity_constant=GRAVITY,
                walls=self.tile_map.sprite_lists.get("Walls", None)
            )
            print("Физический движок обновлен")  # Отладочный вывод
        except Exception as e:
            print(f"Ошибка инициализации физики: {e}")  # Отладочный вывод

    def on_draw(self):
        self.clear()
        
        # Рисуем все объекты через спрайтлисты
        try:
            self.background_list.draw()
            self.platforms_list.draw()
            self.hazards_list.draw()
            self.portal_list.draw()
            self.active_lilypads.draw()
            self.player_list.draw()
            
            # Отладочная информация
            arcade.draw_text(f"Уровень: {self.current_level}", 10, HEIGHT - 30, arcade.color.WHITE, 24)
        except Exception as e:
            print(f"Ошибка отрисовки: {e}")  # Отладочный вывод

    def on_update(self, delta_time):
        if len(self.player_list) == 0:
            return
            
        player = self.player_list[0]
        
        # Проверка перехода на уровень 2
        if self.current_level == 1 and len(self.portal_list) > 0:
            if arcade.check_for_collision_with_list(player, self.portal_list):
                self.setup_level(2)
                return
        
        # Проверка опасностей
        if len(self.hazards_list) > 0:
            if arcade.check_for_collision_with_list(player, self.hazards_list):
                self.setup_level(self.current_level)
                return
        
        # Механика кувшинок
        if self.current_level == 2 and len(self.lilypads_list) > 0:
            need_update = False
            for lilypad in self.lilypads_list:
                data = self.lilypads_data[lilypad]
                
                if not data['active']:
                    data['disappear_time'] += delta_time
                    if data['disappear_time'] >= LILYPAD_REAPPEAR_DELAY:
                        data['active'] = True
                        data['disappear_time'] = 0.0
                        lilypad.alpha = 255
                        if lilypad not in self.active_lilypads:
                            self.active_lilypads.append(lilypad)
                        need_update = True
                    continue
                
                if arcade.check_for_collision(player, lilypad):
                    data['touch_time'] += delta_time
                    if data['touch_time'] >= LILYPAD_DISAPPEAR_DELAY:
                        data['active'] = False
                        data['touch_time'] = 0.0
                        lilypad.alpha = 0
                        if lilypad in self.active_lilypads:
                            self.active_lilypads.remove(lilypad)
                        need_update = True
                else:
                    data['touch_time'] = 0.0
            
            if need_update:
                self.update_physics_engine()
        
        # Управление
        player.change_x = 0
        if self.left_pressed:
            player.change_x = -SPEED
        if self.right_pressed:
            player.change_x = SPEED
        if self.space_pressed and self.physics_engine and self.physics_engine.can_jump():
            player.change_y = JUMP_SPEED
        
        if self.physics_engine:
            self.physics_engine.update()

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = True
        elif key == arcade.key.SPACE:
            self.space_pressed = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = False
        elif key == arcade.key.SPACE:
            self.space_pressed = False

if __name__ == "__main__":
    try:
        print("Запуск игры...")  # Отладочный вывод
        game = MyGame(WIDTH, HEIGHT, TITLE)
        arcade.run()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")