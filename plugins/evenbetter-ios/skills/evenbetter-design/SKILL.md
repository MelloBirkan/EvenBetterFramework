---
name: evenbetter-design
description: Create distinctive, production-grade SwiftUI iOS interfaces with high design quality. Use this skill when the user asks to build a SwiftUI view, screen, feature, or app, or wants to escape default-iOS aesthetics. Generates creative, polished Swift code that avoids generic AI and out-of-the-box iOS aesthetics.
---

This skill guides creation of distinctive, production-grade SwiftUI iOS interfaces that avoid generic "AI slop" and default-iOS aesthetics. Implement real working SwiftUI code with exceptional attention to aesthetic details and creative choices native to the platform.

The user provides iOS requirements: a SwiftUI view, screen, feature, or full app to build. They may include context about the purpose, audience, deployment target, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (deployment target, Dynamic Type, accessibility, light/dark/high-contrast, performance).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working SwiftUI code (views, modifiers, custom shapes, Metal shaders, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## SwiftUI Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid defaulting to SF Pro for every text style; opt instead for distinctive choices that elevate the screen via `Font.custom(_:size:relativeTo:)` so custom faces still scale with Dynamic Type. Pair a distinctive display face with a refined body face. Use weight, `tracking`, `kerning`, and `lineSpacing` deliberately. Reach for `@ScaledMetric` to keep custom sizing accessible.
- **Color & Theme**: Commit to a cohesive aesthetic. Define palettes in the asset catalog with explicit light, dark, and high-contrast variants, and reference them as semantic `Color`s. Dominant colors with sharp accents outperform timid, evenly-distributed palettes. Custom `ShapeStyle`, gradient stops, and `MeshGradient` (iOS 18+) beat the system-blue-on-white default.
- **Motion**: Use animations for effects and micro-interactions, but choreograph them. Prefer SwiftUI-native springs (`withAnimation(.bouncy)`, `.smooth`, `.snappy`, `.spring`). Reach for `PhaseAnimator` and `keyframeAnimator(initialValue:trigger:keyframes:)` for staged sequences, `matchedGeometryEffect` for hero transitions, `.scrollTransition` for scroll-driven reveals, `.symbolEffect(.bounce/.pulse/.variableColor)` for SF Symbols, and `.contentTransition(.numericText())` for counters. One well-orchestrated screen entrance with staggered reveals creates more delight than scattered micro-interactions.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Break out of stock `Form` and `List` defaults when the aesthetic calls for it. Use `ZStack` with alignment guides, `containerRelativeFrame`, `GeometryReader`, and `visualEffect { content, geo in ... }` to drive grid-breaking placement. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid system backgrounds. Layer `Material` stacks (`.ultraThinMaterial`, `.thinMaterial`, `.regularMaterial`, `.thickMaterial`) with tints. Apply Metal shaders via `.colorEffect`, `.distortionEffect`, and `.layerEffect`. Drive procedural backgrounds with `Canvas` + `TimelineView`. Use custom `Shape`/`Path`, gradient meshes, grain/noise overlays, dramatic shadows, and decorative borders. On iOS 26+, reach for `.glassEffect` and `GlassEffectContainer` when Liquid Glass aligns with the aesthetic.

NEVER use generic AI-generated or default-iOS aesthetics like SF Pro for every text style, system-blue accent on a plain white background, vanilla `Form` and `List` screens with no character, the reflexive `RoundedRectangle(cornerRadius: 12)` everywhere, a lone `.ultraThinMaterial` sheet with no other treatment, `.fill(.blue.gradient)` cards, and identical neutral palettes that lack context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (a deep navy + cream pairing, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate SwiftUI with custom shaders, layered materials, and choreographed phase animations. Minimalist or refined designs need restraint, precision, and careful attention to type pairings, spacing, and subtle motion. Elegance comes from executing the vision well.

Remember: SwiftUI is capable of extraordinary creative work - Metal shaders, mesh gradients, Liquid Glass, symbol effects, custom shapes, procedural canvases. Don't hold back; show what can truly be built on iOS when thinking outside the default aesthetic and committing fully to a distinctive vision.
