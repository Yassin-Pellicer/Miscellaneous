const mysql = require('mysql2')
const cors = require('cors')
const express = require('express')
const bodyParser = require('body-parser');

const app = express()
app.use(cors())
app.use(bodyParser.json());

const connection = mysql.createConnection({
  host: 'localhost',
  user: 'root',
  password: 'secret',
  database: 'todo-schema',
  port: '3306'
})

app.get('/', (re, res) => {
  return res.json("From Backend Side")
})

app.listen(3001, () => {
  console.log("\nListening!") 
})

connection.connect((err) => {
  if (err) {
    console.log("\nAn error has occurred: " + err + ".")
  }
  else {
    console.log("\nDatabase connected successfully.")
  }
})

app.get("/user", (req, res) => {
  const query = "SELECT * FROM user";
  connection.query(query, (err, data) => {
    if (err) return res.json(err)
    return res.json(data)
  })
})

app.get("/user/get/:id", (req, res)=> {
  const userId = req.params.id;
  const query = `SELECT * FROM user WHERE id = ?`
  connection.query(query, [userId], (err, data) => {
    if (err) return res.json(err)
    return res.json(data)
  })
})

app.post("/user/add", (req, res)=> {
  const {name, surname, birth, username, email, password } = req.body
  if (!name || !email || !password || !surname || !username || !password || !birth) {
    return res.status(400).json({ error: 'Missing field is required.' });
  }
  const query = `INSERT INTO user(name, surname, birth, email, username, password) VALUES (?, ?, ?, ?, ?, ?)`
  connection.query(query, [name, surname, birth, email, username, password], (err, data) => {
    if (err) res.json(err)
    else {
      console.log(`User with name '${name}' has been successfully added to the DB`)
      res.json({ message: 'User has been successfully added to the DB' });
    }
  })
})

app.post("/user/delete", (req, res)=> {
  const { id } = req.body
  const query = `DELETE FROM user WHERE id = ?`
  connection.query(query, [id], (err, data) => {
    if (err) res.json(err)
    else {
      console.log(`User with id '${id}' has been successfully removed from the DB`)
      res.json({ message: 'User deleted successfully (or has been already deleted)' });
    }
  })
})

app.post("/user/verify", (req, res)=> {
  const { email, password } = req.body
  if (!email || !password) {
    return res.status(400).json({ error: 'Missing field is required.' });
  }
  const query = `SELECT * FROM user WHERE email = ? AND password = ? `
  connection.query(query, [email, password], (err, data) => {
    if (err) res.json(err)
    else {
      console.log(`User with email '${email}' has been found`)
      console.log(data)
      if(data.length == 0){
        res.json({ message: 'User NOT found.', found: false, user: null}) 
      }
      else{
        res.json({ message: 'User found!', found: true, user: data})
      }
    }
  })
})

app.post("/user/exists", (req, res)=> {
  const { id } = req.body
  if (!id) {
    return res.status(400).json({ error: 'Missing field is required.' });
  }
  const query = `SELECT * FROM user WHERE id = ?`
  connection.query(query, [ id ], (err, data) => {
    if (err) res.json(err)
    else {
      console.log(`User with id '${id}' has been found`)
      console.log(data)
      if(data.length == 0){
        res.json({ message: 'User NOT found.', found: false, user: null}) 
      }
      else{
        res.json({ message: 'User found!', found: true, user: data})
      }
    }
  })
})

app.post("/user/used", (req, res)=> {
  const { email} = req.body
  if (!email) {
    return res.status(400).json({ error: 'Missing field is required.' });
  }
  const query = `SELECT * FROM user WHERE email = ?`
  connection.query(query, [email], (err, data) => {
    if (err) res.json(err)
    else {
      console.log(`User with email '${email}' has been found`)
      console.log(data)
      if(data.length == 0){
        res.json({ message: 'User NOT found.', found: false}) 
      }
      else{
        res.json({ message: 'User found!', found: true})
      }
    }
  })
})

app.get("/user/get/tasks/:id", (req, res)=> {
  id = req.params.id;
  const query = `SELECT * FROM tasks WHERE id = ?`
  connection.query(query, [id], (err, data) => {
    if (err) res.json(err)
    else {
      console.log(data)
      if(data.length != 0){
        res.json({tasks: data}) 
      }
    }
  })
})

app.get("/user/tasks/delete/:id", (req, res)=> {
  id = req.params.id;
  const query = `DELETE FROM tasks WHERE inner_id = ?`
  connection.query(query, [id], (err, data) => {
    if (err) res.json(err)
    else {
      console.log(data)
      res.json({found: true}) 
    }
  })
})


app.post("/user/tasks/add", (req, res)=> {
  const {id, title, description, due} = req.body
  console.log(req.body);
  if (!title || !description || !due) {
    return res.status(400).json({ err: 'Missing field is required.' });
  }
  const query = `INSERT INTO tasks(id, title, description, due, completed, creation_date) VALUES (?, ?, ?, ?, false, CURDATE())`
  connection.query(query, [id, title, description, due], (err, data) => {
    if (err) res.json(err)
    else {
      res.json({ message: 'Task has been successfully added to the DB', err: '' });
    }
  })
})

app.post("/user/tasks/modify", (req, res)=> {
  const {inner_id, description} = req.body
  console.log(req.body);
  if (!description) {
    return res.status(400).json({ err: 'Missing field is required.' });
  }
  const query = `UPDATE tasks SET description = ? WHERE inner_id = ?`
  connection.query(query, [description, inner_id], (err, data) => {
    if (err) res.json(err)
    else {
      res.json({ message: 'Task has been successfully modified to the DB', err: '' });
    }
  })
})


