# Adversome - Drug Compound Data API (Under Construction)

An API for analyzing drug compound data and adverse effects across similar molecules using ChEMBL and FDA data sources.

This is just the skeleton for a larger project, more to come. I have been working on this with a bioinformatician (credits forthcoming).

## Overview

Adversome provides drug compound information and analyzes adverse effects patterns across chemically similar compounds:

- **ChEMBL**: Chemical structures, SMILES data, molecular properties
- **FAERS**: FDA Adverse Event Reporting System data for safety analysis

## Features

- **Drug Compound Search** - Search by drug name or ChEMBL ID or SMILES
- **Adverse Effects** - Get adverse events for a drug
- **Similarity-Based Safety Profiling** - Find adverse effects common to chemically similar drugs


## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd adversome

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the API

```bash
# Start the development server
python drug_data_api.py
```

The API will be available at `http://localhost:5001`

## API Endpoints

### GET /
Returns API information and available endpoints.

### GET /api/compound/\<identifier>
Get comprehensive drug data combining ChEMBL and FDA adverse event data.
- **Parameters**: `?type=name|chembl_id` (default: name)
- **Example**: `curl "http://localhost:5001/api/compound/aspirin"`

### GET /api/chembl/\<chembl_id>
Get compound data from ChEMBL database.
- **Example**: `curl "http://localhost:5001/api/chembl/CHEMBL25"`

### GET /api/adverse-events/\<drug_name>
Get FDA adverse event data for a drug.
- **Parameters**: `?limit=number` (default: 10)
- **Example**: `curl "http://localhost:5001/api/adverse-events/ibuprofen?limit=20"`

### GET /api/similar-compounds/adverse-effects/\<compound>
Get aggregated adverse effects across chemically similar compounds. (Tanimoto similarity)
- **Input**: Drug name, ChEMBL ID, or SMILES string
- **Parameters**: `?limit=number` (default: 20 similar compounds)
- **Examples**:
  ```bash
  # By name
  curl "http://localhost:5001/api/similar-compounds/adverse-effects/aspirin"
  
  # By ChEMBL ID
  curl "http://localhost:5001/api/similar-compounds/adverse-effects/CHEMBL25"
  ```

## Response Format
All endpoints return JSON responses. Check the API root endpoint (`GET /`) for endpoint details and response structure examples.

## Testing

Run the comprehensive test suite:

```bash
python test_api.py
```

This will test all endpoints and verify:
- Data retrieval from all sources
- Rate limiting functionality
- Error handling
- Response structure validation

## Data Sources

### ChEMBL Database
- **URL**: https://www.ebi.ac.uk/chembl/
- **Data**: Chemical structures, bioactivity data, drug information
- **Usage**: Compound searches, SMILES data, molecular similarity analysis

### FAERS (FDA Adverse Event Reporting System)  
- **URL**: https://open.fda.gov/apis/drug/event/
- **Data**: Post-market safety surveillance data
- **Usage**: Adverse event reporting, safety signal detection across similar compounds


## Development

### Project Structure
```
adversome/
├── drug_data_api.py      # Main API application
├── test_api.py           # Comprehensive test suite
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### Key Functionality

The API's main feature is analyzing adverse effects across chemically similar compounds. This helps identify potential safety signals by:

1. Getting compound data from CHEM
2. Finding compounds with similar chemical structures (using Tanimoto similarity)
3. Aggregating adverse event data from FDA FAERS for each similar compound  
4. Listing adverse effects common to structurally related drugs


## License

This project is open source. Please check the license file for details.

## Disclaimer

This API is for research and educational purposes. The data provided should not be used for clinical decision-making without proper validation. Always consult official drug databases and healthcare professionals for medical information.
