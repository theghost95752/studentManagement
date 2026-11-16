import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Navbar from "./Navbar";
import "./Home.css";

const API_URL = "http://localhost:5000";

async function fetchStudentData(path, token) {
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

function StudentProfile() {
    const { id } = useParams();
    const [student, setStudent] = useState(null);
    const [assignments, setAssignments] = useState([]);
    const [fees, setFees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const token = localStorage.getItem("token");

    useEffect(() => {
        let cancelled = false;

        async function loadProfile() {
            if (!id || !token) {
                setError("Please log in to view your student profile.");
                setLoading(false);
                return;
            }

            setLoading(true);
            setError("");

            try {
                const [studentData, feeData, assignmentData] = await Promise.all([
                    fetchStudentData(`/students/${id}`, token),
                    fetchStudentData(`/students/${id}/fees`, token),
                    fetchStudentData(`/students/${id}/assignments`, token),
                ]);

                if (!cancelled) {
                    setStudent(studentData);
                    setFees(feeData);
                    setAssignments(assignmentData);
                }
            } catch (requestError) {
                if (!cancelled) {
                    setError(requestError.message);
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
    }, [id, token]);

    if (loading) {
        return <p className="container mt-4">Loading student profile...</p>;
    }

    if (error) {
        return (
            <div className="container mt-4">
                <div className="alert alert-danger" role="alert">{error}</div>
                {!token && <Link to="/studentlogin">Go to student login</Link>}
            </div>
        );
    }

    const outstandingBalance = fees
        .filter((fee) => fee.status?.toLowerCase() !== "paid")
        .reduce((total, fee) => total + Number(fee.amount || 0), 0);

    return (
        <main className="container mt-4">
            <Navbar />
            <h1>Student Profile</h1>
            <div className="profile-details">
                <section className="mt-4">
                    <h2>Student Details</h2>
                    <p><strong>First Name:</strong> {student.first_name}</p>
                    <p><strong>Last Name:</strong> {student.last_name}</p>
                    <p><strong>Email:</strong> {student.email}</p>
                    <p><strong>Date of entry:</strong> {new Date(student.created_at).toLocaleDateString()}</p>
                </section>

                <section className="mt-4">
                    <h2>Fees</h2>
                    <p><strong>Outstanding balance:</strong> {outstandingBalance.toFixed(2)}</p>
                    {fees.length > 0 ? (
                        <ul className="list-group">
                            {fees.map((fee) => (
                                <li className="list-group-item" key={fee.id}>
                                    <p><strong>Amount:</strong> {Number(fee.amount).toFixed(2)}</p>
                                    <p><strong>Due Date:</strong> {new Date(fee.due_date).toLocaleDateString()}</p>
                                    <p><strong>Status:</strong> {fee.status}</p>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p>No fees found.</p>
                    )}
                </section>
            </div>

            <section className="mt-4">
                <h2>Assignments</h2>
                {assignments.length > 0 ? (
                    <ul className="list-group">
                        {assignments.map((assignment) => (
                            <li className="list-group-item" key={assignment.id}>
                                <p><strong>Title:</strong> {assignment.title}</p>
                                <p><strong>Description:</strong> {assignment.description || "No description"}</p>
                                <p><strong>Due Date:</strong> {new Date(assignment.due_date).toLocaleDateString()}</p>
                                <p><strong>Marks:</strong> {assignment.marks}</p>
                                {assignment.file_url && (
                                    <p>
                                        <a href={assignment.file_url} target="_blank" rel="noreferrer">
                                            View assignment file
                                        </a>
                                    </p>
                                )}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>No assignments found.</p>
                )}
            </section>
        </main>
    );
}

export default StudentProfile;
