import React from "react"
import Quill from 'quill';
import 'react-quill/dist/quill.bubble.css';
import { useEffect, useRef, useState } from "react";

const Tasks = (props) => {
  /* Quill configuration */
const dateInputRef = useRef(null);
  console.log(props.title);
  const initialValue = props.due.substring(0, 10);
  console.log(initialValue);
  const quillRef = useRef(null); // Reference to the editor div
  const [quill, setQuill] = useState(null); // State to hold the Quill instance
  const [editable, setEditable] = useState(false);
  const [buttonText, setButtonText] = useState('Edit Task'); // State to manage button text

  // Initialize Quill editor
  useEffect(() => {
    if (quillRef.current && !quill) {
      const quillInstance = new Quill(quillRef.current, {
        theme: 'snow',
      });
      setQuill(quillInstance);
      quillInstance.disable(); // Start in read-only mode
      quillInstance.root.innerHTML = props.description;
    }
  }, [quill, props.description]);

  // Toggle editability
  const edit = () => {
    setEditable(prevEditable => {
      const newEditable = !prevEditable;
      if (quill) {
        quill.enable(newEditable); // Enable or disable the editor
        if(!newEditable) { handleModify(); console.log("hola")}
        setButtonText(newEditable ? 'Save All' : 'Edit Task'); // Update button text
      }
      return newEditable;
    });
  };

  // Set initial value for the date input
  useEffect(() => {
    const dateInput = dateInputRef.current;
    if (dateInput) {
      dateInput.value = initialValue;

      const handleInput = () => {
        dateInput.value = initialValue;
      };
      dateInput.addEventListener('input', handleInput);
      return () => {
        dateInput.removeEventListener('input', handleInput);
      };
    }
  }, [initialValue]);

  const [formData, setFormData] = useState({
    inner_id: '',
    description: '',
  });

  const extractContents = () => {
    if (quill) {
      const delta = quill.root.innerHTML // Get the Delta format
      const plainText = quill.getText(); // Get plain text

      console.log('Delta:', JSON.stringify(delta));
      console.log('Plain Text:', plainText);

      formData.description = delta
      formData.inner_id = props.inner_id;
    }
  };

  const handleModify = async (e) => {
    extractContents()
    try {
      var response = await fetch('http://localhost:3001/user/tasks/modify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      var data = await response.json();

      if (data.err != "") {
        alert("Invalid entries. Please check.")
      }
      else {
        alert("Task modified successfully.")
        setFormData({
          id: '',
          title: '',
          description: '',
          due: ''
        })
      }
    } catch (error) {
      alert("Invalid field(s) - please check your input.")
      console.error('Error:', error);
    }
  };

  const handleDelete = async (e) => {
    
    const buttonToTrigger = document.getElementById('fetchButton');

    console.log("Delete Submitted. ID:", props.inner_id);
    try {
      var response = await fetch(`http://localhost:3001/user/tasks/delete/${props.inner_id}`);
      var data = await response.json();
      console.log(data)
  
      if (data.found === true) {
        alert("Task removed successfully")
      }
      else{
        alert("An error has occurred")
      }
      buttonToTrigger.click(); 

    } catch (error) {
      console.error('Error:', error);
    }
  };

  var body =
    <div className="containerSign" style={{ padding: "40px", paddingTop: "10px" }}>
      <p style={{ textAlign: "left", marginTop: "30px", marginBottom: "10px", fontSize: "30px", fontWeight: "bold" }}>
        {props.title}
      </p>
      <div ref={quillRef} style={{ maxHeight: '200px' }} />
      <p id="due_to_header" style={{ textAlign: "left", marginBottom: "10px" }}>
        Due to...
      </p>
      <input type="date" id="due_date" ref={dateInputRef} style={{
        borderRadius: "8px",
        width: "100%",
        padding: "5px",
        borderColor: "black",
        boxSizing: "border-box"
      }}>
      </input>
      <div className="SignUpButtonDiv" style={{ position: "relative", display: "flex", justifyContent: "space-between" }}>
        <button className="SignUpButton" style={{ marginTop: "20px", backgroundColor: "rgb(145, 255, 122)" }}>Complete task</button>
        <button className="SignUpButton" onClick={handleDelete} style={{ marginTop: "20px", backgroundColor: "rgb(255, 74, 92)" }}>Delete task</button>
        <button className="SignUpButton" id="modifyButton" onClick={edit} style={{ marginTop: "20px", backgroundColor: "rgb(138, 142, 255)" }}>{buttonText}</button>
      </div>
    
    </div>

  if (initialValue == null && document.getElementById("due_date") != null && document.getElementById("due_to_header") != null ){
    document.getElementById("due_date").remove()
    document.getElementById("due_to_header").remove()
  }  

  return (
  <div style={{
      borderRadius: "50px",
      borderColor: "black", 
      boxSizing: "border-box",
      border: "1px solid black",
      flexWrap: "wrap",
      backgroundColor: "white",
      margin:"20px",
      width:"auto"
    }}>
      {body}
    </div>
  )
}

export default Tasks