const canvas = document.getElementById('drawingCanvas') as HTMLCanvasElement;
const ctx = canvas.getContext('2d')!;
const colorPicker = document.getElementById('colorPicker') as HTMLInputElement;
const brushSize = document.getElementById('brushSize') as HTMLInputElement;
const brushSizeValue = document.getElementById('brushSizeValue') as HTMLSpanElement;
const clearBtn = document.getElementById('clearBtn') as HTMLButtonElement;
const undoBtn = document.getElementById('undoBtn') as HTMLButtonElement;
const saveBtn = document.getElementById('saveBtn') as HTMLButtonElement;

let isDrawing = false;
let currentColor = '#000000';
let currentBrushSize = 5;
let drawHistory: ImageData[] = [];

ctx.lineCap = 'round';
ctx.lineJoin = 'round';
ctx.strokeStyle = currentColor;
ctx.lineWidth = currentBrushSize;

function saveState() {
    drawHistory.push(ctx.getImageData(0, 0, canvas.width, canvas.height));
    if (drawHistory.length > 20) {
        drawHistory.shift();
    }
}

function startDrawing(e: MouseEvent | TouchEvent | PointerEvent) {
    isDrawing = true;
    saveState();
    const point = getPoint(e);
    ctx.beginPath();
    ctx.moveTo(point.x, point.y);
}

function draw(e: MouseEvent | TouchEvent | PointerEvent) {
    if (!isDrawing) return;
    
    e.preventDefault();
    const point = getPoint(e);
    ctx.lineTo(point.x, point.y);
    ctx.stroke();
}

function stopDrawing() {
    if (isDrawing) {
        isDrawing = false;
    }
}

function getPoint(e: MouseEvent | TouchEvent | PointerEvent): { x: number; y: number } {
    const rect = canvas.getBoundingClientRect();
    if (e instanceof TouchEvent && e.touches.length > 0) {
        return {
            x: e.touches[0].clientX - rect.left,
            y: e.touches[0].clientY - rect.top
        };
    }
    if (e instanceof PointerEvent || e instanceof MouseEvent) {
        return {
            x: (e as MouseEvent).clientX - rect.left,
            y: (e as MouseEvent).clientY - rect.top
        };
    }
    return { x: 0, y: 0 };
}

colorPicker.addEventListener('input', (e) => {
    currentColor = (e.target as HTMLInputElement).value;
    ctx.strokeStyle = currentColor;
});

brushSize.addEventListener('input', (e) => {
    currentBrushSize = parseInt((e.target as HTMLInputElement).value);
    brushSizeValue.textContent = currentBrushSize.toString();
    ctx.lineWidth = currentBrushSize;
});

canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDrawing);
canvas.addEventListener('mouseleave', stopDrawing);

canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    startDrawing(e);
});
canvas.addEventListener('touchmove', (e) => {
    e.preventDefault();
    draw(e);
});
canvas.addEventListener('touchend', stopDrawing);

canvas.addEventListener('pointerdown', startDrawing);
canvas.addEventListener('pointermove', draw);
canvas.addEventListener('pointerup', stopDrawing);

clearBtn.addEventListener('click', () => {
    saveState();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
});

undoBtn.addEventListener('click', () => {
    if (drawHistory.length > 0) {
        ctx.putImageData(drawHistory.pop()!, 0, 0);
    }
});

saveBtn.addEventListener('click', () => {
    const link = document.createElement('a');
    link.download = 'drawing.png';
    link.href = canvas.toDataURL();
    link.click();
});

saveState();

