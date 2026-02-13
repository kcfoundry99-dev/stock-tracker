import Foundation

struct VinylRecord: Identifiable, Codable, Hashable {
    let id: UUID
    var discogsId: Int?
    var title: String
    var artist: String
    var year: Int?
    var genre: [String]
    var style: [String]
    var label: String?
    var catalogNumber: String?
    var coverImageURL: String?
    var labelImageURL: String?
    var localCoverImageData: Data?
    var localLabelImageData: Data?
    var format: String?
    var country: String?
    var tracklist: [Track]
    var condition: RecordCondition
    var purchasePrice: Double?
    var marketValue: Double?
    var notes: String
    var dateAdded: Date
    var isWishlist: Bool

    init(
        id: UUID = UUID(),
        discogsId: Int? = nil,
        title: String = "",
        artist: String = "",
        year: Int? = nil,
        genre: [String] = [],
        style: [String] = [],
        label: String? = nil,
        catalogNumber: String? = nil,
        coverImageURL: String? = nil,
        labelImageURL: String? = nil,
        localCoverImageData: Data? = nil,
        localLabelImageData: Data? = nil,
        format: String? = nil,
        country: String? = nil,
        tracklist: [Track] = [],
        condition: RecordCondition = .good,
        purchasePrice: Double? = nil,
        marketValue: Double? = nil,
        notes: String = "",
        dateAdded: Date = Date(),
        isWishlist: Bool = false
    ) {
        self.id = id
        self.discogsId = discogsId
        self.title = title
        self.artist = artist
        self.year = year
        self.genre = genre
        self.style = style
        self.label = label
        self.catalogNumber = catalogNumber
        self.coverImageURL = coverImageURL
        self.labelImageURL = labelImageURL
        self.localCoverImageData = localCoverImageData
        self.localLabelImageData = localLabelImageData
        self.format = format
        self.country = country
        self.tracklist = tracklist
        self.condition = condition
        self.purchasePrice = purchasePrice
        self.marketValue = marketValue
        self.notes = notes
        self.dateAdded = dateAdded
        self.isWishlist = isWishlist
    }

    var formattedValue: String {
        guard let value = marketValue else { return "Unknown" }
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.currencyCode = "USD"
        return formatter.string(from: NSNumber(value: value)) ?? "Unknown"
    }

    var formattedPurchasePrice: String {
        guard let price = purchasePrice else { return "Not recorded" }
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.currencyCode = "USD"
        return formatter.string(from: NSNumber(value: price)) ?? "Unknown"
    }
}

struct Track: Identifiable, Codable, Hashable {
    let id: UUID
    var position: String
    var title: String
    var duration: String

    init(id: UUID = UUID(), position: String = "", title: String = "", duration: String = "") {
        self.id = id
        self.position = position
        self.title = title
        self.duration = duration
    }
}

enum RecordCondition: String, Codable, CaseIterable, Identifiable {
    case mint = "Mint"
    case nearMint = "Near Mint"
    case veryGoodPlus = "Very Good Plus"
    case veryGood = "Very Good"
    case good = "Good"
    case fair = "Fair"
    case poor = "Poor"

    var id: String { rawValue }

    var description: String {
        switch self {
        case .mint: return "Perfect condition, like new"
        case .nearMint: return "Almost perfect, minimal signs of use"
        case .veryGoodPlus: return "Minor wear, excellent sound"
        case .veryGood: return "Some signs of wear, good sound"
        case .good: return "Noticeable wear but playable"
        case .fair: return "Significant wear, may have issues"
        case .poor: return "Heavy wear, may be damaged"
        }
    }
}
