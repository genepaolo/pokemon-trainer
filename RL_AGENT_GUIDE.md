# RL Agent Development Guide for Pokemon Blue

## Table of Contents
1. [Introduction](#introduction)
2. [Understanding Your Environment](#understanding-your-environment)
3. [RL Concepts for Pokemon Blue](#rl-concepts-for-pokemon-blue)
4. [Step-by-Step Training Process](#step-by-step-training-process)
5. [Choosing an RL Algorithm](#choosing-an-rl-algorithm)
6. [Implementation Checklist](#implementation-checklist)
7. [Common Challenges & Solutions](#common-challenges--solutions)
8. [Resources & Next Steps](#resources--next-steps)

---

## Introduction

This guide will help you build an RL agent to play Pokemon Blue. Your agent will learn to navigate the overworld, explore areas, and eventually complete objectives.

### What You're Building
- **Simple Walker**: Agent learns to move around without getting stuck
- **Explorer**: Agent discovers new map areas and avoids walls
- **Goal Seeker**: Agent navigates to specific locations (gym, PokeCenter, etc.)
- **Advanced Player**: Eventually learns to catch Pokemon, battle, and complete objectives

---

## Understanding Your Environment

### Current Files

**File**: env/pyboy_pokeblue_env_walker.py (39 lines - incomplete)
- **Purpose**: Walk around the overworld
- **Status**: Needs implementation

**File**: env/pyboy_pokeblue_env.py (43 lines - incomplete)
- **Purpose**: Full game interaction
- **Status**: Needs implementation

### Key Components to Implement

```python
class PyBoyPokeBlueEnvWalker(gym.Env):
    def __init__(self, rom_path):
        # TODO: Initialize PyBoy emulator
        # TODO: Define observation space
        # TODO: Define action space
        
    def reset(self, seed=None):
        # TODO: Start new game/episode
        # TODO: Return initial observation
        # TODO: Return info dict
        
    def step(self, action):
        # TODO: Execute action
        # TODO: Update game state
        # TODO: Calculate reward
        # TODO: Check if done/truncated
        # TODO: Return (observation, reward, terminated, truncated, info)
        
    def render(self, mode='human'):
        # TODO: Display current game state
        pass
```

---

## RL Concepts for Pokemon Blue

### 1. Observation Space
**What the agent sees:**

```python
observation_space = gym.spaces.Dict({
    'screen': gym.spaces.Box(0, 255, (144, 160, 3), dtype=np.uint8),  # Screen pixels
    'map_id': gym.spaces.Discrete(256),  # Current map
    'player_pos': gym.spaces.Box(0, 256, (2,), dtype=np.uint8),  # (x, y)
    'inventory': gym.spaces.Box(0, 255, (20,), dtype=np.uint8),  # Items
    'pokemon_count': gym.spaces.Discrete(6),  # How many Pokemon
})
```

**Key Observations for Walker:**
- Player position (x, y) on current map
- Map ID (which location player is in)
- Screen pixels (raw visual input)
- Collision map (where walls are)

### 2. Action Space
**What the agent can do:**

```python
action_space = gym.spaces.Discrete(4)

# Actions:
# 0 = Up (↑)
# 1 = Down (↓)
# 2 = Left (←)
# 3 = Right (→)

# For full game, you'd add:
# 5 = A (interact, confirm)
# 6 = B (cancel, run)
# 7 = Start (menu)
```

### 3. Reward Structure
**How to design rewards:**

#### Simple Walker Rewards:
```python
def calculate_reward(self):
    reward = 0
    
    # Distance-based reward (encourage exploration)
    distance_from_start = sqrt((x - start_x)**2 + (y - start_y)**2)
    reward += distance_from_start * 0.01
    
    # New map bonus (explore new areas)
    if current_map_id not in self.visited_maps:
        reward += 10
        self.visited_maps.add(current_map_id)
    
    # Wall collision penalty
    if self.hit_wall:
        reward -= 1
    
    # Reached goal (massive bonus)
    if at_goal_position:
        reward += 100
    
    return reward
```

#### Advanced Rewards:
```python
def calculate_reward(self):
    reward = 0
    
    # Battle rewards
    if won_battle:
        reward += 50
    if caught_pokemon:
        reward += 25
    
    # Health-related
    if pokemon_health_increased:
        reward += pokemon_health_gained * 0.1
    
    # Economy
    money_gained = current_money - previous_money
    reward += money_gained * 0.01
    
    return reward
```

### 4. Episode Termination
**When episodes end:**

```python
def is_episode_done(self):
    # Success conditions
    if reached_gym:
        return True, "Success! Reached gym"
    if battled_elite_four:
        return True, "Success! Beat game"
    
    # Failure conditions
    if all_pokemon_fainted:
        return True, "Failed! Team wiped"
    if money <= 0 and no_items:
        return True, "Failed! Out of resources"
    
    # Timeout
    if steps >= max_steps:
        return True, "Timeout"
    
    return False, "Continue"
```

---

## Step-by-Step Training Process

### Phase 1: Basic Walking (Week 1)

**Goal**: Agent learns to move without getting stuck

**Implementation:**
```python
# Simple observation: just player position
observation_space = gym.spaces.Box(
    low=0, high=256, shape=(2,), dtype=np.uint8  # (x, y)
)

# Simple actions: 4 movement directions
action_space = gym.spaces.Discrete(4)

# Simple reward: distance traveled
def calculate_reward(self):
    return abs(current_x - last_x) + abs(current_y - last_y)

# Simple termination: stuck in same position
if stayed_in_same_position_for_10_steps:
    done = True
```

**Expected Learning:**
- Agent learns that moving = reward
- Agent learns to avoid not pressing buttons (staying still)
- Agent doesn't yet understand walls

### Phase 2: Wall Avoidance (Week 2)

**Goal**: Agent learns not to hit walls

**Implementation:**
```python
# Observation: position + collision info
observation_space = gym.spaces.Box(
    low=0, high=256, shape=(6,), dtype=np.uint8
    # [x, y, can_move_up, can_move_down, can_move_left, can_move_right]
)

# Reward: distance - collision penalty
def calculate_reward(self):
    reward = distance_traveled
    if hit_wall:
        reward -= 5  # Strong penalty
    return reward
```

**Expected Learning:**
- Agent learns that hitting walls = negative reward
- Agent learns to explore in valid directions
- Agent starts navigating more efficiently

### Phase 3: Goal Seeking (Week 3)

**Goal**: Agent learns to reach specific locations

**Implementation:**
```python
# Observation: position + goal position
observation_space = gym.spaces.Box(
    low=0, high=256, shape=(4,), dtype=np.uint8
    # [x, y, goal_x, goal_y]
)

# Reward: closer to goal = better
def calculate_reward(self):
    distance_to_goal = sqrt((x - goal_x)**2 + (y - goal_y)**2)
    reward = 100 - distance_to_goal  # Closer = higher reward
    if reached_goal:
        reward += 1000
    return reward
```

**Expected Learning:**
- Agent learns to navigate toward targets
- Agent learns to plan paths
- Agent develops spatial understanding

### Phase 4: Advanced (Weeks 4+)

**Goal**: Full game interaction

**Implementation:**
```python
# Rich observation: screen + game state
observation_space = gym.spaces.Dict({
    'screen': Box(0, 255, (144, 160, 3)),
    'map_id': Discrete(256),
    'position': Box(0, 256, (2,)),
    'pokemon_count': Discrete(6),
    'has_pokeball': Discrete(2),
})

# Complex reward: multiple objectives
def calculate_reward(self):
    reward = 0
    reward += exploration_bonus()
    reward += battle_reward()
    reward += catch_pokemon_reward()
    reward += gym_battle_reward()
    return reward
```

**Expected Learning:**
- Agent understands game mechanics
- Agent learns to use menus, items, Pokemon
- Agent develops strategic thinking

---

## Choosing an RL Algorithm

### For Beginners: Start Simple

#### 1. **DQN (Deep Q-Network)** - Recommended First Choice
**Why**: Good for discrete actions (like Pokemon controls)
**When**: Limited observation space (position, map, etc.)
**Pros**: 
- Well-documented
- Stable learning
- Works with screens as input
**Cons**: 
- Can be slow to train
- Memory intensive

```python
# Using Stable-Baselines3
from stable_baselines3 import DQN

model = DQN('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=10000)
```

#### 2. **PPO (Proximal Policy Optimization)** - For Complex Tasks
**Why**: Good for complex, high-dimensional observations
**When**: Using screen pixels as input
**Pros**: 
- Works well with images
- More stable than vanilla policy gradient
- Good for continuous and discrete actions
**Cons**: 
- More hyperparameters to tune
- Requires more compute

```python
from stable_baselines3 import PPO

model = PPO('CnnPolicy', env, verbose=1)  # CnnPolicy for image input
model.learn(total_timesteps=50000)
```

#### 3. **A2C (Advantage Actor-Critic)** - Fast Training
**Why**: Faster than PPO, simpler than DQN
**When**: Medium complexity tasks
**Pros**: 
- Faster iterations
- Good balance
**Cons**: 
- Less stable than PPO
- May need more tuning

---

## Implementation Checklist

### Step 1: Complete Environment Implementation

**File**: env/pyboy_pokeblue_env_walker.py

See the current implementation and add missing methods.

### Step 2: Train Your First Agent

**Create**: train_walker.py

```python
import gymnasium as gym
from stable_baselines3 import DQN
from env.pyboy_pokeblue_env_walker import PyBoyPokeBlueEnvWalker

# Create environment
env = PyBoyPokeBlueEnvWalker('pokeblue.gbc')

# Create and train agent
model = DQN(
    'MlpPolicy', 
    env,
    verbose=1,
    learning_rate=0.0001,
    buffer_size=10000,
    learning_starts=1000,
)

# Train for 10,000 steps
model.learn(total_timesteps=10000)

# Save model
model.save('walker_model')

# Test the model
obs, info = env.reset()
for i in range(100):
    action, _states = model.predict(obs)
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        obs, info = env.reset()

env.close()
```

### Step 3: Read Memory for Real Observations

**Install**: PyBoy memory reading

```bash
pip install pyboy
```

**Example**: Reading player position

```python
def _get_player_position(self):
    """Read actual player position from game memory"""
    # These addresses vary by game version
    # You'll need to find these using a memory editor
    
    player_y = self.pyboy.memory[0x13FE]  # Player Y position
    player_x = self.pyboy.memory[0x13FF]  # Player X position
    
    return (player_x, player_y)

def _get_map_id(self):
    """Read current map ID"""
    map_id = self.pyboy.memory[0x13F0]  # Current map ID
    return map_id
```

**Finding Memory Addresses:**
1. Use BGB emulator (Debug → Memory Viewer)
2. Play game and note your position
3. Search memory for that value
4. Move and find the bytes that change

### Step 4: Monitor Training

**Create**: monitor_training.py

```python
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import EvalCallback

# Wrap environment with Monitor
env = Monitor(PyBoyPokeBlueEnvWalker('pokeblue.gbc'), 'logs/')

# Create evaluation callback
eval_callback = EvalCallback(
    env, 
    best_model_save_path='./best_model/',
    log_path='./logs/',
    eval_freq=1000,
    deterministic=True,
)

# Train with monitoring
model = DQN('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=50000, callback=eval_callback)
```

### Step 5: Visualize Results

**Install**: TensorBoard

```bash
pip install tensorboard
tensorboard --logdir=./logs/
```

Open browser: `http://localhost:6006`

---

## Common Challenges & Solutions

### Challenge 1: Agent Doesn't Learn

**Symptoms**: Agent doesn't improve, always random behavior

**Solutions**:
- Increase reward magnitude (make rewards bigger)
- Simplify environment (start with basic walking)
- Increase training time (learn for more steps)
- Check that observations are correct

### Challenge 2: Agent Exploits Rewards

**Symptoms**: Agent does same thing repeatedly for small rewards

**Solutions**:
- Add exploration bonus (reward for new areas)
- Penalize repetitive behavior
- Use entropy bonus (encourage diverse actions)

### Challenge 3: Too Slow Training

**Symptoms**: Takes hours to see any progress

**Solutions**:
- Use `headless` mode (disable rendering during training)
- Reduce observation space (use simpler observations)
- Use CPU instead of GPU (if using screen pixels)
- Reduce step complexity (fewer frames per action)

### Challenge 4: Memory Issues

**Symptoms**: Out of memory errors

**Solutions**:
- Reduce replay buffer size
- Don't store full screen in replay buffer
- Use smaller neural network
- Train in shorter episodes

---

## Resources & Next Steps

### Essential Reading

1. **OpenAI Spinning Up**: https://spinningup.openai.com/
   - Best RL tutorial
   - Explains key concepts clearly

2. **Stable-Baselines3 Docs**: https://stable-baselines3.readthedocs.io/
   - Complete API reference
   - Example code

3. **Gymnasium Docs**: https://gymnasium.farama.org/
   - How to create environments
   - Standard interface

### Books

1. **Deep Reinforcement Learning** by Pieter Abbeel
   - Theory and practice
   - Andrew Ng's course materials

2. **Reinforcement Learning: An Introduction** by Sutton & Barto
   - Classic textbook
   - Free online

### Practical Tutorials

1. **Train Pong Agent**: https://stable-baselines3.readthedocs.io/en/master/guide/tutorial.html
   - Start here
   - Complete working example

2. **Create Custom Environment**: https://gymnasium.farama.org/tutorials/environment_creation/
   - Step-by-step
   - Your Pokemon env is custom

### Communities

1. **r/reinforcementlearning**: Reddit community
2. **Stable-Baselines3 Discord**: Active help
3. **OpenAI Discord**: RL discussions

### Next Steps

**This Week**:
1. ✅ Complete environment implementation
2. ✅ Implement memory reading
3. ✅ Create train script
4. ✅ Train first agent
5. ✅ Watch agent fail hilariously

**Next Week**:
1. Improve reward structure
2. Add wall collision detection
3. Train for 50k steps
4. Visualize agent behavior

**Month 1 Goal**: Agent walks around without getting stuck

**Month 2 Goal**: Agent explores new areas

**Month 3 Goal**: Agent reaches specific goals

**Final Goal**: Agent completes game objectives


