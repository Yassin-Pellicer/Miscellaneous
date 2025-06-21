import React from "react"
import Quill from 'quill';
import 'react-quill/dist/quill.snow.css';
import { useEffect, useRef, useState } from "react";

const Task = (props) => {
  const [formData, setFormData] = useState({
    id: '',
    title: '',
    description: '',
    due: ''
  }); 

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((values) => ({
      ...values,
      [name]: value,
    }));
  };

  /* Quill configuration */
  const quillRef = useRef(null); // Reference to the editor div
  const [quill, setQuill] = useState(null); // State to hold the Quill instance

  useEffect(() => {
    if (quillRef.current && !quill) {
      const quillInstance = new Quill(quillRef.current, {
        theme: 'snow',
      });
      setQuill(quillInstance);
    }
  }, [quill]);
  
  const extractContents = () => {
    if (quill) {
      const delta = quill.root.innerHTML // Get the Delta format
      const plainText = quill.getText(); // Get plain text

      console.log('Delta:', JSON.stringify(delta));
      console.log('Plain Text:', plainText);

      formData.description = delta
      formData.id = props.id;

      console.log(formData)
    }
  };

  const handleSubmit = async (e) => {
    extractContents();
    e.preventDefault();
    
    const buttonToTrigger = document.getElementById('fetchButton');

    try {
      var response = await fetch('http://localhost:3001/user/exists', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      var data = await response.json();
  
      if (!data.found) {
        alert("User does NOT exist. Please create your user first.")
      }
      else {
        console.log("Form submitted:", formData);
        try {
          var response = await fetch('http://localhost:3001/user/tasks/add', {
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
            alert("Task added successfully.")
            setFormData({
              id: '',
              title: '',
              description: '',
              due: ''
            })
            document.getElementById("form").reset();
            quill.setContents([{ insert: '\n' }]);
          }
        } catch (error) {
          alert("Invalid field(s) - please check your input.")
          console.error('Error:', error);
        }
        buttonToTrigger.click(); 
      }
    } catch (error) {} 
  };
  
  return (
    <div style={{
      borderRadius: "50px",
      borderColor: "black",
      boxSizing: "border-box",
      border: "1px solid black",
      flexWrap: "wrap",
      backgroundColor: "white"
    }}>
      <form id="form">
        <div className="containerSign" style={{ padding: "40px", paddingTop: "10px" }}>
          <p style={{ textAlign: "left", marginTop: "30px", marginBottom: "10px", fontSize: "30px", fontWeight: "bold" }}>
            Add New Task:
          </p>

          <p style={{ textAlign: "left", marginTop: "20px", marginBottom: "10px" }}>
            Title:
          </p>
          <input
            name="title"
            value={formData.name}
            onChange={handleChange}
            type="text" style={{
              borderRadius: "8px",
              width: "100%",
              padding: "5px",
              borderColor: "black",
              boxSizing: "border-box"
            }}>
          </input>
          <p style={{ textAlign: "left", marginBottom: "10px" }}>
            Description:
          </p>
          <div ref={quillRef} style={{ height: '200px' }} />
          <p style={{ textAlign: "left", marginBottom: "10px" }}>
            Due to...
          </p>
          <input type="date"
            name="due"
            onChange={handleChange}
            style={{
              borderRadius: "8px",
              width: "100%",
              padding: "5px",
              marginBottom: "30px",
              borderColor: "black",
              boxSizing: "border-box"
            }}>
          </input>
          <div className="SignUpButtonDiv">
            <button className="SignUpButton" onClick={handleSubmit} >Upload Task</button>
          </div>
        </div>
      </form>
      
    </div>
  )
}

export default Task