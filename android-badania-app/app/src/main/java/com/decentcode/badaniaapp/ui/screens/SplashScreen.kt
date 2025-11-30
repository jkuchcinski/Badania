package com.decentcode.badaniaapp.ui.screens

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.decentcode.badaniaapp.R
import com.decentcode.badaniaapp.utils.Color as ColorExt
import kotlinx.coroutines.delay

/**
 * Ekran startowy z logo i copyright
 */
@Composable
fun SplashScreen(
    onNavigateToMain: () -> Unit
) {
    val context = LocalContext.current
    var startAnimation by remember { mutableStateOf(false) }
    val alphaAnim = animateFloatAsState(
        targetValue = if (startAnimation) 1f else 0f,
        animationSpec = tween(durationMillis = 1000),
        label = "alpha"
    )

    LaunchedEffect(key1 = true) {
        startAnimation = true
        delay(2500) // 2.5 sekundy
        onNavigateToMain()
    }

    Splash(alpha = alphaAnim.value)
}

@Composable
fun Splash(alpha: Float) {
    val context = LocalContext.current
    
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.White),
        contentAlignment = Alignment.Center
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .alpha(alpha),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Spacer(modifier = Modifier.weight(1f))
            
            // Logo
            val logoResId = try {
                val drawableName = "decent_code_1024x0"
                val resId = context.resources.getIdentifier(
                    drawableName,
                    "drawable",
                    context.packageName
                )
                if (resId != 0) resId else null
            } catch (e: Exception) {
                null
            }
            
            if (logoResId != null) {
                Image(
                    painter = painterResource(id = logoResId),
                    contentDescription = "Logo",
                    modifier = Modifier
                        .size(300.dp)
                        .padding(16.dp),
                    contentScale = ContentScale.Fit
                )
            } else {
                // Fallback ikona
                Text(
                    text = "🏥",
                    fontSize = 150.sp,
                    modifier = Modifier.padding(16.dp)
                )
            }
            
            Spacer(modifier = Modifier.weight(1f))
            
            // Copyright
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.padding(bottom = 40.dp)
            ) {
                Text(
                    text = stringResource(R.string.copyright),
                    fontSize = 14.sp,
                    color = ColorExt("757575"),
                    textAlign = TextAlign.Center
                )
                Text(
                    text = stringResource(R.string.all_rights_reserved),
                    fontSize = 14.sp,
                    color = ColorExt("757575"),
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}

