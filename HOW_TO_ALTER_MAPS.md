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

