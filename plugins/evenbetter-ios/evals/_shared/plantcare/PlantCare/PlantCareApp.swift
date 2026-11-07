import SwiftUI

@main
struct PlantCareApp: App {
    @State private var store = PlantStore()

    var body: some Scene {
        WindowGroup {
            PlantListView()
                .environment(store)
        }
    }
}
