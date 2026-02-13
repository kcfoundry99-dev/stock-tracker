import Foundation
import UIKit

actor DiscogsService {
    private let baseURL = "https://api.discogs.com"
    private let decoder: JSONDecoder

    init() {
        decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
    }

    func search(query: String, type: SearchType = .release, page: Int = 1, perPage: Int = 25) async throws -> DiscogsSearchResponse {
        var components = URLComponents(string: "\(baseURL)/database/search")
        components?.queryItems = [
            URLQueryItem(name: "q", value: query),
            URLQueryItem(name: "type", value: type.rawValue),
            URLQueryItem(name: "page", value: String(page)),
            URLQueryItem(name: "per_page", value: String(perPage)),
            URLQueryItem(name: "key", value: Secrets.discogsKey),
            URLQueryItem(name: "secret", value: Secrets.discogsSecret)
        ]

        guard let url = components?.url else {
            throw DiscogsError.invalidURL
        }

        let (data, _) = try await URLSession.shared.data(from: url)
        return try decoder.decode(DiscogsSearchResponse.self, from: data)
    }

    func getRelease(id: Int) async throws -> DiscogsRelease {
        guard let url = URL(string: "\(baseURL)/releases/\(id)?key=\(Secrets.discogsKey)&secret=\(Secrets.discogsSecret)") else {
            throw DiscogsError.invalidURL
        }

        let (data, _) = try await URLSession.shared.data(from: url)
        return try decoder.decode(DiscogsRelease.self, from: data)
    }

    func getArtist(id: Int) async throws -> DiscogsArtist {
        guard let url = URL(string: "\(baseURL)/artists/\(id)?key=\(Secrets.discogsKey)&secret=\(Secrets.discogsSecret)") else {
            throw DiscogsError.invalidURL
        }

        let (data, _) = try await URLSession.shared.data(from: url)
        return try decoder.decode(DiscogsArtist.self, from: data)
    }

    func downloadImage(from urlString: String) async throws -> Data {
        guard let url = URL(string: urlString) else {
            throw DiscogsError.invalidImageURL
        }

        let (data, _) = try await URLSession.shared.data(from: url)
        return data
    }
}

enum SearchType: String {
    case release = "release"
    case master = "master"
    case artist = "artist"
    case label = "label"
}

enum DiscogsError: LocalizedError {
    case invalidURL
    case invalidImageURL
    case noData
    case apiError(String)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid URL"
        case .invalidImageURL: return "Invalid image URL"
        case .noData: return "No data received"
        case .apiError(let message): return "API Error: \(message)"
        }
    }
}

// MARK: - Discogs API Response Models

struct DiscogsSearchResponse: Codable {
    let pagination: DiscogsPagination
    let results: [DiscogsSearchResult]
}

struct DiscogsPagination: Codable {
    let page: Int
    let pages: Int
    let perPage: Int
    let items: Int
}

struct DiscogsSearchResult: Codable {
    let id: Int
    let type: String
    let masterId: Int?
    let masterUrl: String?
    let uri: String?
    let title: String
    let thumb: String?
    let coverImage: String?
    let resourceUrl: String
    let country: String?
    let year: String?
    let format: [String]?
    let label: [String]?
    let genre: [String]?
    let style: [String]?
    let barcode: [String]?
    let catno: String?

    enum CodingKeys: String, CodingKey {
        case id, type, uri, title, thumb, country, year, format, label, genre, style, barcode
        case masterId = "master_id"
        case masterUrl = "master_url"
        case coverImage = "cover_image"
        case resourceUrl = "resource_url"
        case catno
    }
}

struct DiscogsRelease: Codable {
    let id: Int
    let title: String
    let artists: [DiscogsArtistSummary]?
    let artistsSort: String?
    let year: Int?
    let images: [DiscogsImage]?
    let genres: [String]?
    let styles: [String]?
    let labels: [DiscogsLabelSummary]?
    let formats: [DiscogsFormat]?
    let tracklist: [DiscogsTrack]?
    let country: String?
    let released: String?
    let notes: String?
    let community: DiscogsCommunity?

    enum CodingKeys: String, CodingKey {
        case id, title, year, images, genres, styles, labels, formats, tracklist, country, notes, community
        case artists = "artists"
        case artistsSort = "artists_sort"
        case released
    }
}

struct DiscogsArtistSummary: Codable {
    let id: Int
    let name: String
    let namevariations: [String]?
    let anv: String?
    let join: String?
    let role: String?
    let tracks: String?
    let resourceUrl: String?
}

struct DiscogsArtist: Codable {
    let id: Int
    let name: String
    let realName: String?
    let images: [DiscogsImage]?
    let profile: String?
    let namevariations: [String]?

    enum CodingKeys: String, CodingKey {
        case id, name, images, profile
        case realName = "real_name"
        case namevariations = "name_variations"
    }
}

struct DiscogsImage: Codable {
    let type: String
    let uri: String?
    let uri150: String?
    let width: Int
    let height: Int

    enum CodingKeys: String, CodingKey {
        case type, uri, width, height
        case uri150 = "uri150"
    }
}

struct DiscogsLabelSummary: Codable {
    let id: Int
    let name: String
    let catno: String?
    let entityType: String?

    enum CodingKeys: String, CodingKey {
        case id, name, catno
        case entityType = "entity_type"
    }
}

struct DiscogsFormat: Codable {
    let name: String
    let qty: String?
    let descriptions: [String]?
    let text: String?
}

struct DiscogsTrack: Codable {
    let position: String
    let title: String
    let duration: String?
}

struct DiscogsCommunity: Codable {
    let have: Int?
    let want: Int?
    let rating: DiscogsRating?
}

struct DiscogsRating: Codable {
    let count: Int
    let average: Double
}

// MARK: - API Credentials Helper

enum Secrets {
    // IMPORTANT: Replace these with your own Discogs API credentials!
    // Get them at https://www.discogs.com/developers/consumer
    static let discogsKey = "YOUR_CONSUMER_KEY"
    static let discogsSecret = "YOUR_CONSUMER_SECRET"
}
