package com.decentcode.badaniaapp.viewmodels

import androidx.lifecycle.ViewModel
import com.decentcode.badaniaapp.models.Badanie
import com.decentcode.badaniaapp.models.WybraneBadanie
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

/**
 * ViewModel zarządzający wybranymi badaniami i sumą
 */
class SelectedBadaniaViewModel : ViewModel() {
    private val _wybraneBadania = MutableStateFlow<List<WybraneBadanie>>(emptyList())
    val wybraneBadania: StateFlow<List<WybraneBadanie>> = _wybraneBadania.asStateFlow()
    
    /**
     * Oblicza sumę wszystkich wybranych badań
     */
    val suma: Double
        get() = _wybraneBadania.value.sumOf { it.calkowitaKwota() }
    
    /**
     * Formatuje sumę do wyświetlania
     */
    val formattedSuma: String
        get() = String.format("%.2f", suma).replace(".", ",") + " zł"
    
    /**
     * Liczba wybranych badań
     */
    val liczbaWybranych: Int
        get() = _wybraneBadania.value.size
    
    /**
     * Dodaje badanie do listy wybranych
     * Jeśli badanie już istnieje, zwiększa ilość
     */
    fun dodajBadanie(badanie: Badanie) {
        _wybraneBadania.update { currentList ->
            val existingIndex = currentList.indexOfFirst { it.badanie.id == badanie.id }
            if (existingIndex != -1) {
                // Badanie już istnieje - zwiększ ilość
                currentList.toMutableList().apply {
                    this[existingIndex] = this[existingIndex].copy(ilosc = this[existingIndex].ilosc + 1)
                }
            } else {
                // Nowe badanie - dodaj do listy
                currentList + WybraneBadanie(badanie = badanie, ilosc = 1)
            }
        }
    }
    
    /**
     * Usuwa badanie z listy wybranych
     */
    fun usunBadanie(wybraneBadanie: WybraneBadanie) {
        _wybraneBadania.update { currentList ->
            currentList.filter { it.id != wybraneBadanie.id }
        }
    }
    
    /**
     * Usuwa wszystkie wybrane badania
     */
    fun usunWszystkie() {
        _wybraneBadania.value = emptyList()
    }
    
    /**
     * Zmniejsza ilość badania o 1, lub usuwa jeśli ilość = 1
     */
    fun zmniejszIlosc(wybraneBadanie: WybraneBadanie) {
        _wybraneBadania.update { currentList ->
            val index = currentList.indexOfFirst { it.id == wybraneBadanie.id }
            if (index != -1) {
                val current = currentList[index]
                if (current.ilosc > 1) {
                    currentList.toMutableList().apply {
                        this[index] = current.copy(ilosc = current.ilosc - 1)
                    }
                } else {
                    currentList.filter { it.id != wybraneBadanie.id }
                }
            } else {
                currentList
            }
        }
    }
    
    /**
     * Zwiększa ilość badania o 1
     */
    fun zwiekszIlosc(wybraneBadanie: WybraneBadanie) {
        _wybraneBadania.update { currentList ->
            val index = currentList.indexOfFirst { it.id == wybraneBadanie.id }
            if (index != -1) {
                val current = currentList[index]
                currentList.toMutableList().apply {
                    this[index] = current.copy(ilosc = current.ilosc + 1)
                }
            } else {
                currentList
            }
        }
    }
}

