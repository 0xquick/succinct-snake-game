import random
import time
from flask import Flask, jsonify, request

# Game Constants
WIDTH, HEIGHT = 20, 20  # Grid size in cells
TICK_RATE = 0.2  # 200ms per tick (same as time.sleep(0.2) in old code)

# Game State
game_started = False
game_over = False
score = 0
high_score = 0
direction = (1, 0)
last_move_time = time.time()  # Track the last move time

def reset_game():
    global snake, direction, food, game_over, game_started, score, last_move_time
    snake = [(5, 5), (4, 5), (3, 5)]  # Start with length of 3
    direction = (1, 0)
    food = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
    game_over = False
    game_started = False
    score = 0
    last_move_time = time.time()  # Reset movement timer

reset_game()

def move_snake():
    """ Moves the snake forward if enough time has passed (every TICK_RATE seconds) """
    global food, game_over, snake, game_started, score, high_score, last_move_time
    
    if not game_started or game_over:
        return

    if time.time() - last_move_time < TICK_RATE:  # ✅ Only move every TICK_RATE seconds
        return
    last_move_time = time.time()  # ✅ Update last move time

    # Compute new head position
    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    # Collision Detection
    if head in snake or head[0] < 0 or head[1] < 0 or head[0] >= WIDTH or head[1] >= HEIGHT:
        game_over = True
        if score > high_score:
            high_score = score
        return

    snake.insert(0, head)  # Move forward

    if head == food:
        food = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))  # Generate new food
        score += 1
    else:
        snake.pop()  # Remove tail

# Flask Web Server
app = Flask(__name__)

@app.route('/game_state')
def game_state():
    """ Moves snake and returns game state. """
    move_snake()  # ✅ Moves the snake only when the frontend requests it
    return jsonify({
        "snake": snake,
        "food": food,
        "game_over": game_over,
        "game_started": game_started,
        "score": score,
        "high_score": high_score
    })

@app.route('/start_game')
def start_game():
    """ Resets the game and starts playing. """
    global game_started, game_over
    reset_game()
    game_started = True
    return "Game Started"

@app.route('/change_direction')
def change_direction():
    """ Handles direction change from frontend. """
    global direction
    key = request.args.get("key")
    if key == "ArrowUp" and direction != (0, 1):
        direction = (0, -1)
    elif key == "ArrowDown" and direction != (0, -1):
        direction = (0, 1)
    elif key == "ArrowLeft" and direction != (1, 0):
        direction = (-1, 0)
    elif key == "ArrowRight" and direction != (-1, 0):
        direction = (1, 0)
    return "OK"

@app.route('/')
def serve_game():
    """ Serves the frontend game page. """
    return open("arcade_snake.html").read()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
