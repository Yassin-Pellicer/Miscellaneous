import { Link } from "react-router-dom";
import React, { useEffect, useState } from "react";
import { useNavigate } from 'react-router-dom';

const Login = () => {
  // Initializing formData with keys for all form fields
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
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
      const response = await fetch('http://localhost:3001/user/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      
      const data = await response.json();
      if (data.found) {
        navigate('/Tasks', { state: data.user });
      }
      else {
        alert("Invalid e-mail or password. Please try again or make sure you have previously signed up.")
        setFormData(({
            email: '',
            password: '',
          })
        );
        document.getElementById("form").reset();
      }

    } catch (error) {
      alert("Invalid e-mail or password. Please try again or make sure you have previously signed up.")
      console.error('Error:', error);
    }
  };

  return (
    <div style={{ display: "flow", justifyContent: "center", alignItems: "center" }}>
      <h1 className='Main_Title'> To Do's!</h1>
      <form
        id="form"
        className="containerSign"
        style={{
          margin: "auto",
          padding: "40px",
          borderRadius: "50px",
          borderColor: "black",
          justifyContent: "center",
          alignItems: "center",
          boxSizing: "border-box",
          border: "1px solid black",
          backgroundColor: "white",
          width: "600px",
        }}
      >
        <h1 className="log-in" style={{ textAlign: "left", marginBottom: "20px" }}>
          Log In:
        </h1>
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
            marginBottom:"30px"
          }}
        />
        <div className="SignUpButtonDiv">
          <button className="SignUpButton" onClick={handleSubmit}>Log In</button>
        </div>
        <p className="DontHaveAcc" style={{ textAlign: "center", marginLeft: "40px", marginRight: "40px", marginBottom: "0px", marginTop: "40px" }}>
          Don't have an account yet?
        </p>
        <div style={{ marginBottom: "40px", marginTop: "10px", textAlign: "center" }}>
          <Link to="/SignIn" className="RegHere">Register Here!</Link>
        </div>
      </form>

    </div>
  );
};

export default Login;