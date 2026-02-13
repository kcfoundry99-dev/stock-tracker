import SwiftUI

struct ContentView: View {
    @EnvironmentObject var collectionManager: CollectionManager
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            CollectionView()
                .tabItem {
                    Label("Collection", systemImage: "music.note.list")
                }
                .tag(0)

            SearchView()
                .tabItem {
                    Label("Search", systemImage: "magnifyingglass")
                }
                .tag(1)

            WishlistView()
                .tabItem {
                    Label("Wishlist", systemImage: "heart")
                }
                .tag(2)

            StatsView()
                .tabItem {
                    Label("Stats", systemImage: "chart.bar")
                }
                .tag(3)
        }
        .tint(.blue)
    }
}

#Preview {
    ContentView()
        .environmentObject(CollectionManager())
        .environmentObject(DiscogsService())
}
