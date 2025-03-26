import React, { useState } from "react";
import GaugeChart from "react-gauge-chart";
import Accordian from "./Accordian";
import StepperComponent from "./StepStatus";

const transactions = [
    {
        transactionId: "TXN001",
        extractedEntities: ["Acme Corporation", "Sovco Capital Partners"],
        entityTypes: ["Corporation", "Corporation"],
        riskScore: 0.35,
        supportingEvidence: ["OpenCorporates", "Company Website"],
        confidenceScore: 0.95,
        reason:
            "SovCo Capital Partners is not on the sanctions list but is an entity of interest. It is owned by Russian businessmen and related to Socombank PJSC, a sanctioned entity.",
    },
    {
        transactionId: "TXN002",
        extractedEntities: ["XYZ Holdings", "Global Bank Ltd"],
        entityTypes: ["Holding", "Bank"],
        riskScore: 0.72,
        supportingEvidence: ["Financial Reports", "Banking Records"],
        confidenceScore: 0.87,
        reason:
            "XYZ Holdings has been flagged in multiple fraud reports and is under investigation for money laundering.",
    },
    {
        transactionId: "TXN003",
        extractedEntities: ["Tech Ventures Inc.", "Credit Solutions"],
        entityTypes: ["Tech Company", "Credit Agency"],
        riskScore: 0.12,
        supportingEvidence: ["Government Registrations", "Financial Reports"],
        confidenceScore: 0.98,
        reason: "No negative indicators found. The transaction appears to be low risk.",
    },
];

const RiskReport = () => {
    const [currentIndex, setCurrentIndex] = useState(0);

    const handleNext = () => {
        if (currentIndex < transactions.length - 1) {
            setCurrentIndex(currentIndex + 1);
        }
    };

    const handlePrevious = () => {
        if (currentIndex > 0) {
            setCurrentIndex(currentIndex - 1);
        }
    };

    const transaction = transactions[currentIndex];

    return (
        <div className="risk-report">
            <header className="header">
                <img src={`/header.png`} alt="Header" className="header-image" />
            </header>

            <div className="main-body">
                <div className="header-content">
                    <h1 style={{ marginTop: "15px" }}>Risk Report</h1>
                    <p>Automated entity extraction, classification, and risk scoring to empower smarter financial decisions.</p>
                </div>
                <StepperComponent />

                <div className="cl">
                    <div className="left-cont">
                        <div className="txid"><div>Transaction ID: {transaction.transactionId}</div>
                            <div className="navigation-buttons" style={{ display: "flex", width: "30%" }}>
                                <button onClick={handlePrevious} disabled={currentIndex === 0} className={`input-button active prev`}>&lt;</button>
                                {/* <div>{`Transaction ${currentIndex + 1} of ${transactions.length}`}</div> */}
                                <button onClick={handleNext} disabled={currentIndex === transactions.length - 1} className={`input-button active next`}>&gt;</button>
                            </div></div>
                        <RiskScoreIndicator score={transaction.riskScore} />
                        <ConfidenceScoreBar score={transaction.confidenceScore} />
                    </div>
                    <div className="right-cont">
                        <Accordian transaction={transaction} />
                    </div>
                </div>


            </div>
        </div>
    );
};

export default RiskReport;



const RiskScoreIndicator = ({ score }) => {
    let riskLevel;

    if (score < 0.3) {
        riskLevel = "Low";
    } else if (score < 0.75) {
        riskLevel = "Medium";
    } else {
        riskLevel = "High";
    }

    return (
        <div className="risk-score-container">
            <h2 className="section-title">Risk Score Indicator</h2>
            <div className="legend">
                <div className="legend-div"><div className="legend-color one" style={{ backgroundColor: "#5BE12C" }}></div> Low</div>
                <div className="legend-div"><div className="legend-color two" style={{ backgroundColor: "#F5CD19" }}></div> Medium</div>
                <div className="legend-div"><div className="legend-color three" style={{ backgroundColor: "#EA4228" }}></div> High</div>
            </div>
            <GaugeChart
                id="gauge-chart"
                nrOfLevels={30}
                arcsLength={[0.3, 0.45, 0.25]}
                colors={['#5BE12C', '#F5CD19', '#CD1309']}
                percent={score}
                arcWidth={0.3}
                needleColor="grey"
                arcPadding={0.1}
            />
            <div className="risk-level">
                <span className="risk-label">{riskLevel} Risk</span>
            </div>
        </div>
    );
};

const ConfidenceScoreBar = ({ score }) => {
    let barColor;

    if (score < 0.5) {
        barColor = "#CD1309"; // Low confidence
    } else if (score < 0.8) {
        barColor = "#F5CD19"; // Medium confidence
    } else {
        barColor = "#5BE12C"; // High confidence
    }

    return (
        <div className="confidence-score-container">
            <h2 className="section-title">Confidence Score</h2>
            <div className="legend">
                <div className="legend-div"><div className="legend-color one" style={{ backgroundColor: "#5BE12C" }}></div> Low</div>
                <div className="legend-div"><div className="legend-color two" style={{ backgroundColor: "#F5CD19" }}></div> Medium</div>
                <div className="legend-div"><div className="legend-color three" style={{ backgroundColor: "#EA4228" }}></div> High</div>
            </div>
            <div className="progress-bar">
                <div
                    className="progress-fill"
                    style={{ width: `${score * 100}%`, backgroundColor: barColor }}
                ></div>
            </div>
            <div className="risk-level">
                <span className="risk-label"> {score * 100}% Confident</span>
            </div>
        </div>
    );
};

