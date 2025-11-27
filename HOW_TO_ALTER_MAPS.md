# How to Alter Pokemon Maps for RL Training

## 🔧 Direct Map Modification (Hard Way)

### Option 1: Swap .blk Files (Easiest)
Since .blk files are binary, the easiest approach is to **swap existing maps**:

```bash
cd pokered_experimental/

# Example: Make Pallet Town use a different map layout
cp maps/ViridianCity.blk maps/PalletTown.blk
# Or copy a small house map
cp maps/RedsHouse1F.blk maps/PalletTown.blk
```

### Option 2: Edit Map Dimensions (Simple)
Change map sizes in constants file:

Edit `pokered_experimental/constants/map_constants.asm`:

```asm
; BEFORE
map_const PALLET_TOWN, 10, 9  ; 10 wide, 9 tall

; AFTER - Make it smaller for easier navigation
map_const PALLET_TOWN, 5, 5   ; 5 wide, 5 tall
```

**Note**: This requires you to also edit the .blk file or create a new one.

### Option 3: Modify Map Connections (Easier)
Change where maps connect:

Edit `pokered_experimental/data/maps/headers/PalletTown.asm`:

```asm
; BEFORE - Pallet Town can go north to Route 1
map_header PalletTown, PALLET_TOWN, OVERWORLD, NORTH | SOUTH
connection north, Route1, ROUTE_1, 0
connection south, Route21, ROUTE_21, 0
end_map_header

; AFTER - Block all connections for training
map_header PalletTown, PALLET_TOWN, OVERWORLD, 0
end_map_header
```

## 🎯 Recommended Approach: Create a Simple Test Map

### Step 1: Create New Map Constant

Edit `pokered_experimental/constants/map_constants.asm`:

Find an unused map ID (like `UNUSED_MAP_0B`) and change it:

```asm
; BEFORE
map_const UNUSED_MAP_0B, 0, 0

; AFTER - Create your training map
map_const TRAINING_MAP, 5, 5  ; 5x5 tiles
```

### Step 2: Create Map Files

Create `pokered_experimental/data/maps/headers/TrainingMap.asm`:

```asm
map_header TrainingMap, TRAINING_MAP, OVERWORLD, 0
; No connections - just a standalone test area
end_map_header
```

### Step 3: Copy Small Map as Starting Point

```bash
# Use a small house map as template
cp pokered_experimental/maps/RedsHouse1F.blk pokered_experimental/maps/TrainingMap.blk
```

### Step 4: Register the Map

Add to `pokered_experimental/maps.asm`:

```asm
INCLUDE "data/maps/headers/TrainingMap.asm"
INCLUDE "data/maps/objects/TrainingMap.asm"
TrainingMap_Blocks: INCBIN "maps/TrainingMap.blk"
```

### Step 5: Add to Map Header Pointers

Edit `pokered_experimental/data/maps/map_header_pointers.asm`:

Find unused map entry and change:

```asm
dw TrainingMap_h  ; Instead of UNUSED_MAP_0B_h
```

## 🚀 Quick Start: Simplest Modification

For your RL agent, the **simplest approach** is:

### 1. Make Pallet Town Self-Contained

Edit `pokered_experimental/data/maps/headers/PalletTown.asm`:

```asm
map_header PalletTown, PALLET_TOWN, OVERWORLD, 0
end_map_header
```

This removes all map connections, creating a closed training environment.

### 2. Modify Map Size

Edit `pokered_experimental/constants/map_constants.asm`:

```asm
map_const PALLET_TOWN, 10, 10  ; Keep same size, or make it smaller
```

### 3. Build Your Test ROM

```bash
cd pokered_experimental/
make blue
```

You'll get `pokeblue.gbc` with your modifications!

## 🎮 Testing Your Map Changes

Once you've built the ROM:

```bash
# Test in an emulator
open pokered_experimental/pokeblue.gbc

# Or test with PyBoy
python3 -c "from pyboy import PyBoy; pb = PyBoy('pokered_experimental/pokeblue.gbc')"
```

## 📚 Understanding Map Connections

Map connections work like this:

```asm
connection DIRECTION, MapName, MAP_CONSTANT, offset

; Example:
connection north, Route1, ROUTE_1, 0
```

- **DIRECTION**: `north`, `south`, `east`, `west`
- **MapName**: Symbol name of connected map
- **MAP_CONSTANT**: Constant from map_constants.asm
- **offset**: Where to connect (0 = center)

To isolate a map for training, **remove all connections**.

## 🎯 For Your RL Training

**Recommendation**: Start by making Pallet Town:
1. **Smaller** (10x10 → 5x5)
2. **Isolated** (no map connections)
3. **Simple** (copy RedsHouse1F.blk as base)

This creates a small, contained environment perfect for training navigation!

---

## Creating a Walking Simulator (No Battles, No NPCs)

This section covers how to create a pure walking simulator for RL training by disabling wild pokemon encounters, removing NPCs, and setting up multi-map navigation.

### Disable Wild Pokemon Battles

**File**: `pokered_experimental/data/wild/grass_water.asm`

The `WildDataPointers` table maps each map to its wild pokemon data. To disable encounters on any route or map, change its entry to `NothingWildMons`:

**Example for Route 1** (line 15):
```asm
; BEFORE
dw Route1WildMons          ; ROUTE_1

; AFTER
dw NothingWildMons         ; ROUTE_1 - No wild encounters
```

**What `NothingWildMons` does**:
```asm
NothingWildMons:
    def_grass_wildmons 0 ; encounter rate = 0
    end_grass_wildmons
    def_water_wildmons 0 ; encounter rate = 0
    end_water_wildmons
```

**Key Points**:
- Setting a route to `NothingWildMons` disables encounters even if grass tiles exist
- You don't need to remove grass tiles from the .blk file
- This works for any map (routes, towns, cities)

### Remove NPCs from Maps

**File**: `pokered_experimental/data/maps/objects/[MapName].asm`

Remove or comment out the `def_object_events` section:

**Example for Pallet Town**:
```asm
; BEFORE
def_object_events
    object_event  8,  5, SPRITE_OAK, STAY, NONE, TEXT_PALLETTOWN_OAK
    object_event  3,  8, SPRITE_GIRL, WALK, ANY_DIR, TEXT_PALLETTOWN_GIRL
    object_event 11, 14, SPRITE_FISHER, WALK, ANY_DIR, TEXT_PALLETTOWN_FISHER

; AFTER
def_object_events
    ; No NPCs - removed for RL training
```

**Example for Route 1**:
```asm
; BEFORE
def_object_events
    object_event  5, 24, SPRITE_YOUNGSTER, WALK, UP_DOWN, TEXT_ROUTE1_YOUNGSTER1
    object_event 15, 13, SPRITE_YOUNGSTER, WALK, LEFT_RIGHT, TEXT_ROUTE1_YOUNGSTER2

; AFTER
def_object_events
    ; No NPCs - removed for RL training
```

**Key Points**:
- Empty `def_object_events` section removes all NPCs
- This also removes trainers (no forced battles)
- NPCs won't spawn even if the .blk file has space for them

### Remove Grass Tiles (Optional)

**Note**: Grass tiles are defined in the `.blk` file (binary), so you can't easily edit them directly. However:

- **You don't need to remove grass tiles** - setting wild pokemon to `NothingWildMons` prevents encounters even if grass tiles exist
- **If you want to remove grass visually**, you can:
  - Copy a map without grass (like an indoor map) as your template
  - Use a town/city map that has minimal grass
  - The grass will still be there visually, but encounters are disabled

### Multi-Map Setup (Town → Route → Town)

To create a walking trainer that can navigate between multiple maps:

#### Step 1: Set Up Map Connections

**File**: `pokered_experimental/data/maps/headers/PalletTown.asm`
```asm
map_header PalletTown, PALLET_TOWN, OVERWORLD, NORTH
connection north, Route1, ROUTE_1, 0
end_map_header
```

**File**: `pokered_experimental/data/maps/headers/Route1.asm`
```asm
map_header Route1, ROUTE_1, OVERWORLD, NORTH | SOUTH
connection south, PalletTown, PALLET_TOWN, 0
connection north, ViridianCity, VIRIDIAN_CITY, -5
end_map_header
```

**File**: `pokered_experimental/data/maps/headers/ViridianCity.asm`
```asm
map_header ViridianCity, VIRIDIAN_CITY, OVERWORLD, SOUTH
connection south, Route1, ROUTE_1, 5
end_map_header
```

#### Step 2: Disable Wild Pokemon on Routes

**File**: `pokered_experimental/data/wild/grass_water.asm` (line 15):
```asm
dw NothingWildMons         ; ROUTE_1 - No wild encounters for RL training
```

#### Step 3: Remove NPCs from All Maps

Remove NPCs from:
- `data/maps/objects/PalletTown.asm`
- `data/maps/objects/Route1.asm`
- `data/maps/objects/ViridianCity.asm`

Set all `def_object_events` sections to empty:
```asm
def_object_events
    ; No NPCs - removed for RL training
```

#### Step 4: Set Starting Location

**File**: `pokered_experimental/data/maps/special_warps.asm` (line 47-48):
```asm
NewGameWarp:
    special_warp_spec PALLET_TOWN, 5, 6, OVERWORLD
```

### Complete Example: Pallet Town → Route 1 → Viridian City

Here's a complete setup for a three-map walking simulator:

1. **Disable Wild Pokemon on Route 1**
   - File: `pokered_experimental/data/wild/grass_water.asm` (line 15)
   - Change: `dw Route1WildMons` → `dw NothingWildMons`

2. **Remove NPCs from Pallet Town**
   - File: `pokered_experimental/data/maps/objects/PalletTown.asm`
   - Empty the `def_object_events` section

3. **Remove NPCs from Route 1**
   - File: `pokered_experimental/data/maps/objects/Route1.asm`
   - Empty the `def_object_events` section

4. **Remove NPCs from Viridian City**
   - File: `pokered_experimental/data/maps/objects/ViridianCity.asm`
   - Empty the `def_object_events` section

5. **Verify Map Connections**
   - Check that header files have proper connections (they should already be set)

6. **Set Starting Location**
   - File: `pokered_experimental/data/maps/special_warps.asm`
   - Set `NewGameWarp` to start in Pallet Town

**Result**: A three-map walking simulator where the agent can:
- Start in Pallet Town
- Walk north to Route 1 (no wild pokemon encounters)
- Walk north to Viridian City
- Navigate back and forth between all three maps
- No NPCs, no battles, no forced encounters

### Quick Reference Table

| Task | Solution | File |
|------|----------|------|
| **Disable wild pokemon** | Change to `NothingWildMons` | `data/wild/grass_water.asm` |
| **Remove NPCs** | Empty `def_object_events` | `data/maps/objects/[Map].asm` |
| **Remove grass tiles** | Not needed (set encounters to 0) | N/A (or copy non-grass .blk) |
| **Multi-map setup** | Set connections + disable encounters + remove NPCs | Multiple files |

### Recommended Approach

For RL training, the simplest approach is:

1. **Use existing maps** (Pallet Town, Route 1, Viridian City)
2. **Disable wild pokemon** on Route 1 by setting it to `NothingWildMons`
3. **Remove NPCs** from all three maps
4. **Keep map connections** so the agent can travel between them
5. **Set starting location** to Pallet Town

This gives you a working three-map walking simulator with no battles or NPCs, perfect for training navigation RL agents.

