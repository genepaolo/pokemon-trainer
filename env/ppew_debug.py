"""
Optimized PyBoy runner with modular overlay system
Much faster than ppew_debug.py - suitable for training multiple instances

Features:
1. Headless mode for training (no PyBoy window)
2. SDL2 mode for interactive play (PyBoy handles controls)
3. Modular overlays: --info (stats panel), --tiles (grid), --dir (movement arrows)
4. Configurable overlay refresh rate
5. Clean, modern UI design
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env.pyboy_pokeblue_env_walker import PyBoyPokeBlueEnvWalker
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.patches as patches
import numpy as np
import time
from collections import deque

class OptimizedDebugRunner:
    # Screen and tile constants
    SCREEN_WIDTH = 160
    SCREEN_HEIGHT = 144
    MAP_TILE_SIZE = 16  # Pokemon map tiles are 16x16 pixels (2x2 GB tiles)
    GRID_TILE_SIZE = 16  # Display grid tile size (16x16 pixels)
    GRID_WIDTH = SCREEN_WIDTH // GRID_TILE_SIZE  # 10 tiles
    GRID_HEIGHT = SCREEN_HEIGHT // GRID_TILE_SIZE  # 9 tiles

    # Memory addresses for scroll registers
    ADDR_SCROLL_X = 0xFF43  # SCX register
    ADDR_SCROLL_Y = 0xFF42  # SCY register
    
    # Player sprite screen position (fixed - player is always centered on screen)
    # Screen is 160x144 pixels = 10x9 tiles (16px each)
    # Player is at tile (4, 4), center at pixel (72, 72)
    PLAYER_SCREEN_CENTER_X = 72
    PLAYER_SCREEN_CENTER_Y = 72
    
    # Arrow direction offset for centering arrows within tiles
    # Negative shifts arrow backward along its direction, positive shifts forward
    ARROW_DIRECTION_OFFSET = -2

    def __init__(
        self,
        rom_path,
        show_pyboy_window=False,
        show_info=False,
        show_tiles=False,
        show_dir=False,
        overlay_refresh_rate=2,
        max_fps=60,
        print_stats=True
    ):
        """
        Args:
            rom_path: Path to Pokemon ROM
            show_pyboy_window: Show PyBoy SDL2 window (for interactive play with arrow keys)
            show_info: Show info panel with stats (--info)
            show_tiles: Show tile grid overlay (--tiles)
            show_dir: Show movement direction arrows (--dir)
            overlay_refresh_rate: Update display every N frames
            max_fps: Target FPS (0 = unlimited)
            print_stats: Print performance statistics to console
        """
        self.show_pyboy_window = show_pyboy_window
        self.show_info = show_info
        self.show_tiles = show_tiles
        self.show_dir = show_dir
        self.show_overlay = show_info or show_tiles or show_dir  # Show matplotlib if any overlay is enabled
        self.overlay_refresh_rate = overlay_refresh_rate
        self.max_fps = max_fps
        self.print_stats = print_stats
        self.frame_count = 0
        self.start_time = None

        # Movement tracking for direction arrows
        self.movement_history = deque(maxlen=100)  # Keep last 100 movements
        self.visited_tiles = {}  # Dict: (x, y, map_id) -> visit_count
        self.prev_pos = None
        self.prev_map = None

        # Choose window type
        window_mode = "SDL2" if show_pyboy_window else "null"

        print(f"🎮 Initializing PyBoy in {window_mode} mode...")
        overlays_active = []
        if show_info:
            overlays_active.append("INFO")
        if show_tiles:
            overlays_active.append("TILES")
        if show_dir:
            overlays_active.append("DIR")

        if overlays_active:
            print(f"📊 Active Overlays: {', '.join(overlays_active)}")
        else:
            print("📊 Overlays: OFF")

        print(f"⚡ Max FPS: {max_fps if max_fps > 0 else 'UNLIMITED'}")

        if show_pyboy_window:
            print("💡 TIP: Use arrow keys in the PyBoy window to move!")
        else:
            print("💡 Running in headless mode (no display)")

        # Create environment
        self.env = PyBoyPokeBlueEnvWalker(
            rom_path,
            debug_overlay=False,
            window_type=window_mode
        )

        # Setup matplotlib if any overlay is enabled
        self.fig = None
        self.ax_game = None
        self.ax_stats = None
        self.img_plot = None
        self.stats_text = None
        self.tile_lines = []  # Store tile grid line objects
        self.arrow_patches = []  # Store arrow patch objects
        self.player_marker = None  # Store player position marker

        if self.show_overlay:
            self._setup_ui()

    def _setup_ui(self):
        """Setup matplotlib UI with game screen and optional info panel"""
        plt.ion()

        # Calculate layout based on whether info panel is shown
        if self.show_info:
            # Two-panel layout: game + info
            self.fig = plt.figure(figsize=(12, 6))
            gs = GridSpec(1, 2, figure=self.fig, width_ratios=[2, 1], wspace=0.1)
            self.ax_game = self.fig.add_subplot(gs[0])
        else:
            # Single panel: game only
            self.fig = plt.figure(figsize=(8, 6))
            self.ax_game = self.fig.add_subplot(111)

        self.ax_game.axis('off')

        # Set title based on active overlays
        title_parts = ["Pokemon Blue"]
        if self.show_pyboy_window:
            title_parts.append("Use Arrow Keys in PyBoy Window")
        if self.show_tiles:
            title_parts.append("[TILES]")
        if self.show_dir:
            title_parts.append("[DIRECTION]")

        self.ax_game.set_title(" - ".join(title_parts), fontsize=12, fontweight='bold', pad=10)

        # Pre-create game screen image
        dummy_img = np.zeros((144, 160, 3), dtype=np.uint8)
        self.img_plot = self.ax_game.imshow(dummy_img, interpolation='nearest', zorder=1)
        
        # Fix axis limits to prevent shrinking when arrows are added
        self.ax_game.set_xlim(-0.5, self.SCREEN_WIDTH - 0.5)
        self.ax_game.set_ylim(self.SCREEN_HEIGHT - 0.5, -0.5)  # Inverted for image coordinates

        # Setup info panel if enabled
        if self.show_info:
            self.ax_stats = self.fig.add_subplot(gs[1])
            self.ax_stats.axis('off')
            self.ax_stats.set_facecolor('#1e1e1e')

            self.stats_text = self.ax_stats.text(
                0.05, 0.95, "",
                transform=self.ax_stats.transAxes,
                fontfamily='monospace',
                fontsize=10,
                verticalalignment='top',
                color='#00ff00'
            )

        # Setup tile grid if enabled
        if self.show_tiles:
            self._setup_tile_grid()

    def _setup_tile_grid(self):
        """Pre-create tile grid lines - these will be updated each frame to align with world tiles"""
        # Create enough lines to cover the screen plus one extra for scrolling
        # Vertical lines
        for _ in range(self.GRID_WIDTH + 2):
            line, = self.ax_game.plot([], [], color='#00ff00', alpha=0.4, linewidth=0.5, zorder=2)
            self.tile_lines.append(('v', line))

        # Horizontal lines
        for _ in range(self.GRID_HEIGHT + 2):
            line, = self.ax_game.plot([], [], color='#00ff00', alpha=0.4, linewidth=0.5, zorder=2)
            self.tile_lines.append(('h', line))

    def _update_tile_grid(self):
        """Update tile grid position based on scroll registers to align with world tiles"""
        if not self.show_tiles:
            return

        # Get scroll registers - tells us camera position in world
        scx = self.env.pyboy.memory[self.ADDR_SCROLL_X]
        scy = self.env.pyboy.memory[self.ADDR_SCROLL_Y]

        # Calculate grid offset based on scroll position
        # Grid lines should appear at world tile boundaries
        # World boundaries are at 0, 16, 32... in world space
        # To convert to screen: screen_x = world_x - scx
        # First visible boundary: world_x = (scx // 16) * 16, screen_x = -(scx % 16)
        offset_x = -(scx % self.GRID_TILE_SIZE)
        offset_y = -(scy % self.GRID_TILE_SIZE)

        # Update line positions
        v_idx = 0
        h_idx = 0
        for line_type, line in self.tile_lines:
            if line_type == 'v':
                x = offset_x + v_idx * self.GRID_TILE_SIZE - 0.5
                if -self.GRID_TILE_SIZE <= x <= self.SCREEN_WIDTH + self.GRID_TILE_SIZE:
                    line.set_data([x, x], [-0.5, self.SCREEN_HEIGHT - 0.5])
                else:
                    line.set_data([], [])
                v_idx += 1
            else:  # 'h'
                y = offset_y + h_idx * self.GRID_TILE_SIZE - 0.5
                if -self.GRID_TILE_SIZE <= y <= self.SCREEN_HEIGHT + self.GRID_TILE_SIZE:
                    line.set_data([-0.5, self.SCREEN_WIDTH - 0.5], [y, y])
                else:
                    line.set_data([], [])
                h_idx += 1

    def _track_movement(self):
        """Track player movement for direction arrows"""
        if not self.show_dir:
            return

        pos = self.env._get_player_position()
        map_id = self.env._get_map_id()

        # Track movement if position changed
        if self.prev_pos is not None and self.prev_map == map_id:
            prev_x, prev_y = self.prev_pos
            curr_x, curr_y = pos

            # Only track if actually moved to a new tile
            if (prev_x, prev_y) != (curr_x, curr_y):
                self.movement_history.append((prev_x, prev_y, curr_x, curr_y, map_id))
                
                # Track visit count only when entering a NEW tile (not every frame)
                tile_key = (curr_x, curr_y, map_id)
                self.visited_tiles[tile_key] = self.visited_tiles.get(tile_key, 0) + 1
        elif self.prev_pos is None:
            # First frame - initialize the starting tile with 1 visit
            tile_key = (pos[0], pos[1], map_id)
            self.visited_tiles[tile_key] = 1

        self.prev_pos = pos
        self.prev_map = map_id

    def _get_visit_color(self, visit_count):
        """Get color based on visit count (green → yellow → orange → red)
        
        1 visit:     Green  (#00ff00)
        2-3 visits:  Yellow (#ffff00)
        4-6 visits:  Orange (#ff8000)
        7+ visits:   Red    (#ff0000)
        """
        if visit_count <= 1:
            return '#00ff00'  # Green - first visit
        elif visit_count <= 3:
            return '#ffff00'  # Yellow - revisited
        elif visit_count <= 6:
            return '#ff8000'  # Orange - frequently visited
        else:
            return '#ff0000'  # Red - heavily trafficked

    def _draw_direction_arrows(self):
        """Draw arrows showing movement history (one arrow per tile, latest overrides)
        
        Key insight: In Pokemon, the player sprite is ALWAYS at the center of the screen.
        The background scrolls around the player. So to draw arrows at the correct position:
        1. Get current player position (map tile coords)
        2. For each historical movement, calculate the tile's offset from current player position
        3. Draw the arrow at screen_center + offset_in_pixels
        
        Arrow color indicates visit count:
        - Green: 1 visit (first time)
        - Yellow: 2-3 visits
        - Orange: 4-6 visits
        - Red: 7+ visits (heavily trafficked)
        """
        if not self.show_dir:
            return

        # Clear old arrows
        for arrow in self.arrow_patches:
            arrow.remove()
        self.arrow_patches.clear()

        # Get current map and player position
        current_map = self.env._get_map_id()
        current_player_x, current_player_y = self.env._get_player_position()

        # Build a dict of tile -> most recent arrow data
        # Key: (from_x, from_y), Value: (to_x, to_y, index)
        tile_arrows = {}
        for i, (from_x, from_y, to_x, to_y, map_id) in enumerate(self.movement_history):
            if map_id == current_map:
                tile_key = (from_x, from_y)
                # Override previous arrow from this tile with the most recent one
                tile_arrows[tile_key] = (to_x, to_y, i)

        # Player is always at screen center
        player_screen_x = self.PLAYER_SCREEN_CENTER_X
        player_screen_y = self.PLAYER_SCREEN_CENTER_Y

        # Draw one arrow per tile (the most recent movement from that tile)
        for (from_x, from_y), (to_x, to_y, index) in tile_arrows.items():
            # Calculate tile offset from current player position (in map tiles)
            tile_offset_x = from_x - current_player_x
            tile_offset_y = from_y - current_player_y

            # Convert tile offset to pixel offset
            pixel_offset_x = tile_offset_x * self.MAP_TILE_SIZE
            pixel_offset_y = tile_offset_y * self.MAP_TILE_SIZE

            # Calculate screen position for the arrow start
            from_screen_px = player_screen_x + pixel_offset_x
            from_screen_py = player_screen_y + pixel_offset_y

            # Skip if not visible on screen (with some margin)
            margin = self.MAP_TILE_SIZE
            if (from_screen_px < -margin or
                from_screen_px >= self.SCREEN_WIDTH + margin or
                from_screen_py < -margin or
                from_screen_py >= self.SCREEN_HEIGHT + margin):
                continue

            # Calculate arrow direction (in pixels, based on tile movement)
            dx = (to_x - from_x) * self.MAP_TILE_SIZE
            dy = (to_y - from_y) * self.MAP_TILE_SIZE

            # Skip if no movement
            if dx == 0 and dy == 0:
                continue

            # Arrow sizing and positioning
            arrow_scale = 0.6
            arrow_dx = dx * arrow_scale
            arrow_dy = dy * arrow_scale
            head_length = 4
            head_width = 5

            # Center arrow on tile: start at (tile_center - half_arrow_length)
            # Apply direction offset to fine-tune centering
            arrow_length = (arrow_dx**2 + arrow_dy**2)**0.5
            if arrow_length > 0:
                offset_x = (arrow_dx / arrow_length) * self.ARROW_DIRECTION_OFFSET
                offset_y = (arrow_dy / arrow_length) * self.ARROW_DIRECTION_OFFSET
            else:
                offset_x = offset_y = 0
            
            arrow_start_x = from_screen_px - arrow_dx / 2 + offset_x
            arrow_start_y = from_screen_py - arrow_dy / 2 + offset_y

            # Get visit count for this tile to determine color
            tile_key = (from_x, from_y, current_map)
            visit_count = self.visited_tiles.get(tile_key, 1)
            arrow_color = self._get_visit_color(visit_count)

            # Alpha based on recency (newer = more opaque)
            alpha = 0.6 + (index / len(self.movement_history)) * 0.4

            # Draw arrow with black outline for visibility
            arrow = self.ax_game.arrow(
                arrow_start_x, arrow_start_y, arrow_dx, arrow_dy,
                head_width=head_width, head_length=head_length,
                fc=arrow_color,      # Fill color based on visit count
                ec='#000000',        # Black outline
                alpha=alpha,
                linewidth=1.5,       # Outline thickness
                zorder=3
            )
            self.arrow_patches.append(arrow)

    def _draw_player_marker(self):
        """Draw a marker at the player's current position (screen center) for debugging alignment"""
        # Remove old marker
        if self.player_marker is not None:
            self.player_marker.remove()
            self.player_marker = None

        # Draw a small rectangle around where the player should be
        # Player is at screen center (fixed position)
        rect = patches.Rectangle(
            (self.PLAYER_SCREEN_CENTER_X - 8, self.PLAYER_SCREEN_CENTER_Y - 8),
            16, 16,
            linewidth=2,
            edgecolor='#ff00ff',  # Magenta for visibility
            facecolor='none',
            linestyle='--',
            zorder=4
        )
        self.player_marker = self.ax_game.add_patch(rect)

    def _update_overlay(self):
        """Update game screen and overlays"""
        if not self.show_overlay:
            return

        # Track movement
        self._track_movement()

        # Update game screen
        screen_array = self.env.pyboy.screen.ndarray
        self.img_plot.set_data(screen_array)

        # Update tile grid if enabled (moves with world)
        if self.show_tiles:
            self._update_tile_grid()

        # Update direction arrows if enabled
        if self.show_dir:
            self._draw_direction_arrows()
            self._draw_player_marker()

        # Update info panel if enabled
        if self.show_info:
            self._update_info_panel()

        plt.draw()
        plt.pause(0.001)

    def _update_info_panel(self):
        """Update the info panel with current stats"""
        # Get stats
        pos = self.env._get_player_position()
        map_id = self.env._get_map_id()
        steps = self.env.state['steps']
        visited = len(self.env.state['visited_maps'])

        # Calculate FPS
        fps = 0
        if self.start_time:
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0

        # Get movement stats
        unique_tiles_visited = len([k for k in self.visited_tiles.keys() if k[2] == map_id])
        total_movements = len(self.movement_history)

        # Format stats text
        stats_lines = [
            "╔══════════════════════╗",
            "║   GAME STATISTICS    ║",
            "╚══════════════════════╝",
            "",
            f"⚡ FPS: {fps:.1f}",
            f"🎮 Frames: {self.frame_count:,}",
            "",
            "╔══════════════════════╗",
            "║   PLAYER INFO        ║",
            "╚══════════════════════╝",
            "",
            f"📍 Position:",
            f"   X: {pos[0]:3d} (Tile)",
            f"   Y: {pos[1]:3d} (Tile)",
            "",
            f"🗺️  Map ID: {map_id}",
            f"👟 Steps: {steps:,}",
            f"🌍 Maps Visited: {visited}",
        ]

        if self.show_dir:
            # Calculate max visits for current map
            map_visits = [v for (x, y, m), v in self.visited_tiles.items() if m == map_id]
            max_visits = max(map_visits) if map_visits else 0
            
            stats_lines.extend([
                "",
                "╔══════════════════════╗",
                "║   MOVEMENT STATS     ║",
                "╚══════════════════════╝",
                "",
                f"🔵 Tiles (This Map): {unique_tiles_visited}",
                f"➡️  Movements: {total_movements}",
                f"🔥 Max Visits: {max_visits}",
                "",
                "Arrow Colors:",
                "  🟢 Green:  1 visit",
                "  🟡 Yellow: 2-3 visits",
                "  🟠 Orange: 4-6 visits",
                "  🔴 Red:    7+ visits",
            ])

        stats_lines.extend([
            "",
            "╔══════════════════════╗",
            "║   CONTROLS           ║",
            "╚══════════════════════╝",
            "",
        ])

        if self.show_pyboy_window:
            stats_lines.extend([
                "Use PyBoy Window:",
                "↑ ↓ ← → Arrow Keys",
                "         Move Player",
            ])
        else:
            stats_lines.extend([
                "Headless Mode",
                "(No Interactive",
                " Controls)",
            ])

        stats_lines.extend(["", "Ctrl+C   Exit"])

        stats_text = "\n".join(stats_lines)
        self.stats_text.set_text(stats_text)

    def _print_performance_stats(self):
        """Print performance statistics to console"""
        if not self.print_stats or not self.start_time:
            return

        elapsed = time.time() - self.start_time
        if elapsed > 5:  # Print every 5 seconds
            fps = self.frame_count / elapsed
            pos = self.env._get_player_position()
            map_id = self.env._get_map_id()
            steps = self.env.state['steps']
            visited = len(self.env.state['visited_maps'])

            stats = f"⚡ {fps:.1f} FPS | 🎮 {self.frame_count:,} frames | " \
                   f"👟 {steps:,} steps | 🗺️ {visited} maps | " \
                   f"📍 ({pos[0]}, {pos[1]}) | Map {map_id}"

            if self.show_dir:
                stats += f" | ➡️ {len(self.movement_history)} moves"

            print(stats)

            # Reset timer
            self.start_time = time.time()
            self.frame_count = 0

    def run(self, duration_seconds=None, max_frames=None):
        """
        Run the game with optimized rendering

        Args:
            duration_seconds: Run for N seconds (None = run indefinitely)
            max_frames: Run for N frames (None = run indefinitely)
        """
        print("\n🎮 Game starting...")
        print()

        # Load game
        print("⏳ Loading game...")
        for _ in range(240):  # ~4 seconds at 60fps
            self.env.pyboy.tick()
        print("✅ Game loaded!\n")

        self.start_time = time.time()
        target_frame_time = 1.0 / self.max_fps if self.max_fps > 0 else 0

        try:
            while self.env.pyboy.tick():
                frame_start = time.time()
                self.frame_count += 1

                # Update overlay at reduced rate
                if self.show_overlay and (self.frame_count % self.overlay_refresh_rate == 0):
                    self._update_overlay()

                # Print stats periodically
                self._print_performance_stats()

                # Check termination conditions
                if max_frames and self.frame_count >= max_frames:
                    print(f"\n✅ Reached max frames ({max_frames})")
                    break

                if duration_seconds:
                    elapsed = time.time() - self.start_time
                    if elapsed >= duration_seconds:
                        print(f"\n✅ Reached duration ({duration_seconds}s)")
                        break

                # FPS limiting
                if target_frame_time > 0:
                    elapsed = time.time() - frame_start
                    if elapsed < target_frame_time:
                        time.sleep(target_frame_time - elapsed)

        except KeyboardInterrupt:
            print("\n\n⏸️  Interrupted by user")
        finally:
            self._cleanup()

    def _cleanup(self):
        """Cleanup resources"""
        total_time = time.time() - self.start_time if self.start_time else 0
        avg_fps = self.frame_count / total_time if total_time > 0 else 0

        print(f"\n📊 Final Stats:")
        print(f"   Frames: {self.frame_count:,}")
        print(f"   Duration: {total_time:.1f}s")
        print(f"   Average FPS: {avg_fps:.1f}")
        print(f"   Steps: {self.env.state['steps']:,}")
        print(f"   Maps Visited: {len(self.env.state['visited_maps'])}")

        if self.show_dir:
            print(f"   Total Movements: {len(self.movement_history)}")
            print(f"   Unique Tiles Visited: {len(self.visited_tiles)}")

        if self.show_overlay:
            plt.ioff()
            plt.close()
        self.env.pyboy.stop()
        print("✅ Cleanup complete!")


def run_optimized(
    rom_path="pokered_experimental/pokeblue.gbc",
    show_pyboy_window=False,
    show_info=False,
    show_tiles=False,
    show_dir=False,
    overlay_refresh_rate=2,
    max_fps=60,
    duration_seconds=None,
    max_frames=None
):
    """
    Convenience function to run optimized debug session

    Examples:
        # Just the game, no overlays
        run_optimized(show_pyboy_window=True)

        # Interactive with info panel
        run_optimized(show_pyboy_window=True, show_info=True)

        # All overlays
        run_optimized(show_pyboy_window=True, show_info=True, show_tiles=True, show_dir=True)

        # Training mode (no display)
        run_optimized(max_fps=0)
    """
    runner = OptimizedDebugRunner(
        rom_path=rom_path,
        show_pyboy_window=show_pyboy_window,
        show_info=show_info,
        show_tiles=show_tiles,
        show_dir=show_dir,
        overlay_refresh_rate=overlay_refresh_rate,
        max_fps=max_fps,
        print_stats=True
    )
    runner.run(duration_seconds=duration_seconds, max_frames=max_frames)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Optimized Pokemon Blue Debug Runner with Modular Overlays')
    parser.add_argument('--rom', default='pokered_experimental/pokeblue.gbc', help='ROM path')
    parser.add_argument('--pyboy-window', action='store_true', help='Show PyBoy SDL2 window for interactive play')

    # Modular overlay flags
    parser.add_argument('--info', action='store_true', help='Show info panel with game statistics')
    parser.add_argument('--tiles', action='store_true', help='Show tile grid overlay (16x16 pixel grid)')
    parser.add_argument('--dir', action='store_true', help='Show movement direction arrows')

    parser.add_argument('--overlay-rate', type=int, default=2, help='Overlay refresh rate (frames)')
    parser.add_argument('--fps', type=int, default=60, help='Max FPS (0=unlimited)')
    parser.add_argument('--duration', type=int, help='Run duration in seconds')
    parser.add_argument('--frames', type=int, help='Max number of frames to run')

    args = parser.parse_args()

    run_optimized(
        rom_path=args.rom,
        show_pyboy_window=args.pyboy_window,
        show_info=args.info,
        show_tiles=args.tiles,
        show_dir=args.dir,
        overlay_refresh_rate=args.overlay_rate,
        max_fps=args.fps,
        duration_seconds=args.duration,
        max_frames=args.frames
    )
