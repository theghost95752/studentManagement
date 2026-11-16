import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Navbar from "./Navbar";
import "./Home.css";

const API_URL = "http://localhost:5000";

async function fetchTeacherData(path, token) {
    const response = await fetch(`${API_URL}${path}`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || `Request failed (${response.status})`);
    }

    return data;
}

function TeacherProfile() {
    const { teacher_id } = useParams();
    const [teacherData, setTeacherData] = useState(null);
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let cancelled = false;

        async function loadProfile() {
            try {
                if (!teacher_id) {
                    throw new Error("Teacher ID is missing.");
                }

                const token = localStorage.getItem("token");
                if (!token) {
                    throw new Error("Please log in to view the teacher profile.");
                }

                const [teacher, teacherCourses] = await Promise.all([
                    fetchTeacherData(`/teachers/${teacher_id}`, token),
                    fetchTeacherData(`/teachers/${teacher_id}/courses`, token),
                ]);

                if (!cancelled) {
                    setTeacherData(teacher);
                    setCourses(teacherCourses);
                }
            } catch (err) {
                if (!cancelled) {
                    setError(err instanceof Error ? err.message : "Unable to load teacher data.");
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }

        loadProfile();
        return () => {
            cancelled = true;
        };
    }, [teacher_id]);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    if (!teacherData) return <div>Teacher not found</div>;

    return (
        <div className="container mt-4">
            <Navbar />
            <h1>Teacher Profile</h1>
            <p><strong>Name:</strong> {teacherData.first_name} {teacherData.last_name}</p>
            <p><strong>Email:</strong> {teacherData.email}</p>

            <h2>Courses you teach</h2>
            {courses.length === 0 ? (
                <p>You are not assigned to any courses yet.</p>
            ) : (
                courses.map((course) => (
                    <section key={course.id} className="mb-4">
                        <h3>{course.name}</h3>
                        {course.description && <p>{course.description}</p>}

                        <h4>Enrolled students</h4>
                        {course.students.length === 0 ? (
                            <p>No students are enrolled in this course.</p>
                        ) : (
                            <ul>
                                {course.students.map((student) => (
                                    <li key={student.id}>
                                        {student.first_name} {student.last_name} ({student.email})
                                    </li>
                                ))}
                            </ul>
                        )}

                        <h4>Assignments</h4>
                        {course.assignments.length === 0 ? (
                            <p>No assignments have been uploaded for this course.</p>
                        ) : (
                            <ul>
                                {course.assignments.map((assignment) => (
                                    <li key={assignment.id}>
                                        <strong>{assignment.title}</strong>
                                        {assignment.description && <p>{assignment.description}</p>}
                                        <h5> 
                                            Submitted by: {assignment.student.first_name} {assignment.student.last_name}
                                        </h5>
                                        <p>Due: {assignment.due_date}</p>
                                        <p>Marks: {assignment.marks}</p>
                                        {assignment.file_url && <p>File: {assignment.file_url}</p>}
                                    </li>
                                ))}
                            </ul>
                        )}
                    </section>
                ))
            )}
        </div>
    );
}

export default TeacherProfile;
