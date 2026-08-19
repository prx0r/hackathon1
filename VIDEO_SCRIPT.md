# Video walkthrough script (target: ~2 minutes)

## 0:00–0:10 — Hook

"An AI agent used OpenAIRE to conclude that Dataset D supports Claim C. That conclusion is stored in memory. But OpenAIRE changed. Does Claim C still hold?"

## 0:10–0:25 — The problem

OpenAIRE and Alien Intelligence have made scholarly intelligence directly accessible to autonomous agents. That creates a new problem: **what happens to agent conclusions when the evidence changes?**

Alien can give the agent the new state. But the old conclusion already exists.

## 0:25–0:40 — MCP trace

Show the Alien/OpenAIRE MCP interface. Agent makes real queries.

"Pāṭala records the exact tool calls, OpenAIRE identifiers, and evidence as a credential-redacted, hashed trace."

Show the 11-tool-call live trace.

## 0:40–1:00 — Dependencies

"Pāṭala compiles observations into explicit dependencies: Claim C depends on relation D, which depends on evidence E."

Show the dependency graph.

## 1:00–1:20 — Change detection

"OpenAIRE changes. Relation D disappears."

Show the semantic diff.

## 1:20–1:40 — Impact

"Pāṭala identifies: Claim C is affected. Claim A and Claim B are unaffected."

Show:
```
CLAIM C    ← REVERIFY_REQUIRED
  Reason: relation D changed
  Action: verify dataset-support dependency

CLAIM A    ← CURRENT (unaffected)
CLAIM B    ← CURRENT (unaffected)
```

## 1:40–1:55 — Proof obligation

"A frozen proof obligation prevents the agent from silently declaring C current. The obligation specifies exactly what check would restore confidence."

Show the ProofObligation with frozen ResolutionPlan.

## 1:55–2:00 — The hook

**Verbal, over final visual:**

> "Alien makes research intelligence available to agents. Pāṭala makes what they learn maintainable. When inference becomes abundant, knowing what remains justified becomes the scarce resource."
