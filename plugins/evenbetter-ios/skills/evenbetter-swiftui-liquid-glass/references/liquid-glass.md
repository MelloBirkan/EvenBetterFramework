# Implementing Liquid Glass in SwiftUI

Contents:

- Overview
- Where glass belongs
- Basic implementation
- Customizing Liquid Glass effects
- Working with multiple glass effects
- Morphing effects and transitions
- Button styling with Liquid Glass
- Toolbars and navigation bars
- Background extension effect
- Accessibility and fallbacks
- Best practices
- Example: flat badges with a floating glass control
- References

## Overview

Liquid Glass is the dynamic material Apple introduced in iOS 26. It combines the optical properties of glass with a sense of fluidity: it blurs the content behind it, reflects color and light from the content around it, and reacts to touch and pointer input in real time. Apple describes it as a distinct functional layer for controls and navigation that sits above the content. This guide covers how to apply and customize it in SwiftUI.

What Liquid Glass does:
- Blurs content behind the material
- Reflects color and light from surrounding content
- Reacts to touch and pointer interactions
- Morphs between shapes during transitions
- Applies to standard and custom components

Standard components (bars, sheets, popovers, controls) adopt it automatically when the app is built with the iOS 26 SDK or later, so a migration starts with a rebuild, not with new code.

## Where glass belongs

Apple's Adopting Liquid Glass overview and the WWDC26 SwiftUI group lab agree on these placement rules:

- Glass goes on controls and navigation, never on the content layer. List rows, cards, badges, images and text blocks stay flat. With no content scrolling beneath it, a glass surface has nothing to refract and just looks static.
- Use it sparingly. Overusing glass in custom controls distracts from the content it is meant to frame, so limit it to the most important functional elements.
- Do not layer glass on top of glass. Keep standard spacing between glass elements rather than overlapping them.
- Remove custom backgrounds from bars, tab bars, split views and toolbars. They can overlay or interfere with the system glass and the scroll edge effect.
- For a custom bar with content scrolling beneath it, register it with `safeAreaBar(edge:alignment:spacing:content:)` so it gets the scroll edge effect.

## Basic implementation

### Adding Liquid Glass to a view

The simplest way to add Liquid Glass to a view is the `glassEffect()` modifier:

```swift
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect()
```

By default this applies the regular variant of `Glass` within a capsule shape behind the view's content. The full signature is `glassEffect(_ glass: Glass = .regular, in shape: some Shape = DefaultGlassEffectShape())`.

### Customizing the shape

You can specify a different shape for the Liquid Glass effect:

```swift
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(in: .rect(cornerRadius: 16.0))
```

Common shape options:
- `.capsule` (default)
- `.rect(cornerRadius: CGFloat)`
- `.circle`

For shapes that should stay concentric with their container, Apple points to `ConcentricRectangle` and `rect(corners:isUniform:)`.

## Customizing Liquid Glass effects

### Glass variants and properties

You customize the effect by configuring the `Glass` structure:

```swift
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(.regular.tint(.orange).interactive())
```

Variants (all iOS 26):
- `.regular`: the standard glass, and the default.
- `.clear`: a more transparent glass for controls over media. Apple asks for a dimming layer or another treatment beneath the glass so its content stays legible, for example a translucent black layer over the bright media behind it.
- `.identity`: leaves the content as if no glass were applied. Use it to switch the effect off conditionally without changing the view tree.

Modifiers on a variant:
- `.tint(Color)` adds a color tint that suggests prominence.
- `.interactive(Bool)` makes the glass react to touch and pointer interactions.

```swift
Button("Play", systemImage: "play.fill") { player.play() }
    .labelStyle(.iconOnly)
    .padding()
    .glassEffect(isOverVideo ? .clear.interactive() : .regular.interactive(), in: .circle)
```

### Making interactive glass

To make Liquid Glass react to touch and pointer interactions:

```swift
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(.regular.interactive(true))
```

Or more concisely:

```swift
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(.regular.interactive())
```

Add `.interactive()` only to elements a person can tap or focus.

## Working with multiple glass effects

### Using GlassEffectContainer

When several views carry Liquid Glass, wrap them in a `GlassEffectContainer`. The container renders them together, which performs better, and lets the shapes blend and morph:

```swift
GlassEffectContainer(spacing: 40.0) {
    HStack(spacing: 40.0) {
        Image(systemName: "scribble.variable")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()

        Image(systemName: "eraser.fill")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()
    }
}
```

The `spacing` parameter controls how the Liquid Glass effects interact with each other:
- Smaller spacing: views need to be closer to merge effects
- Larger spacing: effects merge at greater distances

### Uniting multiple glass effects

To combine multiple views into a single Liquid Glass effect, use the `glassEffectUnion(id:namespace:)` modifier:

```swift
@Namespace private var namespace

// Later in your view:
GlassEffectContainer(spacing: 20.0) {
    HStack(spacing: 20.0) {
        ForEach(symbolSet.indices, id: \.self) { item in
            Image(systemName: symbolSet[item])
                .frame(width: 80.0, height: 80.0)
                .font(.system(size: 36))
                .glassEffect()
                .glassEffectUnion(id: item < 2 ? "1" : "2", namespace: namespace)
        }
    }
}
```

This is useful when views are created dynamically or live outside one `HStack` or `VStack`.

## Morphing effects and transitions

### Creating morphing transitions

To morph glass shapes as views appear and disappear:

1. Create a namespace with the `@Namespace` property wrapper.
2. Give each Liquid Glass effect a unique identifier with `glassEffectID(_:in:)`.
3. Change the view hierarchy inside an animation.

```swift
@State private var isExpanded: Bool = false
@Namespace private var namespace

var body: some View {
    GlassEffectContainer(spacing: 40.0) {
        HStack(spacing: 40.0) {
            Image(systemName: "scribble.variable")
                .frame(width: 80.0, height: 80.0)
                .font(.system(size: 36))
                .glassEffect()
                .glassEffectID("pencil", in: namespace)

            if isExpanded {
                Image(systemName: "eraser.fill")
                    .frame(width: 80.0, height: 80.0)
                    .font(.system(size: 36))
                    .glassEffect()
                    .glassEffectID("eraser", in: namespace)
            }
        }
    }

    Button("Toggle") {
        withAnimation {
            isExpanded.toggle()
        }
    }
    .buttonStyle(.glass)
}
```

The morph happens when views with Liquid Glass appear or disappear because the view hierarchy changed. `GlassEffectTransition` controls how an effect is added or removed.

## Button styling with Liquid Glass

Use the glass button styles instead of a raw `glassEffect` on a `Button`. They apply glass based on the button's context. Set the shape with `buttonBorderShape(_:)` rather than a custom clip.

### Glass button style

```swift
Button("Click Me") {
    // Action
}
.buttonStyle(.glass)
```

### Glass prominent button style

For the primary action on a screen:

```swift
Button("Important Action") {
    // Action
}
.buttonStyle(.glassProminent)
```

### Configurable glass and border shape

`.glass(_:)` takes a `Glass` value, so a button can use the clear variant or a tint:

```swift
Button("Close", systemImage: "xmark") { dismiss() }
    .labelStyle(.iconOnly)
    .buttonStyle(.glass(.clear))
    .buttonBorderShape(.circle)
    .controlSize(.large)
```

## Toolbars and navigation bars

Toolbar and navigation bar items get glass automatically and share one glass background per logical group. Do not add `glassEffect` or custom backgrounds to them.

- To make one item stand out, tint it instead of adding a custom background.
- Group related actions, and separate groups with `ToolbarSpacer(.fixed)`. Do not mix text and icons within one shared background.
- `sharedBackgroundVisibility(.hidden)` (iOS 26) removes an item's glass and puts it in its own group, which suits a profile photo or a status view.
- Hide a whole item with `hidden(_:)` instead of hiding the view inside it, which leaves an empty glass item behind.
- Give every icon-only item an accessibility label.

```swift
ContentView()
    .toolbar {
        ToolbarItem(placement: .topBarLeading) {
            ProfileButton()
        }
        .sharedBackgroundVisibility(.hidden)

        ToolbarItem(placement: .topBarTrailing) {
            Button("Share", systemImage: "square.and.arrow.up") { share() }
        }
        ToolbarSpacer(.fixed, placement: .topBarTrailing)
        ToolbarItem(placement: .topBarTrailing) {
            Button("Archive", systemImage: "archivebox") { archive() }
        }
    }
```

### iOS 27: visibility priority

When a toolbar runs out of space, it moves items into an overflow menu. `visibilityPriority(_:)` on a toolbar item (iOS 27) decides the order: items with a lower priority move first. The values are `.low`, `.automatic` (the default) and `.high`. Gate it on the deployment target like any iOS 27 API.

```swift
.toolbar {
    ToolbarItem {
        ArchiveButton()
    }
    ToolbarItem {
        ShareButton()
    }
    .visibilityPriority(.high)
}
```

## Background extension effect

`backgroundExtensionEffect()` (iOS 26) mirrors a view into copies around any edge with available safe area and blurs them. In a `NavigationSplitView` this makes a hero image look as if it extends under the sidebar or inspector, without placing content under them. Apply it to a single background view; Apple warns about clarity and performance with more. The modifier clips the view so the copies do not overlap.

```swift
NavigationSplitView {
    // Sidebar content
} detail: {
    ZStack {
        BannerView()
            .backgroundExtensionEffect()
    }
}
.inspector(isPresented: $showInspector) {
    // Inspector content
}
```

To check whether content peeks through correctly next to a sidebar or inspector, audit the safe areas of the detail column.

## Accessibility and fallbacks

- People can turn on Reduce Transparency or Reduce Motion, and choose a preferred glass look in Settings. These remove or change glass effects. Standard components adapt on their own; test custom glass, colors and animations with each setting on.
- Keep tinted glass legible. Use system colors, or custom colors with light, dark and increased-contrast variants.
- Gate glass APIs with `#available(iOS 26, *)` when the deployment target is lower, and give a non-glass fallback such as `.bordered` buttons or a material background.

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

## Best practices

1. Put glass on controls and navigation only, and keep the content layer flat.
2. Wrap groups of custom glass views in a `GlassEffectContainer` for performance and morphing.
3. Apply `.glassEffect()` after the modifiers that set the view's layout and appearance.
4. Pick container spacing on purpose, since it decides when nearby effects merge.
5. Change the view hierarchy inside an animation so glass morphs smoothly.
6. Add `.interactive()` only to glass that responds to input.
7. Keep shapes and tints consistent across related controls.

## Example: flat badges with a floating glass control

Badges are content, so they stay flat. The filter button floats above the scrolling grid in the control layer, where the glass has content to refract.

```swift
struct BadgeView: View {
    let symbol: String
    let color: Color
    let name: String

    var body: some View {
        ZStack {
            Image(systemName: "hexagon.fill")
                .foregroundStyle(color)
                .font(.system(size: 50))

            Image(systemName: symbol)
                .foregroundStyle(.white)
                .font(.system(size: 30))
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(name)
    }
}

// Usage:
ScrollView {
    LazyVGrid(columns: [GridItem(.adaptive(minimum: 72))], spacing: 20) {
        ForEach(badges) { badge in
            BadgeView(symbol: badge.symbol, color: badge.color, name: badge.name)
        }
    }
    .padding()
}
.overlay(alignment: .bottomTrailing) {
    Button("Filter", systemImage: "line.3.horizontal.decrease") { showFilters = true }
        .labelStyle(.iconOnly)
        .buttonStyle(.glass)
        .buttonBorderShape(.circle)
        .controlSize(.large)
        .padding()
}
```

## References

- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/SwiftUI/Applying-Liquid-Glass-to-custom-views)
- [Landmarks: Building an app with Liquid Glass](https://developer.apple.com/documentation/SwiftUI/Landmarks-Building-an-app-with-Liquid-Glass)
- [SwiftUI View.glassEffect(_:in:)](https://developer.apple.com/documentation/SwiftUI/View/glassEffect(_:in:))
- [SwiftUI GlassEffectContainer](https://developer.apple.com/documentation/SwiftUI/GlassEffectContainer)
- [SwiftUI GlassEffectTransition](https://developer.apple.com/documentation/SwiftUI/GlassEffectTransition)
- [SwiftUI GlassButtonStyle](https://developer.apple.com/documentation/SwiftUI/GlassButtonStyle)
- [SwiftUI View.backgroundExtensionEffect()](https://developer.apple.com/documentation/SwiftUI/View/backgroundExtensionEffect())
- [SwiftUI ToolbarContent.sharedBackgroundVisibility(_:)](https://developer.apple.com/documentation/SwiftUI/ToolbarContent/sharedBackgroundVisibility(_:))
- [SwiftUI ToolbarContent.visibilityPriority(_:)](https://developer.apple.com/documentation/SwiftUI/ToolbarContent/visibilityPriority(_:))
- [SwiftUI ToolbarSpacer](https://developer.apple.com/documentation/SwiftUI/ToolbarSpacer)
- [WWDC26 SwiftUI group lab](https://developer.apple.com/videos/play/wwdc2026/8120/)
