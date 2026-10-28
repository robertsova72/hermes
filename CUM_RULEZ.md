# Cum rulez laboratorul HERMES (v0.4.0-dev4)

## 1. Instalare (o singură dată)

1. Instalați Python 3.11 sau mai nou, de pe python.org. Pe Windows bifați „Add Python to PATH”.
2. Deschideți un terminal în folderul proiectului (cel care conține `app.py`):
   - Windows: scrieți `cmd` în bara de adresă a folderului și apăsați Enter;
   - Mac: click dreapta pe folder → Services → New Terminal at Folder.
3. Instalați bibliotecile:
   ```
   pip install -r requirements.txt
   ```
   (pe Mac: `pip3 install -r requirements.txt`)
4. Verificați mediul:
   ```
   python scripts/check_environment.py
   ```
   La `_hermes` trebuie să apară `"meyer_backend": "pywt-dmey-level10"` și `"formal_evidence_admissible": true`. Dacă apare `analytic-meyer-fallback`, PyWavelets nu este instalat: `pip install PyWavelets`.

Nu mai sunt necesare R sau rpy2.

## 2. Interfața

```
streamlit run app.py
```
(sau `python -m streamlit run app.py`)

Se deschide browserul. În bara laterală alegeți modul de validare și varianta simulatorului:

| Mod | Ce face | Varianta implicită |
|---|---|---|
| 1. Diagnostic distribuțional (D-01…D-05) | Verifică proprietățile procesului: medie, varianță, covarianță, autosimilaritate, lege marginală | corectată |
| 2. Volatilitate integrată – o celulă | Rulează o celulă din Tabelele 1–5 și o compară cu valoarea publicată | originală |
| 3. Matricea publicată | Rulează cele 60 de celule ale protocolului HERMES-TRL4-LVP-1.0 | originală |
| 4. Recuperarea parametrului Hurst | Estimează H pe traiectoriile simulate | originală |

Fiecare rulare se salvează în `results/` și poate fi descărcată ca arhivă din pagină.

## 3. Fără interfață (linie de comandă)

```
python scripts/run_distribution_diagnostics.py --variant corrected --n_paths 1000 --J 12
python scripts/run_distribution_diagnostics.py --variant legacy --n_paths 1000 --J 12
python scripts/run_published_matrix.py --variant legacy                  # 60 celule, J=18, N=17, 100 replicări
python scripts/run_published_matrix.py --variant legacy --processes fbm  # doar q = 1
python -m pytest -q                                                       # testele automate
```

Durate orientative pe un nucleu:
- matricea completă: 30–60 de minute;
- diagnosticul cu 1.000 de traiectorii la J = 12: câteva minute.

## 4. Cele două variante de simulator

- **Originală (`legacy`)** – codul auditat al autorilor, vectorizat, cu rezultate identice bit cu bit. Reproduce valorile publicate în Tabelele 1–5. Are însă două anomalii documentate:
  - centrarea seriei FARIMA: Z(1) ≈ 0 pentru q = 1, derivă negativă pentru q = 2, varianță prăbușită pentru q = 3;
  - normalizarea separată pe fiecare traiectorie.
- **Corectată (`corrected`)** – fără centrare, cu normalizare deterministă exactă: Var Z(1) = 1. Trece diagnosticul distribuțional, dar nu reproduce valorile publicate, care au fost obținute cu varianta originală.

Pentru protocolul înghețat HERMES-TRL4-LVP-1.0, a cărui referință sunt tabelele publicate, rulați matricea cu varianta originală și raportați diagnosticul distribuțional ca dovadă suplimentară, împreună cu limitările constatate.
