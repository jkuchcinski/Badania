package com.decentcode.badaniaapp.viewmodels

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.decentcode.badaniaapp.models.Badanie
import com.decentcode.badaniaapp.models.CSVParser
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

/**
 * ViewModel zarządzający listą wszystkich badań i wyszukiwaniem
 */
class BadaniaViewModel(application: Application) : AndroidViewModel(application) {
    private val _wszystkieBadania = MutableStateFlow<List<Badanie>>(emptyList())
    val wszystkieBadania: StateFlow<List<Badanie>> = _wszystkieBadania.asStateFlow()
    
    private val _filtrowaneBadania = MutableStateFlow<List<Badanie>>(emptyList())
    val filtrowaneBadania: StateFlow<List<Badanie>> = _filtrowaneBadania.asStateFlow()
    
    private val _searchText = MutableStateFlow("")
    val searchText: StateFlow<String> = _searchText.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()
    
    private var searchJob: Job? = null
    
    init {
        setupSearchFilter()
        loadBadania()
    }
    
    /**
     * Wczytuje badania z pliku CSV
     */
    fun loadBadania() {
        _isLoading.value = true
        _errorMessage.value = null
        
        viewModelScope.launch {
            CSVParser.parseCSV(getApplication()).fold(
                onSuccess = { badania ->
                    _wszystkieBadania.value = badania
                    _filtrowaneBadania.value = filterBadania(_searchText.value)
                    _isLoading.value = false
                },
                onFailure = { error ->
                    _isLoading.value = false
                    _errorMessage.value = "Błąd podczas wczytywania danych: ${error.message}"
                }
            )
        }
    }
    
    /**
     * Aktualizuje tekst wyszukiwania
     */
    fun updateSearchText(text: String) {
        _searchText.value = text
    }
    
    /**
     * Konfiguruje filtrowanie w czasie rzeczywistym podczas wpisywania z debounce
     */
    private fun setupSearchFilter() {
        // Debounce będzie obsługiwany przez updateSearchText
    }
    
    /**
     * Filtruje badania na podstawie tekstu wyszukiwania (case-insensitive)
     */
    private fun filterBadania(searchText: String): List<Badanie> {
        if (searchText.isEmpty()) {
            return _wszystkieBadania.value
        }
        
        val lowercasedSearch = searchText.lowercase()
        return _wszystkieBadania.value.filter { badanie ->
            badanie.nazwa.lowercase().contains(lowercasedSearch) ||
            badanie.kod.lowercase().contains(lowercasedSearch)
        }
    }
    
    /**
     * Aktualizuje filtrowane badania z debounce
     */
    fun performSearch() {
        searchJob?.cancel()
        searchJob = viewModelScope.launch {
            delay(300) // Debounce 300ms
            _filtrowaneBadania.value = filterBadania(_searchText.value)
        }
    }
}

