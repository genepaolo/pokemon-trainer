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

class PyBoyPokeBlueEnvWalker(gym.Env):
    def __init__(self, rom_path):
        self.pyboy = pyboy.PyBoy(rom_path)
        self.screen = self.pyboy.screen
        self.action_space = gym.spaces.Discrete(4)
        