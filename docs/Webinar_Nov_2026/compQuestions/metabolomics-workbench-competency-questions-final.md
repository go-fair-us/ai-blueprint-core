# Metabolomics Workbench competency questions (final example set)

Verified with public HTTP GET calls (`curl -L`, no credentials) on 9 November 2026 (America/Chicago). These questions follow the shape of [`docs/Webinar_Nov_2026/compQuestions`](https://github.com/go-fair-us/ai-blueprint-core/tree/116743c1caaaa92d6574643251240598f04d771e/docs/Webinar_Nov_2026/compQuestions). They were derived from the public services on [Advanced Searches](https://www.metabolomicsworkbench.org/search/advancedsearches.php) and the [REST Help](https://www.metabolomicsworkbench.org/tools/mw_rest.php) examples that page links to.

This is an **external test set**. Metabolomics Workbench has not published these questions, and they have not been vetted by a repository operator or a domain expert. They are not a certification. Answerability is not scientific accuracy. The `competency-questions` prompt would still look for a site-authored list.

Each question has one checkable answer that can be finished within 5 public requests. Run up to 3 per origin as `competency-answerability` input. The input field is `origin:` (`target` is the report field). Keep the answer key with the grader. Paste only a fenced YAML run block into the chat the agent sees.

The HTML mass-search forms are multi-option POSTs. The questions use the documented REST counterparts (`study`, `refmet`, `compound`, and `moverz`). The HTML forms were inspected but not POSTed.

## HTTP notes for graders

- Grade the response **body**, not the HTTP status alone. Do not let a HEAD-only client fail a question on status.
- A GET of some `/rest/` URLs (including `/rest/study/study_id/ST000001/summary`, `/rest/refmet/name/Cholesterol/all`, and `/rest/compound/regno/11/name`) may return HTTP 200 and a usable JSON body, especially with `Accept: application/json`. Those 200s are not a fix of the earlier status finding: HEAD on the same URLs still returned HTTP 406 at 8:50 PM CT on 9 November 2026, and a GET without that Accept header can also return 406 while still carrying the fields in the body.
- `moverz` and `exactmass` URLs may return HTTP 302, then 200, with `Content-Type: text/html` even when the body is tab-separated or line-oriented text. Encode `+` in ion types as `%2B` (for example `M%2BH`).
- For precursor-ion tables, grade by the **smallest mass delta**, not by row order alone. If more than one name shares that delta, all of those names are the expected answer.

## Metabolomics Workbench

Origin: https://www.metabolomicsworkbench.org/

### MW-1 (lookup, stable)

**Q:** What is the study title and species of Metabolomics Workbench study ST000001?

**Expected answer:** Fatb Induction Experiment (FatBIE); Arabidopsis thaliana

**Check:** contains: 'FatBIE' AND 'Arabidopsis thaliana'

**Templates:** competency-answerability, metadata-api

**API calls:**

- `GET https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/summary` — {"fields": ["study_title", "species"], "headers": {"Accept": "application/json"}}

_Note:_ The same JSON also reports institute "University of California, Davis", 24 samples, and analysis type GC-MS.

### MW-2 (lookup, stable)

**Q:** What license and license URL does Metabolomics Workbench record for study ST000001?

**Expected answer:** CC BY-NC-ND; https://creativecommons.org/licenses/by-nc-nd/4.0/deed.en

**Check:** contains: 'CC BY-NC-ND' AND 'creativecommons.org/licenses/by-nc-nd/4.0'

**Templates:** competency-answerability, metadata-api, rights-and-license

**API calls:**

- `GET https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/summary` — {"fields": ["license", "license_url"], "headers": {"Accept": "application/json"}}

_Note:_ This license is in the REST summary JSON. It is not, on its own, a claim about the first HTML of the study page, and it is not a legal opinion.

### MW-3 (lookup, stable)

**Q:** What PubChem CID, InChIKey, and RefMet ID does Metabolomics Workbench RefMet assign to Cholesterol?

**Expected answer:** pubchem_cid 5997; InChIKey HVYWMOMLDIMFJA-DPAQBDIFSA-N; refmet_id RM0135639

**Check:** exact on '5997'; contains: 'HVYWMOMLDIMFJA-DPAQBDIFSA-N' AND 'RM0135639'

**Templates:** competency-answerability, vocabulary, persistent-identifiers, metadata-api

**API calls:**

- `GET https://www.metabolomicsworkbench.org/rest/refmet/name/Cholesterol/all` — {"fields": ["pubchem_cid", "inchi_key", "refmet_id"]}

_Note:_ The same record reports formula C27H46O, exact mass 386.354865, regno 34361, and super_class "Sterol Lipids".

### MW-4 (lookup, stable)

**Q:** What official RefMet name does the Metabolomics Workbench REST service return when matching the synonym "citrate"?

**Expected answer:** Citric acid

**Check:** exact (case-insensitive) on 'Citric acid'

**Templates:** competency-answerability, vocabulary

**API calls:**

- `GET https://www.metabolomicsworkbench.org/rest/refmet/match/citrate/name/` — {"field": "refmet_name"}

_Note:_ The same payload reports formula C6H8O7, exact mass 192.0270, and class "TCA acids".

### MW-5 (lookup, stable)

**Q:** What exact mass (m/z) and formula does the Metabolomics Workbench REST exact-mass service report for the [M+H]+ ion of PC(34:1)?

**Expected answer:** 760.585077; C42H83NO8P

**Check:** exact on 760.585077; contains: 'C42H83NO8P'

**Templates:** competency-answerability, metadata-api

**API calls:**

- `GET https://www.metabolomicsworkbench.org/rest/moverz/exactmass/PC(34:1)/M%2BH`

_Note:_ This is the documented `moverz` exact-mass example. The response may 302 to `LM_get_mass_web.php`, then return `Content-Type: text/html` with `PC 34:1`, `[M+H]+`, `760.585077`, and `C42H83NO8P` separated by `</br>`. The formula is the ion formula as reported. Status may be 200, 302, or 406; grade the body.

### MW-6 (lookup, semi-stable)

**Q:** How many named metabolites does analysis AN000001 of Metabolomics Workbench study ST000001 report?

**Expected answer:** 102

**Check:** numeric exact 102 (may change if the study is revised)

**Templates:** competency-answerability, metadata-api

**API calls:**

- `GET https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/number_of_metabolites/` — {"fields": ["analysis_id", "num_metabolites"]}

_Note:_ The same JSON reports analysis_id AN000001, 24 samples, and the study title Fatb Induction Experiment (FatBIE). Version and revision_no were both 1 in the companion summary record on this date.

### MW-7 (lookup, semi-stable)

**Q:** In the RefMet precursor-ion search at m/z 255.2, ion type [M+H]+, and mass tolerance 0.2, which names share the smallest mass delta, and what matched m/z is reported for them?

**Expected answer:** 5-Hydroxyculmorin and Hydroxypentadecadienoic acid; 255.1955 (delta 0.0045, formula C15H27O3)

**Check:** contains: '5-Hydroxyculmorin' AND 'Hydroxypentadecadienoic acid' AND '255.1955'

**Templates:** competency-answerability, vocabulary, metadata-api

**API calls:**

- `GET https://www.metabolomicsworkbench.org/rest/moverz/REFMET/255.2/M%2BH/0.2/txt` — {"parse": "all data rows with the smallest delta, not merely the first data row"}

_Note:_ This is the documented REST equivalent of the Advanced Searches RefMet precursor-ion form. The table in this check had 81 data rows. Two names tie at the smallest delta; do not treat 5-Hydroxyculmorin as the unique closest hit. Palmitoleic acid is also in the list (matched m/z 255.2319, delta 0.0319) but is not a closest hit. The closest names could change if RefMet is updated.

### MW-8 (lookup, semi-stable)

**Q:** In the virtual lipid-class precursor-ion search at m/z 513.45, ion type [M-2H]2-, and mass tolerance 0.2, what chemical formula do the closest matches share, and is DG 66:8 among them?

**Expected answer:** C69H118O5; yes. The closest names are DG 66:8, DG O-66:9;O, and TG O-66:8 (matched m/z 513.4495, delta 0.0005)

**Check:** contains: 'C69H118O5' AND 'DG 66:8'

**Templates:** competency-answerability, metadata-api

**API calls:**

- `GET https://www.metabolomicsworkbench.org/rest/moverz/LIPIDS/513.45/M-2H/0.2/txt` — {"parse": "rows with the smallest delta; the /txt table may concatenate matched m/z and delta"}

_Note:_ This is the documented LIPIDS virtual-database example (Advanced Searches option i). In this check the table had 77 rows and wrote matched m/z and delta as a single field (`513.4495.0005`). Parse that field before ranking by delta. Closest names could change if the virtual database is updated.

### MW-9 (lookup, semi-stable)

**Q:** In the Metabolite Database precursor-ion search at m/z 635.52, ion type [M+H]+, and mass tolerance 0.5, what is the name of the unique closest match (smallest delta)?

**Expected answer:** EC-18 (matched m/z 635.5245, delta 0.0045, formula C39H71O6)

**Check:** contains: 'EC-18'

**Templates:** competency-answerability, metadata-api

**API calls:**

- `GET https://www.metabolomicsworkbench.org/rest/moverz/MB/635.52/M%2BH/0.5/txt` — {"parse": "the unique row with the smallest delta"}

_Note:_ This is the documented Metabolite Database precursor-ion example (Advanced Searches options ii/iii). EC-18 was the unique closest row in this check (158 data rows; the next row was PE-Cer(d14:0/18:0) at delta 0.0077). That uniqueness could change if the database is updated.

### MW-10 (lookup, stable)

**Q:** What diet factor groups, and how many samples in each, does Metabolomics Workbench report for untargeted analysis AN000113?

**Expected answer:** Diet:Pooled_All 3; Diet:Pooled_Prudent 3; Diet:Pooled_Western 3; Diet:Prudent_611 13; Diet:Western_907 8

**Check:** contains: 'Diet:Pooled_All', 'Diet:Pooled_Prudent', 'Diet:Pooled_Western', 'Diet:Prudent_611', 'Diet:Western_907' and those counts

**Templates:** competency-answerability, metadata-api

**API calls:**

- `GET https://www.metabolomicsworkbench.org/rest/study/analysis_id/AN000113/untarg_factors/`

_Note:_ AN000113 is the documented untargeted-analysis example on the REST Help page, and it is the REST path that corresponds to the Advanced Searches untargeted MS service. This question uses the small factors endpoint, not a live count of untargeted studies. On this date, `GET .../rest/study/study_id/x/untarg_studies/` was large (2,471 analyses, 1,294 studies, about 0.75 MB) and associated AN000113 with study ST000072, “Effect of diet and age on ovarian metabolome (via tissue)” (Macaca fascicularis; University of North Carolina). The HTML untargeted m/z form was not POSTed.

### MW-11 (lookup, stable)

**Q:** What common name does the Metabolomics Workbench compound database give for regno 11?

**Expected answer:** Dideoxymycobactin

**Check:** exact (case-insensitive) on 'Dideoxymycobactin'

**Templates:** competency-answerability, metadata-api

**API calls:**

- `GET https://www.metabolomicsworkbench.org/rest/compound/regno/11/name` — {"field": "name"}

_Note:_ This is the first compound-context example on the REST Help page. A GET may return `application/json` with that name; grade the body, not the status alone (HEAD on this URL still returned HTTP 406 at 8:50 PM CT).

## Answerability runs

Paste only the fenced YAML into the chat the agent sees. Leave the answer-key table out.

### Run A

Stable study metadata and RefMet lookups.

```yaml
origin: https://www.metabolomicsworkbench.org/
questions:
  - "What is the study title and species of Metabolomics Workbench study ST000001?"
  - "What PubChem CID, InChIKey, and RefMet ID does Metabolomics Workbench RefMet assign to Cholesterol?"
  - "What official RefMet name does the Metabolomics Workbench REST service return when matching the synonym \"citrate\"?"
```

#### Answer key: Metabolomics Workbench Run A

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| MW-1 | Fatb Induction Experiment (FatBIE); Arabidopsis thaliana | contains: 'FatBIE' AND 'Arabidopsis thaliana' | `GET https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/summary` (`Accept: application/json`) | stable |
| MW-3 | pubchem_cid 5997; InChIKey HVYWMOMLDIMFJA-DPAQBDIFSA-N; refmet_id RM0135639 | exact on '5997'; contains InChIKey and 'RM0135639' | `GET https://www.metabolomicsworkbench.org/rest/refmet/name/Cholesterol/all` | stable |
| MW-4 | Citric acid | exact (case-insensitive) | `GET https://www.metabolomicsworkbench.org/rest/refmet/match/citrate/name/` | stable |

### Run B

License, the documented exact-mass example, and the ST000001 metabolite count.

```yaml
origin: https://www.metabolomicsworkbench.org/
questions:
  - "What license and license URL does Metabolomics Workbench record for study ST000001?"
  - "What exact mass (m/z) and formula does the Metabolomics Workbench REST exact-mass service report for the [M+H]+ ion of PC(34:1)?"
  - "How many named metabolites does analysis AN000001 of Metabolomics Workbench study ST000001 report?"
```

#### Answer key: Metabolomics Workbench Run B

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| MW-2 | CC BY-NC-ND; https://creativecommons.org/licenses/by-nc-nd/4.0/deed.en | contains: 'CC BY-NC-ND' AND 'creativecommons.org/licenses/by-nc-nd/4.0' | `GET https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/summary` (`Accept: application/json`) | stable |
| MW-5 | 760.585077; C42H83NO8P | exact on 760.585077; contains: 'C42H83NO8P' | `GET https://www.metabolomicsworkbench.org/rest/moverz/exactmass/PC(34:1)/M%2BH` | stable |
| MW-6 | 102 | numeric exact 102 (may change if revised) | `GET https://www.metabolomicsworkbench.org/rest/study/study_id/ST000001/number_of_metabolites/` | semi-stable |

### Run C

The three documented precursor-ion examples that correspond to Advanced Searches options (i) lipid virtual database, (ii) RefMet, and (iii) Metabolite Database. Grade by smallest delta.

```yaml
origin: https://www.metabolomicsworkbench.org/
questions:
  - "In the RefMet precursor-ion search at m/z 255.2, ion type [M+H]+, and mass tolerance 0.2, which names share the smallest mass delta, and what matched m/z is reported for them?"
  - "In the virtual lipid-class precursor-ion search at m/z 513.45, ion type [M-2H]2-, and mass tolerance 0.2, what chemical formula do the closest matches share, and is DG 66:8 among them?"
  - "In the Metabolite Database precursor-ion search at m/z 635.52, ion type [M+H]+, and mass tolerance 0.5, what is the name of the unique closest match (smallest delta)?"
```

#### Answer key: Metabolomics Workbench Run C

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| MW-7 | 5-Hydroxyculmorin and Hydroxypentadecadienoic acid; 255.1955 | contains: '5-Hydroxyculmorin' AND 'Hydroxypentadecadienoic acid' AND '255.1955' | `GET https://www.metabolomicsworkbench.org/rest/moverz/REFMET/255.2/M%2BH/0.2/txt` (81 rows in this check; two-name tie at delta 0.0045) | semi-stable |
| MW-8 | C69H118O5; yes. Closest names: DG 66:8, DG O-66:9;O, TG O-66:8 | contains: 'C69H118O5' AND 'DG 66:8' | `GET https://www.metabolomicsworkbench.org/rest/moverz/LIPIDS/513.45/M-2H/0.2/txt` (the `/txt` table concatenated matched m/z and delta as `513.4495.0005`) | semi-stable |
| MW-9 | EC-18 (matched m/z 635.5245, delta 0.0045) | contains: 'EC-18' | `GET https://www.metabolomicsworkbench.org/rest/moverz/MB/635.52/M%2BH/0.5/txt` (unique closest row among 158 hits in this check) | semi-stable |

### Run D

The documented untargeted-analysis example and the documented compound-database example.

```yaml
origin: https://www.metabolomicsworkbench.org/
questions:
  - "What diet factor groups, and how many samples in each, does Metabolomics Workbench report for untargeted analysis AN000113?"
  - "What common name does the Metabolomics Workbench compound database give for regno 11?"
```

#### Answer key: Metabolomics Workbench Run D

| ID | Expected answer | Check | Supporting call(s) | Stability |
|---|---|---|---|---|
| MW-10 | Diet:Pooled_All 3; Diet:Pooled_Prudent 3; Diet:Pooled_Western 3; Diet:Prudent_611 13; Diet:Western_907 8 | contains the five group names and those counts | `GET https://www.metabolomicsworkbench.org/rest/study/analysis_id/AN000113/untarg_factors/` | stable |
| MW-11 | Dideoxymycobactin | exact (case-insensitive) | `GET https://www.metabolomicsworkbench.org/rest/compound/regno/11/name` | stable |
