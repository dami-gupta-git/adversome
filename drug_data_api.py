from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

def get_chembl_data(chembl_id):
    url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/{chembl_id}.json"
    headers = {'Accept': 'application/json'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return None
        
        data = response.json()
        structures = data.get('molecule_structures', {})
        properties = data.get('molecule_properties', {})
        
        return {
            'chembl_id': data.get('molecule_chembl_id'),
            'pref_name': data.get('pref_name'),
            'smiles': structures.get('canonical_smiles'),
            'inchi': structures.get('standard_inchi'),
            'inchi_key': structures.get('standard_inchi_key'),
            'molecular_weight': properties.get('mw_freebase'),
            'formula': properties.get('full_mwt'),
            'max_phase': data.get('max_phase'),
            'molecule_type': data.get('molecule_type'),
            'therapeutic_flag': data.get('therapeutic_flag')
        }
    except:
        return None

def search_compound(name):
    url = "https://www.ebi.ac.uk/chembl/api/data/molecule/search.json"
    headers = {'Accept': 'application/json'}
    params = {'q': name}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code != 200:
            return []
        
        data = response.json()
        results = []
        
        for molecule in data.get('molecules', []):
            structures = molecule.get('molecule_structures', {})
            results.append({
                'chembl_id': molecule.get('molecule_chembl_id'),
                'pref_name': molecule.get('pref_name'),
                'smiles': structures.get('canonical_smiles'),
                'max_phase': molecule.get('max_phase')
            })
        return results
    except:
        return []

def get_similar_compounds(smiles, limit=20):
    url = f"https://www.ebi.ac.uk/chembl/api/data/similarity/{smiles}/70.json"
    headers = {'Accept': 'application/json'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return []
        
        data = response.json()
        results = []
        
        for item in data.get('molecules', [])[:limit]:
            similarity = item.get('similarity')
            structures = item.get('molecule_structures', {})
            properties = item.get('molecule_properties', {})
            
            results.append({
                'chembl_id': item.get('molecule_chembl_id'),
                'pref_name': item.get('pref_name'),
                'smiles': structures.get('canonical_smiles'),
                'similarity': float(similarity) if similarity else None,
                'molecular_weight': properties.get('mw_freebase'),
                'max_phase': item.get('max_phase')
            })
        
        return results
    except:
        return []

def get_adverse_events(drug_name, limit=10):
    search_term = f'patient.drug.medicinalproduct:"{drug_name}"'
    params = {
        'search': search_term,
        'limit': limit,
        'count': 'patient.reaction.reactionmeddrapt.exact'
    }
    
    try:
        response = requests.get("https://api.fda.gov/drug/event.json", params=params, timeout=30)
        if response.status_code != 200:
            return {'drug_name': drug_name, 'total_reports': 0, 'adverse_events': []}
        
        data = response.json()
        adverse_events = []
        
        for result in data.get('results', []):
            adverse_events.append({
                'reaction': result.get('term'),
                'count': result.get('count')
            })
        
        return {
            'drug_name': drug_name,
            'total_reports': len(adverse_events),
            'adverse_events': adverse_events
        }
    except:
        return {'drug_name': drug_name, 'total_reports': 0, 'adverse_events': []}


def get_full_drug_data(identifier, id_type='name'):
    data = {'query': identifier, 'query_type': id_type}
    
    if id_type == 'chembl_id':
        chembl_data = get_chembl_data(identifier)
        if chembl_data:
            data['chembl_data'] = chembl_data
            drug_name = chembl_data.get('pref_name', identifier)
        else:
            drug_name = identifier
            data['chembl_data'] = None
    else:
        chembl_results = search_compound(identifier)
        if chembl_results:
            data['chembl_data'] = chembl_results[0]
            drug_name = identifier
        else:
            drug_name = identifier
            data['chembl_data'] = None
    
    adverse_events = get_adverse_events(drug_name)
    data['adverse_events'] = adverse_events
    
    return data

@app.route('/')
def home():
    return jsonify({
        'message': 'Drug Compound Data API',
        'version': '1.0',
        'endpoints': {
            '/api/compound/<identifier>': 'GET - Get comprehensive drug data by name or ChEMBL ID',
            '/api/chembl/<chembl_id>': 'GET - Get ChEMBL data for specific compound',
            '/api/adverse-events/<drug_name>': 'GET - Get FAERS adverse event data',
            '/api/similar-compounds/adverse-effects/<compound>': 'GET - Get adverse effects across 20 similar compounds'
        }
    })

@app.route('/api/compound/<identifier>')
def compound_data(identifier):
    id_type = request.args.get('type', 'name')
    if id_type not in ['name', 'chembl_id']:
        return jsonify({'error': 'Invalid identifier type'}), 400
    
    data = get_full_drug_data(identifier, id_type)
    return jsonify(data)

@app.route('/api/chembl/<chembl_id>')
def chembl_data(chembl_id):
    data = get_chembl_data(chembl_id)
    if not data:
        return jsonify({'error': 'Compound not found'}), 404
    return jsonify(data)

@app.route('/api/adverse-events/<drug_name>')
def adverse_events(drug_name):
    limit = request.args.get('limit', 10, type=int)
    data = get_adverse_events(drug_name, limit)
    return jsonify(data)


@app.route('/api/similar-compounds/adverse-effects/<compound>')
def similar_adverse_effects(compound):
    limit = request.args.get('limit', 20, type=int)
    
    if compound.startswith('CHEMBL'):
        compound_data = get_chembl_data(compound)
        if compound_data and compound_data.get('smiles'):
            smiles = compound_data['smiles']
        else:
            return jsonify({'error': 'Compound not found'}), 404
    else:
        if any(char in compound for char in ['=', '#', '(', ')', '[', ']']):
            smiles = compound
        else:
            search_results = search_compound(compound)
            if search_results and search_results[0].get('smiles'):
                smiles = search_results[0]['smiles']
            else:
                return jsonify({'error': 'Compound not found'}), 404
    
    similar_compounds = get_similar_compounds(smiles, limit)
    
    all_reactions = {}
    
    for comp in similar_compounds:
        if comp.get('pref_name'):
            adverse_data = get_adverse_events(comp['pref_name'], 50)
            for event in adverse_data.get('adverse_events', []):
                reaction = event.get('reaction')
                count = event.get('count', 0)
                if reaction:
                    if reaction in all_reactions:
                        all_reactions[reaction] += count
                    else:
                        all_reactions[reaction] = count
    
    sorted_reactions = sorted([
        {'reaction': reaction, 'total_count': count} 
        for reaction, count in all_reactions.items()
    ], key=lambda x: x['total_count'], reverse=True)
    
    return jsonify({
        'query_compound': compound,
        'query_smiles': smiles,
        'total_unique_reactions': len(all_reactions),
        'adverse_effects_across_similar_compounds': sorted_reactions
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)