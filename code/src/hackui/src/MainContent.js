import React, { useState } from 'react';
import './App.css';
import Stats from './Stats';
import KeyFeatures from './KeyFeatures';
import HowItWorks from './HowItWorks';
import RiskFactors from './RiskFactors';
import {  useNavigate } from "react-router-dom";

const steps = [
    "Step 1: Initialize Project",
    "Step 2: Install Dependencies",
    "Step 3: Setup Tailwind",
    "Step 4: Build UI Components",
    "Step 5: Test & Deploy",
];

function MainContent() {
    const [showManualEntry, setShowManualEntry] = useState(false);
    const [file, setFile] = useState(null);
    const [text, setText] = useState("");
    const navigate = useNavigate()

    // Handle File Upload
    const handleFileChange = (event) => {
        const uploadedFile = event.target.files[0];
        if (uploadedFile) {
            setFile(uploadedFile);
        }
    };

    // Remove Uploaded File
    const clearFile = () => {
        setFile(null);
    };

    // Process Data (Can be expanded based on your use case)
    const processData = async () => {
        if (showManualEntry) {
            alert(`Processing Manual Entry:\n${text}`);
            return;
        }

        if (!file) {
            alert("No file provided!");
            return;
        }

        navigate("/stepper");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("http://localhost:8002/upload", {
                method: "POST",
                body: formData,
            });

            const result = await response.json();

            if (response.ok) {
                console.log(`File processed successfully! Output file: ${result.output_json}`);
                console.log(result.output_json)
            } else {
                console.log(`Error: ${result.error}`);
            }
        } catch (error) {
            console.error("Error uploading file:", error);
            alert("Failed to process file. Please try again.");
        }
    };

    return (
        <div className="App">
            <header className="header">
                <img src={`/header.png`} alt="Header" className="header-image" />
            </header>

            <div className='main-body'>
                <div style={{ width: "80%" }}>
                    <div style={{textAlign:"center"}}>
                    <h1 style={{ marginTop: "15px" }}>RiskWise</h1>
                    <p>
                        Automated entity extraction, classification, and risk scoring to empower
                        smarter financial decisions.
                    </p>
                    </div>

                    <div className='cs'>
                        <div className='left-conta'>
                            <KeyFeatures />
                        </div>
                        <div className='right-conta'>
                            <HowItWorks />
                        </div>
                    </div>
                    <Stats />
                    <RiskFactors />

                    <div style={{ textAlign: "center" }}>
                        <button
                            onClick={() => navigate("/input")}
                            className={`input-button active`}
                            style={{ width: "40%", marginTop: "15px", marginLeft: "0", marginBottom: "50px" }}
                        >
                            Get Started
                        </button>
                    </div>

                </div>
            </div>
        </div>


    );
}

export default MainContent;
