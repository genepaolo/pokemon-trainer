"""
Optimized PyBoy runner with side panel stats
Much faster than ppew_debug.py - suitable for training multiple instances

Features:
1. Headless mode for training (no PyBoy window)
2. SDL2 mode for interactive play (PyBoy handles controls)
3. Side panel for stats (no screen clutter)
4. Configurable overlay refresh rate
5. Clean, modern UI design
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env.pyboy_pokeblue_env_walker import PyBoyPokeBlueEnvWalker
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import time

class OptimizedDebugRunner:
    def __init__(
        self,
        rom_path,
        show_pyboy_window=False,
        show_overlay=True,
        overlay_refresh_rate=2,
        max_fps=60,
        print_stats=True
    ):
        """
        Args:
            rom_path: Path to Pokemon ROM
            show_pyboy_window: Show PyBoy SDL2 window (for interactive play with arrow keys)
            show_overlay: Show matplotlib with side panel stats
            overlay_refresh_rate: Update display every N frames
            max_fps: Target FPS (0 = unlimited)
            print_stats: Print performance statistics to console
        """
        self.show_overlay = show_overlay
        self.show_pyboy_window = show_pyboy_window
        self.overlay_refresh_rate = overlay_refresh_rate
        self.max_fps = max_fps
        self.print_stats = print_stats
        self.frame_count = 0
        self.start_time = None

        # Choose window type
        # For interactive play: use SDL2 window (PyBoy handles keyboard input)
        # For training: use null window (headless, no display)
        window_mode = "SDL2" if show_pyboy_window else "null"

        print(f"🎮 Initializing PyBoy in {window_mode} mode...")
        print(f"📊 Side Panel: {'ON' if show_overlay else 'OFF'}")
        print(f"⚡ Max FPS: {max_fps if max_fps > 0 else 'UNLIMITED'}")

        if show_pyboy_window:
            print("💡 TIP: Use arrow keys in the PyBoy window to move!")
        else:
            print("💡 Running in headless mode (no display)")

        # Create environment
        self.env = PyBoyPokeBlueEnvWalker(
            rom_path,
            debug_overlay=False,  # We'll handle overlay ourselves
            window_type=window_mode
        )

        # Setup matplotlib with side panel
        self.fig = None
        self.ax_game = None
        self.ax_stats = None
        self.img_plot = None
        self.stats_text = None

        if show_overlay:
            self._setup_ui()

    def _setup_ui(self):
        """Setup matplotlib UI with game screen and side panel"""
        plt.ion()

        # Create figure with GridSpec for layout
        self.fig = plt.figure(figsize=(12, 6))
        gs = GridSpec(1, 2, figure=self.fig, width_ratios=[2, 1], wspace=0.1)

        # Game screen (left)
        self.ax_game = self.fig.add_subplot(gs[0])
        self.ax_game.axis('off')

        title = "Pokemon Blue"
        if self.show_pyboy_window:
            title += " - Use Arrow Keys in PyBoy Window"
        else:
            title += " - Headless Mode"
        self.ax_game.set_title(title, fontsize=12, fontweight='bold', pad=10)

        # Stats panel (right)
        self.ax_stats = self.fig.add_subplot(gs[1])
        self.ax_stats.axis('off')

        # Pre-create game screen image
        dummy_img = np.zeros((144, 160, 3), dtype=np.uint8)
        self.img_plot = self.ax_game.imshow(dummy_img, interpolation='nearest')

        # Stats panel background
        self.ax_stats.set_facecolor('#1e1e1e')

        # Create stats text placeholder
        self.stats_text = self.ax_stats.text(
            0.05, 0.95, "",
            transform=self.ax_stats.transAxes,
            fontfamily='monospace',
            fontsize=10,
            verticalalignment='top',
            color='#00ff00'
        )

    def _update_overlay(self):
        """Update game screen and stats panel"""
        if not self.show_overlay:
            return

        # Update game screen
        screen_array = self.env.pyboy.screen.ndarray
        self.img_plot.set_data(screen_array)

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

        # Format stats text with better spacing
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
            f"   X: {pos[0]:3d}",
            f"   Y: {pos[1]:3d}",
            "",
            f"🗺️  Map ID: {map_id}",
            f"👟 Steps: {steps:,}",
            f"🌍 Maps Visited: {visited}",
            "",
            "╔══════════════════════╗",
            "║   CONTROLS           ║",
            "╚══════════════════════╝",
            "",
        ]

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

        plt.draw()
        plt.pause(0.001)

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

            print(f"⚡ {fps:.1f} FPS | 🎮 {self.frame_count:,} frames | "
                  f"👟 {steps:,} steps | 🗺️ {visited} maps | "
                  f"📍 ({pos[0]}, {pos[1]}) | Map {map_id}")

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

        if self.show_overlay:
            plt.ioff()
            plt.close()
        self.env.pyboy.stop()
        print("✅ Cleanup complete!")


def run_optimized(
    rom_path="pokered_experimental/pokeblue.gbc",
    show_pyboy_window=False,
    show_overlay=True,
    overlay_refresh_rate=2,
    max_fps=60,
    duration_seconds=None,
    max_frames=None
):
    """
    Convenience function to run optimized debug session

    Examples:
        # Default: headless with side panel at 60fps
        run_optimized()

        # Interactive play with PyBoy window
        run_optimized(show_pyboy_window=True)

        # Maximum speed for training (no visual output)
        run_optimized(show_overlay=False, max_fps=0)
    """
    runner = OptimizedDebugRunner(
        rom_path=rom_path,
        show_pyboy_window=show_pyboy_window,
        show_overlay=show_overlay,
        overlay_refresh_rate=overlay_refresh_rate,
        max_fps=max_fps,
        print_stats=True
    )
    runner.run(duration_seconds=duration_seconds, max_frames=max_frames)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Optimized Pokemon Blue Debug Runner')
    parser.add_argument('--rom', default='pokered_experimental/pokeblue.gbc', help='ROM path')
    parser.add_argument('--pyboy-window', action='store_true', help='Show PyBoy SDL2 window for interactive play')
    parser.add_argument('--no-overlay', action='store_true', help='Disable matplotlib overlay')
    parser.add_argument('--overlay-rate', type=int, default=2, help='Overlay refresh rate (frames)')
    parser.add_argument('--fps', type=int, default=60, help='Max FPS (0=unlimited)')
    parser.add_argument('--duration', type=int, help='Run duration in seconds')
    parser.add_argument('--frames', type=int, help='Max number of frames to run')

    args = parser.parse_args()

    run_optimized(
        rom_path=args.rom,
        show_pyboy_window=args.pyboy_window,
        show_overlay=not args.no_overlay,
        overlay_refresh_rate=args.overlay_rate,
        max_fps=args.fps,
        duration_seconds=args.duration,
        max_frames=args.frames
    )
