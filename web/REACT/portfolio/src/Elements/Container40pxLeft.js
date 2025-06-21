import React from "react"

export default function Container40({img, text}){
    return(
        <div style={{
            borderRadius: "50px",
            borderColor: "black", 
            boxSizing: "border-box",
            border: "1px solid black", 
            display: "flex",
            flexWrap:"wrap",
            margin: "40px",
            justifyContent: "center",
            alignItems: "center"}}>
                {text}
                {img}
        </div>
    )
}