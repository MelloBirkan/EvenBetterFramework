# Phase 2: Planning and design

## Table of contents
1. Defining vision and purpose
2. From vision to milestones
3. Starting with requirements
4. Wireframing
5. Storyboarding
6. Apple's Human Interface Guidelines (HIG)
7. Translating design to development

---

## 1. Defining vision and purpose

Every remarkable app starts with: "Why are we building this?" This is the guiding star that keeps the project on track.

### Step 1: Develop a vision
- Identify what problem your app solves or what need it fulfills
- Identify your target audience
- Understand their preferences and pain points

### Step 2: Research and collect information
- Interview and survey users for qualitative data
- Observe how users interact with similar apps
- Perform market research (trends, competitors, gaps)
- Analyze support tickets, forums, and feedback channels
- Analyze competitor apps for features that work well and areas to improve

### Vision vs. development purpose
- **Vision:** The broader picture ("create the best online marketplace for used books")
- **Purpose:** The steps to achieve it ("develop an intuitive book listing feature for the next sprint")

## 2. From vision to milestones

Break down features based on roadmap and vision:
1. List all features you envision
2. Categorize by priority (pivotal vs. enhancement)
3. Revisit them now and then. Milestones can move, but they always serve the primary vision.

Example milestones for a fitness app:
1. Create user-friendly onboarding
2. Develop basic tracking for running, cycling, swimming
3. Integrate social feature for sharing progress

## 3. Starting with requirements

### Identify features
- Determine core features your app needs
- Distinguish must-haves from nice-to-haves

### Target audience
- Who are the users?
- What problems are you solving?

### Architecture decisions
- Data sources and data models
- Local storage vs. cloud
- SwiftData, Core Data, or other persistence

## 4. Wireframing

Wireframes are visual guides representing the skeletal framework of an app. They make abstract ideas tangible and prevent misinterpretations.

### Low-fidelity wireframes (start here)
- Quick to create and modify
- Focus on what needs to be included, not how it looks
- Perfect for initial brainstorming

Example (Login Screen):
```
+--------------------------+
|     App Name/Logo        |
| Email: _________         |
| Password: _________      |
|    [  Login Button  ]    |
| Forgot Password Link     |
+--------------------------+
```

### High-fidelity wireframes (next step)
- Much closer to final design
- Include specific button styles, font choices, icon placement
- Specify UI kit components, animations, transitions
- Show how SwiftUI views should be structured

### Benefits of wireframing
- Clarify app requirements and functionality
- Ensure alignment between developers and designers
- Assist in workload estimation
- Reduce misunderstandings during development

## 5. Storyboarding

Storyboards depict the user flow between screens:
- Map how users navigate through the app
- Show transitions and interactions
- Identify edge cases and dead ends
- Ensure logical progression through features

## 6. Apple's Human Interface Guidelines (HIG)

Study the HIG before you design and build. App Review checks design under guideline 4, and apps that ignore platform conventions can be rejected. For screen-by-screen HIG and accessibility planning, use the evenbetter-ios-feature skill (one screen) or evenbetter-ios-epic (several screens or a whole app).

### Key areas covered by HIG
- **Layout:** Organizing UI elements for clear, logical navigation
- **Visual Design:** Color, typography, icons, imagery for cohesive aesthetics
- **Usability:** Accessibility for all users, including those with disabilities
- **Interaction Design:** Touch gestures, standard controls (buttons, sliders, switches)
- **Common UI Patterns:** Navigation bars, tab bars, and implementation best practices
- **Sound & Haptics:** Incorporating feedback for immersive experience
- **Brand Integration:** Advice on integrating brand elements

### Key HIG principles for iOS
- Use tab bars for primary navigation (bottom of screen)
- Follow recommended typography and color contrast guidelines
- Use standard controls (sliders, switches, buttons)
- Ensure consistency with the iOS ecosystem

### Benefits of following HIG
- App fits well within the Apple ecosystem
- Meets user expectations for quality and usability
- Fewer design-related surprises in App Review

## 7. Translating design to development

### From wireframes to requirements
1. Each screen in wireframe → list of UI components needed
2. Each interaction → Swift/SwiftUI implementation task
3. Each data field → data model property
4. Each navigation path → NavigationStack/TabView structure

### From requirements to code structures
- Map UI elements to SwiftUI views
- Map data models to SwiftData entities
- Map navigation to NavigationStack and TabView
- Map user interactions to state management (@State, @Binding, @Observable)

### Generating development tasks
1. Break each screen into individual UI tasks
2. Create data model tasks for each entity
3. Create navigation tasks for each flow
4. Create integration tasks for connecting UI to data
5. Prioritize: core features first, enhancements later
