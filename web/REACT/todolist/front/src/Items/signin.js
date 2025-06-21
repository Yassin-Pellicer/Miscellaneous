import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useNavigate } from 'react-router-dom';

const SignIn = () => {
  // Initializing formData with keys for all form fields
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: '',
    surname: '',
    username: '',
    email: '',
    password: '',
    birth: ''
  });

  // Handle input change
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((values) => ({
      ...values,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("Form submitted:", formData);
    try {
      /* We check for existing mail */
      var response = await fetch('http://localhost:3001/user/used', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      var data = await response.json();
      if (!data.found) {
        /* We validate the input */
        response = await fetch('http://localhost:3001/user/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
        });
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        data = await response.json();
        console.log('Success:', data);
        alert("New user has been correctly registered!")
        navigate('/');
      }
      else {
        alert("These credentials are already in use. Please choose a different email address.")
        setFormData(() => ({
            email: '',
            password: '',
          })
        );
      }
    } catch (error) {
      alert("Invalid field(s) - please check your input.")
      console.error('Error:', error);
    }
  };

  return (
    <div style={{display:"flow", justifyContent:"center", alignItems:"center"}}>
    <form
        id="form"
        className="containerSign"
        style={{
        margin: "auto",
        marginTop:"60px",
        padding: "40px",
        borderRadius: "50px",
        borderColor: "black",
        justifyContent: "center",
        alignItems:"center",
        boxSizing: "border-box",
        border: "1px solid black",
        backgroundColor: "white",
        width: "600px",
        }}
    >
      <h1 className="log-in" style={{ textAlign: "left", marginBottom: "20px" }}>
        Sign Up:
      </h1>
      <label style={{ textAlign: "left", marginBottom: "0px" }}>
        Name:
        <input
          id="name"
          name="name" // Added name attribute
          type="text"
          value={formData.name}
          onChange={handleChange}
          style={{
            borderRadius: "8px",
            width: "100%",
            padding: "5px",
            borderColor: "black",
            boxSizing: "border-box",
          }}
        />
      </label>
      <p style={{ textAlign: "left", marginBottom: "0px" }}>Surname:</p>
      <input
        type="text"
        name="surname" // Added name attribute
        value={formData.surname}
        onChange={handleChange}
        style={{
          borderRadius: "8px",
          width: "100%",
          padding: "5px",
          borderColor: "black",
          boxSizing: "border-box",
        }}
      />
      <p style={{ textAlign: "left", marginBottom: "0px" }}>Username:</p>
      <input
        type="text"
        name="username" // Added name attribute
        value={formData.username}
        onChange={handleChange}
        style={{
          borderRadius: "8px",
          width: "100%",
          padding: "5px",
          borderColor: "black",
          boxSizing: "border-box",
        }}
      />
      <p style={{ textAlign: "left", marginBottom: "0px" }}>E-mail:</p>
      <input
        type="text"
        name="email" // Added name attribute
        value={formData.email}
        onChange={handleChange}
        style={{
          width: "100%",
          borderRadius: "8px",
          padding: "5px",
          borderColor: "black",
          boxSizing: "border-box",
        }}
      />
      <p style={{ textAlign: "left", marginBottom: "0px" }}>Password:</p>
      <input
        type="password"
        name="password" // Added name attribute
        value={formData.password}
        onChange={handleChange}
        style={{
          width: "100%",
          borderRadius: "8px",
          padding: "5px",
          borderColor: "black",
          boxSizing: "border-box",
        }}
      />
      <p style={{ textAlign: "left", marginBottom: "0px" }}>Repeat Password:</p>
      <input
        type="password"
        name="password" // Added name attribute
        value={formData.password}
        onChange={handleChange}
        style={{
          width: "100%",
          borderRadius: "8px",
          padding: "5px",
          borderColor: "black",
          boxSizing: "border-box",
        }}
      />
      <p style={{ textAlign: "left", marginBottom: "0px" }}>Date of Birth:</p>
      <input
        type="date"
        name="birth" // Added name attribute
        value={formData.birth}
        onChange={handleChange}
        style={{
          width: "100%",
          borderRadius: "8px",
          padding: "5px",
          borderColor: "black",
          boxSizing: "border-box",
          marginBottom:"30px"
        }}
      />
      <div className="SignUpButtonDiv">
        <button className="SignUpButton" onClick={handleSubmit}>
          Sign Up
        </button>
      </div>
      <p
        className="DontHaveAcc"
        style={{
          textAlign: "center",
          marginLeft: "40px",
          marginRight: "40px",
          marginBottom: "0px",
          marginTop: "40px",
        }}
      >
        Already have an account?
      </p>
      <div
        style={{
          marginBottom: "40px",
          marginTop: "10px",
          textAlign: "center",
        }}
      >
        <Link to="/" className="RegHere">
          Register Here!
        </Link>
      </div>
    </form>
    </div>
  );
};

export default SignIn;
