# Architecture

This skill documents the validator part of EvenBetter's compliance-auditing architecture. It combines an analyzer first pass with an evidence-checking correction pass: the analyzer proposes issues and `ai_fix_prompt` values, then the validator corrects the analyzer report so downstream users and fixers see the current issue set.

```mermaid
flowchart LR
  A["evenbetter-ios-analyze orchestrator"] --> B["Typography worker"]
  A --> C["Color worker"]
  A --> D["Components worker"]
  A --> E["Layout worker"]
  A --> F["Navigation worker"]
  A --> G["Accessibility worker"]
  B --> H[".evenbetter/analyze-{N}.json"]
  C --> H
  D --> H
  E --> H
  F --> H
  G --> H
  H --> O[".evenbetter/manifest.json"]
  O --> I["evenbetter-validate"]
  H --> I
  I --> J["Source excerpt"]
  I --> K["Corpus clause"]
  I --> L["Verified HIG/WCAG URL"]
  I --> R["Optional primary-source web evidence"]
  J --> M["Correct analyzer JSON"]
  K --> M
  L --> M
  R --> M
  M --> H
  M --> O
  H --> P["generate_html_report.py"]
  O --> P
  P --> Q[".evenbetter/evenbetter-validate-{N}.html"]
  H --> S["evenbetter-fix"]
```

The analyzer workers make first-pass domain judgments, create `ai_fix_prompt` values, and store each run as a numbered analyzer report indexed by `manifest.json`. The validator does not assume those judgments are correct; it reloads code, reloads the rule clause, verifies or corrects the source URL, optionally uses native web lookup for uncertain cases, corrects severity and guideline references, and rejects unsupported findings through analyzer state.

The resulting HTML report is generated from the corrected analyzer JSON. It focuses on current issues, not on what the validator checked, kept, dropped, or skipped.
