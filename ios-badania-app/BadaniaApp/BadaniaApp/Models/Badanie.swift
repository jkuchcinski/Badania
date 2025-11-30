//
//  Badanie.swift
//  BadaniaApp
//
//  Model danych badania lekarskiego
//

import Foundation

struct Badanie: Identifiable, Codable, Equatable {
    let id: UUID
    let kod: String
    let nazwa: String
    let kwota: Double?
    
    init(id: UUID = UUID(), kod: String, nazwa: String, kwota: Double?) {
        self.id = id
        self.kod = kod
        self.nazwa = nazwa
        self.kwota = kwota
    }
    
    /// Formatuje kwotę do wyświetlania w formacie "X,XX zł"
    var formattedKwota: String {
        guard let kwota = kwota else {
            return "-"
        }
        return String(format: "%.2f", kwota).replacingOccurrences(of: ".", with: ",") + " zł"
    }
}

/// Reprezentuje wybrane badanie z ilością
struct WybraneBadanie: Identifiable, Equatable {
    let id: UUID
    let badanie: Badanie
    var ilosc: Int
    
    init(id: UUID = UUID(), badanie: Badanie, ilosc: Int = 1) {
        self.id = id
        self.badanie = badanie
        self.ilosc = ilosc
    }
    
    /// Oblicza całkowitą kwotę dla tego badania (kwota * ilość)
    var calkowitaKwota: Double {
        guard let kwota = badanie.kwota else {
            return 0.0
        }
        return kwota * Double(ilosc)
    }
    
    /// Formatuje całkowitą kwotę do wyświetlania
    var formattedCalkowitaKwota: String {
        return String(format: "%.2f", calkowitaKwota).replacingOccurrences(of: ".", with: ",") + " zł"
    }
}

