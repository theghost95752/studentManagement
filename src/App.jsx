import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './server/pages/Home'
import './App.css'
import StudentLogin from './server/pages/StudentLogin'
import StudentProfile from './server/pages/StudentProfile'
import TeacherLogin from './server/pages/TeacherLogin'
import TeacherProfile from './server/pages/TeacherProfile'

function App() {
  return (
    <div className="app">
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/studentlogin" element={<StudentLogin />} />
          <Route path="/studentprofile/:id" element={<StudentProfile />} />
          <Route path="/teacherlogin" element={<TeacherLogin />} />
          <Route path="/teacherprofile/:teacher_id" element={<TeacherProfile />} />
        </Routes>
      </Router>
    </div>
  )
}

export default App
