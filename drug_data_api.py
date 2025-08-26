from flask import Flask, jsonify, request
import requests

# Initialize Flask application
app = Flask(__name__)

def get_chembl_data(chembl_id):
    """
    Retrieve detailed compound data from ChEMBL database.
    
    Args:
        chembl_id (str): ChEMBL compound identifier (e.g., 'CHEMBL25')
    
    Returns:
        dict: Compound data including chemical properties, structure information,
              and development phase, or None if compound not found
    
    Example:
        >>> get_chembl_data('CHEMBL25')
        {
            'chembl_id': 'CHEMBL25',
            'pref_name': 'ASPIRIN',
            'smiles': 'CC(=O)Oc1ccccc1C(=O)O',
            'molecular_weight': 180.16,
            ...
        }
    """
    # Construct ChEMBL API URL for molecule data
    url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/{chembl_id}.json"
    headers = {'Accept': 'application/json'}
    
    try:
        # Make API request to ChEMBL with 30 second timeout
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return None
        
        # Parse JSON response and extract structure/property data
        data = response.json()
        structures = data.get('molecule_structures', {})
        properties = data.get('molecule_properties', {})
        
        # Return structured compound data
        return {
            'chembl_id': data.get('molecule_chembl_id'),  # ChEMBL identifier
            'pref_name': data.get('pref_name'),  # Preferred compound name
            'smiles': structures.get('canonical_smiles'),  # SMILES notation
            'inchi': structures.get('standard_inchi'),  # InChI identifier
            'inchi_key': structures.get('standard_inchi_key'),  # InChI key
            'molecular_weight': properties.get('mw_freebase'),  # Molecular weight
            'formula': properties.get('full_mwt'),  # Molecular formula
            'max_phase': data.get('max_phase'),  # Development phase (0-4)
            'molecule_type': data.get('molecule_type'),  # Type of molecule
            'therapeutic_flag': data.get('therapeutic_flag')  # Therapeutic use flag
        }
    except Exception:
        # Return None on any error (network, parsing, etc.)
        return None

def search_compound(name):
    """
    Search for compounds in ChEMBL database by name.
    
    Args:
        name (str): Compound name to search for
    
    Returns:
        list: List of matching compounds with basic information,
              empty list if no matches found
    
    Example:
        >>> search_compound('aspirin')
        [{
            'chembl_id': 'CHEMBL25',
            'pref_name': 'ASPIRIN',
            'smiles': 'CC(=O)Oc1ccccc1C(=O)O',
            'max_phase': 4
        }]
    """
    # ChEMBL search endpoint with query parameters
    url = "https://www.ebi.ac.uk/chembl/api/data/molecule/search.json"
    headers = {'Accept': 'application/json'}
    params = {'q': name}  # Search query
    
    try:
        # Search ChEMBL database for matching compounds
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code != 200:
            return []
        
        data = response.json()
        results = []
        
        # Extract key information from each search result
        for molecule in data.get('molecules', []):
            structures = molecule.get('molecule_structures', {})
            results.append({
                'chembl_id': molecule.get('molecule_chembl_id'),
                'pref_name': molecule.get('pref_name'),
                'smiles': structures.get('canonical_smiles'),
                'max_phase': molecule.get('max_phase')  # Development phase
            })
        return results
    except Exception:
        # Return empty list on any error
        return []

def get_similar_compounds(smiles, limit=20):
    """
    Find structurally similar compounds using Tanimoto similarity.
    
    Args:
        smiles (str): SMILES notation of query compound
        limit (int): Maximum number of similar compounds to return (default: 20)
    
    Returns:
        list: List of similar compounds with similarity scores,
              empty list if no similar compounds found
    
    Note:
        Uses 70% Tanimoto similarity threshold via ChEMBL API
    
    Example:
        >>> get_similar_compounds('CC(=O)Oc1ccccc1C(=O)O', 5)
        [{
            'chembl_id': 'CHEMBL521',
            'similarity': 0.85,
            'smiles': '...',
            ...
        }]
    """
    # ChEMBL similarity search with 70% Tanimoto threshold
    url = f"https://www.ebi.ac.uk/chembl/api/data/similarity/{smiles}/70.json"
    headers = {'Accept': 'application/json'}
    
    try:
        # Request similar compounds from ChEMBL
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return []
        
        data = response.json()
        results = []
        
        # Process similarity results, limiting to requested number
        for item in data.get('molecules', [])[:limit]:
            similarity = item.get('similarity')
            structures = item.get('molecule_structures', {})
            properties = item.get('molecule_properties', {})
            
            results.append({
                'chembl_id': item.get('molecule_chembl_id'),
                'pref_name': item.get('pref_name'),
                'smiles': structures.get('canonical_smiles'),
                'similarity': float(similarity) if similarity else None,  # Tanimoto score
                'molecular_weight': properties.get('mw_freebase'),
                'max_phase': item.get('max_phase')
            })
        
        return results
    except Exception:
        # Return empty list on any error
        return []

def get_adverse_events(drug_name, limit=10):
    """
    Retrieve adverse event data from FDA FAERS database.
    
    Args:
        drug_name (str): Name of the drug to search for
        limit (int): Maximum number of adverse events to return (default: 10)
    
    Returns:
        dict: Adverse event data with drug name, total reports count,
              and list of adverse events with reaction counts
    
    Example:
        >>> get_adverse_events('aspirin', 5)
        {
            'drug_name': 'aspirin',
            'total_reports': 3,
            'adverse_events': [
                {'reaction': 'NAUSEA', 'count': 1250},
                {'reaction': 'HEADACHE', 'count': 890},
                ...
            ]
        }
    """
    # Construct FDA openFDA API search parameters
    search_term = f'patient.drug.medicinalproduct:"{drug_name}"'  # Search by product name
    params = {
        'search': search_term,
        'limit': limit,
        'count': 'patient.reaction.reactionmeddrapt.exact'  # Count reactions by MedDRA term
    }
    
    try:
        # Query FDA FAERS database for adverse events
        response = requests.get("https://api.fda.gov/drug/event.json", params=params, timeout=30)
        if response.status_code != 200:
            return {'drug_name': drug_name, 'total_reports': 0, 'adverse_events': []}
        
        data = response.json()
        adverse_events = []
        
        # Extract adverse event reactions and their frequencies
        for result in data.get('results', []):
            adverse_events.append({
                'reaction': result.get('term'),  # MedDRA preferred term
                'count': result.get('count')     # Number of reports
            })
        
        return {
            'drug_name': drug_name,
            'total_reports': len(adverse_events),  # Number of unique adverse events
            'adverse_events': adverse_events
        }
    except Exception:
        # Return empty result on any error
        return {'drug_name': drug_name, 'total_reports': 0, 'adverse_events': []}


def get_full_drug_data(identifier, id_type='name'):
    """
    Aggregate comprehensive drug data from multiple sources.
    
    Args:
        identifier (str): Drug identifier (name or ChEMBL ID)
        id_type (str): Type of identifier - 'name' or 'chembl_id' (default: 'name')
    
    Returns:
        dict: Combined data including query info, ChEMBL compound data,
              and FDA adverse events
    
    Example:
        >>> get_full_drug_data('aspirin', 'name')
        {
            'query': 'aspirin',
            'query_type': 'name',
            'chembl_data': {...},
            'adverse_events': {...}
        }
    """
    # Initialize response with query information
    data = {'query': identifier, 'query_type': id_type}
    
    # Get ChEMBL data based on identifier type
    if id_type == 'chembl_id':
        # Direct ChEMBL lookup by ID
        chembl_data = get_chembl_data(identifier)
        if chembl_data:
            data['chembl_data'] = chembl_data
            drug_name = chembl_data.get('pref_name', identifier)
        else:
            drug_name = identifier
            data['chembl_data'] = None
    else:
        # Search ChEMBL by compound name
        chembl_results = search_compound(identifier)
        if chembl_results:
            data['chembl_data'] = chembl_results[0]  # Use first match
            drug_name = identifier
        else:
            drug_name = identifier
            data['chembl_data'] = None
    
    # Get FDA adverse event data
    adverse_events = get_adverse_events(drug_name)
    data['adverse_events'] = adverse_events
    
    return data

@app.route('/')
def home():
    """Returns API information and available endpoints."""
    return jsonify({
        'message': 'Drug Compound Data API',
        'version': '1.0',
        'endpoints': {
            '/api/compound/<identifier>': 'GET - Get comprehensive drug data by name or ChEMBL ID',
            '/api/chembl/<chembl_id>': 'GET - Get ChEMBL data for specified compound',
            '/api/adverse-events/<drug_name>': 'GET - Get FAERS adverse event data for specified compound',
            '/api/similar-compounds/adverse-effects/<compound>': 'GET - Get adverse effects across 20 similar compounds'
        }
    })

@app.route('/api/compound/<identifier>')
def compound_data(identifier):
    """
    Get comprehensive drug data by name or ChEMBL ID, including adverse event data from FDA FAERS
    Query param: ?type=name|chembl_id
    """

    # Validate identifier type parameter
    id_type = request.args.get('type', 'name')
    if id_type not in ['name', 'chembl_id']:
        return jsonify({'error': 'Invalid identifier type'}), 400
    
    data = get_full_drug_data(identifier, id_type)
    return jsonify(data)

@app.route('/api/chembl/<chembl_id>')
def chembl_data(chembl_id):
    """Get ChEMBL compound data by ChEMBL ID."""

    # Retrieve ChEMBL data and handle not found case
    data = get_chembl_data(chembl_id)
    if not data:
        return jsonify({'error': 'Compound not found'}), 404
    return jsonify(data)

@app.route('/api/adverse-events/<drug_name>')
def adverse_events(drug_name):
    """Get adverse event data for a drug from FDA FAERS. Query param: ?limit=number"""
    # Parse limit parameter and get adverse event data
    limit = request.args.get('limit', 10, type=int)
    data = get_adverse_events(drug_name, limit)
    return jsonify(data)


@app.route('/api/similar-compounds/adverse-effects/<compound>')
def similar_adverse_effects(compound):
    """
    Get unique adverse effects across similar compounds. Accepts drug name, ChEMBL ID, or SMILES.
    Query param: ?limit=number
    """

    # Parse query parameters
    limit = request.args.get('limit', 20, type=int)
    
    # Determine compound type and get SMILES representation
    if compound.startswith('CHEMBL'):
        # Handle ChEMBL ID input
        compound_data = get_chembl_data(compound)
        if compound_data and compound_data.get('smiles'):
            smiles = compound_data['smiles']
        else:
            return jsonify({'error': 'Compound not found'}), 404
    else:
        # Check if input is already a SMILES string (contains chemical notation)
        if any(char in compound for char in ['=', '#', '(', ')', '[', ']']):
            smiles = compound
        else:
            # Search by compound name to get SMILES
            search_results = search_compound(compound)
            if search_results and search_results[0].get('smiles'):
                smiles = search_results[0]['smiles']
            else:
                return jsonify({'error': 'Compound not found'}), 404
    
    # Find structurally similar compounds using Tanimoto similarity
    similar_compounds = get_similar_compounds(smiles, limit)
    
    # Dictionary to aggregate adverse reactions across all similar compounds
    all_reactions = {}
    
    # Collect adverse events for each similar compound
    for comp in similar_compounds:
        if comp.get('pref_name'):
            # Get adverse events for this similar compound (up to 50 events)
            adverse_data = get_adverse_events(comp['pref_name'], 50)
            for event in adverse_data.get('adverse_events', []):
                reaction = event.get('reaction')
                count = event.get('count', 0)
                if reaction:
                    # Aggregate reaction counts across all similar compounds
                    if reaction in all_reactions:
                        all_reactions[reaction] += count
                    else:
                        all_reactions[reaction] = count
    
    # Sort adverse reactions by frequency (highest first)
    sorted_reactions = sorted([
        {'reaction': reaction, 'total_count': count} 
        for reaction, count in all_reactions.items()
    ], key=lambda x: x['total_count'], reverse=True)
    
    # Return aggregated adverse effects analysis
    return jsonify({
        'query_compound': compound,  # Original compound identifier
        'query_smiles': smiles,      # SMILES representation used for similarity
        'total_unique_reactions': len(all_reactions),  # Number of distinct adverse reactions
        'adverse_effects_across_similar_compounds': sorted_reactions  # Sorted by frequency
    })

# Run the Flask development server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)