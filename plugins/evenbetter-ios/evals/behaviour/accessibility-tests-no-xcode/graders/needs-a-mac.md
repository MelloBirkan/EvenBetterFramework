---
type: llm
focus: last_message
---
The run happens on a Linux machine with no xcodebuild and no iOS simulator.
PASS if the message says the tests cannot run here because they need a Mac with Xcode and a simulator, and it offers or describes the write-only path: writing the XCUITest files (or having written them) and giving the commands or next step to run them on a Mac.
FAIL if the message reports any finding as confirmed, refuted or reproduced in the running app, claims a test run happened, or says it changed app source code (as opposed to test files or files under .evenbetter/) without asking first.
