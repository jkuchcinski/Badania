package com.decentcode.badaniaapp.ui.screens

import android.os.VibrationEffect
import android.os.Vibrator
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.List
import androidx.compose.material3.*
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.decentcode.badaniaapp.R
import com.decentcode.badaniaapp.ui.components.SumView
import com.decentcode.badaniaapp.ui.components.WybraneBadanieRow
import com.decentcode.badaniaapp.viewmodels.SelectedBadaniaViewModel

/**
 * Ekran z listą wybranych badań
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SelectedBadaniaScreen(
    viewModel: SelectedBadaniaViewModel
) {
    val context = LocalContext.current
    val wybraneBadania by viewModel.wybraneBadania.collectAsState()
    val suma by remember { derivedStateOf { viewModel.suma } }
    val formattedSuma by remember { derivedStateOf { viewModel.formattedSuma } }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.selected_badania_title)) },
                actions = {
                    if (wybraneBadania.isNotEmpty()) {
                        IconButton(onClick = { viewModel.usunWszystkie() }) {
                            Icon(
                                imageVector = Icons.Default.Delete,
                                contentDescription = stringResource(R.string.delete_all)
                            )
                        }
                    }
                }
            )
        },
        bottomBar = {
            if (wybraneBadania.isNotEmpty()) {
                SumView(
                    sum = suma,
                    formattedSum = formattedSuma
                )
            }
        }
    ) { paddingValues ->
        if (wybraneBadania.isEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                    modifier = Modifier.padding(16.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.List,
                        contentDescription = null,
                        modifier = Modifier.size(50.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = stringResource(R.string.no_selected_badania),
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = stringResource(R.string.add_from_search),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentPadding = PaddingValues(vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(
                    items = wybraneBadania,
                    key = { it.id }
                ) { wybrane ->
                    WybraneBadanieRow(
                        wybrane = wybrane,
                        onDecrease = {
                            val vibrator = context.getSystemService(Vibrator::class.java)
                            vibrator?.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_CLICK))
                            viewModel.zmniejszIlosc(wybrane)
                        },
                        onIncrease = {
                            val vibrator = context.getSystemService(Vibrator::class.java)
                            vibrator?.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_CLICK))
                            viewModel.zwiekszIlosc(wybrane)
                        }
                    )
                    HorizontalDivider(modifier = Modifier.padding(horizontal = 16.dp))
                }
            }
        }
    }
}

