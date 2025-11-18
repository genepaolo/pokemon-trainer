# Creating a Custom Map for RL Training (Walking Simulator)

This guide shows you how to create a simple custom map for your RL training environment - a walking simulator with no battles, no wild pokemon, and a clear goal.

## Overview

You **don't need to edit .blk files directly**. Instead, you'll:
1. Use an unused map slot (UNUSED_MAP_0B)
2. Copy a simple existing map's .blk file as a template
3. Create minimal header and object files
4. Register the map in the game
5. Set it as your starting location

## Step-by-Step Guide

### Step 1: Choose a Map ID

We'll use `UNUSED_MAP_0B` (map ID $0B) which is already defined but unused.

**File**: `pokered_experimental/constants/map_constants.asm`

**Line 31**: Change from:
```asm
map_const UNUSED_MAP_0B,                  0,  0 ; $0B
```

To:
```asm
map_const TRAINING_MAP,                   10, 10 ; $0B - 10x10 tiles for RL training
```

### Step 2: Create Map Header

**File**: `pokered_experimental/data/maps/headers/TrainingMap.asm` (create new file)

```asm
map_header TrainingMap, TRAINING_MAP, OVERWORLD, 0
; No connections - isolated training environment
end_map_header
```

**Key points**:
- `TRAINING_MAP` - the constant we defined
- `OVERWORLD` - tileset type (can also use `HOUSE` for indoor)
- `0` - no map connections (isolated)

### Step 3: Create Map Objects File

**File**: `pokered_experimental/data/maps/objects/TrainingMap.asm` (create new file)

```asm
object_const_def
; No object constants needed for a simple walking simulator

TrainingMap_Object:
	db $a ; border block (wall tile)

	def_warp_events
	; No warps - isolated map

	def_bg_events
	; Optional: Add a sign or goal marker
	; bg_event 9, 9, TEXT_TRAINING_MAP_GOAL

	def_object_events
	; No NPCs, no trainers, no battles

	def_warps_to TRAINING_MAP
```

**Key points**:
- `border block` - tile used for map edges (usually `$a` for walls)
- No `warp_events` - prevents leaving the map
- No `object_events` - no NPCs or trainers
- Optional `bg_events` - can add a goal marker

### Step 4: Copy a Simple .blk File

Since .blk files are binary, we'll copy a simple existing map:

```bash
cd pokered_experimental/maps
# Copy a small indoor map as template (RedsHouse1F is simple)
cp RedsHouse1F.blk TrainingMap.blk
```

**Alternative**: Use a larger outdoor map:
```bash
# For a larger training area
cp PalletTown.blk TrainingMap.blk
```

**Note**: The .blk file defines the tile layout. You can't easily edit it, but copying a simple map gives you a working starting point.

### Step 5: Register the Map

**File**: `pokered_experimental/maps.asm`

Find a good place to add (after other map entries, around line 50-100):

```asm
INCLUDE "data/maps/headers/TrainingMap.asm"
INCLUDE "data/maps/objects/TrainingMap.asm"
TrainingMap_Blocks: INCBIN "maps/TrainingMap.blk"
```

### Step 6: Update Map Header Pointers

**File**: `pokered_experimental/data/maps/map_header_pointers.asm`

**Line 15**: Change from:
```asm
	dw SaffronCity_h ; UNUSED_MAP_0B
```

To:
```asm
	dw TrainingMap_h ; TRAINING_MAP (was UNUSED_MAP_0B)
```

### Step 7: Add Map to Other Required Files

#### Map Header Banks
**File**: `pokered_experimental/data/maps/map_header_banks.asm`

Find the entry for map $0B (around line 12) and change:
```asm
	db BANK(SaffronCity_h) ; UNUSED_MAP_0B
```

To:
```asm
	db BANK(TrainingMap_h) ; TRAINING_MAP
```

#### Map Names
**File**: `pokered_experimental/data/maps/names.asm`

Add:
```asm
	db "TRAINING MAP@"
```

#### Map Songs
**File**: `pokered_experimental/data/maps/songs.asm`

Find the entry for map $0B and set a song:
```asm
	db MUSIC_PALLET_TOWN, BANK(Music_PalletTown) ; TRAINING_MAP
```

#### Sprite Sets
**File**: `pokered_experimental/data/maps/sprite_sets.asm`

Find the entry for map $0B and set:
```asm
	db SPRITESET_PALLET_VIRIDIAN ; TRAINING_MAP
```

### Step 8: Set as Starting Location

**File**: `pokered_experimental/data/maps/special_warps.asm`

**Line 47-48**: Change `NewGameWarp`:
```asm
NewGameWarp:
    special_warp_spec TRAINING_MAP, 5, 5, OVERWORLD
```

**File**: `pokered_experimental/engine/overworld/special_warps.asm`

**Line 79**: Update the fly warp data (for debug mode):
```asm
.PalletTown:     fly_warp TRAINING_MAP,      5,  5
```

Or better, make debug mode use NewGameWarp (see Option 2 in the main documentation).

### Step 9: Build and Test

```bash
cd pokered_experimental
make clean
make pokeblue.gbc
```

Test with PyBoy:
```bash
python3 env/ppew_debug.py
```

## Simplifying Further: Remove All Encounters

### Disable Wild Pokemon

Wild pokemon only spawn on routes/overworld maps. Since we're using `OVERWORLD` tileset, you might get wild encounters. To disable:

**Option A**: Use `HOUSE` tileset instead (no wild pokemon):
```asm
map_header TrainingMap, TRAINING_MAP, HOUSE, 0
```

**Option B**: Create an empty wild data entry (more complex).

### Remove All NPCs

Your objects file already has no `object_events`, so no NPCs will spawn.

### Remove Warps

Your objects file already has no `warp_events`, so the map is isolated.

## Adding a Goal

### Option 1: Background Event (Sign)

In `TrainingMap.asm` objects file:
```asm
	def_bg_events
	bg_event 9, 9, TEXT_TRAINING_MAP_GOAL
```

Then create a text constant (in a text file) that says "GOAL REACHED!" or similar.

### Option 2: Detect Position in RL Environment

In your `pyboy_pokeblue_env_walker.py`, check if player reaches goal coordinates:
```python
def _check_goal(self):
    pos = self._get_player_position()
    goal_pos = np.array([9, 9])  # Goal at (9, 9)
    return np.array_equal(pos, goal_pos)
```

### Option 3: Use a Specific Tile

The .blk file defines tiles. You can't easily edit it, but you can:
- Copy a map that has a distinctive tile (like a door or special floor)
- Use that tile as your goal
- Detect when player is on that tile type

## Recommended Map Setup for RL Training

### Minimal Training Map

**Size**: 10x10 tiles (small enough to learn quickly)
**Tileset**: `HOUSE` (no wild pokemon)
**Connections**: None (isolated)
**Objects**: None (no NPCs, no trainers)
**Goal**: Reach coordinate (9, 9) or a specific tile

### Example: Simple Corridor

If you want a more interesting layout, you could:
1. Copy `RedsHouse1F.blk` (simple indoor map)
2. The layout will be a small house - perfect for learning navigation
3. Goal: Reach a specific room or tile

### Example: Open Field

1. Copy `PalletTown.blk` (larger outdoor map)
2. Remove all NPCs and warps
3. Goal: Navigate to a specific corner

## Troubleshooting

### Map doesn't load
- Check that all files are created
- Verify map_header_pointers.asm has the correct entry
- Check map_header_banks.asm has the correct bank

### White screen
- Make sure the .blk file exists
- Check that the map is registered in maps.asm
- Verify tileset type matches (OVERWORLD vs HOUSE)

### Can't move
- Check border block is set correctly
- Verify map dimensions match the .blk file size

### Wild pokemon appear
- Change tileset from `OVERWORLD` to `HOUSE`
- Or disable wild pokemon data (more complex)

## Next Steps

1. **Start simple**: Use `RedsHouse1F.blk` as template (small, indoor, no wild pokemon)
2. **Test navigation**: Make sure player can move around
3. **Add goal detection**: Implement goal checking in your RL environment
4. **Iterate**: Once it works, you can experiment with different layouts

## Alternative: Modify Existing Map

If creating a new map seems complex, you can also:

1. **Modify Pallet Town** to be isolated:
   - Remove connections in `PalletTown.asm` header
   - Remove all objects in `PalletTown.asm` objects file
   - Use it as your training map

2. **Use an existing simple map**:
   - `RedsHouse1F` - small indoor map
   - `Daycare` - simple building
   - Set one of these as starting location

See `HOW_TO_ALTER_MAPS.md` for more details on modifying existing maps.

