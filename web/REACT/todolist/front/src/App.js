import './App.css'
import Login from './Items/login.js'
import SignIn from './Items/signin.js'
import Tasks from './Items/tasks.js'
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App () {
  return (
    <BrowserRouter>
    <Routes>
      <Route path="/" element={<Login/>}></Route>
      <Route path="/SignIn" element={<SignIn/>}></Route>
      <Route path="/Tasks" element={<Tasks/>}></Route>
    </Routes>  
    </BrowserRouter>
  )
}

export default App

