import streamlit as st
import pandas as pd

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
    .critical-param {
        color: #856404;
        background-color: #ffcccc;
        padding: 0.5rem;
        border-radius: 3px;
        margin: 0.2rem 0;
        border-left: 4px solid #ff0000;
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
# ÉVALUATION 3: PROBABILITÉ HTAP ESC 2022 - RÉVISÉE ET COMPLÈTE
# ============================================================================

elif evaluation_choice == "Probabilité d'HTAP - ESC 2022":
    
    st.markdown("## 🌊 Probabilité d'Hypertension Artérielle Pulmonaire - ESC/ERS 2022")
    
    st.markdown("""
    <div class="recommendation-box">
    <strong>📋 Définition HTAP:</strong> PAPm ≥20 mmHg au repos + PVR ≥3 UW + PCP ≤15 mmHg<br>
    <strong>⚠️ Attention:</strong> Ces algorithmes donnent une probabilité, pas un diagnostic définitif
    </div>
    """, unsafe_allow_html=True)
    
    # Paramètres d'entrée COMPLETS
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Paramètres Échocardiographiques Complets")
    
    # Groupe 1: Paramètres principaux
    st.sidebar.markdown("**🎯 Paramètres principaux:**")
    tr_vitesse = st.sidebar.number_input("Vitesse TR maximale (m/s)", 1.5, 5.0, 2.8, 0.1)
    paps = st.sidebar.number_input("PAP systolique (mmHg)", 15, 120, 40)
    vc_diametre = st.sidebar.number_input("Diamètre VCI (mm)", 10, 30, 17)
    vc_collapsus = st.sidebar.number_input("Collapsus VCI (%)", 0, 100, 50)
    rv_ra_ratio = st.sidebar.selectbox("Rapport VD/OG (apical 4 cavités)", ["<0.6", "0.6-1.0", "≥1.0"])
    
    # Groupe 2: Paramètres VD
    st.sidebar.markdown("**📊 Fonction VD:**")
    tapse = st.sidebar.number_input("TAPSE (mm)", 5, 25, 20)
    s_tricuspide = st.sidebar.number_input("S' tricuspide (cm/s)", 5.0, 15.0, 12.0, 0.1)
    fac_vd = st.sidebar.number_input("FAC VD (%)", 20, 60, 45)
    strain_vd = st.sidebar.number_input("Strain longitudinal VD (%)", -30, -10, -22)
    rimp_vd = st.sidebar.number_input("Index de performance VD (RIMP)", 0.2, 1.5, 0.4, 0.1)
    
    # Groupe 3: Paramètres artère pulmonaire
    st.sidebar.markdown("**📈 Artère pulmonaire:**")
    acceleration_time = st.sidebar.number_input("Temps d'accélération VTID (ms)", 40, 120, 80)
    diam_ap = st.sidebar.number_input("Diamètre artère pulmonaire (mm)", 15, 40, 25)
    notch_mesosystolique = st.sidebar.selectbox("Notch mésosystolique VTID", ["Absent", "Présent"])
    pvr_estimee = st.sidebar.number_input("PVR estimée (UW)", 1.0, 15.0, 2.5, 0.1)
    
    # Groupe 4: Paramètres supplémentaires
    st.sidebar.markdown("**🔍 Paramètres supplémentaires:**")
    septum_paradoxal = st.sidebar.selectbox("Mouvement septum paradoxal", ["Absent", "Présent"])
    gradient_diastolique_pulmonaire = st.sidebar.number_input("Gradient diastolique pulm (mmHg)", 0, 30, 5)
    diam_og = st.sidebar.number_input("Diamètre OG (mm)", 30, 60, 40)
    
    # Calculs automatiques
    st.markdown("## 🎯 **Algorithme Probabilité HTAP - Patients sans Cardiopathie Gauche**")
    
    # Score principal ESC 2022
    score_principal = 0
    
    # Vitesse TR
    if tr_vitesse <= 2.8 or tr_vitesse == 2.9:
        score_principal += 0
    elif 3.0 <= tr_vitesse <= 3.4:
        score_principal += 1
    else:
        score_principal += 2
    
    # VCI
    if vc_diametre <= 21 and vc_collapsus > 50:
        score_principal += 0
    elif vc_diametre > 21 or vc_collapsus <= 50:
        score_principal += 1
    else:
        score_principal += 2
    
    # Ratio VD/OG
    if rv_ra_ratio == "<0.6":
        score_principal += 0
    elif rv_ra_ratio == "0.6-1.0":
        score_principal += 1
    else:
        score_principal += 2
    
    # Septum paradoxal
    if septum_paradoxal == "Présent":
        score_principal += 1
    
    # Score secondaire (paramètres de confirmation)
    score_secondaire = 0
    if tapse < 17: score_secondaire += 1
    if s_tricuspide < 9.5: score_secondaire += 1
    if fac_vd < 35: score_secondaire += 1
    if acceleration_time < 80: score_secondaire += 1
    if notch_mesosystolique == "Présent": score_secondaire += 1
    if pvr_estimee > 3: score_secondaire += 1
    
    # Interprétation
    st.markdown(f"### **Score de probabilité principal: {score_principal}/7 points**")
    st.markdown(f"### **Score de confirmation secondaire: {score_secondaire}/6 points**")
    
    # Décision
    if score_principal <= 1:
        st.markdown('<div class="success-box">🟢 **PROBABILITÉ FAIBLE**<br>Score principal ≤1 - HTAP peu probable</div>', unsafe_allow_html=True)
    elif score_principal == 2:
        if score_secondaire >= 2:
            st.markdown('<div class="warning">🟡 **PROBABILITÉ INTERMÉDIAIRE**<br>Score principal = 2 + signes secondaires → Investigations nécessaires</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box">🟢 **PROBABILITÉ FAIBLE**<br>Score principal = 2 mais peu de signes secondaires</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="danger-box">🔴 **PROBABILITÉ ÉLEVÉE**<br>Score principal ≥3 - HTAP probable, cathétérisme recommandé</div>', unsafe_allow_html=True)
    
    # Tableau détaillé des paramètres
    st.markdown("## 📊 **Analyse Détaillée des Paramètres**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📈 Paramètres Principaux:**")
        data_principaux = {
            "Paramètre": ["Vitesse TR", "PAPs", "VCI diam/collapsus", "VD/OG ratio", "Septum paradoxal"],
            "Valeur": [f"{tr_vitesse} m/s", f"{paps} mmHg", f"{vc_diametre} mm/{vc_collapsus}%", rv_ra_ratio, septum_paradoxal],
            "Interprétation": [
                "Normal" if tr_vitesse <= 2.8 else "Élevé" if tr_vitesse <= 3.4 else "Très élevé",
                "Normal" if paps <= 35 else "Élevé" if paps <= 50 else "Très élevé",
                "Normal" if vc_diametre <= 21 and vc_collapsus > 50 else "Anormal",
                "Normal" if rv_ra_ratio == "<0.6" else "Limite" if rv_ra_ratio == "0.6-1.0" else "Anormal",
                "Normal" if septum_paradoxal == "Absent" else "Anormal"
            ]
        }
        st.dataframe(pd.DataFrame(data_principaux))
    
    with col2:
        st.markdown("**📊 Paramètres Secondaires:**")
        data_secondaires = {
            "Paramètre": ["TAPSE", "S' tricuspide", "FAC VD", "Temps accélération", "PVR estimée"],
            "Valeur": [f"{tapse} mm", f"{s_tricuspide} cm/s", f"{fac_vd}%", f"{acceleration_time} ms", f"{pvr_estimee} UW"],
            "Interprétation": [
                "Normal" if tapse >= 17 else "Altéré",
                "Normal" if s_tricuspide >= 9.5 else "Altéré",
                "Normal" if fac_vd >= 35 else "Altéré",
                "Normal" if acceleration_time >= 80 else "Court",
                "Normal" if pvr_estimee <= 3 else "Élevée"
            ]
        }
        st.dataframe(pd.DataFrame(data_secondaires))
    
    # Algorithme pour cardiopathie gauche
    st.markdown("## 💔 **Algorithme pour Patients avec Cardiopathie Gauche**")
    
    st.markdown("""
    <div class="step-box">
    <strong>Étape 1:</strong> Évaluer la probabilité HTAP sans contexte → Score principal<br>
    <strong>Étape 2:</strong> Si probabilité ≥ intermédiaire, rechercher discordance VD/VG:<br>
    &nbsp;&nbsp;• Atteinte VD disproportionnée vs atteinte VG<br>
    &nbsp;&nbsp;• PVR ≥ 5 UW par écho<br>
    &nbsp;&nbsp;• Temps accélération VTID très court (<65 ms)<br>
    &nbsp;&nbsp;• Strain VD très altéré (> -15%)<br>
    <strong>Étape 3:</strong> Si ≥2 critères de discordance → Suspicion HTAP combinée, cathétérisme
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# ÉVALUATION 4: PÉRICARDITE CONSTRICTIVE vs RESTRICTIVE - RÉVISÉE
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
    
    # Paramètres d'entrée COMPLETS
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Critères Différentiels Complets")
    
    st.sidebar.markdown("**🔄 Paramètres respiratoires:**")
    variation_respiratoire = st.sidebar.selectbox("Variation respiratoire flux mitral E", ["<10%", "10-25%", "≥25%"])
    variation_tricuspide = st.sidebar.selectbox("Variation respiratoire flux tricuspide", ["<15%", "15-40%", "≥40%"])
    augmentation_inspiratoire_tr = st.sidebar.selectbox("Augmentation inspiratoire onde TR", ["Absente", "Présente"])
    
    st.sidebar.markdown("**📐 Paramètres structuraux:**")
    septal_bounce = st.sidebar.selectbox("Mouvement septal paradoxal", ["Absent", "Présent"])
    annulus_reverse = st.sidebar.selectbox("Annulus paradoxal (e' latéral > e' septal)", ["Non", "Oui"])
    epaisseur_pericarde = st.sidebar.selectbox("Épaisseur péricarde", ["Normal (<3 mm)", "Épaissi (3-5 mm)", "Très épaissi (>5 mm)", "Calcifié"])
    dilatation_veine_cave = st.sidebar.selectbox("Dilatation veine cave", ["Absente", "Modérée", "Sévère"])
    
    st.sidebar.markdown("**📊 Paramètres fonctionnels:**")
    vp_couleur = st.sidebar.number_input("Vitesse propagation Vp (cm/s)", 30, 80, 45)
    strain_longitudinal = st.sidebar.number_input("Strain longitudinal global (%)", -25, -10, -18)
    fonction_vg = st.sidebar.selectbox("Fonction VG systolique", ["Normale", "Légèrement altérée", "Modérément altérée", "Sévèrement altérée"])
    fonction_vd = st.sidebar.selectbox("Fonction VD", ["Normale", "Altérée"])
    
    st.sidebar.markdown("**🔍 Paramètres avancés:**")
    rapport_e_e_prime = st.sidebar.number_input("Rapport E/e' moyen", 5.0, 25.0, 12.0, 0.1)
    temps_relaxation_vg = st.sidebar.number_input("Temps relaxation VG (ms)", 40, 120, 65)
    flux_hepatique = st.sidebar.selectbox("Flux hépatique diastolique", ["Normal", "Inversion expiratoire", "Inversion continu"])
    
    # Algorithme de décision COMPLET
    st.markdown("## 🎯 **Arbre Décisionnel ASE 2021 Révisé**")
    
    score_constriction = 0
    score_restrictif = 0
    
    # Critères constriction majeurs (2 points chacun)
    if variation_respiratoire == "≥25%": score_constriction += 2
    if septal_bounce == "Présent": score_constriction += 2
    if annulus_reverse == "Oui": score_constriction += 2
    if epaisseur_pericarde in ["Très épaissi (>5 mm)", "Calcifié"]: score_constriction += 2
    
    # Critères constriction mineurs (1 point chacun)
    if variation_tricuspide == "≥40%": score_constriction += 1
    if augmentation_inspiratoire_tr == "Présente": score_constriction += 1
    if dilatation_veine_cave in ["Modérée", "Sévère"]: score_constriction += 1
    if flux_hepatique in ["Inversion expiratoire", "Inversion continu"]: score_constriction += 1
    
    # Critères restrictif majeurs (2 points chacun)
    if fonction_vg in ["Modérément altérée", "Sévèrement altérée"]: score_restrictif += 2
    if strain_longitudinal > -15: score_restrictif += 2
    if rapport_e_e_prime > 15: score_restrictif += 1
    
    # Critères restrictif mineurs (1 point chacun)
    if variation_respiratoire == "<10%": score_restrictif += 1
    if fonction_vd == "Altérée": score_restrictif += 1
    if vp_couleur < 40: score_restrictif += 1
    
    st.markdown(f"### **Score Constriction: {score_constriction}/11**")
    st.markdown(f"### **Score Restrictif: {score_restrictif}/7**")
    
    # Diagnostic
    if score_constriction >= 4 and score_constriction > score_restrictif:
        st.markdown('<div class="danger-box">🎯 **CONSTRICTION PÉRICARDIQUE PROBABLE**<br>Score élevé pour constriction</div>', unsafe_allow_html=True)
        if score_constriction >= 6:
            st.markdown('<div class="critical-param">🔴 **CONSTRICTION PÉRICARDIQUE FORTEMENT PROBABLE**<br>Score très élevé</div>', unsafe_allow_html=True)
    elif score_restrictif >= 3 and score_restrictif > score_constriction:
        st.markdown('<div class="danger-box">🎯 **CARDIOMYOPATHIE RESTRICTIVE PROBABLE**<br>Score élevé pour restriction</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="warning">⚠️ **DIAGNOSTIC INDÉTERMINÉ**<br>Rechercher d\'autres causes ou imagerie complémentaire (IRM, scanner)</div>', unsafe_allow_html=True)
    
    # Tableau comparatif détaillé
    st.markdown("## 📊 **Tableau Comparatif Complet des Critères**")
    
    data_comparatif = {
        "Paramètre": ["Variation respiratoire E mitral", "Mouvement septum", "Annulus mitral", "Épaisseur péricarde", "Fonction VG", "Strain longitudinal", "Flux hépatique", "Dilatation VCI"],
        "Constriction": ["≥25%", "Bounce paradoxal", "e' latéral > e' septal", "Épaissi/calcifié", "Préservée", "Relativement préservé", "Inversion expiratoire", "Fréquente"],
        "Restrictive": ["<10%", "Normal ou réduit", "e' latéral ≈ e' septal", "Normal", "Altérée", "Altéré (≥ -15%)", "Normal", "Variable"]
    }
    
    st.table(data_comparatif)

# ============================================================================
# ÉVALUATION 5: PROTHÈSES VALVULAIRES - RÉVISÉE ET COMPLÈTE
# ============================================================================

elif evaluation_choice == "Évaluation Prothèses Valvulaires":
    
    st.markdown("## ⚙️ Évaluation des Prothèses Valvulaires - Guide Pas-à-Pas Complet")
    
    # Sélection du type de prothèse
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 Type de Prothèse")
    type_prothese = st.sidebar.selectbox("Type de prothèse", [
        "Prothèse aortique mécanique",
        "Prothèse aortique biologique", 
        "Prothèse mitrale mécanique",
        "Prothèse mitrale biologique",
        "TAVI",
        "Anneau mitral"
    ])
    
    # Paramètres communs
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Paramètres Hémodynamiques")
    
    # Paramètres selon le type de prothèse
    if "aortique" in type_prothese or type_prothese == "TAVI":
        st.sidebar.markdown("**📈 Paramètres aortiques:**")
        gradient_moyen = st.sidebar.number_input("Gradient moyen (mmHg)", 5, 60, 15)
        gradient_pic = st.sidebar.number_input("Gradient pic (mmHg)", 10, 100, 25)
        vti_lvot = st.sidebar.number_input("VTI LVOT (cm)", 15, 30, 20)
        vti_prothese = st.sidebar.number_input("VTI prothèse (cm)", 10, 25, 15)
        eoa = st.sidebar.number_input("Surface effective (EOA cm²)", 0.5, 3.0, 1.5, 0.1)
        dvi = st.sidebar.number_input("Index de performance (DVI)", 0.1, 0.5, 0.35, 0.01)
        acceleration_time = st.sidebar.number_input("Temps accélération (ms)", 50, 150, 90)
        
        # Paramètres théoriques pour comparaison
        st.sidebar.markdown("**📐 Paramètres théoriques:**")
        eoa_theorique = st.sidebar.number_input("EOA théorique (cm²)", 1.0, 4.0, 2.0, 0.1)
        taille_prothese = st.sidebar.number_input("Taille prothèse (mm)", 19, 29, 23)
        
    else:  # Prothèses mitrales
        st.sidebar.markdown("**📈 Paramètres mitrales:**")
        gradient_moyen = st.sidebar.number_input("Gradient moyen (mmHg)", 2, 15, 5)
        pht = st.sidebar.number_input("Temps pression-demi (ms)", 50, 300, 120)
        eoa = st.sidebar.number_input("Surface effective (cm²)", 0.5, 3.0, 1.8, 0.1)
        pression_og_estimee = st.sidebar.number_input("Pression OG estimée (mmHg)", 5, 40, 15)
        
        # Paramètres théoriques pour comparaison
        st.sidebar.markdown("**📐 Paramètres théoriques:**")
        eoa_theorique = st.sidebar.number_input("EOA théorique (cm²)", 1.5, 4.0, 2.5, 0.1)
        taille_prothese = st.sidebar.number_input("Taille prothèse (mm)", 25, 35, 29)
    
    # Paramètres communs à toutes les prothèses
    st.sidebar.markdown("**🔄 Régurgitation:**")
    regurgitation = st.sidebar.selectbox("Régurgitation para-valvulaire", ["Absente", "Légère", "Modérée", "Sévère"])
    localisation_regurgitation = st.sidebar.selectbox("Localisation fuite", ["Para-valvulaire", "Intra-prothétique", "Mixte"])
    
    st.sidebar.markdown("**📊 Fonction cardiaque:**")
    fevg = st.sidebar.number_input("FE VG (%)", 20, 70, 55)
    pap_systolique = st.sidebar.number_input("PAP systolique (mmHg)", 15, 100, 35)
    
    # Algorithme d'évaluation COMPLET
    st.markdown(f"## 🔍 **Évaluation de la {type_prothese}**")
    
    st.markdown("### 📋 **Étape 1: Mesures Standard Obligatoires**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Prothèse Aortique/TAVI:**")
        st.markdown("- Gradient moyen et pic")
        st.markdown("- Surface effective (EOA)")
        st.markdown("- Index de performance (DVI)")
        st.markdown("- Accélération temps")
        st.markdown("- Vitesse VTI LVOT/Prothèse")
        st.markdown("- Comparaison EOA mesurée/théorique")
        
    with col2:
        st.markdown("**📊 Prothèse Mitrale/Anneau:**")
        st.markdown("- Gradient moyen")
        st.markdown("- Temps pression-demi (PHT)")
        st.markdown("- Surface effective")
        st.markdown("- Pression artérielle pulmonaire")
        st.markdown("- Fonction VG")
        st.markdown("- Comparaison EOA mesurée/théorique")
    
    st.markdown("### 🎯 **Étape 2: Analyse de la Performance**")
    
    # Calculs spécifiques selon le type
    if "aortique" in type_prothese or type_prothese == "TAVI":
        # Calcul du DVI
        dvi_calcule = vti_lvot / vti_prothese if vti_prothese > 0 else dvi
        
        # Comparaison EOA théorique/mesurée
        ratio_eoa = (eoa / eoa_theorique) * 100 if eoa_theorique > 0 else 0
        
        st.markdown(f"**📐 Comparaison EOA:** {ratio_eoa:.1f}% (mesurée/théorique)")
        st.markdown(f"**📊 DVI calculé:** {dvi_calcule:.2f}")
        
        # Critères de dysfonction
        st.markdown("**🔍 Critères de Sténose Prothétique Aortique (ESC 2021):**")
        
        criteres_severes = 0
        if gradient_moyen > 35: criteres_severes += 1
        if eoa < 1.0: criteres_severes += 1
        if dvi_calcule < 0.25: criteres_severes += 1
        if ratio_eoa < 50: criteres_severes += 1
        
        if criteres_severes >= 3:
            st.markdown('<div class="danger-box">🔴 **DYSFONCTION SÉVÈRE**<br>≥3 critères sévères présents</div>', unsafe_allow_html=True)
        elif criteres_severes >= 2:
            st.markdown('<div class="warning">🟡 **DYSFONCTION MODÉRÉE**<br>2 critères sévères</div>', unsafe_allow_html=True)
        elif gradient_moyen > 20 or eoa < 1.2 or dvi_calcule < 0.30 or ratio_eoa < 65:
            st.markdown('<div class="warning">🟡 **DYSFONCTION LÉGÈRE**<br>Au moins 1 critère</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box">🟢 **FONCTION NORMALE**<br>Critères dans les limites</div>', unsafe_allow_html=True)
            
    else:  # Prothèses mitrales
        # Comparaison EOA théorique/mesurée
        ratio_eoa = (eoa / eoa_theorique) * 100 if eoa_theorique > 0 else 0
        
        st.markdown(f"**📐 Comparaison EOA:** {ratio_eoa:.1f}% (mesurée/théorique)")
        
        # Critères de dysfonction
        st.markdown("**🔍 Critères de Sténose Prothétique Mitrale (ASE 2017):**")
        
        criteres_severes = 0
        if gradient_moyen > 10: criteres_severes += 1
        if eoa < 1.0: criteres_severes += 1
        if pht > 200: criteres_severes += 1
        if ratio_eoa < 50: criteres_severes += 1
        
        if criteres_severes >= 3:
            st.markdown('<div class="danger-box">🔴 **DYSFONCTION SÉVÈRE**</div>', unsafe_allow_html=True)
        elif criteres_severes >= 2:
            st.markdown('<div class="warning">🟡 **DYSFONCTION MODÉRÉE**</div>', unsafe_allow_html=True)
        elif gradient_moyen > 7 or eoa < 1.3 or ratio_eoa < 65:
            st.markdown('<div class="warning">🟡 **DYSFONCTION LÉGÈRE**</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box">🟢 **FONCTION NORMALE**</div>', unsafe_allow_html=True)
    
    st.markdown("### 🔬 **Étape 3: Recherche de Complications**")
    
    with st.expander("📋 **Checklist complications détaillée**"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**⚙️ Prothèses Mécaniques:**")
            st.markdown("- **Thrombose:** Gradient augmenté progressif")
            st.markdown("- **Pannus:** Gradient augmenté progressif + EOA réduite")
            st.markdown("- **Fuites para-valvulaires:** Jet excentrique")
            st.markdown("- **Déhiscence:** Mobilité excessive de l'anneau")
            st.markdown("- **Endocardite:** Vegetations, abcès, nouvelles fuites")
            st.markdown("- **Hémolyse:** Fuites importantes")
            
        with col2:
            st.markdown("**🌿 Prothèses Biologiques/TAVI:**")
            st.markdown("- **Dégénérescence:** Calcifications, restriction mobilité")
            st.markdown("- **Sténose:** Gradient augmenté progressif")
            st.markdown("- **Régurgitation intra-prothétique:** Usure des feuillets")
            st.markdown("- **Endocardite:** Mêmes critères que mécaniques")
            st.markdown("- **Malposition:** Fuites para-valvulaires")
            st.markdown("- **Conduction disorders:** Blocs post-implantation")
    
    st.markdown("### 📈 **Valeurs de Référence par Type de Prothèse**")
    
    if "aortique" in type_prothese or type_prothese == "TAVI":
        data_prothese = {
            "Type": ["Mécanique double ailette", "Bioprothèse stented", "Bioprothèse stentless", "TAVI"],
            "Gradient moyen normal": ["10-20 mmHg", "10-15 mmHg", "5-10 mmHg", "5-10 mmHg"],
            "EOA normale": ["1.5-2.5 cm²", "1.2-1.8 cm²", "1.4-2.2 cm²", "1.5-2.5 cm²"],
            "DVI normal": [">0.30", ">0.30", ">0.30", ">0.30"],
            "Ratio EOA attendu": [">65%", ">65%", ">65%", ">65%"]
        }
    else:
        data_prothese = {
            "Type": ["Mécanique double ailette", "Bioprothèse stented", "Anneau mitral", "Valve native préservée"],
            "Gradient moyen normal": ["3-5 mmHg", "3-6 mmHg", "1-3 mmHg", "1-3 mmHg"],
            "EOA normale": ["2.0-3.0 cm²", "1.8-2.5 cm²", "3.0-4.0 cm²", "4.0-5.0 cm²"],
            "PHT normal": ["80-120 ms", "90-130 ms", "60-100 ms", "60-80 ms"],
            "Ratio EOA attendu": [">65%", ">65%", "N/A", "N/A"]
        }
    
    st.table(pd.DataFrame(data_prothese))

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
<li>Le cathétérisme cardiaque reste le gold standard pour les diagnostics incertains</li>
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
    
    **📊 Paramètres inclus:** Tous les paramètres essentiels selon les dernières recommandations
    """)
