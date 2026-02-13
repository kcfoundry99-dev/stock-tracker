import SwiftUI

struct SearchResultDetailView: View {
    let result: DiscogsSearchResult
    @EnvironmentObject var collectionManager: CollectionManager
    @Environment(\.dismiss) private var dismiss
    @State private var isLoading = false
    @State private var release: DiscogsRelease?
    @State private var error: String?

    var body: some View {
        NavigationStack {
            ScrollView {
                if isLoading {
                    ProgressView("Loading details...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                        .padding(.top, 100)
                } else if let release = release {
                    VStack(alignment: .leading, spacing: 20) {
                        // Cover Image
                        AsyncImage(url: URL(string: release.images?.first?.uri ?? "")) { phase in
                            switch phase {
                            case .success(let image):
                                image
                                    .resizable()
                                    .aspectRatio(contentMode: .fit)
                                    .clipShape(RoundedRectangle(cornerRadius: 12))
                            default:
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(Color.gray.opacity(0.2))
                                    .frame(height: 300)
                                    .overlay {
                                        Image(systemName: "music.note")
                                            .font(.largeTitle)
                                            .foregroundStyle(.gray)
                                    }
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.horizontal)

                        VStack(alignment: .leading, spacing: 16) {
                            // Title & Artist
                            Text(release.title)
                                .font(.title)
                                .fontWeight(.bold)

                            if let artist = release.artistsSort {
                                Text(artist)
                                    .font(.title3)
                                    .foregroundStyle(.secondary)
                            }

                            // Info Grid
                            LazyVGrid(columns: [
                                GridItem(.flexible()),
                                GridItem(.flexible())
                            ], spacing: 12) {
                                if let year = release.year {
                                    DetailItem(title: "Year", value: String(year))
                                }

                                if let country = release.country {
                                    DetailItem(title: "Country", value: country)
                                }

                                if let genre = release.genres?.joined(separator: ", ") {
                                    DetailItem(title: "Genre", value: genre)
                                }

                                if let style = release.styles?.joined(separator: ", ") {
                                    DetailItem(title: "Style", value: style)
                                }
                            }

                            // Labels
                            if let labels = release.labels {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Label")
                                        .font(.headline)

                                    ForEach(labels, id: \.id) { label in
                                        HStack {
                                            Text(label.name)
                                            if let catno = label.catno {
                                                Text(catno)
                                                    .foregroundStyle(.secondary)
                                            }
                                        }
                                        .font(.subheadline)
                                    }
                                }
                            }

                            // Format
                            if let formats = release.formats {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Format")
                                        .font(.headline)

                                    ForEach(formats, id: \.name) { format in
                                        VStack(alignment: .leading, spacing: 4) {
                                            Text("\(format.qty ?? "")x \(format.name)")
                                            if let desc = format.descriptions?.joined(separator: ", ") {
                                                Text(desc)
                                                    .font(.caption)
                                                    .foregroundStyle(.secondary)
                                            }
                                        }
                                        .font(.subheadline)
                                    }
                                }
                            }

                            // Tracklist
                            if let tracklist = release.tracklist, !tracklist.isEmpty {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Tracklist")
                                        .font(.headline)

                                    ForEach(tracklist, id: \.position) { track in
                                        HStack {
                                            Text(track.position)
                                                .font(.caption)
                                                .foregroundStyle(.secondary)
                                                .frame(width: 30)

                                            Text(track.title)
                                                .lineLimit(1)

                                            Spacer()

                                            Text(track.duration ?? "")
                                                .font(.caption)
                                                .foregroundStyle(.secondary)
                                        }
                                        .padding(.vertical, 4)
                                    }
                                }
                            }

                            // Community Rating
                            if let community = release.community {
                                HStack {
                                    Image(systemName: "star.fill")
                                        .foregroundStyle(.yellow)
                                    Text(String(format: "%.1f", community.rating?.average ?? 0))
                                        .fontWeight(.semibold)
                                    Text("(\(community.rating?.count ?? 0) ratings)")
                                        .foregroundStyle(.secondary)
                                }
                                .padding(.vertical, 8)
                            }

                            // Notes
                            if let notes = release.notes, !notes.isEmpty {
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Notes")
                                        .font(.headline)

                                    Text(notes)
                                        .font(.body)
                                        .foregroundStyle(.secondary)
                                }
                            }

                            // Add Buttons
                            HStack(spacing: 16) {
                                Button {
                                    addToCollection(asWishlist: false)
                                } label: {
                                    Label("Add to Collection", systemImage: "plus.circle.fill")
                                        .frame(maxWidth: .infinity)
                                }
                                .buttonStyle(.borderedProminent)

                                Button {
                                    addToCollection(asWishlist: true)
                                } label: {
                                    Label("Add to Wishlist", systemImage: "heart")
                                        .frame(maxWidth: .infinity)
                                }
                                .buttonStyle(.bordered)
                            }
                            .padding(.top)
                        }
                        .padding()
                    }
                } else if let error = error {
                    ContentUnavailableView(
                        "Error",
                        systemImage: "exclamationmark.triangle",
                        description: Text(error)
                    )
                }
            }
            .navigationTitle("Details")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Close") {
                        dismiss()
                    }
                }
            }
            .task {
                await loadDetails()
            }
        }
    }

    private func loadDetails() async {
        isLoading = true
        error = nil

        do {
            // For now, we'll create a mock release from search results
            // In production, you'd call discogsService.getRelease(id: result.id)
            release = DiscogsRelease(
                id: result.id,
                title: result.title,
                artists: nil,
                artistsSort: nil,
                year: Int(result.year ?? ""),
                images: result.thumb.map { [DiscogsImage(type: "cover", uri: $0, uri150: $0, width: 600, height: 600)] },
                genres: result.genre,
                styles: result.style,
                labels: result.label.map { [DiscogsLabelSummary(id: 0, name: $0, catno: result.catno, entityType: nil)] },
                formats: result.format.map { [DiscogsFormat(name: $0.first ?? "Vinyl", qty: "1", descriptions: Array($0.dropFirst()), text: nil)] },
                tracklist: nil,
                country: result.country,
                released: result.year,
                notes: nil,
                community: nil
            )
        }

        isLoading = false
    }

    private func addToCollection(asWishlist: Bool) {
        guard let release = release else { return }

        let record = VinylRecord(
            discogsId: release.id,
            title: release.title,
            artist: release.artistsSort ?? "Unknown Artist",
            year: release.year,
            genre: release.genres ?? [],
            style: release.styles ?? [],
            label: release.labels?.first?.name,
            catalogNumber: release.labels?.first?.catno,
            coverImageURL: release.images?.first?.uri,
            format: release.formats?.first?.name,
            country: release.country,
            tracklist: release.tracklist?.map {
                Track(position: $0.position, title: $0.title, duration: $0.duration ?? "")
            } ?? [],
            condition: .good,
            isWishlist: asWishlist
        )

        if asWishlist {
            collectionManager.addToWishlist(record)
        } else {
            collectionManager.addRecord(record)
        }

        dismiss()
    }
}

struct DetailItem: View {
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
            Text(value)
                .font(.subheadline)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

#Preview {
    SearchResultDetailView(result: DiscogsSearchResult(
        id: 12345,
        type: "release",
        masterId: nil,
        masterUrl: nil,
        uri: nil,
        title: "Kind of Blue - Miles Davis",
        thumb: "https://i.discogs.com/xyz.jpg",
        coverImage: nil,
        resourceUrl: "",
        country: "US",
        year: "1959",
        format: ["Vinyl", "LP", "Album"],
        label: ["Columbia"],
        genre: ["Jazz"],
        style: ["Cool Jazz"],
        barcode: nil,
        catno: "CP 1275"
    ))
    .environmentObject(CollectionManager())
}
