# Pokemon Blue Walker Map - Experimental Changes

This document tracks all changes made to create an isolated walking simulator map (Pallet Town → Route 1 → Viridian City) for RL training.

**Status: ✅ COMPLETE AND WORKING**

---

## Goal

Create a 3-map walking environment with:
- ✅ **No NPCs** (no dialogue requiring A button)
- ✅ **No wild Pokémon** (no battles on Route 1)
- ✅ **Isolated maps**: Pallet Town ↔ Route 1 ↔ Viridian City (dead ends on both sides)
- ✅ **Building warps kept** (adds complexity for future training)
- ✅ **Signs kept** (passive - only trigger with A button)

---

## Map Layout

```
                    ┌─────────────────────────────────┐
                    │       VIRIDIAN CITY             │
                    │         (20×18 tiles)           │
                    │                                 │
                    │    Dead end - no exit north     │
                    │    Dead end - no exit west      │
                    │    Buildings accessible         │
                    │    No NPCs                      │
                    └───────────────┬─────────────────┘
                                    │ (south exit only)
                                    │
                    ┌───────────────┴─────────────────┐
                    │          ROUTE 1                │
                    │         (10×18 tiles)           │
                    │                                 │
                    │    Grass - NO wild battles      │
                    │    No NPCs                      │
                    │                                 │
                    └───────────────┬─────────────────┘
                                    │
                                    │
                    ┌───────────────┴─────────────────┐
                    │        PALLET TOWN              │
                    │         (10×9 tiles)            │
                    │                                 │
                    │    START: spawn at (5,6)        │
                    │    Dead end - no exit south     │
                    │    Buildings accessible         │
                    │    No NPCs (Oak removed)        │
                    │    Oak cutscene DISABLED        │
                    └─────────────────────────────────┘
```

---

## All Changes Made

### Change 1: Pallet Town Header - Remove South Connection

**File:** `data/maps/headers/PalletTown.asm`

**Original:**
```asm
map_header PalletTown, PALLET_TOWN, OVERWORLD, NORTH | SOUTH
connection north, Route1, ROUTE_1, 0
connection south, Route21, ROUTE_21, 0
end_map_header
```

**Modified:**
```asm
map_header PalletTown, PALLET_TOWN, OVERWORLD, NORTH
connection north, Route1, ROUTE_1, 0

end_map_header
```

**Effect:** Player cannot exit south to Route 21.

⚠️ **Critical:** The connection flags (`NORTH`) MUST match the actual connections defined. Mismatch causes game crash!

---

### Change 2: Pallet Town Objects - Remove NPCs

**File:** `data/maps/objects/PalletTown.asm`

**Removed from `def_object_events`:**
```asm
object_event  8,  5, SPRITE_OAK, STAY, NONE, TEXT_PALLETTOWN_OAK
object_event  3,  8, SPRITE_GIRL, WALK, ANY_DIR, TEXT_PALLETTOWN_GIRL
object_event 11, 14, SPRITE_FISHER, WALK, ANY_DIR, TEXT_PALLETTOWN_FISHER
```

**Kept intact:**
- `const_export` lines (PALLETTOWN_OAK, PALLETTOWN_GIRL, PALLETTOWN_FISHER) - required by scripts
- `warp_event` lines (building doors)
- `bg_event` lines (signs)

---

### Change 3: Pallet Town Script - Skip Oak Encounter

**File:** `scripts/PalletTown.asm`

**Original:**
```asm
PalletTownDefaultScript:
	CheckEvent EVENT_FOLLOWED_OAK_INTO_LAB
```

**Modified:**
```asm
PalletTownDefaultScript:
	ret ; RL Training: Skip Oak encounter entirely
	CheckEvent EVENT_FOLLOWED_OAK_INTO_LAB
```

**Effect:** The "Hey wait! Don't go out!" cutscene is completely skipped.

---

### Change 4: Route 1 Objects - Remove NPCs

**File:** `data/maps/objects/Route1.asm`

**Removed from `def_object_events`:**
```asm
object_event  5, 24, SPRITE_YOUNGSTER, WALK, UP_DOWN, TEXT_ROUTE1_YOUNGSTER1
object_event 15, 13, SPRITE_YOUNGSTER, WALK, LEFT_RIGHT, TEXT_ROUTE1_YOUNGSTER2
```

**Kept intact:**
- `const_export` lines (ROUTE1_YOUNGSTER1, ROUTE1_YOUNGSTER2)
- `bg_event` lines (sign)

---

### Change 5: Route 1 Wild Pokémon - Disabled

**File:** `data/wild/grass_water.asm`

**Line 15, Original:**
```asm
dw Route1WildMons          ; ROUTE_1
```

**Modified:**
```asm
dw NothingWildMons         ; ROUTE_1
```

**Effect:** Walking through grass on Route 1 will NOT trigger wild Pokémon battles.

---

### Change 6: Viridian City Header - Remove North and West Connections

**File:** `data/maps/headers/ViridianCity.asm`

**Original:**
```asm
map_header ViridianCity, VIRIDIAN_CITY, OVERWORLD, NORTH | SOUTH | WEST
connection north, Route2, ROUTE_2, 5
connection south, Route1, ROUTE_1, 5
connection west, Route22, ROUTE_22, 4
end_map_header
```

**Modified:**
```asm
map_header ViridianCity, VIRIDIAN_CITY, OVERWORLD, SOUTH

connection south, Route1, ROUTE_1, 5

end_map_header
```

**Effect:** Player cannot exit north to Route 2 or west to Route 22. Viridian City is a dead-end.

---

### Change 7: Viridian City Objects - Remove NPCs

**File:** `data/maps/objects/ViridianCity.asm`

**Removed from `def_object_events`:**
```asm
object_event 13, 20, SPRITE_YOUNGSTER, WALK, ANY_DIR, TEXT_VIRIDIANCITY_YOUNGSTER1
object_event 30,  8, SPRITE_GAMBLER, STAY, NONE, TEXT_VIRIDIANCITY_GAMBLER1
object_event 30, 25, SPRITE_YOUNGSTER, WALK, ANY_DIR, TEXT_VIRIDIANCITY_YOUNGSTER2
object_event 17,  9, SPRITE_GIRL, STAY, RIGHT, TEXT_VIRIDIANCITY_GIRL
object_event 18,  9, SPRITE_GAMBLER_ASLEEP, STAY, NONE, TEXT_VIRIDIANCITY_OLD_MAN_SLEEPY
object_event  6, 23, SPRITE_FISHER, STAY, DOWN, TEXT_VIRIDIANCITY_FISHER
object_event 17,  5, SPRITE_GAMBLER, WALK, LEFT_RIGHT, TEXT_VIRIDIANCITY_OLD_MAN
```

**Kept intact:**
- `const_export` lines (all 7 NPC constants) - required by hide/show data
- `warp_event` lines (building doors)
- `bg_event` lines (signs)

---

## Summary Table

| File | Change | Lines Affected |
|------|--------|----------------|
| `data/maps/headers/PalletTown.asm` | Remove south connection | Line 1, remove line 3 |
| `data/maps/objects/PalletTown.asm` | Remove 3 NPCs | Lines 21-23 (emptied) |
| `scripts/PalletTown.asm` | Add `ret` to skip Oak | Line 22 (added) |
| `data/maps/objects/Route1.asm` | Remove 2 NPCs | Lines 14-15 (emptied) |
| `data/wild/grass_water.asm` | Disable wild Pokémon | Line 15 |
| `data/maps/headers/ViridianCity.asm` | Remove north/west connections | Lines 1-4 |
| `data/maps/objects/ViridianCity.asm` | Remove 7 NPCs | Lines 28-34 (emptied) |

---

## Build Commands

```bash
cd pokered_experimental
make pokeblue.gbc
```

## Test Command

```bash
python3 env/ppew_debug.py --pyboy-window --tiles --dir
```

---

## Key Learnings

1. **Header connection flags must match actual connections** - If you declare `NORTH | SOUTH` but only define a north connection, the game will crash or have invisible player.

2. **Keep `const_export` lines** - Even if you remove NPCs, keep the constant exports. Other files (scripts, hide_show_data) reference these constants.

3. **Scripts are separate from sprites** - Removing an NPC sprite doesn't remove the script events. Oak's encounter is triggered by a script checking player position, not by the Oak sprite.

4. **Wild data is separate from map layout** - Wild Pokémon are controlled by `grass_water.asm`, not by the map tiles or objects.

---

## Future Enhancements

- [ ] Remove building warps for simpler environment
- [ ] Add goal detection in RL environment (reach Viridian City)
- [ ] Create smaller custom training map
- [ ] Add reward shaping based on distance traveled
