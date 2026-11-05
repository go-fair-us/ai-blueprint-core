# Text and Data Mining (TDM)

Text and data mining means using automated techniques to analyze digital text or data. It can support research and other uses, including some AI development. The legal rules depend on the jurisdiction, the content, and the circumstances; a website signal is not a substitute for checking those rules. This overview is informational, not legal advice.

## The EU rule and rights reservations

[Article 4 of the EU Copyright in the Digital Single Market Directive](https://eur-lex.europa.eu/eli/dir/2019/790/oj/eng#art_4) provides a TDM exception for works that are lawfully accessible, unless rightsholders expressly reserve their rights in an appropriate manner, such as machine-readable means for content made publicly available online. The Directive also has a distinct research exception in Article 3. Which provision applies depends on the circumstances.

The [EU AI Act, Article 53(1)(c)](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng#art_53), requires providers of general-purpose AI models within its scope to put in place a copyright-compliance policy, including identifying and complying with relevant rights reservations. This is not a blanket rule for every AI system or company, and a web declaration alone does not determine whether a particular use is lawful.

## TDM Reservation Protocol (TDMRep)

The [TDM Reservation Protocol (TDMRep)](https://www.w3.org/community/reports/tdmrep/CG-FINAL-tdmrep-20240510/) is a [W3C Community Group Final Report](https://www.w3.org/community/tdmrep/), not a W3C Recommendation. It describes ways to publish machine-readable TDM rights signals, including a site-level `/.well-known/tdmrep.json` file, HTTP response headers, and HTML metadata. The report also specifies how an agent should interpret declarations when more than one applies; follow its rules rather than assuming that one signal always overrides another.

The protocol uses two properties:

- `tdm-reservation`: `1` indicates that TDM rights are reserved; `0` indicates that they are not reserved by that declaration.
- `tdm-policy`: an optional link to a policy or licensing information.

These are signals about rights, not access controls. The policy link may provide more detail, but a reservation signal does not itself grant permission or settle questions about exceptions, licenses, or applicable law. Check the report for the supported mechanisms and format-specific details before embedding metadata in downloadable files.

## Related signals and robots.txt

Other machine-readable signals sit near TDMRep but mean different things:

- **[TDM·AI](https://docs.tdmai.org/)** defines AI-use preferences. It is not TDMRep; read its current specification before treating a declaration as a rights reservation.
- **IETF AI Preferences (AIPREF)** is draft work on vocabulary and attachment (including a `Content-Usage` rule). Treat it as an Internet-Draft, not a finished RFC.
- **Really Simple Licensing (RSL)** can be pointed to from `robots.txt` with a `License:` line. That value must be an **absolute URL** to an RSL XML document.

Do not confuse any of these with [robots.txt](https://www.rfc-editor.org/rfc/rfc9309) itself. The Robots Exclusion Protocol communicates crawler access preferences. It does not, by itself, grant or deny copyright permission. A TDM reservation states a rights position but does not block a crawler from fetching a URL. Sites may need both access rules and rights signals; their operational and legal effects differ.

