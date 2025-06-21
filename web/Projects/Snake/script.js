const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');
const pointsScore = document.querySelector('[score]');

canvas.width = 600;
canvas.height = 600;
const resolution = 30;
const unitsize = canvas.width/resolution;

let randXfruit;
let randYfruit;

let snakeBody = []

let xVel = 0;
let yVel = 0;

let score = 0;
let snakeLen;

function gameStart(){
    snakeBody = [
        {x: 400, y: 400},
    ]
    running = true;
    xVel = 0;
    yVel = 0;
    score = 0;
    snakeLen = snakeBody.length;
    generateFood();
    drawFood();
    gameTick();
}

function gameTick(){
    if(running){
        moveSnake();
        clearBoard();
        drawSnake();
        drawFood();
        checkGameOver();
        setTimeout(() =>{
            gameTick();
        }, 60 );
    }
    else{
        displayGameOver();
        return;
    }
}

function drawFood(){
    ctx.fillStyle = 'red';
    ctx.fillRect(randXfruit, randYfruit, unitsize, unitsize);
}

function generateFood(){
    function randomGen(min, max){
        return Math.round((Math.random()*(max-min))/unitsize)*unitsize; 
    }
    randXfruit = randomGen(0, canvas.width-unitsize);
    randYfruit = randomGen(0, canvas.height-unitsize);
}

function moveSnake(){
    const head = {x: snakeBody[0].x + xVel,
                  y: snakeBody[0].y + yVel}
    
    snakeBody.unshift(head);
    if(snakeBody.length > snakeLen){
        snakeBody.pop();
    }

    if(snakeBody[0].x == randXfruit && snakeBody[0].y == randYfruit){
        score++;
        pointsScore.innerHTML = 'Score: ' + score.toString();
        snakeLen++;
        generateFood();
    }

    const moveUp = (yVel == -unitsize);
    const moveDown = (yVel == unitsize);
    const moveLeft = (xVel == -unitsize);
    const moveRight = (xVel == unitsize);

    document.addEventListener('keydown', (event) =>{
        if(event.key == 'w' && !moveDown){
            yVel = -unitsize;
            xVel = 0;
        }
        else if(event.key == 'a' && !moveRight){
            xVel = -unitsize;
            yVel = 0;
        }
        else if(event.key == 's' && !moveUp){
                yVel = unitsize;
                xVel = 0;
        }
        else if(event.key == 'd' && !moveLeft){
            xVel = unitsize;
            yVel = 0;
        }
    })

    if(head.x > canvas.width - unitsize){
        head.x = 0;
    }
    if(head.x < 0){
        head.x = canvas.width - unitsize;
    }
    if(head.y > canvas.height - unitsize){
        head.y = 0;
    }
    if(head.y < 0){
        head.y = canvas.height - unitsize;
    }
}

function drawSnake(){
    ctx.fillStyle = 'white';
    ctx.strokeStyle = 'green';
    snakeBody.forEach(snakeBody =>{
        ctx.fillRect(snakeBody.x, snakeBody.y, unitsize, unitsize);
        ctx.strokeRect(snakeBody.x, snakeBody.y, unitsize, unitsize);
    });
}

function clearBoard(){
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function checkGameOver(){
    for(let i = 1; i < snakeBody.length; i++){
        if(snakeBody[0].x == snakeBody[i].x && snakeBody[0].y == snakeBody[i].y){
            running = false;
        }
    }
}

function displayGameOver(){
    clearBoard();
    ctx.font = "50px MV Boli";
    ctx.fillStyle = "white";
    ctx.textAlign = "center";
    ctx.fillText("GAME OVER!", canvas.width / 2, canvas.height / 2);
    ctx.font = "25px MV Boli";
    ctx.fillText("press R to restart", canvas.width / 1.5, canvas.height / 1.5);
    if(running == false){
        document.addEventListener('keydown', (event) =>{
            if(event.key == 'r'){
                window.location.href = window.location.href;
            }
        });
    }
}

gameStart();
