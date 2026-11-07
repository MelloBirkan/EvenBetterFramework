# Third-party notices

EvenBetter is released under the MIT License (see `LICENSE`). Some skills in the `evenbetter-ios` plugin began as copies of skills published by other projects and were then changed for EvenBetter. This file keeps the notices those licenses ask for.

## openai/plugins, `build-ios-apps` plugin (MIT)

- Source: https://github.com/openai/plugins/tree/main/plugins/build-ios-apps
- License: MIT, as declared in the plugin's manifest (author: OpenAI).
- Derived EvenBetter skills: `evenbetter-swiftui-ui-patterns`, `evenbetter-swiftui-view-refactor`, `evenbetter-swiftui-performance-audit`, `evenbetter-swiftui-liquid-glass`, `evenbetter-ios-debugger-agent`, `evenbetter-ios-app-intents`.
- Changes: renamed, given EvenBetter routing and Codex tool notes, corrected for current Apple APIs and tools, and linked to the EvenBetter corpus.

## Dimillian/Skills (MIT)

- Source: https://github.com/Dimillian/Skills
- Earlier versions of the SwiftUI skills above (UI patterns, view refactor, performance audit, Liquid Glass, iOS debugger agent) were published here before `build-ios-apps` carried them forward. The `mv-patterns.md` reference of `evenbetter-swiftui-view-refactor` is also inspired by Thomas Ricouard's article "SwiftUI in 2025: Forget MVVM".

```text
MIT License

Copyright (c) 2026 Thomas Ricouard

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

The `build-ios-apps` plugin ships no license file of its own; the same MIT terms apply to the parts taken from it, with OpenAI as the copyright holder.

## anthropics/skills, `frontend-design` skill (Apache-2.0)

- Source: https://github.com/anthropics/skills/tree/main/skills/frontend-design
- Derived EvenBetter skill: `evenbetter-design`, rewritten for SwiftUI and iOS. The skill folder carries a copy of the Apache License 2.0 in `LICENSE.txt`, and its `SKILL.md` says that it was changed from the original.
