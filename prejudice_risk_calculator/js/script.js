// Legal Prejudice Risk Calculator
document.addEventListener('DOMContentLoaded', function() {
    // Tab Navigation
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Add active class to clicked button and corresponding pane
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Next and Previous Button Navigation
    const nextButtons = document.querySelectorAll('.next-btn');
    const prevButtons = document.querySelectorAll('.prev-btn');
    
    nextButtons.forEach(button => {
        button.addEventListener('click', () => {
            const nextTabId = button.getAttribute('data-next');
            
            // Remove active class from all buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Add active class to next tab button and pane
            document.querySelector(`.tab-btn[data-tab="${nextTabId}"]`).classList.add('active');
            document.getElementById(nextTabId).classList.add('active');
        });
    });
    
    prevButtons.forEach(button => {
        button.addEventListener('click', () => {
            const prevTabId = button.getAttribute('data-prev');
            
            // Remove active class from all buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Add active class to previous tab button and pane
            document.querySelector(`.tab-btn[data-tab="${prevTabId}"]`).classList.add('active');
            document.getElementById(prevTabId).classList.add('active');
        });
    });
    
    // Set current date as default for assessment date
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('assessment-date').value = today;
    
    // Calculate Results Button
    const calculateBtn = document.getElementById('calculate-btn');
    calculateBtn.addEventListener('click', calculateResults);
    
    // Save PDF Button
    const savePdfBtn = document.getElementById('save-pdf-btn');
    savePdfBtn.addEventListener('click', () => {
        alert('PDF generation would be implemented here. This would require a PDF generation library like jsPDF or a server-side solution.');
    });
    
    // Reset Form Button
    const resetFormBtn = document.getElementById('reset-form-btn');
    resetFormBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to reset the entire form? All entered data will be lost.')) {
            resetForm();
        }
    });
    
    // Initialize Risk Matrix Visualization
    initializeRiskMatrix();
});

// Factor data structure
const factorGroups = {
    relationship: {
        name: "Relationship-Based",
        factors: [
            { id: "financial-direct", name: "Direct financial interest" },
            { id: "financial-indirect", name: "Indirect financial interest" },
            { id: "relationship-family", name: "Family relationship" },
            { id: "relationship-social", name: "Social/professional relationship" },
            { id: "political-contributions", name: "Political contributions" },
            { id: "ideological-advocacy", name: "Prior advocacy on disputed issue" }
        ]
    },
    conduct: {
        name: "Conduct-Based",
        factors: [
            { id: "statements-disparaging", name: "Disparaging remarks" },
            { id: "statements-prejudgment", name: "Expressions indicating prejudgment" },
            { id: "rulings-onesided", name: "One-sided evidentiary rulings" },
            { id: "rulings-unequal", name: "Unequal allocation of time/resources" },
            { id: "extrajudicial-public", name: "Public comments on pending case" },
            { id: "extrajudicial-media", name: "Media interviews/social media posts" }
        ]
    },
    contextual: {
        name: "Contextual",
        factors: [
            { id: "historical-consistent", name: "Consistent rulings favoring similar parties" },
            { id: "historical-prior", name: "Prior reversal for bias" },
            { id: "procedural-deviation", name: "Deviation from standard procedures" },
            { id: "procedural-reasoning", name: "Failure to provide reasoning" },
            { id: "external-public", name: "High-profile case with public pressure" },
            { id: "external-political", name: "Political implications for judge" }
        ]
    }
};

// Calculate risk scores and update results
function calculateResults() {
    // Get case information
    const caseName = document.getElementById('case-name').value || 'Unnamed Case';
    const judgeName = document.getElementById('judge-name').value || 'Unnamed Judge';
    const assessmentDate = document.getElementById('assessment-date').value;
    const assessorName = document.getElementById('assessor-name').value || 'Unnamed Assessor';
    
    // Calculate scores for each category
    const scores = {
        relationship: calculateCategoryScore('relationship'),
        conduct: calculateCategoryScore('conduct'),
        contextual: calculateCategoryScore('contextual')
    };
    
    // Calculate overall risk score (average of all factors with values)
    let totalScore = 0;
    let factorCount = 0;
    
    for (const category in scores) {
        if (scores[category].count > 0) {
            totalScore += scores[category].score;
            factorCount += scores[category].count;
        }
    }
    
    const overallScore = factorCount > 0 ? Math.round(totalScore / factorCount) : 0;
    
    // Determine risk level
    let riskLevel;
    if (overallScore >= 20) {
        riskLevel = "Critical";
    } else if (overallScore >= 15) {
        riskLevel = "High";
    } else if (overallScore >= 8) {
        riskLevel = "Medium";
    } else {
        riskLevel = "Low";
    }
    
    // Update results display
    document.getElementById('overall-risk-score').querySelector('.score-value').textContent = overallScore;
    
    const riskLevelElement = document.getElementById('risk-level');
    riskLevelElement.querySelector('.level-value').textContent = riskLevel;
    riskLevelElement.setAttribute('data-level', riskLevel);
    
    document.getElementById('relationship-score').textContent = 
        scores.relationship.count > 0 ? scores.relationship.score : 'N/A';
    document.getElementById('conduct-score').textContent = 
        scores.conduct.count > 0 ? scores.conduct.score : 'N/A';
    document.getElementById('contextual-score').textContent = 
        scores.contextual.count > 0 ? scores.contextual.score : 'N/A';
    
    // Update risk matrix visualization
    updateRiskMatrix(getHighRiskFactors());
    
    // Generate recommendations based on risk level
    generateRecommendations(riskLevel, overallScore);
    
    // Display high risk factors
    displayHighRiskFactors(getHighRiskFactors());
}

// Calculate score for a specific category
function calculateCategoryScore(category) {
    let totalScore = 0;
    let factorCount = 0;
    
    factorGroups[category].factors.forEach(factor => {
        const likelihoodRadio = document.querySelector(`input[name="${factor.id}-likelihood"]:checked`);
        const impactRadio = document.querySelector(`input[name="${factor.id}-impact"]:checked`);
        
        if (likelihoodRadio && impactRadio) {
            const likelihood = parseInt(likelihoodRadio.value);
            const impact = parseInt(impactRadio.value);
            const factorScore = likelihood * impact;
            totalScore += factorScore;
            factorCount++;
        }
    });
    
    return {
        score: factorCount > 0 ? Math.round(totalScore / factorCount) : 0,
        count: factorCount
    };
}

// Get all factors with their scores
function getAllFactorScores() {
    const factorScores = [];
    
    for (const categoryKey in factorGroups) {
        const category = factorGroups[categoryKey];
        
        category.factors.forEach(factor => {
            const likelihoodRadio = document.querySelector(`input[name="${factor.id}-likelihood"]:checked`);
            const impactRadio = document.querySelector(`input[name="${factor.id}-impact"]:checked`);
            
            if (likelihoodRadio && impactRadio) {
                const likelihood = parseInt(likelihoodRadio.value);
                const impact = parseInt(impactRadio.value);
                const score = likelihood * impact;
                
                factorScores.push({
                    id: factor.id,
                    name: factor.name,
                    category: category.name,
                    likelihood: likelihood,
                    impact: impact,
                    score: score,
                    notes: document.getElementById(`${factor.id}-notes`).value
                });
            }
        });
    }
    
    // Sort by score (highest first)
    factorScores.sort((a, b) => b.score - a.score);
    
    return factorScores;
}

// Get high risk factors (score >= 15)
function getHighRiskFactors() {
    return getAllFactorScores().filter(factor => factor.score >= 15);
}

// Display high risk factors
function displayHighRiskFactors(highRiskFactors) {
    const container = document.getElementById('high-risk-factors');
    container.innerHTML = '';
    
    if (highRiskFactors.length === 0) {
        container.innerHTML = '<p>No high-risk factors identified.</p>';
        return;
    }
    
    highRiskFactors.forEach(factor => {
        const factorElement = document.createElement('div');
        factorElement.className = 'high-risk-factor-item';
        
        factorElement.innerHTML = `
            <h4>${factor.name} (${factor.category})</h4>
            <p><strong>Risk Score:</strong> ${factor.score} (Likelihood: ${factor.likelihood}, Impact: ${factor.impact})</p>
            ${factor.notes ? `<p><strong>Notes:</strong> ${factor.notes}</p>` : ''}
        `;
        
        container.appendChild(factorElement);
    });
}

// Generate recommendations based on risk level
function generateRecommendations(riskLevel, score) {
    const container = document.getElementById('recommendations-container');
    container.innerHTML = '';
    
    let recommendations = '';
    
    switch (riskLevel) {
        case 'Critical':
            recommendations = `
                <p>With a Critical risk score of ${score}, immediate formal action is strongly recommended:</p>
                <ul>
                    <li>File a formal motion to recuse/disqualify immediately</li>
                    <li>Consider motion to stay proceedings pending resolution</li>
                    <li>Prepare detailed affidavit documenting all prejudice factors</li>
                    <li>Consult with appellate counsel regarding potential mandamus relief</li>
                    <li>Implement comprehensive documentation protocol for all interactions</li>
                    <li>Prepare client for potential media interest and case delays</li>
                </ul>
                <p>Refer to the Practical Guide Section III.A for detailed guidance on Critical risk responses.</p>
            `;
            break;
            
        case 'High':
            recommendations = `
                <p>With a High risk score of ${score}, urgent action is recommended:</p>
                <ul>
                    <li>File a motion to recuse/disqualify or for disclosure of potential conflicts</li>
                    <li>Consider requesting a hearing on prejudice concerns</li>
                    <li>Develop detailed documentation of all prejudice indicators</li>
                    <li>Implement strategic adjustments to case presentation</li>
                    <li>Prepare record for potential appeal on prejudice grounds</li>
                </ul>
                <p>Refer to the Practical Guide Section III.B for detailed guidance on High risk responses.</p>
            `;
            break;
            
        case 'Medium':
            recommendations = `
                <p>With a Medium risk score of ${score}, prompt strategic response is recommended:</p>
                <ul>
                    <li>Enhance documentation of potential prejudice indicators</li>
                    <li>Consider strategic motion practice to test for bias</li>
                    <li>Modify case presentation approach to mitigate prejudice impact</li>
                    <li>Request written rulings for significant decisions</li>
                    <li>Preserve all procedural objections related to potential prejudice</li>
                </ul>
                <p>Refer to the Practical Guide Section III.C for detailed guidance on Medium risk responses.</p>
            `;
            break;
            
        case 'Low':
            recommendations = `
                <p>With a Low risk score of ${score}, monitoring is recommended:</p>
                <ul>
                    <li>Document potential prejudice indicators as they arise</li>
                    <li>Track rulings for emerging patterns</li>
                    <li>Compare treatment with opposing party</li>
                    <li>Maintain professional conduct to avoid escalation</li>
                    <li>Reassess risk level periodically throughout proceedings</li>
                </ul>
                <p>Refer to the Practical Guide Section III.D for detailed guidance on Low risk responses.</p>
            `;
            break;
            
        default:
            recommendations = '<p>Please complete the assessment to receive recommendations.</p>';
    }
    
    container.innerHTML = recommendations;
}

// Initialize risk matrix visualization
function initializeRiskMatrix() {
    const matrixContainer = document.getElementById('risk-matrix-visualization');
    
    // Create basic matrix structure
    matrixContainer.innerHTML = `
        <div style="width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <div style="font-size: 1.2rem; margin-bottom: 20px;">Complete the assessment to generate the risk matrix visualization</div>
            <div style="width: 300px; height: 300px; position: relative; border: 1px solid #ddd;">
                <!-- Matrix will be populated here -->
            </div>
        </div>
    `;
}

// Update risk matrix with factor data
function updateRiskMatrix(highRiskFactors) {
    const matrixContainer = document.getElementById('risk-matrix-visualization');
    
    // Create matrix HTML
    let matrixHTML = `
        <div style="width: 100%; height: 100%; display: flex; flex-direction: column;">
            <div style="text-align: center; margin-bottom: 20px;">Risk Matrix Visualization</div>
            <div style="flex-grow: 1; display: flex; flex-direction: column;">
                <div style="display: flex; height: 100%;">
                    <!-- Y-axis label -->
                    <div style="writing-mode: vertical-rl; transform: rotate(180deg); text-align: center; padding: 10px;">
                        Impact
                    </div>
                    
                    <!-- Matrix grid -->
                    <div style="flex-grow: 1; display: flex; flex-direction: column; border: 1px solid #ddd;">
                        <!-- Row 5 (highest impact) -->
                        <div style="flex-grow: 1; display: flex;">
                            <div style="width: 20%; height: 100%; background-color: #FFF59D; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-1-5"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFCC80; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-2-5"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFAB91; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-3-5"></div>
                            <div style="width: 20%; height: 100%; background-color: #FF8A65; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-4-5"></div>
                            <div style="width: 20%; height: 100%; background-color: #FF5252; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-5-5"></div>
                        </div>
                        
                        <!-- Row 4 -->
                        <div style="flex-grow: 1; display: flex;">
                            <div style="width: 20%; height: 100%; background-color: #FFF9C4; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-1-4"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFE0B2; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-2-4"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFCCBC; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-3-4"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFAB91; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-4-4"></div>
                            <div style="width: 20%; height: 100%; background-color: #FF8A65; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-5-4"></div>
                        </div>
                        
                        <!-- Row 3 -->
                        <div style="flex-grow: 1; display: flex;">
                            <div style="width: 20%; height: 100%; background-color: #FFFDE7; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-1-3"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFF9C4; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-2-3"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFE0B2; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-3-3"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFCCBC; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-4-3"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFAB91; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-5-3"></div>
                        </div>
                        
                        <!-- Row 2 -->
                        <div style="flex-grow: 1; display: flex;">
                            <div style="width: 20%; height: 100%; background-color: #F5F5F5; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-1-2"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFFDE7; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-2-2"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFF9C4; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-3-2"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFE0B2; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-4-2"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFCCBC; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-5-2"></div>
                        </div>
                        
                        <!-- Row 1 (lowest impact) -->
                        <div style="flex-grow: 1; display: flex;">
                            <div style="width: 20%; height: 100%; background-color: #F5F5F5; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-1-1"></div>
                            <div style="width: 20%; height: 100%; background-color: #F5F5F5; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-2-1"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFFDE7; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-3-1"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFF9C4; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-4-1"></div>
                            <div style="width: 20%; height: 100%; background-color: #FFE0B2; border: 1px solid #ddd; display: flex; justify-content: center; align-items: center;" id="cell-5-1"></div>
                        </div>
                    </div>
                </div>
                
                <!-- X-axis label -->
                <div style="text-align: center; padding: 10px;">Likelihood</div>
                
                <!-- Legend -->
                <div style="display: flex; justify-content: center; margin-top: 20px;">
                    <div style="margin: 0 10px;"><span style="display: inline-block; width: 20px; height: 20px; background-color: #F5F5F5; border: 1px solid #ddd;"></span> Low (1-7)</div>
                    <div style="margin: 0 10px;"><span style="display: inline-block; width: 20px; height: 20px; background-color: #FFF9C4; border: 1px solid #ddd;"></span> Medium (8-14)</div>
                    <div style="margin: 0 10px;"><span style="display: inline-block; width: 20px; height: 20px; background-color: #FFAB91; border: 1px solid #ddd;"></span> High (15-19)</div>
                    <div style="margin: 0 10px;"><span style="display: inline-block; width: 20px; height: 20px; background-color: #FF5252; border: 1px solid #ddd;"></span> Critical (20-25)</div>
                </div>
            </div>
        </div>
    `;
    
    matrixContainer.innerHTML = matrixHTML;
    
    // Plot factors on the matrix
    const allFactors = getAllFactorScores();
    
    allFactors.forEach(factor => {
        const cellId = `cell-${factor.likelihood}-${factor.impact}`;
        const cell = document.getElementById(cellId);
        
        if (cell) {
            // Create a dot representing the factor
            const dot = document.createElement('div');
            dot.style.width = '10px';
            dot.style.height = '10px';
            dot.style.borderRadius = '50%';
            dot.style.backgroundColor = '#333';
            dot.style.margin = '2px';
            dot.title = `${factor.name} (${factor.category}): Score ${factor.score}`;
            
            cell.appendChild(dot);
        }
    });
}

// Reset the entire form
function resetForm() {
    // Reset all radio buttons
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.checked = false;
    });
    
    // Reset all textareas
    document.querySelectorAll('textarea').forEach(textarea => {
        textarea.value = '';
    });
    
    // Reset case info
    document.getElementById('case-name').value = '';
    document.getElementById('judge-name').value = '';
    document.getElementById('assessor-name').value = '';
    
    // Reset date to current date
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('assessment-date').value = today;
    
    // Reset results
    document.getElementById('overall-risk-score').querySelector('.score-value').textContent = '--';
    document.getElementById('risk-level').querySelector('.level-value').textContent = '--';
    document.getElementById('relationship-score').textContent = '--';
    document.getElementById('conduct-score').textContent = '--';
    document.getElementById('contextual-score').textContent = '--';
    
    // Reset recommendations
    document.getElementById('recommendations-container').innerHTML = '<p>Complete the assessment to receive recommendations.</p>';
    
    // Reset high risk factors
    document.getElementById('high-risk-factors').innerHTML = '<p>Complete the assessment to identify high-risk factors.</p>';
    
    // Reset risk matrix
    initializeRiskMatrix();
    
    // Return to first tab
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    document.querySelector('.tab-btn[data-tab="relationship"]').classList.add('active');
    document.getElementById('relationship').classList.add('active');
}