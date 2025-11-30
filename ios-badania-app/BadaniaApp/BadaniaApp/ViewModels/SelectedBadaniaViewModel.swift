//
//  SelectedBadaniaViewModel.swift
//  BadaniaApp
//
//  ViewModel zarządzający wybranymi badaniami i sumą
//

import Foundation
import Combine

@MainActor
class SelectedBadaniaViewModel: ObservableObject {
    @Published var wybraneBadania: [WybraneBadanie] = []
    
    /// Oblicza sumę wszystkich wybranych badań
    var suma: Double {
        wybraneBadania.reduce(0.0) { $0 + $1.calkowitaKwota }
    }
    
    /// Formatuje sumę do wyświetlania
    var formattedSuma: String {
        String(format: "%.2f", suma).replacingOccurrences(of: ".", with: ",") + " zł"
    }
    
    /// Liczba wybranych badań
    var liczbaWybranych: Int {
        wybraneBadania.count
    }
    
    /// Dodaje badanie do listy wybranych
    /// Jeśli badanie już istnieje, zwiększa ilość
    func dodajBadanie(_ badanie: Badanie) {
        if let index = wybraneBadania.firstIndex(where: { $0.badanie.id == badanie.id }) {
            // Badanie już istnieje - zwiększ ilość
            wybraneBadania[index].ilosc += 1
        } else {
            // Nowe badanie - dodaj do listy
            let wybrane = WybraneBadanie(badanie: badanie, ilosc: 1)
            wybraneBadania.append(wybrane)
        }
    }
    
    /// Usuwa badanie z listy wybranych
    func usunBadanie(_ wybraneBadanie: WybraneBadanie) {
        wybraneBadania.removeAll { $0.id == wybraneBadanie.id }
    }
    
    /// Usuwa wszystkie wybrane badania
    func usunWszystkie() {
        wybraneBadania.removeAll()
    }
    
    /// Zmniejsza ilość badania o 1, lub usuwa jeśli ilość = 1
    func zmniejszIlosc(_ wybraneBadanie: WybraneBadanie) {
        if let index = wybraneBadania.firstIndex(where: { $0.id == wybraneBadanie.id }) {
            if wybraneBadania[index].ilosc > 1 {
                wybraneBadania[index].ilosc -= 1
            } else {
                usunBadanie(wybraneBadanie)
            }
        }
    }
    
    /// Zwiększa ilość badania o 1
    func zwiekszIlosc(_ wybraneBadanie: WybraneBadanie) {
        if let index = wybraneBadania.firstIndex(where: { $0.id == wybraneBadanie.id }) {
            wybraneBadania[index].ilosc += 1
        }
    }
}

