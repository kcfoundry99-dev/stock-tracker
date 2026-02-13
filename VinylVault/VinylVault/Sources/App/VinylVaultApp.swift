import SwiftUI

@main
struct VinylVaultApp: App {
    @StateObject private var collectionManager = CollectionManager()
    @StateObject private var discogsService = DiscogsService()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(collectionManager)
                .environmentObject(discogsService)
        }
    }
}
