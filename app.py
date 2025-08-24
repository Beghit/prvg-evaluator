# app.py
# Streamlit PRVG / LAP Evaluator — context-aware, why + how tooltips, age & athlete handling
import streamlit as st
from math import isfinite

st.set_page_config(page_title="PRVG / LAP Evaluator", page_icon="🫀", layout="wide")

# ========================
# Configurable guideline profiles
# ========================
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
    },
    "BSE-2024": {
        # Same defaults for now (editable)
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

# ========================
# Utilities & QC
# ========================
def nz(x):
    return x is not None and (not (isinstance(x, float) and (x != x)))  # filters None and NaN

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

def qc(meas, ctx):
    w = []
    if ctx["rhythm"] == "AF" and (not nz(meas.get("cycles_averaged")) or meas.get("cycles_averaged") < 5):
        w.append("AF: average ≥5–10 cycles with similar RR intervals.")
    if nz(meas.get("TR_vmax")) and meas.get("TR_vmax") < 0.5:
        w.append("TR signal likely unusable; envelope suspiciously low.")
    if ctx.get("tachycardia"):
        w.append("Tachycardia shortens DT/IVRT — interpret with caution.")
    if ctx.get("bradycardia"):
        w.append("Bradycardia: diastasis may change E/A ratio.")
    if ctx.get("poor_acoustic_window"):
        w.append("Poor window: prefer LARS/LAVi or contrast-enhanced imaging.")
    return w

# ========================
# Atomic rules
# ========================
def rule_relax_abn(m, P):
    return (nz(m.get("e_mean")) and m["e_mean"] <= P["e_mean_low"]) or \
           (nz(m.get("e_septal")) and m["e_septal"] <= P["e_septal_low"]) or \
           (nz(m.get("e_lateral")) and m["e_lateral"] <= P["e_lateral_low"])

def rule_Ee_abn(m, P):
    return (nz(m.get("E_over_e_mean")) and m["E_over_e_mean"] >= P["E_e_mean_abn"]) or \
           (nz(m.get("E_over_e_septal")) and m["E_over_e_septal"] >= P["E_e_septal_abn"]) or \
           (nz(m.get("E_over_e_lateral")) and m["E_over_e_lateral"] >= P["E_e_lateral_abn"])

def rule_TR_abn(m, P): return nz(m.get("TR_vmax")) and m["TR_vmax"] >= P["TR_vmax_abn"]
def rule_LAVi_abn(m, P): return nz(m.get("LAVi")) and m["LAVi"] >= P["LAVi_abn"]
def rule_LARS_low(m, P): return nz(m.get("LARS")) and m["LARS"] <= P["LARS_low"]
def rule_PV_SD_low(m, P): return nz(m.get("pulm_SD")) and m["pulm_SD"] <= P["pulm_SD_low"]
def rule_IVRT_short_sinus(m, P): return nz(m.get("IVRT")) and m["IVRT"] <= P["IVRT_short_sinus"]
def rule_IVRT_short_AF(m, P): return nz(m.get("IVRT")) and m["IVRT"] <= P["IVRT_short_AF"]
def rule_IVRT_short_restrict(m, P): return nz(m.get("IVRT")) and m["IVRT"] <= P["IVRT_short_restrict"]
def rule_ArA_abn(m, P): return nz(m.get("Ar_minus_A")) and m["Ar_minus_A"] >= P["Ar_minus_A_abn"]
def rule_TEe_short(m, P): return nz(m.get("TE_minus_e")) and m["TE_minus_e"] <= P["TE_minus_e_abn"]
def rule_restrictive(m, P): return nz(m.get("EA")) and m["EA"] >= P["E_A_restrictive"]
def rule_low_EA(m, P): return nz(m.get("EA")) and m["EA"] <= P["E_A_low_cut"]

def collect_surrogates_sinus(m, P):
    tags = []
    if rule_Ee_abn(m, P): tags.append("E/e' high")
    if rule_TR_abn(m, P): tags.append("TR_vmax high")
    if rule_LAVi_abn(m, P): tags.append("LAVi enlarged")
    if rule_LARS_low(m, P): tags.append("LARS low")
    if rule_PV_SD_low(m, P): tags.append("PV S/D low")
    if rule_IVRT_short_sinus(m, P): tags.append("IVRT short")
    return tags, len(tags)

# ========================
# Core evaluation functions (sinus/AF + special contexts)
# ========================
def finalize(res, m):
    n_rules = len(res["fired"])
    if res["status"] == "High":
        res["confidence"] = "High" if n_rules >= 3 else ("Medium" if n_rules == 2 else (res.get("confidence") or "Medium"))
    elif res["status"] == "PossibleHigh":
        res["confidence"] = res.get("confidence") or "Medium"
    elif res["status"] == "Normal":
        res["confidence"] = res.get("confidence") or "Medium"
    else:
        res["confidence"] = res.get("confidence") or "Low"
    if res["status"] == "Indeterminate":
        res.setdefault("reco", []).append("Improve acquisition; add LA strain (LARS) and pulmonary vein flow.")
        res.setdefault("reco", []).append("Consider natriuretic peptides; if management depends on LAP, perform invasive hemodynamics.")
    if "TR_vmax high" not in res["fired"] and res["status"] in ["High", "PossibleHigh"] and not nz(m.get("TR_vmax")):
        res.setdefault("reco", []).append("Acquire high-quality CW TR to refine PH/LAP interplay.")
    return res

def eval_sinus(m, ctx, P):
    r = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    missing = []
    if not nz(m.get("EA")): missing.append("E/A")
    if not nz(m.get("e_septal")) and not nz(m.get("e_lateral")): missing.append("e'")
    if not any(nz(m.get(k)) for k in ["E_over_e_mean", "E_over_e_septal", "E_over_e_lateral"]): missing.append("E/e'")
    if not nz(m.get("TR_vmax")): missing.append("TR_vmax")
    if not nz(m.get("LAVi")): missing.append("LAVi")
    r["missing"] = missing

    relax_abn = rule_relax_abn(m, P)
    tags, nSur = collect_surrogates_sinus(m, P)

    # If E/A missing
    if not nz(m.get("EA")):
        if nSur >= 2:
            r.update(status="High", grade="G2_or_G3", confidence="Medium" if relax_abn else "Low", fired=tags,
                     narrative="E/A missing; multiple abnormal surrogates → likely elevated LAP.")
        else:
            r.update(status="Indeterminate", confidence="Low", fired=tags,
                     narrative="E/A missing and insufficient surrogates; obtain core Doppler measures.")
            r.setdefault("reco", []).append("Acquire E/A, repeat E/e', TR, LAVi, LARS.")
        return finalize(r, m)

    # E/A ≤0.8 -> impaired relaxation
    if rule_low_EA(m, P):
        if nSur >= 1:
            r.update(status="High", grade="G1_with_high_LAP", confidence="High" if nSur >= 2 else "Medium",
                     fired=["E/A low"] + tags, narrative="E/A ≤0.8 with ≥1 abnormal surrogate -> elevated LAP.")
        else:
            r.update(status="Normal", grade="G1", confidence="Medium", fired=["E/A low"],
                     narrative="E/A ≤0.8 without abnormal surrogates -> LAP likely normal.")
        return finalize(r, m)

    # E/A >= restrictive cutoff -> check athlete/age exceptions later
    if rule_restrictive(m, P):
        r.update(status="High", grade="G3 (restrictive)", confidence="High" if nSur >= 1 else "Medium",
                 fired=["Restrictive E/A"] + tags, narrative="E/A suggests restrictive filling -> high LAP (unless overridden by context).")
        return finalize(r, m)

    # Intermediate E/A (0.8 < EA < 2)
    if nSur >= 2:
        r.update(status="High", grade="G2 (pseudonormal)", confidence="High", fired=tags + ["E/A intermediate"],
                 narrative="Intermediate E/A with ≥2 abnormal surrogates → elevated LAP.")
    elif nSur == 1:
        r.update(status="PossibleHigh", grade="NA", confidence="Medium", fired=tags + ["E/A intermediate"],
                 narrative="One abnormal surrogate -> possible elevated LAP. Consider LARS/IVRT/pulmonary veins.")
        r.setdefault("reco", []).append("Add LARS or PV S/D or IVRT; consider BNP or stress diastolic if symptomatic.")
    else:
        r.update(status="Normal", grade="NA", confidence="Medium", fired=["E/A intermediate with no abnormal surrogates"],
                 narrative="No abnormal surrogates -> LAP likely normal.")
    return finalize(r, m)

def eval_AF(m, ctx, P):
    r = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    flags = []
    if rule_IVRT_short_AF(m, P): flags.append("IVRT short (AF)")
    if nz(m.get("E_over_e_septal")) and m["E_over_e_septal"] >= P["E_e_septal_abn"]: flags.append("E/e' septal high")
    if rule_TR_abn(m, P): flags.append("TR_vmax high")
    if nz(m.get("E_over_Vp")) and m["E_over_Vp"] >= P["E_over_Vp_AF_abn"]: flags.append("E/Vp high")
    if nz(m.get("EDV")) and m["EDV"] <= P["EDV_AF_low"]: flags.append("PV EDV low (AF)")
    if nz(m.get("DT")) and m["DT"] <= P["DT_short_AF"]: flags.append("DT short (AF)")
    if len(flags) >= 1:
        r.update(status="High", grade="NA", confidence="High" if len(flags) >= 2 else "Medium", fired=flags,
                 narrative="AF: averaged surrogates abnormal across multiple beats.")
    else:
        r.update(status="Indeterminate", confidence="Low", narrative="AF: insufficient abnormal surrogates.")
        r.setdefault("reco", []).append("Average ≥5–10 beats; add LARS/LAVi/PV; consider BNP or invasive testing if discordant.")
    return finalize(r, m)

# For brevity: implement simplified special-context wrappers that call above or apply tailored rule sets
# (MR, MS, MAC, HCM, Restrictive, Aortic, Acute, LVAD, HTx, PH) — logical approach follows earlier pseudocode
def eval_MR(m, ctx, P):
    r = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    f = []
    if rule_ArA_abn(m, P): f.append("PV Ar - MV A ≥ cutoff")
    if rule_TEe_short(m, P): f.append("TE - e' short")
    if rule_Ee_abn(m, P): f.append("E/e' high (interpret with caution in MR)")
    if rule_IVRT_short_sinus(m, P): f.append("IVRT short")
    if rule_LAVi_abn(m, P): f.append("LAVi enlarged")
    if len(f) >= 2 or rule_ArA_abn(m, P):
        r.update(status="High", confidence="High" if len(f) >= 3 else "Medium", fired=f)
    elif len(f) == 1:
        r.update(status="PossibleHigh", confidence="Low", fired=f)
    else:
        r.update(status="Indeterminate", confidence="Low",
                 narrative="MR distorts transmitral indices; rely on PV Ar-A, IVRT, TE-e' and LARS.")
        r.setdefault("reco", []).append("Add PV flow and LARS; consider invasive measurement if management depends on LAP.")
    if r["narrative"] == "": r["narrative"] = "Mitral regurgitation context: use adjunct indices."
    return finalize(r, m)

def eval_MS(m, ctx, P):
    r = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    f = []
    if rule_ArA_abn(m, P): f.append("PV Ar - MV A ≥ cutoff")
    if nz(m.get("IVRT")) and m["IVRT"] < 60: f.append("IVRT very short (MS)")
    if len(f) >= 1:
        r.update(status="PossibleHigh", confidence="Low", fired=f)
    else:
        r.update(status="Indeterminate", confidence="Low",
                 narrative="MS: transmitral indices unreliable. Use PV Ar-A, LARS or invasive hemodyn.")
        r.setdefault("reco", []).append("Consider invasive measurement if needed for decisions.")
    return finalize(r, m)

def eval_MAC(m, ctx, P):
    r = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    if not nz(m.get("EA")):
        r.update(status="Indeterminate", confidence="Low", narrative="MAC: E/A and IVRT needed.")
        r.setdefault("reco", []).append("Obtain E/A and IVRT.")
        return finalize(r, m)
    if m["EA"] <= P["E_A_low_cut"]:
        if nz(m.get("IVRT")) and m["IVRT"] < 80:
            r.update(status="High", confidence="Medium", fired=["E/A low", "IVRT <80ms (MAC)"])
        else:
            r.update(status="Normal", confidence="Medium", fired=["E/A low"])
    elif m["EA"] > 1.8:
        r.update(status="High", confidence="High", fired=["E/A >1.8 (MAC)"])
    else:
        if nz(m.get("IVRT")) and m["IVRT"] < 80:
            r.update(status="High", confidence="Medium", fired=["IVRT <80ms in MAC"])
        else:
            r.update(status="Indeterminate", confidence="Low", narrative="MAC: mid E/A without IVRT support.")
            r.setdefault("reco", []).append("Use LARS or PV; consider invasive if needed.")
    if r["narrative"] == "": r["narrative"] = "MAC modifies annular tissue velocities; combine E/A + IVRT + adjuncts."
    return finalize(r, m)

def eval_Aortic(m, ctx, P):
    r = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    count = 0; flags = []
    if rule_Ee_abn(m, P): count += 1; flags.append("E/e' high")
    if rule_LAVi_abn(m, P): count += 1; flags.append("LAVi enlarged")
    if rule_TR_abn(m, P): count += 1; flags.append("TR_vmax high")
    if count >= 2:
        r.update(status="High", confidence="Medium", fired=flags)
    elif count == 1:
        r.update(status="PossibleHigh", confidence="Low", fired=flags)
    else:
        r.update(status="Indeterminate", confidence="Low", narrative="AS/AR: combine multiple surrogates; single marker weak.")
        r.setdefault("reco", []).append("Add LA strain or PV data; consider invasive if needed.")
    return finalize(r, m)

def eval_HCM(m, ctx, P):
    r = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    f = []
    if rule_Ee_abn(m, P): f.append("E/e' high")
    if rule_LAVi_abn(m, P): f.append("LAVi enlarged")
    if rule_TR_abn(m, P): f.append("TR_vmax high")
    if rule_ArA_abn(m, P): f.append("PV Ar-A positive")
    if len(f) >= 1:
        r.update(status="High", confidence="High" if len(f) >= 2 else "Medium", fired=f)
    else:
        r.update(status="Indeterminate", confidence="Low", narrative="HCM: consider stress diastolic and LA strain.")
        r.setdefault("reco", []).append("Add exercise/stress diastolic testing or LARS.")
    return finalize(r, m)

def eval_Restrictive(m, ctx, P):
    r = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    if rule_restrictive(m, P):
        r.update(status="High", grade="G3 (restrictive)", confidence="High", fired=["Restrictive E/A"],
                 narrative="Restrictive E/A consistent with elevated LAP.")
        return finalize(r, m)
    f = []
    if rule_IVRT_short_restrict(m, P): f.append("IVRT very short")
    if nz(m.get("LARS")) and m["LARS"] <= 12: f.append("Very low LARS")
    if rule_Ee_abn(m, P): f.append("E/e' high")
    if rule_LAVi_abn(m, P): f.append("LAVi enlarged")
    if len(f) >= 2:
        r.update(status="High", confidence="High", fired=f)
    elif len(f) == 1:
        r.update(status="PossibleHigh", confidence="Medium", fired=f)
    else:
        r.update(status="Indeterminate", confidence="Low", narrative="Restrictive substrate: combine echo + biomarkers or invasive hemodynamics.")
        r.setdefault("reco", []).append("Consider NT-proBNP and invasive assessment if needed.")
    return finalize(r, m)

def eval_Acute(m, ctx, P):
    r = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    f=[]
    if rule_TR_abn(m, P): f.append("TR_vmax high")
    if rule_LAVi_abn(m, P): f.append("LAVi enlarged")
    if rule_Ee_abn(m, P): f.append("E/e' high")
    if len(f) >= 2:
        r.update(status="High", confidence="Medium", fired=f)
    elif len(f) == 1:
        r.update(status="PossibleHigh", confidence="Low", fired=f)
    else:
        r.update(status="Indeterminate", confidence="Low", narrative="Acute states can transiently alter Doppler; need ≥2 concordant signs.")
        r.setdefault("reco", []).append("Repeat when patient more stable or consider invasive testing if immediate decisions needed.")
    return finalize(r, m)

def eval_PH(m, ctx, P):
    r = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    f=[]
    if rule_restrictive(m, P): f.append("Restrictive inflow")
    if rule_Ee_abn(m, P): f.append("E/e' high")
    if rule_LAVi_abn(m, P): f.append("LAVi enlarged")
    if len(f) >=1:
        r.update(status="High", confidence="Medium", fired=f, narrative="Echo suggests post-capillary PH due to elevated LAP.")
    else:
        r.update(status="Indeterminate", confidence="Low", narrative="No clear left-heart elevation on echo; precapillary PH possible.")
        r.setdefault("reco", []).append("Estimate PVR by Doppler or consider RHC.")
    return finalize(r, m)

# ========================
# Master routing and age/athlete exceptions
# ========================
def apply_age_athlete_modifiers(res, m, age, athlete):
    """Do not change thresholds. Modify interpretation confidence/rules for young athletes (E/A>2) or elderly isolated E/e'."""
    notes = []
    # Young athlete: E/A > 2 alone less specific => don't classify as High solely on E/A
    if athlete or (age is not None and age < 40):
        # If result was High based only on restrictive E/A (no other fired rules), downgrade to PossibleHigh/Indeterminate
        if res.get("fired") == ["Restrictive E/A"] or (res.get("status") == "High" and "Restrictive E/A" in res.get("fired", []) and len(res.get("fired", [])) == 1):
            res["status"] = "PossibleHigh"
            res["confidence"] = "Low-Medium"
            notes.append("Athlete / age <40: solitary high E/A may be physiological; require supporting surrogates.")
    # Elderly isolated E/e' elevation -> be cautious
    if age is not None and age >= 75:
        # if the only fired rule is E/e' elevate confidence down
        fired = res.get("fired", [])
        if len(fired) == 1 and ("E/e'" in fired[0] or "E/e' septal" in fired[0]):
            res["confidence"] = "Low-Medium"
            notes.append("Age ≥75: isolated E/e' elevation interpreted cautiously without TR or LAVi support.")
    if notes:
        res.setdefault("reco", []).extend(notes)

def evaluate_master(meas, ctx, profile_name, age, athlete):
    P = PROFILES[profile_name]
    compute_derived(meas)
    q = qc(meas, ctx)

    # route
    if ctx.get("LVAD"):
        # simplified LVAD handling: rely on concordant indices (detailed LVAD logic can be expanded)
        r = eval_HCM(meas, ctx, P)
    elif ctx.get("heart_tx"):
        r = eval_HCM(meas, ctx, P)  # placeholder for detailed HTx logic
    elif ctx.get("MS_present"):
        r = eval_MS(meas, ctx, P)
    elif ctx.get("MR_sev"):
        r = eval_MR(meas, ctx, P)
    elif ctx.get("MAC_modsev"):
        r = eval_MAC(meas, ctx, P)
    elif ctx.get("amyloid_rcm"):
        r = eval_Restrictive(meas, ctx, P)
    elif ctx.get("HCM"):
        r = eval_HCM(meas, ctx, P)
    elif ctx.get("aortic"):
        r = eval_Aortic(meas, ctx, P)
    elif ctx.get("acute"):
        r = eval_Acute(meas, ctx, P)
    elif ctx.get("precap_PH"):
        r = eval_PH(meas, ctx, P)
    elif ctx.get("rhythm") == "AF":
        r = eval_AF(meas, ctx, P)
    else:
        r = eval_sinus(meas, ctx, P)

    r["qc"] = q
    apply_age_athlete_modifiers(r, meas, age, athlete)
    return r

# ========================
# UI: Context selector with minimal fields + measurement tooltips
# ========================
st.title("🫀 PRVG / LAP Evaluator — Context-aware + Why/How tooltips")
st.caption("ASE/BSE style thresholds. Age & Athlete aware. 'Why' panel explains which rules fired; 'How' shows measurement technique.")

with st.sidebar:
    st.header("Settings")
    profile = st.selectbox("Guideline profile", list(PROFILES.keys()))
    age = st.number_input("Patient age (years)", min_value=1, max_value=110, value=65, step=1)
    athlete = st.checkbox("Trained athlete (physiologic high E/A possible)")
    rhythm = st.radio("Rhythm", ["Sinus", "AF"])
    st.markdown("---")
    st.subheader("Clinical context (choose all that apply)")
    MR_sev = st.checkbox("Mitral regurgitation ≥ moderate")
    MS_present = st.checkbox("Mitral stenosis")
    MAC_modsev = st.checkbox("Mitral annular calcification (moderate–severe)")
    aortic = st.checkbox("Aortic valve disease (AS/AR)")
    HCM = st.checkbox("Hypertrophic cardiomyopathy (HCM)")
    amyloid_rcm = st.checkbox("Restrictive cardiomyopathy / Amyloid")
    LVAD = st.checkbox("LVAD")
    heart_tx = st.checkbox("Heart transplant")
    acute = st.checkbox("Acute state (PE / sepsis / postop / ACS)")
    precap_PH = st.checkbox("Suspected precapillary PH")
    st.markdown("---")
    st.subheader("Acquisition/UX")
    minimal_mode = st.checkbox("Minimal inputs only (recommended)", value=True)
    auto_eval = st.checkbox("Auto-evaluate when core fields present", value=True)
    st.markdown("**Acquisition notes**")
    tachy = st.checkbox("Tachycardia (>100 bpm)")
    brady = st.checkbox("Bradycardia (<50 bpm)")
    poor_win = st.checkbox("Poor acoustic window")

# decide core fields by context
def minimal_fields_for_context():
    if MS_present:
        return ["IVRT", "Ar_minus_A"]
    if MR_sev:
        return ["Ar_minus_A", "IVRT", "LAVi"]
    if amyloid_rcm:
        return ["E", "A", "LARS", "IVRT"]
    if aortic:
        return ["E_over_e_mean", "TR_vmax", "LAVi"]
    if rhythm == "AF":
        return ["IVRT", "TR_vmax", "DT"]
    # default sinus minimal
    return ["E", "A", "one_e_prime", "TR_vmax", "LAVi"]

core = minimal_fields_for_context()

# show measurement input with Why + How expanders
st.markdown("## Measurements (enter what you have; advanced items are hidden when Minimal mode is ON)")
c1, c2, c3 = st.columns([1,1,1])

# helper to decide visibility
def show_if(name):
    return (name in core) or (not minimal_mode)

# left column
with c1:
    E = st.number_input("E (cm/s)", min_value=0.0, step=0.1, format="%.1f", disabled=not show_if("E"))
    A = st.number_input("A (cm/s)", min_value=0.0, step=0.1, format="%.1f", disabled=not show_if("A"))
    e_sept = st.number_input("e' septal (cm/s)", min_value=0.0, step=0.1, format="%.1f", disabled=not (show_if("one_e_prime") or show_if("e_septal")))
    e_lat = st.number_input("e' lateral (cm/s)", min_value=0.0, step=0.1, format="%.1f", disabled=not (show_if("one_e_prime") or show_if("e_lateral")))
    E_e_mean = st.number_input("E/e' (mean)", min_value=0.0, step=0.1, format="%.1f", disabled=not show_if("E_over_e_mean"))

    # Why/how expanders near these inputs
    with st.expander("Why E / A ?"):
        st.write("**Why:** The E/A ratio reflects early (E) to late (A) ventricular filling. It helps detect impaired relaxation (low E/A) or restrictive physiology (high E/A).")
        st.write("**Clinical note:** in young healthy people and athletes, E/A can be >2 physiologically. Use age/athlete context.")
    with st.expander("How to measure E/A"):
        st.write("Apical 4-chamber PW Doppler at mitral leaflet tips, average 3 cycles in sinus (5–10 in AF where possible). Optimize alignment; minimize angle error.")

# middle column
with c2:
    E_e_sept = st.number_input("E/e' (septal)", min_value=0.0, step=0.1, format="%.1f", disabled=not show_if("E_over_e_septal"))
    E_e_lat = st.number_input("E/e' (lateral)", min_value=0.0, step=0.1, format="%.1f", disabled=not show_if("E_over_e_lateral"))
    TR_v = st.number_input("TR Vmax (m/s)", min_value=0.0, step=0.1, format="%.2f", disabled=not show_if("TR_vmax"))
    LAVi = st.number_input("LAVi (mL/m²)", min_value=0.0, step=0.1, format="%.1f", disabled=not show_if("LAVi"))
    LARS = st.number_input("LA Reservoir Strain LARS (%)", min_value=0.0, step=0.1, format="%.1f", disabled=not show_if("LARS"))

    with st.expander("Why E/e' ?"):
        st.write("**Why:** E/e' is a surrogate of LV filling pressure (E = transmitral early; e' = myocardial relaxation). Higher values suggest higher LAP.")
        st.write("**Note:** use mean E/e' if both septal & lateral available. In AF favor septal or averaged approaches and average multiple beats.")
    with st.expander("How to measure e' and E/e'"):
        st.write("Place TDI cursor at septal and lateral mitral annulus in apical 4C. Record peak early diastolic e' velocity (cm/s). For E/e' divide E by e' (mean if both). Use multiple cycles in AF.")

# right column
with c3:
    PV_S = st.number_input("Pulmonary vein S (cm/s)", min_value=0.0, step=0.1, format="%.1f", disabled=not show_if("PV_S"))
    PV_D = st.number_input("Pulmonary vein D (cm/s)", min_value=0.0, step=0.1, format="%.1f", disabled=not show_if("PV_D"))
    ArA = st.number_input("PV Ar - MV A (ms)", min_value=0.0, step=1.0, format="%.0f", disabled=not show_if("Ar_minus_A"))
    IVRT = st.number_input("IVRT (ms)", min_value=0.0, step=1.0, format="%.0f", disabled=not show_if("IVRT"))
    DT = st.number_input("E-wave decel time DT (ms)", min_value=0.0, step=1.0, format="%.0f", disabled=not show_if("DT"))

    with st.expander("Why pulmonary veins (S/D) and Ar-A?"):
        st.write("**Why:** Pulmonary vein S/D ratio and Ar-A (PV Ar duration - MV A duration) offer information on LA pressure and timing — useful when transmitral Doppler is confounded (MR, AF). Low S/D or prolonged Ar-A suggests elevated LAP.")
    with st.expander("How to measure pulmonary vein flow & Ar-A"):
        st.write("Use apical 4C, sample pulmonary vein with PW Doppler lateral to LA appendage. Measure systolic (S) and diastolic (D) velocities, and PV Ar duration vs MV A duration (Ar-A). Average multiple beats in AF.")

# advanced zone
with st.expander("Advanced / optional measurements (showing for completeness)"):
    EDV = st.number_input("PV diastolic vel EDV (cm/s) (AF)", min_value=0.0, step=0.1, format="%.1f")
    Vp = st.number_input("Vp (cm/s) (flow propagation speed for E/Vp)", min_value=0.0, step=0.1, format="%.1f")
    E_Vp = st.number_input("E/Vp (if precomputed)", min_value=0.0, step=0.1, format="%.1f")
    TEe = st.number_input("TE - e' (ms)", min_value=0.0, step=1.0, format="%.0f")
    LVEF = st.number_input("LVEF (%) (optional)", min_value=0.0, max_value=90.0, step=1.0, format="%.0f")
    HR = st.number_input("Heart rate (bpm)", min_value=0, step=1, format="%d")
    cycles = st.number_input("Averaged cycles (esp. AF)", min_value=0, step=1, format="%d")

# assemble measurement dict
meas = {
    "E": E or None, "A": A or None, "EA": None,
    "e_septal": e_sept or None, "e_lateral": e_lat or None, "e_mean": None,
    "E_over_e_mean": E_e_mean or None, "E_over_e_septal": E_e_sept or None, "E_over_e_lateral": E_e_lat or None,
    "TR_vmax": TR_v or None, "LAVi": LAVi or None, "LARS": LARS or None,
    "PV_S": PV_S or None, "PV_D": PV_D or None, "pulm_SD": None,
    "Ar_minus_A": ArA or None, "TE_minus_e": TEe or None, "IVRT": IVRT or None,
    "EDV": EDV or None, "Vp": Vp or None, "E_over_Vp": E_Vp or None,
    "DT": DT or None, "HR": HR or None, "cycles_averaged": cycles or None,
}

ctx = {
    "rhythm": "AF" if rhythm == "AF" else "sinus",
    "MR_sev": MR_sev, "MS_present": MS_present, "MAC_modsev": MAC_modsev,
    "aortic": aortic, "HCM": HCM, "amyloid_rcm": amyloid_rcm,
    "LVAD": LVAD, "heart_tx": heart_tx, "acute": acute, "precap_PH": precap_PH,
    "tachycardia": tachy, "bradycardia": brady, "poor_acoustic_window": poor_win,
}

# determine minimal required fields given core
def needed_for_minimal(core_fields, m):
    needed = set()
    for f in core_fields:
        if f == "one_e_prime":
            if not (nz(m.get("e_septal")) or nz(m.get("e_lateral"))):
                needed.add("e' (septal or lateral)")
        elif f == "E":
            if not nz(m.get("E")):
                needed.add("E")
        elif f == "A":
            if not nz(m.get("A")):
                needed.add("A")
        elif f == "E_over_e_mean":
            if not nz(m.get("E_over_e_mean")):
                needed.add("E/e' (mean)")
        else:
            map_key = {"TR_vmax":"TR Vmax", "LAVi":"LAVi", "LARS":"LARS", "Ar_minus_A":"PV Ar - MV A", "IVRT":"IVRT", "DT":"DT"}
            if not nz(m.get(f)):
                needed.add(map_key.get(f, f))
    return needed

needed = needed_for_minimal(core, meas)

# Evaluate automatically or by button
def render_results_block(result):
    st.markdown("## Results — PRVG / LAP Estimation")
    badge = result["status"]
    if badge == "High":
        st.error(f"Status: {badge}")
    elif badge == "PossibleHigh":
        st.warning(f"Status: {badge}")
    elif badge == "Normal":
        st.success(f"Status: {badge}")
    else:
        st.info(f"Status: {badge}")

    cols = st.columns(4)
    cols[0].metric("Grade", result["grade"])
    cols[1].metric("Confidence", result["confidence"])
    cols[2].metric("Triggered rules", str(len(result["fired"])))
    cols[3].metric("Missing critical", str(len(result["missing"])))

    st.markdown("### Why (which rules fired & rationale)")
    if result["fired"]:
        for r in result["fired"]:
            st.write(f"- {r}")
    else:
        st.write("- No specific surrogate rules triggered.")

    if result.get("narrative"):
        st.markdown("**Rationale / narrative:**")
        st.write(result["narrative"])

    if result.get("qc"):
        st.markdown("**Acquisition / QC notes:**")
        for w in result["qc"]:
            st.caption("• " + w)

    if result.get("reco"):
        st.markdown("**Recommendations:**")
        for rec in result["reco"]:
            st.write("• " + rec)

    st.markdown("---")
    # compact "Why details" that show thresholds used
    with st.expander("Show thresholds and exact checks used (for audit)"):
        st.write("Profile:", profile)
        st.write("Thresholds used:")
        st.json(PROFILES[profile])
        st.write("Measurements provided:")
        st.json(meas)

# run
if auto_eval:
    if len(needed) == 0:
        result = evaluate_master(meas, ctx, profile, age, athlete)
        render_results_block(result)
    else:
        st.info("Auto-evaluation waiting for minimal fields: " + ", ".join(sorted(needed)))
        if st.button("Evaluate now (even if incomplete)"):
            result = evaluate_master(meas, ctx, profile, age, athlete)
            render_results_block(result)
else:
    if st.button("Evaluate"):
        result = evaluate_master(meas, ctx, profile, age, athlete)
        render_results_block(result)

# finishing helpful text
st.markdown("---")
st.caption("Clinical decision support only. Noninvasive LAP estimates have limitations. Follow local protocols and consider natriuretic peptides or invasive hemodynamics when management hinges on exact filling pressures.")
