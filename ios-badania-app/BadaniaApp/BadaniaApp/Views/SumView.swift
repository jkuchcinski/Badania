//
//  SumView.swift
//  BadaniaApp
//
//  Panel z sumą wybranych badań
//

import SwiftUI

struct SumView: View {
    let sum: Double
    let formattedSum: String
    
    var body: some View {
        VStack(spacing: 0) {
            Divider()
            
            HStack {
                Text("Suma wybranych badań:")
                    .font(.headline)
                    .foregroundColor(Color(hex: "212121"))
                
                Spacer()
                
                Text(formattedSum)
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(Color(hex: "1976d2"))
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 16)
            .background(Color(.systemBackground))
        }
    }
}

