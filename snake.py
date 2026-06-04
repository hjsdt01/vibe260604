import random
import tkinter as tk

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
UPDATE_DELAY = 120  # milliseconds

DIRECTIONS = {
    'Up': (0, -1),
    'Down': (0, 1),
    'Left': (-1, 0),
    'Right': (1, 0)
}

OPPOSITE = {
    'Up': 'Down',
    'Down': 'Up',
    'Left': 'Right',
    'Right': 'Left'
}

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.width = GRID_WIDTH * CELL_SIZE
        self.height = GRID_HEIGHT * CELL_SIZE
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg='black')
        self.canvas.pack()

        self.reset_game()
        self.root.bind('<Key>', self.on_key_press)
        self.running = True
        self.update()

    def reset_game(self):
        self.human_direction = 'Right'
        self.ai_direction = 'Left'
        self.human_snake = [(5, GRID_HEIGHT // 2), (4, GRID_HEIGHT // 2), (3, GRID_HEIGHT // 2)]
        self.ai_snake = [(GRID_WIDTH - 6, GRID_HEIGHT // 2), (GRID_WIDTH - 5, GRID_HEIGHT // 2), (GRID_WIDTH - 4, GRID_HEIGHT // 2)]
        self.human_score = 0
        self.ai_score = 0
        self.place_food()
        self.draw()

    def place_food(self):
        occupied = set(self.human_snake + self.ai_snake)
        while True:
            self.food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if self.food not in occupied:
                break

    def draw_cell(self, position, color):
        x, y = position
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='gray20')

    def draw(self):
        self.canvas.delete('all')
        self.draw_cell(self.food, 'red')

        for index, part in enumerate(self.human_snake):
            color = 'cyan' if index == 0 else 'blue'
            self.draw_cell(part, color)

        for index, part in enumerate(self.ai_snake):
            color = 'orange' if index == 0 else 'yellow'
            self.draw_cell(part, color)

        score_text = f'Human: {self.human_score}   AI: {self.ai_score}'
        self.canvas.create_text(10, 10, text=score_text, fill='white', anchor='nw', font=('Arial', 12, 'bold'))
        self.canvas.create_text(10, 30, text='Arrow keys: human', fill='white', anchor='nw', font=('Arial', 10))

    def on_key_press(self, event):
        key = event.keysym
        if key in DIRECTIONS:
            if key != OPPOSITE[self.human_direction]:
                self.human_direction = key

    def ai_choose_direction(self):
        target = self.food
        candidates = []

        for direction, delta in DIRECTIONS.items():
            if direction == OPPOSITE[self.ai_direction]:
                continue
            new_head = self._next_position(self.ai_snake[0], delta)
            if self.is_safe_position(new_head, self.ai_snake):
                distance = abs(new_head[0] - target[0]) + abs(new_head[1] - target[1])
                candidates.append((distance, direction))

        if candidates:
            candidates.sort()
            return candidates[0][1]

        for direction, delta in DIRECTIONS.items():
            new_head = self._next_position(self.ai_snake[0], delta)
            if self.is_safe_position(new_head, self.ai_snake):
                return direction

        return self.ai_direction

    def _next_position(self, position, delta):
        return position[0] + delta[0], position[1] + delta[1]

    def is_safe_position(self, position, snake_body):
        x, y = position
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return False

        occupied = set(self.human_snake + self.ai_snake)
        if position in occupied:
            return False

        if position in snake_body[:-1]:
            return False

        return True

    def update(self):
        if not self.running:
            return

        self.ai_direction = self.ai_choose_direction()

        human_head = self._next_position(self.human_snake[0], DIRECTIONS[self.human_direction])
        ai_head = self._next_position(self.ai_snake[0], DIRECTIONS[self.ai_direction])

        if self.is_collision(human_head, self.human_snake, self.ai_snake):
            self.game_over('AI')
            return

        if self.is_collision(ai_head, self.ai_snake, self.human_snake):
            self.game_over('Human')
            return

        if human_head == ai_head:
            self.game_over('Draw')
            return

        self.human_snake.insert(0, human_head)
        self.ai_snake.insert(0, ai_head)

        human_ate = human_head == self.food
        ai_ate = ai_head == self.food

        if human_ate and ai_ate:
            self.human_score += 1
            self.ai_score += 1
            self.place_food()
        elif human_ate:
            self.human_score += 1
            self.place_food()
        elif ai_ate:
            self.ai_score += 1
            self.place_food()

        if not human_ate:
            self.human_snake.pop()
        if not ai_ate:
            self.ai_snake.pop()

        self.draw()
        self.root.after(UPDATE_DELAY, self.update)

    def is_collision(self, new_head, self_snake, other_snake):
        x, y = new_head
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return True

        if new_head in self_snake[:-1]:
            return True

        if new_head in other_snake:
            return True

        return False

    def game_over(self, winner):
        self.running = False
        if winner == 'Draw':
            title = 'Draw!'
            message = 'Both snakes collided.'
        else:
            title = 'Game Over'
            message = f'{winner} wins!'

        self.canvas.create_text(self.width // 2, self.height // 2 - 20,
                                text=title, fill='white', font=('Arial', 24, 'bold'))
        self.canvas.create_text(self.width // 2, self.height // 2 + 10,
                                text=message, fill='white', font=('Arial', 16))
        self.canvas.create_text(self.width // 2, self.height // 2 + 40,
                                text=f'Human: {self.human_score}   AI: {self.ai_score}',
                                fill='white', font=('Arial', 12))
        self.canvas.create_text(self.width // 2, self.height // 2 + 70,
                                text='Press R to retry', fill='white', font=('Arial', 12))
        self.root.bind('<Key-r>', self.on_retry)

    def on_retry(self, event):
        self.reset_game()
        self.running = True
        self.root.bind('<Key>', self.on_key_press)
        self.update()

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Snake Game: Human vs AI')
    game = SnakeGame(root)
    root.mainloop()
