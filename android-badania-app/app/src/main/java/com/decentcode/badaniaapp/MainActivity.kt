package com.decentcode.badaniaapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import com.decentcode.badaniaapp.navigation.MainNavigation
import com.decentcode.badaniaapp.ui.screens.SplashScreen
import com.decentcode.badaniaapp.ui.theme.BadaniaAppTheme
import com.decentcode.badaniaapp.viewmodels.BadaniaViewModel
import com.decentcode.badaniaapp.viewmodels.SelectedBadaniaViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            BadaniaAppTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MainApp()
                }
            }
        }
    }
}

@Composable
fun MainApp() {
    var showSplash by remember { mutableStateOf(true) }
    val selectedViewModel: SelectedBadaniaViewModel = androidx.lifecycle.viewmodel.compose.viewModel()
    val badaniaViewModel: BadaniaViewModel = viewModel()
    
    if (showSplash) {
        SplashScreen(
            onNavigateToMain = {
                showSplash = false
            }
        )
    } else {
        MainNavigation(
            selectedViewModel = selectedViewModel,
            badaniaViewModel = badaniaViewModel
        )
    }
}

