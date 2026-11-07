import SwiftUI

struct AddPlantView: View {
    @Environment(PlantStore.self) private var store
    @State private var name = ""
    @State private var interval = 7

    var body: some View {
        Form {
            TextField("Name", text: $name)
            Stepper("Every \(interval) days", value: $interval, in: 1...30)

            // Correct patterns, should NOT be flagged:
            Button {
                store.plants.append(Plant(name: name, wateringIntervalDays: interval, lastWatered: .now))
            } label: {
                Image(systemName: "checkmark")
            }
            .accessibilityLabel("Save plant")

            Image("divider-flourish")
                .accessibilityHidden(true)
        }
    }
}
