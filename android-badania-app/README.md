# BadaniaApp - Aplikacja Android

Aplikacja mobilna do zarządzania badaniami lekarskimi, stworzona w Kotlin z Jetpack Compose dla Android 8.0+.

## Funkcjonalności

- **Wyszukiwanie badań**: Wyszukiwanie i filtrowanie badań po nazwie lub kodzie
- **Dodawanie badań**: Dodawanie badań do listy wybranych z możliwością wielokrotnego dodania
- **Zarządzanie wybranymi**: Wyświetlanie listy wybranych badań z możliwością zmiany ilości i usuwania
- **Suma**: Automatyczne obliczanie i wyświetlanie sumy wybranych badań
- **Splash Screen**: Ekran startowy z logo firmy i informacjami o prawach autorskich

## Wymagania

- Android 8.0 (API 26)+
- Android Studio Hedgehog | 2023.1.1 lub nowszy
- Gradle 8.2+

## Instalacja

1. Otwórz projekt w Android Studio:
   - File → Open → wybierz folder `android-badania-app`

2. **Konfiguracja projektu:**
   - Upewnij się, że masz zainstalowany Android SDK z API 26+
   - Zsynchronizuj projekt (Sync Project with Gradle Files)

3. **Dodawanie plików zasobów:**
   - Plik `badania.csv` powinien być w `app/src/main/assets/badania.csv`
   - Logo `decent-code-1024x0.png` powinno być w `app/src/main/res/drawable/`

4. **Uruchomienie:**
   - Wybierz urządzenie/emulator
   - Naciśnij Run (Shift+F10) lub kliknij przycisk Run

## Struktura projektu

```
android-badania-app/
├── app/
│   ├── src/main/
│   │   ├── java/com/decentcode/badaniaapp/
│   │   │   ├── MainActivity.kt
│   │   │   ├── models/
│   │   │   │   ├── Badanie.kt
│   │   │   │   ├── WybraneBadanie.kt
│   │   │   │   └── CSVParser.kt
│   │   │   ├── viewmodels/
│   │   │   │   ├── BadaniaViewModel.kt
│   │   │   │   └── SelectedBadaniaViewModel.kt
│   │   │   ├── ui/
│   │   │   │   ├── screens/
│   │   │   │   │   ├── SplashScreen.kt
│   │   │   │   │   ├── SearchScreen.kt
│   │   │   │   │   └── SelectedBadaniaScreen.kt
│   │   │   │   ├── components/
│   │   │   │   │   ├── SearchBar.kt
│   │   │   │   │   ├── BadanieRow.kt
│   │   │   │   │   ├── WybraneBadanieRow.kt
│   │   │   │   │   └── SumView.kt
│   │   │   │   └── theme/
│   │   │   │       ├── Theme.kt
│   │   │   │       └── Type.kt
│   │   │   ├── navigation/
│   │   │   │   └── NavGraph.kt
│   │   │   └── utils/
│   │   │       └── ColorExtensions.kt
│   │   ├── res/
│   │   │   ├── values/
│   │   │   │   ├── strings.xml
│   │   │   │   ├── colors.xml
│   │   │   │   └── themes.xml
│   │   │   ├── drawable/
│   │   │   │   └── decent-code-1024x0.png
│   │   │   └── raw/
│   │   └── assets/
│   │       └── badania.csv
│   └── build.gradle
├── build.gradle
├── settings.gradle
└── gradle.properties
```

## Format danych CSV

Plik `badania.csv` używa następującego formatu:
- Separator: średnik (`;`)
- Kolumny: `KOD;NAZWA BADANIA;KWOTA;KWOTA 2`
- Format kwoty: przecinek jako separator dziesiętny (np. `2,00`)
- Kodowanie: UTF-8
- Lokalizacja: `app/src/main/assets/badania.csv`

## Funkcjonalności szczegółowe

### Wyszukiwanie
- Wyszukiwanie w czasie rzeczywistym (z debounce 300ms)
- Case-insensitive search
- Wyszukiwanie po nazwie i kodzie badania

### Wybrane badania
- Dodawanie tego samego badania wielokrotnie (zliczanie ilości)
- Zmiana ilości przyciskiem +/- 
- Automatyczne przeliczanie sumy przy każdej zmianie
- Usuwanie wszystkich badań jednym przyciskiem

### UI/UX
- Material Design 3 (zgodnie z aplikacją webową)
- Kolory: primary #1976d2, text #212121
- Czcionka: Roboto (domyślna Android)
- Animacje przy dodawaniu/usuwaniu badań
- Haptic feedback przy interakcjach
- Obsługa dark mode (automatyczna)
- Kod badania wyświetlany grubą czcionką

## Technologie

- Kotlin 1.9.22
- Jetpack Compose (najnowsza wersja)
- Material Design 3
- MVVM Architecture
- StateFlow dla reactive state management
- Coroutines dla async operations
- Navigation Component

## Rozwiązywanie problemów

### Problem: "File not found" przy wczytywaniu CSV
- Upewnij się, że plik `badania.csv` jest w `app/src/main/assets/`
- Sprawdź, czy plik ma rozszerzenie `.csv`
- Sprawdź nazwę pliku w kodzie (domyślnie "badania")

### Problem: Logo nie wyświetla się
- Upewnij się, że obraz jest w `app/src/main/res/drawable/`
- Sprawdź nazwę pliku (powinna być "decent_code_1024x0.png" - z podkreślnikami)
- W Android nazwy plików nie mogą zawierać myślników

### Problem: Błędy kompilacji związane z API
- Upewnij się, że masz zainstalowany Android SDK z API 26+
- Sprawdź `minSdk` w `app/build.gradle` (powinno być 26)

## Licencja

© 2025 Decent Code sp. z o.o.
All rights reserved

