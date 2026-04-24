---
description: "Typography analysis rules for SwiftUI projects following Apple Human Interface Guidelines"
---

# Typography Rules — SwiftUI (Apple HIG)

## TYPO-UI-001: Use System Text Styles

- **What to check:** Text views should use built-in text styles (`.font(.title)`, `.font(.body)`, `.font(.caption)`, etc.) rather than hardcoded font sizes.
- **Why it matters:** System text styles automatically adapt to Dynamic Type, ensuring consistent typography across the app and respecting user font size preferences.
- **Correct code example:**
  ```swift
  Text("Hello")
      .font(.title)
  ```

## TYPO-UI-002: Custom Fonts Must Use `relativeTo:`

- **What to check:** When using `Font.custom()`, ensure the `relativeTo:` parameter is provided to map the custom font to a system text style.
- **Why it matters:** Without `relativeTo:`, custom fonts will not scale with Dynamic Type, breaking accessibility for users who adjust their text size.
- **Correct code example:**
  ```swift
  Text("Hello")
      .font(.custom("Avenir", size: 17, relativeTo: .body))
  ```

## TYPO-UI-003: Maintain Weight Hierarchy

- **What to check:** Headings should use heavier font weights than body text. Verify that `.fontWeight()` modifiers maintain a clear visual hierarchy (e.g., titles are `.bold` or `.semibold`, body is `.regular`).
- **Why it matters:** A clear weight hierarchy helps users scan and understand content structure at a glance, following HIG typographic guidance.
- **Correct code example:**
  ```swift
  Text("Section Title")
      .font(.headline)
      .fontWeight(.semibold)
  Text("Body content here")
      .font(.body)
  ```

## TYPO-UX-001: Use `.lineLimit` and `.truncationMode`

- **What to check:** Long text content should specify `.lineLimit()` and `.truncationMode()` to handle overflow gracefully.
- **Why it matters:** Without truncation handling, text can overflow its container, break layouts, or become unreadable on smaller screens.
- **Correct code example:**
  ```swift
  Text("A very long description that might overflow")
      .lineLimit(2)
      .truncationMode(.tail)
  ```

## TYPO-UX-002: Set Appropriate `.lineSpacing`

- **What to check:** Multi-line text should use `.lineSpacing()` to ensure adequate vertical spacing between lines.
- **Why it matters:** Proper line spacing improves readability, especially for longer passages of text. Apple HIG recommends comfortable spacing for legibility.
- **Correct code example:**
  ```swift
  Text("Multi-line paragraph text goes here.")
      .font(.body)
      .lineSpacing(4)
  ```

## TYPO-A11Y-002: Avoid Fixed Frame Heights on Text

- **What to check:** Text views should not have fixed `.frame(height:)` values that prevent text from growing with Dynamic Type.
- **Why it matters:** Fixed heights clip text when users increase their font size, making content inaccessible and violating HIG Dynamic Type guidelines.
- **Correct code example:**
  ```swift
  Text("Scalable text")
      .font(.body)
      .frame(maxWidth: .infinity, alignment: .leading)
  ```

## TYPO-A11Y-001: Minimum Font Size of 11pt

- **What to check:** No text should use a font size smaller than 11 points. Check for `.font(.system(size:))` calls with values below 11.
- **Why it matters:** Apple HIG specifies that text below 11pt is difficult to read for most users, particularly those with visual impairments.
- **Correct code example:**
  ```swift
  Text("Small but readable")
      .font(.caption2) // 11pt, the minimum recommended size
  ```

## TYPO-A11Y-003: Use `.minimumScaleFactor`

- **What to check:** Text that must fit in constrained spaces should use `.minimumScaleFactor()` instead of disabling Dynamic Type or using fixed sizes.
- **Why it matters:** `.minimumScaleFactor` allows text to shrink gracefully in tight layouts while still respecting Dynamic Type as much as possible.
- **Correct code example:**
  ```swift
  Text("Constrained text")
      .font(.body)
      .minimumScaleFactor(0.75)
      .lineLimit(1)
  ```
