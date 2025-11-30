package com.decentcode.badaniaapp.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AddCircle
import androidx.compose.material.icons.filled.RemoveCircle
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.decentcode.badaniaapp.models.WybraneBadanie
import com.decentcode.badaniaapp.utils.Color

/**
 * Komponent wiersza wybranego badania
 */
@Composable
fun WybraneBadanieRow(
    wybrane: WybraneBadanie,
    onDecrease: () -> Unit,
    onIncrease: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp, horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Nazwa badania
        Text(
            text = wybrane.badanie.nazwa,
            style = MaterialTheme.typography.bodyLarge,
            color = Color("212121")
        )
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Kod badania (wyświetlany grubą czcionką)
            Column(
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = "Kod:",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = wybrane.badanie.kod,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color("212121")
                )
                if (wybrane.badanie.kwota != null) {
                    Text(
                        text = "${wybrane.badanie.formattedKwota()} × ${wybrane.ilosc}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(top = 4.dp)
                    )
                }
            }
            
            // Kontrolki ilości
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onDecrease) {
                    Icon(
                        imageVector = Icons.Default.RemoveCircle,
                        contentDescription = "Zmniejsz",
                        tint = Color("1976d2"),
                        modifier = Modifier.size(28.dp)
                    )
                }
                
                Text(
                    text = "${wybrane.ilosc}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color("212121"),
                    modifier = Modifier.width(30.dp)
                )
                
                IconButton(onClick = onIncrease) {
                    Icon(
                        imageVector = Icons.Default.AddCircle,
                        contentDescription = "Zwiększ",
                        tint = Color("1976d2"),
                        modifier = Modifier.size(28.dp)
                    )
                }
            }
            
            // Całkowita kwota
            Column(
                horizontalAlignment = Alignment.End,
                verticalArrangement = Arrangement.spacedBy(2.dp)
            ) {
                Text(
                    text = wybrane.formattedCalkowitaKwota(),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color("1976d2")
                )
            }
        }
    }
}

