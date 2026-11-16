import "./Home.css";
import Navbar from "./Navbar";

function Home() {
  return (
    <div className="home">
      <Navbar />
      <h1>Welcome to the Student Management App!</h1>
      <p>This is the home page for the Student Management App.</p>
      <p>On this page, you can perform various actions:</p>
      <ul>
        <li>adding, removing, updating & viewing new students</li>
        <li>uploading and viewing assignment submissions</li>
        <li> checking grades</li>
        <li> viewing student profiles</li>
      </ul>
      <p>To get started, you can navigate to the different sections of the app using the links below:</p>
      <div className="main-card">
        <div className="card" style={{ maxWidth: "320px" }}>
          <div className="card-body">
            <h4 className="card-title">Student Access</h4>
            <p className="card-text">For students, this is where you can upload assignments and view your fees statements.</p>
            <a href="/studentlogin" className="btn btn-primary">Click as student</a>
          </div>
        </div>
        <div className="card" style={{ maxWidth: "320px" }}>
          <div className="card-body">
            <h4 className="card-title">Teacher Access</h4>
            <p className="card-text">For teachers, this is where you can manage student records and view assignment submissions.</p>
            <a href="/teacherlogin" className="btn btn-primary">Click as teacher</a>
          </div>
        </div>
        <div className="card" style={{ maxWidth: "320px" }}>
          <div className="card-body">
            <h4 className="card-title">Admin Access</h4>
            <p className="card-text">For administrators, this is where you can manage all aspects of the student management system.</p>
            <a href="#" className="btn btn-primary">Click as admin</a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;