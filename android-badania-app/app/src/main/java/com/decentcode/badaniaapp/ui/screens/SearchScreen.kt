package com.decentcode.badaniaapp.ui.screens

import android.os.VibrationEffect
import android.os.Vibrator
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.decentcode.badaniaapp.R
import com.decentcode.badaniaapp.ui.components.BadanieRow
import com.decentcode.badaniaapp.ui.components.SearchBar
import com.decentcode.badaniaapp.viewmodels.BadaniaViewModel
import com.decentcode.badaniaapp.viewmodels.SelectedBadaniaViewModel

/**
 * Ekran wyszukiwania badań
 */
@Composable
fun SearchScreen(
    selectedViewModel: SelectedBadaniaViewModel,
    viewModel: BadaniaViewModel = viewModel()
) {
    val context = LocalContext.current
    val searchText by viewModel.searchText.collectAsState()
    val filtrowaneBadania by viewModel.filtrowaneBadania.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()
    
    // Obsługa debounce dla wyszukiwania
    LaunchedEffect(searchText) {
        viewModel.performSearch()
    }
    
    Column(
        modifier = Modifier.fillMaxSize()
    ) {
        // Search Bar
        SearchBar(
            text = searchText,
            onTextChange = { text ->
                viewModel.updateSearchText(text)
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 8.dp),
            placeholder = stringResource(R.string.search_placeholder)
        )
        
        // Lista badań
        when {
            isLoading -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        CircularProgressIndicator()
                        Text(stringResource(R.string.loading))
                    }
                }
            }
            errorMessage != null -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(16.dp),
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Search,
                            contentDescription = null,
                            modifier = Modifier.size(50.dp),
                            tint = MaterialTheme.colorScheme.error
                        )
                        Text(
                            text = errorMessage ?: stringResource(R.string.error_loading),
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Button(onClick = { viewModel.loadBadania() }) {
                            Text(stringResource(R.string.try_again))
                        }
                    }
                }
            }
            filtrowaneBadania.isEmpty() -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Search,
                            contentDescription = null,
                            modifier = Modifier.size(50.dp),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = if (searchText.isEmpty()) {
                                stringResource(R.string.no_badania)
                            } else {
                                stringResource(R.string.no_results)
                            },
                            style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
            else -> {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(vertical = 8.dp)
                ) {
                    items(filtrowaneBadania) { badanie ->
                        BadanieRow(
                            badanie = badanie,
                            onAdd = {
                                // Haptic feedback
                                val vibrator = context.getSystemService(Vibrator::class.java)
                                vibrator?.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_CLICK))
                                
                                selectedViewModel.dodajBadanie(badanie)
                            }
                        )
                        HorizontalDivider(modifier = Modifier.padding(horizontal = 16.dp))
                    }
                }
            }
        }
    }
}

