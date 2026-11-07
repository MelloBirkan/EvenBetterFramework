# 1-common-tasks

Contents: What counts as a common task, Find the tasks in the code, Build the task table, Borderline tasks, Ask, Output of this stage.

A label covers the app's common tasks, so this list decides what every later stage tests. Apple's overview page explains how to pick them. This stage applies that page to the code and then asks the person to confirm.

## What counts as a common task

Apple names these groups:

- **Primary functionality**: the goals people download the app for. Apple suggests starting from what the App Store description, screenshots and app previews market. Each goal usually brings smaller steps with it: in Apple's to-do example, viewing the list includes marking a task done, undoing that, changing a due date and creating a task.
- **First launch**: onboarding, an intro video, permission prompts, and skipping any of them.
- **Login**: choosing a sign-in service, entering a username and password, the login button, a password reset, and creating an account.
- **Purchase**, when the app sells anything: choosing a payment method, reviewing the offer's terms, and confirming.
- **Settings**: changing the app's settings, managing purchases, and leaving the screen without changing anything.

Apple's checklist for a complete list:

- Include tasks that people with and without disabilities perform.
- Tasks can differ by device. A task that exists only on one device goes only in that device's matrix.
- Include every mandatory task, such as signing up or buying a subscription before the app can be used.
- Default and loading screens count, such as the list before anything has been added.
- Actions outside the app count when they do a common task, such as marking something done from a notification or a widget.
- Uncommon tasks can be left out. Apple's test: would you ship an urgent fix if people could not complete this task? Uncommon tasks can be described on the accessibility URL page instead.

Third-party content, ads and extensions count only when they appear in a common task. Apple also accepts exceptions that people with disabilities would find reasonable.

## Find the tasks in the code

Start from the app's entry point and follow every route a person can take:

1. **Entry.** The `@main` App and its `WindowGroup`, or the UIKit scene delegate's root view controller. This file belongs to every task.
2. **Structure.** `TabView` tabs, `NavigationStack`, `NavigationSplitView` or `NavigationView` roots, and UIKit tab bar and navigation controllers. Each tab or root list is usually one primary task.
3. **Actions on each screen.** Toolbar buttons, `NavigationLink` and `navigationDestination`, `.sheet`, `.fullScreenCover`, `.popover`, `.alert`, `.confirmationDialog`, `.actionSheet`, `.swipeActions`, `.onDelete` and `.contextMenu`. A presented view usually completes a task that starts on the screen that presents it.
4. **First launch.** A flag such as an `@AppStorage` key that hides onboarding after the first run, and views named for onboarding or a welcome.
5. **Login.** `SignInWithAppleButton`, `ASAuthorizationController`, `SecureField`, and views named for sign-in or accounts.
6. **Purchase.** StoreKit's `SubscriptionStoreView`, `StoreView`, `ProductView` and `purchase(options:)`, or a third-party paywall SDK.
7. **Settings.** A settings screen or tab inside the app.
8. **Outside the app.** A widget extension target, notification actions (`UNNotificationCategory` with `UNNotificationAction` buttons), and `AppIntent` types for Shortcuts and Siri.
9. **Default and loading screens.** `ContentUnavailableView`, `ProgressView`, and branches such as `if items.isEmpty`. Add them to the task they belong to as a note. They are not tasks of their own.
10. **Marketing.** Store copy in the repository, such as `fastlane/metadata/`. A feature the description promises is a primary task.

For each task, list the files its screens come from: the entry file, the screens a person passes through to reach it (a detail screen's task includes the list that opens it), the screen's own file, the files of the subviews it shows (a row view belongs to the list that shows it), and the files of the views it presents. `2-evidence` matches findings to tasks through these files.

Note these on the task too:

- **Route gaps.** A screen that no route reaches, for example a `NavigationLink(value:)` with no matching `navigationDestination`. The task stays on the list, because people expect to complete it, and the gap goes under Open questions in the log.
- **Device differences.** Code behind `#if os(...)`, a size-class branch, or a file that only one target builds. Set the task's devices from it.
- **Ads** shown during the task.
- **Media.** The task plays media when it passes through a file that `0-intake` found playing video or audio.

## Build the task table

| # | Task | Kind | Screens (files) | Devices | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | Browse the plant list | Primary | `PlantCareApp.swift`, `PlantListView.swift` | iPhone | Empty list has no message |

- Name each task with a verb, the way a person would say it.
- Kind is one of Primary, First launch, Login, Purchase, Settings or Outside the app.
- Say plainly when the app has no first launch, login, purchase or settings flow, so the person can correct it.
- With a last evaluation, start from its task list. Mark tasks whose files no longer exist, and add tasks for new screens.

## Borderline tasks

Some tasks may or may not be common: a widget, a notification action, an App Intent, an extension, an About screen, help pages, or links to social media and the web. Ask about each with Apple's urgent-fix test, at most three at a time:

"Would you ship an urgent fix if people could not [task]?" Yes, it is a common task (Recommended) / No, describe it on the accessibility URL page.

Recommend No only for links to the app's marketing channels on social media and the web, which is Apple's example of a task you don't need to include. Every other borderline task, an About screen included, gets Yes as the recommendation. A task answered No moves to the URL outline under "Other tasks".

## Ask

Show the table, then ask:

"Are these the common tasks on [devices]?" Use these tasks (Recommended) / Remove some tasks / Add a task (name it in the answer).

- **Remove some tasks**: ask which, as a multi-select or a numbered list. Removed tasks move to the URL outline's "Other tasks".
- **Add a task**: search the code for the screen the person named and fill in its files. When no file matches, keep the task with no files. Its cells then depend on the manual checks alone, and the log lists it under Open questions.

After a change, show the table again and ask the same question once more. With more changes after that, take the table as it stands and note it in Open questions.

## Output of this stage

- The confirmed task table, with each task's files, devices and notes.
- The tasks that moved to the URL outline.
- Route gaps and tasks without files, for Open questions.
