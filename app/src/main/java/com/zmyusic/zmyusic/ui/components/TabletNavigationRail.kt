package com.zmyusic.zmyusic.ui.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.WindowInsetsSides
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.only
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp

/** How wide the rail is, glyph and label included. */
private val RAIL_WIDTH = 88.dp

/** The tappable column inside the rail's padding. */
private val RAIL_ITEM_WIDTH = 64.dp

/**
 * The tab row, stood on its side - what a tablet gets instead of
 * [FloatingBottomBar].
 *
 * A tablet has the height to spare and the width to lose: putting the four
 * tabs down the leading edge leaves the feed its full height and keeps the
 * thumb from travelling to the foot of a 13-inch screen to change tabs.
 * Phones keep the floating bar, and so does anything narrower than the
 * platform's own `sw600dp` tablet cut - see [TABLET_MIN_WIDTH] at the call
 * site in `MainActivity`.
 *
 * Deliberately plain next to the phone's glass: this is a permanent piece of
 * chrome rather than something that rides over the page, so it sits on the
 * window's own background and only the selection is allowed to move.
 */
@Composable
fun TabletNavigationRail(
    tabs: List<BottomTab>,
    selectedIndex: Int,
    onTabSelected: (Int) -> Unit,
    modifier: Modifier = Modifier,
) {
    val colors = MaterialTheme.colorScheme
    Column(
        modifier = modifier
            .width(RAIL_WIDTH)
            .fillMaxHeight()
            // The window's top and bottom insets, plus its leading one: a
            // tablet in landscape has its navigation bar on the long edge,
            // and the rail is the one thing on this side of the page that
            // would otherwise sit under it.
            .windowInsetsPadding(
                WindowInsets.safeDrawing.only(
                    WindowInsetsSides.Start + WindowInsetsSides.Vertical,
                ),
            )
            .padding(horizontal = 8.dp, vertical = 16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Column(
            modifier = Modifier
                .width(RAIL_ITEM_WIDTH)
                // One selection across the four, read as a tab list by a
                // screen reader rather than four unrelated buttons.
                .selectableGroup(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            tabs.forEachIndexed { index, tab ->
                val selected = index == selectedIndex
                val background by animateColorAsState(
                    targetValue = if (selected) colors.secondaryContainer else Color.Transparent,
                    label = "railTabBackground",
                )
                val contentColor by animateColorAsState(
                    targetValue = if (selected) colors.onSecondaryContainer else colors.onSurfaceVariant,
                    label = "railTabContent",
                )
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(20.dp))
                        .background(background)
                        .selectable(
                            selected = selected,
                            role = Role.Tab,
                            onClick = { onTabSelected(index) },
                        )
                        .padding(vertical = 10.dp, horizontal = 4.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Icon(
                        imageVector = tab.icon,
                        contentDescription = tab.label,
                        tint = contentColor,
                        modifier = Modifier.size(24.dp),
                    )
                    Spacer(Modifier.height(4.dp))
                    Text(
                        text = tab.label,
                        color = contentColor,
                        style = MaterialTheme.typography.labelSmall,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        textAlign = TextAlign.Center,
                    )
                }
            }
        }
    }
}
