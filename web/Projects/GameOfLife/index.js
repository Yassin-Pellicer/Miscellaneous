const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');

//dimensions
const resolution = 40;
canvas.width = 4000;
canvas.height = 2000;

const COLS = canvas.width/resolution;
const ROWS = canvas.height/resolution;

//gridbuilding
function buildGridRandom(){
    return new Array(COLS).fill(null)
        .map(() => new Array(ROWS).fill(null)
            .map(() => Math.floor(Math.random()*1.5)));
}

//drawing function
function render(grid){
    for(let col = 0; col < COLS; col++){
        for(let row = 0; row < ROWS; row++){
            const cell = grid[col][row];

            ctx.beginPath();
            ctx.rect(col * resolution, row * resolution, resolution, resolution);
            ctx.fillStyle = cell ? 'black' : 'white';
            ctx.fill();
        }
    }
}

//logic
function logic(grid){
    const newGrid = grid.map(arr => [...arr]);

    for(let col = 0; col < COLS; col++){
        for(let row = 0; row < ROWS; row++){
            const cell = grid[col][row];
            let numNeighbors = 0;
            for(let i = -1; i < 2; i++){
                for(let j = -1; j < 2; j++){
                    if(i === 0 && j == 0){
                        continue;
                    }
                    const x_cell = col + i;
                    const y_cell = row + j;

                    if(x_cell >= 0 && y_cell >= 0 && x_cell < COLS && y_cell < ROWS){
                        currentNeighbor = grid[col + i][row + j]; 
                        numNeighbors += currentNeighbor;
                    }
                }
            }

            //rules
            //underpopulation. Less than 2 neighbouring cells.
            if(cell === 1 && numNeighbors < 2){
                newGrid[col][row] = 0;
            }
            //overpopulation. More than 3 neighbouring cells.
            else if(cell === 1 && numNeighbors > 3){
                newGrid[col][row] = 0;
            }
            //birth. Dead cell with 3 neighbours becomes alive.
            else if(cell === 0 && numNeighbors === 3){
                newGrid[col][row] = 1;
            }
        }
    }
    return newGrid;
}

const clear = document.querySelector('[clear-button]');
const run = document.querySelector('[run-button]');
const step = document.querySelector('[step-button]');
let toggle = -1;
function buttons(){
    clear.addEventListener('click', () =>{
        for(let col = 0; col < grid.length; col++){
            for(let row = 0; row < grid[col].length; row++){
                grid[col][row] = 0;
            }
        }
        run.innerHTML = 'Run';
        toggle = toggle*-1;
        requestAnimationFrame(update);
    });
    
    run.addEventListener('click', () =>{
        toggle = toggle*-1;
        if(toggle == 1){
            run.innerHTML = 'Stop';
            requestAnimationFrame(update());
        }
        else{
            run.innerHTML = 'Run';
        }
    });

    step.addEventListener('click', () =>{
        if(toggle == 1){
            toggle = toggle*-1;
            run.innerHTML = 'Run';
        }
        requestAnimationFrame(update);
    })
}

//Cell adder
function cellAdder(){
    selectorX = 0;
    selectorY = 0;

    document.addEventListener('keypress', (event) =>{
        if(toggle == 1){
            toggle = toggle*-1;
            run.innerHTML = 'Run';
        }
        if(event.key == 'w'){
            console.log(`key: ${event.key} has been pressed down`);
            selectorY--;
        }
        else if(event.key == 'a'){
            console.log(`key: ${event.key} has been pressed down`);
            selectorX--;
        }
        else if(event.key == 's'){
            console.log(`key: ${event.key} has been pressed down`);
            selectorY++;
    
        }
        else if(event.key == 'd'){
            console.log(`key: ${event.key} has been pressed down`);
            selectorX++;
        }
        else if(event.key == 'p'){
            console.log(`key: ${event.key} has been pressed down`);
            if(grid[selectorX][selectorY] == 0){
                grid[selectorX][selectorY] = 1;
                render(grid);
            }
            else{
                grid[selectorX][selectorY] = 0;
                render(grid);
            }
        }

        if(selectorX >= COLS-1){
            selectorX = COLS-1;
        }
        else if(selectorX < 0){
            selectorX = 0;
        }

        if(selectorY < 0){
            selectorY = 0;
        }
        else if(selectorY >= ROWS-1){
            selectorY = ROWS-1;
        }

        for(let col = 0; col < grid.length; col++){
            for(let row = 0; row < grid[col].length; row++){
                const cell = grid[col][row];
                if(selectorX == col && selectorY == row){
                    ctx.beginPath();
                    ctx.rect(col * resolution, row * resolution, resolution, resolution);
                    ctx.fillStyle = 'red';
                    ctx.fill();
                }
                else{
                    ctx.beginPath();
                    ctx.rect(col * resolution, row * resolution, resolution, resolution);
                    ctx.fillStyle = cell ? 'black' : 'white';
                    ctx.fill();
                }
            }
        }
    });
}

let grid = buildGridRandom();
buttons();
cellAdder();
render(grid);

function update(){
    grid = logic(grid);
    render(grid);
    if(toggle == 1){
        requestAnimationFrame(update);
    }
}