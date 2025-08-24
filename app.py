import streamlit as st

st.set_page_config(page_title="PRVG / LAP Echo Evaluator", page_icon="🫀", layout="wide")

# -----------------------------
# Threshold profiles (ASE / BSE)
# -----------------------------
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
        # Keep identical for now; you can tweak if your local team prefers slight variants
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

# -----------------------------
# Helpers
# -----------------------------
def nz(x):
    return x is not None

def safe_mean(*vals):
    vals = [v for v in vals if v is not None]
    return sum(vals)/len(vals) if vals else None

def qc(meas, ctx):
    w = []
    if ctx["rhythm"] == "AF" and (meas["cycles_averaged"] or 0) < 5:
        w.append("AF: average ≥5–10 cycles with similar RR.")
    if nz(meas["TR_vmax"]) and meas["TR_vmax"] < 0.5:
        w.append("TR: envelope likely unusable (too low).")
    if ctx["tachycardia"]:
        w.append("Tachycardia: DT/IVRT shortened—interpret carefully.")
    if ctx["bradycardia"]:
        w.append("Bradycardia: diastasis affects E/A.")
    if ctx["poor_acoustic_window"]:
        w.append("Poor window: prefer LARS/LAVi; consider contrast.")
    return w

def compute_derived(meas):
    if meas["E"] is not None and meas["A"] is not None:
        meas["EA"] = meas["E"]/meas["A"] if meas["A"] != 0 else None
    if meas["e_mean"] is None:
        meas["e_mean"] = safe_mean(meas["e_septal"], meas["e_lateral"])
    if meas["pulm_SD"] is None and nz(meas["PV_S"]) and nz(meas["PV_D"]) and meas["PV_D"] != 0:
        meas["pulm_SD"] = meas["PV_S"]/meas["PV_D"]
    if meas["E_over_Vp"] is None and nz(meas["E"]) and nz(meas["Vp"]) and meas["Vp"] != 0:
        meas["E_over_Vp"] = meas["E"]/meas["Vp"]

# Atomic rules
def rule_relax_abn(meas, P):
    return (nz(meas["e_mean"]) and meas["e_mean"] <= P["e_mean_low"]) or \
           (nz(meas["e_septal"]) and meas["e_septal"] <= P["e_septal_low"]) or \
           (nz(meas["e_lateral"]) and meas["e_lateral"] <= P["e_lateral_low"])

def rule_Ee_abn(meas, P):
    return (nz(meas["E_over_e_mean"]) and meas["E_over_e_mean"] >= P["E_e_mean_abn"]) or \
           (nz(meas["E_over_e_septal"]) and meas["E_over_e_septal"] >= P["E_e_septal_abn"]) or \
           (nz(meas["E_over_e_lateral"]) and meas["E_over_e_lateral"] >= P["E_e_lateral_abn"])

def rule_TR_abn(meas, P): return nz(meas["TR_vmax"]) and meas["TR_vmax"] >= P["TR_vmax_abn"]
def rule_LAVi_abn(meas, P): return nz(meas["LAVi"]) and meas["LAVi"] >= P["LAVi_abn"]
def rule_LARS_low(meas, P): return nz(meas["LARS"]) and meas["LARS"] <= P["LARS_low"]
def rule_PV_SD_low(meas, P): return nz(meas["pulm_SD"]) and meas["pulm_SD"] <= P["pulm_SD_low"]
def rule_IVRT_short_sinus(meas, P): return nz(meas["IVRT"]) and meas["IVRT"] <= P["IVRT_short_sinus"]
def rule_IVRT_short_AF(meas, P): return nz(meas["IVRT"]) and meas["IVRT"] <= P["IVRT_short_AF"]
def rule_IVRT_short_restrict(meas, P): return nz(meas["IVRT"]) and meas["IVRT"] <= P["IVRT_short_restrict"]
def rule_ArA_abn(meas, P): return nz(meas["Ar_minus_A"]) and meas["Ar_minus_A"] >= P["Ar_minus_A_abn"]
def rule_TEe_short(meas, P): return nz(meas["TE_minus_e"]) and meas["TE_minus_e"] <= P["TE_minus_e_abn"]
def rule_restrictive(meas, P): return nz(meas["EA"]) and meas["EA"] >= P["E_A_restrictive"]
def rule_low_EA(meas, P): return nz(meas["EA"]) and meas["EA"] <= P["E_A_low_cut"]

def collect_surrogates_sinus(meas, P):
    tags = []
    if rule_Ee_abn(meas, P): tags.append("E/e′ high")
    if rule_TR_abn(meas, P): tags.append("TR_vmax high")
    if rule_LAVi_abn(meas, P): tags.append("LAVi enlarged")
    if rule_LARS_low(meas, P): tags.append("LARS low")
    if rule_PV_SD_low(meas, P): tags.append("PV S/D low")
    if rule_IVRT_short_sinus(meas, P): tags.append("IVRT short")
    return tags, len(tags)

# Evaluation kernels by context
def eval_sinus(meas, ctx, P):
    res = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    missing = []
    if meas["EA"] is None: missing.append("E/A")
    if meas["e_septal"] is None and meas["e_lateral"] is None: missing.append("e′")
    if all(v is None for v in [meas["E_over_e_mean"], meas["E_over_e_septal"], meas["E_over_e_lateral"]]): missing.append("E/e′")
    if meas["TR_vmax"] is None: missing.append("TR_vmax")
    if meas["LAVi"] is None: missing.append("LAVi")
    res["missing"] = missing

    relax_abn = rule_relax_abn(meas, P)
    tags, nSur = collect_surrogates_sinus(meas, P)

    if meas["EA"] is None:
        if nSur >= 2:
            res.update(status="High", grade="G2_or_G3", confidence="Medium" if relax_abn else "Low",
                       fired=tags, narrative="No E/A; ≥2 surrogates abnormal → LAP likely elevated.")
        else:
            res.update(status="Indeterminate", confidence="Low", fired=tags,
                       narrative="Need E/A with core surrogates.")
            res["reco"].append("Acquire E/A, repeat E/e′, TR, LAVi, LARS.")
        return finalize(res, meas)

    if rule_low_EA(meas, P):
        if nSur >= 1:
            res.update(status="High", grade="G1_with_high_LAP",
                       confidence="High" if nSur>=2 else "Medium",
                       fired=["E/A low"]+tags,
                       narrative="Impaired relaxation + ≥1 abnormal surrogate → elevated LAP.")
        else:
            res.update(status="Normal", grade="G1", confidence="Medium", fired=["E/A low"],
                       narrative="Low E/A without abnormal surrogates → LAP likely normal.")
        return finalize(res, meas)

    if rule_restrictive(meas, P):
        res.update(status="High", grade="G3 (restrictive)",
                   confidence="High" if nSur>=1 else "Medium",
                   fired=["Restrictive E/A"]+tags,
                   narrative="Restrictive inflow → elevated LAP.")
        return finalize(res, meas)

    # 0.8 < E/A < 2.0
    if nSur >= 2:
        res.update(status="High", grade="G2 (pseudonormal)", confidence="High",
                   fired=tags+["E/A intermediate"],
                   narrative="Intermediate E/A + ≥2 abnormal surrogates → elevated LAP.")
    elif nSur == 1:
        res.update(status="PossibleHigh", confidence="Medium",
                   fired=tags+["E/A intermediate"],
                   narrative="One abnormal surrogate → possible elevated LAP; add LARS/IVRT/PV.")
        res["reco"].append("Add LARS or PV S/D or IVRT; consider BNP or stress diastolic if symptomatic.")
    else:
        res.update(status="Normal", confidence="Medium",
                   fired=["E/A intermediate with no abnormal surrogates"],
                   narrative="No abnormal surrogates → LAP likely normal.")
    return finalize(res, meas)

def eval_AF(meas, ctx, P):
    res = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    flags = []
    if rule_IVRT_short_AF(meas, P): flags.append("IVRT short (AF)")
    if nz(meas["E_over_e_septal"]) and meas["E_over_e_septal"] >= P["E_e_septal_abn"]: flags.append("E/e′ septal high")
    if rule_TR_abn(meas, P): flags.append("TR_vmax high")
    if nz(meas["E_over_Vp"]) and meas["E_over_Vp"] >= P["E_over_Vp_AF_abn"]: flags.append("E/Vp high")
    if nz(meas["EDV"]) and meas["EDV"] <= P["EDV_AF_low"]: flags.append("PV EDV low (AF)")
    if nz(meas["DT"]) and meas["DT"] <= P["DT_short_AF"]: flags.append("DT short (AF)")

    if len(flags) >= 1:
        res.update(status="High", confidence="High" if len(flags)>=2 else "Medium",
                   fired=flags, narrative="AF: averaged surrogates abnormal.")
    else:
        res.update(status="Indeterminate", confidence="Low",
                   narrative="AF with no positive surrogates.")
        res["reco"].append("Average ≥5–10 beats; add LARS/LAVi/PV; consider BNP or invasive if discordant.")
    return finalize(res, meas)

def eval_MR(meas, ctx, P):
    res = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    flags=[]
    if rule_ArA_abn(meas, P): flags.append("PV Ar - MV A ≥ cutoff")
    if rule_TEe_short(meas, P): flags.append("TE - e′ short")
    if rule_Ee_abn(meas, P): flags.append("E/e′ high (caution in MR)")
    if rule_IVRT_short_sinus(meas, P): flags.append("IVRT short")
    if rule_LAVi_abn(meas, P): flags.append("LAVi enlarged")
    if len(flags)>=2 or rule_ArA_abn(meas, P):
        res.update(status="High", confidence="High" if len(flags)>=3 else "Medium", fired=flags)
    elif len(flags)==1:
        res.update(status="PossibleHigh", confidence="Low", fired=flags)
    else:
        res.update(status="Indeterminate", confidence="Low",
                   narrative="MR: use PV flow/LARS; echo surrogates may be distorted.")
        res["reco"].append("Add PV flow and LARS; consider invasive if management depends on LAP.")
    if res["narrative"] == "":
        res["narrative"] = "MR distorts transmitral indices; rely on Ar-A, IVRT, TE-e′, LAVi/LARS."
    return finalize(res, meas)

def eval_MS(meas, ctx, P):
    res = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    flags=[]
    if rule_ArA_abn(meas, P): flags.append("PV Ar - MV A ≥ cutoff")
    if nz(meas["IVRT"]) and meas["IVRT"] < 60: flags.append("IVRT very short (MS)")
    if len(flags)>=1:
        res.update(status="PossibleHigh", confidence="Low", fired=flags)
    else:
        res.update(status="Indeterminate", confidence="Low",
                   narrative="MS: transmitral E/A unreliable; need PV Ar-A, LARS, or hemodynamics.")
        res["reco"].append("Use PV flow and LARS; consider invasive LAP if clinical decision requires.")
    if res["narrative"] == "":
        res["narrative"] = "MS alters E/A; rely on PV Ar-A, IVRT, and adjuncts."
    return finalize(res, meas)

def eval_MAC(meas, ctx, P):
    res = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    if meas["EA"] is None:
        res.update(status="Indeterminate", confidence="Low",
                   narrative="MAC: need E/A and IVRT.")
        res["reco"].append("Obtain E/A and IVRT in MAC.")
        return finalize(res, meas)
    if meas["EA"] <= P["E_A_low_cut"]:
        if nz(meas["IVRT"]) and meas["IVRT"] < 80:
            res.update(status="High", confidence="Medium", fired=["E/A low","IVRT <80ms (MAC)"])
        else:
            res.update(status="Normal", confidence="Medium", fired=["E/A low (no supportive surrogates)"])
    elif meas["EA"] > 1.8:
        res.update(status="High", confidence="High", fired=["E/A >1.8 (MAC)"])
    else:
        if nz(meas["IVRT"]) and meas["IVRT"] < 80:
            res.update(status="High", confidence="Medium", fired=["IVRT <80ms in MAC"])
        else:
            res.update(status="Indeterminate", confidence="Low",
                       narrative="MAC mid-range E/A without IVRT support.")
            res["reco"].append("Use LARS or PV; consider invasive if needed.")
    if res["narrative"] == "":
        res["narrative"] = "MAC modifies annular velocities; combine E/A with IVRT and adjunct indices."
    return finalize(res, meas)

def eval_Aortic(meas, ctx, P):
    res = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    count=0; flags=[]
    if rule_Ee_abn(meas, P): count+=1; flags.append("E/e′ high")
    if rule_LAVi_abn(meas, P): count+=1; flags.append("LAVi enlarged")
    if rule_TR_abn(meas, P): count+=1; flags.append("TR_vmax high")
    if count>=2:
        res.update(status="High", confidence="Medium", fired=flags)
    elif count==1:
        res.update(status="PossibleHigh", confidence="Low", fired=flags)
    else:
        res.update(status="Indeterminate", confidence="Low",
                   narrative="AS/AR: combine surrogates; single marker weak.")
        res["reco"].append("Add LARS, PV S/D, or invasive measurement.")
    if res["narrative"] == "":
        res["narrative"] = "In AS/AR, require multiple concordant surrogates."
    return finalize(res, meas)

def eval_HCM(meas, ctx, P):
    res = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    flags=[]
    if rule_Ee_abn(meas, P): flags.append("E/e′ high")
    if rule_LAVi_abn(meas, P): flags.append("LAVi enlarged")
    if rule_TR_abn(meas, P): flags.append("TR_vmax high")
    if rule_ArA_abn(meas, P): flags.append("PV Ar-A positive")
    if len(flags)>=1:
        res.update(status="High", confidence="High" if len(flags)>=2 else "Medium", fired=flags)
    else:
        res.update(status="Indeterminate", confidence="Low",
                   narrative="HCM: consider exercise diastolic and LARS.")
        res["reco"].append("Add LARS; consider stress diastolic testing.")
    if res["narrative"] == "":
        res["narrative"] = "HCM: any concordant surrogate suggests elevated LAP."
    return finalize(res, meas)

def eval_Restrictive(meas, ctx, P):
    res = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    if rule_restrictive(meas, P):
        res.update(status="High", grade="G3 (restrictive)", confidence="High", fired=["Restrictive inflow"],
                   narrative="Classic restrictive filling indicates high LAP.")
        return finalize(res, meas)
    flags=[]
    if rule_IVRT_short_restrict(meas, P): flags.append("IVRT very short")
    if nz(meas["LARS"]) and meas["LARS"] <= 12: flags.append("Very low LARS")
    if rule_Ee_abn(meas, P): flags.append("E/e′ high")
    if rule_LAVi_abn(meas, P): flags.append("LAVi enlarged")
    if len(flags)>=2:
        res.update(status="High", confidence="High", fired=flags)
    elif len(flags)==1:
        res.update(status="PossibleHigh", confidence="Medium", fired=flags)
    else:
        res.update(status="Indeterminate", confidence="Low",
                   narrative="Restrictive substrate: need multi-modality or invasive hemodynamics.")
        res["reco"].append("Combine echo with NT-proBNP and consider invasive assessment.")
    if res["narrative"] == "":
        res["narrative"] = "Restrictive/Amyloid: emphasize IVRT, LARS, concordant surrogates."
    return finalize(res, meas)

def eval_Acute(meas, ctx, P):
    res = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    flags=[]
    if rule_TR_abn(meas, P): flags.append("TR_vmax high")
    if rule_LAVi_abn(meas, P): flags.append("LAVi enlarged")
    if rule_Ee_abn(meas, P): flags.append("E/e′ high")
    if len(flags)>=2:
        res.update(status="High", confidence="Medium", fired=flags)
    elif len(flags)==1:
        res.update(status="PossibleHigh", confidence="Low", fired=flags)
    else:
        res.update(status="Indeterminate", confidence="Low",
                   narrative="Acute states can distort Doppler; need ≥2 concordant signs.")
        res["reco"].append("Repeat when stabilized; consider invasive hemodynamics if decisions depend on LAP.")
    if res["narrative"] == "":
        res["narrative"] = "Acute context: be conservative; seek concordance."
    return finalize(res, meas)

def eval_PH_precap_vs_postcap(meas, ctx, P):
    res = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    flags=[]
    if rule_restrictive(meas, P): flags.append("Restrictive inflow")
    if rule_Ee_abn(meas, P): flags.append("E/e′ high")
    if rule_LAVi_abn(meas, P): flags.append("LAVi enlarged")
    if len(flags)>=1:
        res.update(status="High", confidence="Medium", fired=flags,
                   narrative="Echo supports postcapillary PH (elevated LAP).")
    else:
        res.update(status="Indeterminate", confidence="Low",
                   narrative="No clear left-heart elevation; precapillary PH possible.")
        res["reco"].append("Estimate PVR by Doppler if feasible; consider right heart cath.")
    return finalize(res, meas)

def eval_LVAD(meas, ctx, P):
    res = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    c=0; flags=[]
    if rule_Ee_abn(meas, P): c+=1; flags.append("E/e′ high")
    if nz(meas["LAVi"]) and meas["LAVi"] >= 33: c+=1; flags.append("LAVi ≥33")
    if rule_TR_abn(meas, P): c+=1; flags.append("TR_vmax high")
    if c>=2:
        res.update(status="High", confidence="Medium", fired=flags)
    elif c==1:
        res.update(status="PossibleHigh", confidence="Low", fired=flags)
    else:
        res.update(status="Indeterminate", confidence="Low",
                   narrative="LVAD distorts surrogates; prefer invasive ramp study/clinic data.")
    if res["narrative"] == "":
        res["narrative"] = "LVAD: require multiple concordant signs."
    return finalize(res, meas)

def eval_HTx(meas, ctx, P):
    res = {"status":"", "grade":"NA", "confidence":"", "fired":[], "missing":[], "qc":[], "narrative":"", "reco":[]}
    flags=[]
    if rule_Ee_abn(meas, P): flags.append("E/e′ high")
    if rule_TR_abn(meas, P): flags.append("TR_vmax high")
    if rule_LAVi_abn(meas, P): flags.append("LAVi enlarged")
    if len(flags)>=1:
        res.update(status="PossibleHigh", confidence="Low-Medium", fired=flags)
    else:
        res.update(status="Indeterminate", confidence="Low",
                   narrative="HTx: use multimodal assessment; tissue velocities altered.")
        res["reco"].append("Consider BNP/biopsy/hemodynamics as indicated.")
    if res["narrative"] == "":
        res["narrative"] = "HTx: combine multiple indices and clinical context."
    return finalize(res, meas)

# Finalize
def finalize(res, meas):
    n_rules = len(res["fired"])
    if res["status"] == "High":
        res["confidence"] = "High" if n_rules>=3 else ("Medium" if n_rules==2 else (res["confidence"] or "Medium"))
    elif res["status"] == "PossibleHigh":
        res["confidence"] = res["confidence"] or "Medium"
    elif res["status"] == "Normal":
        res["confidence"] = res["confidence"] or "Medium"
    else:
        res["confidence"] = res["confidence"] or "Low"
    if res["status"] == "Indeterminate":
        res["reco"].append("Improve acquisition; add LARS and PV flow.")
        res["reco"].append("Consider natriuretic peptides; if management depends on LAP, perform invasive hemodynamics.")
    if "TR_vmax high" not in res["fired"] and res["status"] in ["High","PossibleHigh"] and meas["TR_vmax"] is None:
        res["reco"].append("Acquire high-quality CW TR to refine PH/LAP interplay.")
    return res

def evaluate(meas, ctx, profile_name):
    P = PROFILES[profile_name]
    compute_derived(meas)
    res_qc = qc(meas, ctx)

    # Route special contexts first
    if ctx["LVAD"]:          res = eval_LVAD(meas, ctx, P)
    elif ctx["heart_tx"]:    res = eval_HTx(meas, ctx, P)
    elif ctx["MS_present"]:  res = eval_MS(meas, ctx, P)
    elif ctx["MR_sev"]:      res = eval_MR(meas, ctx, P)
    elif ctx["MAC_modsev"]:  res = eval_MAC(meas, ctx, P)
    elif ctx["amyloid_rcm"]: res = eval_Restrictive(meas, ctx, P)
    elif ctx["HCM"]:         res = eval_HCM(meas, ctx, P)
    elif ctx["aortic"]:      res = eval_Aortic(meas, ctx, P)
    elif ctx["acute"]:       res = eval_Acute(meas, ctx, P)
    elif ctx["precap_PH"]:   res = eval_PH_precap_vs_postcap(meas, ctx, P)
    elif ctx["rhythm"] == "AF":
        res = eval_AF(meas, ctx, P)
    else:
        res = eval_sinus(meas, ctx, P)

    res["qc"] = res_qc
    return res

# -----------------------------
# UI
# -----------------------------
st.title("🫀 PRVG / LAP Evaluation — Echo Decision Aid")
st.caption("Guideline-style thresholds (ASE/BSE) • Noninvasive LAP estimation • Use clinical judgment & invasive hemodynamics when needed.")

with st.sidebar:
    st.header("Settings")
    profile = st.selectbox("Guideline profile", ["ASE-2025","BSE-2024"])
    rhythm = st.radio("Rhythm", ["Sinus","AF"])
    st.markdown("---")
    st.subheader("Special contexts")
    MR_sev = st.checkbox("Mitral regurgitation ≥ moderate")
    MS_present = st.checkbox("Mitral stenosis")
    MAC_modsev = st.checkbox("Mitral annular calcification (mod–sev)")
    aortic = st.checkbox("Aortic valve disease (AS/AR)")
    HCM = st.checkbox("Hypertrophic cardiomyopathy")
    amyloid_rcm = st.checkbox("Restrictive / Amyloid")
    LVAD = st.checkbox("LVAD")
    heart_tx = st.checkbox("Heart transplant")
    acute = st.checkbox("Acute state (PE / sepsis / postop / ACS)")
    precap_PH = st.checkbox("Suspected precapillary PH")
    st.markdown("---")
    st.subheader("Acquisition notes")
    tachy = st.checkbox("Tachycardia (>100 bpm)")
    brady = st.checkbox("Bradycardia (<50 bpm)")
    poor_win = st.checkbox("Poor acoustic window")

st.markdown("### Enter measurements (use what you have; leave others blank)")
c1, c2, c3 = st.columns(3)

with c1:
    E = st.number_input("E (cm/s)", min_value=0.0, step=0.1, format="%.1f")
    A = st.number_input("A (cm/s)", min_value=0.0, step=0.1, format="%.1f")
    e_sept = st.number_input("e′ septal (cm/s)", min_value=0.0, step=0.1, format="%.1f")
    e_lat = st.number_input("e′ lateral (cm/s)", min_value=0.0, step=0.1, format="%.1f")
    E_e_mean = st.number_input("E/e′ (mean)", min_value=0.0, step=0.1, format="%.1f")
    E_e_sept = st.number_input("E/e′ (septal)", min_value=0.0, step=0.1, format="%.1f")
    E_e_lat = st.number_input("E/e′ (lateral)", min_value=0.0, step=0.1, format="%.1f")

with c2:
    TR_v = st.number_input("TR Vmax (m/s)", min_value=0.0, step=0.1, format="%.1f")
    LAVi = st.number_input("LAVi (mL/m²)", min_value=0.0, step=0.1, format="%.1f")
    LARS = st.number_input("LA reservoir strain LARS (%)", min_value=0.0, step=0.1, format="%.1f")
    PV_S = st.number_input("Pulm vein S (cm/s)", min_value=0.0, step=0.1, format="%.1f")
    PV_D = st.number_input("Pulm vein D (cm/s)", min_value=0.0, step=0.1, format="%.1f")
    ArA = st.number_input("PV Ar - MV A (ms)", min_value=0.0, step=1.0, format="%.0f")
    TEe = st.number_input("TE - e′ (ms)", min_value=0.0, step=1.0, format="%.0f")

with c3:
    IVRT = st.number_input("IVRT (ms)", min_value=0.0, step=1.0, format="%.0f")
    EDV = st.number_input("PV diastolic vel EDV (cm/s) (AF)", min_value=0.0, step=0.1, format="%.1f")
    Vp = st.number_input("Vp (cm/s) (for E/Vp)", min_value=0.0, step=0.1, format="%.1f")
    E_Vp = st.number_input("E/Vp (if already computed)", min_value=0.0, step=0.1, format="%.1f")
    DT = st.number_input("E-wave decel time DT (ms)", min_value=0.0, step=1.0, format="%.0f")
    HR = st.number_input("Heart rate (bpm)", min_value=0, step=1, format="%d")
    cycles = st.number_input("Averaged cycles (esp. AF)", min_value=0, step=1, format="%d")

if st.button("Evaluate", type="primary", use_container_width=True):
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
        "rhythm": "AF" if rhythm=="AF" else "sinus",
        "MR_sev": MR_sev,
        "MS_present": MS_present,
        "MAC_modsev": MAC_modsev,
        "aortic": aortic,
        "HCM": HCM,
        "amyloid_rcm": amyloid_rcm,
        "LVAD": LVAD,
        "heart_tx": heart_tx,
        "acute": acute,
        "precap_PH": precap_PH,
        "tachycardia": tachy, "bradycardia": brady, "poor_acoustic_window": poor_win
    }

    result = evaluate(meas, ctx, profile)

    # Pretty output
    st.markdown("## Results")
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
    cols[2].metric("Fired rules", str(len(result["fired"])))
    cols[3].metric("Missing critical", str(len(result["missing"])))

    if result["fired"]:
        st.markdown("**Triggered rules:**")
        st.write(", ".join(result["fired"]))
    if result["missing"]:
        st.markdown("**Missing measurements:**")
        st.write(", ".join(result["missing"]))
    if result["qc"]:
        st.markdown("**Acquisition / QC notes:**")
        for w in result["qc"]:
            st.caption("• " + w)
    if result["narrative"]:
        st.markdown("**Rationale:**")
        st.write(result["narrative"])
    if result["reco"]:
        st.markdown("**Recommendations:**")
        for r in result["reco"]:
            st.write("• " + r)

st.markdown("---")
st.caption("This tool synthesizes echo indices (ASE/BSE style cutoffs) to estimate LAP/PRVG. Always integrate with clinical context and invasive hemodynamics when decisions require precision.")
