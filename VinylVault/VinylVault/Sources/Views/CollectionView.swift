import SwiftUI

struct CollectionView: View {
    @EnvironmentObject var collectionManager: CollectionManager
    @State private var showingAddRecord = false
    @State private var searchText = ""
    @State private var sortOrder: SortOrder = .dateAdded

    enum SortOrder: String, CaseIterable {
        case dateAdded = "Date Added"
        case title = "Title"
        case artist = "Artist"
        case value = "Value"
    }

    var filteredRecords: [VinylRecord] {
        var result = collectionManager.records

        if !searchText.isEmpty {
            result = result.filter {
                $0.title.localizedCaseInsensitiveContains(searchText) ||
                $0.artist.localizedCaseInsensitiveContains(searchText)
            }
        }

        switch sortOrder {
        case .dateAdded:
            result.sort { $0.dateAdded > $1.dateAdded }
        case .title:
            result.sort { $0.title.localizedCompare($1.title) == .orderedAscending }
        case .artist:
            result.sort { $0.artist.localizedCompare($1.artist) == .orderedAscending }
        case .value:
            result.sort { ($0.marketValue ?? 0) > ($1.marketValue ?? 0) }
        }

        return result
    }

    var body: some View {
        NavigationStack {
            Group {
                if filteredRecords.isEmpty {
                    ContentUnavailableView(
                        "No Records",
                        systemImage: "music.note",
                        description: Text("Add your first vinyl record to get started!")
                    )
                } else {
                    List {
                        ForEach(filteredRecords) { record in
                            NavigationLink(destination: RecordDetailView(record: record)) {
                                RecordRowView(record: record)
                            }
                        }
                        .onDelete(perform: deleteRecords)
                        .onMove(perform: moveRecords)
                    }
                }
            }
            .navigationTitle("My Collection")
            .searchable(text: $searchText, prompt: "Search records")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Menu {
                        Picker("Sort by", selection: $sortOrder) {
                            ForEach(SortOrder.allCases, id: \.self) { order in
                                Text(order.rawValue).tag(order)
                            }
                        }
                    } label: {
                        Image(systemName: "arrow.up.arrow.down")
                    }
                }

                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        showingAddRecord = true
                    } label: {
                        Image(systemName: "plus")
                    }
                }
            }
            .sheet(isPresented: $showingAddRecord) {
                AddRecordView()
            }
        }
    }

    private func deleteRecords(at offsets: IndexSet) {
        for index in offsets {
            collectionManager.deleteRecord(filteredRecords[index])
        }
    }

    private func moveRecords(from source: IndexSet, to destination: Int) {
        collectionManager.moveRecord(from: source, to: destination)
    }
}

struct RecordRowView: View {
    let record: VinylRecord

    var body: some View {
        HStack(spacing: 12) {
            // Cover Image
            AsyncImage(url: URL(string: record.coverImageURL ?? "")) { phase in
                switch phase {
                case .empty:
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.gray.opacity(0.2))
                        .frame(width: 60, height: 60)
                        .overlay {
                            ProgressView()
                        }
                case .success(let image):
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                        .frame(width: 60, height: 60)
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                case .failure:
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color.gray.opacity(0.2))
                        .frame(width: 60, height: 60)
                        .overlay {
                            Image(systemName: "music.note")
                                .foregroundStyle(.gray)
                        }
                @unknown default:
                    EmptyView()
                }
            }
            .frame(width: 60, height: 60)

            VStack(alignment: .leading, spacing: 4) {
                Text(record.title)
                    .font(.headline)
                    .lineLimit(1)

                Text(record.artist)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)

                if let year = record.year {
                    Text(String(year))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }

            Spacer()

            if let value = record.marketValue, value > 0 {
                VStack(alignment: .trailing, spacing: 2) {
                    Text("Value")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                    Text("$\(String(format: "%.2f", value))")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                        .foregroundStyle(.green)
                }
            }
        }
        .padding(.vertical, 4)
    }
}

#Preview {
    CollectionView()
        .environmentObject(CollectionManager())
}
