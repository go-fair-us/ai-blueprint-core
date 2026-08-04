# Optimized prompt: metadata-schema-attribution-provenance-funder-grant

Source: `/home/fils/src/Projects/NIAID/ai-blueprint-core/okf/prompt_examples/metadata-schema/attribution-provenance/funder-grant.md`

---

# Prompt

## NEW INSTRUCTION SET FOR THE ASSISTANT

### OBJECTIVE
Create **machine‑actionable, Blueprint‑compliant JSON‑LD** that captures **complete funding information** (and all required metadata) for a NIAID Blueprint “worked example” (e.g., SDY998: AMP Rheumatoid Arthritis Phase 1). The output must be a **single, self‑contained Schema.org `Dataset`** object ready for ingestion by FAIR‑compliant repositories, APIs, and downstream tools.

---

### HIGH‑LEVEL WORKFLOW

1. **Retrieve the official Blueprint v2 document**  
   - URL: `https://raw.githubusercontent.com/go-fair-us/ai-blueprint-core/refs/heads/master/docs/BluePrint/NIAID_Blueprint_v2_26Sep2025_forExternal.md`  
   - If the live fetch fails (no browsing capability), **prepend a one‑line plain‑text comment** (starting with `#`) to the final output, e.g.:  
     `# Unable to fetch Blueprint v2 document; proceeding with last known version (26 Sep 2025).`  
   - **Do not** place this comment inside the JSON object. Continue using the latest known version (v2, 26 Sep 2025) and note any assumptions in a top‑level `note` field **only** when values are truly unknown.

2. **Collect scenario‑specific values** (study title, DOI, landing‑page URL, creators, ORCIDs, award numbers, funder RORs, program names/codes, dates, license, keywords, distribution URL, etc.).  
   - **Never** use generic placeholders such as `"UNKNOWN"` unless the information is genuinely unavailable.  
   - When a value is missing, insert `"UNKNOWN"` **and** add a concise entry to a top‑level `note` explaining what must be supplied later.  

3. **Generate realistic identifiers** when the scenario does not provide them, using the exact patterns below:  
   - **DOI**: `https://doi.org/10.21430/<ALPHANUMERIC>` (e.g., `https://doi.org/10.21430/M3KXJHSP4T`).  
   - **Repository accession** (ImmPort, GEO, SRA, OSF, CellxGene, NIAID‑DA, etc.): use authentic‑looking strings (`SDY998`, `GSE123456`, `SRP456789`, `https://osf.io/abcd1`, `https://cellxgene.cziscience.com/collections/hipc-immune-atlas-2024`, …).  
   - **NIH award numbers**: typical formats `R01AI123456-01`, `U19AI123456-01`, `1UH2AR067676-01`, `HHSN272201800006C`.  
   - **Wellcome Trust award numbers**: as supplied (e.g., `220240/Z/20/Z`).  
   - **Program codes**: official numeric/alphanumeric code (e.g., `"AI"` for NIH AI institute, `"HIPC"` for Human Immunology Project Consortium). If truly unknown, set `"UNKNOWN"` and note it.  

4. **Validate identifiers internally** (do not output validation results):  
   - All URLs must be syntactically valid.  
   - Every `Organization` inside a `MonetaryGrant` must have a **resolvable ROR** identifier.  
   - Every award must have a correct DOI URI:  
     - **NIH**: `https://doi.org/10.13039/100000002/{awardNumber}`  
     - **Wellcome**: `https://doi.org/10.13039/100004440/{awardNumber}`  
   - No duplicate funder entries unless they differ by `role`.  

5. **Construct the JSON‑LD** **exactly** in the field order required by the Blueprint (see “FIELD ORDER” below).  
   - Include **all required** fields.  
   - Add **optional but recommended** fields: `additionalProperty`, `citation`, `fundingStatement`, `contactPoint`, `potentialAction`.  
   - Keep the object **compact** (no trailing commas, proper quoting).  
   - Output **only** the JSON (or a single comment line followed by the JSON). Do **not** wrap the output in explanatory prose; you may enclose the whole response in a single fenced block for readability, but the block must contain **only** the comment (if any) and the JSON.  

---

### FIELD ORDER (must be followed verbatim)

1. `@context` – *object* `{ "@vocab": "https://schema.org/" }` (object form is preferred).  
2. `@type` – `"Dataset"`  
3. `identifier` – array of `PropertyValue` objects (include at least DOI and any repository‑specific IDs).  
4. `conformsTo` – `"https://www.niaid.nih.gov/data/blueprint/minimal-metadata-schema"`  
5. `schemaVersion` – `"2.0"`  
6. Core Dataset fields (exact sequence):  
   - `name`  
   - `description`  
   - `url`  
   - `dateCreated`  
   - `datePublished`  
   - `license`  
   - `keywords`  
   - `creator`  
   - `distribution`  
7. `funding` – array of `MonetaryGrant` objects  
8. `fundingStatement` – single string (human‑readable, machine‑parsable) concatenating funder name, award number, and DOI.  
9. `citation` – a `CreativeWork` object (must contain `@id` pointing to the dataset DOI).  
10. `additionalProperty` – array of `PropertyValue` objects (plain‑string values only).  
11. `contactPoint` – optional `ContactPoint` object (recommended).  
12. `potentialAction` – optional `SearchAction` (or equivalent) exposing the API endpoint.  
13. `note` – optional; present **only** if any `"UNKNOWN"` placeholders were used.  

---

### REQUIRED PROPERTIES & SPECIFICATIONS

| Property | Type / Structure | Rules |
|----------|------------------|-------|
| `@context` | object | `{ "@vocab": "https://schema.org/" }` |
| `@type` | string | `"Dataset"` |
| `identifier` | array of `PropertyValue` | Each entry: `@type:"PropertyValue"`, `propertyID` (e.g., `"DOI"`), `value` (full URL). Include at least DOI. |
| `conformsTo` | string | Fixed URI as above. |
| `schemaVersion` | string | `"2.0"` |
| `name` | string | Full study title (may include accession). |
| `description` | string | One‑sentence description (may echo title). |
| `url` | string (URL) | Permanent landing‑page URL. |
| `dateCreated` | string (ISO‑8601) | If only year known, use `"YYYY-01-01"`. |
| `datePublished` | string (ISO‑8601) | Same rule as `dateCreated`. |
| `license` | string (URL) | Prefer an **SPDX** URI (e.g., `https://spdx.org/licenses/CC0-1.0.html`). If license is truly custom, still provide a stable URL. |
| `keywords` | array of strings | 3‑5 relevant terms (use controlled vocabularies when possible). |
| `creator` | array of `Person` / `Organization` | Each entry must have `@type` and `name`. `orcid` optional for `Person`; `identifier` (ROR) optional for `Organization`. At least a name is required. |
| `distribution` | `DataDownload` (or array) | Required fields: `@type:"DataDownload"`, `contentUrl` (URL), `encodingFormat` (MIME). **Add** `accessURL` if the download URL differs from the access portal. |
| `funding` | array of `MonetaryGrant` | Each object must contain: <br>`@type:"MonetaryGrant"` <br>`awardNumber` (string) <br>`awardURI` (full DOI URL) <br>`status` (e.g., `"active"` or `"pending"`) <br>`funder` (Organization with `name`, `identifier` (ROR PropertyValue), optional `role`) <br>`programName` **or** `programCode` (at least one non‑`"UNKNOWN"`). <br>Optional dates: `expectedStartDate`, `expectedEndDate`. |
| `fundingStatement` | string | `"FunderName AwardNumber (AwardDOI); …"` |
| `citation` | `CreativeWork` | Fields: `@type:"CreativeWork"`, `@id` (same as dataset DOI URL), `author` (array), `datePublished`, `name`, `doi`, `citationFormat` (array of `{style, text}` objects). |
| `additionalProperty` | array of `PropertyValue` | Each entry: `@type:"PropertyValue"`, `name`, `value` (plain string). Must include at least: <br>`apiEndpoint` (URL returning the metadata) <br>`fairCompliance` (single‑sentence FAIR summary). |
| `contactPoint` | `ContactPoint` (optional) | Recommended: `@type:"ContactPoint"`, `email`, `url`, `contactType` (e.g., `"repository"`). |
| `potentialAction` | `SearchAction` (optional) | Recommended structure: <br>`@type:"SearchAction"` <br>`target` (API URL with `{?query}` placeholder) <br>`query-input` (e.g., `"required name=query"`). |
| `note` | string (optional) | List what `"UNKNOWN"` placeholders must be replaced. Only present when needed. |

---

### FUNDING‑SPECIFIC GUIDELINES

1. **ROR identifiers** (must be exact):  
   - NIAID: `https://ror.org/05gnns699`  
   - NIAMS: `https://ror.org/006zn3t30`  
   - Wellcome Trust: `https://ror.org/0330j0z60`  
   - Any other funder: look up in the ROR registry; if none exists, use `"UNKNOWN"` and list in `note`.  

2. **Award DOI schemes**  
   - **NIH** (including NIAID, NIAMS, etc.): `https://doi.org/10.13039/100000002/{awardNumber}`  
   - **Wellcome Trust**: `https://doi.org/10.13039/100004440/{awardNumber}`  
   - If an award does **not** have an official DOI, construct a stable placeholder (`https://nih.gov/award/{awardNumber}`) **and** note it in `note`.  

3. **Program identifiers**  
   - Prefer the official **numeric/alphanumeric** `programCode` (e.g., `"AI"` for NIAID AI institute, `"HIPC"` for Human Immunology Project Consortium).  
   - If only a descriptive name is known, use `programName`.  
   - **Never** leave **both** `programName` and `programCode` as `"UNKNOWN"`.  

4. **Funding role** (`role` inside `funder`):  
   - `"primary"` for the main funder, `"secondary"` for supporting funders, etc.  

5. **FundingStatement format** – exactly:  
   ```
   <Funder Name> <AwardNumber> (<AwardDOI>); <Funder Name> <AwardNumber> (<AwardDOI>) …
   ```

6. **FAIR compliance (additionalProperty)** – must be a **single** `PropertyValue` with `name:"fairCompliance"` and a plain‑text value such as:  
   ```
   "Findable: DOI and ROR IDs; Accessible: CC0 license and download URL; Interoperable: schema.org JSON‑LD; Reusable: provenance via funding and citation."
   ```

---

### INTERNAL VALIDATION CHECKLIST (run silently)

- ✅ All URLs syntactically valid.  
- ✅ Every `Organization` in a `MonetaryGrant` has a resolvable ROR ID.  
- ✅ Every award has a correct DOI URI (NIH or Wellcome) or a placeholder flagged in `note`.  
- ✅ No duplicate funder entries unless they differ by `role`.  
- ✅ All required fields present; any missing values replaced with `"UNKNOWN"` and documented in `note`.  
- ✅ JSON syntax is valid (no stray commas, correct quoting).  

---

### OUTPUT REQUIREMENTS

- The response must consist of **exactly one JSON‑LD object** (or a one‑line comment followed by the object).  
- **No surrounding prose** or explanatory text.  
- If you use a fenced code block for readability, it must contain **only** the comment (if any) and the JSON.  
- The JSON must be **valid**, **compact**, and follow the exact field ordering listed above.  
- Do **not** include any fields that are not part of Schema.org `Dataset` unless they appear inside `additionalProperty`, `contactPoint`, `potentialAction`, or `note`.  

---

### STRATEGY SUMMARY (for future assistants)

1. **Fetch Blueprint** → comment if unavailable.  
2. **Gather scenario data** → fill required fields, generate realistic identifiers where missing.  
3. **Validate identifiers & RORs** internally.  
4. **Assemble JSON‑LD** respecting the exact field order, using the object form for `@context`.  
5. **Add optional enhancements** (`contactPoint`, `potentialAction`, `accessURL`) following Blueprint recommendations.  
6. **Insert `note`** only when `"UNKNOWN"` values exist, enumerating what must be supplied later.  
7. **Run internal validation checklist** → only proceed if all checks pass.  
8. **Output** the comment (if any) then the JSON‑LD, with no extra text.  

--- 

*End of instruction set.*
