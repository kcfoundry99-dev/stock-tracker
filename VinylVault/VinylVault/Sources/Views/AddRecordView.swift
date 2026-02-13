import SwiftUI
import PhotosUI

struct AddRecordView: View {
    @EnvironmentObject var collectionManager: CollectionManager
    @Environment(\.dismiss) private var dismiss

    @State private var title = ""
    @State private var artist = ""
    @State private var year = ""
    @State private var genre = ""
    @State private var label = ""
    @State private var catalogNumber = ""
    @State private var condition: RecordCondition = .good
    @State private var purchasePrice = ""
    @State private var marketValue = ""
    @State private var notes = ""
    @State private var isWishlist = false

    @State private var coverImage: UIImage?
    @State private var labelImage: UIImage?
    @State private var selectedCoverItem: PhotosPickerItem?
    @State private var selectedLabelItem: PhotosPickerItem?

    var body: some View {
        NavigationStack {
            Form {
                Section("Basic Info") {
                    TextField("Title", text: $title)
                    TextField("Artist", text: $artist)
                    TextField("Year", text: $year)
                        .keyboardType(.numberPad)
                    TextField("Genre (e.g., Jazz, Rock)", text: $genre)
                    TextField("Label", text: $label)
                    TextField("Catalog Number", text: $catalogNumber)
                }

                Section("Images") {
                    // Cover Image
                    HStack {
                        if let image = coverImage {
                            Image(uiImage: image)
                                .resizable()
                                .aspectRatio(contentMode: .fill)
                                .frame(width: 80, height: 80)
                                .clipShape(RoundedRectangle(cornerRadius: 8))
                        } else {
                            RoundedRectangle(cornerRadius: 8)
                                .fill(Color.gray.opacity(0.2))
                                .frame(width: 80, height: 80)
                                .overlay {
                                    Image(systemName: "camera.fill")
                                        .foregroundStyle(.gray)
                                }
                        }

                        PhotosPicker(selection: $selectedCoverItem, matching: .images) {
                            Label("Add Cover", systemImage: "photo")
                        }
                        .onChange(of: selectedCoverItem) { _, newValue in
                            Task {
                                if let data = try? await newValue?.loadTransferable(type: Data.self),
                                   let image = UIImage(data: data) {
                                    coverImage = image
                                }
                            }
                        }

                        Spacer()
                    }

                    // Label Image
                    HStack {
                        if let image = labelImage {
                            Image(uiImage: image)
                                .resizable()
                                .aspectRatio(contentMode: .fill)
                                .frame(width: 60, height: 60)
                                .clipShape(RoundedRectangle(cornerRadius: 8))
                        } else {
                            RoundedRectangle(cornerRadius: 8)
                                .fill(Color.gray.opacity(0.2))
                                .frame(width: 60, height: 60)
                                .overlay {
                                    Image(systemName: "tag.fill")
                                        .foregroundStyle(.gray)
                                }
                        }

                        PhotosPicker(selection: $selectedLabelItem, matching: .images) {
                            Label("Add Label", systemImage: "photo")
                        }
                        .onChange(of: selectedLabelItem) { _, newValue in
                            Task {
                                if let data = try? await newValue?.loadTransferable(type: Data.self),
                                   let image = UIImage(data: data) {
                                    labelImage = image
                                }
                            }
                        }

                        Spacer()
                    }
                }

                Section("Condition & Value") {
                    Picker("Condition", selection: $condition) {
                        ForEach(RecordCondition.allCases) { cond in
                            Text(cond.rawValue).tag(cond)
                        }
                    }

                    HStack {
                        Text("$")
                        TextField("Purchase Price", text: $purchasePrice)
                            .keyboardType(.decimalPad)
                    }

                    HStack {
                        Text("$")
                        TextField("Market Value", text: $marketValue)
                            .keyboardType(.decimalPad)
                    }
                }

                Section("Notes") {
                    TextEditor(text: $notes)
                        .frame(minHeight: 80)
                }

                Section {
                    Toggle("Add to Wishlist instead", isOn: $isWishlist)
                }
            }
            .navigationTitle("Add Record")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        saveRecord()
                    }
                    .disabled(title.isEmpty || artist.isEmpty)
                }
            }
        }
    }

    private func saveRecord() {
        let record = VinylRecord(
            title: title,
            artist: artist,
            year: Int(year),
            genre: genre.components(separatedBy: ",").map { $0.trimmingCharacters(in: .whitespaces) },
            label: label.isEmpty ? nil : label,
            catalogNumber: catalogNumber.isEmpty ? nil : catalogNumber,
            localCoverImageData: coverImage?.jpegData(compressionQuality: 0.8),
            localLabelImageData: labelImage?.jpegData(compressionQuality: 0.8),
            condition: condition,
            purchasePrice: Double(purchasePrice),
            marketValue: Double(marketValue),
            notes: notes,
            isWishlist: isWishlist
        )

        if isWishlist {
            collectionManager.addToWishlist(record)
        } else {
            collectionManager.addRecord(record)
        }

        dismiss()
    }
}

#Preview {
    AddRecordView()
        .environmentObject(CollectionManager())
}
