const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const gridSize = 20;
const cellSize = canvas.width / gridSize;

let snake = new Snake();
let food = { x: 13, y: 10 };
let score = 0;
let highScore = localStorage.getItem('snakeHighScore') || 0;
let gameRunning = false;
let gamePaused = false;
let aiMode = false;
let gameSpeed = 150;
let lastTime = 0;
let animationFrame;

const scoreElement = document.getElementById('score');
const highScoreElement = document.getElementById('highScore');
const pauseBtn = document.getElementById('pauseBtn');
const restartBtn = document.getElementById('restartBtn');
const aiBtn = document.getElementById('aiBtn');
const difficultySelect = document.getElementById('difficulty');
const startModal = document.getElementById('startModal');
const gameOverModal = document.getElementById('gameOverModal');
const finalScoreElement = document.getElementById('finalScore');
const playAgainBtn = document.getElementById('playAgainBtn');
const menuBtn = document.getElementById('menuBtn');

let waitingForStart = true;

highScoreElement.textContent = highScore;

function playSound(freq, dur, type = 'sine') {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    
    osc.connect(gain);
    gain.connect(ctx.destination);
    
    osc.frequency.value = freq;
    osc.type = type;
    gain.gain.setValueAtTime(0.3, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + dur);
    
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + dur);
}

function playEatSound() {
    playSound(800, 0.1, 'sine');
    setTimeout(() => playSound(1000, 0.1, 'sine'), 50);
}

function playGameOverSound() {
    playSound(200, 0.2, 'sawtooth');
    setTimeout(() => playSound(150, 0.3, 'sawtooth'), 200);
}

function playStartSound() {
    playSound(600, 0.15, 'sine');
    setTimeout(() => playSound(800, 0.15, 'sine'), 100);
}

function getDifficultySpeed() {
    const difficulty = difficultySelect.value;
    if (difficulty === 'easy') return 200;
    if (difficulty === 'medium') return 150;
    return 100;
}

function generateFood(isInitial = false) {
    if (isInitial) {
        const head = snake.getHead();
        food = {
            x: Math.min(head.x + 10, gridSize - 1),
            y: head.y
        };
    } else {
        let newFood;
        do {
            newFood = {
                x: Math.floor(Math.random() * gridSize),
                y: Math.floor(Math.random() * gridSize)
            };
        } while (isSnakeBody(newFood));
        food = newFood;
    }
}

function isSnakeBody(pos) {
    return snake.getBody().some(segment => segment.x === pos.x && segment.y === pos.y);
}

function drawGrid() {
    for (let x = 0; x < gridSize; x++) {
        for (let y = 0; y < gridSize; y++) {
            if ((x + y) % 2 === 0) {
                ctx.fillStyle = '#e0f2fe';
            } else {
                ctx.fillStyle = '#f0f9ff';
            }
            ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
        }
    }
    
    ctx.strokeStyle = '#cfe2ff';
    ctx.lineWidth = 1;
    for (let i = 0; i <= gridSize; i++) {
        ctx.beginPath();
        ctx.moveTo(i * cellSize, 0);
        ctx.lineTo(i * cellSize, canvas.height);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(0, i * cellSize);
        ctx.lineTo(canvas.width, i * cellSize);
        ctx.stroke();
    }
}

function draw() {
    ctx.fillStyle = '#f0f9ff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    drawGrid();

    snake.getBody().forEach((segment, index) => {
        const x = segment.x * cellSize + 1.5;
        const y = segment.y * cellSize + 1.5;
        const size = cellSize - 3;
        const radius = 8;
        
        if (index === 0) {
            ctx.fillStyle = '#4299e1';
        } else {
            ctx.fillStyle = '#3182ce';
        }
        
        ctx.beginPath();
        ctx.moveTo(x + radius, y);
        ctx.lineTo(x + size - radius, y);
        ctx.quadraticCurveTo(x + size, y, x + size, y + radius);
        ctx.lineTo(x + size, y + size - radius);
        ctx.quadraticCurveTo(x + size, y + size, x + size - radius, y + size);
        ctx.lineTo(x + radius, y + size);
        ctx.quadraticCurveTo(x, y + size, x, y + size - radius);
        ctx.lineTo(x, y + radius);
        ctx.quadraticCurveTo(x, y, x + radius, y);
        ctx.closePath();
        ctx.fill();
        
        if (index === 0) {
            let eyeX1, eyeX2, eyeY1, eyeY2, pupilX1, pupilX2, pupilY1, pupilY2;
            const dir = snake.direction;
            
            if (dir.x === 1) {
                eyeX1 = eyeX2 = x + size - 8;
                eyeY1 = y + 6;
                eyeY2 = y + size - 6;
                pupilX1 = pupilX2 = eyeX1 + 1;
                pupilY1 = eyeY1;
                pupilY2 = eyeY2;
            } else if (dir.x === -1) {
                eyeX1 = eyeX2 = x + 8;
                eyeY1 = y + 6;
                eyeY2 = y + size - 6;
                pupilX1 = pupilX2 = eyeX1 - 1;
                pupilY1 = eyeY1;
                pupilY2 = eyeY2;
            } else if (dir.y === -1) {
                eyeX1 = x + 6;
                eyeX2 = x + size - 6;
                eyeY1 = eyeY2 = y + 8;
                pupilX1 = eyeX1;
                pupilX2 = eyeX2;
                pupilY1 = pupilY2 = eyeY1 - 1;
            } else {
                eyeX1 = x + 6;
                eyeX2 = x + size - 6;
                eyeY1 = eyeY2 = y + size - 8;
                pupilX1 = eyeX1;
                pupilX2 = eyeX2;
                pupilY1 = pupilY2 = eyeY1 + 1;
            }
            
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(eyeX1, eyeY1, 3, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(eyeX2, eyeY2, 3, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = 'black';
            ctx.beginPath();
            ctx.arc(pupilX1, pupilY1, 1.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(pupilX2, pupilY2, 1.5, 0, Math.PI * 2);
            ctx.fill();
        }
    });

    const foodX = food.x * cellSize + cellSize / 2;
    const foodY = food.y * cellSize + cellSize / 2;
    const foodRadius = cellSize / 2 - 3;
    
    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.arc(foodX, foodY, foodRadius, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.fillStyle = '#dc2626';
    ctx.beginPath();
    ctx.arc(foodX - 3, foodY - 3, 2, 0, Math.PI * 2);
    ctx.fill();
    
    ctx.strokeStyle = '#22c55e';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(foodX, foodY - foodRadius);
    ctx.lineTo(foodX, foodY - foodRadius - 4);
    ctx.stroke();
    
    ctx.fillStyle = '#22c55e';
    ctx.beginPath();
    ctx.arc(foodX, foodY - foodRadius - 4, 2, 0, Math.PI * 2);
    ctx.fill();
}

function update() {
    if (gamePaused) return;

    if (aiMode) {
        const ai = new AI(snake, food, gridSize);
        const aiDirection = ai.getNextDirection();
        snake.setDirection(aiDirection);
    }

    snake.move();

    if (snake.checkCollision(gridSize)) {
        gameOver();
        return;
    }

    const head = snake.getHead();
    if (head.x === food.x && head.y === food.y) {
        snake.grow();
        score++;
        scoreElement.textContent = score;
        playEatSound();
        if (score > highScore) {
            highScore = score;
            highScoreElement.textContent = highScore;
            localStorage.setItem('snakeHighScore', highScore);
        }
        generateFood();
    }
}

function gameLoopFunction(currentTime) {
    if (!gameRunning) return;
    
    if (currentTime - lastTime >= gameSpeed) {
        update();
        lastTime = currentTime;
    }
    
    draw();
    animationFrame = requestAnimationFrame(gameLoopFunction);
}

function showStartModal() {
    if (gameRunning) return;
    
    snake = new Snake();
    generateFood(true);
    score = 0;
    scoreElement.textContent = score;
    draw();
    
    startModal.classList.remove('hidden');
    waitingForStart = true;
}

function actuallyStartGame(direction) {
    if (gameRunning) return;
    
    if (!waitingForStart) {
        snake = new Snake();
        generateFood(true);
        score = 0;
        scoreElement.textContent = score;
        draw();
    }
    
    snake.setDirection(direction);
    startModal.classList.add('hidden');
    waitingForStart = false;
    gameRunning = true;
    gamePaused = false;
    gameSpeed = getDifficultySpeed();
    lastTime = performance.now();
    
    playStartSound();
    
    cancelAnimationFrame(animationFrame);
    animationFrame = requestAnimationFrame(gameLoopFunction);
    
    pauseBtn.disabled = false;
}

function pauseGame() {
    if (!gameRunning) return;
    
    gamePaused = !gamePaused;
    
    if (gamePaused) {
        cancelAnimationFrame(animationFrame);
        pauseBtn.textContent = 'Resume';
    } else {
        lastTime = performance.now();
        animationFrame = requestAnimationFrame(gameLoopFunction);
        pauseBtn.textContent = 'Pause';
    }
}

function restartGame() {
    cancelAnimationFrame(animationFrame);
    gameRunning = false;
    gamePaused = false;
    waitingForStart = true;
    aiMode = false;
    aiBtn.textContent = 'AI Mode';
    pauseBtn.textContent = 'Pause';
    pauseBtn.disabled = true;
    gameOverModal.classList.add('hidden');
    
    snake = new Snake();
    generateFood(true);
    score = 0;
    scoreElement.textContent = score;
    draw();
    
    startModal.classList.remove('hidden');
}

function gameOver() {
    cancelAnimationFrame(animationFrame);
    gameRunning = false;
    gamePaused = false;
    waitingForStart = false;
    pauseBtn.disabled = true;
    
    playGameOverSound();
    
    finalScoreElement.textContent = score;
    gameOverModal.classList.remove('hidden');
}

function toggleAI() {
    if (!gameRunning) {
        snake = new Snake();
        generateFood(true);
        score = 0;
        scoreElement.textContent = score;
        draw();
        
        aiMode = true;
        gameRunning = true;
        gamePaused = false;
        gameSpeed = getDifficultySpeed();
        lastTime = performance.now();
        
        startModal.classList.add('hidden');
        waitingForStart = false;
        
        playStartSound();
        
        cancelAnimationFrame(animationFrame);
        animationFrame = requestAnimationFrame(gameLoopFunction);
        
        pauseBtn.disabled = false;
        aiBtn.textContent = 'Manual Mode';
    } else {
        aiMode = !aiMode;
        aiBtn.textContent = aiMode ? 'Manual Mode' : 'AI Mode';
    }
}

pauseBtn.addEventListener('click', pauseGame);
restartBtn.addEventListener('click', restartGame);
aiBtn.addEventListener('click', toggleAI);

playAgainBtn.addEventListener('click', () => {
    gameOverModal.classList.add('hidden');
    showStartModal();
});

menuBtn.addEventListener('click', () => {
    gameOverModal.classList.add('hidden');
    pauseBtn.disabled = true;
    gameRunning = false;
    gamePaused = false;
    waitingForStart = true;
    aiMode = false;
    aiBtn.textContent = 'AI Mode';
    
    snake = new Snake();
    generateFood(true);
    score = 0;
    scoreElement.textContent = score;
    draw();
    
    startModal.classList.remove('hidden');
});

difficultySelect.addEventListener('change', () => {
    if (gameRunning && !gamePaused) {
        gameSpeed = getDifficultySpeed();
    }
});

function getDirectionFromKey(key) {
    if (key === 'ArrowUp') return { x: 0, y: -1 };
    if (key === 'ArrowDown') return { x: 0, y: 1 };
    if (key === 'ArrowLeft') return { x: -1, y: 0 };
    if (key === 'ArrowRight') return { x: 1, y: 0 };
    return null;
}

document.addEventListener('keydown', (e) => {
    const dir = getDirectionFromKey(e.key);
    
    if (dir && (!gameRunning || waitingForStart)) {
        e.preventDefault();
        actuallyStartGame(dir);
        return;
    }
    
    if (gamePaused || aiMode) return;
    
    if (dir) {
        snake.setDirection(dir);
    } else if (e.key === ' ') {
        e.preventDefault();
        pauseGame();
    }
});

generateFood(true);
draw();

