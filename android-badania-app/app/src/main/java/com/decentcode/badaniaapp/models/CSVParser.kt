package com.decentcode.badaniaapp.models

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader

/**
 * Parser pliku CSV z badaniami
 */
object CSVParser {
    /**
     * Parsuje plik CSV z assets aplikacji
     * @param context Kontekst aplikacji do dostępu do assets
     * @param filename Nazwa pliku CSV (bez rozszerzenia)
     * @return Lista obiektów Badanie
     */
    suspend fun parseCSV(context: Context, filename: String = "badania"): Result<List<Badanie>> {
        return withContext(Dispatchers.IO) {
            try {
                val inputStream = context.assets.open("$filename.csv")
                val reader = BufferedReader(InputStreamReader(inputStream, "UTF-8"))
                
                val badania = mutableListOf<Badanie>()
                
                // Pomijamy nagłówek (pierwsza linia)
                reader.readLine()
                
                reader.useLines { lines ->
                    lines.forEach { line ->
                        val trimmedLine = line.trim()
                        if (trimmedLine.isEmpty()) return@forEach
                        
                        // CSV używa średnika jako separatora
                        val columns = trimmedLine.split(";")
                        
                        if (columns.size >= 3) {
                            val kod = columns[0].trim()
                            val nazwa = columns[1].trim()
                            val kwotaStr = columns[2].trim()
                            
                            // Pomijamy wiersze bez nazwy badania
                            if (nazwa.isEmpty()) return@forEach
                            
                            // Parsuj kwotę (format: "2,00" -> 2.0)
                            val kwota = parseKwota(kwotaStr)
                            
                            val badanie = Badanie(kod = kod, nazwa = nazwa, kwota = kwota)
                            badania.add(badanie)
                        }
                    }
                }
                
                Result.success(badania.sortedBy { it.nazwa.lowercase() })
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
    
    /**
     * Parsuje kwotę z formatu polskiego (przecinek jako separator dziesiętny)
     * @param kwotaStr String z kwotą w formacie "2,00" lub "150,00"
     * @return Double lub null jeśli nie można sparsować
     */
    private fun parseKwota(kwotaStr: String): Double? {
        val trimmed = kwotaStr.trim()
        if (trimmed.isEmpty()) return null
        
        // Zamień przecinek na kropkę
        val normalized = trimmed.replace(",", ".")
        
        return try {
            normalized.toDouble()
        } catch (e: NumberFormatException) {
            null
        }
    }
}

