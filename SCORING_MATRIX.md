# Six-criterion adversarial scorecard

The hackathon scores every criterion 1–5. This document treats the rubric as a test suite.

## Honest assessment (post pitch1 review)

| Criterion | Score | Evidence | Risk |
|-----------|-------|----------|------|
| **1. AI MCP connector** | **5/5** | Live Alien trace (11 calls, 5 IDs, synthetic=false), credential redaction, companion MCP, trace binding | Low |
| **2. Usefulness/value** | **4.5/5** | Real problem, but story must emphasize "what remains justified" not "skip recomputation" | Medium |
| **3. Originality** | **5/5** | Dependency→change→impact→obligation→receipt is genuinely novel vs existing tools | Low |
| **4. Responsible data** | **5/5** | Anti-cheat invariants, source-health semantics, human-review state, no false claims | Low |
| **5. Reproducibility** | **4/5** | Build certificate predates later commits. Must regenerate on final HEAD. | Medium |
| **6. Clarity** | **4/5** | README is strong. SUBMISSION_FINAL.md too implementation-heavy. Story needs stronger framing. | Medium |

**Self-assessed total: 27.5/30** (not 30/30)

## What the story must emphasize

### OLD (weak):
> "Pāṭala saves 58% recomputation"

### NEW (strong):
> "In a world of abundant inference, the scarce resource is knowing what remains justified."

### OLD (weak):
> "11 dependencies are proven current"

### NEW (honest):
> "11 dependencies triggered no recheck"

### OLD (wrong):
> "Alien missed Y, Pāṭala fixes it"

### NEW (flattering to sponsor):
> "Alien enables a new world where this problem appears. Pāṭala explores what becomes necessary after that succeeds."

## Shortlist blockers

- [x] Live Alien/OpenAIRE MCP trace captured (11 calls, 5 IDs)
- [ ] SUBMISSION_FINAL.md uses stronger framing
- [ ] Build certificate regenerated on final HEAD
- [ ] Every public URL opens in private browser
- [ ] OpenAIRE attributed where metadata redistributed
- [ ] No credentials in traces/docs/fixtures
- [ ] Contact email confirmed
