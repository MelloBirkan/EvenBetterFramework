# Code templates

These templates are generic on purpose. Rename types and services to fit the app.

Contents:

- Choosing the run mode by deployment target
- Open-app handoff intent
- Inline action intent
- Fixed selection with `AppEnum`
- Entity and query
- Dependent query
- Widget configuration intent
- App shortcuts provider
- Inline file input

## Choosing the run mode by deployment target

`openAppWhenRun` is deprecated from iOS 26 in favor of `supportedModes`, but `supportedModes` and `IntentModes` exist only on iOS 26 and later. Pick one per intent based on the app's deployment target:

| Deployment target | Opens the app | Runs without opening the app |
| --- | --- | --- |
| iOS 26 or later | `static let supportedModes: IntentModes = .foreground` | `static let supportedModes: IntentModes = .background` |
| Below iOS 26 | `static let openAppWhenRun = true` | Leave `openAppWhenRun` out (it defaults to `false`) |

When the target moves to iOS 26, replace `openAppWhenRun` with `supportedModes`. Mixed modes are iOS 26 only: `[.background, .foreground(.deferred)]` starts in the background and brings the app forward before the action finishes, and `[.background, .foreground(.dynamic)]` prefers the background but can move to the foreground. Inside `perform()`, `systemContext.currentMode` says where the intent is running.

Keep an intent that opens the app in the app target. Apple documents that `openAppWhenRun = true` raises an error when the intent runs in an app extension.

The templates below show the iOS 26 form, with the lower-target line in a comment.

## Open-app handoff intent

```swift
import AppIntents

struct OpenComposerIntent: AppIntent {
  static let title: LocalizedStringResource = "Open composer"
  static let description = IntentDescription("Open the app to compose content")
  static let supportedModes: IntentModes = .foreground
  // Deployment target below iOS 26: use this line instead of supportedModes.
  // static let openAppWhenRun = true

  @Parameter(
    title: "Prefilled text",
    inputConnectionBehavior: .connectToPreviousIntentResult
  )
  var text: String?

  @MainActor
  func perform() async throws -> some IntentResult {
    AppIntentRouter.shared.handledIntent = .init(intent: self)
    return .result()
  }
}
```

Scene-side handoff:

```swift
import AppIntents
import Observation

@MainActor
@Observable
final class AppIntentRouter {
  struct HandledIntent: Equatable {
    let id = UUID()
    let intent: any AppIntent

    static func == (lhs: Self, rhs: Self) -> Bool {
      lhs.id == rhs.id
    }
  }

  static let shared = AppIntentRouter()
  var handledIntent: HandledIntent?

  private init() {}
}

private func handleIntent() {
  guard let intent = appIntentRouter.handledIntent?.intent else { return }

  if let composerIntent = intent as? OpenComposerIntent {
    appRouter.presentComposer(prefilledText: composerIntent.text ?? "")
  } else if let sectionIntent = intent as? OpenSectionIntent {
    selectedTab = sectionIntent.section.toTab
  }
}
```

## Inline action intent

```swift
import AppIntents

struct CreateItemIntent: AppIntent {
  static let title: LocalizedStringResource = "Create item"
  static let description = IntentDescription("Create a new item without opening the app")
  static let supportedModes: IntentModes = .background
  // Deployment target below iOS 26: delete the supportedModes line; the intent runs without opening the app.

  @Parameter(title: "Title")
  var title: String

  @Parameter(title: "Workspace")
  var workspace: WorkspaceEntity

  func perform() async throws -> some IntentResult & ProvidesDialog {
    do {
      try await ItemService.shared.createItem(title: title, workspaceID: workspace.id)
      return .result(dialog: "Created \(title).")
    } catch {
      return .result(dialog: "Could not create the item. Please try again.")
    }
  }
}
```

## Fixed selection with `AppEnum`

```swift
import AppIntents

enum SectionIntentValue: String, AppEnum {
  case inbox
  case projects
  case settings

  static let typeDisplayRepresentation: TypeDisplayRepresentation = "Section"

  static var caseDisplayRepresentations: [Self: DisplayRepresentation] {
    [
      .inbox: "Inbox",
      .projects: "Projects",
      .settings: "Settings",
    ]
  }

  var toTab: AppTab {
    switch self {
    case .inbox: .inbox
    case .projects: .projects
    case .settings: .settings
    }
  }
}

struct OpenSectionIntent: AppIntent {
  static let title: LocalizedStringResource = "Open section"
  static let supportedModes: IntentModes = .foreground
  // Deployment target below iOS 26: static let openAppWhenRun = true

  @Parameter(title: "Section")
  var section: SectionIntentValue

  @MainActor
  func perform() async throws -> some IntentResult {
    AppIntentRouter.shared.handledIntent = .init(intent: self)
    return .result()
  }
}
```

## Entity and query

```swift
import AppIntents

struct WorkspaceEntity: AppEntity, Identifiable {
  let workspace: Workspace

  var id: String { workspace.id }

  static let typeDisplayRepresentation: TypeDisplayRepresentation = "Workspace"
  static let defaultQuery = WorkspaceQuery()

  var displayRepresentation: DisplayRepresentation {
    DisplayRepresentation(title: "\(workspace.name)")
  }
}

struct WorkspaceQuery: EntityQuery {
  func entities(for identifiers: [WorkspaceEntity.ID]) async throws -> [WorkspaceEntity] {
    let workspaces = try await WorkspaceStore.shared.workspaces(matching: identifiers)
    return workspaces.map(WorkspaceEntity.init)
  }

  func suggestedEntities() async throws -> [WorkspaceEntity] {
    try await WorkspaceStore.shared.recentWorkspaces().map(WorkspaceEntity.init)
  }

  func defaultResult() async -> WorkspaceEntity? {
    guard let workspace = try? await WorkspaceStore.shared.currentWorkspace() else { return nil }
    return WorkspaceEntity(workspace: workspace)
  }
}
```

## Dependent query

```swift
import AppIntents

struct ProjectEntity: AppEntity, Identifiable {
  let project: Project

  var id: String { project.id }

  static let typeDisplayRepresentation: TypeDisplayRepresentation = "Project"
  static let defaultQuery = ProjectQuery()

  var displayRepresentation: DisplayRepresentation {
    DisplayRepresentation(title: "\(project.name)")
  }
}

struct ProjectSelectionIntent: WidgetConfigurationIntent {
  static let title: LocalizedStringResource = "Project widget configuration"

  @Parameter(title: "Workspace")
  var workspace: WorkspaceEntity?

  @Parameter(title: "Project")
  var project: ProjectEntity?
}

struct ProjectQuery: EntityQuery {
  // The wrapped value is an IntentProjection of the configuring intent, nil until it has a workspace.
  // The projection returns listed parameters unwrapped, so `workspace` reads as a non-optional value.
  @IntentParameterDependency<ProjectSelectionIntent>(\.$workspace)
  var selection

  func entities(for identifiers: [ProjectEntity.ID]) async throws -> [ProjectEntity] {
    try await fetchProjects().filter { identifiers.contains($0.id) }.map(ProjectEntity.init)
  }

  func suggestedEntities() async throws -> [ProjectEntity] {
    try await fetchProjects().map(ProjectEntity.init)
  }

  func defaultResult() async -> ProjectEntity? {
    try? await fetchProjects().first.map(ProjectEntity.init)
  }

  private func fetchProjects() async throws -> [Project] {
    guard let workspaceID = selection?.workspace.id else { return [] }
    return try await ProjectStore.shared.projects(in: workspaceID)
  }
}
```

## Widget configuration intent

```swift
import AppIntents
import WidgetKit

struct ActivityWidgetConfiguration: WidgetConfigurationIntent {
  static let title: LocalizedStringResource = "Activity widget configuration"
  static let description = IntentDescription("Choose which workspace and filter the widget should show")

  @Parameter(title: "Workspace")
  var workspace: WorkspaceEntity?

  @Parameter(title: "Filter")
  var filter: ActivityFilterEntity?
}
```

## App shortcuts provider

```swift
import AppIntents

struct AppShortcuts: AppShortcutsProvider {
  static var appShortcuts: [AppShortcut] {
    AppShortcut(
      intent: OpenComposerIntent(),
      phrases: [
        "Open composer in \(.applicationName)",
        "Draft with \(.applicationName)",
      ],
      shortTitle: "Open composer",
      systemImageName: "square.and.pencil"
    )

    AppShortcut(
      intent: CreateItemIntent(),
      phrases: [
        "Create item with \(.applicationName)",
        "Add a task in \(.applicationName)",
      ],
      shortTitle: "Create item",
      systemImageName: "plus.circle"
    )
  }
}
```

## Inline file input

```swift
import AppIntents
import UniformTypeIdentifiers

struct ImportAttachmentIntent: AppIntent {
  static let title: LocalizedStringResource = "Import attachment"
  static let supportedModes: IntentModes = .background
  // Deployment target below iOS 26: delete the supportedModes line.

  @Parameter(
    title: "Files",
    supportedContentTypes: [.image, .pdf, .plainText],
    inputConnectionBehavior: .connectToPreviousIntentResult
  )
  var files: [IntentFile]

  func perform() async throws -> some IntentResult & ProvidesDialog {
    guard !files.isEmpty else {
      return .result(dialog: "No files were provided.")
    }

    for file in files {
      guard let url = file.fileURL else { continue }
      _ = url.startAccessingSecurityScopedResource()
      defer { url.stopAccessingSecurityScopedResource() }
      try await AttachmentImporter.shared.importFile(at: url)
    }

    return .result(dialog: "Imported \(files.count) file(s).")
  }
}
```
