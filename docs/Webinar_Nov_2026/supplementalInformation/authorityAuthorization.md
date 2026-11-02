# Details on representing authority and authorization

Authority and authorization are concepts which come up in multiple locations in the talk.   This also 
goes along with the issue of delegation of these to agents acting on the behalf of people or organizations.  
Which can further complicate the situation.   A key aspect of the presentation is to be explicate about both who 
can access and even elements of what and how they can access.  

Also, the issue of identifying these agents, human or machine, can be an issues.  Notes on this 
can be found in [agentIdentification.md](agentIdentification.md).


### Why do this? Let's raise some concerns up front"

This slide introduces the "Rights & access" concern. 

* **On the slide:** Thought: Update the "Rights & access" bullet to read: *Who can view or use your data and under what specific conditions (e.g., handling clinical or controlled access data).*
* 
* **Speaker Notes:** "When we talk about rights and access, we aren't just talking about copyright. For many of you, we are talking about clinical data or embargoed research. We need frameworks that ensure an AI agent acting on a researcher's behalf only touches the data that specific researcher is authorized to see."

### "Be Callable - MCP Authentication"
 
Clinical data could be seen as a driving use case for *why* OAuth 2.1 and scope-based permissions are necessary.

* **Speaker Notes:** "I want to briefly touch on authentication. If a researcher is using an agent to query clinical data or any controlled access repository, that agent must inherit their exact permissions. MCP handles this by utilizing OAuth protocols and token scopes.  The goal is to gaurd against the agent accidentally pulling or expose clinical records it shouldn't have access to."

### Be Meaningful - Rights & Access

This slide revisits access and mentions that it is evolving, specifically linking to the Data Privacy Vocabulary (DPV). DPV is highly relevant to clinical data privacy.

* **Speaker Notes:** "As access models evolve, vocabularies like the Data Privacy Vocabulary are becoming essential. If you are hosting clinical or controlled access data, these vocabularies allow you to explicitly define in the metadata *why* data is restricted and *how* it can be lawfully processed by an automated system."
