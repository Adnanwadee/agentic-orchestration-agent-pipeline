# Agent Decision Flow

This document is the Milestone 1 Agent decision-flow deliverable for Part A.

`hr_onboarding_agent` is the top-level ReAct Core Agent. It decides which capability should run
next and when. The IT and booking capabilities are bounded Flows that control how
side-effect-sensitive work completes after the Agent selects them.

```mermaid
flowchart TD
    A[User message] --> B[hr_onboarding_agent decides intent]
    B -->|Policy question| C[HR Policy Knowledge Base]
    C --> D{Grounded answer available?}
    D -->|Yes| E[Answer from approved policy]
    D -->|No| F[Abstain from unsupported policy claim]
    E --> G[Continue or exit]
    F --> G

    B -->|IT access request| H[IT Request Flow]
    H --> I[Collect employee name, role, required systems]
    I --> J{Missing fields?}
    J -->|Yes| K[Ask only for missing values]
    K --> I
    J -->|No| L[Review complete IT request]
    L --> M[Explicit Yes/No confirmation]
    M -->|No| N[No persistence]
    M -->|Yes| O[COS JSON IT request]
    N --> P[Return result to Agent]
    O --> P
    P --> Q[Report submitted or cancelled]

    B -->|Orientation booking| R[Orientation Booking Flow]
    R --> S[Show approved slots]
    S --> T[User selects valid slot]
    T --> U[Review selected slot]
    U --> V[Explicit Yes/No confirmation]
    V -->|No| W[No persistence]
    V -->|Yes| X[COS JSON booking]
    W --> Y[Return result to Agent]
    X --> Y
    Y --> Z[Report booked or cancelled]

    B -->|Ambiguous intent| AA[Clarify before side-effect capability]
    B -->|Out of scope| AB[Decline safely]
    B -->|Done| AC[Summarize and exit]
```

Required behavior:

- Policy Q&A uses the native HR Policy Knowledge Base for approved policy content.
- Unsupported policy questions abstain rather than inventing facts.
- IT requests collect employee name, role, and required systems.
- Missing information triggers follow-up.
- IT and booking both require explicit confirmation before persistence.
- No/cancel paths write nothing.
- Confirmed paths create the intended record.
- Completion/exit must not repeat a completed side effect unless the user starts a new request.
