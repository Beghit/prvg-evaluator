import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Guide Échocardiographie Complet - Cardiologie",
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
    .section-header {
        font-size: 1.8rem;
        color: #2e86ab;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #2e86ab;
        padding-bottom: 0.5rem;
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
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .step-box {
        background-color: #e9ecef;
        border-left: 4px solid #6c757d;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .valid-param {
        color: #155724;
        background-color: #d4edda;
        padding: 0.5rem;
        border-radius: 3px;
        margin: 0.2rem 0;
    }
    .invalid-param {
        color: #721c24;
        background-color: #f8d7da;
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

# Titre principal
st.markdown('<div class="main-header">📊 Guide Échocardiographie Complet - Évaluations Avancées</div>', unsafe_allow_html=True)

# ============================================================================
# DICTIONNAIRES DES DONNÉES
# ============================================================================

# Dictionnaire pour PRVG
situations_prvg = {
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

# Dictionnaire des évaluations disponibles
evaluations = {
    "Pression Remplissage VG (PRVG)": {
        "icon": "🫀",
        "description": "Évaluation de la pression de remplissage VG selon situations cliniques",
        "reference": "ASE 2016, ESC 2021"
    },
    "Dysfonction Diastolique - Algorithme Complet": {
        "icon": "📊", 
        "description": "Évaluation complète de la fonction diastolique selon ESC 2016",
        "reference": "ESC 2016, ASE 2016, JASE 2020"
    },
    "Probabilité d'HTAP - ESC 2022": {
        "icon": "🌊",
        "description": "Évaluation de la probabilité d'hypertension artérielle pulmonaire",
        "reference": "ESC/ERS 2022"
    },
    "Péricardite Constrictive vs Restrictive": {
        "icon": "🔄",
        "description": "Différenciation entre constriction péricardique et cardiomyopathie restrictive",
        "reference": "ESC 2015, ASE 2021"
    },
    "Évaluation Prothèses Valvulaires": {
        "icon": "⚙️",
        "description": "Évaluation pas-à-pas des prothèses valvulaires mitrales et aortiques",
        "reference": "ESC 2021, ASE 2017, EACVI 2021"
    }
}

# ============================================================================
# SIDEBAR - SÉLECTION DE L'ÉVALUATION
# ============================================================================

st.sidebar.title("🔍 Sélection de l'Évaluation")
evaluation_choice = st.sidebar.selectbox(
    "Choisir l'évaluation:",
    list(evaluations.keys()),
    format_func=lambda x: f"{evaluations[x]['icon']} {x}"
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Description:** {evaluations[evaluation_choice]['description']}")
st.sidebar.markdown(f"**Référence:** {evaluations[evaluation_choice]['reference']}")

# ============================================================================
# ÉVALUATION 1: PRVG
# ============================================================================

if evaluation_choice == "Pression Remplissage VG (PRVG)":
    
    st.markdown("## 🫀 Évaluation de la Pression de Remplissage VG - Guide Situationnel")
    
    # Sélection de la situation pour PRVG
    st.sidebar.markdown("---")
    st.sidebar.subheader("🩺 Situation Clinique")
    situation = st.sidebar.selectbox(
        "Choisir la situation clinique:",
        list(situations_prvg.keys())
    )
    
    # Affichage des paramètres spécifiques
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Paramètres d'Évaluation")
    
    selected_data = situations_prvg[situation]
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

# ============================================================================
# ÉVALUATION 2: DYSFONCTION DIASTOLIQUE
# ============================================================================

elif evaluation_choice == "Dysfonction Diastolique - Algorithme Complet":
    
    st.markdown("## 🫀 Évaluation de la Dysfonction Diastolique - Algorithme Complet ESC")
    
    with st.expander("📋 **Paramètres à mesurer - Guide pratique**", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📏 Doppler pulsé mitral:**
            - Vitesse onde E (pic précoce)
            - Vitesse onde A (contraction auriculaire)  
            - Rapport E/A
            - Temps de décélération (DT)
            - Temps de relaxation isovolumétrique (IVRT)
            
            **🎯 Doppler tissulaire:**
            - e' septal (annulus mitral)
            - e' latéral (annulus mitral)
            - Rapport E/e' moyen
            - Rapport E/e' septal
            """)
            
        with col2:
            st.markdown("""
            **📊 Paramètres structurels:**
            - Volume oreillette gauche indexé (ml/m²)
            - Masse VG indexée (g/m²)
            - Diamètre OG (mm)
            
            **🌀 Paramètres avancés (souvent oubliés):**
            - Ratio S/D flux pulmonaire
            - Durée Ar - A (différence durée onde Ar et A)
            - Vitesse de propagation (Vp) - Doppler couleur
            - Temps de relaxation VG en TDI
            - Strain longitudinal global
            """)
    
    # Paramètres d'entrée
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Paramètres du Patient")
    
    fevg = st.sidebar.selectbox("FE VG (%)", ["≥50%", "41-49%", "≤40%"])
    age = st.sidebar.number_input("Âge (années)", 20, 100, 65)
    
    st.sidebar.markdown("**Paramètres Doppler:**")
    e_vitesse = st.sidebar.number_input("Vitesse E (cm/s)", 20, 200, 80)
    a_vitesse = st.sidebar.number_input("Vitesse A (cm/s)", 20, 150, 70)
    e_a_ratio = st.sidebar.number_input("Rapport E/A", 0.5, 3.0, 1.2, 0.1)
    dt = st.sidebar.number_input("Temps décélération (ms)", 100, 400, 180)
    
    st.sidebar.markdown("**Doppler tissulaire:**")
    e_prime_septal = st.sidebar.number_input("e' septal (cm/s)", 3.0, 20.0, 7.0, 0.1)
    e_prime_lateral = st.sidebar.number_input("e' latéral (cm/s)", 3.0, 20.0, 9.0, 0.1)
    e_e_prime_moyen = st.sidebar.number_input("E/e' moyen", 5.0, 25.0, 10.0, 0.1)
    
    st.sidebar.markdown("**Paramètres structurels:**")
    volume_og_index = st.sidebar.number_input("Volume OG indexé (ml/m²)", 15, 80, 35)
    tr_vitesse = st.sidebar.number_input("Vitesse TR max (m/s)", 1.5, 4.5, 2.5, 0.1)
    
    # Algorithme de décision
    st.markdown("## 🔍 **Algorithme d'Interprétation ESC 2016**")
    
    if fevg == "≥50%":
        st.markdown("### **FE VG Préservée (≥50%)**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Critères PRVG Normale:**")
            if e_e_prime_moyen <= 8 and volume_og_index <= 34:
                st.markdown('<div class="success-box">✅ PRVG NORMALE<br>E/e\' moyen ≤8 + Volume OG ≤34 ml/m²</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="danger-box">❌ Non rempli</div>', unsafe_allow_html=True)
                
        with col2:
            st.markdown("**Critères PRVG Élevée:**")
            if e_e_prime_moyen > 14:
                st.markdown('<div class="danger-box">✅ PRVG ÉLEVÉE<br>E/e\' moyen >14</div>', unsafe_allow_html=True)
            elif e_e_prime_moyen > 8 and e_e_prime_moyen <= 14:
                st.markdown("**Zone grise - Évaluer critères secondaires:**")
                criteres = 0
                if e_prime_septal < 7: criteres += 1
                if tr_vitesse > 2.8: criteres += 1
                if volume_og_index > 34: criteres += 1
                
                if criteres >= 2:
                    st.markdown(f'<div class="danger-box">✅ PRVG ÉLEVÉE<br>{criteres}/3 critères positifs</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="warning">⚠️ Indéterminé<br>{criteres}/3 critères positifs</div>', unsafe_allow_html=True)
    
    else:  # FE VG réduite
        st.markdown("### **FE VG Réduite (<50%)**")
        
        # Classification des patterns
        if e_a_ratio <= 0.8 and e_vitesse <= 50:
            st.markdown('<div class="success-box">📊 **Pattern de Relaxation Altérée**<br>PRVG probablement normale</div>', unsafe_allow_html=True)
        elif e_a_ratio >= 2 and dt < 160:
            st.markdown('<div class="danger-box">📊 **Pattern Restrictif**<br>PRVG élevée</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning">📊 **Pattern Pseudonormal**<br>Évaluer E/e\' et volume OG</div>', unsafe_allow_html=True)
    
    # Paramètres avancés souvent oubliés
    st.markdown("## 🔬 **Paramètres Avancés - Souvent Oubliés**")
    
    with st.expander("📐 **Comment mesurer les paramètres avancés**"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📏 Ratio S/D flux pulmonaire:**
            - Mesurer en Doppler pulsé veines pulmonaires
            - Ondes S (systolique) et D (diastolique)
            - **Interprétation:**
              * S/D < 1 → PRVG élevée
              * S/D > 1 → Normal
            
            **⏱️ Durée Ar - A:**
            - Mesurer durée onde Ar (flux pulmonaire rétrograde)
            - Mesurer durée onde A (flux mitral)
            - **Interprétation:**
              * Ar-A > 30 ms → PRVG élevée
            """)
            
        with col2:
            st.markdown("""
            **🌀 Vitesse de propagation (Vp):**
            - Mode M couleur avec ligne de base mitral
            - Mesurer pente de propagation première onde diastolique
            - **Interprétation:**
              * Vp < 45 cm/s → Dysfonction diastolique
            
            **📉 Strain diastolique:**
            - Strain rate précoce diastolique
            - **Interprétation:**
              * SR E < 1.0 s⁻¹ → Dysfonction diastolique
            """)
    
    st.markdown("### **Valeurs Seuils Recommandées**")
    
    data = {
        "Paramètre": ["E/e' septal", "E/e' latéral", "Volume OG indexé", "Vitesse TR", "Rapport S/D pulmonaire", "Ar-A durée"],
        "Normal": ["≤8", "≤8", "≤34 ml/m²", "≤2.8 m/s", ">1", "<30 ms"],
        "Anormal": [">15", ">12", ">34 ml/m²", ">2.8 m/s", "<1", ">30 ms"]
    }
    
    st.table(data)

# ============================================================================
# ÉVALUATION 3: PROBABILITÉ HTAP ESC 2022
# ============================================================================

elif evaluation_choice == "Probabilité d'HTAP - ESC 2022":
    
    st.markdown("## 🌊 Probabilité d'Hypertension Artérielle Pulmonaire - ESC/ERS 2022")
    
    st.markdown("""
    <div class="recommendation-box">
    <strong>📋 Définition HTAP:</strong> PAPm ≥20 mmHg au repos + PVR ≥3 UW<br>
    <strong>⚠️ Attention:</strong> Ces algorithmes donnent une probabilité, pas un diagnostic définitif
    </div>
    """, unsafe_allow_html=True)
    
    # Paramètres d'entrée
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Paramètres Échocardiographiques")
    
    tr_vitesse = st.sidebar.number_input("Vitesse TR maximale (m/s)", 1.5, 5.0, 2.8, 0.1)
    paps = st.sidebar.number_input("PAP systolique (mmHg)", 15, 120, 40)
    vc_inferieur = st.sidebar.selectbox("VCI diamètre/collapsibilité", ["Normal (≤21 mm + collapsus >50%)", "Dilatée (≥21 mm) ou collapsus <50%", "Dilatée fixe"])
    rv_ra_ratio = st.sidebar.selectbox("Rapport VD/OG (apical 4 cavités)", ["<1.0", "≥1.0"])
    septum_paradoxal = st.sidebar.selectbox("Mouvement septum paradoxal", ["Non", "Oui"])
    acceleration_time = st.sidebar.number_input("Temps d'accélération VTID (ms)", 40, 120, 80)
    
    # Algorithme pour patients sans cardiopathie gauche
    st.markdown("## 🎯 **Algorithme Probabilité HTAP - Patients sans Cardiopathie Gauche**")
    
    # Calcul du score
    score = 0
    if tr_vitesse <= 2.8 or tr_vitesse == 2.9:
        score += 0
    elif tr_vitesse <= 3.4:
        score += 1
    else:
        score += 2
    
    if vc_inferieur == "Normal (≤21 mm + collapsus >50%)":
        score += 0
    elif vc_inferieur == "Dilatée (≥21 mm) ou collapsus <50%":
        score += 1
    else:
        score += 2
    
    if rv_ra_ratio == "<1.0":
        score += 0
    else:
        score += 1
    
    if septum_paradoxal == "Non":
        score += 0
    else:
        score += 1
    
    # Interprétation du score
    st.markdown(f"### **Score de probabilité: {score}/6 points**")
    
    if score <= 1:
        st.markdown('<div class="success-box">🟢 **PROBABILITÉ FAIBLE**<br>Score ≤1 - HTAP peu probable</div>', unsafe_allow_html=True)
    elif score == 2:
        st.markdown('<div class="warning">🟡 **PROBABILITÉ INTERMÉDIAIRE**<br>Score = 2 - Investigations complémentaires nécessaires</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="danger-box">🔴 **PROBABILITÉ ÉLEVÉE**<br>Score ≥3 - HTAP probable, cathétérisme recommandé</div>', unsafe_allow_html=True)
    
    # Signes supplémentaires
    st.markdown("## 🔍 **Signes Échocardiographiques Supplémentaires**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Paramètres VD:**")
        st.markdown("- TAPSE < 17 mm → Dysfonction VD")
        st.markdown("- S' tricuspide < 9.5 cm/s → Dysfonction VD")
        st.markdown("- FAC VD < 35% → Dysfonction VD")
        st.markdown("- Strain longitudinal VD > -20% → Altération")
        
    with col2:
        st.markdown("**📈 Paramètres Artère Pulmonaire:**")
        st.markdown("- Temps accélération < 80 ms → Suggestif HTAP")
        st.markdown("- Notch mésosystolique → HTAP pré-capillaire")
        st.markdown("- Diamètre AP > 25 mm → Dilatation")
    
    # Algorithme pour patients avec cardiopathie gauche
    st.markdown("## 💔 **Algorithme pour Patients avec Cardiopathie Gauche**")
    
    st.markdown("""
    <div class="step-box">
    <strong>Étape 1:</strong> Évaluer la probabilité HTAP sans contexte<br>
    <strong>Étape 2:</strong> Si probabilité ≥ intermédiaire, rechercher:<br>
    &nbsp;&nbsp;• Discordance sévère VD/atteinte VG<br>
    &nbsp;&nbsp;• PVR ≥ 5 UW par écho<br>
    &nbsp;&nbsp;• Temps accélération VTID très court (<65 ms)<br>
    <strong>Étape 3:</strong> Si présent → Cathétérisme pour confirmation
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# ÉVALUATION 4: PÉRICARDITE CONSTRICTIVE vs RESTRICTIVE
# ============================================================================

elif evaluation_choice == "Péricardite Constrictive vs Restrictive":
    
    st.markdown("## 🔄 Différenciation Péricardite Constrictive vs Cardiomyopathie Restrictive")
    
    st.markdown("""
    <div class="warning">
    <strong>⚠️ Définition:</strong><br>
    • <strong>Constriction péricardique:</strong> Péricarde rigide limitant le remplissage diastolique<br>
    • <strong>Cardiomyopathie restrictive:</strong> Myocarde rigide avec compliance réduite
    </div>
    """, unsafe_allow_html=True)
    
    # Paramètres d'entrée
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Critères Différentiels")
    
    variation_respiratoire = st.sidebar.selectbox("Variation respiratoire flux mitral E", ["<10%", "≥25%", "Intermédiaire (10-25%)"])
    septal_bounce = st.sidebar.selectbox("Mouvement septal paradoxal", ["Présent", "Absent"])
    annulus_reverse = st.sidebar.selectbox("Annulus paradoxal (e' latéral > e' septal)", ["Oui", "Non"])
    vp_couleur = st.sidebar.number_input("Vitesse propagation Vp (cm/s)", 30, 80, 45)
    strain_longitudinal = st.sidebar.number_input("Strain longitudinal global (%)", -25, -10, -18)
    
    st.sidebar.markdown("**Paramètres structurels:**")
    epaisseur_pericarde = st.sidebar.selectbox("Épaisseur péricarde", ["Normal (<3 mm)", "Épaissi (≥3 mm)", "Calcifié"])
    fonction_vg = st.sidebar.selectbox("Fonction VG", ["Préservée", "Légèrement altérée", "Modérément altérée"])
    
    # Algorithme de décision
    st.markdown("## 🎯 **Arbre Décisionnel ASE 2021**")
    
    score_constriction = 0
    score_restrictif = 0
    
    # Critères constriction
    if variation_respiratoire == "≥25%":
        score_constriction += 2
    if septal_bounce == "Présent":
        score_constriction += 2
    if annulus_reverse == "Oui":
        score_constriction += 1
    if epaisseur_pericarde != "Normal (<3 mm)":
        score_constriction += 1
    
    # Critères restrictif
    if variation_respiratoire == "<10%":
        score_restrictif += 2
    if fonction_vg != "Préservée":
        score_restrictif += 1
    if strain_longitudinal > -15:  # Moins négatif = plus altéré
        score_restrictif += 2
    
    st.markdown(f"### **Score Constriction: {score_constriction}/6**")
    st.markdown(f"### **Score Restrictif: {score_restrictif}/5**")
    
    if score_constriction >= 3 and score_constriction > score_restrictif:
        st.markdown('<div class="danger-box">🎯 **CONSTRICTION PÉRICARDIQUE PROBABLE**<br>Score élevé pour constriction</div>', unsafe_allow_html=True)
    elif score_restrictif >= 3 and score_restrictif > score_constriction:
        st.markdown('<div class="danger-box">🎯 **CARDIOMYOPATHIE RESTRICTIVE PROBABLE**<br>Score élevé pour restriction</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="warning">⚠️ **DIAGNOSTIC INDÉTERMINÉ**<br>Rechercher d\'autres causes ou imagerie complémentaire</div>', unsafe_allow_html=True)
    
    # Tableau comparatif
    st.markdown("## 📊 **Tableau Comparatif des Critères**")
    
    data_comparatif = {
        "Paramètre": ["Variation respiratoire onde E", "Mouvement septum", "Annulus mitral", "Épaisseur péricarde", "Fonction VG", "Strain longitudinal"],
        "Constriction": ["≥25%", "Bounce paradoxal", "e' latéral > e' septal", "Épaissi/calcifié", "Préservée", "Relativement préservé"],
        "Restrictive": ["<10%", "Normal ou réduit", "e' latéral ≈ e' septal", "Normal", "Altérée", "Altéré (≥ -15%)"]
    }
    
    st.table(data_comparatif)
    
    # Techniques de mesure spécifiques
    st.markdown("## 🔬 **Techniques de Mesure Recommandées**")
    
    with st.expander("📐 **Comment mesurer la variation respiratoire**"):
        st.markdown("""
        1. **Doppler pulsé mitral** en apical 4 cavités
        2. Demander au patient de respirer calmement
        3. Mesurer la vitesse E sur **3 cycles expiratoires** et **3 cycles inspiratoires**
        4. Calcul: (E_expir - E_inspir) / E_expir × 100
        5. **Seuil constriction:** Variation ≥25%
        """)
    
    with st.expander("📐 **Comment identifier le septal bounce**"):
        st.markdown("""
        1. **Mode M** en parasternal axe court
        2. Ligne de base au **niveau des piliers**
        3. Rechercher mouvement septal **brusque en début diastole**
        4. **Pattern caractéristique:** Mouvement vers la droite en diastole
        """)

# ============================================================================
# ÉVALUATION 5: PROTHÈSES VALVULAIRES
# ============================================================================

elif evaluation_choice == "Évaluation Prothèses Valvulaires":
    
    st.markdown("## ⚙️ Évaluation des Prothèses Valvulaires - Guide Pas-à-Pas")
    
    type_prothese = st.sidebar.selectbox("Type de prothèse", [
        "Prothèse aortique mécanique",
        "Prothèse aortique biologique", 
        "Prothèse mitrale mécanique",
        "Prothèse mitrale biologique"
    ])
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Paramètres Hémodynamiques")
    
    if "aortique" in type_prothese:
        gradient_moyen = st.sidebar.number_input("Gradient moyen (mmHg)", 5, 60, 15)
        vmax = st.sidebar.number_input("Vitesse max (m/s)", 1.5, 5.0, 2.5, 0.1)
        eoa = st.sidebar.number_input("Surface effective (cm²)", 0.5, 3.0, 1.5, 0.1)
        dvi = st.sidebar.number_input("Index de performance (DVI)", 0.1, 0.5, 0.35, 0.01)
    else:  # Mitrale
        gradient_moyen = st.sidebar.number_input("Gradient moyen (mmHg)", 2, 15, 5)
        pht = st.sidebar.number_input("Temps pression-demi (ms)", 50, 300, 120)
        eoa = st.sidebar.number_input("Surface effective (cm²)", 0.5, 3.0, 1.8, 0.1)
    
    st.sidebar.markdown("**Régurgitation:**")
    regurgitation = st.sidebar.selectbox("Régurgitation para-valvulaire", ["Absente", "Légère", "Modérée", "Sévère"])
    
    # Algorithme d'évaluation
    st.markdown(f"## 🔍 **Évaluation de la {type_prothese}**")
    
    st.markdown("### 📋 **Étape 1: Mesures Standard Obligatoires**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Prothèse Aortique:**")
        st.markdown("- Gradient moyen et pic")
        st.markdown("- Surface effective (EOA)")
        st.markdown("- Index de performance (DVI)")
        st.markdown("- Accélération temps")
        st.markdown("- Vitesse VTI LVOT/Prothèse")
        
    with col2:
        st.markdown("**📊 Prothèse Mitrale:**")
        st.markdown("- Gradient moyen")
        st.markdown("- Temps pression-demi (PHT)")
        st.markdown("- Surface effective")
        st.markdown("- Pression artérielle pulmonaire")
        st.markdown("- Fonction VG")
    
    st.markdown("### 🎯 **Étape 2: Critères de Dysfonction**")
    
    if "aortique" in type_prothese:
        st.markdown("**Critères de Sténose Prothétique Aortique (ESC 2021):**")
        
        if gradient_moyen > 35 and eoa < 1.0 and dvi < 0.25:
            st.markdown('<div class="danger-box">🔴 **DYSFONCTION SÉVÈRE**<br>Tous critères présents</div>', unsafe_allow_html=True)
        elif gradient_moyen > 20 or eoa < 1.2 or dvi < 0.30:
            st.markdown('<div class="warning">🟡 **DYSFONCTION MODÉRÉE**<br>Au moins 1 critère</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box">🟢 **FONCTION NORMALE**<br>Critères dans les limites</div>', unsafe_allow_html=True)
            
    else:  # Mitrale
        st.markdown("**Critères de Sténose Prothétique Mitrale (ASE 2017):**")
        
        if gradient_moyen > 10 and eoa < 1.0:
            st.markdown('<div class="danger-box">🔴 **DYSFONCTION SÉVÈRE**</div>', unsafe_allow_html=True)
        elif gradient_moyen > 7 or eoa < 1.3:
            st.markdown('<div class="warning">🟡 **DYSFONCTION MODÉRÉE**</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box">🟢 **FONCTION NORMALE**</div>', unsafe_allow_html=True)
    
    st.markdown("### 🔬 **Étape 3: Recherche de Complications**")
    
    with st.expander("📋 **Checklist complications prothèses mécaniques**"):
        st.markdown("""
        - **Thrombose:** Gradient augmenté progressif
        - **Pannus:** Gradient augmenté progressif + EOA réduite
        - **Fuites para-valvulaires:** Jet excentrique
        - **Déhiscence:** Mobilité excessive de l'anneau
        - **Endocardite:** Vegetations, abcès, nouvelles fuites
        """)
    
    with st.expander("📋 **Checklist complications prothèses biologiques**"):
        st.markdown("""
        - **Dégénérescence:** Calcifications, restriction mobilité
        - **Sténose:** Gradient augmenté progressif
        - **Régurgitation intra-prothétique:** Usure des feuillets
        - **Endocardite:** Mêmes critères que mécaniques
        """)
    
    st.markdown("### 📈 **Valeurs de Référence par Type de Prothèse**")
    
    if "aortique" in type_prothese:
        data_prothese = {
            "Type": ["Mécanique double ailette", "Bioprothèse stented", "Bioprothèse stentless", "TAVI"],
            "Gradient moyen normal": ["10-20 mmHg", "10-15 mmHg", "5-10 mmHg", "5-10 mmHg"],
            "EOA normale": ["1.5-2.5 cm²", "1.2-1.8 cm²", "1.4-2.2 cm²", "1.5-2.5 cm²"],
            "DVI normal": [">0.30", ">0.30", ">0.30", ">0.30"]
        }
    else:
        data_prothese = {
            "Type": ["Mécanique double ailette", "Bioprothèse stented", "Anneau mitral", "Valve native préservée"],
            "Gradient moyen normal": ["3-5 mmHg", "3-6 mmHg", "1-3 mmHg", "1-3 mmHg"],
            "EOA normale": ["2.0-3.0 cm²", "1.8-2.5 cm²", "3.0-4.0 cm²", "4.0-5.0 cm²"],
            "PHT normal": ["80-120 ms", "90-130 ms", "60-100 ms", "60-80 ms"]
        }
    
    st.table(data_prothese)

# ============================================================================
# PIED DE PAGE COMMUN
# ============================================================================

st.markdown("---")
st.markdown("""
<div class="warning">
<strong>⚠️ Avertissements Importants:</strong>
<ul>
<li>Ces algorithmes sont basés sur les dernières recommandations internationales</li>
<li>L'interprétation doit être adaptée au contexte clinique individuel</li>
<li>En cas de doute, consulter un échocardiographiste expérimenté</li>
<li>Les valeurs seuils peuvent varier selon les laboratoires</li>
</ul>
</div>
""", unsafe_allow_html=True)

with st.expander("ℹ️ À propos de cette application"):
    st.markdown("""
    **📚 Références Complètes:**
    - **PRVG & Dysfonction Diastolique:** ESC 2016, ASE 2016, JASE 2020
    - **HTAP:** ESC/ERS 2022 Guidelines
    - **Péricardite:** ESC 2015, ASE 2021 Consensus
    - **Prothèses Valvulaires:** ESC 2021, ASE 2017, EACVI 2021
    
    **🎯 Objectif:** Aide à la réalisation d'évaluations échocardiographiques complexes souvent incomplètes en pratique clinique
    
    **⚠️ Usage:** Complément à l'expertise clinique, pas un substitut
    
    **🔄 Mise à jour:** Dernière mise à jour - Mars 2024
    """)
