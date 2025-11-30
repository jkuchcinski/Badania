package com.decentcode.badaniaapp.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Badge
import androidx.compose.material3.BadgedBox
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.navigation.NavController
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.decentcode.badaniaapp.R
import com.decentcode.badaniaapp.ui.screens.SearchScreen
import com.decentcode.badaniaapp.ui.screens.SelectedBadaniaScreen
import com.decentcode.badaniaapp.viewmodels.BadaniaViewModel
import com.decentcode.badaniaapp.viewmodels.SelectedBadaniaViewModel

sealed class Screen(val route: String, val title: String) {
    object Search : Screen("search", "Wyszukiwanie")
    object Selected : Screen("selected", "Wybrane")
}

@Composable
fun MainNavigation(
    selectedViewModel: SelectedBadaniaViewModel,
    badaniaViewModel: BadaniaViewModel
) {
    val navController = rememberNavController()
    
    Scaffold(
        bottomBar = {
            BottomNavigation(
                navController = navController,
                selectedViewModel = selectedViewModel
            )
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = Screen.Search.route,
            modifier = Modifier.padding(paddingValues)
        ) {
            composable(Screen.Search.route) {
                SearchScreen(
                    selectedViewModel = selectedViewModel,
                    viewModel = badaniaViewModel
                )
            }
            composable(Screen.Selected.route) {
                SelectedBadaniaScreen(viewModel = selectedViewModel)
            }
        }
    }
}

@Composable
fun BottomNavigation(
    navController: NavController,
    selectedViewModel: SelectedBadaniaViewModel
) {
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination
    val liczbaWybranych by selectedViewModel.wybraneBadania.collectAsState()
    val badgeCount = liczbaWybranych.size
    
    NavigationBar {
        NavigationBarItem(
            icon = { Icon(Icons.Default.Search, contentDescription = null) },
            label = { Text(stringResource(R.string.search)) },
            selected = currentDestination?.hierarchy?.any { it.route == Screen.Search.route } == true,
            onClick = {
                navController.navigate(Screen.Search.route) {
                    popUpTo(navController.graph.findStartDestination().id) {
                        saveState = true
                    }
                    launchSingleTop = true
                    restoreState = true
                }
            }
        )
        NavigationBarItem(
            icon = {
                if (badgeCount > 0) {
                    BadgedBox(
                        badge = {
                            Badge {
                                Text(text = badgeCount.toString())
                            }
                        }
                    ) {
                        Icon(Icons.Default.List, contentDescription = null)
                    }
                } else {
                    Icon(Icons.Default.List, contentDescription = null)
                }
            },
            label = { Text(stringResource(R.string.selected)) },
            selected = currentDestination?.hierarchy?.any { it.route == Screen.Selected.route } == true,
            onClick = {
                navController.navigate(Screen.Selected.route) {
                    popUpTo(navController.graph.findStartDestination().id) {
                        saveState = true
                    }
                    launchSingleTop = true
                    restoreState = true
                }
            }
        )
    }
}

