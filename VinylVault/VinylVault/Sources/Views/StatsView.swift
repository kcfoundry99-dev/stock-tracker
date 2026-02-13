import SwiftUI

struct StatsView: View {
    @EnvironmentObject var collectionManager: CollectionManager

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Summary Cards
                    LazyVGrid(columns: [
                        GridItem(.flexible()),
                        GridItem(.flexible())
                    ], spacing: 16) {
                        StatCard(
                            title: "Total Records",
                            value: "\(collectionManager.recordCount)",
                            icon: "music.note",
                            color: .blue
                        )

                        StatCard(
                            title: "Total Value",
                            value: formatCurrency(collectionManager.totalValue),
                            icon: "dollarsign.circle",
                            color: .green
                        )

                        StatCard(
                            title: "Avg Value",
                            value: formatCurrency(collectionManager.averageValue),
                            icon: "chart.bar",
                            color: .orange
                        )

                        StatCard(
                            title: "Total Spent",
                            value: formatCurrency(collectionManager.totalPurchasePrice),
                            icon: "creditcard",
                            color: .red
                        )
                    }
                    .padding(.horizontal)

                    // Genre Breakdown
                    if !genreCounts.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Genre Distribution")
                                .font(.headline)
                                .padding(.horizontal)

                            GenreChart(genreCounts: genreCounts)
                                .frame(height: 200)
                                .padding(.horizontal)
                        }
                    }

                    // Top Valuable Records
                    if !topRecords.isEmpty {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Most Valuable")
                                .font(.headline)
                                .padding(.horizontal)

                            ForEach(topRecords) { record in
                                HStack {
                                    AsyncImage(url: URL(string: record.coverImageURL ?? "")) { phase in
                                        switch phase {
                                        case .success(let image):
                                            image
                                                .resizable()
                                                .aspectRatio(contentMode: .fill)
                                                .frame(width: 40, height: 40)
                                                .clipShape(RoundedRectangle(cornerRadius: 6))
                                        default:
                                            RoundedRectangle(cornerRadius: 6)
                                                .fill(Color.gray.opacity(0.2))
                                                .frame(width: 40, height: 40)
                                                .overlay {
                                                    Image(systemName: "music.note")
                                                        .foregroundStyle(.gray)
                                                }
                                        }
                                    }
                                    .frame(width: 40, height: 40)

                                    VStack(alignment: .leading) {
                                        Text(record.title)
                                            .font(.subheadline)
                                            .lineLimit(1)
                                        Text(record.artist)
                                            .font(.caption)
                                            .foregroundStyle(.secondary)
                                            .lineLimit(1)
                                    }

                                    Spacer()

                                    Text(formatCurrency(record.marketValue ?? 0))
                                        .font(.subheadline)
                                        .fontWeight(.semibold)
                                        .foregroundStyle(.green)
                                }
                                .padding(.horizontal)
                            }
                        }
                    }

                    // Actions
                    VStack(spacing: 12) {
                        Button {
                            exportCollection()
                        } label: {
                            Label("Export Collection (CSV)", systemImage: "square.and.arrow.up")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .padding(.horizontal)
                    }
                    .padding(.top)
                }
                .padding(.vertical)
            }
            .navigationTitle("Statistics")
        }
    }

    private var genreCounts: [(String, Int)] {
        var counts: [String: Int] = [:]

        for record in collectionManager.records {
            for genre in record.genre {
                counts[genre, default: 0] += 1
            }
        }

        return counts.sorted { $0.1 > $1.1 }
    }

    private var topRecords: [VinylRecord] {
        collectionManager.records
            .filter { $0.marketValue != nil && $0.marketValue! > 0 }
            .sorted { ($0.marketValue ?? 0) > ($1.marketValue ?? 0) }
            .prefix(5)
            .map { $0 }
    }

    private func formatCurrency(_ value: Double) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.currencyCode = "USD"
        return formatter.string(from: NSNumber(value: value)) ?? "$0.00"
    }

    private func exportCollection() {
        let csv = collectionManager.exportCollection()
        // In a real app, you'd use UIActivityViewController to share
        print(csv)
    }
}

struct StatCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .foregroundStyle(color)
                Spacer()
            }

            Text(value)
                .font(.title2)
                .fontWeight(.bold)

            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

struct GenreChart: View {
    let genreCounts: [(String, Int)]

    var total: Int {
        genreCounts.map { $0.1 }.reduce(0, +)
    }

    var body: some View {
        GeometryReader { geometry in
            HStack(alignment: .bottom, spacing: 2) {
                ForEach(Array(genreCounts.prefix(6).enumerated()), id: \.offset) { index, item in
                    let percentage = Double(item.1) / Double(total)

                    VStack(spacing: 4) {
                        RoundedRectangle(cornerRadius: 4)
                            .fill(barColor(for: index))
                            .frame(width: geometry.size.width / CGFloat(min(genreCounts.count, 6)) - 8,
                                   height: geometry.size.height * percentage)
                            .animation(.easeInOut(duration: 0.5), value: percentage)

                        Text(item.0)
                            .font(.system(size: 8))
                            .lineLimit(1)
                            .frame(width: geometry.size.width / CGFloat(min(genreCounts.count, 6)) - 8)
                    }
                }
            }
        }
    }

    private func barColor(for index: Int) -> Color {
        let colors: [Color] = [.blue, .green, .orange, .red, .purple, .cyan]
        return colors[index % colors.count]
    }
}

#Preview {
    StatsView()
        .environmentObject(CollectionManager())
}
