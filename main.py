import arcade
import os
import time

# Константы игры
WIDTH = 1280
HEIGHT = 768
TITLE = "Mini Adventure"

SCALE_PLAYER = 0.02
SCALE_COIN = 0.05

SPEED = 60
GRAVITY = 1
JUMP_SPEED = 22

# Стартовые позиции игрока
LEVEL_START_POSITIONS = {
    1: (37, 120),
    2: (200, 400)
}

class Player(arcade.Sprite):
    def __init__(self, texture_right, texture_left, scale=1):
        super().__init__()
        self.texture_right = texture_right
        self.texture_left = texture_left
        self.scale = scale
        self.texture = texture_right
        self.speed = 5
        self.jumping = False
        self.on_ground = False
        self.facing_right = True

    def respawn(self, level):
        start_x, start_y = LEVEL_START_POSITIONS[level]
        self.center_x = start_x
        self.center_y = start_y
        self.change_x = 0
        self.change_y = 0
        self.facing_right = True
        self.texture = self.texture_right

class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        
        # Инициализация спрайт-листов
        self.scene = None
        self.player_list = arcade.SpriteList()
        self.physics_engine = None
        self.bg_sprites = arcade.SpriteList()
        
        # Установка рабочей директории
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        
        # Загрузка текстур
        try:
            self.bg1 = arcade.load_texture("images/loc1.png")
            self.bg2 = arcade.load_texture("images/loc2.png")
            player_texture_right = arcade.load_texture("images/big2.png")
            player_texture_left = arcade.load_texture("images/big2z.png")
            
            self.player = Player(player_texture_right, player_texture_left, SCALE_PLAYER)
            self.player_list.append(self.player)
            
        except FileNotFoundError as e:
            print(f"Ошибка загрузки текстур: {e}")
            raise
        
        # Загрузка первого уровня
        self.current_level = 1
        self.setup_level(1)
        
        # Управление
        self.left_pressed = False
        self.right_pressed = False
        self.space_pressed = False

    def setup_level(self, level_num):
        """Загрузка уровня"""
        self.current_level = level_num
        self.bg = self.bg1 if level_num == 1 else self.bg2
        
        try:
            # Настройка слоёв карты
            layer_options = {
                "Platforms": {"use_spatial_hash": True},
                "Spikes": {"use_spatial_hash": True},
                "water": {"use_spatial_hash": True},
                "portal": {"use_spatial_hash": True} if level_num == 1 else {},
                "plains": {"use_spatial_hash": True} if level_num == 2 else {}
            }
            
            # Загрузка тайл-карты
            map_path = f"maps/map{level_num}.json"
            if not os.path.exists(map_path):
                raise FileNotFoundError(f"Файл карты {map_path} не найден")
            
            self.tile_map = arcade.load_tilemap(map_path, scaling=1.0, layer_options=layer_options)
            self.scene = arcade.Scene.from_tilemap(self.tile_map)
            
            # Добавление игрока
            self.player.respawn(level_num)
            self.player_list.clear()
            self.player_list.append(self.player)
            
            # Настройка физического движка
            platforms = self.tile_map.sprite_lists.get("Platforms", arcade.SpriteList())
            self.physics_engine = arcade.PhysicsEnginePlatformer(
                self.player,
                platforms=platforms,
                gravity_constant=GRAVITY,
                walls=[self.scene["Walls"]] if "Walls" in self.tile_map.sprite_lists else None
            )
            
            # Настройка фона
            self.bg_sprites.clear()
            bg_sprite = arcade.Sprite()
            bg_sprite.texture = self.bg
            bg_sprite.center_x = WIDTH // 2
            bg_sprite.center_y = HEIGHT // 2
            bg_sprite.width = WIDTH
            bg_sprite.height = HEIGHT
            self.bg_sprites.append(bg_sprite)
            
            print(f"Уровень {level_num} загружен успешно")
            print(f"Загружено слоёв: {len(self.tile_map.sprite_lists)}")
            
        except Exception as e:
            print(f"Ошибка загрузки уровня {level_num}: {e}")
            raise

    def on_draw(self):
        """Отрисовка сцены"""
        self.clear()
        
        # Отрисовка фона
        self.bg_sprites.draw()
        
        # Отрисовка тайлмапа
        if hasattr(self, 'tile_map'):
            for sprite_list in self.tile_map.sprite_lists.values():
                sprite_list.draw()
        
        # Отрисовка игрока
        self.player_list.draw()
        
        # Отрисовка интерфейса
        arcade.draw_text(f"Уровень: {self.current_level}", 10, 10, arcade.color.WHITE, 24)

    def on_update(self, delta_time):
        """Обновление игры"""
        if self.physics_engine:
            # Проверка границ экрана
            if self.player.left < 0:
                self.player.left = 0
            if self.player.right > WIDTH:
                self.player.right = WIDTH
            if self.player.bottom < 0:
                self.player.respawn(self.current_level)
            
            # Проверка перехода на уровень 2
            if self.current_level == 1:
                portal_list = self.tile_map.sprite_lists.get("portal", None)
                if portal_list and arcade.check_for_collision_with_list(self.player, portal_list):
                    self.setup_level(2)
                    return
            
            # Проверка опасностей
            water_list = self.tile_map.sprite_lists.get("water", None)
            spikes_list = self.tile_map.sprite_lists.get("Spikes", None)
            
            if water_list and arcade.check_for_collision_with_list(self.player, water_list):
                self.player.respawn(self.current_level)
            if spikes_list and arcade.check_for_collision_with_list(self.player, spikes_list):
                self.player.respawn(self.current_level)
            
            # Обновление физики
            self.physics_engine.update()
        
        # Управление игроком
        self.player.change_x = 0
        
        if self.left_pressed:
            self.player.change_x = -self.player.speed
            self.player.texture = self.player.texture_left
            self.player.facing_right = False
            
        if self.right_pressed:
            self.player.change_x = self.player.speed
            self.player.texture = self.player.texture_right
            self.player.facing_right = True
            
        if self.space_pressed and self.physics_engine.can_jump():
            self.player.change_y = JUMP_SPEED
            self.space_pressed = False

    # Остальные методы без изменений
    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = True
        elif key in (arcade.key.SPACE, arcade.key.UP, arcade.key.W):
            self.space_pressed = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = False
        elif key in (arcade.key.SPACE, arcade.key.UP, arcade.key.W):
            self.space_pressed = False

if __name__ == "__main__":
    print(f"Используется Arcade версии {arcade.__version__}")
    
    try:
        game = MyGame(WIDTH, HEIGHT, TITLE)
        arcade.run()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")