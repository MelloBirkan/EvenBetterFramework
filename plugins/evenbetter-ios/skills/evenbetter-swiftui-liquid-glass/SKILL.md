---
name: evenbetter-swiftui-liquid-glass
description: >-
  Implements and reviews iOS 26 and later SwiftUI Liquid Glass UI: glassEffect, GlassEffectContainer, morphing, glass
  button styles and toolbar glass. Use when adopting Liquid Glass, replacing custom blurs or bar backgrounds with the
  system material, or reviewing glass placement and fallbacks. For general SwiftUI layout and components, use
  evenbetter-swiftui-ui-patterns.
---

# SwiftUI Liquid Glass

> Paths in this skill and its references are relative to this SKILL.md's folder.

## Overview

This skill builds and reviews SwiftUI features that use Liquid Glass (iOS 26 and later). Prefer standard components and the native APIs (`glassEffect`, `GlassEffectContainer`, the glass button styles) over custom blurs. Liquid Glass is the functional layer for controls and navigation that floats above the content, so the content itself stays flat.

Load `references/liquid-glass.md` for API details, code samples, toolbar rules and the iOS 27 additions.

Apple's Xcode 27 SwiftUI skills, SwiftUI Specialist and What's New in SwiftUI, may also be installed. `xcrun agent skills export` copies them out of Xcode for other agents, and third-party copies name the second swiftui-whats-new-27. Use them for SwiftUI API in general. This skill covers where glass goes and how to review it.

If current system, developer or user instructions conflict with this skill, follow them.

## Workflow decision tree

Choose the path that matches the request. If the request does not say, ask one closed question with numbered options: review existing glass usage (recommended), move a feature to Liquid Glass, or build a new feature with it.

### 1. Review an existing feature

- Check where glass appears and where it should not. Glass belongs on controls and navigation, not on content such as list rows, cards, badges or images.
- Check modifier order, shape usage and container placement.
- Check iOS 26 availability handling and the fallback.
- Look for custom backgrounds on navigation bars, tab bars, split views and toolbars that interfere with the system glass.

### 2. Move a feature to Liquid Glass

- Rebuild with the current SDK first. Standard components pick up the new look without code changes.
- Remove custom bar and toolbar backgrounds and let the system draw them.
- Replace buttons that carry a custom glass effect with `.buttonStyle(.glass)` or `.buttonStyle(.glassProminent)`.
- Wrap groups of custom glass elements in `GlassEffectContainer`.
- Add `.interactive()` only to elements a person can tap or focus.

### 3. Implement a new feature

- Decide which controls float above the content and give glass only to those.
- Apply glass modifiers after layout and appearance modifiers.
- Add morphing with `glassEffectID` only when the view hierarchy changes inside an animation.

## Core rules

- Keep glass out of the content layer. Glass with no content scrolling beneath it has nothing to refract and just looks static (WWDC26 SwiftUI group lab).
- Use the glass button styles for buttons instead of `glassEffect` on a `Button`, and set the shape with `buttonBorderShape(_:)`.
- Toolbar and navigation bar items get glass automatically. Tint an item to make it prominent, separate groups with `ToolbarSpacer(.fixed)`, and take an item such as a profile photo out of the shared glass with `sharedBackgroundVisibility(.hidden)`.
- Do not layer glass on glass, and keep standard spacing between glass elements.
- Use `GlassEffectContainer` when several custom glass shapes sit together. It renders them as one and lets them blend and morph.
- Choose the variant on purpose: `.regular` by default, `.clear` with a dimming layer beneath it so content stays legible, and `.identity` to turn the effect off without changing the view tree.
- Apply `.glassEffect(...)` after layout and visual modifiers.
- Gate glass APIs with `#available(iOS 26, *)` when the deployment target is lower, and give a non-glass fallback. Gate `visibilityPriority(_:)` and other iOS 27 toolbar APIs the same way.
- Test custom glass with Reduce Transparency and Reduce Motion on, because both settings remove or change glass effects.
- Give every icon-only glass button or toolbar item an accessibility label.

## Review checklist

- Placement: glass only on controls and navigation, none on content.
- Availability: `#available(iOS 26, *)` present with fallback UI when the deployment target is lower.
- Buttons: glass button styles with `buttonBorderShape`, not a raw `glassEffect`.
- Toolbars: no custom backgrounds, groups split with `ToolbarSpacer`, whole items hidden with `hidden(_:)`.
- Composition: multiple custom glass views wrapped in `GlassEffectContainer`.
- Modifier order: `glassEffect` after layout and appearance modifiers.
- Interactivity: `interactive()` only where a person can interact.
- Transitions: `glassEffectID` with `@Namespace` for morphing.
- Consistency: shapes, tints and spacing match across the feature.

## Implementation checklist

- List the controls that float above the content and the glass prominence each needs.
- Wrap grouped glass elements in `GlassEffectContainer` and tune its spacing.
- Use `.glassEffect(.regular.tint(...).interactive(), in: .rect(cornerRadius: ...))` for custom controls that need it.
- Use `.buttonStyle(.glass)` or `.buttonStyle(.glassProminent)` for actions, and `.glass(.clear)` where the clear variant fits.
- Use `backgroundExtensionEffect()` on one hero view in a `NavigationSplitView` detail column to extend it under the sidebar or inspector.
- Add morphing transitions with `glassEffectID` when the hierarchy changes.
- Provide fallback materials and visuals for earlier iOS versions.

## Quick snippets

Use these patterns directly and tailor shapes, tints and spacing.

```swift
if #available(iOS 26, *) {
    Button("Add", systemImage: "plus") { addItem() }
        .labelStyle(.iconOnly)
        .buttonStyle(.glass)
        .buttonBorderShape(.circle)
} else {
    Button("Add", systemImage: "plus") { addItem() }
        .labelStyle(.iconOnly)
        .buttonStyle(.bordered)
        .buttonBorderShape(.circle)
}
```

```swift
GlassEffectContainer(spacing: 24) {
    HStack(spacing: 24) {
        Image(systemName: "scribble.variable")
            .frame(width: 72, height: 72)
            .font(.system(size: 32))
            .glassEffect()
        Image(systemName: "eraser.fill")
            .frame(width: 72, height: 72)
            .font(.system(size: 32))
            .glassEffect()
    }
}
```

```swift
Button("Confirm") { }
    .buttonStyle(.glassProminent)
```

```swift
NavigationSplitView {
    Sidebar()
} detail: {
    ZStack {
        BannerView()
            .backgroundExtensionEffect()
    }
}
```

## Resources

- Reference guide: `references/liquid-glass.md`
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass), Apple's overview of where the material applies and what to audit.
- For API details newer than the reference, check Apple's documentation with the session's web tools. Apple pages render with JavaScript, so prefer a scraper that renders pages, or the JSON form at `https://developer.apple.com/tutorials/data/documentation/<path>.json`.
