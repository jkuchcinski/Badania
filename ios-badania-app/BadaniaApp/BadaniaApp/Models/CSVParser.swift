//
//  CSVParser.swift
//  BadaniaApp
//
//  Parser pliku CSV z badaniami
//

import Foundation

enum CSVParserError: Error {
    case fileNotFound
    case invalidFormat
    case encodingError
}

class CSVParser {
    /// Parsuje plik CSV z bundle aplikacji
    /// - Parameter filename: Nazwa pliku CSV (bez rozszerzenia)
    /// - Returns: Tablica obiektów Badanie
    static func parseCSV(from filename: String = "badania") throws -> [Badanie] {
        guard let path = Bundle.main.path(forResource: filename, ofType: "csv") else {
            throw CSVParserError.fileNotFound
        }
        
        guard let content = try? String(contentsOfFile: path, encoding: .utf8) else {
            throw CSVParserError.encodingError
        }
        
        let lines = content.components(separatedBy: .newlines)
        guard lines.count > 1 else {
            throw CSVParserError.invalidFormat
        }
        
        // Pomijamy nagłówek (pierwsza linia)
        let dataLines = Array(lines.dropFirst())
        
        var badania: [Badanie] = []
        
        for line in dataLines {
            let trimmedLine = line.trimmingCharacters(in: .whitespacesAndNewlines)
            if trimmedLine.isEmpty {
                continue
            }
            
            // CSV używa średnika jako separatora
            let columns = trimmedLine.components(separatedBy: ";")
            
            guard columns.count >= 3 else {
                continue
            }
            
            let kod = columns[0].trimmingCharacters(in: .whitespacesAndNewlines)
            let nazwa = columns[1].trimmingCharacters(in: .whitespacesAndNewlines)
            let kwotaStr = columns[2].trimmingCharacters(in: .whitespacesAndNewlines)
            
            // Pomijamy wiersze bez nazwy badania
            if nazwa.isEmpty {
                continue
            }
            
            // Parsuj kwotę (format: "2,00" -> 2.0)
            let kwota: Double? = parseKwota(kwotaStr)
            
            let badanie = Badanie(kod: kod, nazwa: nazwa, kwota: kwota)
            badania.append(badanie)
        }
        
        return badania
    }
    
    /// Parsuje kwotę z formatu polskiego (przecinek jako separator dziesiętny)
    /// - Parameter kwotaStr: String z kwotą w formacie "2,00" lub "150,00"
    /// - Returns: Double lub nil jeśli nie można sparsować
    private static func parseKwota(_ kwotaStr: String) -> Double? {
        let trimmed = kwotaStr.trimmingCharacters(in: .whitespacesAndNewlines)
        
        if trimmed.isEmpty {
            return nil
        }
        
        // Zamień przecinek na kropkę
        let normalized = trimmed.replacingOccurrences(of: ",", with: ".")
        
        return Double(normalized)
    }
}

