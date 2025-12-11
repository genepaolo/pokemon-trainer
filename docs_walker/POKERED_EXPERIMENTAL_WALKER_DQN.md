# Pokemon Walker - DQN Learning Plan

A focused guide for learning Deep Q-Networks (DQN) by training an agent to navigate from Pallet Town → Route 1 → Viridian City.

---

## Table of Contents

1. [Understanding the Problem](#understanding-the-problem)
2. [RL Fundamentals](#rl-fundamentals)
3. [DQN Deep Dive](#dqn-deep-dive)
4. [Environment Design Decisions](#environment-design-decisions)
5. [Implementation Roadmap](#implementation-roadmap)
6. [Training & Debugging](#training--debugging)
7. [Scaling to SageMaker](#scaling-to-sagemaker)
8. [Resources](#resources)

---

## Understanding the Problem

### What We're Building

An RL agent that learns to walk from **Pallet Town** to **Viridian City** through **Route 1**.

```
┌─────────────────┐
│  VIRIDIAN CITY  │  ← GOAL
│    (20×18)      │
└────────┬────────┘
         │
┌────────┴────────┐
│    ROUTE 1      │
│    (10×18)      │
└────────┬────────┘
         │
┌────────┴────────┐
│  PALLET TOWN    │  ← START (5, 6)
│    (10×9)       │
└─────────────────┘
```

### Why DQN for Learning?

| Reason | Explanation |
|--------|-------------|
| **Foundational** | DQN introduced deep learning to RL - understanding it unlocks everything else |
| **Discrete actions** | Perfect for our 4-direction movement (Up, Down, Left, Right) |
| **Well-documented** | Extensive tutorials, papers, and implementations available |
| **Debuggable** | Q-values are interpretable - you can see what the agent is "thinking" |

---

## RL Fundamentals

### The Markov Decision Process (MDP)

Every RL problem is formalized as an MDP with 5 components:

| Component | Symbol | Our Walker Example |
|-----------|--------|-------------------|
| **States** | S | Player position (x, y) + map_id |
| **Actions** | A | {Up, Down, Left, Right} |
| **Transition** | P(s'|s,a) | Game physics (deterministic in our case) |
| **Reward** | R(s,a,s') | +1 at goal, shaped rewards for progress |
| **Discount** | γ | 0.99 (value future rewards almost as much as immediate) |

### The Goal

Find a **policy** π(a|s) that maximizes expected cumulative reward:

```
G_t = R_t + γR_{t+1} + γ²R_{t+2} + ... = Σ γ^k R_{t+k}
```

### Value Functions

**State Value V(s)**: Expected return starting from state s, following policy π
```
V^π(s) = E[G_t | S_t = s]
```

**Action Value Q(s,a)**: Expected return starting from state s, taking action a, then following π
```
Q^π(s,a) = E[G_t | S_t = s, A_t = a]
```

**Key Insight**: If we know the optimal Q*(s,a), the optimal policy is just:
```
π*(s) = argmax_a Q*(s,a)
```

---

## DQN Deep Dive

### The Bellman Equation

The foundation of Q-learning:

```
Q*(s,a) = E[R + γ max_a' Q*(s',a')]
```

In words: The value of taking action a in state s equals the immediate reward plus the discounted value of the best action in the next state.

### From Q-Learning to DQN

**Classic Q-Learning**: Store Q-values in a table
- Problem: Doesn't scale (our state space is huge)

**DQN Solution**: Use a neural network to approximate Q(s,a)
- Input: State (coordinates or pixels)
- Output: Q-value for each action

### Key DQN Innovations

#### 1. Experience Replay

**Problem**: Sequential samples are correlated → unstable training

**Solution**: Store experiences (s, a, r, s', done) in a replay buffer, sample randomly

```
Replay Buffer: [(s₁,a₁,r₁,s₁',done₁), (s₂,a₂,r₂,s₂',done₂), ...]
                            ↓ random sample
               Mini-batch for training
```

**Why it works**:
- Breaks correlation between consecutive samples
- Reuses experiences multiple times (data efficient)
- Smooths out learning over many past experiences

#### 2. Target Network

**Problem**: Q-network chases a moving target → oscillation/divergence

**Solution**: Use a separate "target" network that updates slowly

```
Loss = (r + γ max_a' Q_target(s',a') - Q_online(s,a))²
                ↑                        ↑
         Uses frozen weights      Updates every step
         
Every N steps: Q_target ← Q_online (hard update)
           or: Q_target ← τ*Q_online + (1-τ)*Q_target (soft update)
```

#### 3. ε-Greedy Exploration

**Problem**: Need to explore to find good strategies

**Solution**: With probability ε, take random action; otherwise take best action

```
ε starts high (1.0) → explore everything
ε decays over time → exploit learned knowledge
ε minimum (0.01) → always some exploration
```

### DQN Algorithm Summary

```
Initialize:
  - Q_online network with random weights
  - Q_target network (copy of Q_online)
  - Replay buffer (empty)
  - ε = 1.0

For each episode:
  s = env.reset()
  
  While not done:
    # Select action
    if random() < ε:
      a = random_action()
    else:
      a = argmax_a Q_online(s, a)
    
    # Take action
    s', r, done = env.step(a)
    
    # Store experience
    buffer.add(s, a, r, s', done)
    
    # Learn from replay
    if len(buffer) > batch_size:
      batch = buffer.sample(batch_size)
      
      # Calculate target
      target = r + γ * max_a' Q_target(s', a') * (1 - done)
      
      # Update Q_online
      loss = (target - Q_online(s, a))²
      optimizer.step()
    
    # Update target network
    if step % target_update_freq == 0:
      Q_target ← Q_online
    
    # Decay epsilon
    ε = max(ε_min, ε * decay_rate)
    
    s = s'
```

---

## Environment Design Decisions

### Decision 1: Observation Space

**Option A: Coordinates Only (Recommended for Start)**
```python
observation_space = Dict({
    'x': Discrete(256),      # X coordinate
    'y': Discrete(256),      # Y coordinate  
    'map_id': Discrete(256)  # Current map
})
# Or simply: Box(low=0, high=255, shape=(3,))
```

**Pros**: Fast, simple, small network needed
**Cons**: No visual understanding

**Option B: Screen Pixels (Advanced)**
```python
observation_space = Box(low=0, high=255, shape=(84, 84, 1))  # Grayscale, downsampled
```

**Pros**: Agent learns from visuals like humans
**Cons**: Much slower training, needs CNN

**Recommendation**: Start with coordinates. Add pixels later for learning CNNs.

### Decision 2: Action Space

```python
action_space = Discrete(4)  # Up, Down, Left, Right
```

**Mapping**:
| Action ID | Direction | PyBoy Key |
|-----------|-----------|-----------|
| 0 | Up | WindowEvent.PRESS_ARROW_UP |
| 1 | Down | WindowEvent.PRESS_ARROW_DOWN |
| 2 | Left | WindowEvent.PRESS_ARROW_LEFT |
| 3 | Right | WindowEvent.PRESS_ARROW_RIGHT |

### Decision 3: Reward Function

This is the **most critical** decision. Options:

**Sparse Reward (Hard to learn)**
```python
def get_reward(state, next_state, done):
    if reached_viridian_city(next_state):
        return +100
    return 0
```

**Distance-Based (Can get stuck)**
```python
def get_reward(state, next_state, done):
    # Reward for getting closer to Viridian City
    old_dist = distance_to_goal(state)
    new_dist = distance_to_goal(next_state)
    return old_dist - new_dist  # Positive if closer
```

**Exploration Bonus (Encourages wandering)**
```python
def get_reward(state, next_state, done):
    reward = 0
    tile_key = (next_state.x, next_state.y, next_state.map_id)
    
    if tile_key not in visited_tiles:
        reward += 1  # Bonus for new tile
        visited_tiles.add(tile_key)
    
    if reached_viridian_city(next_state):
        reward += 100
    
    return reward
```

**Recommended: Combination**
```python
def get_reward(state, next_state, done):
    reward = -0.01  # Small penalty per step (encourages efficiency)
    
    # Exploration bonus
    if is_new_tile(next_state):
        reward += 0.5
    
    # Map transition bonus
    if next_state.map_id > state.map_id:  # Moved north to new map
        reward += 10
    
    # Goal bonus
    if reached_viridian_city(next_state):
        reward += 100
    
    return reward
```

### Decision 4: Episode Termination

```python
def check_done(state, steps):
    # Success: Reached Viridian City
    if state.map_id == VIRIDIAN_CITY and in_goal_area(state):
        return True, "success"
    
    # Failure: Too many steps
    if steps >= MAX_STEPS:  # e.g., 5000
        return True, "timeout"
    
    # Failure: Entered a building (warp)
    if entered_building(state):
        return True, "warp"
    
    return False, None
```

---

## Implementation Roadmap

### Phase 1: Environment Wrapper (Week 1)

**Goal**: Create a proper Gym environment that DQN libraries can use

**Tasks**:
1. [ ] Implement `reset()` - Start new episode, return initial observation
2. [ ] Implement `step(action)` - Execute action, return (obs, reward, done, info)
3. [ ] Implement `_get_observation()` - Read game state from memory
4. [ ] Implement `_calculate_reward()` - Your reward function
5. [ ] Test manually - Play the game through the environment

**Validation**: 
- Run random actions for 1000 steps
- Verify observations change correctly
- Check reward values make sense

### Phase 2: Simple DQN (Week 2)

**Goal**: Implement basic DQN from scratch (for learning)

**Components to build**:
1. [ ] Replay Buffer class
2. [ ] Q-Network (simple MLP for coordinates)
3. [ ] Target Network (copy of Q-Network)
4. [ ] ε-greedy action selection
5. [ ] Training loop

**Network Architecture (for coordinates)**:
```
Input (3) → Dense(64) → ReLU → Dense(64) → ReLU → Dense(4)
                                                      ↑
                                              Q-value per action
```

**Hyperparameters to start**:
```
learning_rate = 0.001
gamma = 0.99
epsilon_start = 1.0
epsilon_end = 0.01
epsilon_decay = 0.995
batch_size = 64
buffer_size = 100000
target_update_freq = 1000
```

### Phase 3: Training & Debugging (Week 3)

**Goal**: Get the agent to learn something

**Metrics to track**:
- Episode reward (should increase over time)
- Episode length (should decrease if agent finds goal)
- Average Q-value (should increase as agent learns)
- Epsilon value (should decay)
- Buffer size (should fill up)

**Common issues**:
| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Reward stays flat | Reward too sparse | Add shaping |
| Q-values explode | Learning rate too high | Reduce LR |
| Agent oscillates | Target update too frequent | Increase update freq |
| Never explores | Epsilon decays too fast | Slower decay |
| Random behavior | Not learning | Check gradients, loss |

### Phase 4: Improvements (Week 4)

**Goal**: Implement DQN improvements

1. [ ] **Double DQN**: Fix Q-value overestimation
2. [ ] **Dueling DQN**: Separate value and advantage streams
3. [ ] **Prioritized Replay**: Sample important experiences more often
4. [ ] **Noisy Networks**: Replace ε-greedy with learned exploration

### Phase 5: Scale to SageMaker (Week 5+)

**Goal**: Train faster with cloud compute

1. [ ] Package environment as installable module
2. [ ] Create SageMaker training script
3. [ ] Configure hyperparameter tuning
4. [ ] Run distributed training

---

## Training & Debugging

### Logging Essentials

Track these every episode:
```python
log = {
    'episode': episode_num,
    'reward': total_reward,
    'length': steps,
    'epsilon': current_epsilon,
    'avg_q': mean_q_value,
    'loss': mean_loss,
    'buffer_size': len(replay_buffer)
}
```

### Visualization

Use your `ppew_debug.py` overlays:
```bash
# Watch agent learn in real-time
python3 env/ppew_debug.py --pyboy-window --tiles --dir --info
```

The arrow colors (green → red) show which tiles the agent revisits, helping debug reward hacking.

### Debugging Checklist

If training doesn't work:

1. **Environment check**: Run random policy, verify observations/rewards
2. **Buffer check**: Print samples, verify they look correct
3. **Network check**: Print Q-values for same state, verify they change
4. **Gradient check**: Print gradient norms, verify non-zero
5. **Loss check**: Plot loss over time, should decrease initially
6. **Reward check**: Plot episode rewards, should trend upward

---

## Scaling to SageMaker

### When to Move to SageMaker

- Local training takes too long (hours → days)
- You want to run many experiments in parallel
- You need GPU acceleration

### SageMaker RL Options

1. **Built-in Algorithms**: Ray RLlib, Coach
2. **Custom Script**: Bring your own training code
3. **Local Mode**: Test SageMaker code locally first

### Basic SageMaker Setup

```python
from sagemaker.rl import RLEstimator

estimator = RLEstimator(
    entry_point="train.py",
    source_dir="src/",
    role=sagemaker_role,
    framework="pytorch",
    toolkit="ray",
    instance_type="ml.m5.large",
    instance_count=1,
    hyperparameters={
        "learning_rate": 0.001,
        "gamma": 0.99,
        ...
    }
)

estimator.fit()
```

---

## Resources

### Papers to Read

1. **Playing Atari with Deep RL** (Mnih et al., 2013) - Original DQN
2. **Human-level control through deep RL** (Mnih et al., 2015) - Nature DQN
3. **Deep RL with Double Q-learning** (van Hasselt et al., 2016) - Double DQN
4. **Prioritized Experience Replay** (Schaul et al., 2016)
5. **Dueling Network Architectures** (Wang et al., 2016)

### Tutorials

- [Spinning Up in Deep RL](https://spinningup.openai.com/) - OpenAI's intro
- [Deep RL Course](https://huggingface.co/learn/deep-rl-course/) - Hugging Face
- [PyTorch DQN Tutorial](https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html)

### Libraries

- **Stable Baselines3**: Production-ready implementations
- **CleanRL**: Single-file implementations for learning
- **Ray RLlib**: Scalable, SageMaker-compatible

### Memory Addresses (For Environment)

```python
# Player position
ADDRESS_X = 0xD362
ADDRESS_Y = 0xD361
ADDRESS_MAP_ID = 0xD35E

# Map IDs
PALLET_TOWN = 0x00
VIRIDIAN_CITY = 0x01
ROUTE_1 = 0x0C
```

---

## Next Steps

1. **Read**: DQN paper (at least the algorithm section)
2. **Understand**: Each component of the algorithm
3. **Plan**: Write pseudocode for your implementation
4. **Build**: Start with the environment wrapper
5. **Test**: Verify environment works with random actions
6. **Implement**: Build DQN components one at a time
7. **Debug**: Use logging and visualization extensively
8. **Iterate**: Tune hyperparameters, add improvements

