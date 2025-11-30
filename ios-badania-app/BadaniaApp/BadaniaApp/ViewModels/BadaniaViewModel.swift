//
//  BadaniaViewModel.swift
//  BadaniaApp
//
//  ViewModel zarządzający listą wszystkich badań i wyszukiwaniem
//

import Foundation
import Combine

@MainActor
class BadaniaViewModel: ObservableObject {
    @Published var wszystkieBadania: [Badanie] = []
    @Published var filtrowaneBadania: [Badanie] = []
    @Published var searchText: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        setupSearchFilter()
        loadBadania()
    }
    
    /// Wczytuje badania z pliku CSV
    func loadBadania() {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                let badania = try CSVParser.parseCSV()
                await MainActor.run {
                    self.wszystkieBadania = badania.sorted { $0.nazwa.lowercased() < $1.nazwa.lowercased() }
                    // Zaktualizuj filtrowane badania po załadowaniu
                    self.filtrowaneBadania = self.filterBadania(searchText: self.searchText)
                    self.isLoading = false
                }
            } catch {
                await MainActor.run {
                    self.isLoading = false
                    self.errorMessage = "Błąd podczas wczytywania danych: \(error.localizedDescription)"
                }
            }
        }
    }
    
    /// Konfiguruje filtrowanie w czasie rzeczywistym podczas wpisywania
    private func setupSearchFilter() {
        $searchText
            .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
            .map { [weak self] searchText in
                self?.filterBadania(searchText: searchText) ?? []
            }
            .assign(to: &$filtrowaneBadania)
    }
    
    /// Filtruje badania na podstawie tekstu wyszukiwania (case-insensitive)
    private func filterBadania(searchText: String) -> [Badanie] {
        if searchText.isEmpty {
            return wszystkieBadania
        }
        
        let lowercasedSearch = searchText.lowercased()
        return wszystkieBadania.filter { badanie in
            badanie.nazwa.lowercased().contains(lowercasedSearch) ||
            badanie.kod.lowercased().contains(lowercasedSearch)
        }
    }
}

