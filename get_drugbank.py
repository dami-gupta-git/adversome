from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import requests
import zipfile
import io
import os

app = Flask(__name__)

# Configure PostgreSQL database (update with your credentials)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/drugbank_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Drug model for the database
class Drug(db.Model):
    __tablename__ = 'drugs'
    id = db.Column(db.Integer, primary_key=True)
    drugbank_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    synonyms = db.Column(db.Text)
    cas_number = db.Column(db.String(50))
    unii = db.Column(db.String(50))

    def to_dict(self):
        return {
            'drugbank_id': self.drugbank_id,
            'name': self.name,
            'description': self.description,
            'synonyms': self.synonyms,
            'cas_number': self.cas_number,
            'unii': self.unii
        }

# Function to download and extract DrugBank Vocabulary data
def fetch_drugbank_vocabulary():
    url = "https://go.drugbank.com/releases/latest/open_data/vocabulary.csv.zip"
    response = requests.get(url)
    if response.status_code == 200:
        # Extract the CSV from the ZIP
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            with z.open('vocabulary.csv') as f:
                df = pd.read_csv(f)
        return df
    else:
        raise Exception("Failed to download DrugBank Vocabulary data")

# Function to populate the database
def populate_database():
    df = fetch_drugbank_vocabulary()
    for _, row in df.iterrows():
        drug = Drug(
            drugbank_id=row['DrugBank ID'],
            name=row['Common name'],
            description=row.get('Description', ''),
            synonyms=row.get('Synonyms', ''),
            cas_number=row.get('CAS Number', ''),
            unii=row.get('UNII', '')
        )
        db.session.add(drug)
    db.session.commit()

# API route to get all drugs
@app.route('/api/drugs', methods=['GET'])
def get_drugs():
    drugs = Drug.query.all()
    return jsonify([drug.to_dict() for drug in drugs])

# API route to get a specific drug by DrugBank ID
@app.route('/api/drugs/<drugbank_id>', methods=['GET'])
def get_drug(drugbank_id):
    drug = Drug.query.filter_by(drugbank_id=drugbank_id).first()
    if drug:
        return jsonify(drug.to_dict())
    return jsonify({'error': 'Drug not found'}), 404

# Initialize the database and populate it
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables
        if Drug.query.count() == 0:  # Only populate if the table is empty
            try:
                populate_database()
                print("Database populated successfully")
            except Exception as e:
                print(f"Error populating database: {e}")
    app.run(debug=True)