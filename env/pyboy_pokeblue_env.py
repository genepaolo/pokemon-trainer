"""
This file is the environment for the Pokémon Blue game.
It is a wrapper around the PyBoy emulator that provides a Gymnasium environment.

Key Design Questions:
- What skills should the agent learn?
    - Navigate the overworld, explore new areas
    - Catch Pokémon (use items, throw pokeballs, etc.)
    - Battle wild Pokémon (random encounters, gain experience, level up)
    - Battle trainers (scripted encounters, gain experience, level up, earn money)
    - Use PokeCenter (heal your Pokémon)
    - Use PokeMart (buy items) 
    - Battle Boss (Beat the gym, beat the game)
- What information does the agent need?
    - The current map ID
    - The current map's layout
    - The player's position
    - The player's inventory (items, money, etc.)
    - The player's Pokémon (level, experience, stats, moves, etc.)
    - The player's available actions
- What actions can the agent take?
    - Move up, down, left, right, start, select
- How do we measure success?
    - Catching Pokemon
    - Winning battles
    - Earning Money
    - Healing Pokemon (relative to missing team's HP)
    - Defeating the singular gym leader/boss of our game
- When should episodes end?
    - When the player beats the singular gym leader/boss of our game
    - When we reach an x amount of steps/actions
    - When the player runs out of time
"""

import pyboy
import gymnasium as gym
import numpy as np

class PyBoyPokeBlueEnv(gym.Env):
    def __init__(self, rom_path):
        self.pyboy = pyboy.PyBoy(rom_path)
        self.screen = self.pyboy.screen
        self.action_space = gym.spaces.Discrete(8)