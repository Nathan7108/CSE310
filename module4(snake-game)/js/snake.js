class Snake {
    constructor() {
        this.body = [
            { x: 3, y: 10 },
            { x: 2, y: 10 },
            { x: 1, y: 10 },
            { x: 0, y: 10 }
        ];
        this.direction = { x: 1, y: 0 };
        this.nextDirection = { x: 1, y: 0 };
        this.shouldGrow = false;
    }

    move() {
        this.direction = { ...this.nextDirection };
        const head = {
            x: this.body[0].x + this.direction.x,
            y: this.body[0].y + this.direction.y
        };
        this.body.unshift(head);
        
        if (!this.shouldGrow) {
            this.body.pop();
        } else {
            this.shouldGrow = false;
        }
    }

    grow() {
        this.shouldGrow = true;
    }

    checkCollision(gridSize) {
        const head = this.body[0];
        
        if (head.x < 0 || head.x >= gridSize || head.y < 0 || head.y >= gridSize) {
            return true;
        }
        
        for (let i = 1; i < this.body.length; i++) {
            if (head.x === this.body[i].x && head.y === this.body[i].y) {
                return true;
            }
        }
        
        return false;
    }

    setDirection(newDirection) {
        if (this.direction.x === -newDirection.x && this.direction.y === -newDirection.y) {
            return;
        }
        this.nextDirection = newDirection;
    }

    getHead() {
        return this.body[0];
    }

    getBody() {
        return this.body;
    }
}

