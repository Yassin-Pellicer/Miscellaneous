import React from "react"

/*
    Export is a keyword used by the JSX
    syntax to determine a function that can
    be accessed by other .js files.

    Because you can export many variables from the same file,
    default is used only once in the whole file 👉🏼 to let you 
    import this default variable outside without using brackets {}:
*/
export default function Header(){
    return(
        <div>
            <h1 className = "name" style={{"justifyContent":"center",
                "textAlign":"center",
                "fontFamily":"monospace",
                "fontWeight":"bold",
                "fontSize":"10vw",
                "marginTop":"40px"}}>
                    Yassin Pellicer Lamla</h1>    
            <h2 className = "subtitle" style={{"justifyContent":"center",
                "textAlign":"center",
                "fontFamily":"monospace",
                "fontWeight":"100",
                "fontSize":"18px",
                "marginTop":"20px",
                "marginLeft":"100px",
                "marginRight":"100px",
                "marginBottom":"80px"}}>
                    Computer science student in the Polythecnic University of Valencia
                    eager to learn new things and explore the world of programming.</h2>
        </div>
    );
}