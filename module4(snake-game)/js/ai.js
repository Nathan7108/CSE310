class AI {
    constructor(snake, food, gridSize) {
        this.snake = snake;
        this.food = food;
        this.gridSize = gridSize;
    }

    getNextDirection() {
        const head = this.snake.getHead();
        const dx = this.food.x - head.x;
        const dy = this.food.y - head.y;

        let dir = { x: 0, y: 0 };
        if (Math.abs(dx) > Math.abs(dy)) {
            dir.x = dx > 0 ? 1 : -1;
        } else {
            dir.y = dy > 0 ? 1 : -1;
        }

        const test = new Snake();
        test.body = JSON.parse(JSON.stringify(this.snake.getBody()));
        test.direction = dir;
        test.nextDirection = dir;
        test.move();

        if (!this.wouldCollide(test)) {
            return dir;
        }

        const options = [
            { x: 1, y: 0 },
            { x: -1, y: 0 },
            { x: 0, y: 1 },
            { x: 0, y: -1 }
        ];

        for (let opt of options) {
            if (opt.x === -this.snake.direction.x && opt.y === -this.snake.direction.y) {
                continue;
            }
            
            test.body = JSON.parse(JSON.stringify(this.snake.getBody()));
            test.direction = opt;
            test.nextDirection = opt;
            test.move();
            
            if (!this.wouldCollide(test)) {
                return opt;
            }
        }

        return this.snake.direction;
    }

    wouldCollide(snake) {
        const head = snake.getHead();
        
        if (head.x < 0 || head.x >= this.gridSize || head.y < 0 || head.y >= this.gridSize) {
            return true;
        }
        
        const body = snake.getBody();
        for (let i = 1; i < body.length; i++) {
            if (head.x === body[i].x && head.y === body[i].y) {
                return true;
            }
        }
        
        return false;
    }
}

