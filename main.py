import random
import webbrowser
from flask import Flask, jsonify, request
import threading
import time

# Game Constants
WIDTH, HEIGHT = 20, 20  # Grid size in cells
GRID_SIZE = 1

# Score Tracking
game_started = False
score = 0
high_score = 0

def reset_game():
    global snake, direction, food, game_over, game_started, score
    snake = [(5, 5), (4, 5)]  # Start with a length of 2
    direction = (1, 0)
    food = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
    game_over = False
    game_started = False
    score = 0

# Initialize game state
reset_game()

def move_snake():
    global food, game_over, snake, game_started, score, high_score
    if not game_started or game_over:
        return
    
    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    
    if head in snake or head[0] < 0 or head[1] < 0 or head[0] >= WIDTH or head[1] >= HEIGHT:
        game_over = True
        if score > high_score:
            high_score = score
        return
    
    snake.insert(0, head)
    if head == food:
        food = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
        score += 1
    else:
        snake.pop()

def game_loop():
    global direction, game_over, game_started
    while True:
        if game_started and not game_over:
            move_snake()
        time.sleep(0.2)  # Control game speed

# Flask Web Server
app = Flask(__name__, static_folder="static")

@app.route('/game_state')
def game_state():
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
    global game_started, game_over
    reset_game()
    game_started = True
    return "Game Started"

@app.route('/')
def serve_game():
    return '''
    <html>
    <head>
        <style>
            body { display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column; background: url('/static/image.png') no-repeat center center fixed; background-size: cover; color: white; overflow: hidden; }
            #gameCanvas { border: 3px solid white; display: none; }
            #popup { display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: black; color: white; padding: 20px; text-align: center; border-radius: 10px; }
        </style>
        <script>
            document.addEventListener("keydown", function(event) {
                if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) {
                    event.preventDefault(); // Prevents page scrolling
                }
                fetch("/change_direction?key=" + event.key);
            });
            
            async function checkStart() {
                let response = await fetch('/game_state');
                let data = await response.json();
                if (!data.game_started) {
                    document.getElementById("startScreen").style.display = "block";
                    document.getElementById("gameCanvas").style.display = "none";
                } else {
                    document.getElementById("startScreen").style.display = "none";
                    document.getElementById("gameCanvas").style.display = "block";
                }
            }
            
            async function startGame() {
                await fetch('/start_game');
                document.getElementById("popup").style.display = "none";
                checkStart();
            }
            
            async function updateGame() {
                let response = await fetch('/game_state');
                let data = await response.json();
                let canvas = document.getElementById("gameCanvas");
                let ctx = canvas.getContext("2d");
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                ctx.fillStyle = "white";
                ctx.fillRect(data.food[0] * 20, data.food[1] * 20, 20, 20);
                
                ctx.fillStyle = "black";
                for (let part of data.snake) {
                    ctx.fillRect(part[0] * 20, part[1] * 20, 20, 20);
                }
                
                ctx.fillStyle = "white";
                ctx.font = "20px Arial";
                ctx.fillText("Score: " + data.score, 10, 20);
                ctx.fillText("High Score: " + data.high_score, 10, 40);
                
                if (data.game_over) {
                    document.getElementById("popup").style.display = "block";
                    document.getElementById("popupScore").innerText = data.score;
                    document.getElementById("popupHighScore").innerText = data.high_score;
                }
            }
            setInterval(updateGame, 200);
            setInterval(checkStart, 500);
        </script>
    </head>
    <body>
        <div id="startScreen" style="display: block; text-align: center;">
            <h1>Press Enter to Start the Game</h1>
            <button onclick="startGame()">Start Game</button>
        </div>
        <canvas id="gameCanvas" width="400" height="400"></canvas>
        <div id="popup">
            <h1>Game Over!</h1>
            <p>Score: <span id="popupScore">0</span></p>
            <p>High Score: <span id="popupHighScore">0</span></p>
            <button onclick="startGame()">Press Enter to Play Again</button>
        </div>
    </body>
    </html>
    '''

@app.route('/change_direction')
def change_direction():
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

if __name__ == '__main__':
    game_thread = threading.Thread(target=game_loop, daemon=True)
    game_thread.start()
    app.run(host="0.0.0.0", port=10000)
