package com.decentcode.badaniaapp.utils

import androidx.compose.ui.graphics.Color

/**
 * Rozszerzenia kolorów - konwersja hex na Color
 */
fun Color(hex: String): Color {
    val hexColor = hex.trim().removePrefix("#")
    
    val a: Long
    val r: Long
    val g: Long
    val b: Long
    
    when (hexColor.length) {
        6 -> {
            a = 255
            r = hexColor.substring(0, 2).toLong(16)
            g = hexColor.substring(2, 4).toLong(16)
            b = hexColor.substring(4, 6).toLong(16)
        }
        8 -> {
            a = hexColor.substring(0, 2).toLong(16)
            r = hexColor.substring(2, 4).toLong(16)
            g = hexColor.substring(4, 6).toLong(16)
            b = hexColor.substring(6, 8).toLong(16)
        }
        else -> {
            a = 255
            r = 0
            g = 0
            b = 0
        }
    }
    
    return Color(
        red = r / 255f,
        green = g / 255f,
        blue = b / 255f,
        alpha = a / 255f
    )
}

