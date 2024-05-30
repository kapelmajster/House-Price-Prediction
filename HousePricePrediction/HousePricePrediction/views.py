"""
Routes and views for the flask application.
"""

from datetime import datetime
from joblib import load
import os
from flask import jsonify, render_template, request
from sklearn.impute import SimpleImputer
import numpy as np
from HousePricePrediction import app

# Paths to model and preprocessing tools
model_path = os.path.join(app.root_path, 'models', 'rf2.joblib')
city_label_encoder_path = os.path.join(app.root_path, 'models', 'city_label_encoder.joblib')
scaler_path = os.path.join(app.root_path, 'models', 'numerical_scaler.joblib')

# Load the tools
model = load(model_path, mmap_mode='r')
city_label_encoder = load(city_label_encoder_path)
scaler = load(scaler_path)

# Load cities for autocomplete
def load_cities():
    cities_file_path = os.path.join(os.path.dirname(__file__), 'cities.txt')
    with open(cities_file_path, 'r') as f:
        return [line.strip() for line in f]
    
CITIES = load_cities()

# 'City_encoded' mean and standard deviation value for accurately standardise new city data
city_mean = 580.3745
city_std = 319.3460

# Mean values for floor area, current energy rating, and potential energy rating
mean_values = {
    'Bungalow': {
        'floor_area': {1: 58, 2: 50, 3: 63, 4: 79, 5: 97, 6: 121, 7: 146, 8: 175, 9: 197},
        'property_age': {1: 56, 2: 54, 3: 57, 4: 59, 5: 59, 6: 60, 7: 61, 8: 61, 9: 61},
        'current_energy_rating': {1: 3, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4},
        'potential_energy_rating': {1: 5, 2: 6, 3: 6, 4: 5, 5: 5, 6: 5, 7: 5, 8: 5, 9: 5},
    },
    'Flat': {
        'floor_area': {1: 37, 2: 45, 3: 61, 4: 76, 5: 95, 6: 122, 7: 147, 8: 180, 9: 213},
        'property_age': {1: 49, 2: 56, 3: 57, 4: 68, 5: 71, 6: 76, 7: 79, 8: 78, 9: 79},
        'current_energy_rating': {1: 4, 2: 4, 3: 5, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4},
        'potential_energy_rating': {1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 5, 7: 5, 8: 5, 9: 5},
    },
    'House': {
        'floor_area': {1: 69, 2: 56, 3: 65, 4: 78, 5: 92, 6: 118, 7: 144, 8: 173, 9: 204},
        'property_age': {1: 63, 2: 57, 3: 62, 4: 68, 5: 67, 6: 63, 7: 59, 8: 58, 9: 59},
        'current_energy_rating': {1: 3, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4},
        'potential_energy_rating': {1: 5, 2: 6, 3: 6, 4: 6, 5: 6, 6: 5, 7: 5, 8: 5, 9: 5},
    },             
    'Maisonette': {
        'floor_area': {1: 47, 2: 46, 3: 63, 4: 80, 5: 97, 6: 122, 7: 146, 8: 187, 9: 216},
        'property_age': {1: 52, 2: 57, 3: 66, 4: 72, 5: 75, 6: 82, 7: 84, 8: 81, 9: 85},
        'current_energy_rating': {1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4, 9: 4},
        'potential_energy_rating': {1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 5, 7: 5, 8: 5, 9: 5},
    },            
    'Park home': {
        'floor_area': {1: 51, 2: 38, 3: 49, 4: 65, 5: 72},
        'property_age': {1: 38, 2: 50, 3: 38, 4: 29, 5: 30},
        'current_energy_rating': {1: 3, 2: 3, 3: 3, 4: 3, 5: 4},
        'potential_energy_rating': {1: 4, 2: 4, 3: 4, 4: 4, 5: 5},
    },            
    'Retirement Property': {
        'floor_area': {1: 51, 2: 69, 3: 76, 4: 88, 5: 96, 6: 119, 7: 99},
        'property_age': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1},
        'current_energy_rating': {1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 5, 7: 5},
        'potential_energy_rating': {1: 5, 2: 5, 3: 6, 4: 6, 5: 6, 6: 6, 7: 5},
    },    
}

# Month numbers to names
month_to_names = {
    1: 'January', 2: 'February', 3: 'March',
    4: 'April', 5: 'May', 6: 'June', 
    7: 'July', 8: 'August', 9: 'September',
    10: 'October', 11: 'November', 12: 'December'
}

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Process form inputs
        city = request.form.get('city', '')
        rooms = int(request.form.get('number_heated_rooms', 1))
        property_type = request.form.get('property_type', '')
        property_form = request.form.get('property_form', '')        
        current_energy_rating_input = request.form.get('current_energy_rating', '')
        potential_energy_rating_input = request.form.get('potential_energy_rating', '')
        month = int(request.form.get('month', datetime.now().month))
        year = int(request.form.get('year', datetime.now().year))
        
        # Handle "Don't Know" selections 
        floor_area_unknown = 'floor_area_unknown' in request.form
        current_energy_rating_unknown = 'current_energy_rating_unknown' in request.form
        potential_energy_rating_unknown = 'potential_energy_rating_unknown' in request.form

        # Assign mean values if "Don't Know" is selected
        floor_area = get_mean_value(property_type, rooms, 'floor_area') if floor_area_unknown else float(request.form.get('floor_area'))
        current_energy_rating = get_mean_value(property_type, rooms, 'current_energy_rating') if current_energy_rating_input == "Don't Know" else float(current_energy_rating_input)
        potential_energy_rating = get_mean_value(property_type, rooms, 'potential_energy_rating') if potential_energy_rating_input == "Don't Know" else float(potential_energy_rating_input)
       
        property_age_option = request.form.get('property_age_option')

        if property_age_option == "New Building":
            new_build = True
            property_age = 1  # New buildings have an age of 1
        elif property_age_option == "Don't Know":
            new_build = False
            property_age = get_mean_value(property_type, rooms, 'property_age')  
        elif property_age_option == "Specific Age":
            new_build = False
            property_age_input = request.form.get('property_age', '')
            property_age = int(property_age_input) if property_age_input.isdigit() else get_mean_value(property_type, rooms, 'property_age')
        else:
            # Fallback if no option was selected, or an unexpected value was received
            new_build = False
            property_age = get_mean_value(property_type, rooms, 'property_age')
    
        # Map the month number to the month name
        month_name = month_to_names.get(month)
    
        # Prepare features for prediction
        features = prepare_features(city, rooms, property_type, property_form, new_build, property_age, month, year, current_energy_rating, potential_energy_rating, floor_area)

        # Debug: Print the inputs and processed features in console
        print(f"Debug - Inputs: City: {city}, Rooms: {rooms}, Property Type: {property_type}, Property Form: {property_form}, New Build: {'Yes' if new_build else 'No'}, Current Energy Rating: {current_energy_rating}, Potential Energy Rating: {potential_energy_rating}, Total Floor Area: {floor_area}, Property Age: {property_age}, Month: {month}, Year: {year}")
        print(f"Debug - Final Feature Vector: {features}")
        
        # Make prediction
        prediction = model.predict(features)[0]
        prediction_text = f"The {'new' if new_build else 'existing'} {rooms}-room {property_form} {property_type} in {city} in {month_name} {year} will be estimated at {prediction:.0f} GBP."

        return render_template('index.html', month=month_name, prediction=prediction_text)

    return render_template('index.html', title='Home Page')


# Function to get mean value
def get_mean_value(property_type, rooms, value_type):
    # Access the dictionary structure to get the mean value
    try:
        return mean_values[property_type][value_type][rooms]
    except KeyError:
        # Default mean value if the exact combination is not found
        default_mean_values = {
            'floor_area': 75,  # Default floor area if not found
            'current_energy_rating': 3,  # Default current energy rating if not found
            'potential_energy_rating': 5,  # Default potential energy rating if not found
            'property_age': 50  # Default property age if not found
        }
        return default_mean_values[value_type]

# Function to prepare features
def prepare_features(city, rooms, property_type, property_form, new_build, property_age, month, year, current_energy_rating, potential_energy_rating, floor_area):
    # Initialise an array to collect features
    features = []

    # City encoding and standardisation
    city_encoded = city_label_encoder.transform([city])[0]
    city_standardised = (city_encoded - city_mean) / city_std
    features.append(city_standardised)

    # Convert new_build flag to binary
    new_build_binary = int(new_build)

    # Prepare numerical features for scaling 
    numerical_features = np.array([current_energy_rating, potential_energy_rating, floor_area, rooms, property_age]).reshape(1, -1)

    # Scale the numerical features
    numerical_features_scaled = scaler.transform(numerical_features)

    # Append scaled numerical features to the features list
    features.extend(numerical_features_scaled.flatten())

    # Append new_build_binary, month, year directly 
    features.extend([new_build_binary, month, year])

    # One-hot encode property type and form
    property_type_vector = encode_property_type(property_type)
    property_form_vector = encode_property_form(property_form)
    features.extend(property_type_vector)
    features.extend(property_form_vector)

    # Debug: Ensure the final features array matches the expected input shape for the model
    final_features = np.array(features)
    if len(final_features) != 23:
        raise ValueError(f"Expected 23 features, but got {len(final_features)}")

    return final_features.reshape(1, -1)


# Encoding functions based on machine learning structure
def encode_property_type(property_type):
    property_types = ['Bungalow', 'Flat', 'House', 'Maisonette', 'Park home', 'Retirement Property']
    vector = np.zeros(len(property_types))
    try:
        index = property_types.index(property_type)
        vector[index] = 1
    except ValueError:
        # Handle unknown property_type
        print(f'Unknown property type: {property_type}')
    return vector

def encode_property_form(property_form):
    property_forms = ['Detached', 'Enclosed End-Terrace', 'Enclosed Mid-Terrace', 'End-Terrace', 'Mid-Terrace', 'NO DATA!', 'Semi-Detached', 'Terraced']
    vector = np.zeros(len(property_forms))
    try:
        index = property_forms.index(property_form)
        vector[index] = 1
    except ValueError:
        # Handle unknown property_form
        print(f'Unknown property form: {property_form}')
    return vector

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '')
    suggestions = [city for city in CITIES if city.upper().startswith(query.upper())]
    return jsonify(suggestions)

@app.context_processor
def inject_year():
    return {'year': datetime.now().year}
