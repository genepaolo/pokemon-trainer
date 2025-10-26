# Pokémon RL Project — Reinforcement Learning with Game Boy Pokémon Blue

## 🎯 Goal
Train a reinforcement learning (RL) agent to **play a real Pokémon Blue–style ROM**, not a look-alike.
The agent will interact with a genuine Game Boy ROM via an emulator, while we customize maps and content
through the community **pokered disassembly** project.

---

## 🧩 Architecture Overview

| Layer | Component | Purpose |
|:--|:--|:--|
| **Game Engine** | Pokémon Blue ROM (built from `pokered`) | Authentic gameplay logic and mechanics |
| **Emulator** | [PyBoy](https://github.com/Baekalfen/PyBoy) | Headless, scriptable Game Boy emulator |
| **Environment Wrapper** | `pyboy_pokered_env.py` | Converts emulator state → Gymnasium API (obs, reward, done) |
| **RL Framework** | [Stable-Baselines3 (SB3)](https://github.com/DLR-RM/stable-baselines3) | PPO/DQN training algorithms |
| **Custom Content** | Edited maps, events, and trainers in `pokered/` | Define small, deterministic “training routes” for the agent |

---

## 🏗️ Project Layout

poke-rl/
├── README.md
├── envs/
│ └── pyboy_pokered_env.py # Gym wrapper for PyBoy
├── train/
│ └── train_ppo.py # SB3 PPO training script
├── pokered/ # Disassembly (git submodule or clone)
│ ├── maps/
│ └── ...
├── data/
│ └── baserom.gbc # legally obtained Pokémon Blue ROM dump
├── logs/
│ └── tb/ # TensorBoard logs
├── requirements.txt
└── LICENSE

markdown
Copy code

---

## ⚙️ Dependencies

| Tool | Purpose | Install |
|------|----------|---------|
| **Python ≥ 3.9** | main scripting language | — |
| **PyBoy** | Emulator bridge | `pip install pyboy` |
| **Gymnasium** | Env interface | `pip install gymnasium` |
| **Stable-Baselines3** | RL algorithms | `pip install stable-baselines3` |
| **RGBDS toolchain** | Assembler for `pokered` | see `pokered/INSTALL.md` |
| **Make / GNU build tools** | build disassembly | system package manager |

Example:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
🕹️ Step 1 — Build a Custom ROM (using pokered)
Clone the disassembly

bash
Copy code
git clone https://github.com/pret/pokered.git
cd pokered
Provide your legally-owned baserom

bash
Copy code
cp /path/to/PokemonBlue.gb baserom.gbc
Install RGBDS and build

bash
Copy code
make
This produces poke_blue.gbc.

Customize maps and events

Edit map data in maps/ and data/maps/.

Change the player’s start location and warps in constants/map_constants.asm.

Re-run make to rebuild your ROM.

Result → poke_blue.gbc with your custom training route.

⚖️ You must supply your own ROM dump. Distribution of copyrighted ROMs is illegal.

🤖 Step 2 — Wrap the Emulator as a Gym Environment
Implement envs/pyboy_pokered_env.py:

Launch PyBoy headless with your ROM.

Expose actions {Up, Down, Left, Right, A, B, Start}.

Read memory addresses for:

map ID

player (x, y)

in-battle flag

HP values

Convert these plus the screen buffer to the observation vector.

Return (obs, reward, done, info) each step.

Reward suggestions:

Event	Reward
Step / move	−0.01
Discover new tile	+0.1
Defeat wild/trainer	+5
Reach goal tile	+20
Faint	−10

🧠 Step 3 — Train with Stable-Baselines3
train/train_ppo.py example:

python
Copy code
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from envs.pyboy_pokered_env import PokeBlueEnv

def make_env():
    return PokeBlueEnv(rom_path="data/poke_blue.gbc")

if __name__ == "__main__":
    env = DummyVecEnv([make_env])
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./logs/tb")
    model.learn(total_timesteps=500_000)
    model.save("ppo_poke_blue")
Monitor training:

bash
Copy code
tensorboard --logdir ./logs/tb
📈 Curriculum (Progressive Difficulty)
Phase	Description	Features Enabled
A	Navigation only	Overworld movement to goal
B	Random encounters	Wild battles with fixed odds
C	Trainer battles	Deterministic scripted encounters
D	Full route	Items, HP management, multi-trainer path

🧩 Optional Extensions
Add RAM taps for bag items, badges, XP.

Build visual debugging overlay for state display.

Implement curriculum scheduler (train on easy map → harder).

Replace PPO with DQN or IMPALA for pixel-based learning.

Automate ROM rebuilds with make && pytest envs/test_env.py.

⚠️ Legal Notice
This project interacts with copyrighted game data.
You are responsible for supplying your own legally-dumped ROM.
Do not share ROMs, save states, or game assets publicly.

🧭 Next Steps
✅ Confirm pokered builds correctly with your baserom.

✅ Write and test pyboy_pokered_env.py.

🚀 Train a small PPO model to reach a goal tile.

🔁 Iterate on reward shaping and map complexity.

🎓 Extend to trainer battles and multi-map navigation.

📚 References
PyBoy Docs: https://github.com/Baekalfen/PyBoy/wiki

pokered Disassembly: https://github.com/pret/pokered

Gen-1 RAM Map: https://datacrystal.romhacking.net/wiki/Pokémon_Red_and_Blue:RAM_map

Stable-Baselines3 Docs: https://stable-baselines3.readthedocs.io/

Gymnasium Docs: https://gymnasium.farama.org/

🧾 License
This README and sample code are provided under the MIT License.
Pokémon and related assets are © Nintendo / Game Freak / Creatures Inc.
No endorsement or association implied.