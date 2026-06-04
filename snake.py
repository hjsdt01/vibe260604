import random
import tkinter as tk

CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
UPDATE_DELAY = 120  # milliseconds

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
        self.direction = 'Right'
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2),
                      (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
                      (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)]
        self.score = 0
        self.place_food()
        self.draw()

    def place_food(self):
        while True:
            self.food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if self.food not in self.snake:
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
        for index, part in enumerate(self.snake):
            color = 'lime' if index == 0 else 'green'
            self.draw_cell(part, color)
        self.canvas.create_text(60, 12, text=f'Score: {self.score}', fill='white', anchor='nw', font=('Arial', 12, 'bold'))

    def on_key_press(self, event):
        key = event.keysym
        if key in ('Up', 'Down', 'Left', 'Right'):
            opposite = {'Up':'Down', 'Down':'Up', 'Left':'Right', 'Right':'Left'}
            if key != opposite.get(self.direction):
                self.direction = key

    def update(self):
        if not self.running:
            return

        head_x, head_y = self.snake[0]
        if self.direction == 'Up':
            head_y -= 1
        elif self.direction == 'Down':
            head_y += 1
        elif self.direction == 'Left':
            head_x -= 1
        elif self.direction == 'Right':
            head_x += 1

        new_head = (head_x, head_y)

        if (head_x < 0 or head_x >= GRID_WIDTH or
            head_y < 0 or head_y >= GRID_HEIGHT or
            new_head in self.snake):
            self.game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.place_food()
        else:
            self.snake.pop()

        self.draw()
        self.root.after(UPDATE_DELAY, self.update)

    def game_over(self):
        self.running = False
        self.canvas.create_text(self.width // 2, self.height // 2 - 20,
                                text='Game Over', fill='white', font=('Arial', 24, 'bold'))
        self.canvas.create_text(self.width // 2, self.height // 2 + 20,
                                text=f'Final Score: {self.score}', fill='white', font=('Arial', 16))
        self.canvas.create_text(self.width // 2, self.height // 2 + 50,
                                text='Press R to retry', fill='white', font=('Arial', 12))
        self.root.bind('<Key-r>', self.on_retry)

    def on_retry(self, event):
        self.reset_game()
        self.running = True
        self.root.bind('<Key>', self.on_key_press)
        self.update()

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Snake Game')
    game = SnakeGame(root)
    root.mainloop()
