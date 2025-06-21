import React from "react"
import Container40 from "./Container40px.js"
import Container30 from "./Container30px.js"
import Container40Left from "./Container40pxLeft.js"
import MathJax from 'mathjax'

/*info*/
const SnakeGame=
<div style={{padding:"40px", inlineSize:"450px"}}>
    <h1 style={{fontFamily:"monospace", marginBottom:"20px"}}>
        Snake Game
    </h1>
    <p style={{
            justifyContent:"center", 
            alignContent:"center",
            textAlign:"center"}}>
        <img src={require("./ElementImages/snake.png")} alt="" style={{height: "300px"}}></img> <br></br> <br></br>
    </p>
    <p style={{textAlign:"justify"}}>
        The classic snake game <b> done in python with the pygame library </b>
        <br></br> <br></br> This one was <b>one of my first
        projects.</b> It involved learning the basics of python along with pygame to develop something I had already created a while back
        in web with the <b> vanilla elements of HTML, Javascript and CSS</b> (with canvas, textStroke, eventListeners...). <br></br> <br></br>
    </p>
</div>

const inlineFormula = `Z_{n+1} = Z_n^2 + C`;
const juliaSet = 
    <img src={require("./ElementImages/fractals.png")} alt="" style={{height: "700px", borderRadius:"50px", marginRight:"40px",
    marginBottom:"40px", marginTop:"40px"}}></img>
const fractals=
<div style={{padding: "40px", inlineSize:"650px"}}>
    <h1 style={{fontFamily:"monospace", marginBottom:"20px"}}>
        Fractals
    </h1>
    <p style={{
            justifyContent:"center", 
            alignContent:"center",
            textAlign:"center"}}>
        My interest in these mathematical structures sprung from this <b>Numberphile video:</b> <br></br> <br></br>
        <iframe width="400" height="200" src="https://www.youtube.com/embed/FFftmWSzgmk" title="YouTube video player" 
        frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; 
        web-share"></iframe> <br></br> <br></br>
    </p>
    <p style={{
            justifyContent:"center", 
            alignContent:"center",
            textAlign:"justify"}}>
        As we can see in the video, the Julia and Mandlebrot sets are <b>2D portrayals that show which complex numbers C do NOT diverge </b>
        after a certain number of iterations given a starting point based on the following sequence <br></br> <br></br>
        
        <MathJax.Provider><p><MathJax.Node inline formula={inlineFormula}/></p></MathJax.Provider><br></br>

        Where C (our starting imaginary number) and Z0 (the first number in the sequence, n = 0) are a 
        <b> complex number with an imaginary component and a real component. <br></br> </b>The <b>only</b> difference between
        a mandlebrot set and a julia set is that the mandlebrot set's Z0 starts off at 0. <br></br> <br></br>
    </p>
    <p style={{
            justifyContent:"center", 
            alignContent:"center",
            textAlign:"center"}}>
        The approach followed in code is quite simple: <br></br> <br></br>
        <img src={require("./ElementImages/fractalCode.png")} alt="" style={{height: "300px"}}></img>
    </p>
</div>

const brickBreaker=
<div style={{padding: "40px", inlineSize:"450px"}}>
    <h1 style={{fontFamily:"monospace", marginBottom:"20px"}}>
        Brick breaker
    </h1>
    <p style={{
            justifyContent:"center", 
            alignContent:"center",
            textAlign:"center"}}>
        <img src={require("./ElementImages/brickBreaker.png")} alt="" style={{height: "300px"}}></img> <br></br> <br></br>
    </p>
    <p style={{
            justifyContent:"center", 
            alignContent:"center",
            textAlign:"justify"}}>
        I wanted to recreate this <b>classic old-fashion telephone game</b> in python. The premise of the game
        is as simple as it can get: you guide a ball to collide with a group of blocks, making it bounce against a platform
        controlled by A/D and the arrow keys. <br></br> <br></br> If <b>the ball escapes the screen, you lose. If you break every brick, 
        you win! </b>
        <br></br> <br></br>
        
        This project was the one in which i decided to look for the <b>least amount of information</b>, as an intent
        to develop a new idea by myself. If I were to rebuild it today, i'd go for a more intensive OOP approach. <br></br> <br></br>
    </p>
    <p style={{
            justifyContent:"center", 
            alignContent:"center",
            textAlign:"center"}}>

        Here is a snippet with the code that loops along the array of bricks and prints only those still 
        not hit: <br></br> <br></br>
    </p>
    <code style={{fontSize:"13px"}}>
        while i &lt; len(GroupBlock): <br></br>
        &emsp; &emsp; &emsp; if (GroupBlock[i].status is False): <br></br>
        &emsp; &emsp; &emsp; pygame.draw.rect(dis, black, [GroupBlock[i].positionX, <br></br>
        &emsp; &emsp; &emsp; GroupBlock[i].positionY, squareWidth, squareHeight], 1) <br></br>
        &emsp; &emsp; &emsp; i = i + 1
    </code>
</div>

const gameOfLifeImage=
    <video src={require("./ElementImages/conway.mp4")} type="video/mp4" autoPlay loop muted playsinline style={{width:"20vw",
    marginRight:"40px",
    marginBottom:"40px", marginTop:"40px"}}></video>
const gameOfLife=
<div style={{padding: "40px", inlineSize:"650px"}}>
    <h1 style={{fontFamily:"monospace", marginBottom:"20px"}}>
       Conway's Game of Life
    </h1>
    <p style={{
            justifyContent:"center", 
            alignContent:"center",
            textAlign:"justify"}}>
        This zero player game has a very simple dynamic, with just <b>four rules:</b> <br></br>
        <br></br>1. Any live cell with fewer than two live neighbours dies.
        <br></br>2. Any live cell with two or three live neighbours lives on.
        <br></br>3. Any live cell with more than three live neighbours dies.
        <br></br>4. Any dead cell with exactly three live neighbours becomes a live cell.
        <br></br> <br></br>
        
        I performed this project using only the basic HTML, CSS, and Javascript tools. In this particular
        project I learned to manage arrays the way interpreted languages such as python let you use them.
        <br></br> <br></br>

        I had to read quite a bit of documentation for this one, but I was happy <b>I was able to provide my own
        features letting the user randomize and customize the patterns to generate what they want to see.</b> <br></br> The user
        would move a red dot using the WASD keys, and place new cells by pressing ENTER. <br></br> <br></br>

        <b>Here you will see a video of the conway's game of life using my implementation.</b>
    </p>
</div>

const skills =
<div style={{display:"flex", justifyContent:"center", flexWrap:"wrap", padding:"50px"}}>
    <Container30 img={<img src={require("./ElementImages/icons/c-.png")} alt="" style={{height:"150px",
    padding:"20px"}}></img>}/>
        <Container30 img={<img src={require("./ElementImages/icons/letter-c.png")} alt="" style={{height:"150px",
    padding:"20px"}}></img>}/>
        <Container30 img={<img src={require("./ElementImages/icons/haskell.png")} alt="" style={{height:"150px",
    padding:"20px"}}></img>}/>
        <Container30 img={<img src={require("./ElementImages/icons/html-5.png")} alt="" style={{height:"150px",
    padding:"20px"}}></img>}/>
        <Container30 img={<img src={require("./ElementImages/icons/css-3.png")} alt="" style={{height:"150px",
    padding:"20px"}}></img>}/>
        <Container30 img={<img src={require("./ElementImages/icons/js.png")} alt="" style={{height:"150px",
    padding:"20px"}}></img>}/>
        <Container30 img={<img src={require("./ElementImages/icons/physics.png")} alt="" style={{height:"150px",
    padding:"20px"}}></img>}/>
        <Container30 img={<img src={require("./ElementImages/icons/python.png")} alt="" style={{height:"150px",
    padding:"20px"}}></img>}/>
            <Container30 img={<img src={require("./ElementImages/icons/java.png")} alt="" style={{height:"150px",
    padding:"20px"}}></img>}/>
</div>

/*items*/
const rightCardText = 
    <div>
        <h1 style={{marginBottom:"20px", marginTop:"40px", fontFamily:"Syncopate", textAlign:"center"}}>
            PYTHON <br></br> PROJECTS
        </h1>
        <Container40 img={""} text={brickBreaker}/>
        <Container30 img={""} text={SnakeGame}/> 
    </div>

const leftCardText = 
    <div>
        <h1 style={{fontFamily:"Syncopate", padding:"0px", textAlign:"center", marginTop:"40px"}}>
            WEB PROJECTS
        </h1>   
        <Container40Left img={juliaSet} text={fractals}/>
        <br></br>
        <Container40Left img={gameOfLifeImage} text={gameOfLife}/>
    </div>

export default function Projects(){
    return(
        <div>
            <h1 className="titleImportant" style={{textAlign:"center", marginBottom:"40px"}}>
                MY PROJECTS
            </h1>
            <div style={{display:"flex", justifyContent:"space-around", margin:"50px", flexWrap:"wrap"}}>
                {<Container30 img={""} text={leftCardText}/>}
                {<Container30 img={""} text={rightCardText}/>}
            </div>
            <h1 style={{fontFamily:"Syncopate", padding:"0px", textAlign:"center", marginTop:"40px", fontSize:"70px"}}>
                    SKILLS DEVELOPED
            </h1>
            <div style={{display:"flex", justifyContent:"center", marginRight:"200px", marginLeft:"200px", marginBottom:"100px"}}>
                {<Container30 img={""} text={skills}/>}
            </div>  
        </div>
    )
}