# Deployment Concepts

```mermaid
flowchart LR
    c1[Web Client]
    c2[CLI Client]
    
    c1 --> MCP
    c2 --> MCP
    
    MCP[MCP] --> Right
    
    subgraph Right[Skill Bundle ]
        direction TB
        bp_questions[skill]
        bp_build[build]
        bp_validate[validate]
        bp_document[blueprint]
    end
```

* bp_question: The basic question skill. Not a schema builder, but a narrative exchange with the user.
* bp_build: Build a valid JSON-LD for a given resource or example narrative prompt.
* bp_validator: Simple SHACL validation for the schema builder skill.
* bp_document: UNKNOWN REQUIREMENT A reference skill for someone looking for references in the Blueprint to cite. Potentially leveraging the OKF bundle?

--- 

# Workflow Thoughts

This is some previous work that is slightly relatd to this section and added for just simple context.

A simple pipeline from URL to metadata record, with schema-guided LLM extraction, SHACL validation, and human vetting.

Makes for a good skill or, perhaps less so, multi-agent test.

## Vertical flow

```mermaid
flowchart TD
    URL[URL<br/>dataset / resource page]

    subgraph inputs["Context for LLM"]
        SCHEMA[Metadata Schema<br/>target format & fields]
    end

    LLM[LLM<br/>extract & structure metadata]
    RECORD[Metadata Record<br/>e.g. JSON-LD]
    SHACL[SHACL Validation Skill<br/>check shape & constraints]

    HITL[Human in the Loop<br/>review & approve]
    PRESENT[Present Metadata Record]

    URL --> LLM
    SCHEMA --> LLM
    LLM --> RECORD
    RECORD --> SHACL

    SHACL -->|fail| LLM
    SHACL -->|pass| HITL
    HITL --> PRESENT
```

**Flow in short:**

1. **URL** — source page or landing URL to extract from
2. **Metadata Schema** — feeds the LLM so the record matches the expected structure (Blueprint / schema.org fields)
3. **LLM** — produces a draft **Metadata Record**
4. **SHACL skill** — validates the record against shapes and constraints
5. **On fail** — loop back to the LLM (often with validation errors as feedback)
6. **On pass** — **human in the loop** vets the record before it's presented

## Horizontal flow (with explicit retry feedback)

```mermaid
flowchart LR
    URL[URL] --> LLM
    SCHEMA[Metadata Schema] -.->|format spec| LLM
    LLM --> RECORD[Metadata Record]
    RECORD --> SHACL{SHACL Skill}
    SHACL -->|invalid| FIX[Validation errors] --> LLM
    SHACL -->|valid| HITL[Human vetting]
    HITL --> OUT[Published record]
```
