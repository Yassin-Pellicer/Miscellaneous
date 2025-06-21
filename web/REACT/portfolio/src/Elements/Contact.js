import React from "react"
import Projects from './Projects'
import Container40 from "./Container40px.js"
import Container30 from "./Container30px.js"
import Container40Left from "./Container40pxLeft.js"

export default function Contact(){
    return(
        <div style={{background: `linear-gradient(to bottom, rgba(255,255,255,1) 40%, 
        rgba(255,255,255,0)), url(${require("./ElementImages/newyork.jpeg")})`,
        MarginBottom: "50px", backgroundSize:"cover"}}>
            <h1 className="titleImportant">
                CONTACT
            </h1>
            <p style={{fontFamily:"Montserrat", textAlign:"center", marginTop:"50px", fontSize:"20px"}}>
                Here is my CV, with all my contact information and my previous experience.
            </p>
            <div style={{display:"flex", justifyContent:"space-around", marginTop:"50px"}}>
                <Container30 img={<img src={require("./ElementImages/YASSIN.png")} alt="" style={{height:"1250px",
                padding:"50px"}}></img>}/>
            </div>
        </div>
    )
}