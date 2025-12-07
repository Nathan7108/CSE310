const canvas = document.getElementById('drawingCanvas');
const ctx = canvas.getContext('2d');
const colorPicker = document.getElementById('colorPicker');
const brushSize = document.getElementById('brushSize');
const brushSizeValue = document.getElementById('brushSizeValue');
const clearBtn = document.getElementById('clearBtn');
const undoBtn = document.getElementById('undoBtn');
const saveBtn = document.getElementById('saveBtn');
let isDrawing = false;
let currentColor = '#000000';
let currentBrushSize = 5;
let drawHistory = [];
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
function startDrawing(e) {
    isDrawing = true;
    saveState();
    const point = getPoint(e);
    ctx.beginPath();
    ctx.moveTo(point.x, point.y);
}
function draw(e) {
    if (!isDrawing)
        return;
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
function getPoint(e) {
    const rect = canvas.getBoundingClientRect();
    if (e instanceof TouchEvent && e.touches.length > 0) {
        return {
            x: e.touches[0].clientX - rect.left,
            y: e.touches[0].clientY - rect.top
        };
    }
    if (e instanceof PointerEvent || e instanceof MouseEvent) {
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }
    return { x: 0, y: 0 };
}
colorPicker.addEventListener('input', (e) => {
    currentColor = e.target.value;
    ctx.strokeStyle = currentColor;
});
brushSize.addEventListener('input', (e) => {
    currentBrushSize = parseInt(e.target.value);
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
        ctx.putImageData(drawHistory.pop(), 0, 0);
    }
});
saveBtn.addEventListener('click', () => {
    const link = document.createElement('a');
    link.download = 'drawing.png';
    link.href = canvas.toDataURL();
    link.click();
});
saveState();
