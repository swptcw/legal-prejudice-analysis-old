# Legal Prejudice Risk Calculator

This interactive web application implements the risk assessment methodology from the Legal Prejudice Analysis Framework. It allows legal practitioners to systematically evaluate potential judicial prejudice through a structured assessment of relationship-based, conduct-based, and contextual factors.

## Features

- **Comprehensive Factor Assessment**: Evaluate 18 different prejudice factors across three categories
- **Risk Scoring System**: Calculate risk scores based on likelihood and impact ratings
- **Risk Matrix Visualization**: Visual representation of factor distribution on a risk matrix
- **Automated Recommendations**: Receive tailored recommendations based on risk level
- **Documentation Support**: Record detailed notes for each factor
- **PDF Export**: Save assessment results for documentation and sharing (placeholder functionality)

## Getting Started

### Prerequisites

- Python 3.6 or higher

### Running the Application

1. Navigate to the project directory:
   ```
   cd prejudice_risk_calculator
   ```

2. Make the server script executable (Linux/Mac):
   ```
   chmod +x server.py
   ```

3. Run the server:
   ```
   python server.py
   ```

4. The application will automatically open in your default web browser. If it doesn't, navigate to:
   ```
   http://localhost:8000/
   ```

## Using the Risk Calculator

### Step 1: Relationship-Based Factors
Evaluate factors related to financial interests, personal relationships, and political/ideological connections.

### Step 2: Conduct-Based Factors
Assess factors related to in-court statements, procedural rulings, and extra-judicial statements.

### Step 3: Contextual Factors
Evaluate factors related to historical patterns, procedural irregularities, and external pressures.

### Step 4: Results
Review the calculated risk scores, risk matrix visualization, and recommended actions.

## Risk Level Interpretation

- **Critical Risk (20-25)**: Immediate formal challenge required
- **High Risk (15-19)**: Urgent formal or informal action required
- **Medium Risk (8-14)**: Prompt strategic response required
- **Low Risk (1-7)**: Documentation and monitoring required

## Integration with Legal Prejudice Analysis Framework

This calculator implements the risk assessment methodology described in the Legal Prejudice Risk and Probability Analysis document. It is designed to be used in conjunction with the broader Legal Prejudice Analysis Framework, which includes:

- Legal Prejudice Analysis Framework
- Risk and Probability Analysis for Legal Prejudice
- Practical Guide for Legal Practitioners
- Legal Prejudice Case Studies

## Future Enhancements

- Server-side data storage for saving assessments
- User authentication system
- Enhanced PDF export functionality
- Bayesian probability calculator integration
- Pattern detection analytics
- Case management integration

## Technical Details

The application is built using:
- HTML5
- CSS3
- JavaScript (vanilla)
- Python (for the simple HTTP server)

No external libraries or frameworks are required.

## License

This project is part of the Legal Prejudice Analysis Framework.

## Acknowledgments

- Developed based on the Legal Prejudice Analysis Framework
- Risk assessment methodology derived from the Risk and Probability Analysis document