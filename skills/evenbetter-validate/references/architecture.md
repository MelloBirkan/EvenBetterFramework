# Architecture

This skill documents the validator part of EvenBetter's compliance-auditing architecture. It combines Anthropic's orchestrator-workers and evaluator-style checking patterns from [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) into a practical orchestrator-worker-with-validators flow.

```mermaid
flowchart LR
  A["evenbetter-ios-analyze orchestrator"] --> B["Typography worker"]
  A --> C["Color worker"]
  A --> D["Components worker"]
  A --> E["Layout worker"]
  A --> F["Navigation worker"]
  A --> G["Accessibility worker"]
  B --> H[".evenbetter/analyze.json"]
  C --> H
  D --> H
  E --> H
  F --> H
  G --> H
  H --> I["evenbetter-validate"]
  I --> J["Source excerpt"]
  I --> K["Corpus clause"]
  I --> L["Verified source URL"]
  J --> M["Kept, downgraded, dropped"]
  K --> M
  L --> M
  M --> N[".evenbetter/evenbetter-validate.json"]
```

The analyzer workers make first-pass domain judgments. The validator does not assume those judgments are correct; it reloads code, reloads the rule clause, verifies the source URL, and writes a separate validation report with retention statistics.

This separation makes the hallucination-control claim citable: the first pass produces candidate violations, while the second pass filters high-severity findings through independently checked evidence.
