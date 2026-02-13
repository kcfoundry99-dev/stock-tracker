import SwiftUI

struct SearchView: View {
    @EnvironmentObject var collectionManager: CollectionManager
    @StateObject private var discogsService = DiscogsService()
    @State private var searchText = ""
    @State private var searchResults: [DiscogsSearchResult] = []
    @State private var isSearching = false
    @State private var selectedResult: DiscogsSearchResult?
    @State private var showingDetail = false

    var body: some View {
        NavigationStack {
            VStack {
                // Search Bar
                HStack {
                    TextField("Search vinyl records...", text: $searchText)
                        .textFieldStyle(.roundedBorder)
                        .autocorrectionDisabled()

                    Button {
                        Task {
                            await search()
                        }
                    } label: {
                        Image(systemName: "magnifyingglass")
                            .foregroundStyle(.blue)
                    }
                    .disabled(searchText.isEmpty || isSearching)
                }
                .padding()

                if isSearching {
                    ProgressView("Searching Discogs...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if searchResults.isEmpty && !searchText.isEmpty {
                    ContentUnavailableView(
                        "No Results",
                        systemImage: "music.note.list",
                        description: Text("Try a different search term")
                    )
                } else if searchResults.isEmpty {
                    ContentUnavailableView(
                        "Search Discogs",
                        systemImage: "magnifyingglass",
                        description: Text("Enter artist, album, or title to find vinyl records")
                    )
                } else {
                    List(searchResults) { result in
                        Button {
                            selectedResult = result
                            showingDetail = true
                        } label: {
                            SearchResultRow(result: result)
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
            .navigationTitle("Search")
            .sheet(isPresented: $showingDetail) {
                if let result = selectedResult {
                    SearchResultDetailView(result: result)
                }
            }
            .onSubmit(of: .textField) {
                Task {
                    await search()
                }
            }
        }
    }

    private func search() async {
        guard !searchText.isEmpty else { return }

        isSearching = true
        searchResults = []

        do {
            let response = try await discogsService.search(query: searchText)
            searchResults = response.results
        } catch {
            print("Search error: \(error)")
        }

        isSearching = false
    }
}

struct SearchResultRow: View {
    let result: DiscogsSearchResult

    var body: some View {
        HStack(spacing: 12) {
            AsyncImage(url: URL(string: result.thumb ?? "")) { phase in
                switch phase {
                case .empty:
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.gray.opacity(0.2))
                        .frame(width: 50, height: 50)
                        .overlay { ProgressView() }
                case .success(let image):
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(width: 50, height: 50)
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                case .failure:
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.gray.opacity(0.2))
                        .frame(width: 50, height: 50)
                        .overlay {
                            Image(systemName: "music.note")
                                .foregroundStyle(.gray)
                        }
                @unknown default:
                    EmptyView()
                }
            }
            .frame(width: 50, height: 50)

            VStack(alignment: .leading, spacing: 4) {
                Text(result.title)
                    .font(.headline)
                    .lineLimit(2)

                HStack {
                    if let year = result.year, !year.isEmpty {
                        Text(year)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }

                    if let format = result.format?.first {
                        Text(format)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }

                if let label = result.label?.first {
                    Text(label)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                }
            }
        }
        .padding(.vertical, 4)
    }
}

#Preview {
    SearchView()
        .environmentObject(CollectionManager())
}
