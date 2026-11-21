import SwiftUI

// Ports the loading skeletons of ui/components/Skeletons.kt.

/// A pulsing placeholder shape (Skeletons.kt's shimmer), honouring Reduce Motion.
///
/// Driven by a `TimelineView`, as ``ShimmerBlock`` is. A repeating `withAnimation` in `onAppear` took
/// in whatever else changed in that pass: the album page's sort button, added as its loading rows
/// appeared, faded and slid in and out every 1.8 s for as long as the page was up.
struct SkeletonBlock: View {
    var width: CGFloat?
    var height: CGFloat
    var cornerRadius: CGFloat = 6

    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    private static let period = 1.8

    var body: some View {
        let block = RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
            .fill(Color(.tertiarySystemFill))
            .frame(width: width, height: height)
        if reduceMotion {
            block
        } else {
            TimelineView(.animation) { context in
                let phase = context.date.timeIntervalSinceReferenceDate
                    .truncatingRemainder(dividingBy: Self.period) / Self.period
                block.opacity(1 - 0.55 * (1 - cos(2 * .pi * phase)) / 2)
            }
        }
    }
}

/// Stand-in rows while a list loads.
struct SongRowSkeleton: View {
    var body: some View {
        HStack(spacing: 12) {
            SkeletonBlock(width: 48, height: 48, cornerRadius: AppTheme.artCorner)
            VStack(alignment: .leading, spacing: 6) {
                SkeletonBlock(width: 180, height: 12)
                SkeletonBlock(width: 110, height: 10)
            }
            Spacer()
        }
        .padding(.horizontal, AppTheme.gutter)
        .padding(.vertical, 6)
        .accessibilityHidden(true)
    }
}

/// Stand-in shelf while a feed loads.
struct ShelfSkeleton: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            SkeletonBlock(width: 160, height: 18).padding(.horizontal, AppTheme.gutter)
            HStack(spacing: 12) {
                ForEach(0..<3, id: \.self) { _ in
                    VStack(alignment: .leading, spacing: 6) {
                        SkeletonBlock(width: 150, height: 150, cornerRadius: 10)
                        SkeletonBlock(width: 110, height: 10)
                    }
                }
            }
            .padding(.horizontal, AppTheme.gutter)
        }
        .accessibilityHidden(true)
    }
}

/// A list of skeleton rows.
struct ListSkeleton: View {
    var rows = 8

    var body: some View {
        VStack(spacing: 0) {
            ForEach(0..<rows, id: \.self) { _ in SongRowSkeleton() }
        }
    }
}
