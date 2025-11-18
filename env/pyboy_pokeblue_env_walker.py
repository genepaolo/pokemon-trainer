"""
This file is the environment for the Pokémon Blue game.
This is specifically to learn about the gymnasium environment and how to use it.
The goal is to learn how to use the gymnasium environment to train a agent to walk around the overworld.


Key Design Questions:
- What skills should the agent learn?
    - Navigate the overworld, explore new areas
    - Reach a goal position (gym)
- What information does the agent need?
    - The current map ID
    - The current map's layout
    - The player's position
    - The player's available actions
- What actions can the agent take?
    - Move up, down, left, right
- How do we measure success?
    - Exploring new areas (Better rewards in less steps)
    - Reaching the goal position (Immediate reward)
- How do we measure failure?
    - Hitting a wall (Immediate penalty, point)
    - Running out of time (Immediate failure)
    - Not reaching the goal position in certain amount of steps (Immediate failure)
- When should episodes end?
    - When the player reaches the goal position
    - When the player fails
"""

import pyboy
import gymnasium as gym
import numpy as np
from PIL import Image, ImageDraw, ImageFont

class PyBoyPokeBlueEnvWalker(gym.Env):

    # These are the documented Pokemon Red/Blue memory addresses
    ADDRESS_Y_COORD = 0xD361   # Player Y position
    ADDRESS_X_COORD = 0xD362   # Player X position
    ADDRESS_CUR_MAP = 0xD35E   # Current map ID

    def __init__(self, rom_path, debug_overlay=True, window_type="SDL2"):
        # Initialize PyBoy Emulator and stores the screen reference
        # window_type: "SDL2" for visible window, "headless" for no window
        self.pyboy = pyboy.PyBoy(rom_path, window_type=window_type)
        self.screen = self.pyboy.screen
        # Initialize Action Space (4 actions: up, down, left, right)
        self.action_space = gym.spaces.Discrete(4)
        # Define Observation Space
        # What should the agent observe?
        # Let's start simple: [x, y, map_id, steps]
        # self.observation_space = gym.spaces.Box(low=0, high=255, shape=(4, ), dtype=np.uint8)
        self.observation_space = gym.spaces.Dict({
            'curr_pos': gym.spaces.Box(low=0, high=255, shape=(2, ), dtype=np.uint8),
            'map_id': gym.spaces.Discrete(256),
        })

        # Define State
        # Used to calculate rewards, check termination conditions
        # `observation_space`: Defines the shape/types of observations the agent receives.
        #`state`: Internal runtime variables you track (e.g., steps, visited maps).
        self.state = {
            'steps': 0,
            'visited_maps': set(),
            'prev_pos': None,
            'curr_pos': np.array([0, 0]),
        }
        self.max_steps = 10000

        # Debug Overlay
        self.debug_overlay = debug_overlay
        self.font = ImageFont.load_default()

    """
    Pyboy Memory Helper Functions
    def _get_player_position(self):
        # Get the player's position

    """

    def _get_map_id(self):
        # Get the current map ID
        return self.pyboy.memory[self.ADDRESS_CUR_MAP]

    def _get_player_position(self):
        # Get the player's position
        return self.pyboy.memory[self.ADDRESS_X_COORD], self.pyboy.memory[self.ADDRESS_Y_COORD]
    
    """

    Important Environment Functions

    """

    def _get_observation(self):
        # Get the observation
        return {
            'curr_pos': self.observation_space['curr_pos'],
            'map_id': self.observation_space['map_id'],
        }
    
    def reset(self):
        # Reset the Env
        self.pyboy.reset()
        # Getting additiona info from state before resetting
        info = {
            'steps': self.state['steps'],
            'visited_map_count': len(self.state['visited_maps']),
        }

        # Reset State
        self.state = {
            'steps': 0,
            'visited_maps': set(),
            'prev_pos': None,
            'curr_pos': np.array([0, 0]),
        }
        # Return Observation with additional info
        obs = self._get_observation()
        return obs, info

    def step(self, action):
        """Execute action and return (obs, reward, done, truncated, info)"""
        # Map actions, action = (0,1,2,3) randomly selected from action space
        button_map = {
            0: pyboy.WindowEvent.PRESS_ARROW_UP,
            1: pyboy.WindowEvent.PRESS_ARROW_DOWN,
            2: pyboy.WindowEvent.PRESS_ARROW_LEFT,
            3: pyboy.WindowEvent.PRESS_ARROW_RIGHT,
        }
        button = button_map[action]
        self.pyboy.send_input(button)
        # Run emulation for a few frames and calculate new state
        for _ in range(10):
            self.pyboy.tick()
        self.state['steps'] += 1
        self.state['prev_pos'] = self.state['curr_pos']
        self.state['curr_pos'] = self._get_player_position()
        self.state['visited_maps'].add(self._get_map_id())

        # Calculate rewards based on state 
        reward = self._calculate_reward() 

        #Check Termination Conditions
        termianted = False
        truncated = self
        
    """

    Debugging Helper Functions

    """

    def _get_debug_info(self):
        # Get the debug info
        return {
            'steps': self.state['steps'],
            'curr_pos': self.state['curr_pos'],
            'visited_map_count': len(self.state['visited_maps']),
        }

    def _draw_debug_overlay(self, screen_image):
        # Draw the debug overlay on the screen image
        # Convert screen image to PIL Image if it's a numpy array
        if isinstance(screen_image, np.ndarray):
            img = Image.fromarray(screen_image)
        else:
            img = screen_image.copy()
        
        # If debug overlay is disabled, return original image
        if not self.debug_overlay:
            return img

        # Prepare debug info
        pos = self._get_player_position()
        map_id = self._get_map_id()
        debug_info = [
            f"Position: ({pos[0]}, {pos[1]})",
            f"Map ID: {map_id}",
            f"Steps: {self.state['steps']}",
            f"Visited Maps: {len(self.state['visited_maps'])}",
        ]

        # Draw semi-transparent background
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        # Calculate text box size
        text_height = 15
        box_height = len(debug_info) * text_height + 10
        box_width = 200

        # Draw background box
        overlay_draw.rectangle(
            [(5, 5), (box_width, box_height)],
            fill=(0, 0, 0, 180),  # Semi-transparent black
            outline=(255, 255, 255, 255)
        )

        # Draw Text
        y_offset = 10
        for line in debug_info:
            overlay_draw.text(
                (10, y_offset),
                line,
                fill=(255, 255, 255, 255),
                font=self.font,
            )
            y_offset += text_height

        # Composite overlay back onto original image
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        return img

    def render(self, mode='human'):
        """
        Render the environment with debug overlay.
        
        Args:
            mode: 'human' - PyBoy window displays automatically (overlay shown separately)
                  'rgb_array' - Returns numpy array with overlay applied
        
        Returns:
            For 'human' mode: None (PyBoy window updates automatically)
            For 'rgb_array' mode: numpy array (144, 160, 3) with debug overlay
        """
        # Get the screen buffer
        screen_array = self.pyboy.screen.ndarray
        
        if mode == 'human':
            # PyBoy window updates automatically - we can't directly overlay on it
            # But we can return the image with overlay for external display
            # For now, just let PyBoy handle the display
            # The overlay can be viewed via 'rgb_array' mode or separate window
            return None
        elif mode == 'rgb_array':
            # Return RGB array with debug overlay applied
            screen_with_overlay = self._draw_debug_overlay(screen_array)
            # Convert PIL Image back to numpy array if needed
            if isinstance(screen_with_overlay, Image.Image):
                return np.array(screen_with_overlay)
            return screen_with_overlay
        else:
            return None


