import random
import threading
import time
from flask import Flask, jsonify, request

# Game Constants
WIDTH, HEIGHT = 20, 20  # Grid size in cells

# Game State
game_started = False
game_over = False
score = 0
high_score = 0
direction = (1, 0)
game_loop_started = False  # ✅ Ensure only one game loop starts

# Initialize Game
def reset_game():
    global snake, direction, food, game_over, game_started, score
    snake = [(5, 5), (4, 5), (3, 5)]  # Start with a length of 3
    direction = (1, 0)
    food = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
    game_over = False
    game_started = False
    score = 0

reset_game()

# Snake Movement Logic
def move_snake():
    global food, game_over, snake, game_started, score, high_score
    if not game_started or game_over:
        return

    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    # Collision Detection
    if head in snake or head[0] < 0 or head[1] < 0 or head[0] >= WIDTH or head[1] >= HEIGHT:
        game_over = True
        if score > high_score:
            high_score = score
        return

    snake.insert(0, head)  # Move forward

    if head == food:
        food = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))  # New food
        score += 1
    else:
        snake.pop()  # Remove tail

# **Fix: Background Game Loop**
def game_loop():
    """ Runs the snake movement in the background every 0.2s. """
    while True:
        if game_started and not game_over:
            move_snake()
        time.sleep(0.2)  # Controls game speed

# Flask Web Server
app = Flask(__name__)

@app.before_request
def start_game_thread():
    """ ✅ Ensures the game loop starts only once in production. """
    global game_loop_started
    if not game_loop_started:
        game_thread = threading.Thread(target=game_loop, daemon=True)
        game_thread.start()
        game_loop_started = True  # Prevents multiple threads

@app.route('/game_state')
def game_state():
    """ Returns the current game state for the frontend. """
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
    app.run(host="0.0.0.0", port=10000)
