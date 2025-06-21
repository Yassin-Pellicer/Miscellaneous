import React from "react"

export default function Container30({img, text}){
    return(
        <div style={{
            borderRadius: "50px",
            borderColor: "black", 
            boxSizing: "border-box",
            border: "1px solid black", 
            flexWrap: "wrap",
            backgroundColor:"white"
            }}>
                {img}
                <p style={{
                    margin:"0px",
                    fontSize: "20px"}}>
                    {text}
                </p>
        </div>
    )
}