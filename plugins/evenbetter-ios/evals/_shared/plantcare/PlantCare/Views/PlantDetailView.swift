import SwiftUI

struct PlantDetailView: View {
    @Environment(PlantStore.self) private var store
    let plant: Plant
    @State private var showingOptions = false
    @State private var isPulsing = false

    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: "drop.fill")
                .font(.largeTitle)
                .scaleEffect(isPulsing ? 1.2 : 1.0)
                .onAppear {
                    withAnimation(.easeInOut(duration: 1).repeatForever()) {
                        isPulsing = true
                    }
                }

            Text("Water now")
                .padding()
                .background(Color.green)
                .onTapGesture {
                    store.water(plant)
                }
                .sensoryFeedback(.error, trigger: store.didSave)

            Image(systemName: "trash")
                .frame(width: 28, height: 28)
                .onTapGesture {
                    store.delete(plant)
                }

            Button("More") { showingOptions = true }
        }
        .actionSheet(isPresented: $showingOptions) {
            ActionSheet(title: Text("Options"), buttons: [.cancel()])
        }
    }
}
