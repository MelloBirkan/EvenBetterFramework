import SwiftUI

struct PlantListView: View {
    @Environment(PlantStore.self) private var store
    @State private var showingAdd = false

    var body: some View {
        NavigationView {
            List(store.plants) { plant in
                NavigationLink(value: plant) {
                    PlantRow(plant: plant)
                }
            }
            .toolbar {
                Button {
                    showingAdd = true
                } label: {
                    Image(systemName: "plus")
                }
            }
            .sheet(isPresented: $showingAdd) {
                AddPlantView()
            }
        }
    }
}

struct PlantRow: View {
    let plant: Plant

    var body: some View {
        HStack {
            Image("leaf-illustration")
            VStack(alignment: .leading) {
                Text(plant.name)
                    .font(.system(size: 17, weight: .semibold))
                Text("Every \(plant.wateringIntervalDays) days")
                    .font(.system(size: 9))
                    .foregroundColor(.black)
            }
        }
    }
}
