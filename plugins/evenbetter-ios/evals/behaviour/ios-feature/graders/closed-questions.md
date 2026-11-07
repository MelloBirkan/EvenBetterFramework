---
type: llm
focus: last_message
---
PASS if the message asks the user at least one question about the favourites screen, every question offers a short list of concrete, mutually exclusive options (numbered, lettered or bulleted), and at least one option is marked as the recommended choice. Also PASS if, instead of asking, the message says it took the recommended option for the open decisions about the favourites screen, lists those choices as assumptions, and ends with what still waits on the user, such as reviewing the plan.
FAIL if any question is open-ended with no options to pick from, if the message contains Swift code for the new screen, or if it says the screen was built or project files outside .evenbetter/ were changed.
