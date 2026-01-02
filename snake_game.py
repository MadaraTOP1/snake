"""
Изгиб Питона — реализация логики игры "Змейка".

Файл: snake_game.py
Требования: pygame

Запуск:
    python snake_game.py
"""

import random
import sys
from typing import List, Tuple, Optional

import pygame

# Константы игрового поля
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
CELL_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE  # 32
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE  # 24

# Цвета (RGB)
COLOR_BG = (0, 0, 0)
COLOR_SNAKE = (0, 255, 0)
COLOR_APPLE = (255, 0, 0)

# Скорость (итераций в секунду)
FPS = 20

# Направления как вектора (dx, dy) в пикселях
UP = (0, -CELL_SIZE)
DOWN = (0, CELL_SIZE)
LEFT = (-CELL_SIZE, 0)
RIGHT = (CELL_SIZE, 0)


class GameObject:
    """
    Базовый класс игрового объекта.

    Атрибуты:
        position: координаты верхнего левого угла объекта (кортеж (x, y)).
    """

    def __init__(self, position: Tuple[int, int]):
        """
        Инициализирует GameObject с заданной позицией.

        :param position: начальная позиция (x, y)
        """
        self.position = position

    def draw(self, surface: pygame.Surface) -> None:
        """
        Абстрактный метод отрисовки — должен быть переопределён в наследниках.
        """
        pass


class Apple(GameObject):
    """
    Класс яблока.

    Яблоко занимает одну ячейку и создаётся в случайной позиции,
    не пересекающейся со змейкой (если передается список позиций змейки).
    """

    def __init__(self, forbidden_positions: Optional[List[Tuple[int, int]]] = None):
        """
        Инициализирует яблоко и размещает его случайно.

        :param forbidden_positions: список координат, в которых яблоко ставить нельзя
        """
        # временная позиция — затем заменится randomize_position
        center_x = (GRID_WIDTH // 2) * CELL_SIZE
        center_y = (GRID_HEIGHT // 2) * CELL_SIZE
        super().__init__((center_x, center_y))
        self.body_color = COLOR_APPLE
        self.randomize_position(forbidden_positions or [])

    def randomize_position(self, forbidden_positions: List[Tuple[int, int]]) -> None:
        """
        Устанавливает случайную позицию яблока, избегая forbidden_positions.

        :param forbidden_positions: список координат, недопустимых для яблока
        """
        attempts = 0
        while True:
            x = random.randrange(0, GRID_WIDTH) * CELL_SIZE
            y = random.randrange(0, GRID_HEIGHT) * CELL_SIZE
            if (x, y) not in forbidden_positions:
                self.position = (x, y)
                return
            attempts += 1
            # В случае редкой невозможности (очень длинная змея) — сделаем дополнительную защиту
            if attempts > 1000:
                # Попробуем выбрать любую позицию (падение назад)
                for gx in range(GRID_WIDTH):
                    for gy in range(GRID_HEIGHT):
                        maybe = (gx * CELL_SIZE, gy * CELL_SIZE)
                        if maybe not in forbidden_positions:
                            self.position = maybe
                            return


class Snake(GameObject):
    """
    Класс змейки.

    Змея представлена списком координат (positions), где первый элемент — голова.
    """

    def __init__(self):
        """
        Инициализирует змейку в центре игрового поля, длиной 1, движущуюся вправо.
        """
        center_x = (GRID_WIDTH // 2) * CELL_SIZE
        center_y = (GRID_HEIGHT // 2) * CELL_SIZE
        super().__init__((center_x, center_y))
        self.body_color = COLOR_SNAKE
        # Список сегментов: первый — голова
        self.positions: List[Tuple[int, int]] = [(center_x, center_y)]
        self.length: int = 1
        self.direction: Tuple[int, int] = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None

    def get_head_position(self) -> Tuple[int, int]:
        """
        Возвращает координаты головы змейки.
        """
        return self.positions[0]

    @staticmethod
    def _opposite(dir1: Tuple[int, int], dir2: Tuple[int, int]) -> bool:
        """
        Проверяет, являются ли направления противоположными.
        """
        return dir1[0] == -dir2[0] and dir1[1] == -dir2[1]

    def update_direction(self) -> None:
        """
        Применяет next_direction (если задано) с проверкой, что нельзя ехать назад.
        """
        if self.next_direction is None:
            return
        if not self._opposite(self.next_direction, self.direction):
            self.direction = self.next_direction
        # После применения очищаем следующий ход
        self.next_direction = None

    def move(self) -> Optional[Tuple[int, int]]:
        """
        Сдвигает змейку на одну ячейку в текущем направлении.

        Возвращает координаты удалённого хвостового сегмента (если он удалён),
        иначе None (если длина увеличилась и хвост не удалялся).
        """
        current_head = self.get_head_position()
        new_head_x = current_head[0] + self.direction[0]
        new_head_y = current_head[1] + self.direction[1]

        # Обертка по краям: проход сквозь стену на противоположную сторону
        if new_head_x < 0:
            new_head_x = (GRID_WIDTH - 1) * CELL_SIZE
        elif new_head_x >= SCREEN_WIDTH:
            new_head_x = 0
        if new_head_y < 0:
            new_head_y = (GRID_HEIGHT - 1) * CELL_SIZE
        elif new_head_y >= SCREEN_HEIGHT:
            new_head_y = 0

        new_head = (new_head_x, new_head_y)
        # Вставляем новую голову в начало списка
        self.positions.insert(0, new_head)
        removed_tail: Optional[Tuple[int, int]] = None

        # Если текущая длина списка превысила ожидаемую длину — удаляем хвост
        if len(self.positions) > self.length:
            removed_tail = self.positions.pop()
        return removed_tail

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовывает змейку на поверхности.
        """
        for pos in self.positions:
            rect = pygame.Rect(pos[0], pos[1], CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, self.body_color, rect)

    def reset(self) -> None:
        """
        Сбрасывает змейку в начальное состояние (после столкновения с собой).
        """
        center_x = (GRID_WIDTH // 2) * CELL_SIZE
        center_y = (GRID_HEIGHT // 2) * CELL_SIZE
        self.positions = [(center_x, center_y)]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None


def handle_key_event(event: pygame.event.Event, snake: Snake) -> None:
    """
    Обработка нажатий клавиш для управления змейкой.

    Поддерживаются стрелки и WASD.
    """
    if event.type != pygame.KEYDOWN:
        return

    key = event.key
    if key == pygame.K_UP or key == pygame.K_w:
        snake.next_direction = UP
    elif key == pygame.K_DOWN or key == pygame.K_s:
        snake.next_direction = DOWN
    elif key == pygame.K_LEFT or key == pygame.K_a:
        snake.next_direction = LEFT
    elif key == pygame.K_RIGHT or key == pygame.K_d:
        snake.next_direction = RIGHT


def main() -> None:
    """
    Основная функция: инициализация Pygame, создание объектов и игровой цикл.
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Изгиб Питона — Змейка")
    clock = pygame.time.Clock()

    snake = Snake()
    apple = Apple(forbidden_positions=snake.positions)

    running = True
    while running:
        # --- Обработка событий ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            handle_key_event(event, snake)

        if not running:
            break

        # Применяем направление, затем двигаем змейку
        snake.update_direction()
        removed_tail = snake.move()

        # Проверяем съела ли змейка яблоко (голова совпала с позицией яблока)
        if snake.get_head_position() == apple.position:
            # Увеличиваем длину на 1 — и возвращаем удалённый хвост (если был)
            snake.length += 1
            # Если при движении хвост удалялся, восстанавливаем его — чтобы рост произошёл сразу
            if removed_tail is not None:
                snake.positions.append(removed_tail)
                removed_tail = None
            # Перемещаем яблоко в новую случайную позицию, избегая текущих позиций змейки
            apple.randomize_position(snake.positions)

        # Проверяем столкновение головы с телом (кроме первого элемента)
        head = snake.get_head_position()
        if head in snake.positions[1:]:
            # Сброс при самопересечении
            snake.reset()
            # Переставим яблоко в безопасное место
            apple.randomize_position(snake.positions)

        # --- Отрисовка ---
        screen.fill(COLOR_BG)

        # Отрисуем яблоко и змейку
        # Яблоко
        apple_rect = pygame.Rect(apple.position[0], apple.position[1], CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, apple.body_color, apple_rect)

        # Змейка
        snake.draw(screen)

        # Обновляем экран
        pygame.display.update()

        # Ограничение частоты обновлений
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
