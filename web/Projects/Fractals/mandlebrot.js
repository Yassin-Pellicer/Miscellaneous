const canvas1 = document.getElementById('firstCanvas');
const ctx1 = canvas1.getContext('2d');

canvas1.width = 1000;
canvas1.height = 1000;

width1 = canvas1.width;
height1 = canvas1.height;

function drawParticle(x, y, particleSize, c){
    ctx1.beginPath();
    ctx1.rect(x, y, particleSize, particleSize);
    ctx1.fillStyle = c;
    ctx1.fill();
}

function portrayMandlebrot(){
    for(let x = 0; x <= width1; x++){
        for(let y = 0; y <= height1; y++){

            dx = (x-500)/500 - 0.5;
            dy = (y-500)/500;
            a = dx;
            b = dy;

            for(let t = 0; t <= 100; t++){
                // z = z^2 + c -> z = (a + bi)(a + bi) + (a + bi) -> z = a^2 - b^2 + 2abi + (a + bi) -> zn+1 = (a^2 - b^2 + a)^2 - (2abi + bi)^2 + (a + bi)
                d = (a*a) - (b*b) + dx; // a^2 - b^2 + a, real part
                b = 2*(a*b) + dy; // 2abi + bi, imaginary part, -0.76932, -0.17523 for a cool julia set!
                a = d;
                H = Math.abs(d+b)> 100;
                if(H){drawParticle(x, y, 1, "rgb("+ t*10 +","+ t*4 +","+ t*2.5 +")"); break;}
            }
        }
    }
}

portrayMandlebrot();