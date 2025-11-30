//
//  MainTabView.swift
//  BadaniaApp
//
//  Główna nawigacja aplikacji z TabView
//

import SwiftUI

struct MainTabView: View {
    @StateObject private var selectedViewModel = SelectedBadaniaViewModel()
    
    var body: some View {
        TabView {
            SearchView(selectedViewModel: selectedViewModel)
                .tabItem {
                    Label("Wyszukiwanie", systemImage: "magnifyingglass")
                }
            
            Group {
                SelectedBadaniaView(viewModel: selectedViewModel)
                    .tabItem {
                        Label("Wybrane", systemImage: "list.bullet")
                    }
            }
            .badge(selectedViewModel.liczbaWybranych > 0 ? selectedViewModel.liczbaWybranych : 0)
        }
        .accentColor(Color(hex: "1976d2"))
    }
}
