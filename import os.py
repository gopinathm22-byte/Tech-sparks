import os
import json
from transformers import pipeline

# --- 1. SET UP API KEYS AND CREDENTIALS ---
# In a real application, you'd load these securely.
# For demonstration, we'll use placeholder values.
# IBM Watson Health API is no longer offered as a standalone service.
# You'd use services within the broader IBM Cloud/watsonx.
# For this example, we'll simulate a call to a hypothetical Watson API.

IBM_WATSON_API_KEY = "YOUR_IBM_WATSON_API_KEY"
IBM_WATSON_URL = "YOUR_IBM_WATSON_URL"

# --- 2. HUGGING FACE COMPONENT: ANALYZE PATIENT TEXT ---
def analyze_patient_notes(patient_notes):
    """
    Uses a Hugging Face model to extract key health insights from text.
    For this example, we use a named entity recognition (NER) pipeline
    to find diseases, symptoms, and drug names.
    """
    try:
        # We'll use a pre-trained biomedical NER model from the Hub.
        # "d4data/biomedical-ner-all" is a good example.
        nlp_pipeline = pipeline("ner", model="d4data/biomedical-ner-all")
        entities = nlp_pipeline(patient_notes)
        
        # Extract and organize the recognized entities
        health_insights = {
            "diseases": [e['word'] for e in entities if e['entity'] == 'DISEASE'],
            "symptoms": [e['word'] for e in entities if e['entity'] == 'SYMPTOM'],
            "drugs": [e['word'] for e in entities if e['entity'] == 'DRUG']
        }
        return health_insights
    except Exception as e:
        print(f"Error with Hugging Face pipeline: {e}")
        return {}

# --- 3. IBM WATSON COMPONENT: RETRIEVE DRUG DATA ---
def get_drug_data_from_watson(drug_name, patient_age, patient_weight_kg):
    """
    Simulates a call to an IBM Watson Health API to get structured
    drug information and age-specific dosage guidelines.
    """
    print(f"Calling IBM Watson for data on {drug_name} for a patient aged {patient_age}...")
    
    # In a real scenario, this would be an API call. We'll use a mock response.
    # The response would contain data from clinical trials and databases.
    mock_watson_response = {
        "drug_name": drug_name,
        "base_dosage_mg_kg": 50,  # Base adult dosage in mg/kg
        "age_modifications": [
            {"age_group": "pediatric (0-12 yrs)", "factor": 0.6, "notes": "Reduced dosage due to immature liver function."},
            {"age_group": "geriatric (65+ yrs)", "factor": 0.75, "notes": "Start with lower dose due to decreased renal clearance."},
            {"age_group": "adult (13-64 yrs)", "factor": 1.0, "notes": "Standard dosage."},
        ],
        "safety_profiles": {
            "renal_impairment_factor": 0.5,
            "liver_impairment_factor": 0.6
        }
    }
    
    return mock_watson_response

# --- 4. CORE LOGIC: COMBINE AND RECOMMEND ---
def recommend_dosage(patient_age, patient_weight_kg, drug_name, patient_notes):
    """
    Combines insights from Hugging Face and IBM Watson to give a final
    dosage recommendation.
    """
    print("--- Starting Dosage Recommendation Process ---")
    
    # Step A: Get insights from patient notes using Hugging Face
    print("Step A: Analyzing patient clinical notes...")
    patient_insights = analyze_patient_notes(patient_notes)
    print(f"Insights extracted: {patient_insights}")
    
    # Step B: Get structured drug data from IBM Watson
    print("\nStep B: Retrieving drug data from IBM Watson...")
    drug_data = get_drug_data_from_watson(drug_name, patient_age, patient_weight_kg)
    
    if not drug_data:
        return "Could not retrieve drug data. Recommendation failed."
        
    # Step C: Calculate the final dosage
    print("\nStep C: Calculating final dosage...")
    
    # Start with the base adult dosage
    base_dosage_mg = drug_data['base_dosage_mg_kg'] * patient_weight_kg
    final_dosage_mg = base_dosage_mg
    rationale = f"Base dosage calculated for patient weight ({patient_weight_kg} kg) is {final_dosage_mg:.2f} mg."
    
    # Apply age-specific modification factor
    age_factor = 1.0
    age_notes = ""
    for group in drug_data['age_modifications']:
        # This is a simple age check; a real system would be more robust.
        if (group['age_group'] == "pediatric (0-12 yrs)" and patient_age <= 12) or \
           (group['age_group'] == "geriatric (65+ yrs)" and patient_age >= 65):
            age_factor = group['factor']
            age_notes = group['notes']
            final_dosage_mg *= age_factor
            rationale += f"\n- Applied age-specific adjustment ({age_factor}) based on patient's age. {age_notes}"
            break

    # Add other safety factors based on patient insights (simulated here)
    if 'renal impairment' in patient_notes.lower() or 'kidney issues' in patient_notes.lower():
        renal_factor = drug_data['safety_profiles']['renal_impairment_factor']
        final_dosage_mg *= renal_factor
        rationale += f"\n- Further reduced dosage by {renal_factor} due to signs of renal impairment found in notes."

    final_dosage_mg = round(final_dosage_mg, 2)
    
    print("\n--- Recommendation Result ---")
    print(f"Recommended Dosage: **{final_dosage_mg} mg**")
    print("Rationale:")
    print(rationale)
    
    return final_dosage_mg, rationale

# --- 5. EXECUTION EXAMPLE ---
if __name__ == "__main__":
    # Example patient data
    patient_info = {
        "age": 7,
        "weight_kg": 25,
        "drug_name": "Amoxicillin",
        "notes": "Patient is a 7-year-old with a bacterial infection. No known allergies or kidney issues. Patient has a history of mild asthma."
    }
    
    # Get the recommendation
    recommendation, rationale = recommend_dosage(
        patient_info["age"],
        patient_info["weight_kg"],
        patient_info["drug_name"],
        patient_info["notes"]
    )
    
    # Example for an elderly patient with renal impairment
    print("\n\n" + "="*50 + "\n\n")
    elderly_patient = {
        "age": 75,
        "weight_kg": 70,
        "drug_name": "Lisinopril",
        "notes": "Patient is a 75-year-old with hypertension and mild renal impairment. Stable on current medications. Regular check-ups."
    }
    
    recommendation, rationale = recommend_dosage(
        elderly_patient["age"],
        elderly_patient["weight_kg"],
        elderly_patient["drug_name"],
        elderly_patient["notes"]
    )