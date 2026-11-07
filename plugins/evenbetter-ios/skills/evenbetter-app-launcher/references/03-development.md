# Phase 3: Development and Xcode setup

## Table of contents
1. Creating a new Xcode project
2. Key configuration settings
3. Signing and capabilities
4. Project structure and organization
5. Version control
6. Development workflow
7. Refactoring and iteration

---

## 1. Creating a new Xcode project

1. Open Xcode → "Create a new Xcode project"
2. Choose appropriate template and platform (iOS App with SwiftUI)
3. Name your project and set the bundle identifier
4. Select SwiftData or Core Data for persistence (if needed)

## 2. Key configuration settings

### Bundle identifier
- Use reverse DNS format: `com.yourname.appname`
- Must be unique across the entire App Store
- Example: `com.yourcompany.WeatherWiz`

### Deployment targets
- **iOS Version:** Choose the minimum iOS version your app supports. Since 2026-04-28, App Store uploads must be built with Xcode 26 or later on the iOS 26 SDK, and since 2026-09-09 they must target iOS 13 or later ([upcoming requirements](https://developer.apple.com/news/upcoming-requirements/)). Xcode 26 and 27 only support deployment targets from iOS 15 ([Xcode system requirements](https://developer.apple.com/xcode/system-requirements)), so iOS 15 is the practical floor.
- **Devices:** Specify iPhone, iPad, or both
- Newer devices = latest features but may exclude older device users

### App name and display name
- Names that appear on the device and in the App Store
- Keep it concise and memorable

### Version and build numbers
- **Version Number:** Public release version (e.g., 1.0, 1.1, 2.0)
- **Build Number:** Increments with every build, tracks development stages
- Use semantic versioning: Major.Minor.Patch

### Device orientations
- Set supported orientations (portrait, landscape, or both)
- Most apps default to portrait only

### Info.plist configuration
- Contains app metadata like CFBundleName, CFBundleShortVersionString
- Permission purpose strings must say specifically why the app needs each permission
- Vague purpose strings get the app rejected
- If your code or an SDK uses a required-reason API, add a privacy manifest (`PrivacyInfo.xcprivacy`); see `references/05-appstore-prep.md`

A specific purpose string:
```
"This app needs access to your camera to scan food items and calculate calories"
```

A vague one that gets rejected:
```
"Camera access needed"
```

## 3. Signing and capabilities

### Certificates and profiles
- Link to your Apple Developer Account
- Configure development and distribution signing
- Automatic signing is recommended for most projects

### Capabilities
- Enable features like push notifications, background modes, iCloud
- Each capability must be justified if used

## 4. Project structure and organization

### Recommended folder structure
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
│   └── Localizable.xcstrings   # String Catalog (localization)
└── Info.plist
```

### Networking and data abstractions
- Separate networking logic from views
- Use protocols for testability
- Create clean data service layers
- Handle errors gracefully

## 5. Version control

### Git/GitHub setup
- Initialize Git from project creation
- Create meaningful commit messages
- Use branches for feature development
- Push regularly to remote repository

### Branching strategy
- `main` branch: production-ready code
- `develop` branch: integration branch
- Feature branches: `feature/feature-name`

## 6. Development workflow

### Feature planning and building
1. Start with core features that define your app's value
2. Build one feature at a time, test it, then move on
3. Use iterative development: ship something minimal, then improve it based on feedback
4. Don't over-build before validating

### Laying out the app foundation
1. Set up navigation structure (TabView, NavigationStack)
2. Create placeholder views for each screen
3. Implement data models
4. Connect views to data
5. Add interactions and polish

## 7. Refactoring and iteration

### When to refactor
- When code becomes hard to understand or modify
- When adding new features requires touching many files
- When you notice repeated patterns
- Before major feature additions

### Iterative development principles
- Ship early, get feedback, improve
- Don't pursue perfection before validation
- Each iteration should have a clear goal
- Track what changed and why
