package com.decentcode.badaniaapp.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AddCircle
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.decentcode.badaniaapp.models.Badanie
import com.decentcode.badaniaapp.utils.Color

/**
 * Komponent wiersza badania w liście wyszukiwania
 */
@Composable
fun BadanieRow(
    badanie: Badanie,
    onAdd: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp, horizontal = 16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                text = badanie.nazwa,
                style = MaterialTheme.typography.bodyLarge,
                color = Color("212121")
            )
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Kod: ${badanie.kod}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                if (badanie.kwota != null) {
                    Text(
                        text = badanie.formattedKwota(),
                        style = MaterialTheme.typography.bodySmall,
                        color = Color("1976d2"),
                        fontWeight = FontWeight.Medium
                    )
                } else {
                    Text(
                        text = "Brak ceny",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
        
        IconButton(onClick = onAdd) {
            Icon(
                imageVector = Icons.Default.AddCircle,
                contentDescription = "Dodaj",
                tint = Color("1976d2"),
                modifier = Modifier.size(32.dp)
            )
        }
    }
}

