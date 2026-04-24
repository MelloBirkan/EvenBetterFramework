---
description: "Color and theming analysis rules for SwiftUI projects following Apple Human Interface Guidelines"
---

# Color & Theming Rules — SwiftUI (Apple HIG)

## CLR-UI-001: Use Semantic System Colors

- **What to check:** Views should use semantic colors (`.primary`, `.secondary`, `.accentColor`, `Color(.systemBackground)`, `Color(.label)`) rather than hardcoded RGB or hex values.
- **Why it matters:** Semantic colors automatically adapt to Light/Dark Mode, High Contrast, and other appearance settings. Hardcoded colors break in alternate appearances.
- **Correct code example:**
  ```swift
  Text("Hello")
      .foregroundColor(.primary)
  ```

## CLR-UI-002: Avoid `Color.black` and `Color.white`

- **What to check:** Direct use of `Color.black` or `Color.white` for backgrounds or text. These should be replaced with semantic alternatives.
- **Why it matters:** `Color.black` and `Color.white` do not adapt to Dark Mode. In Dark Mode, white text on a white background (or black on black) becomes invisible.
- **Correct code example:**
  ```swift
  VStack {
      Text("Readable in all modes")
          .foregroundColor(.primary)
  }
  .background(Color(.systemBackground))
  ```

## CLR-UI-003: Asset Catalog Dark Mode Variants

- **What to check:** Custom colors defined in Asset Catalogs should have both "Any Appearance" and "Dark" variants configured.
- **Why it matters:** Without Dark Mode variants, custom colors will look the same in both modes, potentially causing contrast or readability issues in Dark Mode.
- **Correct code example:**
  ```swift
  // In Asset Catalog: "BrandBlue" with Any + Dark variants
  Text("Branded")
      .foregroundColor(Color("BrandBlue"))
  ```

## CLR-UX-001: Color Must Not Be the Only Indicator

- **What to check:** UI elements that convey meaning through color (e.g., error states, success indicators) must also use icons, text labels, or shape to communicate the same information.
- **Why it matters:** Users with color vision deficiencies cannot distinguish meaning from color alone. HIG requires redundant visual cues.
- **Correct code example:**
  ```swift
  HStack {
      Image(systemName: "exclamationmark.triangle.fill")
          .foregroundColor(.red)
      Text("Error: Invalid input")
          .foregroundColor(.red)
  }
  ```

## CLR-A11Y-001: WCAG AA Contrast Ratio

- **What to check:** Text and interactive elements must meet WCAG AA minimum contrast ratios — 4.5:1 for normal text and 3:1 for large text (18pt+ or 14pt+ bold) against their background.
- **Why it matters:** Insufficient contrast makes text difficult or impossible to read for users with low vision. This is both a HIG and WCAG requirement.
- **Correct code example:**
  ```swift
  // Use semantic colors which are designed to meet contrast requirements
  Text("Accessible text")
      .foregroundColor(.primary)
      .background(Color(.systemBackground))
  ```

## CLR-A11Y-002: Red/Green Distinction

- **What to check:** Ensure that red and green are not used as the sole distinguishing colors between two states (e.g., success vs. error, on vs. off).
- **Why it matters:** Red-green color blindness (deuteranopia/protanopia) is the most common form of color vision deficiency. Using only red/green to distinguish states excludes these users.
- **Correct code example:**
  ```swift
  // Use icons in addition to color
  Label("Success", systemImage: "checkmark.circle.fill")
      .foregroundColor(.green)
  Label("Error", systemImage: "xmark.circle.fill")
      .foregroundColor(.red)
  ```
