# Text and Data Mining Observations


## TDM

Under Article 4 of the EU Directive on Copyright in the Digital Single Market (DSM Directive), commercial text and data mining (TDM) is permitted by default unless a rightsholder explicitly reserves their rights in a "machine-readable manner". To meet this legal requirement, specific metadata standards and protocols have been developed to signal these opt-outs to AI crawlers and automated systems.

The primary technical standard for this is the **TDM Reservation Protocol (TDMRep)**, developed by a W3C community group. The protocol utilizes two core properties to express rights:

* tdm-reservation: A boolean value where 1 indicates that rights are reserved (TDM is not permitted without explicit permission) and 0 indicates no reservation is made.   
* tdm-policy: An optional URL that points to a policy file outlining the specific terms, conditions, or licensing agreements under which mining may be conducted.  


To ensure crawlers discover these TDM rights, the TDMRep specification defines a hierarchy of implementation layers, from broad to specific:

* **Site-wide Declarations (.well-known/tdmrep.json)**:A single JSON file hosted at a well-known URL on your domain that dictates TDM rights for the entire site or specific URL patterns.
* **HTTP Response Headers**: You can set tdm-reservation and tdm-policy directly in the HTTP headers of individual responses, which overrides the site-wide .well-known file for that specific resource.
* **HTML Meta Tags**: For standard web pages, adding TDM tags in the HTML document \<head\> provides a page-level declaration that overrides both the .well-known file and HTTP headers.   
* **File-Level Embedded Metadata**: For downloadable assets, TDM declarations can be embedded directly into the file's metadata (such as XMP metadata in PDFs or package metadata in EPUBs). This is the most specific declaration level and ensures the TDM opt-out persists even if the file is downloaded, emailed, or uploaded to a third-party repository.  


## TDM-AI

[https\://docs.tdmai.org/](https://docs.tdmai.org/) 

Another related framework is the **TDM·AI specification**, which defines a technical vocabulary for public, machine-readable AI preferences. It serves as a standardized layer for opt-out declarations to set a default position of "no permission granted," allowing rightsholders to assert their rights under EU law while negotiating separate, explicit licensing deals off-protocol.

It is crucial to distinguish these machine-readable reservations from a standard robots.txt file. While robots.txt dictates whether a bot is allowed to *access* a URL for general purposes like search engine indexing, TDM metadata specifically dictates whether lawfully accessed content may be *extracted and mined for AI training*. Ignorance of properly declared TDM reservations carries legal weight under the EU DSM Directive and the EU AI Act, meaning AI companies that bypass these tags are knowingly acting against expressed wishes.

See Also:  [https\://www\.w3.org/community/reports/tdmrep/CG-FINAL-tdmrep-20240510/](https://www.w3.org/community/reports/tdmrep/CG-FINAL-tdmrep-20240510/)  

