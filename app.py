import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Évaluation PRVG - Guide Situationnel Complet",
    page_icon="❤️",
    layout="wide"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .recommendation-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .parameter-section {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
    }
    .warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .invalid-param {
        color: #dc3545;
        background-color: #f8d7da;
        padding: 0.5rem;
        border-radius: 3px;
        margin: 0.2rem 0;
    }
    .valid-param {
        color: #155724;
        background-color: #d4edda;
        padding: 0.5rem;
        border-radius: 3px;
        margin: 0.2rem 0;
    }
    .caution-param {
        color: #856404;
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 3px;
        margin: 0.2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Dictionnaire des situations avec paramètres spécifiques pour PRVG
situations_data = {
    "FE VG ≥ 50% - Patient standard": {
        "valid_parameters": {
            "E/e' moyen": {"type": "number", "min": 5.0, "max": 25.0, "default": 10.0, "step": 0.1},
            "Volume auriculaire gauche indexé": {"type": "number", "min": 15, "max": 60, "default": 30, "step": 1},
            "Vitesse onde TR maximale": {"type": "number", "min": 1.5, "max": 4.5, "default": 2.5, "step": 0.1}
        },
        "additional_parameters": {
            "E/e' septal": {"type": "number", "min": 5.0, "max": 25.0, "default": 10.0, "step": 0.1},
            "E/e' latéral": {"type": "number", "min": 5.0, "max": 25.0, "default": 8.0, "step": 0.1},
            "Rapport E/A": {"type": "number", "min": 0.5, "max": 3.0, "default": 1.2, "step": 0.1}
        },
        "invalid_parameters": ["Aucun dans cette situation standard"],
        "recommendation": """
        **Algorithme ASE 2016 pour FE VG ≥ 50%:**
        
        **PRVG Normale si:**
        - E/e' moyen ≤ 8 ET Volume OG indexé ≤ 34 ml/m²
        
        **PRVG Élevée si:**
        - E/e' moyen > 14
        - OU si E/e' moyen 9-14 + ≥2 critères parmi:
          * E/e' septal > 15
          * Vitesse TR > 2.8 m/s
          * Volume OG indexé > 34 ml/m²
        """,
        "references": "ASE Guidelines for Diastolic Function 2016",
        "filling_pressure_possible": "Oui - Bien validé"
    },
    
    "FE VG < 50% - Dysfonction systolique": {
        "valid_parameters": {
            "Rapport E/A": {"type": "number", "min": 0.5, "max": 3.0, "default": 1.5, "step": 0.1},
            "E/e' moyen": {"type": "number", "min": 5.0, "max": 25.0, "default": 15.0, "step": 0.1},
            "Volume auriculaire gauche indexé": {"type": "number", "min": 15, "max": 60, "default": 40, "step": 1}
        },
        "additional_parameters": {
            "Temps de décélération (DT)": {"type": "number", "min": 120, "max": 300, "default": 180, "step": 5},
            "Vitesse onde TR maximale": {"type": "number", "min": 1.5, "max": 4.5, "default": 2.8, "step": 0.1}
        },
        "invalid_parameters": ["Aucun - Tous paramètres utilisables"],
        "recommendation": """
        **Algorithme ASE 2016 pour FE VG < 50%:**
        
        **Pattern restrictif (PRVG élevée):**
        - E/A ≥ 2 + DT < 160 ms
        - E/e' moyen > 14
        - Volume OG indexé > 34 ml/m²
        
        **Pattern de relaxation altérée (PRVG normale):**
        - E/A ≤ 0.8 + E ≤ 50 cm/s
        - E/e' moyen ≤ 14
        """,
        "references": "ASE Guidelines for Diastolic Function 2016",
        "filling_pressure_possible": "Oui - Très bien validé"
    },
    
    "Fibrillation auriculaire": {
        "valid_parameters": {
            "E/e' moyen": {"type": "number", "min": 5.0, "max": 25.0, "default": 12.0, "step": 0.1},
            "Volume auriculaire gauche indexé": {"type": "number", "min": 15, "max": 60, "default": 45, "step": 1},
            "Vitesse onde TR maximale": {"type": "number", "min": 1.5, "max": 4.5, "default": 2.9, "step": 0.1}
        },
        "additional_parameters": {
            "PAP systolique": {"type": "number", "min": 15, "max": 100, "default": 45, "step": 1},
            "Diamètre VG télédiastolique": {"type": "number", "min": 35, "max": 70, "default": 52, "step": 1}
        },
        "invalid_parameters": [
            "Rapport E/A - Non valide (variabilité cycle-cycle)",
            "Temps de décélération - Non valide (variabilité cycle-cycle)"
        ],
        "recommendation": """
        **Recommandations FA (ASE 2016, EACVI 2017):**
        
        **Paramètres VALIDES:**
        - E/e' moyen > 11 → PRVG élevée (spécificité 85%)
        - Volume OG indexé > 34 ml/m²
        - Vitesse TR > 2.8 m/s
        
        **Technique:**
        - Moyenne sur 5-10 cycles cardiaques
        - Éviter les cycles avec intervalles R-R extrêmes
        - Indexation des volumes à la surface corporelle
        """,
        "references": "ASE 2016, EACVI Consensus 2017",
        "filling_pressure_possible": "Oui - Avec limitations"
    },
    
    "Sténose mitrale": {
        "valid_parameters": {
            "Pression artérielle pulmonaire systolique": {"type": "number", "min": 15, "max": 100, "default": 50, "step": 1},
            "Volume auriculaire gauche indexé": {"type": "number", "min": 15, "max": 80, "default": 55, "step": 1},
            "Fonction ventriculaire droite": {"type": "select", "options": ["Normale", "Légèrement altérée", "Modérément altérée", "Sévèrement altérée"]}
        },
        "additional_parameters": {
            "Gradient moyen mitral": {"type": "number", "min": 2, "max": 40, "default": 12, "step": 1},
            "Surface mitrale (planimétrie)": {"type": "number", "min": 0.5, "max": 4.0, "default": 1.3, "step": 0.1}
        },
        "invalid_parameters": [
            "E/e' - NON VALIDE (gradient mitral modifie les vitesses)",
            "Rapport E/A - NON VALIDE (dépend de la sténose)",
            "Doppler tissulaire mitral - NON VALIDE"
        ],
        "recommendation": """
        **Évaluation PRVG dans la sténose mitrale (ESC 2021):**
        
        **LIMITATIONS IMPORTANTES:**
        - Les paramètres conventionnels de PRVG ne sont PAS VALIDES
        - La pression capillaire est élevée par mécanisme obstructif
        
        **Paramètres INDIRECTS de retentissement:**
        - PAP systolique > 50 mmHg → Retentissement significatif
        - Dilatation OG sévère (Volume > 60 ml/m²)
        - Altération fonction VD
        - Augmentation des pressions droites
        
        **Gold standard:** Cathétérisme gauche pour pression capillaire
        """,
        "references": "ESC Guidelines 2021, ASE 2017",
        "filling_pressure_possible": "NON - Méthodes conventionnelles non valides"
    },
    
    "Régurgitation mitrale sévère": {
        "valid_parameters": {
            "Volume auriculaire gauche indexé": {"type": "number", "min": 15, "max": 80, "default": 48, "step": 1},
            "Pression artérielle pulmonaire systolique": {"type": "number", "min": 15, "max": 100, "default": 42, "step": 1},
            "Fonction ventriculaire droite": {"type": "select", "options": ["Normale", "Légèrement altérée", "Modérément altérée", "Sévèrement altérée"]}
        },
        "additional_parameters": {
            "Volume régurgitant": {"type": "number", "min": 10, "max": 150, "default": 65, "step": 5},
            "Fraction de régurgitation": {"type": "number", "min": 10, "max": 80, "default": 45, "step": 1}
        },
        "invalid_parameters": [
            "E/e' - PRÉCAUTION (surestimation possible)",
            "Rapport E/A - Interprétation difficile"
        ],
        "recommendation": """
        **Évaluation PRVG dans la régurgitation mitrale (ASE 2017, ESC 2021):**
        
        **LIMITATIONS:**
        - E/e' peut SURESTIMER la PRVG réelle
        - Volume OG est le paramètre le plus fiable
        
        **Paramètres de décision chirurgicale:**
        - Volume OG > 60 ml/m² → Indication opératoire
        - PAP systolique > 50 mmHg → Retentissement
        - FEVG < 60% → Altération fonctionnelle
        - Fonction VD altérée → Pronostic péjoratif
        
        **Interprétation:**
        - Volume OG > 40 ml/m² suggère élévation chronique des pressions
        """,
        "references": "ASE 2017, ESC Guidelines 2021",
        "filling_pressure_possible": "Oui - Avec précautions d'interprétation"
    },
    
    "Prothèse valvulaire mitrale": {
        "valid_parameters": {
            "Volume auriculaire gauche indexé": {"type": "number", "min": 15, "max": 60, "default": 35, "step": 1},
            "Pression artérielle pulmonaire systolique": {"type": "number", "min": 15, "max": 100, "default": 38, "step": 1},
            "Gradient moyen prothèse": {"type": "number", "min": 2.0, "max": 15.0, "default": 6.0, "step": 0.5}
        },
        "additional_parameters": {
            "Index de performance prothèse (DVI)": {"type": "number", "min": 1.0, "max": 3.5, "default": 2.2, "step": 0.1},
            "Temps de pression-demi": {"type": "number", "min": 50, "max": 300, "default": 120, "step": 5}
        },
        "invalid_parameters": [
            "E/e' - NON VALIDE (artefacts prothèse)",
            "Doppler tissulaire - NON VALIDE",
            "Rapport E/A - Interprétation non standard"
        ],
        "recommendation": """
        **Évaluation PRVG avec prothèse mitrale (ASE 2019):**
        
        **LIMITATIONS SÉVÈRES:**
        - Paramètres conventionnels de PRVG NON VALIDES
        - Artefacts acoustiques importants
        
        **Paramètres INDIRECTS:**
        - Volume OG > 34 ml/m² → Suggestif d'élévation pressionnelle
        - PAP systolique > 40 mmHg → Retentissement
        - Gradient prothétique élevé → Dysfonction possible
        
        **Méthodes alternatives:**
        - Cathétérisme cardiaque
        - IRM cardiaque pour volumes
        """,
        "references": "ASE Recommendations 2019, EACVI 2018",
        "filling_pressure_possible": "NON - Méthodes conventionnelles non valides"
    },
    
    "Calcification annulaire mitrale sévère": {
        "valid_parameters": {
            "Volume auriculaire gauche indexé": {"type": "number", "min": 15, "max": 60, "default": 38, "step": 1},
            "Vitesse onde TR maximale": {"type": "number", "min": 1.5, "max": 4.5, "default": 2.7, "step": 0.1},
            "Flux veineux pulmonaire (rapport S/D)": {"type": "number", "min": 0.5, "max": 2.5, "default": 1.2, "step": 0.1}
        },
        "additional_parameters": {
            "PAP systolique": {"type": "number", "min": 15, "max": 100, "default": 42, "step": 1},
            "Temps de relaxation VG": {"type": "number", "min": 40, "max": 120, "default": 75, "step": 5}
        },
        "invalid_parameters": [
            "E/e' - CONTRE-INDIQUÉ (surestimation systématique)",
            "Doppler tissulaire mitral - NON FIABLE"
        ],
        "recommendation": """
        **Évaluation PRVG avec calcification annulaire (ASE 2016):**
        
        **LIMITATIONS CRITIQUES:**
        - E/e' SURESTIME la PRVG de 8-12 mmHg en moyenne
        - Pseudo-normalisation des paramètres
        
        **Paramètres ALTERNATIFS:**
        - Volume OG indexé > 34 ml/m²
        - Vitesse TR > 2.8 m/s
        - Rapport S/D flux pulmonaire < 1
        - PAP systolique > 40 mmHg
        
        **Considérations:**
        - L'élévation de PAP est le signe indirect le plus fiable
        - Volume OG reflète l'exposition chronique aux pressions élevées
        """,
        "references": "ASE Guidelines 2016, JASE 2018",
        "filling_pressure_possible": "Oui - Avec paramètres alternatifs seulement"
    }
}

# Titre principal
st.markdown('<div class="main-header">📊 Évaluation de la Pression de Remplissage VG - Guide Complet</div>', unsafe_allow_html=True)

# Sélection de la situation
st.sidebar.title("🔍 Sélection de la Situation")
situation = st.sidebar.selectbox(
    "Choisir la situation clinique:",
    list(situations_data.keys())
)

# Affichage des paramètres spécifiques
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Paramètres d'Évaluation")

selected_data = situations_data[situation]
user_inputs = {}

# Paramètres valides principaux
st.sidebar.markdown("**Paramètres valides pour cette situation:**")
for param_name, param_config in selected_data["valid_parameters"].items():
    if param_config["type"] == "number":
        user_inputs[param_name] = st.sidebar.number_input(
            param_name,
            min_value=param_config["min"],
            max_value=param_config["max"],
            value=param_config["default"],
            step=param_config["step"],
            key=f"valid_{param_name}"
        )
    elif param_config["type"] == "select":
        user_inputs[param_name] = st.sidebar.selectbox(
            param_name,
            param_config["options"],
            key=f"valid_{param_name}"
        )

# Paramètres additionnels
if selected_data.get("additional_parameters"):
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Paramètres additionnels:**")
    for param_name, param_config in selected_data["additional_parameters"].items():
        if param_config["type"] == "number":
            user_inputs[param_name] = st.sidebar.number_input(
                param_name,
                min_value=param_config["min"],
                max_value=param_config["max"],
                value=param_config["default"],
                step=param_config["step"],
                key=f"add_{param_name}"
            )
        elif param_config["type"] == "select":
            user_inputs[param_name] = st.sidebar.selectbox(
                param_name,
                param_config["options"],
                key=f"add_{param_name}"
            )

# Affichage principal
st.subheader(f"📋 {situation}")

# Évaluation de la faisabilité
st.markdown("### 📈 Évaluation de la PRVG Possible?")
if "NON" in selected_data["filling_pressure_possible"]:
    st.error(f"**{selected_data['filling_pressure_possible']}**")
elif "Avec limitations" in selected_data["filling_pressure_possible"]:
    st.warning(f"**{selected_data['filling_pressure_possible']}**")
else:
    st.success(f"**{selected_data['filling_pressure_possible']}**")

# Paramètres valides vs invalides
col1, col2 = st.columns(2)

with col1:
    st.markdown("### ✅ Paramètres Valides")
    for param in selected_data["valid_parameters"]:
        st.markdown(f'<div class="valid-param">✓ {param}</div>', unsafe_allow_html=True)
    
    if selected_data.get("additional_parameters"):
        for param in selected_data["additional_parameters"]:
            st.markdown(f'<div class="caution-param">↳ {param} (additionnel)</div>', unsafe_allow_html=True)

with col2:
    if selected_data["invalid_parameters"] and selected_data["invalid_parameters"][0] != "Aucun dans cette situation standard":
        st.markdown("### ❌ Paramètres Non Valides")
        for param in selected_data["invalid_parameters"]:
            st.markdown(f'<div class="invalid-param">✗ {param}</div>', unsafe_allow_html=True)

# Recommandations
st.markdown("### 💡 Recommandations Spécifiques")
st.markdown('<div class="recommendation-box">', unsafe_allow_html=True)
st.markdown(selected_data["recommendation"])
st.markdown('</div>', unsafe_allow_html=True)

# Références
st.markdown("### 📚 Références")
st.info(f"**Sources:** {selected_data['references']}")

# Résumé des paramètres saisis
if user_inputs:
    with st.expander("📋 Voir les paramètres saisis"):
        col1, col2 = st.columns(2)
        for i, (param, value) in enumerate(user_inputs.items()):
            if i % 2 == 0:
                col1.write(f"**{param}:** {value}")
            else:
                col2.write(f"**{param}:** {value}")

# Section d'avertissement générale
st.markdown("---")
st.markdown("""
<div class="warning">
<strong>⚠️ Avertissements Cliniques:</strong>
<ul>
<li>L'évaluation de la PRVG doit toujours être interprétée dans le contexte clinique global</li>
<li>En cas de discordance entre paramètres, privilégier une approche multimodale</li>
<li>Le cathétérisme cardiaque reste le gold standard en cas de doute</li>
<li>Les recommandations évoluent - consulter les dernières guidelines</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Informations supplémentaires
with st.expander("ℹ️ À propos de cette application"):
    st.write("""
    **Objectif:** Cette application fournit des recommandations spécifiques pour l'évaluation de la pression de remplissage du ventricule gauche (PRVG) selon différentes situations cliniques.
    
    **Sociétés référentes:**
    - ASE (American Society of Echocardiography)
    - EACVI (European Association of Cardiovascular Imaging) 
    - ESC (European Society of Cardiology)
    
    **Cas couverts:**
    - Fonction VG préservée et réduite
    - Fibrillation auriculaire
    - Valvulopathies mitrales (sténose, régurgitation)
    - Prothèses valvulaires
    - Calcifications annulaires
    
    **Mise à jour:** Basée sur les dernières recommandations disponibles
    **Usage:** À des fins éducatives et d'aide à la décision clinique
    """)
