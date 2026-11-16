import { useState } from "react";
import { Link } from "react-router-dom";
import "./Home.css";

function Navbar() {
    return (
        <nav class="navbar navbar-expand-lg navbar-light bg-light">
            <div class="container-fluid">
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <a class="nav-link active" aria-current="page" href="/">Home</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/studentlogin">Students login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/teacherlogin">Teachers login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/adminlogin">Admin login</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    )
}

export default Navbar;