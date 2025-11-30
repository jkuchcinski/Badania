package com.decentcode.badaniaapp.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat
import com.decentcode.badaniaapp.utils.Color

private val DarkColorScheme = darkColorScheme(
    primary = Color("1976d2"),
    secondary = Color("1976d2"),
    tertiary = Color("1976d2")
)

private val LightColorScheme = lightColorScheme(
    primary = Color("1976d2"),
    onPrimary = androidx.compose.ui.graphics.Color.White,
    secondary = Color("1976d2"),
    onSecondary = androidx.compose.ui.graphics.Color.White,
    tertiary = Color("1976d2"),
    background = androidx.compose.ui.graphics.Color.White,
    onBackground = Color("212121"),
    surface = androidx.compose.ui.graphics.Color.White,
    onSurface = Color("212121")
)

@Composable
fun BadaniaAppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            // WindowInsetsController może nie być dostępne we wszystkich wersjach
            // Ustawienie statusBarColor jest wystarczające dla podstawowej funkcjonalności
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}

