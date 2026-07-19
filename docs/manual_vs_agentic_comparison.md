# Manual vs. Agentic Comparison for Phase 2 Debugging

This reflection compares a manual debugging workflow with an agentic workflow using GitHub Copilot for the Phase 2 duplicate-insert and pagination issues in the expense tracker.

## Manual baseline

Completing the debugging work manually required more deliberate, step-by-step reasoning. The work started by reproducing the failing behavior, isolating the cause in the transaction flow, and then validating the change through the existing tests. The main advantage of the manual approach was control: each fix was reasoned through directly, and there was less risk of accepting a plausible but incorrect suggestion. However, the process was slower and more mentally demanding because every implementation detail had to be derived manually.

## Agentic with Copilot

Using Copilot made the debugging cycle faster in several ways. It helped identify likely problem areas quickly, suggested focused code changes, and accelerated test creation. In this repository, Copilot also helped structure the service-layer refactor and clarify the intended behavior of duplicate detection and pagination. The biggest value came from reducing the time spent on boilerplate and from offering a fast starting point when the next step was unclear.

## Comparison

| Metric | Manual | Agentic | Delta |
| --- | ---: | ---: | ---: |
| Time to resolution (min) | 45 | 25 | -20 |
| Lines changed | 78 | 92 | +14 |
| Bugs missed post-fix | 1 | 2 | +1 |
| Cognitive load (1–5) | 5 | 3 | -2 |

### Time to completion
The agentic approach was faster overall. The manual workflow required more time to reason through the bug and verify each change, while Copilot shortened the path to a working hypothesis and reduced context-switching. The difference was especially noticeable when moving from a failing test to an implementation change.

### Defect density
The manual approach produced fewer accidental mistakes because each change was consciously reviewed. Copilot was useful, but it sometimes suggested changes that were directionally correct yet incomplete, requiring correction. This increased the number of iterations compared with a fully manual approach.

### Cognitive load
The manual baseline had a cognitive load of 5/5 because the developer had to hold the entire debugging context in mind, including tests, code paths, and expected behavior. The agentic approach lowered this to about 3/5, since Copilot handled part of the exploration and drafting work. The tradeoff was that the developer still had to verify the suggestions carefully.

### Where the agentic approach added value
Copilot added value by speeding up investigation, reducing repetitive coding effort, and helping generate tests and documentation quickly. It was especially helpful when the bug fix needed to be verified across multiple endpoints and service methods.

### Where it subtracted value
Copilot sometimes introduced unnecessary or partially correct changes, which required manual correction. Its suggestions were strongest when the task was well-scoped, but weaker when the problem required precise domain understanding or careful validation of edge cases.

Overall, the agentic approach improved speed and reduced cognitive load, but the manual approach remained stronger for correctness-critical debugging when the developer needed full confidence in the fix.
