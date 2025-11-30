//
//  SearchView.swift
//  BadaniaApp
//
//  Ekran wyszukiwania badań
//

import SwiftUI

struct SearchView: View {
    @StateObject private var viewModel = BadaniaViewModel()
    @ObservedObject var selectedViewModel: SelectedBadaniaViewModel
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Search Bar
                SearchBar(text: $viewModel.searchText)
                    .padding(.horizontal)
                    .padding(.vertical, 8)
                
                // Lista badań
                if viewModel.isLoading {
                    ProgressView("Ładowanie badań...")
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if let errorMessage = viewModel.errorMessage {
                    VStack(spacing: 16) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.system(size: 50))
                            .foregroundColor(.orange)
                        Text(errorMessage)
                            .font(.body)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                        
                        Button("Spróbuj ponownie") {
                            viewModel.loadBadania()
                        }
                        .buttonStyle(.borderedProminent)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if viewModel.filtrowaneBadania.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "magnifyingglass")
                            .font(.system(size: 50))
                            .foregroundColor(.secondary)
                        Text(viewModel.searchText.isEmpty ? "Brak badań" : "Nie znaleziono badań")
                            .font(.headline)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    List(viewModel.filtrowaneBadania) { badanie in
                        BadanieRowView(badanie: badanie) {
                            selectedViewModel.dodajBadanie(badanie)
                        }
                        .listRowSeparator(.visible)
                    }
                    .listStyle(.plain)
                }
            }
            .navigationTitle("Wyszukiwanie")
            .navigationBarTitleDisplayMode(.large)
        }
    }
}

// Komponent wiersza badania
struct BadanieRowView: View {
    let badanie: Badanie
    let onAdd: () -> Void
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(badanie.nazwa)
                    .font(.title3)
                    .foregroundColor(.accentColor)
                
                HStack(spacing: 12) {
                    Text("Kod: \(badanie.kod)")
                        .font(.caption)
                        .foregroundColor(.primary)
                    
                    if let kwota = badanie.kwota {
                        Text(badanie.formattedKwota)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .fontWeight(.medium)
                    } else {
                        Text("Brak ceny")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            
            Spacer()
            
            Button(action: {
                // Haptic feedback
                let generator = UIImpactFeedbackGenerator(style: .light)
                generator.impactOccurred()
                onAdd()
            }) {
                Image(systemName: "plus.circle.fill")
                    .font(.system(size: 28))
                    .foregroundColor(Color(hex: "1976d2"))
            }
            .buttonStyle(.plain)
        }
        .padding(.vertical, 4)
    }
}

// Komponent Search Bar
struct SearchBar: View {
    @Binding var text: String
    
    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.secondary)
            
            TextField("Szukaj badań...", text: $text)
                .textFieldStyle(.plain)
            
            if !text.isEmpty {
                Button(action: { text = "" }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(Color(.systemGray6))
        .cornerRadius(10)
    }
}

