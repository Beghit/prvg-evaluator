# app.py
# Streamlit PRVG Assistant — Enhanced with clinical adaptation, UI/UX improvements, and educational features
import streamlit as st
from math import isfinite
import pandas as pd
import json
from datetime import datetime
import base64
from io import BytesIO
st.set_page_config(page_title="PRVG Assistant", page_icon="🫀", layout="wide")

# -----------------------
# CSS Styling - Simplified
# -----------------------
st.markdown("""
<style>
/* Main styling */
.card { 
    background: white; 
    padding: 16px; 
    border-radius: 10px; 
    box-shadow: 0 2px 6px rgba(0,0,0,0.06); 
    margin-bottom: 16px;
    color: #000000;
}
.big-btn { 
    padding: 12px 18px; 
    font-size: 16px; 
}
.small-muted { 
    color: #6b7280; 
    font-size: 13px; 
}
.result-card { 
    padding: 14px; 
    border-radius: 10px; 
    color: white; 
}
.status-high { 
    background: linear-gradient(90deg,#ef4444,#b91c1c); 
}
.status-possible { 
    background: linear-gradient(90deg,#f59e0b,#d97706); 
}
.status-normal { 
    background: linear-gradient(90deg,#10b981,#047857); 
}
.status-indet { 
    background: linear-gradient(90deg,#64748b,#334155); 
}
.key { 
    font-weight:600; 
}
.footer { 
    color:#9ca3af; 
    font-size:12px; 
    padding-top:8px; 
}
.why-box {
    background-color: #f8f9fa;
    border-left: 4px solid #3b82f6;
    padding: 12px;
    border-radius: 4px;
    margin: 8px 0;
    color: #000000;
}
.how-box {
    background-color: #f0f9ff;
    border-left: 4px solid #0ea5e9;
    padding: 12px;
    border-radius: 4px;
    margin: 8px 0;
    color: #000000;
}
.parameter-group {
    background-color: #f8f9fa;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 16px;
}
.wizard-step {
    background-color: #f0f9ff;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 16px;
    border-left: 4px solid #3b82f6;
    color: #000000;
}
.wizard-step.active {
    background-color: #e0f2fe;
    border-left: 4px solid #0369a1;
}
.wizard-step.completed {
    background-color: #f0fdf4;
    border-left: 4px solid #16a34a;
}
.mobile-optimized input {
    font-size: 16px !important;
    padding: 12px !important;
}
.mobile-optimized button {
    padding: 14px 20px !important;
    font-size: 16px !important;
}
.algorithm-flow {
    background-color: white;
    padding: 16px;
    border-radius: 8px;
    margin: 16px 0;
    color: #000000;
}
.flow-step {
    padding: 8px 12px;
    border-radius: 6px;
    margin: 8px 0;
    border-left: 4px solid #3b82f6;
}
.flow-step.abnormal {
    border-left-color: #ef4444;
}
.flow-step.normal {
    border-left-color: #10b981;
}
.pitfall-alert {
    background-color: #fef3c7;
    border: 1px solid #f59e0b;
    border-radius: 6px;
    padding: 12px;
    margin: 8px 0;
    color: #000000;
}
.parameter-info {
    background-color: #e1f0fa;
    border-left: 4px solid #3b82f6;
    padding: 12px;
    border-radius: 4px;
    margin-top: 8px;
    color: #000000;
}
.parameter-info h4 {
    margin-top: 0;
    margin-bottom: 8px;
}
.param-link {
    color: #3b82f6;
    text-decoration: underline;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Internationalization (English and French only)
# -----------------------
LANGUAGES = {
    "English": {
        "title": "PRVG Assistant — Comprehensive Echo Hemodynamic Assessment",
        "clinical_presentation": "Clinical presentation (select best match)",
        "age": "Age (years)",
        "rhythm": "Rhythm",
        "sinus": "Sinus",
        "AF": "Atrial Fibrillation",
        "minimal_mode": "Minimal inputs mode",
        "auto_eval": "Auto-evaluate when minimal fields present",
        "profile": "Profile: ASE 2025 thresholds",
        "tachycardia": "Tachycardia",
        "bradycardia": "Bradycardia",
        "poor_window": "Poor acoustic window",
        "measurements": "Measurements",
        "minimal_mode_desc": "Minimal mode shows only required fields for selected presentation. Expand for more parameters.",
        "mitral_inflow": "Mitral Inflow",
        "tissue_doppler": "Tissue Doppler",
        "other_params": "Other Parameters",
        "advanced_params": "Advanced / Optional Parameters",
        "pulmonary_vein": "Pulmonary Vein Flow",
        "other_advanced": "Other Advanced Parameters",
        "contextual_params": "Contextual Parameters",
        "assessment_result": "Assessment Result",
        "evaluate": "Evaluate now",
        "clear": "Clear inputs",
        "auto_eval_status": "Auto-evaluation",
        "detailed_reasoning": "Detailed Medical Reasoning",
        "reasoning_steps": "Reasoning Steps:",
        "rules_triggered": "Rules Triggered:",
        "acquisition_notes": "Acquisition Notes:",
        "clinical_recommendations": "Clinical Recommendations",
        "parameter_explanations": "Parameter Explanations",
        "why_matter": "Why These Parameters Matter",
        "parameters_provided": "Parameters Provided:",
        "export_report": "Export Report",
        "download_full": "Download Full Report (Text)",
        "download_csv": "Download Data (CSV)",
        "report_summary": "Report Summary (for charting)",
        "footer_text": "This tool is for clinical decision support only. Noninvasive estimates of filling pressures have limitations — always correlate with clinical findings and consider natriuretic peptides or invasive hemodynamics when management depends on precise LAP assessment.",
        "based_on": "Based on ASE/EACVI 2016 Guidelines and subsequent literature.",
        "try_example": "Try Example Case",
        "voice_input": "Voice Input",
        "step1_title": "Step 1: Patient Information",
        "step2_title": "Step 2: Key Parameters",
        "step3_title": "Step 3: Results & Export",
        "next_step": "Next Step",
        "prev_step": "Previous Step",
        "required_fields": "Required fields:",
        "pitfall_alerts": "Pitfall Alerts",
        "algorithm_flow": "Algorithm Decision Flow",
        "references": "References",
        "disclaimer": "Disclaimer: This tool is for clinical decision support only and should not be used for standalone diagnosis.",
        "parameter_info_title": "Parameter Information",
        "parameter_info_desc": "Click on any parameter name to see detailed information below."
    },
    "French": {
        "title": "Assistant PRVG — Évaluation hémodynamique échographique complète",
        "clinical_presentation": "Présentation clinique (sélectionnez la meilleure correspondance)",
        "age": "Âge (années)",
        "rhythm": "Rythme",
        "sinus": "Sinus",
        "AF": "Fibrillation Atriale",
        "minimal_mode": "Mode entrées minimales",
        "auto_eval": "Évaluation automatique lorsque les champs minimaux sont présents",
        "profile": "Profil: Seuils ASE 2025",
        "tachycardia": "Tachycardie",
        "bradycardia": "Bradycardie",
        "poor_window": "Fenêtre acoustique médiocre",
        "measurements": "Mesures",
        "minimal_mode_desc": "Le mode minimal n'affiche que les champs requis pour la présentation sélectionnée. Développez pour plus de paramètres.",
        "mitral_inflow": "Flux mitral",
        "tissue_doppler": "Doppler tissulaire",
        "other_params": "Autres paramètres",
        "advanced_params": "Paramètres avancés / optionnels",
        "pulmonary_vein": "Flux veineux pulmonaire",
        "other_advanced": "Autres paramètres avancés",
        "contextual_params": "Paramètres contextuels",
        "assessment_result": "Résultat de l'évaluation",
        "evaluate": "Évaluer maintenant",
        "clear": "Effacer les entrées",
        "auto_eval_status": "Évaluation automatique",
        "detailed_reasoning": "Raisonnement médical détaillé",
        "reasoning_steps": "Étapes de raisonnement:",
        "rules_triggered": "Règles déclenchées:",
        "acquisition_notes": "Notes d'acquisition:",
        "clinical_recommendations": "Recommandations cliniques",
        "parameter_explanations": "Explications des paramètres",
        "why_matter": "Pourquoi ces paramètres sont importants",
        "parameters_provided": "Paramètres fournis:",
        "export_report": "Exporter le rapport",
        "download_full": "Télécharger le rapport complet (Texte)",
        "download_csv": "Télécharger les données (CSV)",
        "report_summary": "Résumé du rapport (pour le dossier)",
        "footer_text": "Cet outil est uniquement destiné à l'aide à la décision clinique. Les estimations non invasives des pressions de remplissage ont des limites — toujours corréler avec les résultats cliniques et envisager les peptides natriurétiques ou l'hémodynamique invasive lorsque la prise en charge dépend d'une estimation précise de la POG.",
        "based_on": "Basé sur les recommandations ASE/EACVI 2016 et la littérature suivante.",
        "try_example": "Essayer un cas exemple",
        "voice_input": "Entrée vocale",
        "step1_title": "Étape 1: Informations patient",
        "step2_title": "Étape 2: Paramètres clés",
        "step3_title": "Étape 3: Résultats & Export",
        "next_step": "Étape suivante",
        "prev_step": "Étape précédente",
        "required_fields": "Champs requis:",
        "pitfall_alerts": "Alertes pièges",
        "algorithm_flow": "Flux de décision de l'algorithme",
        "references": "Références",
        "disclaimer": "Avertissement: Cet outil est destiné à l'aide à la décision clinique et ne doit pas être utilisé pour un diagnóstico autonome.",
        "parameter_info_title": "Informations sur les paramètres",
        "parameter_info_desc": "Cliquez sur le nom d'un paramètre pour voir les informations détaillées ci-dessous."
    }
}

# Initialize session state for wizard steps and language
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'language' not in st.session_state:
    st.session_state.language = "English"
if 'selected_parameter' not in st.session_state:
    st.session_state.selected_parameter = None

# Get current language strings
def t(key):
    return LANGUAGES[st.session_state.language].get(key, key)

# -----------------------
# Profiles / thresholds with age and athlete adjustments
# -----------------------
def get_profile(age, athlete=False):
    base_profile = {
        "E_e_mean_abn": 14.0,
        "E_e_septal_abn": 15.0,
        "E_e_lateral_abn": 13.0,
        "e_septal_low": 6.0,
        "e_lateral_low": 7.0,
        "e_mean_low": 6.5,
        "TR_vmax_abn": 2.8,
        "TR_vmax_stress_abn": 3.2,
        "LAVi_abn": 34.0,
        "LARS_low": 18.0,
        "pulm_SD_low": 0.67,
        "IVRT_short_sinus": 70.0,
        "IVRT_short_AF": 65.0,
        "IVRT_short_restrict": 50.0,
        "Ar_minus_A_abn": 30.0,
        "TE_minus_e_abn": 50.0,
        "E_A_restrictive": 2.0,
        "E_A_low_cut": 0.8,
        "DT_short_AF": 160.0,
        "EDV_AF_low": 220.0,
        "E_over_Vp_AF_abn": 1.4,
    }
    # Age adjustments
    if age < 40:
        # Younger patients have higher e' values
        base_profile["e_septal_low"] = 7.0
        base_profile["e_lateral_low"] = 10.0
        base_profile["e_mean_low"] = 8.5
        base_profile["LAVi_abn"] = 40.0  # Higher LAVi threshold for younger patients
    elif age > 70:
        # Elderly patients have lower e' values
        base_profile["e_septal_low"] = 5.0
        base_profile["e_lateral_low"] = 6.0
        base_profile["e_mean_low"] = 5.5
        base_profile["LAVi_abn"] = 38.0  # Slightly higher LAVi threshold for elderly
    # Athlete adjustments
    if athlete:
        base_profile["E_A_restrictive"] = 2.2  # Higher threshold for athletes
        base_profile["E_e_mean_abn"] = 16.0  # Higher threshold for athletes
        base_profile["E_e_septal_abn"] = 17.0  # Higher threshold for athletes
        base_profile["E_e_lateral_abn"] = 15.0  # Higher threshold for athletes
    return base_profile

# -----------------------
# Medical Knowledge Base with enhanced content
# -----------------------
PARAMETER_EXPLANATIONS = {
    "E": {
        "name": "Mitral Inflow E Velocity",
        "why": "Mitral inflow E velocity reflects early diastolic filling, influenced by LA pressure and LV relaxation.",
        "how": "PW Doppler at mitral leaflet tips in apical 4-chamber view. Measure peak velocity in early diastole.",
        "pitfalls": "Affected by preload, LV relaxation, and mitral regurgitation. Use with caution in tachycardia."
    },
    "A": {
        "name": "Mitral Inflow A Velocity",
        "why": "Mitral inflow A velocity reflects late diastolic filling due to atrial contraction.",
        "how": "PW Doppler at mitral leaflet tips in apical 4-chamber view. Measure peak velocity during atrial systole.",
        "pitfalls": "Not reliable in atrial fibrillation or with significant mitral annular calcification."
    },
    "e_septal": {
        "name": "Septal Mitral Annular Tissue Doppler e' Velocity",
        "why": "Septal mitral annular tissue Doppler e' velocity is a marker of LV relaxation.",
        "how": "TDI at septal mitral annulus in apical 4-chamber view. Measure early diastolic velocity.",
        "pitfalls": "Can be reduced by regional wall motion abnormalities or prior septal infarction."
    },
    "e_lateral": {
        "name": "Lateral Mitral Annular Tissue Doppler e' Velocity",
        "why": "Lateral mitral annular tissue Doppler e' velocity is a marker of LV relaxation.",
        "how": "TDI at lateral mitral annulus in apical 4-chamber view. Measure early diastolic velocity.",
        "pitfalls": "Can be reduced by lateral wall motion abnormalities or prior lateral infarction."
    },
    "E_over_e_mean": {
        "name": "E/e' Mean Ratio",
        "why": "The ratio E/e' approximates LV filling pressures (e.g., PCWP).",
        "how": "Calculate as E divided by the average of septal and lateral e'.",
        "pitfalls": "Less reliable in mitral valve disease, HCM, or constrictive pericarditis."
    },
    "E_over_e_septal": {
        "name": "E/e' Septal Ratio",
        "why": "The ratio E/e' septal approximates LV filling pressures, especially in certain populations.",
        "how": "Calculate as E divided by septal e'.",
        "pitfalls": "Tends to overestimate filling pressures compared to E/e' mean."
    },
    "E_over_e_lateral": {
        "name": "E/e' Lateral Ratio",
        "why": "The ratio E/e' lateral approximates LV filling pressures, but may be less specific.",
        "how": "Calculate as E divided by lateral e'.",
        "pitfalls": "More preload-dependent than septal e'."
    },
    "TR_vmax": {
        "name": "Tricuspid Regurgitation Peak Velocity",
        "why": "TR jet peak velocity estimates systolic pulmonary artery pressure, which can be elevated in heart failure.",
        "how": "CW Doppler across tricuspid valve. Use multiple views to align with jet and measure peak velocity.",
        "pitfalls": "Requires adequate TR signal. May underestimate if jet is not well aligned."
    },
    "LAVi": {
        "name": "Left Atrial Volume Index",
        "why": "Left atrial volume index reflects chronic elevation of LV filling pressures.",
        "how": "Measure LA volume in apical 4-chamber and 2-chamber views at end-systole. Use area-length method and index to BSA.",
        "pitfalls": "Affected by atrial fibrillation, mitral valve disease, and athletic training."
    },
    "LARS": {
        "name": "LA Reservoir Strain",
        "why": "LA reservoir strain is a sensitive marker of LA dysfunction and elevated filling pressures.",
        "how": "Use speckle-tracking echocardiography on apical 4-chamber and 2-chamber views to measure peak systolic strain.",
        "pitfalls": "Requires good image quality and proper tracking. Vendor-dependent values."
    },
    "PV_S": {
        "name": "Pulmonary Vein Systolic Flow Velocity",
        "why": "Pulmonary vein systolic flow velocity can be reduced when LA pressure is elevated.",
        "how": "PW Doppler in right upper pulmonary vein. Measure peak systolic velocity.",
        "pitfalls": "Technically challenging. Affected by age, rhythm, and mitral regurgitation."
    },
    "PV_D": {
        "name": "Pulmonary Vein Diastolic Flow Velocity",
        "why": "Pulmonary vein diastolic flow velocity increases when LA pressure is elevated.",
        "how": "PW Doppler in right upper pulmonary vein. Measure peak diastolic velocity.",
        "pitfalls": "Technically challenging. Affected by age, rhythm, and mitral regurgitation."
    },
    "Ar_minus_A": {
        "name": "PV Ar - MV A Duration Difference",
        "why": "The difference between pulmonary vein Ar duration and mitral A duration reflects LV end-diastolic pressure.",
        "how": "Measure duration of pulmonary vein Ar wave (atrial reversal) and mitral A wave. Subtract mitral A duration from Ar duration.",
        "pitfalls": "Technically challenging. Requires simultaneous recording of PV and mitral flows."
    },
    "IVRT": {
        "name": "Isovolumic Relaxation Time",
        "why": "Isovolumic relaxation time shortens with elevated filling pressures and prolongs with impaired relaxation.",
        "how": "CW or PW Doppler between LV outflow and inflow. Measure from aortic valve closure to mitral valve opening.",
        "pitfalls": "Heart rate dependent. Difficult to measure in tachycardia."
    },
    "DT": {
        "name": "Deceleration Time",
        "why": "Deceleration time of E velocity shortens with restrictive physiology and elevated pressures.",
        "how": "PW Doppler of mitral inflow. Measure time from E peak to where velocity declines to zero (or extrapolate if incomplete).",
        "pitfalls": "Affected by heart rate, age, and loading conditions."
    },
    "EDV": {
        "name": "Pulmonary Vein End-Diastolic Velocity",
        "why": "Pulmonary vein end-diastolic velocity may increase with elevated LA pressure in atrial fibrillation.",
        "how": "PW Doppler in pulmonary vein. Measure velocity at end diastole.",
        "pitfalls": "Technically challenging in AF due to variable cycle lengths."
    },
    "Vp": {
        "name": "Flow Propagation Velocity",
        "why": "Color M-mode flow propagation velocity (Vp) can be used to estimate LV relaxation.",
        "how": "Color M-mode in apical view aligned with inflow. Measure slope of first aliasing from mitral valve to LV apex.",
        "pitfalls": "Technique and measurement not standardized. Angle dependent."
    },
    "E_over_Vp": {
        "name": "E/Vp Ratio",
        "why": "The ratio E/Vp correlates with PCWP.",
        "how": "Calculate as E divided by Vp.",
        "pitfalls": "Limited validation in various clinical scenarios."
    },
    "TE_minus_e": {
        "name": "TE - e' Time Difference",
        "why": "The time difference between onset of E and e' may reflect LV diastolic dysfunction.",
        "how": "Measure time from onset of mitral E to onset of e' on TDI.",
        "pitfalls": "Technically challenging. Requires high frame rate imaging."
    }
}

# -----------------------
# Example Cases
# -----------------------
EXAMPLE_CASES = {
    "Normal": {
        "age": 45,
        "presentation": "General / Routine",
        "rhythm": "Sinus",
        "E": 75.0,
        "A": 65.0,
        "e_septal": 8.0,
        "e_lateral": 12.0,
        "TR_vmax": 2.5,
        "LAVi": 28.0
    },
    "Heart Failure with Preserved EF": {
        "age": 72,
        "presentation": "Heart Failure (chronic)",
        "rhythm": "Sinus",
        "E": 110.0,
        "A": 60.0,
        "e_septal": 5.0,
        "e_lateral": 6.0,
        "TR_vmax": 3.2,
        "LAVi": 42.0,
        "LARS": 16.0
    },
    "Atrial Fibrillation": {
        "age": 68,
        "presentation": "Atrial Fibrillation",
        "rhythm": "AF",
        "IVRT": 60.0,
        "TR_vmax": 3.0,
        "E_over_e_septal": 16.0,
        "EDV": 35.0,
        "cycles_averaged": 8
    },
    "Athlete": {
        "age": 28,
        "presentation": "Athlete / Young",
        "rhythm": "Sinus",
        "E": 95.0,
        "A": 45.0,
        "e_septal": 12.0,
        "e_lateral": 18.0,
        "TR_vmax": 2.3,
        "LAVi": 36.0
    }
}

# -----------------------
# Utilities
# -----------------------
def nz(x): 
    return x is not None and (not (isinstance(x, float) and (x != x)))

def safe_mean(*vals):
    vs = [v for v in vals if nz(v)]
    return sum(vs)/len(vs) if vs else None

def compute_derived(meas):
    if nz(meas.get("E")) and nz(meas.get("A")) and meas.get("A") != 0:
        meas["EA"] = meas["E"]/meas["A"]
    else:
        meas["EA"] = meas.get("EA")
    if not nz(meas.get("e_mean")):
        meas["e_mean"] = safe_mean(meas.get("e_septal"), meas.get("e_lateral"))
    if not nz(meas.get("pulm_SD")) and nz(meas.get("PV_S")) and nz(meas.get("PV_D")) and meas.get("PV_D") != 0:
        meas["pulm_SD"] = meas["PV_S"]/meas["PV_D"]
    if not nz(meas.get("E_over_Vp")) and nz(meas.get("E")) and nz(meas.get("Vp")) and meas.get("Vp") != 0:
        meas["E_over_Vp"] = meas["E"]/meas["Vp"]

def qc_notes(meas, ctx):
    notes = []
    if ctx["rhythm"] == "AF" and (not nz(meas.get("cycles_averaged")) or meas.get("cycles_averaged") < 5):
        notes.append("AF: average ≥5–10 beats with similar RR.")
    if nz(meas.get("TR_vmax")) and meas.get("TR_vmax") < 0.5:
        notes.append("TR envelope suspiciously low; re-acquire.")
    if ctx.get("tachycardia"):
        notes.append("Tachycardia shortens diastolic intervals — interpret with caution.")
    if ctx.get("bradycardia"):
        notes.append("Bradycardia may alter E/A relation.")
    if ctx.get("poor_acoustic_window"):
        notes.append("Poor acoustic window — consider LARS or contrast.")
    # Add pitfall alerts
    if ctx["rhythm"] == "AF" and nz(meas.get("EA")):
        notes.append("E/A unreliable in AF → use E/e' instead.")
    if nz(meas.get("E")) and nz(meas.get("e_septal")) and meas.get("E")/meas.get("e_septal") > 20:
        notes.append("E/e' ratio >20 may indicate severely elevated pressures.")
    if nz(meas.get("LAVi")) and meas.get("LAVi") > 50:
        notes.append("Severe LA enlargement present.")
    return notes

# Atomic rule checks
def rule_low_e_prime(meas, P):
    return (nz(meas.get("e_mean")) and meas["e_mean"] <= P["e_mean_low"]) or \
           (nz(meas.get("e_septal")) and meas["e_septal"] <= P["e_septal_low"]) or \
           (nz(meas.get("e_lateral")) and meas["e_lateral"] <= P["e_lateral_low"])

def rule_Ee_high(meas, P):
    return (nz(meas.get("E_over_e_mean")) and meas["E_over_e_mean"] >= P["E_e_mean_abn"]) or \
           (nz(meas.get("E_over_e_septal")) and meas["E_over_e_septal"] >= P["E_e_septal_abn"]) or \
           (nz(meas.get("E_over_e_lateral")) and meas["E_over_e_lateral"] >= P["E_e_lateral_abn"])

def rule_TR_high(meas, P): 
    return nz(meas.get("TR_vmax")) and meas["TR_vmax"] >= P["TR_vmax_abn"]

def rule_LAVi_high(meas, P): 
    return nz(meas.get("LAVi")) and meas["LAVi"] >= P["LAVi_abn"]

def rule_LARS_low(meas, P): 
    return nz(meas.get("LARS")) and meas["LARS"] <= P["LARS_low"]

def rule_pv_SD_low(meas, P): 
    return nz(meas.get("pulm_SD")) and meas["pulm_SD"] <= P["pulm_SD_low"]

def rule_IVRT_short(meas, P): 
    return nz(meas.get("IVRT")) and meas["IVRT"] <= P["IVRT_short_sinus"]

def rule_restrictive_inflow(meas, P): 
    return nz(meas.get("EA")) and meas["EA"] >= P["E_A_restrictive"]

def rule_low_EA(meas, P): 
    return nz(meas.get("EA")) and meas["EA"] <= P["E_A_low_cut"]

def collect_surrogates(meas, P):
    tags = []
    if rule_Ee_high(meas, P): 
        tags.append("E/e' high")
    if rule_TR_high(meas, P): 
        tags.append("TR Vmax high")
    if rule_LAVi_high(meas, P): 
        tags.append("Enlarged LAVi")
    if rule_LARS_low(meas, P): 
        tags.append("Low LA strain (LARS)")
    if rule_pv_SD_low(meas, P): 
        tags.append("Pulm vein S/D low")
    if rule_IVRT_short(meas, P): 
        tags.append("Short IVRT")
    return tags

# Decision engine with comprehensive medical reasoning
def evaluate_PRVG(meas, ctx, age, athlete):
    P = get_profile(age, athlete)
    compute_derived(meas)
    qc = qc_notes(meas, ctx)
    fired = []
    missing = []
    reasoning = []
    
    # Check minimal requirements based on rhythm
    if ctx["rhythm"] == "AF":
        # AF-specific requirements
        if not any([nz(meas.get("IVRT")), nz(meas.get("TR_vmax")), nz(meas.get("E_over_e_septal")), nz(meas.get("EDV"))]):
            missing = ["IVRT or TR Vmax or E/e' (septal) or PV EDV"]
            reasoning.append("In AF, at least one of IVRT, TR Vmax, E/e' septal, or PV EDV is needed for assessment.")
    else:
        # Sinus rhythm requirements
        if not any([nz(meas.get("EA")), nz(meas.get("E_over_e_mean")), nz(meas.get("TR_vmax")), nz(meas.get("LAVi"))]):
            missing = ["E/A or E/e' or TR Vmax or LAVi"]
            reasoning.append("In sinus rhythm, at least one of E/A, E/e', TR Vmax, or LAVi is needed for assessment.")
    
    # If missing critical parameters -> return indeterminate
    if missing:
        return {
            "status": "Indeterminate",
            "grade": "NA",
            "confidence": "Low",
            "fired": [],
            "missing": missing,
            "qc": qc,
            "reasoning": reasoning,
            "narrative": "Insufficient core indices for reliable noninvasive LAP estimate.",
            "reco": ["Acquire missing core indices; consider LARS or natriuretic peptides if available."],
            "algorithm_flow": ["Missing critical parameters for assessment."]
        }
    
    # Main decision logic
    # AF branch
    if ctx["rhythm"] == "AF":
        flags = []
        reasoning_af = []
        algorithm_flow = ["Atrial Fibrillation algorithm branch"]
        
        if nz(meas.get("IVRT")) and meas["IVRT"] <= P["IVRT_short_AF"]:
            flags.append("Short IVRT (AF)")
            reasoning_af.append(f"IVRT of {meas['IVRT']} ms ≤ {P['IVRT_short_AF']} ms suggests elevated filling pressures in AF.")
            algorithm_flow.append(f"IVRT {meas['IVRT']} ms ≤ {P['IVRT_short_AF']} ms → abnormal")
            
        if nz(meas.get("E_over_e_septal")) and meas["E_over_e_septal"] >= P["E_e_septal_abn"]:
            flags.append("E/e' septal high")
            reasoning_af.append(f"E/e' septal ratio of {meas['E_over_e_septal']} ≥ {P['E_e_septal_abn']} suggests elevated filling pressures.")
            algorithm_flow.append(f"E/e' septal {meas['E_over_e_septal']} ≥ {P['E_e_septal_abn']} → abnormal")
            
        if rule_TR_high(meas, P): 
            flags.append("TR Vmax high")
            reasoning_af.append(f"TR Vmax of {meas['TR_vmax']} m/s ≥ {P['TR_vmax_abn']} m/s suggests pulmonary hypertension.")
            algorithm_flow.append(f"TR Vmax {meas['TR_vmax']} m/s ≥ {P['TR_vmax_abn']} m/s → abnormal")
            
        if nz(meas.get("E_over_Vp")) and meas["E_over_Vp"] >= P["E_over_Vp_AF_abn"]:
            flags.append("E/Vp high")
            reasoning_af.append(f"E/Vp ratio of {meas['E_over_Vp']} ≥ {P['E_over_Vp_AF_abn']} suggests elevated filling pressures in AF.")
            algorithm_flow.append(f"E/Vp {meas['E_over_Vp']} ≥ {P['E_over_Vp_AF_abn']} → abnormal")
            
        # Decision making for AF
        reasoning.extend(reasoning_af)
        if len(flags) >= 2:
            status = "High"
            confidence = "High"
            narrative = "Multiple AF-specific surrogates abnormal, strongly suggesting elevated filling pressures."
            algorithm_flow.append("≥2 abnormal parameters → High probability of elevated pressures")
        elif len(flags) == 1:
            status = "PossibleHigh"
            confidence = "Medium"
            narrative = "One AF-specific surrogate abnormal, suggesting possible elevated filling pressures."
            algorithm_flow.append("1 abnormal parameter → Possible elevated pressures")
        else:
            status = "Indeterminate"
            confidence = "Low"
            narrative = "No AF-specific surrogate clearly abnormal. Consider additional parameters."
            algorithm_flow.append("No abnormal parameters → Indeterminate")
            
        return {
            "status": status,
            "grade": "NA",
            "confidence": confidence,
            "fired": flags,
            "missing": [],
            "qc": qc,
            "reasoning": reasoning,
            "narrative": narrative,
            "reco": ["Average multiple beats; consider invasive measurement if clinical decisions depend on LAP."],
            "algorithm_flow": algorithm_flow
        }
    
    # Sinus rhythm branch
    EA = meas.get("EA")
    surrogates = collect_surrogates(meas, P)
    reasoning_sr = []
    algorithm_flow = ["Sinus rhythm algorithm branch"]
    
    # Low EA (impaired relaxation)
    if rule_low_EA(meas, P):
        reasoning_sr.append(f"E/A ratio of {EA} ≤ {P['E_A_low_cut']} indicates impaired relaxation (Grade I diastolic dysfunction).")
        algorithm_flow.append(f"E/A {EA} ≤ {P['E_A_low_cut']} → impaired relaxation")
        
        if len(surrogates) >= 1:
            fired = ["E/A low"] + surrogates
            reasoning_sr.append(f"Abnormal surrogates ({', '.join(surrogates)}) suggest elevated LAP despite impaired relaxation pattern.")
            algorithm_flow.append(f"Abnormal surrogates present → Grade I with elevated LAP")
            return {
                "status": "High",
                "grade": "G1_with_high_LAP",
                "confidence": "Medium" if len(surrogates)==1 else "High",
                "fired": fired,
                "missing": [],
                "qc": qc,
                "reasoning": reasoning_sr,
                "narrative": "Impaired relaxation with abnormal surrogate(s) suggests elevated LAP (Grade I with elevated filling pressures).",
                "reco": ["Consider LARS and/or BNP; correlate clinically."],
                "algorithm_flow": algorithm_flow
            }
        else:
            algorithm_flow.append("No abnormal surrogates → Normal LAP")
            return {
                "status": "Normal",
                "grade": "G1",
                "confidence": "Medium",
                "fired": ["E/A low"],
                "missing": [],
                "qc": qc,
                "reasoning": reasoning_sr,
                "narrative": "E/A ≤0.8 without abnormal surrogates — likely normal LAP (Grade I diastolic dysfunction).",
                "reco": ["Follow clinical context."],
                "algorithm_flow": algorithm_flow
            }
    
    # Restrictive inflow
    if rule_restrictive_inflow(meas, P):
        reasoning_sr.append(f"E/A ratio of {EA} ≥ {P['E_A_restrictive']} indicates restrictive filling pattern (Grade III diastolic dysfunction).")
        algorithm_flow.append(f"E/A {EA} ≥ {P['E_A_restrictive']} → restrictive pattern")
        
        # Apply athlete/young exception
        if athlete and age < 40:
            reasoning_sr.append("Athlete/young exception applied: restrictive pattern may be normal in highly trained individuals.")
            narrative = "Restrictive pattern detected but may be normal in athletes. Correlate with clinical context."
            reco = ["Evaluate for other causes of high output state.", "Consider exercise testing."]
            confidence = "Low"
            algorithm_flow.append("Athlete/young exception applied → may be normal")
        else:
            narrative = "Restrictive inflow suggests high LAP (Grade III diastolic dysfunction)."
            reco = ["Confirm with LAVi/TR and consider invasive testing if discordant."]
            confidence = "High" if len(surrogates)>=1 else "Medium"
            algorithm_flow.append("Restrictive pattern confirmed → Grade III")
            
        fired = ["E/A restrictive"] + surrogates
        reasoning_sr.extend([f"Surrogate(s) abnormal: {', '.join(surrogates)}"] if surrogates else ["No additional abnormal surrogates."])
        return {
            "status": "High",
            "grade": "G3",
            "confidence": confidence,
            "fired": fired,
            "missing": [],
            "qc": qc,
            "reasoning": reasoning_sr,
            "narrative": narrative,
            "reco": reco,
            "algorithm_flow": algorithm_flow
        }
    
    # Intermediate EA (pseudonormal)
    if EA and 0.8 < EA < P["E_A_restrictive"]:
        reasoning_sr.append(f"E/A ratio of {EA} suggests pseudonormal filling (Grade II diastolic dysfunction).")
        algorithm_flow.append(f"E/A {EA} → pseudonormal pattern")
        
        if len(surrogates) >= 2:
            fired = surrogates
            reasoning_sr.append(f"Multiple abnormal surrogates ({', '.join(surrogates)}) strongly suggest elevated LAP.")
            algorithm_flow.append("≥2 abnormal surrogates → elevated LAP")
            return {
                "status": "High",
                "grade": "G2",
                "confidence": "High",
                "fired": fired,
                "missing": [],
                "qc": qc,
                "reasoning": reasoning_sr,
                "narrative": "Intermediate E/A with multiple abnormal surrogates → elevated LAP (Grade II diastolic dysfunction).",
                "reco": ["If symptomatic consider stress diastolic echo or BNP."],
                "algorithm_flow": algorithm_flow
            }
        elif len(surrogates) == 1:
            fired = surrogates
            reasoning_sr.append(f"One abnormal surrogate ({surrogates[0]}) suggests possible elevated LAP.")
            algorithm_flow.append("1 abnormal surrogate → possible elevated LAP")
            return {
                "status": "PossibleHigh",
                "grade": "NA",
                "confidence": "Medium",
                "fired": fired,
                "missing": [],
                "qc": qc,
                "reasoning": reasoning_sr,
                "narrative": "One abnormal surrogate → possible elevated LAP.",
                "reco": ["Add LARS/IVRT/PV flow or BNP to improve confidence."],
                "algorithm_flow": algorithm_flow
            }
        else:
            reasoning_sr.append("No abnormal surrogates suggest normal LAP despite pseudonormal pattern.")
            algorithm_flow.append("No abnormal surrogates → normal LAP")
            return {
                "status": "Normal",
                "grade": "NA",
                "confidence": "Medium",
                "fired": [],
                "missing": [],
                "qc": qc,
                "reasoning": reasoning_sr,
                "narrative": "Intermediate E/A without abnormal surrogates → LAP likely normal.",
                "reco": ["If symptoms persist, perform stress diastolic testing."],
                "algorithm_flow": algorithm_flow
            }
    
    # Fallback safety net
    reasoning_sr.append("Could not classify with confidence — data borderline or conflicting.")
    algorithm_flow.append("Data borderline or conflicting → indeterminate")
    return {
        "status": "Indeterminate",
        "grade": "NA",
        "confidence": "Low",
        "fired": surrogates,
        "missing": [],
        "qc": qc,
        "reasoning": reasoning_sr,
        "narrative": "Could not classify with confidence — data borderline or conflicting.",
        "reco": ["Obtain additional indices: LARS, PV flow, TR, or consider invasive hemodynamics."],
        "algorithm_flow": algorithm_flow
    }

# -----------------------
# UI Implementation
# -----------------------
# Language selector in sidebar
with st.sidebar:
    st.session_state.language = st.selectbox("Language", list(LANGUAGES.keys()), index=0)
    # Voice input placeholder
    st.write(f"🔊 {t('voice_input')} (Coming soon)")
    
    # Example cases
    st.markdown("---")
    st.subheader(t("try_example"))
    example_case = st.selectbox("Select example case", list(EXAMPLE_CASES.keys()))
    if st.button("Load Example"):
        case_data = EXAMPLE_CASES[example_case]
        # Set session state values for all inputs
        for key, value in case_data.items():
            if key in ["age", "presentation", "rhythm"]:
                st.session_state[key] = value
            else:
                st.session_state[f"{key}_input"] = value
        # Set contextual flags based on presentation
        if case_data["presentation"] == "Athlete / Young":
            st.session_state.athlete = True
        else:
            st.session_state.athlete = False
        # Set rhythm
        if case_data["rhythm"] == "AF":
            st.session_state.rhythm_af = True
        else:
            st.session_state.rhythm_af = False
        st.success(f"Loaded {example_case} example")
        st.rerun()
    
    # References
    st.markdown("---")
    st.subheader(t("references"))
    st.markdown("""
    - Nagueh SF et al. Recommendations for the Evaluation of Left Ventricular Diastolic Function by Echocardiography. JASE 2016.
    - Lancellotti P et al. EACVI recommendations for the assessment of left ventricular filling pressure. Eur Heart J Cardiovasc Imaging 2024.
    """)

# Wizard navigation
st.markdown(f"""
<div class='card'>
    <h2 style='margin:0'>{t('title')}</h2>
    <div class='small-muted'>{t('disclaimer')}</div>
</div>
""", unsafe_allow_html=True)

# Wizard steps
col1, col2, col3 = st.columns(3)
with col1:
    step1_class = "wizard-step active" if st.session_state.current_step == 1 else "wizard-step completed" if st.session_state.current_step > 1 else "wizard-step"
    st.markdown(f'<div class="{step1_class}"><h4>{t("step1_title")}</h4></div>', unsafe_allow_html=True)
with col2:
    step2_class = "wizard-step active" if st.session_state.current_step == 2 else "wizard-step completed" if st.session_state.current_step > 2 else "wizard-step"
    st.markdown(f'<div class="{step2_class}"><h4>{t("step2_title")}</h4></div>', unsafe_allow_html=True)
with col3:
    step3_class = "wizard-step active" if st.session_state.current_step == 3 else "wizard-step"
    st.markdown(f'<div class="{step3_class}"><h4>{t("step3_title")}</h4></div>', unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'age' not in st.session_state:
    st.session_state.age = 65
if 'presentation' not in st.session_state:
    st.session_state.presentation = "General / Routine"
if 'rhythm' not in st.session_state:
    st.session_state.rhythm = "Sinus"
if 'minimal_mode' not in st.session_state:
    st.session_state.minimal_mode = True
if 'auto_eval' not in st.session_state:
    st.session_state.auto_eval = True
if 'tachycardia' not in st.session_state:
    st.session_state.tachycardia = False
if 'bradycardia' not in st.session_state:
    st.session_state.bradycardia = False
if 'poor_window' not in st.session_state:
    st.session_state.poor_window = False

# Step 1: Patient Information
if st.session_state.current_step == 1:
    st.markdown(f"### {t('step1_title')}")
    with st.container():
        p1, p2, p3 = st.columns([2, 1, 1])
        with p1:
            presentation = st.selectbox(
                t("clinical_presentation"),
                ["General / Routine", "Athlete / Young", "Hypertension / LVH", "Heart Failure (chronic)", 
                 "Atrial Fibrillation", "Pulmonary Hypertension", "Post-op / Acute", "Valve disease (MR/MS/AS)"],
                key="presentation_select",
                index=["General / Routine", "Athlete / Young", "Hypertension / LVH", "Heart Failure (chronic)", 
                 "Atrial Fibrillation", "Pulmonary Hypertension", "Post-op / Acute", "Valve disease (MR/MS/AS)"].index(st.session_state.presentation)
            )
            age = st.number_input(t("age"), min_value=12, max_value=110, value=st.session_state.age, step=1, key="age_input")
            athlete = True if presentation == "Athlete / Young" else False
        with p2:
            rhythm = st.radio(t("rhythm"), ["Sinus", "AF"], 
                             index=0 if st.session_state.rhythm == "Sinus" else 1, 
                             key="rhythm_radio")
            minimal_mode = st.checkbox(t("minimal_mode"), value=st.session_state.minimal_mode, 
                                      help="Show only the most relevant parameters for the selected presentation",
                                      key="minimal_mode_check")
            auto_eval = st.checkbox(t("auto_eval"), value=st.session_state.auto_eval, key="auto_eval_check")
        with p3:
            st.write("")  # spacing
            st.caption(t("profile"))
            # Add contextual flags
            tachycardia = st.checkbox(t("tachycardia"), value=st.session_state.tachycardia, 
                                     help="HR > 100 bpm - may shorten diastolic intervals",
                                     key="tachycardia_check")
            bradycardia = st.checkbox(t("bradycardia"), value=st.session_state.bradycardia, 
                                     help="HR < 60 bpm - may alter E/A relation",
                                     key="bradycardia_check")
            poor_window = st.checkbox(t("poor_window"), value=st.session_state.poor_window, 
                                     help="Consider LARS or contrast enhancement",
                                     key="poor_window_check")
    
    # Navigation buttons
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1:
        if st.button(t("next_step")):
            # Save step 1 values to session state
            st.session_state.age = age
            st.session_state.presentation = presentation
            st.session_state.rhythm = rhythm
            st.session_state.minimal_mode = minimal_mode
            st.session_state.auto_eval = auto_eval
            st.session_state.tachycardia = tachycardia
            st.session_state.bradycardia = bradycardia
            st.session_state.poor_window = poor_window
            st.session_state.current_step = 2
            st.rerun()

# Step 2: Key Parameters
elif st.session_state.current_step == 2:
    st.markdown(f"### {t('step2_title')}")
    # Use values from session state
    presentation = st.session_state.presentation
    rhythm = st.session_state.rhythm
    minimal_mode = st.session_state.minimal_mode
    auto_eval = st.session_state.auto_eval
    tachycardia = st.session_state.tachycardia
    bradycardia = st.session_state.bradycardia
    poor_window = st.session_state.poor_window
    age = st.session_state.age
    athlete = True if presentation == "Athlete / Young" else False
    
    # Determine minimal fields based on presentation
    def minimal_fields(pres, rhythm):
        if pres == "Athlete / Young":
            return ["E", "A", "one_e_prime", "LAVi"]
        if pres == "Atrial Fibrillation" or rhythm == "AF":
            return ["IVRT", "TR_vmax", "E_over_e_septal"]
        if pres == "Valve disease (MR/MS/AS)":
            return ["Ar_minus_A", "IVRT", "LAVi", "TR_vmax"]
        if pres == "Pulmonary Hypertension":
            return ["TR_vmax", "E_over_e_mean", "LAVi"]
        if pres == "Post-op / Acute":
            return ["E_over_e_mean", "TR_vmax", "LAVi"]
        # Default
        return ["E", "A", "one_e_prime", "TR_vmax", "LAVi"]
    
    core = minimal_fields(presentation, rhythm)
    
    # Show required fields
    st.markdown(f"**{t('required_fields')}** {', '.join(core)}")
    
    # Inputs area
    st.markdown(f"### {t('measurements')}")
    st.caption(t("minimal_mode_desc"))
    
    # Create input sections
    cols = st.columns(3)
    
    def show_if(name):
        return (not minimal_mode) or (name in core)
    
    # Helper function to create clickable parameter labels
    def param_label(param_key, label):
        return f"<span class='param-link' onclick='window.streamlitSessionState.set({{selected_parameter: \"{param_key}\"}});'>{label}</span>"

    with cols[0]:
        st.markdown(f"#### {t('mitral_inflow')}")
        # Initialize session state for inputs if not exists
        if 'E_input' not in st.session_state:
            st.session_state.E_input = None
        if 'A_input' not in st.session_state:
            st.session_state.A_input = None
        if 'EA_input' not in st.session_state:
            st.session_state.EA_input = None
            
        E = st.number_input("E (cm/s)", min_value=0.0, step=0.1, format="%.1f", 
                           disabled=not show_if("E"), key="E_input", value=float(st.session_state.E_input) if st.session_state.E_input is not None else 0.0)
        A = st.number_input("A (cm/s)", min_value=0.0, step=0.1, format="%.1f", 
                           disabled=not show_if("A"), key="A_input", value=float(st.session_state.A_input) if st.session_state.A_input is not None else 0.0)
        EA = st.number_input("E/A ratio (if pre-calculated)", min_value=0.0, step=0.1, format="%.2f", 
                            disabled=not show_if("EA"), key="EA_input", value=float(st.session_state.EA_input) if st.session_state.EA_input is not None else 0.0)
    
    with cols[1]:
        st.markdown(f"#### {t('tissue_doppler')}")
        # Initialize session state for inputs if not exists
        if 'e_septal_input' not in st.session_state:
            st.session_state.e_septal_input = None
        if 'e_lateral_input' not in st.session_state:
            st.session_state.e_lateral_input = None
        if 'E_over_e_septal_input' not in st.session_state:
            st.session_state.E_over_e_septal_input = None
        if 'E_over_e_lateral_input' not in st.session_state:
            st.session_state.E_over_e_lateral_input = None
        if 'E_over_e_mean_input' not in st.session_state:
            st.session_state.E_over_e_mean_input = None
            
        e_sept = st.number_input("e' septal (cm/s)", min_value=0.0, step=0.1, format="%.1f", 
                                disabled=not (show_if("e_septal") or show_if("one_e_prime")), key="e_septal_input", 
                                value=float(st.session_state.e_septal_input) if st.session_state.e_septal_input is not None else 0.0)
        e_lat = st.number_input("e' lateral (cm/s)", min_value=0.0, step=0.1, format="%.1f", 
                               disabled=not (show_if("e_lateral") or show_if("one_e_prime")), key="e_lateral_input", 
                               value=float(st.session_state.e_lateral_input) if st.session_state.e_lateral_input is not None else 0.0)
        E_over_e_sept = st.number_input("E/e' septal", min_value=0.0, step=0.1, format="%.1f", 
                                       disabled=not show_if("E_over_e_septal"), key="E_over_e_septal_input", 
                                       value=float(st.session_state.E_over_e_septal_input) if st.session_state.E_over_e_septal_input is not None else 0.0)
        E_over_e_lat = st.number_input("E/e' lateral", min_value=0.0, step=0.1, format="%.1f", 
                                      disabled=not show_if("E_over_e_lateral"), key="E_over_e_lateral_input", 
                                      value=float(st.session_state.E_over_e_lateral_input) if st.session_state.E_over_e_lateral_input is not None else 0.0)
        E_over_e_mean = st.number_input("E/e' mean", min_value=0.0, step=0.1, format="%.1f", 
                                       disabled=not show_if("E_over_e_mean"), key="E_over_e_mean_input", 
                                       value=float(st.session_state.E_over_e_mean_input) if st.session_state.E_over_e_mean_input is not None else 0.0)
    
    with cols[2]:
        st.markdown(f"#### {t('other_params')}")
        # Initialize session state for inputs if not exists
        if 'TR_vmax_input' not in st.session_state:
            st.session_state.TR_vmax_input = None
        if 'LAVi_input' not in st.session_state:
            st.session_state.LAVi_input = None
        if 'LARS_input' not in st.session_state:
            st.session_state.LARS_input = None
            
        TR_vmax = st.number_input("TR Vmax (m/s)", min_value=0.0, step=0.01, format="%.2f", 
                                 disabled=not show_if("TR_vmax"), key="TR_vmax_input", 
                                 value=float(st.session_state.TR_vmax_input) if st.session_state.TR_vmax_input is not None else 0.0)
        LAVi = st.number_input("LAVi (mL/m²)", min_value=0.0, step=0.1, format="%.1f", 
                              disabled=not show_if("LAVi"), key="LAVi_input", 
                              value=float(st.session_state.LAVi_input) if st.session_state.LAVi_input is not None else 0.0)
        LARS = st.number_input("LA reservoir strain (LARS %)", min_value=0.0, step=0.1, format="%.1f", 
                              disabled=not show_if("LARS"), key="LARS_input", 
                              value=float(st.session_state.LARS_input) if st.session_state.LARS_input is not None else 0.0)
    
    # Advanced parameters
    with st.expander(t("advanced_params")):
        adv_cols = st.columns(2)
        with adv_cols[0]:
            st.markdown(f"#### {t('pulmonary_vein')}")
            # Initialize session state for inputs if not exists
            if 'PV_S_input' not in st.session_state:
                st.session_state.PV_S_input = None
            if 'PV_D_input' not in st.session_state:
                st.session_state.PV_D_input = None
            if 'Ar_minus_A_input' not in st.session_state:
                st.session_state.Ar_minus_A_input = None
                
            PV_S = st.number_input("PV S (cm/s)", min_value=0.0, step=0.1, format="%.1f", 
                                  key="PV_S_input", value=float(st.session_state.PV_S_input) if st.session_state.PV_S_input is not None else 0.0)
            PV_D = st.number_input("PV D (cm/s)", min_value=0.0, step=0.1, format="%.1f", 
                                  key="PV_D_input", value=float(st.session_state.PV_D_input) if st.session_state.PV_D_input is not None else 0.0)
            Ar_minus_A = st.number_input("PV Ar - MV A (ms)", min_value=0, step=1, format="%d",
                                        disabled=not show_if("Ar_minus_A"), key="Ar_minus_A_input", 
                                        value=int(st.session_state.Ar_minus_A_input) if st.session_state.Ar_minus_A_input is not None else 0)
        with adv_cols[1]:
            st.markdown(f"#### {t('other_advanced')}")
            # Initialize session state for inputs if not exists
            if 'IVRT_input' not in st.session_state:
                st.session_state.IVRT_input = None
            if 'DT_input' not in st.session_state:
                st.session_state.DT_input = None
            if 'EDV_input' not in st.session_state:
                st.session_state.EDV_input = None
            if 'Vp_input' not in st.session_state:
                st.session_state.Vp_input = None
            if 'E_over_Vp_input' not in st.session_state:
                st.session_state.E_over_Vp_input = None
            if 'TE_minus_e_input' not in st.session_state:
                st.session_state.TE_minus_e_input = None
                
            IVRT = st.number_input("IVRT (ms)", min_value=0, step=1, format="%d",
                                  key="IVRT_input", value=int(st.session_state.IVRT_input) if st.session_state.IVRT_input is not None else 0)
            DT = st.number_input("DT (ms)", min_value=0, step=1, format="%d",
                                key="DT_input", value=int(st.session_state.DT_input) if st.session_state.DT_input is not None else 0)
            EDV = st.number_input("PV EDV (cm/s)", min_value=0.0, step=0.1, format="%.1f", 
                                 key="EDV_input", value=float(st.session_state.EDV_input) if st.session_state.EDV_input is not None else 0.0)
            Vp = st.number_input("Vp (cm/s)", min_value=0.0, step=0.1, format="%.1f", 
                                key="Vp_input", value=float(st.session_state.Vp_input) if st.session_state.Vp_input is not None else 0.0)
            E_over_Vp = st.number_input("E/Vp", min_value=0.0, step=0.1, format="%.1f", 
                                       key="E_over_Vp_input", value=float(st.session_state.E_over_Vp_input) if st.session_state.E_over_Vp_input is not None else 0.0)
            TEe = st.number_input("TE - e' (ms)", min_value=0, step=1, format="%d",
                                 key="TE_minus_e_input", value=int(st.session_state.TE_minus_e_input) if st.session_state.TE_minus_e_input is not None else 0)
        st.markdown(f"#### {t('contextual_params')}")
        ctx_cols = st.columns(3)
        with ctx_cols[0]:
            # Initialize session state for inputs if not exists
            if 'cycles_input' not in st.session_state:
                st.session_state.cycles_input = None
            cycles = st.number_input("Averaged cycles (AF)", min_value=0, step=1, format="%d", 
                                    key="cycles_input", value=int(st.session_state.cycles_input) if st.session_state.cycles_input is not None else 0)
        with ctx_cols[1]:
            # Initialize session state for inputs if not exists
            if 'HR_input' not in st.session_state:
                st.session_state.HR_input = None
            HR = st.number_input("HR (bpm)", min_value=0, step=1, format="%d", 
                                key="HR_input", value=int(st.session_state.HR_input) if st.session_state.HR_input is not None else 0)
        with ctx_cols[2]:
            # Initialize session state for inputs if not exists
            if 'LVEF_input' not in st.session_state:
                st.session_state.LVEF_input = None
            LVEF = st.number_input("LVEF (%)", min_value=0, max_value=100, step=1, format="%d", 
                                  key="LVEF_input", value=int(st.session_state.LVEF_input) if st.session_state.LVEF_input is not None else 0)
    
    # Measurement dictionary
    meas = {
        "E": E or None, "A": A or None, "EA": EA or None,
        "e_septal": e_sept or None, "e_lateral": e_lat or None, "e_mean": None,
        "E_over_e_mean": E_over_e_mean or None, "E_over_e_septal": E_over_e_sept or None, 
        "E_over_e_lateral": E_over_e_lat or None, "TR_vmax": TR_vmax or None, 
        "LAVi": LAVi or None, "LARS": LARS or None, "PV_S": PV_S or None, 
        "PV_D": PV_D or None, "pulm_SD": None, "Ar_minus_A": Ar_minus_A or None, 
        "TE_minus_e": TEe or None, "IVRT": IVRT or None, "EDV": EDV or None, 
        "Vp": Vp or None, "E_over_Vp": E_over_Vp or None, "DT": DT or None, 
        "HR": HR or None, "cycles_averaged": cycles or None, "LVEF": LVEF or None
    }
    
    ctx = {
        "rhythm": "AF" if rhythm == "AF" else "sinus", 
        "tachycardia": tachycardia, 
        "bradycardia": bradycardia, 
        "poor_acoustic_window": poor_window
    }
    
    # Check for minimal required fields
    def needed_for_minimal(core_fields, m):
        needed = []
        for f in core_fields:
            if f == "one_e_prime":
                if not (nz(m.get("e_septal")) or nz(m.get("e_lateral"))):
                    needed.append("e' (septal or lateral)")
            elif f == "E":
                if not nz(m.get("E")):
                    needed.append("E")
            elif f == "A":
                if not nz(m.get("A")):
                    needed.append("A")
            elif f == "E_over_e_mean":
                if not nz(m.get("E_over_e_mean")):
                    needed.append("E/e' (mean)")
            else:
                mapping = {
                    "TR_vmax": "TR Vmax", "LAVi": "LAVi", "LARS": "LARS", 
                    "Ar_minus_A": "PV Ar-MV A", "IVRT": "IVRT", "DT": "DT"
                }
                if not nz(m.get(f)):
                    needed.append(mapping.get(f, f))
        return needed
    
    needed = needed_for_minimal(core, meas)
    
    # Evaluate or wait
    if auto_eval and len(needed) == 0:
        result = evaluate_PRVG(meas, ctx, age, athlete)
        st.session_state.result = result
    else:
        result = None
    
    # Show evaluate controls
    colA, colB, colC = st.columns([2, 1, 1])
    with colA:
        if not auto_eval:
            if st.button(t("evaluate"), key="eval"):
                result = evaluate_PRVG(meas, ctx, age, athlete)
                st.session_state.result = result
    with colB:
        st.write("")
        if st.button(t("clear")):
            # Clear all input values
            for key in st.session_state.keys():
                if key.endswith('_input'):
                    st.session_state[key] = None
            st.session_state.selected_parameter = None
            st.rerun()
    with colC:
        st.write("")
        st.caption(f"{t('auto_eval_status')} " + ("enabled" if auto_eval else "disabled"))
    
    # If auto-eval not ready show info
    if auto_eval and result is None:
        st.info(f"{t('auto_eval_status')} waits for minimal fields: " + ", ".join(needed))
        
    # Parameter Information Section
    st.markdown("---")
    st.markdown(f"#### {t('parameter_info_title')}")
    st.caption(t("parameter_info_desc"))
    
    # Parameter selector dropdown
    param_options = {k: v["name"] for k, v in PARAMETER_EXPLANATIONS.items()}
    selected_param = st.selectbox(
        "Select parameter to view details",
        options=list(param_options.keys()),
        format_func=lambda x: param_options[x],
        key="param_select"
    )
    st.session_state.selected_parameter = selected_param
    
    # Display information for the selected parameter
    if st.session_state.selected_parameter and st.session_state.selected_parameter in PARAMETER_EXPLANATIONS:
        param_info = PARAMETER_EXPLANATIONS[st.session_state.selected_parameter]
        st.markdown(f"""
        <div class="parameter-info">
            <h4>{param_info['name']}</h4>
            <p><strong>Why it matters:</strong> {param_info['why']}</p>
            <p><strong>How to measure:</strong> {param_info['how']}</p>
            <p><strong>Pitfalls:</strong> {param_info['pitfalls']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Select a parameter above to see detailed information.")
    
    # Navigation buttons
    col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 4])
    with col_nav1:
        if st.button(t("prev_step")):
            st.session_state.current_step = 1
            st.rerun()
    with col_nav2:
        if st.button(t("next_step")) and result is not None:
            st.session_state.current_step = 3
            st.rerun()

# Step 3: Results & Export
elif st.session_state.current_step == 3:
    st.markdown(f"### {t('step3_title')}")
    if 'result' not in st.session_state:
        st.warning("Please go back to Step 2 and evaluate first.")
        if st.button(t("prev_step")):
            st.session_state.current_step = 2
            st.rerun()
        st.stop()
    
    # Use values from session state
    presentation = st.session_state.presentation
    rhythm = st.session_state.rhythm
    age = st.session_state.age
    athlete = True if presentation == "Athlete / Young" else False
    result = st.session_state.result
    
    # Create ctx dictionary for this step
    ctx = {
        "rhythm": "AF" if rhythm == "AF" else "sinus",
        "tachycardia": st.session_state.tachycardia,
        "bradycardia": st.session_state.bradycardia,
        "poor_acoustic_window": st.session_state.poor_window
    }
    
    # Color card
    status = result["status"]
    if status == "High":
        cls = "status-high"
        status_text = "🔴 High Probability"
    elif status == "PossibleHigh":
        cls = "status-possible"
        status_text = "🟡 Possible High Probability"
    elif status == "Normal":
        cls = "status-normal"
        status_text = "🟢 Normal Probability"
    else:
        cls = "status-indet"
        status_text = "⚪ Indeterminate"
    
    st.markdown(f"""
    <div class='result-card {cls}'>
        <h3 style='margin:4px'>{status_text} of Elevated Filling Pressures</h3>
        <div style='font-size:15px'>{result.get('narrative','')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics tiles
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Diastolic Grade", result.get("grade", "NA"))
    t2.metric("Confidence", result.get("confidence", ""))
    t3.metric("Triggered Rules", str(len(result.get("fired", []))))
    t4.metric("Missing Params", str(len(result.get("missing", []))))
    
    # Algorithm flow visualization
    with st.expander(t("algorithm_flow"), expanded=True):
        st.markdown("#### Algorithm Decision Path")
        for i, step in enumerate(result.get("algorithm_flow", [])):
            step_class = "flow-step abnormal" if "abnormal" in step else "flow-step normal" if "normal" in step else "flow-step"
            st.markdown(f'<div class="{step_class}">{i+1}. {step}</div>', unsafe_allow_html=True)
    
    # Pitfall alerts
    if result.get("qc"):
        with st.expander(t("pitfall_alerts"), expanded=True):
            for q in result["qc"]:
                st.markdown(f'<div class="pitfall-alert">⚠️ {q}</div>', unsafe_allow_html=True)
    
    # Detailed reasoning
    with st.expander(t("detailed_reasoning"), expanded=True):
        if result.get("reasoning"):
            st.markdown(f"#### {t('reasoning_steps')}")
            for i, reason in enumerate(result["reasoning"], 1):
                st.markdown(f"{i}. {reason}")
        if result.get("fired"):
            st.markdown(f"#### {t('rules_triggered')}")
            for r in result["fired"]:
                st.write(f"- {r}")
        if result.get("qc"):
            st.markdown(f"#### {t('acquisition_notes')}")
            for q in result["qc"]:
                st.info(f"• {q}")
    
    # Recommendations
    with st.expander(t("clinical_recommendations")):
        if result.get("reco"):
            for rec in result["reco"]:
                st.write(f"• {rec}")
        # Additional context-specific recommendations
        if result["status"] == "High":
            st.write("• Consider correlation with NT-proBNP/BNP levels if available.")
            st.write("• Evaluate for signs and symptoms of heart failure.")
        if athlete and result["status"] in ["High", "PossibleHigh"]:
            st.write("• In athletes, consider exercise stress echocardiography to distinguish physiological from pathological adaptation.")
    
    # Parameter explanations
    with st.expander(t("parameter_explanations")):
        st.markdown(f"#### {t('why_matter')}")
        st.markdown("""
        Assessment of left atrial pressure (LAP) requires integration of multiple echocardiographic parameters 
        as no single measurement is perfectly accurate. The algorithm follows ASE/EACVI guidelines to integrate
        these parameters into a comprehensive assessment.
        """)
        # Get measurements from session state
        used_params = []
        for key in st.session_state.keys():
            if key.endswith('_input') and st.session_state[key] is not None and st.session_state[key] != 0:
                param_name = key.replace('_input', '')
                if param_name in PARAMETER_EXPLANATIONS:
                    used_params.append(param_name)
        
        if used_params:
            st.markdown(f"##### {t('parameters_provided')}")
            for param in used_params:
                exp = PARAMETER_EXPLANATIONS[param]
                st.markdown(f"**{exp['name']}**")
                st.markdown(f"<div class='why-box'>{exp['why']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='how-box'>{exp['how']}</div>", unsafe_allow_html=True)
                if "pitfalls" in exp:
                    st.markdown(f"**Pitfalls:** {exp['pitfalls']}")
        else:
            st.info("No parameters with explanations were provided.")
    
    # Export & report section
    st.markdown("---")
    st.markdown(f"#### {t('export_report')}")
    
    # summary text
    now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    summary_lines = [
        f"PRVG Assistant Comprehensive Report — {now}",
        f"Presentation: {presentation} (Age {age})  Rhythm: {rhythm}",
        f"Result: {result['status']}  Grade: {result.get('grade','NA')}  Confidence: {result.get('confidence','')}",
        "",
        "Narrative:",
        result.get('narrative', ''),
        "",
        "Reasoning:",
    ]
    if result.get("reasoning"):
        for i, reason in enumerate(result["reasoning"], 1):
            summary_lines.append(f"{i}. {reason}")
    
    summary_lines.extend([
        "",
        "Triggered rules: " + (", ".join(result.get("fired", [])) or "none"),
        "Recommendations:",
    ])
    if result.get("reco"):
        for rec in result["reco"]:
            summary_lines.append(f"- {rec}")
    
    summary_lines.extend([
        "",
        "Measurements provided:"
    ])
    # Get measurements from session state
    for key in st.session_state.keys():
        if key.endswith('_input') and st.session_state[key] is not None and st.session_state[key] != 0:
            param_name = key.replace('_input', '')
            summary_lines.append(f"- {param_name}: {st.session_state[key]}")
    
    summary_text = "\n".join(summary_lines)
    
    # Create two columns for export buttons
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        st.download_button(t("download_full"), data=summary_text, 
                          file_name="prvg_comprehensive_report.txt", mime="text/plain")
    with exp_col2:
        # Create data for CSV export
        data_dict = {}
        for key in st.session_state.keys():
            if key.endswith('_input') and st.session_state[key] is not None and st.session_state[key] != 0:
                param_name = key.replace('_input', '')
                data_dict[param_name] = [st.session_state[key]]
        # Add context information
        data_dict["Presentation"] = [presentation]
        data_dict["Age"] = [age]
        data_dict["Rhythm"] = [rhythm]
        data_dict["Result"] = [result['status']]
        data_dict["Grade"] = [result.get('grade', 'NA')]
        data_dict["Confidence"] = [result.get('confidence', '')]
        df = pd.DataFrame(data_dict)
        st.download_button(t("download_csv"), data=df.to_csv(index=False), 
                          file_name="prvg_data.csv", mime="text/csv")
    
    st.text_area(t("report_summary"), value=summary_text, height=250)
    
    # Navigation buttons
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1:
        if st.button(t("prev_step")):
            st.session_state.current_step = 2
            st.rerun()

# Footer
st.markdown("---")
st.markdown(f"""
<div class='footer'>
{t('footer_text')}
<br><br>
{t('based_on')}
</div>
""", unsafe_allow_html=True)

# Add JavaScript for parameter selection
st.markdown("""
<script>
// Function to handle parameter selection
function selectParameter(param) {
    window.streamlitSessionState.set({selected_parameter: param});
}
</script>
""", unsafe_allow_html=True)
