import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Échocardiographie Expert - Guide Complet Dynamique",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# STYLE CSS COMPLET AVEC ANIMATIONS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .dynamic-result {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        transition: all 0.4s ease;
        border: 2px solid transparent;
    }
    .dynamic-result:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.2);
        border: 2px solid #ffffff;
    }
    .parameter-feedback {
        background-color: #f8f9fa;
        border-left: 5px solid #6c757d;
        padding: 1.2rem;
        margin: 0.7rem 0;
        border-radius: 8px;
        transition: all 0.3s ease;
        font-size: 1.1rem;
    }
    .parameter-feedback.good {
        border-left-color: #28a745;
        background-color: #d4edda;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.2);
    }
    .parameter-feedback.warning {
        border-left-color: #ffc107;
        background-color: #fff3cd;
        box-shadow: 0 2px 8px rgba(255, 193, 7, 0.2);
    }
    .parameter-feedback.danger {
        border-left-color: #dc3545;
        background-color: #f8d7da;
        box-shadow: 0 2px 8px rgba(220, 53, 69, 0.2);
    }
    .real-time-value {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1f77b4;
        animation: pulse 1.5s infinite;
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        background: rgba(255,255,255,0.9);
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.8rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 0.8rem;
        transition: all 0.4s ease;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .metric-card:hover {
        transform: scale(1.08);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .section-header {
        font-size: 2rem;
        color: #2e86ab;
        margin: 2rem 0 1rem 0;
        border-bottom: 3px solid #2e86ab;
        padding-bottom: 0.7rem;
        font-weight: bold;
    }
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.7rem 2rem;
        border-radius: 25px;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    }
    .patient-info {
        background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .critical-alert {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        animation: alert-pulse 2s infinite;
        border: 3px solid #ffdd59;
    }
    @keyframes alert-pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(255, 107, 107, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); }
    }
    .success-alert {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid #55efc4;
    }
    .warning-alert {
        background: linear-gradient(135deg, #feca57 0%, #ff9ff3 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid #ffdd59;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# BASES DE DONNÉES COMPLÈTES DES PROTHÈSES
# ============================================================================

protheses_aortiques = {
    "Mécaniques": {
        "St Jude Medical (Regent)": {
            "19": {"EOA_théorique": 1.3, "Gradient_moyen_normal": "10-15"},
            "21": {"EOA_théorique": 1.5, "Gradient_moyen_normal": "8-12"},
            "23": {"EOA_théorique": 1.7, "Gradient_moyen_normal": "7-11"},
            "25": {"EOA_théorique": 2.0, "Gradient_moyen_normal": "6-10"},
            "27": {"EOA_théorique": 2.4, "Gradient_moyen_normal": "5-9"},
            "29": {"EOA_théorique": 2.8, "Gradient_moyen_normal": "4-8"}
        },
        "Carbomedics (Top Hat)": {
            "19": {"EOA_théorique": 1.2, "Gradient_moyen_normal": "12-16"},
            "21": {"EOA_théorique": 1.4, "Gradient_moyen_normal": "10-14"},
            "23": {"EOA_théorique": 1.6, "Gradient_moyen_normal": "9-13"},
            "25": {"EOA_théorique": 1.9, "Gradient_moyen_normal": "8-12"},
            "27": {"EOA_théorique": 2.2, "Gradient_moyen_normal": "7-11"},
            "29": {"EOA_théorique": 2.6, "Gradient_moyen_normal": "6-10"}
        },
        "On-X": {
            "19": {"EOA_théorique": 1.5, "Gradient_moyen_normal": "9-13"},
            "21": {"EOA_théorique": 1.8, "Gradient_moyen_normal": "7-11"},
            "23": {"EOA_théorique": 2.1, "Gradient_moyen_normal": "6-10"},
            "25": {"EOA_théorique": 2.5, "Gradient_moyen_normal": "5-9"},
            "27": {"EOA_théorique": 2.9, "Gradient_moyen_normal": "4-8"},
            "29": {"EOA_théorique": 3.3, "Gradient_moyen_normal": "4-7"}
        }
    },
    "Biologiques": {
        "Carpentier-Edwards Perimount": {
            "19": {"EOA_théorique": 1.1, "Gradient_moyen_normal": "14-18"},
            "21": {"EOA_théorique": 1.3, "Gradient_moyen_normal": "12-16"},
            "23": {"EOA_théorique": 1.5, "Gradient_moyen_normal": "10-14"},
            "25": {"EOA_théorique": 1.7, "Gradient_moyen_normal": "9-13"},
            "27": {"EOA_théorique": 1.9, "Gradient_moyen_normal": "8-12"},
            "29": {"EOA_théorique": 2.1, "Gradient_moyen_normal": "7-11"}
        },
        "Medtronic Mosaic": {
            "19": {"EOA_théorique": 1.0, "Gradient_moyen_normal": "15-20"},
            "21": {"EOA_théorique": 1.2, "Gradient_moyen_normal": "13-17"},
            "23": {"EOA_théorique": 1.4, "Gradient_moyen_normal": "11-15"},
            "25": {"EOA_théorique": 1.6, "Gradient_moyen_normal": "10-14"},
            "27": {"EOA_théorique": 1.8, "Gradient_moyen_normal": "9-13"},
            "29": {"EOA_théorique": 2.0, "Gradient_moyen_normal": "8-12"}
        },
        "St Jude Medical Biocor": {
            "19": {"EOA_théorique": 1.2, "Gradient_moyen_normal": "13-17"},
            "21": {"EOA_théorique": 1.4, "Gradient_moyen_normal": "11-15"},
            "23": {"EOA_théorique": 1.6, "Gradient_moyen_normal": "10-14"},
            "25": {"EOA_théorique": 1.8, "Gradient_moyen_normal": "9-13"},
            "27": {"EOA_théorique": 2.0, "Gradient_moyen_normal": "8-12"},
            "29": {"EOA_théorique": 2.2, "Gradient_moyen_normal": "7-11"}
        }
    },
    "TAVI": {
        "Edwards SAPIEN 3": {
            "20": {"EOA_théorique": 1.4, "Gradient_moyen_normal": "8-12"},
            "23": {"EOA_théorique": 1.7, "Gradient_moyen_normal": "7-11"},
            "26": {"EOA_théorique": 2.0, "Gradient_moyen_normal": "6-10"},
            "29": {"EOA_théorique": 2.3, "Gradient_moyen_normal": "5-9"}
        },
        "Medtronic Evolut": {
            "23": {"EOA_théorique": 1.9, "Gradient_moyen_normal": "6-10"},
            "26": {"EOA_théorique": 2.2, "Gradient_moyen_normal": "5-9"},
            "29": {"EOA_théorique": 2.6, "Gradient_moyen_normal": "4-8"},
            "34": {"EOA_théorique": 3.2, "Gradient_moyen_normal": "3-7"}
        },
        "Boston Scientific ACURATE": {
            "23": {"EOA_théorique": 1.8, "Gradient_moyen_normal": "7-11"},
            "25": {"EOA_théorique": 2.0, "Gradient_moyen_normal": "6-10"},
            "27": {"EOA_théorique": 2.3, "Gradient_moyen_normal": "5-9"}
        }
    }
}

protheses_mitrales = {
    "Mécaniques": {
        "St Jude Medical": {
            "25": {"EOA_théorique": 2.1, "Gradient_moyen_normal": "3-5"},
            "27": {"EOA_théorique": 2.3, "Gradient_moyen_normal": "2.5-4.5"},
            "29": {"EOA_théorique": 2.5, "Gradient_moyen_normal": "2-4"},
            "31": {"EOA_théorique": 2.7, "Gradient_moyen_normal": "2-3.5"},
            "33": {"EOA_théorique": 2.9, "Gradient_moyen_normal": "1.5-3"}
        },
        "Carbomedics": {
            "25": {"EOA_théorique": 2.0, "Gradient_moyen_normal": "3.5-5.5"},
            "27": {"EOA_théorique": 2.2, "Gradient_moyen_normal": "3-5"},
            "29": {"EOA_théorique": 2.4, "Gradient_moyen_normal": "2.5-4.5"},
            "31": {"EOA_théorique": 2.6, "Gradient_moyen_normal": "2-4"},
            "33": {"EOA_théorique": 2.8, "Gradient_moyen_normal": "2-3.5"}
        }
    },
    "Biologiques": {
        "Carpentier-Edwards Perimount": {
            "25": {"EOA_théorique": 1.8, "Gradient_moyen_normal": "4-6"},
            "27": {"EOA_théorique": 2.0, "Gradient_moyen_normal": "3.5-5.5"},
            "29": {"EOA_théorique": 2.2, "Gradient_moyen_normal": "3-5"},
            "31": {"EOA_théorique": 2.4, "Gradient_moyen_normal": "2.5-4.5"},
            "33": {"EOA_théorique": 2.6, "Gradient_moyen_normal": "2-4"}
        },
        "Hancock II": {
            "25": {"EOA_théorique": 1.7, "Gradient_moyen_normal": "4.5-6.5"},
            "27": {"EOA_théorique": 1.9, "Gradient_moyen_normal": "4-6"},
            "29": {"EOA_théorique": 2.1, "Gradient_moyen_normal": "3.5-5.5"},
            "31": {"EOA_théorique": 2.3, "Gradient_moyen_normal": "3-5"},
            "33": {"EOA_théorique": 2.5, "Gradient_moyen_normal": "2.5-4.5"}
        }
    }
}

# ============================================================================
# FONCTIONS DE CALCUL DYNAMIQUE COMPLÈTES
# ============================================================================

def evaluer_prvg_fevg_preservee(e_e_prime, volume_og, tr_vitesse):
    """Évaluation dynamique de la PRVG pour FE VG ≥ 50%"""
    resultats = {
        "prvg_normale": e_e_prime <= 8 and volume_og <= 34,
        "prvg_elevee": e_e_prime > 14,
        "zone_grise": 8 < e_e_prime <= 14,
        "criteres_secondaires": 0
    }
    
    if e_e_prime > 15: resultats["criteres_secondaires"] += 1
    if tr_vitesse > 2.8: resultats["criteres_secondaires"] += 1
    if volume_og > 34: resultats["criteres_secondaires"] += 1
        
    return resultats

def evaluer_pattern_diastolique(e_a_ratio, dt, e_vitesse):
    """Détermination du pattern diastolique"""
    if e_a_ratio <= 0.8 and e_vitesse <= 50:
        return "relaxation_alteree", "Pattern de Relaxation Altérée"
    elif e_a_ratio >= 2 and dt < 160:
        return "restrictif", "Pattern Restrictif"
    else:
        return "pseudonormal", "Pattern Pseudonormal"

def calculer_ppm(eoa_mesuree, surface_corporelle):
    """Calcul du Patient-Prothèse Mismatch"""
    eoai = eoa_mesuree / surface_corporelle
    if eoai < 0.65: return "severe", eoai
    elif eoai < 0.85: return "modere", eoai
    else: return "absent", eoai

def evaluer_risque_thrombose(categorie, fevg, fa, antecedent_te, inr):
    """Évaluation du risque de thrombose"""
    score = 0
    if "Mécanique" in categorie: score += 2
    if fevg < 40: score += 1
    if fa: score += 1
    if antecedent_te: score += 2
    if inr < 2.0: score += 2
    
    if score >= 5: return "eleve", score
    elif score >= 3: return "modere", score
    else: return "faible", score

def calculer_probabilite_htap(tr_vitesse, vc_diametre, vc_collapsus, rv_ra_ratio, septum_paradoxal):
    """Calcul du score de probabilité HTAP ESC 2022"""
    score = 0
    
    # Vitesse TR
    if tr_vitesse <= 2.8 or tr_vitesse == 2.9: score += 0
    elif 3.0 <= tr_vitesse <= 3.4: score += 1
    else: score += 2
    
    # VCI
    if vc_diametre <= 21 and vc_collapsus > 50: score += 0
    elif vc_diametre > 21 or vc_collapsus <= 50: score += 1
    else: score += 2
    
    # Ratio VD/OG
    if rv_ra_ratio == "<0.6": score += 0
    elif rv_ra_ratio == "0.6-1.0": score += 1
    else: score += 2
    
    # Septum paradoxal
    if septum_paradoxal == "Présent": score += 1
    
    return score

def evaluer_constrictive_restrictive(variation_respiratoire, septal_bounce, annulus_reverse, fonction_vg, strain_longitudinal):
    """Évaluation différentielle constrictive vs restrictive"""
    score_constriction = 0
    score_restrictif = 0
    
    # Critères constriction
    if variation_respiratoire == "≥25%": score_constriction += 2
    if septal_bounce == "Présent": score_constriction += 2
    if annulus_reverse == "Oui": score_constriction += 2
    
    # Critères restrictif
    if fonction_vg in ["Modérément altérée", "Sévèrement altérée"]: score_restrictif += 2
    if strain_longitudinal > -15: score_restrictif += 2
    
    return score_constriction, score_restrictif

def evaluer_dysfonction_diastolique_complete(e_a_ratio, e_e_prime, volume_og, tr_vitesse, dt, e_vitesse, fevg):
    """Évaluation complète de la fonction diastolique"""
    if fevg == "≥50%":
        return evaluer_prvg_fevg_preservee(e_e_prime, volume_og, tr_vitesse)
    else:
        pattern, libelle = evaluer_pattern_diastolique(e_a_ratio, dt, e_vitesse)
        return {"pattern": pattern, "libelle": libelle}

# ============================================================================
# INTERFACE PRINCIPALE COMPLÈTE
# ============================================================================

st.markdown('<div class="main-header">🫀 ÉCHOCARDIOGRAPHIE EXPERT - GUIDE DYNAMIQUE COMPLET</div>', unsafe_allow_html=True)

# ============================================================================
# SIDEBAR DE NAVIGATION COMPLÈTE
# ============================================================================

st.sidebar.title("🧭 NAVIGATION")
evaluation_choice = st.sidebar.radio(
    "CHOISIR L'ÉVALUATION:",
    ["🏠 Accueil", 
     "🫀 Pression Remplissage VG", 
     "📊 Dysfonction Diastolique Complète",
     "🌊 Probabilité HTAP ESC 2022",
     "🔄 Constrictive vs Restrictive",
     "⚙️ Prothèses Valvulaires"]
)

# Section informations patient
st.sidebar.markdown("---")
st.sidebar.subheader("👤 INFORMATIONS PATIENT")
patient_id = st.sidebar.text_input("ID Patient", "PAT-2024-001")
age = st.sidebar.slider("Âge", 20, 100, 65)
sexe = st.sidebar.selectbox("Sexe", ["Masculin", "Féminin"])
surface_corporelle = st.sidebar.slider("Surface corporelle (m²)", 1.4, 2.5, 1.8, 0.1)

# ============================================================================
# PAGE ACCUEIL COMPLÈTE
# ============================================================================

if evaluation_choice == "🏠 Accueil":
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; border-radius: 20px; margin: 2rem 0;'>
            <h1>🫀 BIENVENUE</h1>
            <p style='font-size: 1.3rem;'>Guide Échocardiographique Complet avec Feedback Dynamique</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Métriques rapides
    st.markdown("### 📈 ÉVALUATIONS DISPONIBLES")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🫀 PRVG</h3>
            <p>Pression Remplissage VG</p>
            <p style='font-size: 0.9rem; color: #666;'>Algorithmes situationnels</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Diastolique</h3>
            <p>Fonction Diastolique</p>
            <p style='font-size: 0.9rem; color: #666;'>Évaluation complète</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🌊 HTAP</h3>
            <p>Hypertension Pulmonaire</p>
            <p style='font-size: 0.9rem; color: #666;'>ESC 2022</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🔄 Péricarde</h3>
            <p>Diagnostic Différentiel</p>
            <p style='font-size: 0.9rem; color: #666;'>Constrictive vs Restrictive</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="metric-card">
            <h3>⚙️ Prothèses</h3>
            <p>Valvulaires</p>
            <p style='font-size: 0.9rem; color: #666;'>Base de données complète</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Section d'information
    st.markdown("---")
    st.markdown("### 💡 COMMENT UTILISER CETTE APPLICATION")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.markdown("""
        <div class="patient-info">
            <h4>🎯 1. Sélectionnez l'évaluation</h4>
            <p>Choisissez l'évaluation souhaitée dans le menu de navigation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info2:
        st.markdown("""
        <div class="patient-info">
            <h4>📊 2. Entrez les paramètres</h4>
            <p>Utilisez les sliders et menus déroulants pour saisir les valeurs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info3:
        st.markdown("""
        <div class="patient-info">
            <h4>🔄 3. Obtenez les résultats</h4>
            <p>Les résultats se mettent à jour automatiquement en temps réel</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# ÉVALUATION PRVG - COMPLÈTE ET DYNAMIQUE
# ============================================================================

elif evaluation_choice == "🫀 Pression Remplissage VG":
    
    st.markdown('<div class="section-header">🫀 ÉVALUATION PRESSION DE REMPLISSAGE VG</div>', unsafe_allow_html=True)
    
    # Configuration en colonnes
    col_config, col_feedback = st.columns([1, 2])
    
    with col_config:
        st.subheader("🎯 CONFIGURATION")
        
        # Situation clinique
        situation = st.selectbox("Situation Clinique", [
            "FE VG ≥ 50% - Patient standard",
            "FE VG < 50% - Dysfonction systolique",
            "Fibrillation auriculaire",
            "Sténose mitrale",
            "Régurgitation mitrale sévère",
            "Prothèse valvulaire mitrale",
            "Calcification annulaire mitrale sévère"
        ])
        
        st.markdown("---")
        st.subheader("📊 PARAMÈTRES MESURÉS")
        
        # Paramètres communs
        e_e_prime_moyen = st.slider("E/e' moyen", 5.0, 25.0, 12.0, 0.1, key="e_e_prime_prvg")
        volume_og_index = st.slider("Volume OG indexé (ml/m²)", 15, 80, 35, key="volume_og_prvg")
        tr_vitesse = st.slider("Vitesse TR max (m/s)", 1.5, 4.5, 2.8, 0.1, key="tr_vitesse_prvg")
        
        if situation not in ["Fibrillation auriculaire", "Sténose mitrale", "Prothèse valvulaire mitrale"]:
            e_a_ratio = st.slider("Rapport E/A", 0.5, 3.0, 1.2, 0.1, key="e_a_ratio_prvg")
            dt = st.slider("Temps décélération (ms)", 100, 400, 180, key="dt_prvg")
            e_vitesse = st.slider("Vitesse E (cm/s)", 20, 200, 80, key="e_vitesse_prvg")
        
        # Paramètres spécifiques selon la situation
        if situation == "Sténose mitrale":
            gradient_mitral = st.slider("Gradient moyen mitral (mmHg)", 2, 40, 12, key="gradient_mitral")
            surface_mitrale = st.slider("Surface mitrale (cm²)", 0.5, 4.0, 1.3, 0.1, key="surface_mitrale")
        
        elif situation == "Régurgitation mitrale sévère":
            volume_regurgitant = st.slider("Volume régurgitant (ml)", 10, 150, 65, key="volume_regurgitant")
            pap_systolique = st.slider("PAP systolique (mmHg)", 15, 100, 42, key="pap_rm")
        
        elif situation == "Prothèse valvulaire mitrale":
            gradient_prothese = st.slider("Gradient moyen prothèse (mmHg)", 2, 15, 6, key="gradient_prothese")
            eoa_prothese = st.slider("EOA prothèse (cm²)", 0.5, 3.0, 1.8, 0.1, key="eoa_prothese")
    
    with col_feedback:
        st.subheader("📈 RÉSULTATS EN TEMPS RÉEL")
        
        # Évaluation dynamique selon la situation
        if "≥ 50%" in situation:
            evaluation = evaluer_prvg_fevg_preservee(e_e_prime_moyen, volume_og_index, tr_vitesse)
            
            if evaluation["prvg_normale"]:
                st.markdown("""
                <div class="success-alert">
                    <h3>✅ PRESSION DE REMPLISSAGE VG NORMALE</h3>
                    <p><strong>Critères remplis:</strong> E/e' moyen ≤ 8 ET Volume OG ≤ 34 ml/m²</p>
                    <p><em>Recommandation:</em> Surveillance standard</p>
                </div>
                """, unsafe_allow_html=True)
                
            elif evaluation["prvg_elevee"]:
                st.markdown("""
                <div class="critical-alert">
                    <h3>🔴 PRESSION DE REMPLISSAGE VG ÉLEVÉE</h3>
                    <p><strong>Critère majeur:</strong> E/e' moyen > 14</p>
                    <p><em>Recommandation:</em> Évaluation clinique approfondie urgente</p>
                </div>
                """, unsafe_allow_html=True)
                
            elif evaluation["zone_grise"]:
                if evaluation["criteres_secondaires"] >= 2:
                    st.markdown(f"""
                    <div class="warning-alert">
                        <h3>🟡 PRESSION DE REMPLISSAGE VG PROBABLEMENT ÉLEVÉE</h3>
                        <p><strong>Zone grise avec {evaluation['criteres_secondaires']}/3 critères secondaires positifs</strong></p>
                        <p><em>Recommandation:</em> Évaluation multimodale recommandée</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="dynamic-result">
                        <h3>🟡 INDÉTERMINÉ - SURVEILLANCE RENFORCÉE</h3>
                        <p><strong>Seulement {evaluation['criteres_secondaires']}/3 critères secondaires</strong></p>
                        <p><em>Recommandation:</em> Évaluation clinique contextuelle</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        elif "< 50%" in situation:
            pattern, libelle = evaluer_pattern_diastolique(e_a_ratio, dt, e_vitesse)
            
            if pattern == "relaxation_alteree":
                st.markdown("""
                <div class="success-alert">
                    <h3>📊 PATTERN DE RELAXATION ALTÉRÉE</h3>
                    <p><strong>PRVG probablement normale</strong></p>
                    <p><em>Caractéristiques:</em> E/A ≤ 0.8 + E ≤ 50 cm/s</p>
                </div>
                """, unsafe_allow_html=True)
            elif pattern == "restrictif":
                st.markdown("""
                <div class="critical-alert">
                    <h3>📊 PATTERN RESTRICTIF</h3>
                    <p><strong>PRVG ÉLEVÉE - PRONOSTIC DÉFAVORABLE</strong></p>
                    <p><em>Caractéristiques:</em> E/A ≥ 2 + DT < 160 ms</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="warning-alert">
                    <h3>📊 PATTERN PSEUDONORMAL</h3>
                    <p><strong>ÉVALUATION COMPLÉMENTAIRE NÉCESSAIRE</strong></p>
                    <p><em>Recommandation:</em> Évaluer E/e' et volume OG pour confirmation</p>
                </div>
                """, unsafe_allow_html=True)
        
        elif situation == "Fibrillation auriculaire":
            st.markdown("""
            <div class="dynamic-result">
                <h3>💓 FIBRILLATION AURICULAIRE - ÉVALUATION SPÉCIFIQUE</h3>
                <p><strong>Paramètres valides en FA:</strong> E/e' moyen, Volume OG, Vitesse TR</p>
                <p><strong>Paramètres non valides:</strong> Rapport E/A, Temps de décélération</p>
                <p><strong>Seuils spécifiques:</strong> E/e' > 11 → PRVG élevée (spécificité 85%)</p>
            </div>
            """, unsafe_allow_html=True)
            
            if e_e_prime_moyen > 11:
                st.markdown("""
                <div class="critical-alert">
                    <h3>🔴 PRESSION DE REMPLISSAGE VG ÉLEVÉE EN FA</h3>
                    <p><strong>E/e' moyen > 11 → PRVG élevée avec bonne spécificité</strong></p>
                </div>
                """, unsafe_allow_html=True)
        
        elif situation == "Sténose mitrale":
            st.markdown("""
            <div class="critical-alert">
                <h3>⚠️ ATTENTION - STÉNOSE MITRALE</h3>
                <p><strong>Les paramètres conventionnels de PRVG ne sont PAS VALIDES</strong></p>
                <p><em>Limitations:</em> Le gradient mitral modifie les vitesses Doppler</p>
                <p><em>Recommandation:</em> Utiliser des paramètres indirects (PAP, dimensions OG, fonction VD)</p>
            </div>
            """, unsafe_allow_html=True)
        
        elif situation == "Régurgitation mitrale sévère":
            st.markdown("""
            <div class="warning-alert">
                <h3>🟡 RÉGURGITATION MITRALE SÉVÈRE - INTERPRÉTATION AVEC PRÉCAUTION</h3>
                <p><strong>E/e' peut surestimer la PRVG réelle</strong></p>
                <p><em>Paramètre le plus fiable:</em> Volume OG indexé</p>
                <p><em>Seuil significatif:</em> Volume OG > 40 ml/m² → élévation chronique des pressions</p>
            </div>
            """, unsafe_allow_html=True)
        
        elif situation == "Prothèse valvulaire mitrale":
            st.markdown("""
            <div class="critical-alert">
                <h3>🔴 PROTHÈSE VALVULAIRE MITRALE - LIMITATIONS SÉVÈRES</h3>
                <p><strong>Paramètres conventionnels de PRVG NON VALIDES</strong></p>
                <p><em>Raisons:</em> Artefacts acoustiques, modifications hémodynamiques</p>
                <p><em>Recommandation:</em> Utiliser des paramètres indirects (PAP, volume OG, fonction VD)</p>
            </div>
            """, unsafe_allow_html=True)
        
        elif situation == "Calcification annulaire mitrale sévère":
            st.markdown("""
            <div class="critical-alert">
                <h3>🔴 CALCIFICATION ANNULAIRE - CONTRE-INDICATION</h3>
                <p><strong>E/e' EST CONTRE-INDIQUÉ - SURESTIMATION SYSTÉMATIQUE</strong></p>
                <p><em>Alternative:</em> Volume OG, Vitesse TR, Flux veineux pulmonaire</p>
                <p><em>Seuils alternatifs:</em> Volume OG > 34 ml/m², TR > 2.8 m/s</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Feedback paramétrique détaillé
        st.subheader("🔍 ANALYSE PARAMÈTRE PAR PARAMÈTRE")
        
        # E/e' moyen (sauf contre-indications)
        if situation not in ["Sténose mitrale", "Prothèse valvulaire mitrale", "Calcification annulaire mitrale sévère"]:
            classe_e_e_prime = "good" if e_e_prime_moyen <= 8 else "warning" if e_e_prime_moyen <= 14 else "danger"
            interpretation_e_e = "NORMAL" if e_e_prime_moyen <= 8 else "LIMITE" if e_e_prime_moyen <= 14 else "ÉLEVÉ"
            
            if situation == "Fibrillation auriculaire":
                interpretation_e_e = "NORMAL" if e_e_prime_moyen <= 11 else "ÉLEVÉ"
            
            st.markdown(f"""
            <div class="parameter-feedback {classe_e_e_prime}">
                <strong>E/e' moyen:</strong> {e_e_prime_moyen} 
                <span class="real-time-value">→ {interpretation_e_e}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="parameter-feedback danger">
                <strong>E/e' moyen:</strong> {e_e_prime_moyen} 
                <span class="real-time-value">→ NON INTERPRÉTABLE</span>
                <p style='margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #721c24;'>Contre-indiqué dans cette situation</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Volume OG (toujours valide)
        classe_volume_og = "good" if volume_og_index <= 34 else "warning" if volume_og_index <= 40 else "danger"
        st.markdown(f"""
        <div class="parameter-feedback {classe_volume_og}">
            <strong>Volume OG indexé:</strong> {volume_og_index} ml/m²
            <span class="real-time-value">→ {'NORMAL' if volume_og_index <= 34 else 'LIMITE' if volume_og_index <= 40 else 'DILATÉ'}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Vitesse TR (toujours valide)
        classe_tr = "good" if tr_vitesse <= 2.8 else "warning" if tr_vitesse <= 3.4 else "danger"
        st.markdown(f"""
        <div class="parameter-feedback {classe_tr}">
            <strong>Vitesse TR:</strong> {tr_vitesse} m/s
            <span class="real-time-value">→ {'NORMAL' if tr_vitesse <= 2.8 else 'LIMITE' if tr_vitesse <= 3.4 else 'ÉLEVÉE'}</span>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# ÉVALUATION HTAP - COMPLÈTE ET DYNAMIQUE
# ============================================================================

elif evaluation_choice == "🌊 Probabilité HTAP ESC 2022":
    
    st.markdown('<div class="section-header">🌊 PROBABILITÉ D\'HYPERTENSION ARTÉRIELLE PULMONAIRE ESC 2022</div>', unsafe_allow_html=True)
    
    col_config, col_feedback = st.columns([1, 2])
    
    with col_config:
        st.subheader("🎯 PARAMÈTRES PRINCIPAUX")
        
        tr_vitesse = st.slider("Vitesse TR maximale (m/s)", 1.5, 5.0, 3.2, 0.1)
        vc_diametre = st.slider("Diamètre VCI (mm)", 10, 30, 22)
        vc_collapsus = st.slider("Collapsus VCI (%)", 0, 100, 35)
        rv_ra_ratio = st.selectbox("Rapport VD/OG", ["<0.6", "0.6-1.0", "≥1.0"])
        septum_paradoxal = st.selectbox("Mouvement septum paradoxal", ["Absent", "Présent"])
        
        st.markdown("---")
        st.subheader("📊 PARAMÈTRES SECONDAIRES")
        
        tapse = st.slider("TAPSE (mm)", 5, 25, 16)
        s_tricuspide = st.slider("S' tricuspide (cm/s)", 5.0, 15.0, 10.5, 0.1)
        fac_vd = st.slider("FAC VD (%)", 20, 60, 38)
        acceleration_time = st.slider("Temps accélération VTID (ms)", 40, 120, 65)
        diam_ap = st.slider("Diamètre artère pulmonaire (mm)", 15, 40, 32)
        pvr_estimee = st.slider("PVR estimée (UW)", 1.0, 15.0, 4.5, 0.1)
        
        st.markdown("---")
        st.subheader("🔍 PARAMÈTRES ADDITIONNELS")
        
        contexte_cardio_gauche = st.selectbox("Cardiopathie gauche connue", ["Non", "Oui"])
        diam_og = st.slider("Diamètre OG (mm)", 30, 60, 42)
        strain_vd = st.slider("Strain longitudinal VD (%)", -30, -10, -18)
    
    with col_feedback:
        st.subheader("📈 PROBABILITÉ HTAP EN TEMPS RÉEL")
        
        # Calcul du score
        score_htap = calculer_probabilite_htap(tr_vitesse, vc_diametre, vc_collapsus, rv_ra_ratio, septum_paradoxal)
        
        # Calcul score secondaire
        score_secondaire = 0
        if tapse < 17: score_secondaire += 1
        if s_tricuspide < 9.5: score_secondaire += 1
        if fac_vd < 35: score_secondaire += 1
        if acceleration_time < 80: score_secondaire += 1
        if pvr_estimee > 3: score_secondaire += 1
        
        # Affichage résultat principal
        if score_htap <= 1:
            st.markdown("""
            <div class="success-alert">
                <h3>🟢 PROBABILITÉ FAIBLE</h3>
                <p><strong>Score principal:</strong> ≤1 point - HTAP peu probable</p>
                <p><strong>Score secondaire:</strong> {score_secondaire}/5 points de confirmation</p>
                <p><em>Recommandation:</em> Surveillance standard si clinique concordante</p>
            </div>
            """.format(score_secondaire=score_secondaire), unsafe_allow_html=True)
        
        elif score_htap == 2:
            if score_secondaire >= 2:
                st.markdown("""
                <div class="warning-alert">
                    <h3>🟡 PROBABILITÉ INTERMÉDIAIRE</h3>
                    <p><strong>Score principal:</strong> 2 points</p>
                    <p><strong>Score secondaire:</strong> {score_secondaire}/5 points de confirmation</p>
                    <p><em>Recommandation:</em> Investigations complémentaires nécessaires</p>
                </div>
                """.format(score_secondaire=score_secondaire), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="success-alert">
                    <h3>🟢 PROBABILITÉ FAIBLE</h3>
                    <p><strong>Score principal:</strong> 2 points mais peu de signes secondaires</p>
                    <p><strong>Score secondaire:</strong> {score_secondaire}/5 points de confirmation</p>
                    <p><em>Recommandation:</em> Surveillance renforcée</p>
                </div>
                """.format(score_secondaire=score_secondaire), unsafe_allow_html=True)
        
        else:
            st.markdown("""
            <div class="critical-alert">
                <h3>🔴 PROBABILITÉ ÉLEVÉE</h3>
                <p><strong>Score principal:</strong> ≥3 points - HTAP probable</p>
                <p><strong>Score secondaire:</strong> {score_secondaire}/5 points de confirmation</p>
                <p><em>Recommandation:</em> Cathétérisme cardiaque recommandé</p>
            </div>
            """.format(score_secondaire=score_secondaire), unsafe_allow_html=True)
        
        # Métriques détaillées
        st.subheader("📊 SCORING DÉTAILLÉ")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🎯 Score Principal</h3>
                <p style="font-size: 2rem; font-weight: bold; color: {'#28a745' if score_htap <= 1 else '#ffc107' if score_htap == 2 else '#dc3545'}">
                    {score_htap}/7
                </p>
                <p>Probabilité HTAP</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📏 Score Secondaire</h3>
                <p style="font-size: 2rem; font-weight: bold; color: {'#28a745' if score_secondaire <= 1 else '#ffc107' if score_secondaire <= 3 else '#dc3545'}">
                    {score_secondaire}/5
                </p>
                <p>Signes de confirmation</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📏 Vitesse TR</h3>
                <p style="font-size: 1.8rem; font-weight: bold;">
                    {tr_vitesse} m/s
                </p>
                <p>{'Normale' if tr_vitesse <= 2.8 else 'Limite' if tr_vitesse <= 3.4 else 'Élevée'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>💓 TAPSE</h3>
                <p style="font-size: 1.8rem; font-weight: bold;">
                    {tapse} mm
                </p>
                <p>{'Normal' if tapse >= 17 else 'Altéré'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Feedback paramétrique détaillé
        st.subheader("🔍 ANALYSE PARAMÈTRE PAR PARAMÈTRE")
        
        # Vitesse TR
        classe_tr_htap = "good" if tr_vitesse <= 2.8 else "warning" if tr_vitesse <= 3.4 else "danger"
        st.markdown(f"""
        <div class="parameter-feedback {classe_tr_htap}">
            <strong>Vitesse TR:</strong> {tr_vitesse} m/s
            <span class="real-time-value">→ {'NORMAL' if tr_vitesse <= 2.8 else 'LIMITE' if tr_vitesse <= 3.4 else 'ÉLEVÉE'}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # VCI
        classe_vci = "good" if vc_diametre <= 21 and vc_collapsus > 50 else "warning" if vc_diametre <= 21 or vc_collapsus > 50 else "danger"
        interpretation_vci = "NORMAL" if vc_diametre <= 21 and vc_collapsus > 50 else "LIMITE" if vc_diametre <= 21 or vc_collapsus > 50 else "ANORMAL"
        st.markdown(f"""
        <div class="parameter-feedback {classe_vci}">
            <strong>VCI:</strong> {vc_diametre} mm / {vc_collapsus}% collapsus
            <span class="real-time-value">→ {interpretation_vci}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # TAPSE
        classe_tapse = "good" if tapse >= 17 else "warning" if tapse >= 14 else "danger"
        st.markdown(f"""
        <div class="parameter-feedback {classe_tapse}">
            <strong>TAPSE:</strong> {tapse} mm
            <span class="real-time-value">→ {'NORMAL' if tapse >= 17 else 'LIMITE' if tapse >= 14 else 'ALTÉRÉ'}</span>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# ÉVALUATION PROTHÈSES VALVULAIRES - COMPLÈTE ET DYNAMIQUE
# ============================================================================

elif evaluation_choice == "⚙️ Prothèses Valvulaires":
    
    st.markdown('<div class="section-header">⚙️ ÉVALUATION DES PROTHÈSES VALVULAIRES</div>', unsafe_allow_html=True)
    
    col_config, col_feedback = st.columns([1, 2])
    
    with col_config:
        st.subheader("🔧 CONFIGURATION PROTHÈSE")
        
        type_general = st.selectbox("Type de prothèse", ["Prothèse aortique", "Prothèse mitrale"])
        
        if type_general == "Prothèse aortique":
            categorie = st.selectbox("Catégorie", list(protheses_aortiques.keys()))
            marque = st.selectbox("Marque/Modèle", list(protheses_aortiques[categorie].keys()))
            tailles_disponibles = list(protheses_aortiques[categorie][marque].keys())
            taille = st.selectbox("Taille (mm)", tailles_disponibles)
            
            donnees_theoriques = protheses_aortiques[categorie][marque][taille]
            eoa_theorique = donnees_theoriques["EOA_théorique"]
            gradient_theorique = donnees_theoriques["Gradient_moyen_normal"]
            
            st.markdown("---")
            st.subheader("📊 MESURES AORTIQUES")
            
            gradient_moyen = st.slider("Gradient moyen (mmHg)", 5, 60, 18, key="gradient_aortique")
            eoa_mesuree = st.slider("EOA mesurée (cm²)", 0.5, 3.0, eoa_theorique, 0.1, key="eoa_aortique")
            dvi = st.slider("DVI", 0.1, 0.5, 0.32, 0.01, key="dvi")
            acceleration_time = st.slider("Temps accélération (ms)", 50, 150, 90, key="acceleration_time")
            
        else:
            categorie = st.selectbox("Catégorie", list(protheses_mitrales.keys()))
            marque = st.selectbox("Marque/Modèle", list(protheses_mitrales[categorie].keys()))
            tailles_disponibles = list(protheses_mitrales[categorie][marque].keys())
            taille = st.selectbox("Taille (mm)", tailles_disponibles)
            
            donnees_theoriques = protheses_mitrales[categorie][marque][taille]
            eoa_theorique = donnees_theoriques["EOA_théorique"]
            gradient_theorique = donnees_theoriques["Gradient_moyen_normal"]
            
            st.markdown("---")
            st.subheader("📊 MESURES MITRALES")
            
            gradient_moyen = st.slider("Gradient moyen (mmHg)", 2, 15, 6, key="gradient_mitral")
            eoa_mesuree = st.slider("EOA mesurée (cm²)", 0.5, 3.0, eoa_theorique, 0.1, key="eoa_mitrale")
            pht = st.slider("PHT (ms)", 50, 300, 130, key="pht")
            pression_og_estimee = st.slider("Pression OG estimée (mmHg)", 5, 40, 15, key="pression_og")
        
        st.markdown("---")
        st.subheader("👤 FACTEURS PATIENT")
        
        fa = st.checkbox("Fibrillation auriculaire", key="fa_prothese")
        antecedent_te = st.checkbox("Antécédent thrombo-embolique", key="antecedent_te_prothese")
        inr = st.slider("INR", 1.0, 5.0, 2.3, 0.1, key="inr_prothese")
        fevg_prothese = st.slider("FE VG (%)", 20, 70, 55, key="fevg_prothese")
        
        st.markdown("---")
        st.subheader("🔄 ÉVOLUTION")
        
        gradient_precedent = st.slider("Gradient précédent (mmHg) - si connu", 
                                     5, 60, 15, key="gradient_precedent")
        delta_temps = st.slider("Délai depuis dernier examen (mois)", 1, 60, 12, key="delta_temps")
    
    with col_feedback:
        st.subheader("📈 PERFORMANCE PROTHÈTIQUE EN TEMPS RÉEL")
        
        # Calculs dynamiques
        ratio_eoa = (eoa_mesuree / eoa_theorique) * 100
        severite_ppm, eoai = calculer_ppm(eoa_mesuree, surface_corporelle)
        risque_thrombose, score_thrombose = evaluer_risque_thrombose(
            categorie, fevg_prothese, fa, antecedent_te, inr
        )
        
        # Calcul évolution
        if gradient_precedent:
            delta_gradient = gradient_moyen - gradient_precedent
            evolution_annuelle = (delta_gradient / delta_temps) * 12 if delta_temps > 0 else 0
        else:
            delta_gradient = 0
            evolution_annuelle = 0
        
        # Détermination performance
        if type_general == "Prothèse aortique":
            if gradient_moyen > 35 and eoa_mesuree < 1.0 and dvi < 0.25:
                performance = "Dysfonction sévère"
                couleur_perf = "🔴"
            elif gradient_moyen > 20 or eoa_mesuree < 1.2 or dvi < 0.30:
                performance = "Dysfonction modérée"
                couleur_perf = "🟡"
            else:
                performance = "Fonction normale"
                couleur_perf = "🟢"
        else:
            if gradient_moyen > 10 and eoa_mesuree < 1.0:
                performance = "Dysfonction sévère"
                couleur_perf = "🔴"
            elif gradient_moyen > 7 or eoa_mesuree < 1.3:
                performance = "Dysfonction modérée"
                couleur_perf = "🟡"
            else:
                performance = "Fonction normale"
                couleur_perf = "🟢"
        
        # Affichage métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{couleur_perf} Performance</h3>
                <p style="font-size: 1.5rem; font-weight: bold; color: {'#dc3545' if 'sévère' in performance else '#ffc107' if 'modérée' in performance else '#28a745'}">
                    {performance}
                </p>
                <p>Gradient: {gradient_moyen} mmHg</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            couleur_ppm = "🔴" if severite_ppm == "severe" else "🟡" if severite_ppm == "modere" else "🟢"
            libelle_ppm = "Sévère" if severite_ppm == "severe" else "Modéré" if severite_ppm == "modere" else "Absent"
            
            st.markdown(f"""
            <div class="metric-card">
                <h3>{couleur_ppm} PPM</h3>
                <p style="font-size: 1.5rem; font-weight: bold; color: {'#dc3545' if severite_ppm == 'severe' else '#ffc107' if severite_ppm == 'modere' else '#28a745'}">
                    {libelle_ppm}
                </p>
                <p>EOAi: {eoai:.2f} cm²/m²</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            couleur_thrombose = "🔴" if risque_thrombose == "eleve" else "🟡" if risque_thrombose == "modere" else "🟢"
            libelle_thrombose = "Élevé" if risque_thrombose == "eleve" else "Modéré" if risque_thrombose == "modere" else "Faible"
            
            st.markdown(f"""
            <div class="metric-card">
                <h3>{couleur_thrombose} Risque Thrombose</h3>
                <p style="font-size: 1.5rem; font-weight: bold; color: {'#dc3545' if risque_thrombose == 'eleve' else '#ffc107' if risque_thrombose == 'modere' else '#28a745'}">
                    {libelle_thrombose}
                </p>
                <p>Score: {score_thrombose}/8</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            if gradient_precedent:
                couleur_evolution = "danger" if delta_gradient > 10 else "warning" if delta_gradient > 5 else "good"
                libelle_evolution = "Aggravation rapide" if delta_gradient > 10 else "Évolution défavorable" if delta_gradient > 5 else "Stable"
                
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📈 Évolution</h3>
                    <p style="font-size: 1.5rem; font-weight: bold; color: {'#dc3545' if delta_gradient > 10 else '#ffc107' if delta_gradient > 5 else '#28a745'}">
                        {libelle_evolution}
                    </p>
                    <p>Δ: {delta_gradient:+d} mmHg</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📈 Évolution</h3>
                    <p style="font-size: 1.5rem; font-weight: bold; color: #6c757d">
                        Données manquantes
                    </p>
                    <p>Examen de référence nécessaire</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Feedback détaillé
        st.subheader("🔍 ANALYSE DÉTAILLÉE")
        
        # Gradient
        if type_general == "Prothèse aortique":
            seuil_alerte_gradient = 35 if "sévère" in performance else 20
            classe_gradient = "good" if gradient_moyen <= 20 else "warning" if gradient_moyen <= 35 else "danger"
        else:
            seuil_alerte_gradient = 10 if "sévère" in performance else 7
            classe_gradient = "good" if gradient_moyen <= 7 else "warning" if gradient_moyen <= 10 else "danger"
        
        st.markdown(f"""
        <div class="parameter-feedback {classe_gradient}">
            <strong>Gradient moyen:</strong> {gradient_moyen} mmHg
            <span class="real-time-value">→ {'NORMAL' if gradient_moyen <= seuil_alerte_gradient else 'ÉLEVÉ'}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # EOA
        st.markdown(f"""
        <div class="parameter-feedback {'good' if ratio_eoa >= 80 else 'warning' if ratio_eoa >= 65 else 'danger'}">
            <strong>EOA mesurée/théorique:</strong> {eoa_mesuree} cm² / {ratio_eoa:.1f}%
            <span class="real-time-value">→ {'BON MATCH' if ratio_eoa >= 80 else 'MATCH ACCEPTABLE' if ratio_eoa >= 65 else 'MISMATCH'}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # PPM
        classe_ppm = "good" if severite_ppm == "absent" else "warning" if severite_ppm == "modere" else "danger"
        st.markdown(f"""
        <div class="parameter-feedback {classe_ppm}">
            <strong>Patient-Prothèse Mismatch:</strong> {libelle_ppm}
            <span class="real-time-value">→ EOAi = {eoai:.2f} cm²/m²</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Évolution
        if gradient_precedent:
            classe_evolution = "good" if delta_gradient <= 0 else "warning" if delta_gradient <= 5 else "danger"
            st.markdown(f"""
            <div class="parameter-feedback {classe_evolution}">
                <strong>Évolution du gradient:</strong> {delta_gradient:+d} mmHg en {delta_temps} mois
                <span class="real-time-value">→ {'STABLE' if delta_gradient <= 0 else 'LENTE' if delta_gradient <= 5 else 'RAPIDE'}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Recommandations finales
        st.subheader("💡 RECOMMANDATIONS FINALES")
        
        if performance == "Dysfonction sévère":
            st.error("""
            **🔴 ACTION REQUISE - CONSULTATION CHIRURGICALE URGENTE**
            - Évaluation pour reintervention
            - Surveillance très rapprochée
            - Optimisation traitement médical en attendant
            - Considérer anticoagulation si mécanique
            """)
        elif performance == "Dysfonction modérée":
            st.warning("""
            **🟡 SURVEILLANCE RENFORCÉE - CONTRÔLE 6 MOIS**
            - Optimisation traitement médical
            - Surveillance des symptômes
            - Vérifier observance anticoagulation si mécanique
            - Préparer éventuelle intervention
            """)
        else:
            st.success("""
            **🟢 SURVEILLANCE STANDARD - CONTRÔLE ANNUEL**
            - Maintenir traitement actuel
            - Surveillance clinique régulière
            - Éducation du patient sur les signes d'alerte
            - Maintenir INR thérapeutique si mécanique
            """)
        
        if severite_ppm == "severe":
            st.error("""
            **🔴 PPM SÉVÈRE DÉTECTÉ - IMPACT PRONOSTIQUE DÉFAVORABLE**
            - Optimisation maximale traitement médical
            - Surveillance rapprochée des symptômes
            - Considérer reintervention si symptomatique
            - Évaluation nutritionnelle et réadaptation
            """)

# ============================================================================
# ÉVALUATIONS RESTANTES (structure complète)
# ============================================================================

elif evaluation_choice == "📊 Dysfonction Diastolique Complète":
    
    st.markdown('<div class="section-header">📊 ÉVALUATION COMPLÈTE FONCTION DIASTOLIQUE</div>', unsafe_allow_html=True)
    
    col_config, col_feedback = st.columns([1, 2])
    
    with col_config:
        st.subheader("🎯 PARAMÈTRES D'ENTRÉE")
        
        fevg = st.selectbox("FE VG", ["≥50%", "41-49%", "≤40%"], key="fevg_diastolique")
        
        st.markdown("**📏 Doppler pulsé mitral:**")
        e_vitesse = st.slider("Vitesse E (cm/s)", 20, 200, 80, key="e_vitesse_diastolique")
        a_vitesse = st.slider("Vitesse A (cm/s)", 20, 150, 70, key="a_vitesse_diastolique")
        e_a_ratio = st.slider("Rapport E/A", 0.5, 3.0, 1.2, 0.1, key="e_a_ratio_diastolique")
        dt = st.slider("Temps décélération (ms)", 100, 400, 180, key="dt_diastolique")
        
        st.markdown("**🎯 Doppler tissulaire:**")
        e_prime_septal = st.slider("e' septal (cm/s)", 3.0, 20.0, 7.0, 0.1, key="e_prime_septal_diastolique")
        e_prime_lateral = st.slider("e' latéral (cm/s)", 3.0, 20.0, 9.0, 0.1, key="e_prime_lateral_diastolique")
        e_e_prime_moyen = st.slider("E/e' moyen", 5.0, 25.0, 10.0, 0.1, key="e_e_prime_moyen_diastolique")
        
        st.markdown("**📊 Paramètres structurels:**")
        volume_og_index = st.slider("Volume OG indexé (ml/m²)", 15, 80, 35, key="volume_og_diastolique")
        tr_vitesse = st.slider("Vitesse TR max (m/s)", 1.5, 4.5, 2.5, 0.1, key="tr_vitesse_diastolique")
        
        st.markdown("**🌀 Paramètres avancés:**")
        rapport_s_d = st.slider("Rapport S/D flux pulmonaire", 0.5, 2.5, 1.2, 0.1, key="rapport_s_d")
        duree_ar_a = st.slider("Durée Ar-A (ms)", -50, 100, 10, key="duree_ar_a")
        vp = st.slider("Vitesse propagation Vp (cm/s)", 30, 80, 45, key="vp")
    
    with col_feedback:
        st.subheader("📈 RÉSULTATS DÉTAILLÉS")
        
        # Évaluation complète
        evaluation = evaluer_dysfonction_diastolique_complete(
            e_a_ratio, e_e_prime_moyen, volume_og_index, tr_vitesse, dt, e_vitesse, fevg
        )
        
        if fevg == "≥50%":
            if evaluation["prvg_normale"]:
                st.markdown("""
                <div class="success-alert">
                    <h3>✅ FONCTION DIASTOLIQUE NORMALE</h3>
                    <p><strong>Classification:</strong> Grade 0</p>
                    <p><strong>PRVG:</strong> Normale</p>
                </div>
                """, unsafe_allow_html=True)
            elif evaluation["prvg_elevee"]:
                st.markdown("""
                <div class="critical-alert">
                    <h3>🔴 DYSFONCTION DIASTOLIQUE SÉVÈRE</h3>
                    <p><strong>Classification:</strong> Grade 3</p>
                    <p><strong>PRVG:</strong> Élevée</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="warning-alert">
                    <h3>🟡 DYSFONCTION DIASTOLIQUE MODÉRÉE</h3>
                    <p><strong>Classification:</strong> Grade 2</p>
                    <p><strong>PRVG:</strong> Indéterminée - Zone grise</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            pattern = evaluation.get("pattern", "")
            if pattern == "relaxation_alteree":
                st.markdown("""
                <div class="success-alert">
                    <h3>📊 DYSFONCTION DIASTOLIQUE LÉGÈRE</h3>
                    <p><strong>Classification:</strong> Grade 1</p>
                    <p><strong>Pattern:</strong> Relaxation altérée</p>
                    <p><strong>PRVG:</strong> Probablement normale</p>
                </div>
                """, unsafe_allow_html=True)
            elif pattern == "restrictif":
                st.markdown("""
                <div class="critical-alert">
                    <h3>📊 DYSFONCTION DIASTOLIQUE SÉVÈRE</h3>
                    <p><strong>Classification:</strong> Grade 3</p>
                    <p><strong>Pattern:</strong> Restrictif</p>
                    <p><strong>PRVG:</strong> Élevée</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="warning-alert">
                    <h3>📊 DYSFONCTION DIASTOLIQUE MODÉRÉE</h3>
                    <p><strong>Classification:</strong> Grade 2</p>
                    <p><strong>Pattern:</strong> Pseudonormal</p>
                    <p><strong>PRVG:</strong> Élevée</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Feedback paramétrique détaillé
        st.subheader("🔍 ANALYSE PARAMÉTRIQUE COMPLÈTE")
        
        # Création d'un tableau des paramètres
        parametres_data = {
            "Paramètre": ["Rapport E/A", "E/e' moyen", "Volume OG indexé", "Vitesse TR", 
                         "Temps décélération", "Rapport S/D", "Durée Ar-A", "Vitesse Vp"],
            "Valeur": [e_a_ratio, e_e_prime_moyen, f"{volume_og_index} ml/m²", f"{tr_vitesse} m/s",
                      f"{dt} ms", rapport_s_d, f"{duree_ar_a} ms", f"{vp} cm/s"],
            "Interprétation": [
                "Normal" if 0.8 <= e_a_ratio <= 2.0 else "Anormal",
                "Normal" if e_e_prime_moyen <= 8 else "Limite" if e_e_prime_moyen <= 14 else "Élevé",
                "Normal" if volume_og_index <= 34 else "Limite" if volume_og_index <= 40 else "Dilaté",
                "Normal" if tr_vitesse <= 2.8 else "Limite" if tr_vitesse <= 3.4 else "Élevée",
                "Normal" if 160 <= dt <= 240 else "Court" if dt < 160 else "Long",
                "Normal" if rapport_s_d > 1 else "Inversé",
                "Normal" if duree_ar_a < 30 else "Prolongé",
                "Normal" if vp >= 45 else "Ralenti"
            ]
        }
        
        st.dataframe(pd.DataFrame(parametres_data), use_container_width=True)

elif evaluation_choice == "🔄 Constrictive vs Restrictive":
    
    st.markdown('<div class="section-header">🔄 DIAGNOSTIC DIFFÉRENTIEL PÉRICARDITE CONSTRICTIVE vs RESTRICTIVE</div>', unsafe_allow_html=True)
    
    col_config, col_feedback = st.columns([1, 2])
    
    with col_config:
        st.subheader("🎯 CRITÈRES DIFFÉRENTIELS")
        
        st.markdown("**🔄 Paramètres respiratoires:**")
        variation_respiratoire = st.selectbox("Variation respiratoire flux mitral E", 
                                            ["<10%", "10-25%", "≥25%"], key="variation_respiratoire")
        variation_tricuspide = st.selectbox("Variation respiratoire flux tricuspide",
                                          ["<15%", "15-40%", "≥40%"], key="variation_tricuspide")
        augmentation_inspiratoire_tr = st.selectbox("Augmentation inspiratoire onde TR",
                                                  ["Absente", "Présente"], key="augmentation_tr")
        
        st.markdown("**📐 Paramètres structuraux:**")
        septal_bounce = st.selectbox("Mouvement septal paradoxal", ["Absent", "Présent"], key="septal_bounce")
        annulus_reverse = st.selectbox("Annulus paradoxal (e' latéral > e' septal)", ["Non", "Oui"], key="annulus_reverse")
        epaisseur_pericarde = st.selectbox("Épaisseur péricarde",
                                         ["Normal (<3 mm)", "Épaissi (3-5 mm)", "Très épaissi (>5 mm)", "Calcifié"],
                                         key="epaisseur_pericarde")
        
        st.markdown("**📊 Paramètres fonctionnels:**")
        fonction_vg = st.selectbox("Fonction VG systolique",
                                 ["Normale", "Légèrement altérée", "Modérément altérée", "Sévèrement altérée"],
                                 key="fonction_vg")
        fonction_vd = st.selectbox("Fonction VD", ["Normale", "Altérée"], key="fonction_vd")
        strain_longitudinal = st.slider("Strain longitudinal global (%)", -25, -10, -18, key="strain_longitudinal")
        
        st.markdown("**🔍 Paramètres avancés:**")
        flux_hepatique = st.selectbox("Flux hépatique diastolique",
                                    ["Normal", "Inversion expiratoire", "Inversion continu"],
                                    key="flux_hepatique")
    
    with col_feedback:
        st.subheader("🎯 DIAGNOSTIC DIFFÉRENTIEL")
        
        # Calcul des scores
        score_constriction, score_restrictif = evaluer_constrictive_restrictive(
            variation_respiratoire, septal_bounce, annulus_reverse, fonction_vg, strain_longitudinal
        )
        
        # Diagnostic
        if score_constriction >= 4 and score_constriction > score_restrictif:
            st.markdown("""
            <div class="critical-alert">
                <h3>🎯 CONSTRICTION PÉRICARDIQUE PROBABLE</h3>
                <p><strong>Score constriction:</strong> {score_constriction}/6</p>
                <p><strong>Score restrictif:</strong> {score_restrictif}/4</p>
                <p><em>Recommandation:</em> IRM cardiaque et avis spécialisé</p>
            </div>
            """.format(score_constriction=score_constriction, score_restrictif=score_restrictif), unsafe_allow_html=True)
        
        elif score_restrictif >= 3 and score_restrictif > score_constriction:
            st.markdown("""
            <div class="critical-alert">
                <h3>🎯 CARDIOMYOPATHIE RESTRICTIVE PROBABLE</h3>
                <p><strong>Score constriction:</strong> {score_constriction}/6</p>
                <p><strong>Score restrictif:</strong> {score_restrictif}/4</p>
                <p><em>Recommandation:</em> Bilan étiologique complet et avis spécialisé</p>
            </div>
            """.format(score_constriction=score_constriction, score_restrictif=score_restrictif), unsafe_allow_html=True)
        
        else:
            st.markdown("""
            <div class="warning-alert">
                <h3>⚠️ DIAGNOSTIC INDÉTERMINÉ</h3>
                <p><strong>Score constriction:</strong> {score_constriction}/6</p>
                <p><strong>Score restrictif:</strong> {score_restrictif}/4</p>
                <p><em>Recommandation:</em> Investigations complémentaires nécessaires (IRM, scanner, cathétérisme)</p>
            </div>
            """.format(score_constriction=score_constriction, score_restrictif=score_restrictif), unsafe_allow_html=True)
        
        # Tableau comparatif
        st.subheader("📊 TABLEAU COMPARATIF")
        
        comparatif_data = {
            "Critère": ["Variation respiratoire E mitral", "Mouvement septum", "Annulus mitral",
                       "Épaisseur péricarde", "Fonction VG", "Strain longitudinal", "Flux hépatique"],
            "Constriction": ["≥25%", "Bounce paradoxal", "e' latéral > e' septal", "Épaissi/calcifié",
                           "Préservée", "Relativement préservé", "Inversion expiratoire"],
            "Restrictive": ["<10%", "Normal ou réduit", "e' latéral ≈ e' septal", "Normal",
                          "Altérée", "Altéré (≥ -15%)", "Normal"]
        }
        
        st.dataframe(pd.DataFrame(comparatif_data), use_container_width=True)

# ============================================================================
# PIED DE PAGE COMPLET
# ============================================================================

st.markdown("---")
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown(f"""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p><strong>🔄 APPLICATION ÉCHOCARDIOGRAPHIQUE COMPLÈTE ET DYNAMIQUE</strong></p>
        <p>Dernière mise à jour: {current_time} | Patient: {patient_id}</p>
        <p><em>Tous les résultats se mettent à jour automatiquement en temps réel - Aucun bouton de calcul nécessaire</em></p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# SIDEBAR INFERIEUR - FONCTIONNALITÉS COMPLÈMENTAIRES
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.subheader("📋 RAPPORT AUTOMATIQUE")

if st.sidebar.button("🖨️ Générer Rapport Complet", key="rapport_complet"):
    st.sidebar.success("Rapport généré avec succès!")
    
    # Simulation de données de rapport
    rapport_data = f"""
    RAPPORT ÉCHOCARDIOGRAPHIQUE COMPLET
    Patient: {patient_id}
    Date: {current_time}
    Âge: {age} ans | Sexe: {sexe} | Surface corporelle: {surface_corporelle} m²
    
    ÉVALUATION RÉALISÉE: {evaluation_choice}
    
    Ce rapport a été généré automatiquement par le système d'aide à l'évaluation échocardiographique.
    Les résultats sont basés sur les paramètres saisis et les algorithmes des dernières recommandations.
    
    ---
    Signature électronique
    Système Expert Échocardiographique
    """
    
    st.sidebar.download_button(
        label="📥 Télécharger Rapport PDF",
        data=rapport_data,
        file_name=f"rapport_echo_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

st.sidebar.markdown("---")
st.sidebar.subheader("📚 RÉFÉRENCES")

with st.sidebar.expander("Voir les références"):
    st.sidebar.markdown("""
    **📖 Recommandations:**
    - **ESC 2021** - Valvulopathies
    - **ASE 2016** - Fonction Diastolique  
    - **ESC/ERS 2022** - Hypertension Pulmonaire
    - **ASE 2021** - Péricardite Constrictive
    - **EACVI 2021** - Prothèses Valvulaires
    
    **🎯 Sociétés Savantes:**
    - European Society of Cardiology (ESC)
    - American Society of Echocardiography (ASE)
    - European Association of Cardiovascular Imaging (EACVI)
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; color: #888; font-size: 0.8rem;'>
    <p>© 2024 - Guide Échocardiographique Expert</p>
    <p>Version 2.0 - Interface Dynamique Complète</p>
</div>
""", unsafe_allow_html=True)
