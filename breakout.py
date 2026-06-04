import tkinter as tk
import random
import time
import math

WIDTH = 800
HEIGHT = 600
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 12
BALL_RADIUS = 8
BRICK_ROWS = 6
BRICK_COLS = 10
BRICK_WIDTH = (WIDTH - 40) // BRICK_COLS
BRICK_HEIGHT = 20
BRICK_PADDING = 4


class BreakoutGame:
    def __init__(self, master):
        self.master = master
        master.title("Breakout - tkinter")

        self.canvas = tk.Canvas(master, width=WIDTH, height=HEIGHT, bg="#111")
        self.canvas.pack()

        # 공 기본 속도 (사용자가 조절 가능)
        self.ball_speed = 5.0

        # 파워업/아이템 설정
        self.items = []  # 떨어지는 아이템
        self.active_powerups = {}  # {name: expiry_time}
        self.ITEM_FALL_SPEED = 3
        self.ITEM_CHANCE = 0.25

        self.reset_game_state()

        # Bind controls
        master.bind("<Left>", lambda e: self.move_paddle(-1))
        master.bind("<Right>", lambda e: self.move_paddle(1))
        master.bind("<space>", lambda e: self.start_game())
        master.bind("<Up>", lambda e: self.change_speed(0.5))
        master.bind("<Down>", lambda e: self.change_speed(-0.5))
        self.canvas.bind("<Motion>", self.on_mouse_move)

        # 초기 루프 상태
        self.running = False
        self._loop()

    def reset_game_state(self):
        self.score = 0
        self.lives = 3
        self.create_bricks()

        # Paddle center
        self.paddle_x = WIDTH // 2

        # Balls: support 다중 공
        self.balls = []
        self.spawn_ball(center=True)

        # 아이템 목록 초기화
        self.items = []

        self.game_over = False

    def create_bricks(self):
        self.bricks = []
        top_offset = 40
        for row in range(BRICK_ROWS):
            brick_row = []
            for col in range(BRICK_COLS):
                x1 = 20 + col * BRICK_WIDTH + BRICK_PADDING // 2
                y1 = top_offset + row * (BRICK_HEIGHT + BRICK_PADDING)
                x2 = x1 + BRICK_WIDTH - BRICK_PADDING
                y2 = y1 + BRICK_HEIGHT
                color = ["#f44336", "#ff9800", "#ffeb3b", "#4caf50", "#2196f3", "#9c27b0"][row % 6]
                brick_row.append(((x1, y1, x2, y2), color))
            self.bricks.append(brick_row)

    def move_paddle(self, direction):
        # direction -1 left, 1 right
        self.paddle_x += direction * 40
        self.paddle_x = max(PADDLE_WIDTH // 2, min(WIDTH - PADDLE_WIDTH // 2, self.paddle_x))

    def on_mouse_move(self, event):
        self.paddle_x = event.x

    def start_game(self):
        if not self.running and not self.game_over:
            self.running = True
        elif self.game_over:
            self.reset_game_state()
            self.running = True

    def _loop(self):
        if self.running and not self.game_over:
            self.update()
        self.draw()
        self.master.after(16, self._loop)

    def update(self):
        # Move balls
        for ball in list(self.balls):
            ball['x'] += ball['vx']
            ball['y'] += ball['vy']

            # Wall collisions
            if ball['x'] - ball['radius'] <= 0:
                ball['x'] = ball['radius']
                ball['vx'] = -ball['vx']
            if ball['x'] + ball['radius'] >= WIDTH:
                ball['x'] = WIDTH - ball['radius']
                ball['vx'] = -ball['vx']
            if ball['y'] - ball['radius'] <= 0:
                ball['y'] = ball['radius']
                ball['vy'] = -ball['vy']

            # Paddle collision
            paddle_top = HEIGHT - 40
            paddle_left = self.paddle_x - PADDLE_WIDTH // 2
            paddle_right = self.paddle_x + PADDLE_WIDTH // 2
            paddle_bottom = paddle_top + PADDLE_HEIGHT

            if (paddle_left - ball['radius'] <= ball['x'] <= paddle_right + ball['radius'] and
                    paddle_top - ball['radius'] <= ball['y'] <= paddle_bottom + ball['radius'] and
                    ball['vy'] > 0):
                offset = (ball['x'] - self.paddle_x) / (PADDLE_WIDTH / 2)
                ball['vx'] += offset * 2
                max_speed = 12
                ball['vx'] = max(-max_speed, min(max_speed, ball['vx']))
                ball['vy'] = -abs(ball['vy'])

            # Brick collisions
            for r, row in enumerate(self.bricks):
                hit = False
                for c, brick in enumerate(row):
                    if brick is None:
                        continue
                    (x1, y1, x2, y2), color = brick
                    if x1 - ball['radius'] <= ball['x'] <= x2 + ball['radius'] and y1 - ball['radius'] <= ball['y'] <= y2 + ball['radius']:
                        # remove brick
                        self.bricks[r][c] = None
                        self.score += 10
                        # spawn item with chance
                        if random.random() < self.ITEM_CHANCE:
                            self.spawn_item((x1 + x2) / 2, (y1 + y2) / 2)

                        # if ball has piercing powerup, do not reflect
                        if not self.active_powerups.get('pierce', False) and not ball.get('pierce', False):
                            # determine side of collision
                            if x1 < ball['x'] < x2:
                                ball['vy'] = -ball['vy']
                            else:
                                ball['vx'] = -ball['vx']
                        hit = True
                        break
                if hit:
                    break

            # Bottom (ball lost)
            if ball['y'] - ball['radius'] > HEIGHT:
                try:
                    self.balls.remove(ball)
                except ValueError:
                    pass

        # If no balls remain, lose a life and respawn
        if len(self.balls) == 0:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self.running = False
            else:
                self.paddle_x = WIDTH // 2
                self.spawn_ball(center=True)
                self.running = False

        # Update items falling and collisions with paddle
        for item in list(self.items):
            item['y'] += self.ITEM_FALL_SPEED
            # check paddle collision
            paddle_top = HEIGHT - 40
            paddle_left = self.paddle_x - PADDLE_WIDTH // 2
            paddle_right = self.paddle_x + PADDLE_WIDTH // 2
            if paddle_left <= item['x'] <= paddle_right and paddle_top <= item['y'] <= paddle_top + PADDLE_HEIGHT:
                self.activate_powerup(item['type'])
                try:
                    self.items.remove(item)
                except ValueError:
                    pass

        # Deactivate expired powerups
        self.deactivate_powerups()

        # Win check
        if all(b is None for row in self.bricks for b in row):
            self.game_over = True
            self.running = False

    def change_speed(self, delta):
        old = getattr(self, "ball_speed", 5.0)
        new = max(1.0, min(15.0, old + delta))
        if new == old:
            return
        factor = new / old
        self.ball_speed = new
        # 속도 비율로 현재 공 속도 조정
        if hasattr(self, 'ball_vx') and hasattr(self, 'ball_vy'):
            # adjust all balls
            for b in self.balls:
                b['vx'] *= factor
                b['vy'] *= factor

    # --- 아이템/파워업 관련 ---
    def spawn_item(self, x, y):
        types = ['pierce', 'multi', 'expand']
        t = random.choice(types)
        self.items.append({'x': x, 'y': y, 'type': t})

    def activate_powerup(self, name):
        now = time.time()
        if name == 'pierce':
            self.active_powerups['pierce'] = now + 10.0
        elif name == 'multi':
            # split each existing ball into 3
            new_balls = []
            for b in list(self.balls):
                new_balls.extend(self.split_ball(b, 3))
            self.balls = new_balls
        elif name == 'expand':
            # expand paddle temporarily
            self.active_powerups['expand'] = now + 12.0
            global PADDLE_WIDTH
            PADDLE_WIDTH = min(200, PADDLE_WIDTH * 2)

    def spawn_ball(self, center=False):
        # create a new ball and append to self.balls
        if center:
            x = WIDTH // 2
            y = HEIGHT - 60
        else:
            x = self.paddle_x
            y = HEIGHT - 60
        speed = self.ball_speed
        vx = speed * random.choice([-1, 1]) * abs(random.uniform(0.4, 0.8))
        vy = -speed * abs(random.uniform(0.6, 1.0))
        shape = random.choice(['circle', 'square', 'triangle'])
        self.balls.append({'x': x, 'y': y, 'vx': vx, 'vy': vy, 'radius': BALL_RADIUS, 'shape': shape})

    def deactivate_powerups(self):
        now = time.time()
        to_remove = []
        for name, expiry in list(self.active_powerups.items()):
            if now >= expiry:
                to_remove.append(name)
        for name in to_remove:
            if name == 'expand':
                # reset paddle width to default
                global PADDLE_WIDTH
                PADDLE_WIDTH = 100
            del self.active_powerups[name]

    def split_ball(self, ball, count):
        res = []
        base_speed = math.hypot(ball['vx'], ball['vy']) or self.ball_speed
        angle0 = math.atan2(ball['vy'], ball['vx'])
        spread = 0.6
        for i in range(count):
            ang = angle0 + (i - (count - 1) / 2) * spread
            vx = base_speed * math.cos(ang)
            vy = base_speed * math.sin(ang)
            shape = random.choice(['circle', 'square', 'triangle', 'star'])
            res.append({'x': ball['x'], 'y': ball['y'], 'vx': vx, 'vy': vy, 'radius': BALL_RADIUS, 'shape': shape})
        return res

    def draw(self):
        self.canvas.delete("all")

        # Draw bricks
        for row in self.bricks:
            for brick in row:
                if brick is None:
                    continue
                (x1, y1, x2, y2), color = brick
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, width=0)

        # Draw paddle
        paddle_top = HEIGHT - 40
        x1 = self.paddle_x - PADDLE_WIDTH // 2
        y1 = paddle_top
        x2 = self.paddle_x + PADDLE_WIDTH // 2
        y2 = paddle_top + PADDLE_HEIGHT
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#ddd", outline="")

        # Draw items
        for item in self.items:
            col = {'pierce': '#ff0', 'multi': '#0f0', 'expand': '#0ff'}.get(item['type'], '#fff')
            self.canvas.create_oval(item['x'] - 8, item['y'] - 8, item['x'] + 8, item['y'] + 8, fill=col, outline='')
            self.canvas.create_text(item['x'], item['y'], text=item['type'][0].upper(), fill='#000', font=("Arial", 8))

        # Draw balls (다양한 모양)
        for b in self.balls:
            shape = b.get('shape', 'circle')
            r = b.get('radius', BALL_RADIUS)
            if shape == 'circle':
                self.canvas.create_oval(b['x'] - r, b['y'] - r, b['x'] + r, b['y'] + r, fill="#fff", outline="")
            elif shape == 'square':
                self.canvas.create_rectangle(b['x'] - r, b['y'] - r, b['x'] + r, b['y'] + r, fill="#fff", outline="")
            elif shape == 'triangle':
                points = [b['x'], b['y'] - r, b['x'] - r, b['y'] + r, b['x'] + r, b['y'] + r]
                self.canvas.create_polygon(points, fill="#fff", outline="")
            else:
                # star-like: draw circle with small spikes
                self.canvas.create_oval(b['x'] - r, b['y'] - r, b['x'] + r, b['y'] + r, fill="#fff", outline="")

        # Draw HUD with active powerups and speed
        hud = f"점수: {self.score}  목숨: {self.lives}  속도: {self.ball_speed:.1f}"
        self.canvas.create_text(10, 10, anchor="nw", fill="#fff", font=("Arial", 14), text=hud)

        # Active powerups
        if self.active_powerups:
            lines = []
            now = time.time()
            for name, expiry in self.active_powerups.items():
                remain = max(0, int(expiry - now))
                lines.append(f"{name}:{remain}s")
            self.canvas.create_text(10, 34, anchor="nw", fill="#fff", font=("Arial", 12), text=" ".join(lines))

        if not self.running and not self.game_over:
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2, fill="#fff", font=("Arial", 18), text="스페이스로 시작하세요")

        if self.game_over:
            msg = "모두 클리어!" if all(b is None for row in self.bricks for b in row) and self.lives > 0 else "게임 오버"
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 20, fill="#fff", font=("Arial", 28), text=msg)
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 20, fill="#fff", font=("Arial", 14), text="스페이스로 재시작")


def main():
    root = tk.Tk()
    game = BreakoutGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
