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

### Root Endpoint
```bash
GET /
```
Returns API information and available endpoints.

### Drug Data
```bash
GET /api/compound/<identifier>?type=<name|chembl_id>
```
Get aggregated data from all sources for a drug compound.

**Example:**
```bash
curl "http://localhost:5001/api/compound/aspirin"
```

### ChEMBL Data
```bash
GET /api/chembl/<chembl_id>
```
Get specific compound data from ChEMBL database.

**Example:**
```bash
curl "http://localhost:5001/api/chembl/CHEMBL25"
```

### Adverse Events
```bash
GET /api/adverse-events/<drug_name>?limit=<number>
```
Get FDA adverse event data for a drug.

**Example:**
```bash
curl "http://localhost:5001/api/adverse-events/ibuprofen?limit=20"
```

### Similar Compounds Adverse Effects
```bash
GET /api/similar-compounds/adverse-effects/<compound>?limit=<number>
```
Get unique adverse effects across 20 most similar compounds using Tanimoto similarity. Accepts ChEMBL IDs, compound names, or SMILES strings.

**Parameters:**
- `limit`: Number of similar compounds to analyze (default: 20)

**Examples:**
```bash
# By compound name
curl "http://localhost:5001/api/similar-compounds/adverse-effects/aspirin"

# By ChEMBL ID
curl "http://localhost:5001/api/similar-compounds/adverse-effects/CHEMBL25"

# By SMILES string
curl "http://localhost:5001/api/similar-compounds/adverse-effects/CC(=O)Oc1ccccc1C(=O)O"
```

## Response Format
All endpoints return JSON responses with consistent structure:

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
