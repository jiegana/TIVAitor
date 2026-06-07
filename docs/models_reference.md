# TIVAitor: Pharmacokinetic Models Reference
*Extracted from TIVAtrainer (https://www.tivatrainer.com/about/) for future development planning.*

## 1. Hypnotics / Intravenous Anesthetics

### Propofol
*   **Marsh** (Standard)
*   **Marsh (short ke0)** (Likely Diprifusor implementation, ke0 = 0.26)
*   **Eleveld** (Universal model, all ages/weights)
*   **Eleveld (+opioid)** (Adjusted for opioid co-administration)
*   **Kenny: Paedfusor** (Pediatric model)
*   **Schnider (ke0)** (Effect-site targeting using fixed ke0)
*   **Schnider (TPE)** (Effect-site targeting using Time-to-Peak Effect method)
*   **Marsh/Thomson (Pd)** (Pediatric model)
*   **White/Kenny** (Alternative pediatric/infant model)
*   **Cortinez** (Obese patients model)

### Ketamine
*   **Ketamine Racemic:** Clements
*   **Ketamine Racemic:** Domino/Navarrete
*   **Ketamine S+ (Esketamine):** Geisslinger
*   **Ketamine S+ (Esketamine):** White

### Midazolam & Remimazolam
*   **Midazolam:** Zomorodi
*   **Remimazolam (ASA I/II):** Masui
*   **Remimazolam (ASA III/IV):** Masui
*   **Remimazolam (child):** Gao

### Dexmedetomidine
*   **Dexmedetomidine:** Dyck
*   **Dexmedetomidine:** Hannivoort

---

## 2. Opioids / Analgesics

### Remifentanil
*   **Minto** (Standard adult model)
*   **Eleveld** (Universal model)
*   **Kim-Obara-Egan** (Alternative model)

### Fentanyl
*   **Fentanyl:** Shafer (Standard 3-compartment model)

### Sufentanil
*   **Sufentanil:** Bovill
*   **Sufentanil:** Gepts
*   **Sufentanil:** Greeley/Bovil
*   **Sufentanil (short Thalf ke0):** Gepts (Effect-site targeting variation)

### Alfentanil
*   **Alfentanil:** Scott
*   **Alfentanil:** Maitre

### Morphine
*   **Morphine:** Sarton

---

## 3. Adjuncts / Non-Anesthetics

### Local Anesthetics
*   **Lidocaine:** Kuipers (IV Lidocaine PK)

### Non-Opioid Analgesics
*   **Paracetamol (IV):** Wuerthwein (Adult)
*   **Paracetamol (Ped):** Wang (Pediatric)

### Antifibrinolytics
*   **Tranexamic Acid:** Grassin-Delyle

### Novel Compounds
*   **2,6-disubstituted phenol:** IC, FE, GK (Experimental/Research compound)