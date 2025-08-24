# app.py
# Streamlit PRVG Assistant — Comprehensive medical reasoning with detailed tooltips
import streamlit as st
from math import isfinite
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="PRVG Assistant", page_icon="🫀", layout="wide")

# -----------------------
# CSS Styling
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
}
.how-box {
    background-color: #f0f9ff;
    border-left: 4px solid #0ea5e9;
    padding: 12px;
    border-radius: 4px;
    margin: 8px 0;
}
.tooltip-icon {
    color: #3b82f6;
    cursor: pointer;
    margin-left: 4px;
}
.parameter-group {
    background-color: #f8f9fa;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Profiles / thresholds
# -----------------------
PROFILES = {
    "ASE-2025": {
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
}
DEFAULT_PROFILE = "ASE-2025"
P = PROFILES[DEFAULT_PROFILE]

# -----------------------
# Medical Knowledge Base
# -----------------------
PARAMETER_EXPLANATIONS = {
    "E": {
        "why": "Mitral inflow E velocity reflects early diastolic filling, influenced by LA pressure and LV relaxation.",
        "how": "PW Doppler at mitral leaflet tips in apical 4-chamber view. Measure peak velocity in early diastole."
    },
    "A": {
        "why": "Mitral inflow A velocity reflects late diastolic filling due to atrial contraction.",
        "how": "PW Doppler at mitral leaflet tips in apical 4-chamber view. Measure peak velocity during atrial systole."
    },
    "e_septal": {
        "why": "Septal mitral annular tissue Doppler e' velocity is a marker of LV relaxation.",
        "how": "TDI at septal mitral annulus in apical 4-chamber view. Measure early diastolic velocity."
    },
    "e_lateral": {
        "why": "Lateral mitral annular tissue Doppler e' velocity is a marker of LV relaxation.",
        "how": "TDI at lateral mitral annulus in apical 4-chamber view. Measure early diastolic velocity."
    },
    "E_over_e_mean": {
        "why": "The ratio E/e' approximates LV filling pressures (e.g., PCWP).",
        "how": "Calculate as E divided by the average of septal and lateral e'."
    },
    "E_over_e_septal": {
        "why": "The ratio E/e' septal approximates LV filling pressures, especially in certain populations.",
        "how": "Calculate as E divided by septal e'."
    },
    "E_over_e_lateral": {
        "why": "The ratio E/e' lateral approximates LV filling pressures, but may be less specific.",
        "how": "Calculate as E divided by lateral e'."
    },
    "TR_vmax": {
        "why": "TR jet peak velocity estimates systolic pulmonary artery pressure, which can be elevated in heart failure.",
        "how": "CW Doppler across tricuspid valve. Use multiple views to align with jet and measure peak velocity."
    },
    "LAVi": {
        "why": "Left atrial volume index reflects chronic elevation of LV filling pressures.",
        "how": "Measure LA volume in apical 4-chamber and 2-chamber views at end-systole. Use area-length method and index to BSA."
    },
    "LARS": {
        "why": "LA reservoir strain is a sensitive marker of LA dysfunction and elevated filling pressures.",
        "how": "Use speckle-tracking echocardiography on apical 4-chamber and 2-chamber views to measure peak systolic strain."
    },
    "PV_S": {
        "why": "Pulmonary vein systolic flow velocity can be reduced when LA pressure is elevated.",
        "how": "PW Doppler in right upper pulmonary vein. Measure peak systolic velocity."
    },
    "PV_D": {
        "why": "Pulmonary vein diastolic flow velocity increases when LA pressure is elevated.",
        "how": "PW Doppler in right upper pulmonary vein. Measure peak diastolic velocity."
    },
    "Ar_minus_A": {
        "why": "The difference between pulmonary vein Ar duration and mitral A duration reflects LV end-diastolic pressure.",
        "how": "Measure duration of pulmonary vein Ar wave (atrial reversal) and mitral A wave. Subtract mitral A duration from Ar duration."
    },
    "IVRT": {
        "why": "Isovolumic relaxation time shortens with elevated filling pressures and prolongs with impaired relaxation.",
        "how": "CW or PW Doppler between LV outflow and inflow. Measure from aortic valve closure to mitral valve opening."
    },
    "DT": {
        "why": "Deceleration time of E velocity shortens with restrictive physiology and elevated pressures.",
        "how": "PW Doppler of mitral inflow. Measure time from E peak to where velocity declines to zero (or extrapolate if incomplete)."
    },
    "EDV": {
        "why": "Pulmonary vein end-diastolic velocity may increase with elevated LA pressure in atrial fibrillation.",
        "how": "PW Doppler in pulmonary vein. Measure velocity at end diastole."
    },
    "Vp": {
        "why": "Color M-mode flow propagation velocity (Vp) can be used to estimate LV relaxation.",
        "how": "Color M-mode in apical view aligned with inflow. Measure slope of first aliasing from mitral valve to LV apex."
    },
    "E_over_Vp": {
        "why": "The ratio E/Vp correlates with PCWP.",
        "how": "Calculate as E divided by Vp."
    },
    "TE_minus_e": {
        "why": "The time difference between onset of E and e' may reflect LV diastolic dysfunction.",
        "how": "Measure time from onset of mitral E to onset of e' on TDI."
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
    return notes

def create_tooltip(parameter_name):
    explanation = PARAMETER_EXPLANATIONS.get(parameter_name, {})
    why = explanation.get("why", "No explanation available.")
    how = explanation.get("how", "No measurement instructions available.")
    
    tooltip_html = f"""
    <div class="tooltip-icon" title="Why: {why}&#10;How: {how}">ℹ️</div>
    """
    return tooltip_html

# Atomic rule checks
def rule_low_e_prime(meas):
    return (nz(meas.get("e_mean")) and meas["e_mean"] <= P["e_mean_low"]) or \
           (nz(meas.get("e_septal")) and meas["e_septal"] <= P["e_septal_low"]) or \
           (nz(meas.get("e_lateral")) and meas["e_lateral"] <= P["e_lateral_low"])

def rule_Ee_high(meas):
    return (nz(meas.get("E_over_e_mean")) and meas["E_over_e_mean"] >= P["E_e_mean_abn"]) or \
           (nz(meas.get("E_over_e_septal")) and meas["E_over_e_septal"] >= P["E_e_septal_abn"]) or \
           (nz(meas.get("E_over_e_lateral")) and meas["E_over_e_lateral"] >= P["E_e_lateral_abn"])

def rule_TR_high(meas): 
    return nz(meas.get("TR_vmax")) and meas["TR_vmax"] >= P["TR_vmax_abn"]

def rule_LAVi_high(meas): 
    return nz(meas.get("LAVi")) and meas["LAVi"] >= P["LAVi_abn"]

def rule_LARS_low(meas): 
    return nz(meas.get("LARS")) and meas["LARS"] <= P["LARS_low"]

def rule_pv_SD_low(meas): 
    return nz(meas.get("pulm_SD")) and meas["pulm_SD"] <= P["pulm_SD_low"]

def rule_IVRT_short(meas): 
    return nz(meas.get("IVRT")) and meas["IVRT"] <= P["IVRT_short_sinus"]

def rule_restrictive_inflow(meas): 
    return nz(meas.get("EA")) and meas["EA"] >= P["E_A_restrictive"]

def rule_low_EA(meas): 
    return nz(meas.get("EA")) and meas["EA"] <= P["E_A_low_cut"]

def collect_surrogates(meas):
    tags = []
    if rule_Ee_high(meas): 
        tags.append("E/e' high")
    if rule_TR_high(meas): 
        tags.append("TR Vmax high")
    if rule_LAVi_high(meas): 
        tags.append("Enlarged LAVi")
    if rule_LARS_low(meas): 
        tags.append("Low LA strain (LARS)")
    if rule_pv_SD_low(meas): 
        tags.append("Pulm vein S/D low")
    if rule_IVRT_short(meas): 
        tags.append("Short IVRT")
    return tags

# Decision engine with comprehensive medical reasoning
def evaluate_PRVG(meas, ctx, age, athlete):
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
            "reco": ["Acquire missing core indices; consider LARS or natriuretic peptides if available."]
        }

    # Main decision logic
    # AF branch
    if ctx["rhythm"] == "AF":
        flags = []
        reasoning_af = []
        
        if nz(meas.get("IVRT")) and meas["IVRT"] <= P["IVRT_short_AF"]:
            flags.append("Short IVRT (AF)")
            reasoning_af.append(f"IVRT of {meas['IVRT']} ms ≤ {P['IVRT_short_AF']} ms suggests elevated filling pressures in AF.")
        
        if nz(meas.get("E_over_e_septal")) and meas["E_over_e_septal"] >= P["E_e_septal_abn"]:
            flags.append("E/e' septal high")
            reasoning_af.append(f"E/e' septal ratio of {meas['E_over_e_septal']} ≥ {P['E_e_septal_abn']} suggests elevated filling pressures.")
        
        if rule_TR_high(meas): 
            flags.append("TR Vmax high")
            reasoning_af.append(f"TR Vmax of {meas['TR_vmax']} m/s ≥ {P['TR_vmax_abn']} m/s suggests pulmonary hypertension.")
        
        if nz(meas.get("E_over_Vp")) and meas["E_over_Vp"] >= P["E_over_Vp_AF_abn"]:
            flags.append("E/Vp high")
            reasoning_af.append(f"E/Vp ratio of {meas['E_over_Vp']} ≥ {P['E_over_Vp_AF_abn']} suggests elevated filling pressures in AF.")
        
        # Decision making for AF
        reasoning.extend(reasoning_af)
        
        if len(flags) >= 2:
            status = "High"
            confidence = "High"
            narrative = "Multiple AF-specific surrogates abnormal, strongly suggesting elevated filling pressures."
        elif len(flags) == 1:
            status = "PossibleHigh"
            confidence = "Medium"
            narrative = "One AF-specific surrogate abnormal, suggesting possible elevated filling pressures."
        else:
            status = "Indeterminate"
            confidence = "Low"
            narrative = "No AF-specific surrogate clearly abnormal. Consider additional parameters."
        
        return {
            "status": status,
            "grade": "NA",
            "confidence": confidence,
            "fired": flags,
            "missing": [],
            "qc": qc,
            "reasoning": reasoning,
            "narrative": narrative,
            "reco": ["Average multiple beats; consider invasive measurement if clinical decisions depend on LAP."]
        }

    # Sinus rhythm branch
    EA = meas.get("EA")
    surrogates = collect_surrogates(meas)
    reasoning_sr = []
    
    # Low EA (impaired relaxation)
    if rule_low_EA(meas):
        reasoning_sr.append(f"E/A ratio of {EA} ≤ {P['E_A_low_cut']} indicates impaired relaxation (Grade I diastolic dysfunction).")
        
        if len(surrogates) >= 1:
            fired = ["E/A low"] + surrogates
            reasoning_sr.append(f"Abnormal surrogates ({', '.join(surrogates)}) suggest elevated LAP despite impaired relaxation pattern.")
            
            return {
                "status": "High",
                "grade": "G1_with_high_LAP",
                "confidence": "Medium" if len(surrogates)==1 else "High",
                "fired": fired,
                "missing": [],
                "qc": qc,
                "reasoning": reasoning_sr,
                "narrative": "Impaired relaxation with abnormal surrogate(s) suggests elevated LAP (Grade I with elevated filling pressures).",
                "reco": ["Consider LARS and/or BNP; correlate clinically."]
            }
        else:
            return {
                "status": "Normal",
                "grade": "G1",
                "confidence": "Medium",
                "fired": ["E/A low"],
                "missing": [],
                "qc": qc,
                "reasoning": reasoning_sr,
                "narrative": "E/A ≤0.8 without abnormal surrogates — likely normal LAP (Grade I diastolic dysfunction).",
                "reco": ["Follow clinical context."]
            }
    
    # Restrictive inflow
    if rule_restrictive_inflow(meas):
        reasoning_sr.append(f"E/A ratio of {EA} ≥ {P['E_A_restrictive']} indicates restrictive filling pattern (Grade III diastolic dysfunction).")
        
        # Apply athlete/young exception
        if athlete and age < 40:
            reasoning_sr.append("Athlete/young exception applied: restrictive pattern may be normal in highly trained individuals.")
            narrative = "Restrictive pattern detected but may be normal in athletes. Correlate with clinical context."
            reco = ["Evaluate for other causes of high output state.", "Consider exercise testing."]
            confidence = "Low"
        else:
            narrative = "Restrictive inflow suggests high LAP (Grade III diastolic dysfunction)."
            reco = ["Confirm with LAVi/TR and consider invasive testing if discordant."]
            confidence = "High" if len(surrogates)>=1 else "Medium"
        
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
            "reco": reco
        }

    # Intermediate EA (pseudonormal)
    if EA and 0.8 < EA < P["E_A_restrictive"]:
        reasoning_sr.append(f"E/A ratio of {EA} suggests pseudonormal filling (Grade II diastolic dysfunction).")
        
        if len(surrogates) >= 2:
            fired = surrogates
            reasoning_sr.append(f"Multiple abnormal surrogates ({', '.join(surrogates)}) strongly suggest elevated LAP.")
            
            return {
                "status": "High",
                "grade": "G2",
                "confidence": "High",
                "fired": fired,
                "missing": [],
                "qc": qc,
                "reasoning": reasoning_sr,
                "narrative": "Intermediate E/A with multiple abnormal surrogates → elevated LAP (Grade II diastolic dysfunction).",
                "reco": ["If symptomatic consider stress diastolic echo or BNP."]
            }
        elif len(surrogates) == 1:
            fired = surrogates
            reasoning_sr.append(f"One abnormal surrogate ({surrogates[0]}) suggests possible elevated LAP.")
            
            return {
                "status": "PossibleHigh",
                "grade": "NA",
                "confidence": "Medium",
                "fired": fired,
                "missing": [],
                "qc": qc,
                "reasoning": reasoning_sr,
                "narrative": "One abnormal surrogate → possible elevated LAP.",
                "reco": ["Add LARS/IVRT/PV flow or BNP to improve confidence."]
            }
        else:
            reasoning_sr.append("No abnormal surrogates suggest normal LAP despite pseudonormal pattern.")
            
            return {
                "status": "Normal",
                "grade": "NA",
                "confidence": "Medium",
                "fired": [],
                "missing": [],
                "qc": qc,
                "reasoning": reasoning_sr,
                "narrative": "Intermediate E/A without abnormal surrogates → LAP likely normal.",
                "reco": ["If symptoms persist, perform stress diastolic testing."]
            }

    # Fallback safety net
    reasoning_sr.append("Could not classify with confidence — data borderline or conflicting.")
    
    return {
        "status": "Indeterminate",
        "grade": "NA",
        "confidence": "Low",
        "fired": surrogates,
        "missing": [],
        "qc": qc,
        "reasoning": reasoning_sr,
        "narrative": "Could not classify with confidence — data borderline or conflicting.",
        "reco": ["Obtain additional indices: LARS, PV flow, TR, or consider invasive hemodynamics."]
    }

# -----------------------
# UI Implementation
# -----------------------
st.markdown("""
<div class='card'>
    <h2 style='margin:0'>PRVG Assistant — Comprehensive Echo Hemodynamic Assessment</h2>
    <div class='small-muted'>Adaptive inputs • Age & Athlete aware • Detailed medical reasoning • Export summary</div>
</div>
""", unsafe_allow_html=True)

st.write("")

# Step 1: Presentation selector
with st.container():
    p1, p2, p3 = st.columns([2, 1, 1])
    with p1:
        presentation = st.selectbox(
            "Clinical presentation (select best match)",
            ["General / Routine", "Athlete / Young", "Hypertension / LVH", "Heart Failure (chronic)", 
             "Atrial Fibrillation", "Pulmonary Hypertension", "Post-op / Acute", "Valve disease (MR/MS/AS)"]
        )
        age = st.number_input("Age (years)", min_value=12, max_value=110, value=65, step=1)
        athlete = True if presentation == "Athlete / Young" else False
        
    with p2:
        rhythm = st.radio("Rhythm", ["Sinus", "AF"], index=0 if presentation != "Atrial Fibrillation" else 1)
        minimal_mode = st.checkbox("Minimal inputs mode", value=True, 
                                  help="Show only the most relevant parameters for the selected presentation")
        auto_eval = st.checkbox("Auto-evaluate when minimal fields present", value=True)
        
    with p3:
        st.write("")  # spacing
        st.caption("Profile: ASE 2025 thresholds")
        # Add contextual flags
        tachycardia = st.checkbox("Tachycardia", value=False, 
                                 help="HR > 100 bpm - may shorten diastolic intervals")
        bradycardia = st.checkbox("Bradycardia", value=False, 
                                 help="HR < 60 bpm - may alter E/A relation")
        poor_window = st.checkbox("Poor acoustic window", value=False, 
                                 help="Consider LARS or contrast enhancement")

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

# Inputs area with tooltips
st.markdown("### Measurements")
st.caption("Minimal mode shows only required fields for selected presentation. Expand for more parameters.")

# Create input sections with tooltips
cols = st.columns(3)

def show_if(name):
    return (not minimal_mode) or (name in core)

with cols[0]:
    st.markdown("#### Mitral Inflow")
    E = st.number_input(f"E (cm/s) {create_tooltip('E')}", min_value=0.0, step=0.1, format="%.1f", 
                       disabled=not show_if("E"), key="E_input")
    A = st.number_input(f"A (cm/s) {create_tooltip('A')}", min_value=0.0, step=0.1, format="%.1f", 
                       disabled=not show_if("A"), key="A_input")
    EA = st.number_input("E/A ratio (if pre-calculated)", min_value=0.0, step=0.1, format="%.1f", 
                        disabled=not show_if("EA"), key="EA_input")

with cols[1]:
    st.markdown("#### Tissue Doppler")
    e_sept = st.number_input(f"e' septal (cm/s) {create_tooltip('e_septal')}", min_value=0.0, step=0.1, format="%.1f", 
                            disabled=not (show_if("e_septal") or show_if("one_e_prime")), key="e_septal_input")
    e_lat = st.number_input(f"e' lateral (cm/s) {create_tooltip('e_lateral')}", min_value=0.0, step=0.1, format="%.1f", 
                           disabled=not (show_if("e_lateral") or show_if("one_e_prime")), key="e_lateral_input")
    E_over_e_sept = st.number_input(f"E/e' septal {create_tooltip('E_over_e_septal')}", min_value=0.0, step=0.1, format="%.1f", 
                                   disabled=not show_if("E_over_e_septal"), key="E_over_e_septal_input")
    E_over_e_lat = st.number_input(f"E/e' lateral {create_tooltip('E_over_e_lateral')}", min_value=0.0, step=0.1, format="%.1f", 
                                  disabled=not show_if("E_over_e_lateral"), key="E_over_e_lateral_input")
    E_over_e_mean = st.number_input(f"E/e' mean {create_tooltip('E_over_e_mean')}", min_value=0.0, step=0.1, format="%.1f", 
                                   disabled=not show_if("E_over_e_mean"), key="E_over_e_mean_input")

with cols[2]:
    st.markdown("#### Other Parameters")
    TR_vmax = st.number_input(f"TR Vmax (m/s) {create_tooltip('TR_vmax')}", min_value=0.0, step=0.01, format="%.2f", 
                             disabled=not show_if("TR_vmax"), key="TR_vmax_input")
    LAVi = st.number_input(f"LAVi (mL/m²) {create_tooltip('LAVi')}", min_value=0.0, step=0.1, format="%.1f", 
                          disabled=not show_if("LAVi"), key="LAVi_input")
    LARS = st.number_input(f"LA reservoir strain (LARS %) {create_tooltip('LARS')}", min_value=0.0, step=0.1, format="%.1f", 
                          disabled=not show_if("LARS"), key="LARS_input")

# Advanced parameters
with st.expander("Advanced / Optional Parameters"):
    adv_cols = st.columns(2)
    
    with adv_cols[0]:
        st.markdown("#### Pulmonary Vein Flow")
        PV_S = st.number_input(f"PV S (cm/s) {create_tooltip('PV_S')}", min_value=0.0, step=0.1, format="%.1f", key="PV_S_input")
        PV_D = st.number_input(f"PV D (cm/s) {create_tooltip('PV_D')}", min_value=0.0, step=0.1, format="%.1f", key="PV_D_input")
        Ar_minus_A = st.number_input(f"PV Ar - MV A (ms) {create_tooltip('Ar_minus_A')}", min_value=0.0, step=1, format="%.0f", 
                                    disabled=not show_if("Ar_minus_A"), key="Ar_minus_A_input")
    
    with adv_cols[1]:
        st.markdown("#### Other Advanced Parameters")
        IVRT = st.number_input(f"IVRT (ms) {create_tooltip('IVRT')}", min_value=0.0, step=1, format="%.0f", key="IVRT_input")
        DT = st.number_input(f"DT (ms) {create_tooltip('DT')}", min_value=0.0, step=1, format="%.0f", key="DT_input")
        EDV = st.number_input(f"PV EDV (cm/s) {create_tooltip('EDV')}", min_value=0.0, step=0.1, format="%.1f", key="EDV_input")
        Vp = st.number_input(f"Vp (cm/s) {create_tooltip('Vp')}", min_value=0.0, step=0.1, format="%.1f", key="Vp_input")
        E_over_Vp = st.number_input(f"E/Vp {create_tooltip('E_over_Vp')}", min_value=0.0, step=0.1, format="%.1f", key="E_over_Vp_input")
        TEe = st.number_input(f"TE - e' (ms) {create_tooltip('TE_minus_e')}", min_value=0.0, step=1, format="%.0f", key="TE_minus_e_input")
        
    st.markdown("#### Contextual Parameters")
    ctx_cols = st.columns(3)
    with ctx_cols[0]:
        cycles = st.number_input("Averaged cycles (AF)", min_value=0, step=1, format="%d", key="cycles_input")
    with ctx_cols[1]:
        HR = st.number_input("HR (bpm)", min_value=0, step=1, format="%d", key="HR_input")
    with ctx_cols[2]:
        LVEF = st.number_input("LVEF (%)", min_value=0, max_value=100, step=1, format="%d", key="LVEF_input")

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
else:
    result = None

# Show evaluate controls
colA, colB, colC = st.columns([2, 1, 1])
with colA:
    if not auto_eval:
        if st.button("Evaluate now", key="eval"):
            result = evaluate_PRVG(meas, ctx, age, athlete)
with colB:
    st.write("")
    if st.button("Clear inputs"):
        st.experimental_rerun()
with colC:
    st.write("")
    st.caption("Auto-evaluation " + ("enabled" if auto_eval else "disabled"))

# If auto-eval not ready show info
if auto_eval and result is None:
    st.info("Auto-evaluation waits for minimal fields: " + ", ".join(needed))

# Results area
st.markdown("### Assessment Result")
if result is None:
    st.info("No evaluation performed yet. Provide required measurements above.")
else:
    # Color card
    status = result["status"]
    if status == "High":
        cls = "status-high"
    elif status == "PossibleHigh":
        cls = "status-possible"
    elif status == "Normal":
        cls = "status-normal"
    else:
        cls = "status-indet"
    
    st.markdown(f"""
    <div class='result-card {cls}'>
        <h3 style='margin:4px'>{status} Probability of Elevated Filling Pressures</h3>
        <div style='font-size:15px'>{result.get('narrative','')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics tiles
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Diastolic Grade", result.get("grade", "NA"))
    t2.metric("Confidence", result.get("confidence", ""))
    t3.metric("Triggered Rules", str(len(result.get("fired", []))))
    t4.metric("Missing Params", str(len(result.get("missing", []))))

    # Detailed reasoning
    with st.expander("Detailed Medical Reasoning", expanded=True):
        if result.get("reasoning"):
            st.markdown("#### Reasoning Steps:")
            for i, reason in enumerate(result["reasoning"], 1):
                st.markdown(f"{i}. {reason}")
        
        if result.get("fired"):
            st.markdown("#### Rules Triggered:")
            for r in result["fired"]:
                st.write(f"- {r}")
        
        if result.get("qc"):
            st.markdown("#### Acquisition Notes:")
            for q in result["qc"]:
                st.info(f"• {q}")

    # Recommendations
    with st.expander("Clinical Recommendations"):
        if result.get("reco"):
            for rec in result["reco"]:
                st.write(f"• {rec}")
        
        # Additional context-specific recommendations
        if result["status"] == "High":
            st.write("• Consider correlation with NT-proBNP/BNP levels if available.")
            st.write("• Evaluate for signs and symptoms of heart failure.")
            if ctx["rhythm"] == "AF":
                st.write("• In AF, consider rate control strategy to improve diastolic filling.")
        
        if athlete and result["status"] in ["High", "PossibleHigh"]:
            st.write("• In athletes, consider exercise stress echocardiography to distinguish physiological from pathological adaptation.")

    # Parameter explanations
    with st.expander("Parameter Explanations"):
        st.markdown("""
        #### Why These Parameters Matter
        Assessment of left atrial pressure (LAP) requires integration of multiple echocardiographic parameters 
        as no single measurement is perfectly accurate. The algorithm follows ASE/EACVI guidelines to integrate
        these parameters into a comprehensive assessment.
        """)
        
        used_params = [k for k, v in meas.items() if v is not None and k in PARAMETER_EXPLANATIONS]
        
        if used_params:
            st.markdown("##### Parameters Provided:")
            for param in used_params:
                exp = PARAMETER_EXPLANATIONS[param]
                st.markdown(f"**{param}**")
                st.markdown(f"<div class='why-box'>{exp['why']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='how-box'>{exp['how']}</div>", unsafe_allow_html=True)
        else:
            st.info("No parameters with explanations were provided.")

    # Export & report section
    st.markdown("---")
    st.markdown("#### Export Report")
    
    # summary text
    now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    summary_lines = [
        f"PRVG Assistant Comprehensive Report — {now}",
        f"Presentation: {presentation} (Age {age})  Rhythm: {ctx['rhythm']}",
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
    
    for k, v in meas.items():
        if v is not None:
            summary_lines.append(f"- {k}: {v}")
    
    summary_text = "\n".join(summary_lines)
    
    # Create two columns for export buttons
    exp_col1, exp_col2 = st.columns(2)
    
    with exp_col1:
        st.download_button("Download Full Report (Text)", data=summary_text, 
                          file_name="prvg_comprehensive_report.txt", mime="text/plain")
    
    with exp_col2:
        st.download_button("Download Data (CSV)", data=pd.DataFrame([meas]).to_csv(index=False), 
                          file_name="prvg_data.csv", mime="text/csv")
    
    st.text_area("Report Summary (for charting)", value=summary_text, height=250)

# Footer
st.markdown("---")
st.markdown("""
<div class='footer'>
This tool is for clinical decision support only. Noninvasive estimates of filling pressures have limitations — 
always correlate with clinical findings and consider natriuretic peptides or invasive hemodynamics when management depends on precise LAP assessment.
<br><br>
Based on ASE/EACVI 2016 Guidelines and subsequent literature.
</div>
""", unsafe_allow_html=True)
