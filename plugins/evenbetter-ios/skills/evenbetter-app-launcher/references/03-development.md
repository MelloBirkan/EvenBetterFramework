# Phase 3 — Development & Xcode Setup

## Table of Contents
1. Creating a New Xcode Project
2. Key Configuration Settings
3. Signing and Capabilities
4. Project Structure and Organization
5. Version Control
6. Development Workflow
7. Refactoring and Iteration

---

## 1. Creating a New Xcode Project

1. Open Xcode → "Create a new Xcode project"
2. Choose appropriate template and platform (iOS App with SwiftUI)
3. Name your project and set the bundle identifier
4. Select SwiftData or Core Data for persistence (if needed)

## 2. Key Configuration Settings

### Bundle Identifier
- Use reverse DNS format: `com.yourname.appname`
- Must be unique across the entire App Store
- Example: `com.yourcompany.WeatherWiz`

### Deployment Targets
- **iOS Version:** Choose minimum iOS version your app supports
- **Devices:** Specify iPhone, iPad, or both
- Newer devices = latest features but may exclude older device users

### App Name and Display Name
- Names that appear on the device and in the App Store
- Keep it concise and memorable

### Version and Build Numbers
- **Version Number:** Public release version (e.g., 1.0, 1.1, 2.0)
- **Build Number:** Increments with every build, tracks development stages
- Use semantic versioning: Major.Minor.Patch

### Device Orientations
- Set supported orientations (portrait, landscape, or both)
- Most apps default to portrait only

### Info.plist Configuration
- Contains app metadata like CFBundleName, CFBundleShortVersionString
- **CRITICAL:** Permission descriptions must clearly explain WHY each permission is needed
- Vague descriptions = App Store rejection

Example of GOOD permission description:
```
"This app needs access to your camera to scan food items and calculate calories"
```

Example of BAD permission description (will be rejected):
```
"Camera access needed"
```

## 3. Signing and Capabilities

### Certificates and Profiles
- Link to your Apple Developer Account
- Configure development and distribution signing
- Automatic signing is recommended for most projects

### Capabilities
- Enable features like push notifications, background modes, iCloud
- Each capability must be justified if used

## 4. Project Structure and Organization

### Recommended Folder Structure
```
MyApp/
├── App/
│   └── MyAppApp.swift          # App entry point
├── Models/
│   └── DataModels.swift        # SwiftData/Core Data models
├── Views/
│   ├── ContentView.swift       # Main view
│   ├── Components/             # Reusable UI components
│   └── Screens/                # Full-screen views
├── ViewModels/                 # Business logic (if using MVVM)
├── Services/
│   ├── NetworkService.swift    # API/networking layer
│   └── DataService.swift       # Data persistence layer
├── Utilities/
│   └── Extensions.swift        # Helper extensions
├── Resources/
│   ├── Assets.xcassets         # Images, colors, app icon
│   └── Localizable.strings     # Localization
└── Info.plist
```

### Networking and Data Abstractions
- Separate networking logic from views
- Use protocols for testability
- Create clean data service layers
- Handle errors gracefully

## 5. Version Control

### Git/GitHub Setup
- Initialize Git from project creation
- Create meaningful commit messages
- Use branches for feature development
- Push regularly to remote repository

### Branching Strategy
- `main` branch: production-ready code
- `develop` branch: integration branch
- Feature branches: `feature/feature-name`

## 6. Development Workflow

### Feature Planning and Building
1. Start with core features that define your app's value
2. Build one feature at a time, test it, then move on
3. Use iterative development — ship minimal, improve based on feedback
4. Don't over-build before validating

### Laying Out the App Foundation
1. Set up navigation structure (TabView, NavigationStack)
2. Create placeholder views for each screen
3. Implement data models
4. Connect views to data
5. Add interactions and polish

## 7. Refactoring and Iteration

### When to Refactor
- When code becomes hard to understand or modify
- When adding new features requires touching many files
- When you notice repeated patterns
- Before major feature additions

### Iterative Development Principles
- Ship early, get feedback, improve
- Don't pursue perfection before validation
- Each iteration should have a clear goal
- Track what changed and why
