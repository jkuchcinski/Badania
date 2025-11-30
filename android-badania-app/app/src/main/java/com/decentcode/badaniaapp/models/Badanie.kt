package com.decentcode.badaniaapp.models

import java.util.UUID

/**
 * Model danych badania lekarskiego
 */
data class Badanie(
    val id: String = UUID.randomUUID().toString(),
    val kod: String,
    val nazwa: String,
    val kwota: Double?
) {
    /**
     * Formatuje kwotę do wyświetlania w formacie "X,XX zł"
     */
    fun formattedKwota(): String {
        return kwota?.let {
            String.format("%.2f", it).replace(".", ",") + " zł"
        } ?: "-"
    }
}

/**
 * Reprezentuje wybrane badanie z ilością
 */
data class WybraneBadanie(
    val id: String = UUID.randomUUID().toString(),
    val badanie: Badanie,
    var ilosc: Int = 1
) {
    /**
     * Oblicza całkowitą kwotę dla tego badania (kwota * ilość)
     */
    fun calkowitaKwota(): Double {
        return badanie.kwota?.let { it * ilosc } ?: 0.0
    }

    /**
     * Formatuje całkowitą kwotę do wyświetlania
     */
    fun formattedCalkowitaKwota(): String {
        return String.format("%.2f", calkowitaKwota()).replace(".", ",") + " zł"
    }
}

