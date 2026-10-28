"""HERMES Hermite/GHP Laboratory -- interfață Streamlit (dev4).

Pornire, din folderul proiectului:   streamlit run app.py
"""
import io
import json
import os
import sys
import zipfile
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
try:
    import streamlit as st
except ImportError as e:
    raise SystemExit("Instalați interfața: pip install streamlit") from e
import numpy as np
import pandas as pd
from hermes_lab.version import __version__
from hermes_lab.config import ExperimentConfig
from hermes_lab.environment import lab_environment
from hermes_lab.validation.runner import run_hurst_recovery
from hermes_lab.validation.integrated_runner import run_integrated_volatility
from hermes_lab.validation.published_matrix import run_published_matrix, matrix_plan
from hermes_lab.validation.distribution import run_distribution_diagnostics
from hermes_lab.reporting.report import build_html

st.set_page_config(page_title="HERMES – laborator TRL 4", layout="wide")

auth_key = os.environ.get("HERMES_AUTH_SESSION_KEY")
if auth_key and not st.session_state.get(auth_key):
    st.warning("Autentificați-vă în HERMES pentru a accesa laboratorul.")
    st.stop()

env = lab_environment()
st.title("HERMES – laborator de validare TRL 4")
st.caption(f"Versiune {__version__} · protocol HERMES-TRL4-LVP-1.0 · backend Meyer: {env['meyer_backend']}")
if not env["formal_evidence_admissible"]:
    st.warning("PyWavelets nu este instalat: pentru q = 2 și q = 3 se folosește transformata Meyer analitică. "
               "Rezultatele sunt orientative, nu dovezi formale. Instalați cu: pip install PyWavelets")

PROC_LABEL = {"fbm": "q = 1 · Brownian fracționar", "rosenblatt": "q = 2 · Rosenblatt", "hermite3": "q = 3 · Hermite"}
VAR_LABEL = {"corrected": "corectată (dev4: fără centrare, normalizare exactă)",
             "legacy": "originală (cod auditat, cu anomaliile documentate)"}


def out_dir(name):
    return ROOT / "results" / f"ui_{name}_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}"


def zip_folder(folder):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(Path(folder).rglob("*")):
            if f.is_file():
                z.write(f, arcname=str(f.relative_to(folder)))
    return buf.getvalue()


mode = st.sidebar.radio("Mod de validare", [
    "1. Diagnostic distribuțional (D-01…D-05)",
    "2. Volatilitate integrată – o celulă",
    "3. Matricea publicată (Tabelele 1–5)",
    "4. Recuperarea parametrului Hurst",
])
# Protocol HERMES-TRL4-LVP-1.0 benchmarks the published tables, which were produced with the
# original (legacy) simulator; the corrected variant is the default only for the diagnostics.
_default_variant = 0 if mode.startswith("1") else 1
variant = st.sidebar.selectbox("Varianta simulatorului", ["corrected", "legacy"], index=_default_variant,
                               format_func=VAR_LABEL.get)
if not mode.startswith("1") and variant == "corrected":
    st.sidebar.info("Tabelele publicate au fost generate cu varianta originală; varianta corectată nu le reproduce.")
seed = st.sidebar.number_input("Sămânța", 0, 2**31 - 1, 20261028)
st.sidebar.caption("elar = floor(2^(εJ)) ca în main.py și ec. (87); ε = 0,001 ⇒ elar = 1.")

# ---------------------------------------------------------------- 1. distributional diagnostics
if mode.startswith("1"):
    st.subheader("Diagnostic distribuțional")
    st.write("Verifică pe traiectorii independente proprietățile procesului Hermite: medie zero, Var Z(t) = t^(2H), "
             "structura de covarianță, autosimilaritatea și legea marginală (gaussiană pentru q = 1, ne-gaussiană pentru q ≥ 2).")
    with st.form("dist"):
        c1, c2, c3 = st.columns(3)
        procs = c1.multiselect("Procese", list(PROC_LABEL), default=list(PROC_LABEL), format_func=PROC_LABEL.get)
        Hs = c2.multiselect("H", [0.6, 0.7, 0.8, 0.9], default=[0.7, 0.8, 0.9])
        J = c2.slider("J (rezoluție)", 9, 14, 12)
        n_paths = c3.number_input("Traiectorii pe combinație", 100, 5000, 1000, step=100)
        go = st.form_submit_button("Rulează diagnosticul", type="primary")
    if go:
        if n_paths < 1000:
            st.info("Sub 1.000 de traiectorii, testele pentru q ≥ 2 (cozi grele) pot pica izolat din cauza eșantionului.")
        bar = st.progress(0.0, "Pornire…")
        od = out_dir(f"distribution_{variant}")
        df, detail, plots = run_distribution_diagnostics(procs, Hs, int(J), int(n_paths), int(seed), variant, od,
                                                         progress=lambda f, m: bar.progress(f, m))
        bar.empty()
        st.session_state["dist"] = (df, detail, plots, str(od))
    if "dist" in st.session_state:
        df, detail, plots, od = st.session_state["dist"]
        tests = ["D-01", "D-02", "D-03", "D-04", "D-05"]
        npass = int(df[tests].values.sum()); ntot = df[tests].size
        (st.success if npass == ntot else st.warning)(f"{npass} din {ntot} verificări trecute · varianta {df['variant'].iloc[0]}")
        show = df.copy(); show[tests] = show[tests].replace({True: "DA", False: "NU"})
        st.dataframe(show, hide_index=True, use_container_width=True)
        for key, pl in plots.items():
            with st.expander(key):
                g1, g2 = st.columns(2)
                g1.caption("10 traiectorii")
                g1.line_chart(pd.DataFrame(np.asarray(pl["paths"]).T, index=np.round(pl["time"], 4)))
                g2.caption("Var Z(t): empiric vs. teoretic t^(2H)")
                g2.line_chart(pd.DataFrame({"empiric": pl["var_emp"], "teoretic": pl["var_th"]}, index=np.round(pl["t_var"], 4)))
                st.json(detail[key], expanded=False)
        st.download_button("Descarcă rezultatele", zip_folder(od), file_name=f"{Path(od).name}.zip")

# ---------------------------------------------------------------- 2. single integrated-volatility cell
elif mode.startswith("2"):
    st.subheader("Volatilitate integrată – o celulă din articol")
    with st.form("iv"):
        c1, c2, c3 = st.columns(3)
        process = c1.selectbox("Proces", list(PROC_LABEL), format_func=PROC_LABEL.get)
        hfun = c1.selectbox("h(t)", ["identity", "cubic", "exponential", "square_root"])
        hurst = c2.select_slider("H", options=[0.6, 0.7, 0.8, 0.9], value=0.7)
        gamma = c2.selectbox("γ", [0.8, 0.95], index=1)
        J = c3.number_input("J", 8, 18, 18)
        N = c3.number_input("N", 4, 17, 17)
        reps = c3.number_input("Replicări (100 = formal)", 1, 500, 100)
        go = st.form_submit_button("Rulează", type="primary")
    if go:
        cfg = ExperimentConfig(experiment_id="ui_iv", process=process, hurst=hurst, J=int(J), N=int(min(N, J)),
                               gamma=gamma, replications=int(reps), seed=int(seed), h_function=hfun,
                               simulator_variant=variant).validate()
        od = out_dir(f"iv_{variant}")
        with st.spinner("Simulare…"):
            df, agg = run_integrated_volatility(cfg, od)
        build_html(od)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Media estimării", f"{agg['mean']:.4f}")
        m2.metric("Media publicată", "—" if agg.get("published_reference_mean") is None else f"{agg['published_reference_mean']:.3f}")
        m3.metric("Țintă teoretică", f"{agg['target']:.4f}")
        m4.metric("Status", f"{agg.get('status')} / {agg.get('formal_status')}")
        st.json(agg, expanded=False)
        st.download_button("Descarcă rezultatele", zip_folder(od), file_name=f"{od.name}.zip")

# ---------------------------------------------------------------- 3. published matrix
elif mode.startswith("3"):
    st.subheader("Matricea publicată – 60 de celule (5 familii × 4 H × 3 procese)")
    st.write("Fiecare celulă se compară cu media și abaterea standard publicate (Welch și F, Bonferroni α = 0,05/60). "
             "Execuția formală cere 100 de replicări, J = 18, N = 17 și PyWavelets instalat.")
    with st.form("mx"):
        c1, c2 = st.columns(2)
        procs = c1.multiselect("Procese", list(PROC_LABEL), default=list(PROC_LABEL), format_func=PROC_LABEL.get)
        reps = c1.number_input("Replicări pe celulă", 2, 200, 100)
        J = c2.number_input("J", 8, 18, 18)
        N = c2.number_input("N", 4, 17, 17)
        est = len(procs) * 20 * int(reps) * (0.8 if J >= 18 else 0.05)
        st.caption(f"Durată orientativă: ~{est / 60:.0f} minute pe un nucleu.")
        go = st.form_submit_button("Rulează matricea", type="primary")
    if go:
        base = ExperimentConfig(experiment_id="ui_matrix", process="fbm", hurst=0.6, J=int(J), N=int(min(N, J)), gamma=0.8,
                                replications=int(reps), seed=int(seed), simulator_variant=variant).validate()
        od = out_dir(f"matrix_{variant}")
        with st.spinner("Rulare matrice… (fereastra trebuie să rămână deschisă)"):
            res = run_published_matrix(base, od, process_filter=set(procs))
        st.session_state["mx"] = (res, str(od))
    if "mx" in st.session_state:
        res, od = st.session_state["mx"]
        cols = [c for c in ["h_function", "gamma", "H", "process", "mean", "std", "published_reference_mean",
                            "published_reference_std", "status", "formal_status", "accept_mean_p_value",
                            "accept_variance_p_value", "execution_status"] if c in res.columns]
        counts = res["status"].value_counts().to_dict() if "status" in res else {}
        st.write("Rezumat status celule:", counts)
        st.dataframe(res[cols], hide_index=True, use_container_width=True)
        st.download_button("Descarcă rezultatele", zip_folder(od), file_name=f"{Path(od).name}.zip")

# ---------------------------------------------------------------- 4. Hurst recovery
else:
    st.subheader("Recuperarea parametrului Hurst (Local Whittle, GPH)")
    with st.form("hr"):
        c1, c2 = st.columns(2)
        process = c1.selectbox("Proces", list(PROC_LABEL), format_func=PROC_LABEL.get)
        hurst = c1.select_slider("H", options=[0.6, 0.7, 0.8, 0.9], value=0.7)
        J = c2.number_input("J", 8, 18, 12)
        reps = c2.number_input("Replicări", 1, 500, 20)
        go = st.form_submit_button("Rulează", type="primary")
    if go:
        cfg = ExperimentConfig(experiment_id="ui_hurst", process=process, hurst=hurst, J=int(J), N=min(10, int(J)),
                               gamma=0.95, replications=int(reps), seed=int(seed), simulator_variant=variant).validate()
        od = out_dir(f"hurst_{variant}")
        df = run_hurst_recovery(cfg, od)
        build_html(od)
        st.metric("H estimat (Local Whittle, medie)", f"{df['H_local_whittle'].mean():.3f}", f"{df['H_local_whittle'].mean() - hurst:+.3f}")
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.download_button("Descarcă rezultatele", zip_folder(od), file_name=f"{od.name}.zip")

st.divider()
st.caption("Ramura Hermite generalizată (GHP) rămâne exclusă din baza TRL 4 până la validarea științifică separată.")
