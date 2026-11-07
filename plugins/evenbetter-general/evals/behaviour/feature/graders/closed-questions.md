---
type: llm
focus: last_message
---
PASS if the message asks the user at least one question about adding due dates, every question offers a short list of concrete, mutually exclusive options (numbered, lettered or bulleted), and at least one option is marked as the recommended choice. Also PASS if, instead of asking, the message says it took the recommended option for the open decisions about due dates, lists those choices as assumptions, and ends with what still waits on the user, such as reviewing the plan.
FAIL if any question is open-ended with no options to pick from, if the message contains the implementation code, or if it says source files outside .evenbetter/ were changed or the feature was built.
