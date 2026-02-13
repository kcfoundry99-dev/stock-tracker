import SwiftUI

struct WishlistView: View {
    @EnvironmentObject var collectionManager: CollectionManager
    @State private var searchText = ""

    var filteredWishlist: [VinylRecord] {
        if searchText.isEmpty {
            return collectionManager.wishlist
        }
        return collectionManager.wishlist.filter {
            $0.title.localizedCaseInsensitiveContains(searchText) ||
            $0.artist.localizedCaseInsensitiveContains(searchText)
        }
    }

    var body: some View {
        NavigationStack {
            Group {
                if filteredWishlist.isEmpty {
                    ContentUnavailableView(
                        "Wishlist Empty",
                        systemImage: "heart",
                        description: Text("Add records you want to find!")
                    )
                } else {
                    List {
                        ForEach(filteredWishlist) { record in
                            NavigationLink(destination: RecordDetailView(record: record)) {
                                HStack {
                                    VStack(alignment: .leading) {
                                        Text(record.title)
                                            .font(.headline)
                                        Text(record.artist)
                                            .font(.subheadline)
                                            .foregroundStyle(.secondary)
                                        if let year = record.year {
                                            Text(String(year))
                                                .font(.caption)
                                                .foregroundStyle(.secondary)
                                        }
                                    }

                                    Spacer()

                                    Button {
                                        collectionManager.moveToCollection(record)
                                    } label: {
                                        Image(systemName: "checkmark.circle.fill")
                                            .foregroundStyle(.green)
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                        }
                        .onDelete(perform: deleteRecords)
                    }
                }
            }
            .navigationTitle("Wishlist")
            .searchable(text: $searchText, prompt: "Search wishlist")
            .overlay {
                if !filteredWishlist.isEmpty {
                    VStack {
                        Spacer()
                        HStack {
                            Text("\(filteredWishlist.count) records")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                                .padding(8)
                                .background(.ultraThinMaterial)
                                .clipShape(Capsule())
                        }
                        .padding()
                    }
                }
            }
        }
    }

    private func deleteRecords(at offsets: IndexSet) {
        for index in offsets {
            collectionManager.removeFromWishlist(filteredWishlist[index])
        }
    }
}

#Preview {
    WishlistView()
        .environmentObject(CollectionManager())
}
