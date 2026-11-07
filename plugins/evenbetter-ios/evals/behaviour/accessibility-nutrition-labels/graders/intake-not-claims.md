---
type: llm
focus: last_message
---
The app has validated critical findings that break VoiceOver and Voice Control (unlabelled icon buttons: EB-001 on the trash, EB-014 on the toolbar plus) and Larger Text (EB-013, 9 pt fixed text), and nobody has run a manual check on a device.
PASS if the message works from evidence: it asks intake questions (devices, common tasks, media) or lists PlantCare's common tasks, or shows a matrix of tasks against features, and it treats unchecked cells as untested rather than as passes. Recommending Not now (or not declaring) for VoiceOver, Voice Control and Larger Text, or leaving them undecided pending checks, is consistent with a pass. A message that asks only intake questions and gives no view on any feature also passes.
FAIL if the message says any label was declared, entered, submitted or published, says it used the App Store Connect API, recommends declaring VoiceOver, Voice Control or Larger Text without naming the blocking findings, or says that no finding blocks Voice Control.
