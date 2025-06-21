import React from "react"
import Container30 from "./Container30px.js"
import { Link } from "react-router-dom";
import AddNewTask from "./AddNewTask.js";

const text=
<div className="containerSign" style={{padding:"40px", paddingTop:"10px"}}>
    <p style={{textAlign:"left", marginBottom:"0px"}}>
        Title:
    </p>
    <input type="text" style={{
        borderRadius: "8px",
        width:"100%",
        padding:"5px",
        borderColor: "black", 
        boxSizing: "border-box"}}>
    </input>   
    <p style={{textAlign:"left", marginBottom:"0px"}}>
        Description:
    </p>
    <input type="text" style={{
        borderRadius: "8px",
        width:"100%",
        padding:"5px",
        borderColor: "black", 
        boxSizing: "border-box"}}>
    </input>   
    <p style={{textAlign:"left", marginBottom:"0px"}}>
        Due to...
    </p>
    <input type="date" style={{
        borderRadius: "8px",
        width:"100%",
        padding:"5px",
        borderColor: "black", 
        boxSizing: "border-box"}}>
    </input>   
    <div className="SignUpButtonDiv">
        <button className="SignUpButton">Add Task</button>
    </div>
    
</div>

export default function Login(){
    return(
        <div>
            <div className="logContainer" style={{maxWidth:"1000px", margin:"auto"}}>
                <Container30 img={""} text={text}></Container30>
            </div>   
        </div>
    );
}