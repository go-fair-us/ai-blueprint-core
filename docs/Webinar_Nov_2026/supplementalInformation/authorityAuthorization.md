# Details on representing authority and authorization

Authority and authorization are concepts which come up in multiple locations in the talk.   This also 
goes along with the issue of delegation of these to agents acting on the behalf of people or organizations.  
Which can further complicate the situation.  

Also, the issue of identifying these agents, human or machine, can be an issues.  Notes on this 
can be found in [agentIdentification.md](agentIdentification.md).



### Why do this? Let's raise some concerns up front"

This slide introduces the "Rights & access" concern. This is the most natural place to introduce the concept of clinical data as the primary example of why we need these safeguards.

* **On the slide:** Update the "Rights & access" bullet to read: *Who can view or use your data and under what specific conditions (e.g., handling clinical or controlled access data).*
* **Speaker Notes:** "When we talk about rights and access, we aren't just talking about copyright. For many of you, we are talking about clinical data or embargoed research. We need frameworks that ensure an AI agent acting on a researcher's behalf only touches the data that specific researcher is authorized to see."

### "Be Callable - MCP Authentication"

I noticed you added a draft slide on MCP Authentication and Authorization! This is an excellent addition that solves one of the gaps we discussed earlier. You can use clinical data here as the driving use case for *why* OAuth 2.1 and scope-based permissions are necessary.

* **Speaker Notes:** "I want to briefly touch on authentication. If a researcher is using an agent to query clinical data or any controlled access repository, that agent must inherit their exact permissions. MCP handles this by utilizing OAuth protocols and token scopes, ensuring the agent doesn't accidentally pull or expose clinical records it shouldn't have access to."

### Be Meaningful - Rights & Access

This slide revisits access and mentions that it is evolving, specifically linking to the Data Privacy Vocabulary (DPV). DPV is highly relevant to clinical data privacy.

* **On the slide:** You could add a sub-bullet under Data Privacy Vocabulary: *(Crucial for clinical and controlled access data)*.
* **Speaker Notes:** "As access models evolve, vocabularies like the Data Privacy Vocabulary are becoming essential. If you are hosting clinical or controlled access data, these vocabularies allow you to explicitly define in the metadata *why* data is restricted and *how* it can be lawfully processed by an automated system."

**Recommendation:** Option 1 (Slide 6) is the lightest lift and sets the stage early, making the audience feel heard right away. Pairing a brief verbal mention on Slide 6 with your new MCP Auth slide (Slide 22) perfectly closes the loop on how to handle clinical data technically.
