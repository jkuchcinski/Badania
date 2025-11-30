//
//  SelectedBadaniaView.swift
//  BadaniaApp
//
//  Ekran z tabelą wybranych badań
//

import SwiftUI

struct SelectedBadaniaView: View {
    @ObservedObject var viewModel: SelectedBadaniaViewModel
    
    var body: some View {
        NavigationView {
            ZStack {
                VStack(spacing: 0) {
                    // Lista wybranych badań
                    if viewModel.wybraneBadania.isEmpty {
                        VStack(spacing: 16) {
                            Image(systemName: "list.bullet.rectangle")
                                .font(.system(size: 50))
                                .foregroundColor(.secondary)
                            Text("Brak wybranych badań")
                                .font(.headline)
                                .foregroundColor(.secondary)
                            Text("Dodaj badania z zakładki Wyszukiwanie")
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .multilineTextAlignment(.center)
                        }
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                    } else {
                        List {
                            ForEach(viewModel.wybraneBadania) { wybrane in
                                WybraneBadanieRowView(wybrane: wybrane, viewModel: viewModel)
                                    .listRowSeparator(.visible)
                            }
                            .onDelete(perform: deleteBadania)
                        }
                        .listStyle(.plain)
                    }
                    
                    // Sticky footer z sumą
                    if !viewModel.wybraneBadania.isEmpty {
                        SumView(sum: viewModel.suma, formattedSum: viewModel.formattedSuma)
                            .background(Color(.systemBackground))
                            .shadow(color: .black.opacity(0.1), radius: 5, x: 0, y: -2)
                    }
                }
            }
            .navigationTitle("Wybrane badania")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                if !viewModel.wybraneBadania.isEmpty {
                    ToolbarItem(placement: .navigationBarTrailing) {
                        Button(action: {
                            viewModel.usunWszystkie()
                        }) {
                            Label("Usuń wszystkie", systemImage: "trash")
                        }
                    }
                }
            }
        }
    }
    
    private func deleteBadania(at offsets: IndexSet) {
        for index in offsets {
            let wybrane = viewModel.wybraneBadania[index]
            viewModel.usunBadanie(wybrane)
        }
    }
}

// Komponent wiersza wybranego badania
struct WybraneBadanieRowView: View {
    let wybrane: WybraneBadanie
    @ObservedObject var viewModel: SelectedBadaniaViewModel
    
    var body: some View {
        
        
        VStack {
            HStack {
                Text(wybrane.badanie.nazwa)
                    .font(.title3)
                    //.fontWeight(.bold)
                    .foregroundColor(.accentColor)
                Spacer()
            }
            
            HStack(spacing: 4) {
                //VStack(alignment: .leading, spacing: 4) {
                
                VStack(alignment: .leading, spacing: 4) {

                    HStack() {
                        
                        VStack(alignment: .leading) {
                            Text("Kod:")
                                .font(.caption)
                                //.fontWeight(.bold)
                                .foregroundColor(.primary)
                            Text("\(wybrane.badanie.kod)")
                                .font(.title2)
                                .fontWeight(.bold)
                                .foregroundColor(.primary)
                            if let kwota = wybrane.badanie.kwota {
                                Text("\(wybrane.badanie.formattedKwota) × \(wybrane.ilosc)")
                                    .font(.footnote)
                                    .foregroundColor(.secondary).padding(.bottom, 4)
                            }

                        }
                        //Spacer()

                    }
                }
                //}
                
                Spacer()
                
                // Kontrolki ilości
                HStack(spacing: 8) {
                    Button(action: {
                        let generator = UIImpactFeedbackGenerator(style: .light)
                        generator.impactOccurred()
                        viewModel.zmniejszIlosc(wybrane)
                    }) {
                        Image(systemName: "minus.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(Color(hex: "1976d2"))
                    }
                    .buttonStyle(.plain)
                    
                    Text("\(wybrane.ilosc)")
                        .font(.headline)
                        .frame(minWidth: 30)
                        .foregroundColor(.primary)
                    
                    Button(action: {
                        let generator = UIImpactFeedbackGenerator(style: .light)
                        generator.impactOccurred()
                        viewModel.zwiekszIlosc(wybrane)
                    }) {
                        Image(systemName: "plus.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(Color(hex: "1976d2"))
                    }
                    .buttonStyle(.plain)
                }
                
                // Całkowita kwota
                VStack(alignment: .trailing, spacing: 2) {
                    Text(wybrane.formattedCalkowitaKwota)
                        .font(.headline)
                        .foregroundColor(.accentColor)
                }
                .frame(width: 110, alignment: .trailing)
            }
            .padding(.vertical, 4)
        }
    }
}

