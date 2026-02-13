import SwiftUI

struct RecordDetailView: View {
    @EnvironmentObject var collectionManager: CollectionManager
    let record: VinylRecord

    @State private var isEditing = false
    @State private var showingDeleteAlert = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Cover Image
                if let imageData = record.localCoverImageData,
                   let uiImage = UIImage(data: imageData) {
                    Image(uiImage: uiImage)
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(maxWidth: .infinity)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                } else if let urlString = record.coverImageURL,
                          let url = URL(string: urlString) {
                    AsyncImage(url: url) { phase in
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
                } else {
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color.gray.opacity(0.2))
                        .frame(height: 300)
                        .overlay {
                            Image(systemName: "music.note")
                                .font(.largeTitle)
                                .foregroundStyle(.gray)
                        }
                }

                VStack(alignment: .leading, spacing: 16) {
                    // Title & Artist
                    VStack(alignment: .leading, spacing: 4) {
                        Text(record.title)
                            .font(.title)
                            .fontWeight(.bold)

                        Text(record.artist)
                            .font(.title3)
                            .foregroundStyle(.secondary)
                    }

                    // Info Grid
                    LazyVGrid(columns: [
                        GridItem(.flexible()),
                        GridItem(.flexible())
                    ], spacing: 16) {
                        InfoCard(title: "Year", value: record.year.map { String($0) } ?? "Unknown")
                        InfoCard(title: "Genre", value: record.genre.joined(separator: ", ").isEmpty ? "Unknown" : record.genre.joined(separator: ", "))
                        InfoCard(title: "Label", value: record.label ?? "Unknown")
                        InfoCard(title: "Format", value: record.format ?? "Unknown")
                        InfoCard(title: "Condition", value: record.condition.rawValue, color: conditionColor)
                        InfoCard(title: "Country", value: record.country ?? "Unknown")
                    }

                    // Value Section
                    if record.marketValue != nil || record.purchasePrice != nil {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Value")
                                .font(.headline)

                            HStack(spacing: 20) {
                                ValueCard(
                                    title: "Market Value",
                                    value: record.formattedValue,
                                    color: .green
                                )

                                ValueCard(
                                    title: "Purchase Price",
                                    value: record.formattedPurchasePrice,
                                    color: .blue
                                )
                            }
                        }
                    }

                    // Tracklist
                    if !record.tracklist.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Tracklist")
                                .font(.headline)

                            ForEach(record.tracklist) { track in
                                HStack {
                                    Text(track.position)
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                        .frame(width: 30)

                                    Text(track.title)
                                        .lineLimit(1)

                                    Spacer()

                                    Text(track.duration)
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                                .padding(.vertical, 4)
                            }
                        }
                    }

                    // Notes
                    if !record.notes.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Notes")
                                .font(.headline)

                            Text(record.notes)
                                .font(.body)
                                .foregroundStyle(.secondary)
                        }
                    }

                    // Date Added
                    Text("Added on \(record.dateAdded.formatted(date: .abbreviated, time: .shortened))")
                        .font(.caption)
                        .foregroundStyle(.tertiary)
                }
                .padding()
            }
        }
        .navigationTitle(record.title)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Menu {
                    Button {
                        // Share functionality
                    } label: {
                        Label("Share", systemImage: "square.and.arrow.up")
                    }

                    Button(role: .destructive) {
                        showingDeleteAlert = true
                    } label: {
                        Label("Delete", systemImage: "trash")
                    }
                } label: {
                    Image(systemName: "ellipsis.circle")
                }
            }
        }
        .alert("Delete Record", isPresented: $showingDeleteAlert) {
            Button("Cancel", role: .cancel) { }
            Button("Delete", role: .destructive) {
                collectionManager.deleteRecord(record)
            }
        } message: {
            Text("Are you sure you want to delete \"\(record.title)\" from your collection?")
        }
    }

    private var conditionColor: Color {
        switch record.condition {
        case .mint: return .green
        case .nearMint: return .green
        case .veryGoodPlus: return .blue
        case .veryGood: return .blue
        case .good: return .orange
        case .fair: return .orange
        case .poor: return .red
        }
    }
}

struct InfoCard: View {
    let title: String
    let value: String
    var color: Color = .primary

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)

            Text(value)
                .font(.subheadline)
                .fontWeight(.medium)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }
}

struct ValueCard: View {
    let title: String
    let value: String
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)

            Text(value)
                .font(.title3)
                .fontWeight(.bold)
                .foregroundStyle(color)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(color.opacity(0.1))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }
}

#Preview {
    NavigationStack {
        RecordDetailView(record: VinylRecord(
            title: "Kind of Blue",
            artist: "Miles Davis",
            year: 1959,
            genre: ["Jazz"],
            label: "Columbia",
            condition: .veryGoodPlus,
            marketValue: 150.00
        ))
    }
    .environmentObject(CollectionManager())
}
