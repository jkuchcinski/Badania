//
//  SplashScreenView.swift
//  BadaniaApp
//
//  Ekran startowy z logo i copyright
//

import SwiftUI

struct SplashScreenView: View {
    @State private var isActive = false
    @State private var opacity = 0.0
    
    var body: some View {
        if isActive {
            MainTabView()
        } else {
            ZStack {
                Color.white
                    .ignoresSafeArea()
                
                VStack(spacing: 40) {
                    Spacer()
                    
                    // Logo
                    Group {
                        if let image = UIImage(named: "decent-code-1024x0") {
                            Image(uiImage: image)
                                .resizable()
                                .scaledToFit()
                        } else if let path = Bundle.main.path(forResource: "decent-code-1024x0", ofType: "png"),
                                  let image = UIImage(contentsOfFile: path) {
                            Image(uiImage: image)
                                .resizable()
                                .scaledToFit()
                        } else {
                            // Fallback jeśli logo nie zostanie znalezione
                            Image(systemName: "cross.case.fill")
                                .resizable()
                                .scaledToFit()
                                .foregroundColor(Color(hex: "1976d2"))
                        }
                    }
                    .frame(maxWidth: 300, maxHeight: 300)
                    .opacity(opacity)
                    .animation(.easeIn(duration: 1.0), value: opacity)
                    //Spacer()
                    
                    VStack{
                        Text("BADANIA")
                            .font(.largeTitle).fontWeight(.heavy)
                            .foregroundColor(.accentColor)
                        Text("Przychodnia Hipokrates")
                            .font(.title2).fontWeight(.light)
                            .foregroundColor(.accentColor)
                    }
                    
                    Spacer()
                    
                    // Copyright
                    VStack(spacing: 8) {
                        Text("© 2025 Decent Code sp. z o.o.")
                            .font(.system(size: 14, weight: .regular))
                            .foregroundColor(Color(hex: "757575"))
                        
                        Text("All rights reserved")
                            .font(.system(size: 14, weight: .regular))
                            .foregroundColor(Color(hex: "757575"))
                    }
                    .opacity(opacity)
                    .padding(.bottom, 40)
                }
            }
            .onAppear {
                // Animacja fade-in
                withAnimation {
                    opacity = 1.0
                }
                
                // Automatyczne przejście po 2.5 sekundach
                DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) {
                    withAnimation {
                        isActive = true
                    }
                }
            }
        }
    }
}

// Extension do konwersji hex na Color
extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

