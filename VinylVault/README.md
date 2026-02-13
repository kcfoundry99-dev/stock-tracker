# Vinyl Vault 🎵

A beautiful iOS app for managing your vinyl record collection. Take photos of your records, search Discogs database, track values, and organize your collection.

![Vinyl Vault](https://img.shields.io/badge/iOS-16.0+-blue.svg)
![Swift](https://img.shields.io/badge/Swift-5.9-orange.svg)
![Xcode](https://img.shields.io/badge/Xcode-15.0+-blue.svg)

## Features

- 📸 **Scan Records** - Photograph album covers and record labels
- 🔍 **Search Discogs** - Database integration for finding release info
- 💰 **Track Values** - Monitor your collection's market value
- ❤️ **Wishlist** - Keep track of records you want
- 📊 **Statistics** - Visualize your collection by genre and value
- 📤 **Export** - Export collection to CSV

## Setup Instructions

### Prerequisites

1. **Mac** - Any Mac from 2017 or later
2. **Xcode 15+** - Free from the Mac App Store
3. **Apple Developer Account** - $99/year (required for app installation on device)

### Step 1: Install XcodeGen

```bash
brew install xcodegen
```

### Step 2: Get Discogs API Credentials

1. Go to [Discogs Developers](https://www.discogs.com/developers/)
2. Click "Create an Application"
3. Fill in the application details
4. Copy your **Consumer Key** and **Consumer Secret**

### Step 3: Configure API Credentials

Open `VinylVault/Sources/Services/DiscogsService.swift` and replace:

```swift
enum Secrets {
    static let discogsKey = "YOUR_CONSUMER_KEY"
    static let discogsSecret = "YOUR_CONSUMER_SECRET"
}
```

With your actual credentials from Discogs.

### Step 4: Generate Xcode Project

```bash
cd VinylVault
xcodegen generate
```

### Step 5: Open and Run

```bash
open VinylVault.xcodeproj
```

1. Select a simulator or your device
2. Press `Cmd + R` to build and run

## App Structure

```
VinylVault/
├── project.yml              # XcodeGen configuration
├── VinylVault/
│   ├── Sources/
│   │   ├── App/
│   │   │   └── VinylVaultApp.swift      # App entry point
│   │   ├── Models/
│   │   │   └── VinylRecord.swift         # Data models
│   │   ├── Services/
│   │   │   ├── DiscogsService.swift      # API integration
│   │   │   └── CollectionManager.swift   # Data management
│   │   └── Views/
│   │       ├── ContentView.swift          # Tab navigation
│   │       ├── CollectionView.swift       # Main collection
│   │       ├── SearchView.swift          # Discogs search
│   │       ├── AddRecordView.swift        # Add new records
│   │       ├── RecordDetailView.swift     # Record details
│   │       ├── WishlistView.swift         # Wishlist management
│   │       ├── StatsView.swift            # Statistics & charts
│   │       └── SearchResultDetailView.swift
│   └── Resources/
│       ├── Info.plist
│       └── Assets.xcassets/
```

## Usage

### Adding Records

1. Tap the **+** button in Collection view
2. Enter basic info (title, artist, year)
3. Optionally add photos of cover and label
4. Set condition and values
5. Save to collection or wishlist

### Searching Discogs

1. Go to **Search** tab
2. Enter artist, album, or title
3. Tap search to browse results
4. Tap a result to see details
5. Add directly to collection or wishlist

### Viewing Statistics

- **Total Records** - Number of records in collection
- **Total Value** - Sum of market values
- **Average Value** - Mean value per record
- **Genre Distribution** - Visual chart of genres

## Technologies Used

- **SwiftUI** - Modern declarative UI framework
- **Async/Action** - Concurrency handling
- **Core Image** - Image processing
- **Discogs API** - Music database
- **Swift Charts** - Statistics visualization (iOS 16+)
- **PhotosUI** - Image picker

## Troubleshooting

### "No such module" error
Make sure you've generated the project with XcodeGen:
```bash
xcodegen generate
```

### Photos not saving
Check that you've granted Camera and Photo Library permissions in Settings.

### Discogs API errors
Verify your API credentials are correct and haven't expired.

## Future Enhancements

- [ ] Barcode scanning for faster lookup
- [ ] Cloud sync across devices
- [ ] Collection sharing with friends
- [ ] Price alerts
- [ ] Wantlist integration
- [ ] Multiple image support per record

## License

MIT License - Feel free to use and modify!

## Contributing

Pull requests welcome! For major changes, please open an issue first.

---

Made with ❤️ for vinyl enthusiasts
