import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import AddNewTask from "./add_task";
import ListedTask from "./listed_task";

const notLogged = (
  <div>
    <h1 className="Main_Title_Tasks">Looks like you aren't logged in yet...</h1>
    <div className="TaskPage" style={{ display: "flex", justifyContent: "space-around" }}>
      <div style={{ width: "500px" }}>
        <h1 style={{ fontSize: "20px", textAlign: "center" }}>Please log in or register if you haven't yet</h1>
        <div style={{ display: "flex" }}>
          <div>
            <p className="DontHaveAcc" style={{ textAlign: "center", margin: "40px 40px 0px 40px" }}>
              Don't have an account yet?
            </p>
            <div style={{ marginBottom: "40px", marginTop: "10px", textAlign: "center" }}>
              <Link to="/SignIn" className="RegHere">
                Register Here!
              </Link>
            </div>
          </div>
          <div>
            <p className="DontHaveAcc" style={{ textAlign: "center", margin: "40px 40px 0px 40px" }}>
              Already have an account?
            </p>
            <div style={{ marginBottom: "40px", marginTop: "10px", textAlign: "center" }}>
              <Link to="/" className="RegHere">
                Log In!
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const Tasks = () => {
  const location = useLocation();
  const user = location.state || {};
  const [taskList, setTaskList] = useState([]);

  const fetchTasks = async () => {
    if (Object.keys(user).length > 0) {
      try {
        const response = await fetch(`http://localhost:3001/user/get/tasks/${user[0].id}`);
        const data = await response.json();
        setTaskList(data.tasks || []);
        console.log(data.tasks)
      } catch (error) {
        console.error('Error:', error);
      }
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);
 
  if (Object.keys(user).length === 0) {
    return notLogged;
  }

  return (
    <div>
      <div
        style={{
          backgroundColor: "rgb(105, 162, 255)",
          color: "white",
          justifyContent: "space-between",
          display: "flex",
        }}
      >
        <h1 className="Main_Title_Tasks" style={{ marginLeft: "80px", marginTop: "20px", marginBottom: "20px" }}>
          Welcome, {user[0].name}.
        </h1>
        <div className="SignUpButtonDiv" style={{ alignContent: "center", marginTop: "7px" }}>
          <button className="SignUpButton" style={{ marginRight: "80px", marginTop: "20px", marginBottom: "20px" }}>
            Log out
          </button>
        </div>
      </div>

      <div className="TaskPage" style={{ display: "flex", justifyContent: "space-between", padding: "40px" }}>
        <div style={{ margin: "40px", boxSizing: "border-box", height: "600px", width: "60vw" }}>
          <AddNewTask id={user[0].id} />
        </div>
        <div style={{ flexDirection: "column", justifyContent: "space-around", height: "600px", width: "100vw", margin: "40px" }}>
          <div
            style={{
              borderRadius: "50px",
              borderTopRightRadius: "0px",
              borderBottomRightRadius: "0px",
              borderColor: "black",
              boxSizing: "border-box",
              border: "1px solid black",
              backgroundColor: "white",
            }}
          >
            <div
              className="containerSign"
              style={{
                padding: "40px",
                paddingTop: "10px",
                height: "603px",
                overflowX: "hidden",
                overflowY: "auto",
                boxSizing: "border-box",
                scrollbars: "right",
              }}
            >
              <div style={{display:"flex", justifyContent:"space-between"}}>
                <p style={{ textAlign: "left", marginBottom:"25px", marginLeft: "20px", marginTop: "20px", fontSize: "35px", fontWeight: "bold" }}>
                  Pending Tasks:
                </p>
                <div style={{display:"flex"}}>
                  <button id="fetchButton" className="SignUpButton" style={{padding:"5px", width:"70px", height:"40px", marginRight:"15px", marginTop:"20px"}} onClick={() => {fetchTasks()}}>
                    Fetch
                  </button>
                  <button id="fetchButton" className="SignUpButton" style={{padding:"5px", width:"140px", height:"40px", marginRight:"15px", marginTop:"20px", fontSize:"15px"}}>
                    View Completed
                  </button>
                </div>
              </div>
              <div>
                {taskList.length <= 0 ? (
                  <p style={{ marginLeft: "20px", marginTop: "20px", marginBottom: "20px", fontFamily:"arial", fontSize:"40px"}}>
                    You have no pending tasks.
                  </p>
                ) : (taskList.map((task, index) => (
                  <ListedTask
                    key={task.inner_id}
                    title={task.title}
                    description={task.description}
                    due={task.due}
                    inner_id={task.inner_id}
                  />
                )))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Tasks;

