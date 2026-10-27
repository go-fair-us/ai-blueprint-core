A glossary (also called a cheat sheet or term list). Here are the eight terms from Jim Clyde Monge’s piece, in plain language.

**1. Harness**  
The software wrapped around a model so it can actually do work. It supplies tools, permissions, instructions, and rules for when to retry, stop, or ask you.  
Formula in the piece: **Agent = Model + Harness**. Two products can use the same model and behave differently because their harnesses differ.

**2. Agents**  
Systems that take a goal and work through multiple steps: plan, act, check the result, decide what to do next. They use tools (web, email, files, calendar) within the permissions you give them. What they can finish depends on those tools and on when they must ask for approval.

**3. MCP (Model Context Protocol)**  
A shared standard for connecting AI apps to tools and data — the “USB-C for AI.” An MCP server exposes tools or information (search company docs, create a ticket). The app still has to support MCP, and you still grant permissions. Without a standard, every app needs its own custom integration.

**4. Loop engineering**  
Designing the agent’s repeat cycle: act, check, retry or stop. It answers: what counts as done, how many retries, how much time or money, when to ask for help, and who checks the result. The harness provides the tools; loop engineering decides how the agent uses them over and over without spinning forever or quitting early.

**5. Skills**  
A saved procedure an agent loads when a task matches — often a `SKILL.md` plus scripts, templates, or reference docs. The agent first sees only the name and description, then loads the full instructions if relevant. MCP gives access to tools and data; a skill says how to do a specific job with them (for example, how to build the monthly sales report).

**6. GEO / AEO**  
About being found by AI answers, not about building agents.  
- **SEO:** rank in the classic list of links.  
- **GEO (Generative Engine Optimization):** get mentioned, cited, or recommended in AI-generated answers.  
- **AEO (Answer Engine Optimization):** make content useful as a direct answer (answer boxes and AI assistants).  
The two overlap, and companies don’t always use them the same way. Neither guarantees an AI will cite you.

**7. Computer Use**  
The model drives a screen the way a person would: screenshot, decide, click or type, look again. Useful when there is no API. It can also misclick, misread a page, or get stuck, so access and review matter for purchases, submissions, and account changes.

**8. AGI / Superintelligence**  
- **AGI (artificial general intelligence):** AI that can handle a broad range of intellectual tasks at roughly human level. Definitions and tests are still disputed.  
- **Superintelligence:** AI that would substantially beat humans across a broad range of intellectual tasks.  
Being excellent at one thing (code, math) is not either of these. The label matters less than what a system has actually demonstrated.

Quick map: harness and loop engineering shape how an agent runs; MCP connects it to tools; skills tell it how to use those tools; computer use is the fallback when there is no API; GEO/AEO is about showing up in answers; AGI and superintelligence are capability claims, not product features.


