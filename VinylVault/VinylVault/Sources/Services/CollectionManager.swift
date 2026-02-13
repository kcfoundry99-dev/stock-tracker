import Foundation
import SwiftUI
import Combine

@MainActor
final class CollectionManager: ObservableObject {
    @Published var records: [VinylRecord] = []
    @Published var wishlist: [VinylRecord] = []
    @Published var searchResults: [DiscogsSearchResult] = []
    @Published var selectedRecord: VinylRecord?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let collectionKey = "vinyl_collection"
    private let wishlistKey = "vinyl_wishlist"

    init() {
        loadCollection()
        loadWishlist()
    }

    // MARK: - Collection Management

    func addRecord(_ record: VinylRecord) {
        records.append(record)
        saveCollection()
    }

    func updateRecord(_ record: VinylRecord) {
        if let index = records.firstIndex(where: { $0.id == record.id }) {
            records[index] = record
            saveCollection()
        }
    }

    func deleteRecord(_ record: VinylRecord) {
        records.removeAll { $0.id == record.id }
        saveCollection()
    }

    func deleteRecords(at offsets: IndexSet) {
        records.remove(atOffsets: offsets)
        saveCollection()
    }

    func moveRecord(from source: IndexSet, to destination: Int) {
        records.move(fromOffsets: source, toOffset: destination)
        saveCollection()
    }

    // MARK: - Wishlist Management

    func addToWishlist(_ record: VinylRecord) {
        var wishlistRecord = record
        wishlistRecord.isWishlist = true
        wishlist.append(wishlistRecord)
        saveWishlist()
    }

    func removeFromWishlist(_ record: VinylRecord) {
        wishlist.removeAll { $0.id == record.id }
        saveWishlist()
    }

    func moveToCollection(_ record: VinylRecord) {
        removeFromWishlist(record)
        var collectionRecord = record
        collectionRecord.isWishlist = false
        addRecord(collectionRecord)
    }

    // MARK: - Statistics

    var totalValue: Double {
        records.compactMap { $0.marketValue }.reduce(0, +)
    }

    var totalPurchasePrice: Double {
        records.compactMap { $0.purchasePrice }.reduce(0, +)
    }

    var recordCount: Int {
        records.count
    }

    var averageValue: Double {
        guard !records.isEmpty else { return 0 }
        return totalValue / Double(records.count)
    }

    // MARK: - Filtering

    var filteredRecords: [VinylRecord] {
        records
    }

    func recordsByArtist(_ artist: String) -> [VinylRecord] {
        records.filter { $0.artist.localizedCaseInsensitiveContains(artist) }
    }

    func recordsByYear(_ year: Int) -> [VinylRecord] {
        records.filter { $0.year == year }
    }

    func recordsByGenre(_ genre: String) -> [VinylRecord] {
        records.filter { $0.genre.contains(genre) }
    }

    // MARK: - Persistence

    private func saveCollection() {
        if let encoded = try? JSONEncoder().encode(records) {
            UserDefaults.standard.set(encoded, forKey: collectionKey)
        }
    }

    private func loadCollection() {
        if let data = UserDefaults.standard.data(forKey: collectionKey),
           let decoded = try? JSONDecoder().decode([VinylRecord].self, from: data) {
            records = decoded
        }
    }

    private func saveWishlist() {
        if let encoded = try? JSONEncoder().encode(wishlist) {
            UserDefaults.standard.set(encoded, forKey: wishlistKey)
        }
    }

    private func loadWishlist() {
        if let data = UserDefaults.standard.data(forKey: wishlistKey),
           let decoded = try? JSONDecoder().decode([VinylRecord].self, from: data) {
            wishlist = decoded
        }
    }

    // MARK: - Export

    func exportCollection() -> String {
        var csv = "Title,Artist,Year,Genre,Label,Condition,Purchase Price,Market Value,Date Added\n"

        for record in records {
            csv += "\"\(record.title)\",\"\(record.artist)\","
            csv += "\(record.year ?? 0),"
            csv += "\"\(record.genre.joined(separator: "; "))\","
            csv += "\"\(record.label ?? "")\","
            csv += "\"\(record.condition.rawValue)\","
            csv += "\(record.purchasePrice ?? 0),"
            csv += "\(record.marketValue ?? 0),"
            csv += "\"\(record.dateAdded)\"\n"
        }

        return csv
    }
}
