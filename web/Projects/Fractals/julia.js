const canvas3 = document.getElementById('thirdCanvas');
const ctx3 = canvas3.getContext('2d');

canvas3.width = 1000;
canvas3.height = 1000;

width1 = canvas3.width;
height1 = canvas3.height;

function drawParticle(x, y, particleSize, c){
    ctx3.beginPath();
    ctx3.rect(x, y, particleSize, particleSize);
    ctx3.fillStyle = c;
    ctx3.fill();
}

function portrayJulia(){
    for(let x = 0; x <= width1; x++){
        for(let y = 0; y <= height1; y++){

            dx = (x-500)/300;
            dy = (y-500)/300;
            a = dx;
            b = dy;

            for(let t = 0; t <= 100; t++){
                d = (a*a) - (b*b) -0.76932;
                b = 2*(a*b) + -0.17523 ; 
                a = d;
                H = Math.abs(d+b)> 100;
                if(H){drawParticle(x, y, 1, 
                    "rgb("+ t*3 +","+ t*4 +","+ t*2.5 +")"); 
                    break;}
            }
        }
    }
}

portrayJulia();