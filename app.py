import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt

# Charger les modèles sauvegardés
log_model = joblib.load(os.path.join('model.pkl'))
knn_model = joblib.load(os.path.join('knn_model.pkl'))
scaler = joblib.load(os.path.join('scaler.pkl'))

# Variables utilisées
features = ['Age', 'Marital', 'Expenses', 'Income', 'Amount', 'Price']

# Titre de l'application
st.title("Prédiction de Solvabilité Client")

# Choisir la méthode de saisie des données
mode = st.radio("Méthode de saisie des données :", ["Charger un fichier", "Saisie manuelle"])

if mode == "Charger un fichier":
    uploaded_file = st.file_uploader("Importer un fichier CSV", type=["csv"])
    
    if uploaded_file is not None:
        input_df = pd.read_csv(uploaded_file)
        st.write("Aperçu des données importées :", input_df)
        
        missing_columns = [col for col in features if col not in input_df.columns]
        if missing_columns:
            st.error(f"Colonnes manquantes : {', '.join(missing_columns)}. Veuillez vérifier le fichier.")
        else:
            st.write("Statistiques descriptives des données :")
            st.write(input_df.describe())
            
            st.write("Distribution des variables principales :")
            fig, ax = plt.subplots()
            input_df[features].hist(ax=ax, bins=15)
            st.pyplot(fig)
else:
    st.subheader("Remplir les informations du client :")
    
    def validate_input(input_data):
        errors = []
        for feature, value in input_data.items():
            if value <= 0:
                errors.append(f"{feature} doit être un nombre positif.")
        return errors
    
    input_data = {feature: st.number_input(feature, min_value=0.0, step=1.0) for feature in features}
    errors = validate_input(input_data)
    
    if errors:
        for error in errors:
            st.error(error)
    else:
        input_df = pd.DataFrame([input_data])

# Sélection du modèle
model_choice = st.selectbox("Choisir le modèle de prédiction :", ["Régression Logistique", "KNN"])

if st.button("Prédire la solvabilité"):
    X_scaled = scaler.transform(input_df)

    model = log_model if model_choice == "Régression Logistique" else knn_model

    prediction = model.predict(X_scaled)[0]
    probability = model.predict_proba(X_scaled)[0][1]

    statut = "Solvable" if prediction == "Solvable" or prediction == 1 else "Non Solvable"
    st.markdown(f"Résultat : {statut}")
    st.markdown(f"Probabilité de solvabilité : {probability:.2%}")
    
    st.write("Visualisation de la probabilité :")
    fig, ax = plt.subplots()
    ax.barh([0], [probability], color="green" if prediction == "Solvable" or prediction == 1 else "red")
    ax.set_xlim(0, 1)
    ax.set_yticks([0])
    ax.set_yticklabels(["Solvabilité"])
    ax.set_xlabel("Probabilité")
    ax.set_title("Probabilité de solvabilité")
    st.pyplot(fig)

    st.progress(probability)

    if probability < 0.5:
        st.warning("La probabilité de solvabilité est faible. Vous pourriez envisager d'améliorer certains aspects financiers.")
    else:
        st.success("La probabilité de solvabilité est élevée ! Vous êtes sur la bonne voie.")

    result_df = pd.DataFrame({
        'Prediction': [statut],
        'Probabilité de solvabilité': [f"{probability:.2%}"]
    })

    csv = result_df.to_csv(index=False)
    st.download_button(
        label="Télécharger les résultats (CSV)",
        data=csv,
        file_name='resultats_prediction.csv',
        mime='text/csv'
    )
