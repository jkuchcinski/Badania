# BadaniaApp - Aplikacja iOS

Aplikacja mobilna do zarządzania badaniami lekarskimi, stworzona w SwiftUI dla iOS 17+.

## Funkcjonalności

- **Wyszukiwanie badań**: Wyszukiwanie i filtrowanie badań po nazwie lub kodzie
- **Dodawanie badań**: Dodawanie badań do listy wybranych z możliwością wielokrotnego dodania
- **Zarządzanie wybranymi**: Wyświetlanie listy wybranych badań z możliwością zmiany ilości i usuwania
- **Suma**: Automatyczne obliczanie i wyświetlanie sumy wybranych badań
- **Splash Screen**: Ekran startowy z logo firmy i informacjami o prawach autorskich

## Wymagania

- iOS 17.0+
- Xcode 15.0+
- Swift 5.9+

## Instalacja

1. Otwórz projekt w Xcode:
   ```bash
   open ios-badania-app/BadaniaApp.xcodeproj
   ```
   (lub utwórz nowy projekt Xcode i dodaj pliki)

2. **Ważne - Konfiguracja projektu Xcode:**
   
   Jeśli tworzysz nowy projekt Xcode:
   - Utwórz nowy projekt iOS App w Xcode
   - Wybierz SwiftUI jako interfejs
   - Ustaw minimalną wersję iOS na 17.0
   - Skopiuj wszystkie pliki z katalogu `BadaniaApp/` do projektu
   - Dodaj plik `badania.csv` do projektu (Target Membership: BadaniaApp)
   - Dodaj obraz `decent-code-1024x0.png` do Assets.xcassets jako "decent-code-1024x0"

3. **Dodawanie plików do Assets:**
   - Otwórz `Assets.xcassets` w Xcode
   - Utwórz nowy Image Set o nazwie "decent-code-1024x0"
   - Przeciągnij plik `decent-code-1024x0.png` do tego Image Set

4. **Konfiguracja Info.plist:**
   - Upewnij się, że w Info.plist jest ustawiona odpowiednia nazwa aplikacji
   - Sprawdź, czy plik `badania.csv` jest dodany do Bundle Resources

## Struktura projektu

```
BadaniaApp/
├── BadaniaAppApp.swift          # Główny plik aplikacji
├── Models/
│   ├── Badanie.swift            # Model danych badania
│   └── CSVParser.swift          # Parser pliku CSV
├── ViewModels/
│   ├── BadaniaViewModel.swift   # ViewModel dla wyszukiwania
│   └── SelectedBadaniaViewModel.swift  # ViewModel dla wybranych badań
├── Views/
│   ├── SplashScreenView.swift   # Ekran startowy
│   ├── SearchView.swift         # Ekran wyszukiwania
│   ├── SelectedBadaniaView.swift # Ekran wybranych badań
│   ├── SumView.swift            # Komponent sumy
│   └── MainTabView.swift        # Główna nawigacja
└── Resources/
    ├── badania.csv              # Plik z danymi badań
    └── decent-code-1024x0.png   # Logo firmy
```

## Format danych CSV

Plik `badania.csv` używa następującego formatu:
- Separator: średnik (`;`)
- Kolumny: `KOD;NAZWA BADANIA;KWOTA;KWOTA 2`
- Format kwoty: przecinek jako separator dziesiętny (np. `2,00`)
- Kodowanie: UTF-8

## Funkcjonalności szczegółowe

### Wyszukiwanie
- Wyszukiwanie w czasie rzeczywistym (z debounce 300ms)
- Case-insensitive search
- Wyszukiwanie po nazwie i kodzie badania

### Wybrane badania
- Dodawanie tego samego badania wielokrotnie (zliczanie ilości)
- Zmiana ilości przyciskiem +/- lub usunięcie przez swipe
- Automatyczne przeliczanie sumy przy każdej zmianie
- Usuwanie wszystkich badań jednym przyciskiem

### UI/UX
- Material Design-inspired design
- Kolory zgodne z aplikacją webową (#1976d2, #212121)
- Haptic feedback przy interakcjach
- Obsługa dark mode
- Accessibility support (VoiceOver, Dynamic Type)

## Uruchomienie

1. Wybierz docelowe urządzenie lub symulator w Xcode
2. Naciśnij Cmd+R lub kliknij przycisk Run
3. Aplikacja automatycznie wyświetli splash screen, a następnie przejdzie do głównej aplikacji

## Rozwiązywanie problemów

### Problem: "File not found" przy wczytywaniu CSV
- Upewnij się, że plik `badania.csv` jest dodany do projektu
- Sprawdź Target Membership w File Inspector
- Sprawdź, czy plik jest w Bundle Resources

### Problem: Logo nie wyświetla się
- Upewnij się, że obraz jest dodany do Assets.xcassets
- Sprawdź nazwę Image Set (powinna być "decent-code-1024x0")
- Sprawdź, czy plik PNG jest poprawnie załadowany

### Problem: Błędy kompilacji związane z iOS 17
- Upewnij się, że minimalna wersja iOS jest ustawiona na 17.0
- Sprawdź Deployment Target w ustawieniach projektu

## Licencja

© 2025 Decent Code sp. z o.o.
All rights reserved

