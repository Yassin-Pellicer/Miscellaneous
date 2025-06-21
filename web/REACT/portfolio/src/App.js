import Header from './Elements/Header'
import TopBar from './Elements/topBar'
import AboutMe from './Elements/AboutMe'
import Projects from './Elements/Projects'
import Contact from './Elements/Contact'
import "./style.css"

function App() {
	return (
		<div className = "App">
			<div style={{background: `linear-gradient(to bottom, rgba(255,255,255,0) 40%, 
				rgba(255,255,255,1)), url(${require("./Elements/ElementImages/Sky.jpg")})`,
				BackgroundSize: "100vh",
				MarginBottom: "50px"}}>
				<TopBar/>
				<Header/>
				<AboutMe/>
			</div>
				<Projects/>
				<Contact/>
		</div>
	);
}

export default App;
