const canvas = document.getElementById('secondCanvas');
const ctx = canvas.getContext('2d');

canvas.width = 1000;
canvas.height = 1000;

width = canvas.width;
height = canvas.height;

function drawTriangle(x, y, l){
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 0.3;
    ctx.beginPath();
    ctx.moveTo(x, y);

    z = Math.tan(60*Math.PI/180)*l/2

    ctx.lineTo(x+l/2, y+z);
    ctx.lineTo(x-l/2, y+z);
    ctx.lineTo(x,y);

    ctx.stroke();
}

function sierpinskiTriangle(x, y, l, n){
    if(n == 1){
        drawTriangle(x, y, l);
    }
    else{
        z = Math.tan(60*Math.PI/180)*l/4;
        sierpinskiTriangle(x-l/4, y+z, l/2, n-1);
        sierpinskiTriangle(x, y, l/2, n-1);
        sierpinskiTriangle(x+l/4, y+z, l/2, n-1);
        
        drawTriangle(x, y, l);
    }
}

sierpinskiTriangle(width/2, 175, 700, 9);



