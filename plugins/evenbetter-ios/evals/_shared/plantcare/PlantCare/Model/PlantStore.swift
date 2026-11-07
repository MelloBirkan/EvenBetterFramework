import Foundation
import Observation

struct Plant: Identifiable, Hashable {
    let id = UUID()
    var name: String
    var wateringIntervalDays: Int
    var lastWatered: Date
}

@Observable
final class PlantStore {
    var plants: [Plant] = [
        Plant(name: "Monstera", wateringIntervalDays: 7, lastWatered: .now),
        Plant(name: "Fiddle Leaf Fig", wateringIntervalDays: 10, lastWatered: .now),
    ]
    var didSave = false

    func delete(_ plant: Plant) {
        plants.removeAll { $0.id == plant.id }
    }

    func water(_ plant: Plant) {
        guard let index = plants.firstIndex(of: plant) else { return }
        plants[index].lastWatered = .now
        didSave.toggle()
    }
}
