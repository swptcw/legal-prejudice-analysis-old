/**
 * Legal Prejudice Risk Calculator - Enhanced Version
 * Main JavaScript functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    const assessmentData = {
        caseInfo: {},
        relationshipFactors: {},
        conductFactors: {},
        contextualFactors: {},
        results: {
            riskScore: 0,
            riskLevel: 'Not Calculated',
            confidenceScore: 0,
            factorCounts: {
                total: 0,
                critical: 0,
                highImpact: 0
            },
            recommendations: []
        }
    };
    
    // DOM Elements
    const progressBar = document.getElementById('assessment-progress');
    const progressSteps = document.querySelectorAll('.progress-step');
    const sections = document.querySelectorAll('.calculator-section');
    const nextButtons = document.querySelectorAll('.next-section');
    const prevButtons = document.querySelectorAll('.prev-section');
    const calculateButton = document.querySelector('.calculate-btn');
    const toggleInputs = document.querySelectorAll('.toggle input[type="radio"]');
    const ratingItems = document.querySelectorAll('.rating-item');
    const vizTabs = document.querySelectorAll('.viz-tab');
    const vizPanels = document.querySelectorAll('.viz-panel');
    const loginBtn = document.querySelector('.login-btn');
    const loginModal = document.getElementById('login-modal');
    const closeModal = document.querySelector('.close-modal');
    const modalTabs = document.querySelectorAll('.modal-tab');
    const modalPanels = document.querySelectorAll('.modal-panel');
    const saveAssessmentBtn = document.getElementById('save-assessment-btn');
    const exportPdfBtn = document.getElementById('export-pdf-btn');
    const startNewBtn = document.getElementById('start-new-btn');
    
    // Initialize the calculator
    initCalculator();
    
    /**
     * Initialize the calculator functionality
     */
    function initCalculator() {
        // Set up event listeners
        setupNavigationListeners();
        setupToggleListeners();
        setupRatingListeners();
        setupVisualizationTabs();
        setupModalListeners();
        setupActionButtons();
        
        // Initialize header scroll effect
        initHeaderScroll();
    }
    
    /**
     * Set up navigation between sections
     */
    function setupNavigationListeners() {
        // Next section buttons
        nextButtons.forEach(button => {
            button.addEventListener('click', function() {
                const currentSection = this.closest('.calculator-section');
                const nextSectionId = this.dataset.next;
                
                // Validate current section if needed
                if (validateSection(currentSection.id)) {
                    // Save data from current section
                    saveCurrentSectionData(currentSection.id);
                    
                    // Navigate to next section
                    navigateToSection(nextSectionId);
                }
            });
        });
        
        // Previous section buttons
        prevButtons.forEach(button => {
            button.addEventListener('click', function() {
                const prevSectionId = this.dataset.prev;
                navigateToSection(prevSectionId);
            });
        });
        
        // Calculate button
        if (calculateButton) {
            calculateButton.addEventListener('click', function() {
                const currentSection = this.closest('.calculator-section');
                
                // Validate current section
                if (validateSection(currentSection.id)) {
                    // Save data from current section
                    saveCurrentSectionData(currentSection.id);
                    
                    // Calculate results
                    calculateResults();
                    
                    // Navigate to results section
                    navigateToSection('results');
                }
            });
        }
    }
    
    /**
     * Navigate to a specific section
     * @param {string} sectionId - The ID of the section to navigate to
     */
    function navigateToSection(sectionId) {
        // Hide all sections
        sections.forEach(section => {
            section.classList.remove('active');
        });
        
        // Show the target section
        const targetSection = document.getElementById(`${sectionId}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
        }
        
        // Update progress bar and steps
        updateProgress(sectionId);
    }
    
    /**
     * Update the progress bar and steps
     * @param {string} currentSectionId - The ID of the current section
     */
    function updateProgress(currentSectionId) {
        const steps = ['case-info', 'relationship-factors', 'conduct-factors', 'contextual-factors', 'results'];
        const currentIndex = steps.indexOf(currentSectionId);
        
        if (currentIndex >= 0) {
            // Update progress bar
            const progressPercentage = (currentIndex / (steps.length - 1)) * 100;
            progressBar.style.width = `${progressPercentage}%`;
            
            // Update progress steps
            progressSteps.forEach((step, index) => {
                if (index <= currentIndex) {
                    step.classList.add('active');
                } else {
                    step.classList.remove('active');
                }
                
                if (index < currentIndex) {
                    step.classList.add('completed');
                } else {
                    step.classList.remove('completed');
                }
            });
        }
    }
    
    /**
     * Validate the current section
     * @param {string} sectionId - The ID of the section to validate
     * @returns {boolean} - Whether the section is valid
     */
    function validateSection(sectionId) {
        // For now, we'll just return true
        // In a real implementation, you would validate the inputs
        return true;
    }
    
    /**
     * Save data from the current section
     * @param {string} sectionId - The ID of the section to save data from
     */
    function saveCurrentSectionData(sectionId) {
        switch (sectionId) {
            case 'case-info':
                assessmentData.caseInfo = {
                    caseName: document.getElementById('case-name').value,
                    caseNumber: document.getElementById('case-number').value,
                    jurisdiction: document.getElementById('jurisdiction').value,
                    courtType: document.getElementById('court-type').value,
                    judgeName: document.getElementById('judge-name').value,
                    caseDescription: document.getElementById('case-description').value
                };
                break;
                
            case 'relationship-factors':
                assessmentData.relationshipFactors = collectFactorData('relationship-factors');
                break;
                
            case 'conduct-factors':
                assessmentData.conductFactors = collectFactorData('conduct-factors');
                break;
                
            case 'contextual-factors':
                assessmentData.contextualFactors = collectFactorData('contextual-factors');
                break;
        }
    }
    
    /**
     * Collect factor data from a section
     * @param {string} sectionId - The ID of the section to collect data from
     * @returns {Object} - The collected factor data
     */
    function collectFactorData(sectionId) {
        const factorData = {};
        const section = document.getElementById(`${sectionId}-section`);
        
        // Get all factor items in the section
        const factorItems = section.querySelectorAll('.factor-item');
        
        factorItems.forEach(item => {
            // Get the factor name from the radio input name
            const radioInput = item.querySelector('input[type="radio"]');
            if (radioInput) {
                const factorName = radioInput.name;
                const isPresent = item.querySelector(`input[name="${factorName}"]:checked`)?.value === 'yes';
                
                // If the factor is present, collect likelihood and impact ratings
                if (isPresent) {
                    const likelihoodRating = parseInt(item.querySelector(`#${factorName}-likelihood`).dataset.rating) || 0;
                    const impactRating = parseInt(item.querySelector(`#${factorName}-impact`).dataset.rating) || 0;
                    const notes = item.querySelector(`#${factorName}-notes`)?.value || '';
                    
                    factorData[factorName] = {
                        present: true,
                        likelihood: likelihoodRating,
                        impact: impactRating,
                        notes: notes
                    };
                } else {
                    factorData[factorName] = {
                        present: false
                    };
                }
            }
        });
        
        return factorData;
    }
    
    /**
     * Set up toggle input listeners
     */
    function setupToggleListeners() {
        toggleInputs.forEach(input => {
            input.addEventListener('change', function() {
                const factorItem = this.closest('.factor-item');
                const factorDetails = factorItem.querySelector('.factor-details');
                const factorName = this.name;
                
                if (this.value === 'yes' && factorDetails) {
                    factorDetails.style.display = 'block';
                } else if (factorDetails) {
                    factorDetails.style.display = 'none';
                    
                    // Reset ratings
                    const likelihoodRating = factorItem.querySelector(`#${factorName}-likelihood`);
                    const impactRating = factorItem.querySelector(`#${factorName}-impact`);
                    
                    if (likelihoodRating) {
                        likelihoodRating.dataset.rating = '0';
                        updateRatingDisplay(likelihoodRating);
                    }
                    
                    if (impactRating) {
                        impactRating.dataset.rating = '0';
                        updateRatingDisplay(impactRating);
                    }
                }
            });
        });
    }
    
    /**
     * Set up rating input listeners
     */
    function setupRatingListeners() {
        ratingItems.forEach(item => {
            item.addEventListener('click', function() {
                const rating = this.closest('.rating');
                const value = parseInt(this.dataset.value);
                
                // Update the rating value
                rating.dataset.rating = value;
                
                // Update the display
                updateRatingDisplay(rating);
            });
        });
    }
    
    /**
     * Update the rating display
     * @param {HTMLElement} rating - The rating element to update
     */
    function updateRatingDisplay(rating) {
        const value = parseInt(rating.dataset.rating);
        const items = rating.querySelectorAll('.rating-item');
        const label = rating.parentElement.querySelector('.rating-label');
        
        // Update the rating items
        items.forEach((item, index) => {
            const itemValue = parseInt(item.dataset.value);
            
            // Clear existing classes
            item.classList.remove('active');
            
            // Update the icon
            if (itemValue <= value) {
                item.classList.add('active');
                item.innerHTML = '<i class="fas fa-circle"></i>';
            } else {
                item.innerHTML = '<i class="far fa-circle"></i>';
            }
        });
        
        // Update the label
        if (label) {
            if (value === 0) {
                label.textContent = 'Not Selected';
            } else if (value === 1) {
                label.textContent = 'Very Low';
            } else if (value === 2) {
                label.textContent = 'Low';
            } else if (value === 3) {
                label.textContent = 'Medium';
            } else if (value === 4) {
                label.textContent = 'High';
            } else if (value === 5) {
                label.textContent = 'Very High';
            }
        }
    }
    
    /**
     * Set up visualization tabs
     */
    function setupVisualizationTabs() {
        vizTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const tabId = this.dataset.tab;
                
                // Update active tab
                vizTabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                // Show the corresponding panel
                vizPanels.forEach(panel => {
                    panel.classList.remove('active');
                });
                document.getElementById(`${tabId}-panel`).classList.add('active');
            });
        });
    }
    
    /**
     * Set up modal listeners
     */
    function setupModalListeners() {
        // Open modal
        if (loginBtn) {
            loginBtn.addEventListener('click', function(e) {
                e.preventDefault();
                loginModal.classList.add('active');
            });
        }
        
        // Close modal
        if (closeModal) {
            closeModal.addEventListener('click', function() {
                loginModal.classList.remove('active');
            });
        }
        
        // Close modal when clicking outside
        window.addEventListener('click', function(e) {
            if (e.target === loginModal) {
                loginModal.classList.remove('active');
            }
        });
        
        // Modal tabs
        modalTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const tabId = this.dataset.tab;
                
                // Update active tab
                modalTabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                // Show the corresponding panel
                modalPanels.forEach(panel => {
                    panel.classList.remove('active');
                });
                document.getElementById(`${tabId}-panel`).classList.add('active');
            });
        });
    }
    
    /**
     * Set up action buttons
     */
    function setupActionButtons() {
        // Save assessment button
        if (saveAssessmentBtn) {
            saveAssessmentBtn.addEventListener('click', function() {
                // Check if user is logged in
                const isLoggedIn = false; // This would be determined by your authentication system
                
                if (isLoggedIn) {
                    saveAssessment();
                } else {
                    // Show login modal
                    loginModal.classList.add('active');
                }
            });
        }
        
        // Export PDF button
        if (exportPdfBtn) {
            exportPdfBtn.addEventListener('click', function() {
                exportToPdf();
            });
        }
        
        // Start new button
        if (startNewBtn) {
            startNewBtn.addEventListener('click', function() {
                resetCalculator();
            });
        }
    }
    
    /**
     * Initialize header scroll effect
     */
    function initHeaderScroll() {
        const header = document.querySelector('.header');
        const scrollThreshold = 50;
        
        function handleScroll() {
            if (window.scrollY > scrollThreshold) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        }
        
        window.addEventListener('scroll', handleScroll);
        handleScroll(); // Check initial state
    }
    
    /**
     * Calculate the results based on the assessment data
     */
    function calculateResults() {
        // Combine all factors
        const allFactors = {
            ...assessmentData.relationshipFactors,
            ...assessmentData.conductFactors,
            ...assessmentData.contextualFactors
        };
        
        // Count factors
        let totalFactors = 0;
        let criticalFactors = 0;
        let highImpactFactors = 0;
        let totalRiskScore = 0;
        let maxPossibleScore = 0;
        let factorCount = 0;
        
        // Process each factor
        for (const factorName in allFactors) {
            const factor = allFactors[factorName];
            
            if (factor.present) {
                totalFactors++;
                
                // Calculate risk score for this factor
                const factorScore = factor.likelihood * factor.impact;
                totalRiskScore += factorScore;
                maxPossibleScore += 25; // Max possible is 5 * 5
                factorCount++;
                
                // Check if critical (both likelihood and impact are high)
                if (factor.likelihood >= 4 && factor.impact >= 4) {
                    criticalFactors++;
                }
                
                // Check if high impact
                if (factor.impact >= 4) {
                    highImpactFactors++;
                }
            }
        }
        
        // Calculate final risk score (0-100 scale)
        let finalRiskScore = 0;
        if (maxPossibleScore > 0) {
            finalRiskScore = Math.round((totalRiskScore / maxPossibleScore) * 100);
        }
        
        // Determine risk level
        let riskLevel = 'Not Calculated';
        if (finalRiskScore >= 80) {
            riskLevel = 'Critical';
        } else if (finalRiskScore >= 60) {
            riskLevel = 'High';
        } else if (finalRiskScore >= 40) {
            riskLevel = 'Medium';
        } else if (finalRiskScore >= 20) {
            riskLevel = 'Low';
        } else if (finalRiskScore > 0) {
            riskLevel = 'Minimal';
        }
        
        // Calculate confidence score (based on number of factors assessed)
        const confidenceScore = Math.min(100, Math.round((factorCount / 10) * 100));
        
        // Generate recommendations based on risk level
        const recommendations = generateRecommendations(riskLevel, criticalFactors, highImpactFactors);
        
        // Store results
        assessmentData.results = {
            riskScore: finalRiskScore,
            riskLevel: riskLevel,
            confidenceScore: confidenceScore,
            factorCounts: {
                total: totalFactors,
                critical: criticalFactors,
                highImpact: highImpactFactors
            },
            recommendations: recommendations
        };
        
        // Update the results display
        updateResultsDisplay();
        
        // Initialize charts
        initCharts();
    }
    
    /**
     * Generate recommendations based on risk level
     * @param {string} riskLevel - The calculated risk level
     * @param {number} criticalFactors - The number of critical factors
     * @param {number} highImpactFactors - The number of high impact factors
     * @returns {Array} - Array of recommendation objects
     */
    function generateRecommendations(riskLevel, criticalFactors, highImpactFactors) {
        const recommendations = [];
        
        // Base recommendations on risk level
        if (riskLevel === 'Critical') {
            recommendations.push({
                title: 'File Motion for Recusal Immediately',
                text: 'The risk level indicates a strong case for judicial prejudice. File a motion for recusal within 48 hours.',
                icon: 'exclamation-triangle'
            });
            
            recommendations.push({
                title: 'Document All Interactions',
                text: 'Maintain detailed records of all interactions with the court, including verbatim statements.',
                icon: 'file-alt'
            });
            
            recommendations.push({
                title: 'Prepare for Appeal',
                text: 'Begin preparing appeal strategy focused on judicial prejudice issues.',
                icon: 'gavel'
            });
        } 
        else if (riskLevel === 'High') {
            recommendations.push({
                title: 'Consider Motion for Recusal',
                text: 'Evaluate filing a motion for recusal based on the identified prejudice factors.',
                icon: 'balance-scale'
            });
            
            recommendations.push({
                title: 'Document Key Factors',
                text: 'Document all instances of potential prejudice with dates, witnesses, and context.',
                icon: 'clipboard-list'
            });
            
            recommendations.push({
                title: 'Consult with Ethics Counsel',
                text: 'Seek advice from ethics counsel regarding the appropriate response strategy.',
                icon: 'user-tie'
            });
        }
        else if (riskLevel === 'Medium') {
            recommendations.push({
                title: 'Monitor Ongoing Conduct',
                text: 'Closely monitor judicial conduct for additional signs of prejudice.',
                icon: 'eye'
            });
            
            recommendations.push({
                title: 'Document Concerning Behavior',
                text: 'Document any concerning behavior or statements for future reference.',
                icon: 'clipboard'
            });
            
            recommendations.push({
                title: 'Consider Disclosure Filing',
                text: 'Consider filing a disclosure document noting potential concerns about impartiality.',
                icon: 'file-signature'
            });
        }
        else if (riskLevel === 'Low') {
            recommendations.push({
                title: 'Standard Documentation',
                text: 'Maintain standard documentation of proceedings.',
                icon: 'file'
            });
            
            recommendations.push({
                title: 'Routine Monitoring',
                text: 'Continue routine monitoring of judicial conduct.',
                icon: 'search'
            });
        }
        else if (riskLevel === 'Minimal') {
            recommendations.push({
                title: 'No Special Action Required',
                text: 'Continue standard case management practices.',
                icon: 'check-circle'
            });
        }
        
        // Add recommendations based on critical factors
        if (criticalFactors > 0) {
            recommendations.push({
                title: `Address ${criticalFactors} Critical Factor${criticalFactors > 1 ? 's' : ''}`,
                text: `Focus on documenting and addressing the ${criticalFactors} critical prejudice factor${criticalFactors > 1 ? 's' : ''} identified in this assessment.`,
                icon: 'exclamation-circle'
            });
        }
        
        return recommendations;
    }
    
    /**
     * Update the results display
     */
    function updateResultsDisplay() {
        const results = assessmentData.results;
        
        // Update risk score
        document.getElementById('risk-score-value').textContent = results.riskScore;
        
        // Update risk level
        const riskLevelElement = document.querySelector('#risk-level .risk-level-value');
        riskLevelElement.textContent = results.riskLevel;
        riskLevelElement.className = 'risk-level-value ' + results.riskLevel.toLowerCase();
        
        // Update confidence score
        document.getElementById('confidence-fill').style.width = `${results.confidenceScore}%`;
        document.getElementById('confidence-value').textContent = `${results.confidenceScore}%`;
        
        // Update factor counts
        document.getElementById('total-factors').textContent = results.factorCounts.total;
        document.getElementById('critical-factors').textContent = results.factorCounts.critical;
        document.getElementById('high-impact').textContent = results.factorCounts.highImpact;
        
        // Update recommendations
        const recommendationsContent = document.getElementById('recommendations-content');
        recommendationsContent.innerHTML = '';
        
        if (results.recommendations.length > 0) {
            results.recommendations.forEach(recommendation => {
                const recommendationItem = document.createElement('div');
                recommendationItem.className = 'recommendation-item';
                
                recommendationItem.innerHTML = `
                    <div class="recommendation-icon">
                        <i class="fas fa-${recommendation.icon}"></i>
                    </div>
                    <div class="recommendation-text">
                        <h4>${recommendation.title}</h4>
                        <p>${recommendation.text}</p>
                    </div>
                `;
                
                recommendationsContent.appendChild(recommendationItem);
            });
        } else {
            recommendationsContent.innerHTML = '<p>No recommendations available.</p>';
        }
    }
    
    /**
     * Initialize the charts
     */
    function initCharts() {
        initRiskMatrixChart();
        initFactorChart();
        initCategoryChart();
    }
    
    /**
     * Initialize the risk matrix chart
     */
    function initRiskMatrixChart() {
        const ctx = document.getElementById('risk-matrix-chart').getContext('2d');
        
        // Combine all factors
        const allFactors = {
            ...assessmentData.relationshipFactors,
            ...assessmentData.conductFactors,
            ...assessmentData.contextualFactors
        };
        
        // Prepare data for the chart
        const dataPoints = [];
        const labels = [];
        
        for (const factorName in allFactors) {
            const factor = allFactors[factorName];
            
            if (factor.present) {
                dataPoints.push({
                    x: factor.likelihood,
                    y: factor.impact,
                    r: 8, // Bubble size
                    factorName: formatFactorName(factorName)
                });
                labels.push(formatFactorName(factorName));
            }
        }
        
        // Create the chart
        const riskMatrixChart = new Chart(ctx, {
            type: 'bubble',
            data: {
                datasets: [{
                    label: 'Risk Factors',
                    data: dataPoints,
                    backgroundColor: function(context) {
                        const index = context.dataIndex;
                        const value = context.dataset.data[index];
                        const x = value.x; // likelihood
                        const y = value.y; // impact
                        const risk = x * y;
                        
                        if (risk >= 16) {
                            return 'rgba(231, 76, 60, 0.7)'; // Critical (red)
                        } else if (risk >= 9) {
                            return 'rgba(230, 126, 34, 0.7)'; // High (orange)
                        } else if (risk >= 4) {
                            return 'rgba(241, 196, 15, 0.7)'; // Medium (yellow)
                        } else {
                            return 'rgba(46, 204, 113, 0.7)'; // Low (green)
                        }
                    },
                    borderColor: 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        min: 0.5,
                        max: 5.5,
                        title: {
                            display: true,
                            text: 'Likelihood'
                        },
                        ticks: {
                            stepSize: 1,
                            callback: function(value) {
                                if (value === 1) return 'Very Low';
                                if (value === 2) return 'Low';
                                if (value === 3) return 'Medium';
                                if (value === 4) return 'High';
                                if (value === 5) return 'Very High';
                                return '';
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    y: {
                        type: 'linear',
                        min: 0.5,
                        max: 5.5,
                        title: {
                            display: true,
                            text: 'Impact'
                        },
                        ticks: {
                            stepSize: 1,
                            callback: function(value) {
                                if (value === 1) return 'Very Low';
                                if (value === 2) return 'Low';
                                if (value === 3) return 'Medium';
                                if (value === 4) return 'High';
                                if (value === 5) return 'Very High';
                                return '';
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const dataPoint = context.raw;
                                return [
                                    dataPoint.factorName,
                                    `Likelihood: ${getLikelihoodLabel(dataPoint.x)}`,
                                    `Impact: ${getImpactLabel(dataPoint.y)}`,
                                    `Risk Score: ${dataPoint.x * dataPoint.y}`
                                ];
                            }
                        }
                    },
                    legend: {
                        display: false
                    }
                }
            }
        });
        
        // Add risk zones
        const originalDraw = riskMatrixChart.draw;
        riskMatrixChart.draw = function() {
            originalDraw.apply(this, arguments);
            
            const chart = this;
            const ctx = chart.ctx;
            const chartArea = chart.chartArea;
            const xAxis = chart.scales.x;
            const yAxis = chart.scales.y;
            
            // Draw risk zones
            ctx.save();
            
            // Critical zone (red)
            ctx.fillStyle = 'rgba(231, 76, 60, 0.1)';
            ctx.fillRect(
                xAxis.getPixelForValue(3.5),
                yAxis.getPixelForValue(5.5),
                xAxis.getPixelForValue(5.5) - xAxis.getPixelForValue(3.5),
                yAxis.getPixelForValue(3.5) - yAxis.getPixelForValue(5.5)
            );
            
            // High zone (orange)
            ctx.fillStyle = 'rgba(230, 126, 34, 0.1)';
            ctx.fillRect(
                xAxis.getPixelForValue(2.5),
                yAxis.getPixelForValue(3.5),
                xAxis.getPixelForValue(5.5) - xAxis.getPixelForValue(2.5),
                yAxis.getPixelForValue(2.5) - yAxis.getPixelForValue(3.5)
            );
            ctx.fillRect(
                xAxis.getPixelForValue(3.5),
                yAxis.getPixelForValue(2.5),
                xAxis.getPixelForValue(5.5) - xAxis.getPixelForValue(3.5),
                yAxis.getPixelForValue(0.5) - yAxis.getPixelForValue(2.5)
            );
            
            // Medium zone (yellow)
            ctx.fillStyle = 'rgba(241, 196, 15, 0.1)';
            ctx.fillRect(
                xAxis.getPixelForValue(1.5),
                yAxis.getPixelForValue(2.5),
                xAxis.getPixelForValue(2.5) - xAxis.getPixelForValue(1.5),
                yAxis.getPixelForValue(0.5) - yAxis.getPixelForValue(2.5)
            );
            ctx.fillRect(
                xAxis.getPixelForValue(2.5),
                yAxis.getPixelForValue(1.5),
                xAxis.getPixelForValue(3.5) - xAxis.getPixelForValue(2.5),
                yAxis.getPixelForValue(0.5) - yAxis.getPixelForValue(1.5)
            );
            
            // Low zone (green)
            ctx.fillStyle = 'rgba(46, 204, 113, 0.1)';
            ctx.fillRect(
                xAxis.getPixelForValue(0.5),
                yAxis.getPixelForValue(1.5),
                xAxis.getPixelForValue(1.5) - xAxis.getPixelForValue(0.5),
                yAxis.getPixelForValue(0.5) - yAxis.getPixelForValue(1.5)
            );
            
            ctx.restore();
        };
        
        riskMatrixChart.update();
    }
    
    /**
     * Initialize the factor chart
     */
    function initFactorChart() {
        const ctx = document.getElementById('factor-chart').getContext('2d');
        
        // Combine all factors
        const allFactors = {
            ...assessmentData.relationshipFactors,
            ...assessmentData.conductFactors,
            ...assessmentData.contextualFactors
        };
        
        // Prepare data for the chart
        const labels = [];
        const likelihoodData = [];
        const impactData = [];
        const riskScoreData = [];
        
        for (const factorName in allFactors) {
            const factor = allFactors[factorName];
            
            if (factor.present) {
                labels.push(formatFactorName(factorName));
                likelihoodData.push(factor.likelihood);
                impactData.push(factor.impact);
                riskScoreData.push(factor.likelihood * factor.impact);
            }
        }
        
        // Create the chart
        const factorChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Risk Score',
                        data: riskScoreData,
                        backgroundColor: function(context) {
                            const value = context.dataset.data[context.dataIndex];
                            
                            if (value >= 16) {
                                return 'rgba(231, 76, 60, 0.7)'; // Critical (red)
                            } else if (value >= 9) {
                                return 'rgba(230, 126, 34, 0.7)'; // High (orange)
                            } else if (value >= 4) {
                                return 'rgba(241, 196, 15, 0.7)'; // Medium (yellow)
                            } else {
                                return 'rgba(46, 204, 113, 0.7)'; // Low (green)
                            }
                        },
                        borderColor: 'rgba(0, 0, 0, 0.1)',
                        borderWidth: 1,
                        order: 1
                    },
                    {
                        label: 'Likelihood',
                        data: likelihoodData,
                        type: 'line',
                        borderColor: 'rgba(52, 152, 219, 0.7)',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgba(52, 152, 219, 0.7)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 1,
                        pointRadius: 4,
                        fill: false,
                        order: 0
                    },
                    {
                        label: 'Impact',
                        data: impactData,
                        type: 'line',
                        borderColor: 'rgba(155, 89, 182, 0.7)',
                        backgroundColor: 'rgba(155, 89, 182, 0.1)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgba(155, 89, 182, 0.7)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 1,
                        pointRadius: 4,
                        fill: false,
                        order: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        ticks: {
                            autoSkip: false,
                            maxRotation: 45,
                            minRotation: 45
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 25,
                        title: {
                            display: true,
                            text: 'Value'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const datasetLabel = context.dataset.label;
                                const value = context.raw;
                                
                                if (datasetLabel === 'Likelihood') {
                                    return `Likelihood: ${value} (${getLikelihoodLabel(value)})`;
                                } else if (datasetLabel === 'Impact') {
                                    return `Impact: ${value} (${getImpactLabel(value)})`;
                                } else {
                                    return `Risk Score: ${value}`;
                                }
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Initialize the category chart
     */
    function initCategoryChart() {
        const ctx = document.getElementById('category-chart').getContext('2d');
        
        // Calculate category scores
        const relationshipScore = calculateCategoryScore(assessmentData.relationshipFactors);
        const conductScore = calculateCategoryScore(assessmentData.conductFactors);
        const contextualScore = calculateCategoryScore(assessmentData.contextualFactors);
        
        // Create the chart
        const categoryChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Relationship Factors', 'Conduct Factors', 'Contextual Factors'],
                datasets: [{
                    label: 'Category Risk Scores',
                    data: [relationshipScore, conductScore, contextualScore],
                    backgroundColor: 'rgba(52, 152, 219, 0.2)',
                    borderColor: 'rgba(52, 152, 219, 0.7)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(52, 152, 219, 0.7)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 1,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                return `Risk Score: ${value}%`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Calculate the score for a category of factors
     * @param {Object} factors - The factors in the category
     * @returns {number} - The category score (0-100)
     */
    function calculateCategoryScore(factors) {
        let totalScore = 0;
        let maxPossibleScore = 0;
        
        for (const factorName in factors) {
            const factor = factors[factorName];
            
            if (factor.present) {
                totalScore += factor.likelihood * factor.impact;
                maxPossibleScore += 25; // Max possible is 5 * 5
            }
        }
        
        if (maxPossibleScore === 0) {
            return 0;
        }
        
        return Math.round((totalScore / maxPossibleScore) * 100);
    }
    
    /**
     * Format a factor name for display
     * @param {string} factorName - The factor name to format
     * @returns {string} - The formatted factor name
     */
    function formatFactorName(factorName) {
        // Convert kebab-case to Title Case
        return factorName
            .split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
    
    /**
     * Get the label for a likelihood value
     * @param {number} value - The likelihood value
     * @returns {string} - The likelihood label
     */
    function getLikelihoodLabel(value) {
        if (value === 1) return 'Very Low';
        if (value === 2) return 'Low';
        if (value === 3) return 'Medium';
        if (value === 4) return 'High';
        if (value === 5) return 'Very High';
        return 'Unknown';
    }
    
    /**
     * Get the label for an impact value
     * @param {number} value - The impact value
     * @returns {string} - The impact label
     */
    function getImpactLabel(value) {
        if (value === 1) return 'Very Low';
        if (value === 2) return 'Low';
        if (value === 3) return 'Medium';
        if (value === 4) return 'High';
        if (value === 5) return 'Very High';
        return 'Unknown';
    }
    
    /**
     * Save the current assessment
     */
    function saveAssessment() {
        // This would typically involve an API call to save the assessment data
        console.log('Saving assessment:', assessmentData);
        
        // For now, just show an alert
        alert('Assessment saved successfully!');
    }
    
    /**
     * Export the assessment to PDF
     */
    function exportToPdf() {
        // This would typically involve generating a PDF
        console.log('Exporting to PDF:', assessmentData);
        
        // For now, just show an alert
        alert('PDF export functionality will be implemented in a future update.');
    }
    
    /**
     * Reset the calculator
     */
    function resetCalculator() {
        // Reset assessment data
        assessmentData.caseInfo = {};
        assessmentData.relationshipFactors = {};
        assessmentData.conductFactors = {};
        assessmentData.contextualFactors = {};
        assessmentData.results = {
            riskScore: 0,
            riskLevel: 'Not Calculated',
            confidenceScore: 0,
            factorCounts: {
                total: 0,
                critical: 0,
                highImpact: 0
            },
            recommendations: []
        };
        
        // Reset form inputs
        document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea, select').forEach(input => {
            input.value = '';
        });
        
        // Reset radio buttons
        document.querySelectorAll('input[type="radio"]').forEach(radio => {
            radio.checked = false;
        });
        
        // Reset ratings
        document.querySelectorAll('.rating').forEach(rating => {
            rating.dataset.rating = '0';
            updateRatingDisplay(rating);
        });
        
        // Hide factor details
        document.querySelectorAll('.factor-details').forEach(details => {
            details.style.display = 'none';
        });
        
        // Navigate to first section
        navigateToSection('case-info');
    }
});