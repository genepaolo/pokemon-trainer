# Pre-Oak Speech Flow - Game Initialization

## Overview
This document explains what happens before Oak's speech in Pokemon Red/Blue. This is crucial for understanding how the game initializes player data and sets up the beginning of the game.

## Files Involved

### Main Flow
- **File**: `pokered_experimental/engine/movie/oak_speech/oak_speech.asm`
- **Lines**: 1-65 (Pre-Speech Setup)
- **Lines**: 42-242 (Oak Speech Function)

### Related Data Files
- **File**: `pokered_experimental/engine/movie/title.asm`
- **Lines**: 412-416 (Debug Names)

- **File**: `pokered_experimental/data/player_names.asm`
- **Lines**: 17-31 (Default Player Names for Blue)

- **File**: `pokered/home/copy.asm`
- **Lines**: 15-24 (CopyData Function)

- **File**: `pokered/constants/text_constants.asm`
- **Line**: 1 (NAME_LENGTH = 11)

- **File**: `pokered/ram/wram.asm`
- **Line**: 1710 (wPlayerName memory address)
- **Line**: 1758 (wRivalName memory address)

---

## Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Game Start (New Game Selected)                             │
│  File: engine/menus/main_menu.asm, Line 314                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  PrepareOakSpeech() - Line 1                                │
│  File: engine/movie/oak_speech/oak_speech.asm             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Line 2-5: Save current game options                │  │
│  │   - Text speed, game settings                      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Line 13-20: Clear player and sprite data           │  │
│  │   - Zero out wPlayerName memory                    │  │
│  │   - Zero out wSpriteData memory                    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Line 33-40: Set default names                       │  │
│  │   FROM: "NINTEN" (title.asm:412)                    │  │
│  │   TO: wPlayerName (RAM location)                   │  │
│  │   FROM: "SONY" (title.asm:415)                      │  │
│  │   TO: wRivalName (RAM location)                     │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  OakSpeech() - Line 42                                      │
│  File: engine/movie/oak_speech/oak_speech.asm             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Line 43-44: Stop all music                          │  │
│  │   call PlaySound                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Line 45-48: Start route music                       │  │
│  │   Load Music_Routes2                                │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Line 49-50: Clear screen and load graphics          │  │
│  │   call ClearScreen                                   │  │
│  │   call LoadTextBoxTilePatterns                       │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Line 51: Call PrepareOakSpeech                      │  │
│  │   (Does all the name copying above)                 │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Line 52: Initialize player data                      │  │
│  │   predef InitPlayerData2                             │  │
│  │   - Sets starting money                              │  │
│  │   - Sets starting position                           │  │
│  │   - Initializes stats                               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Line 53-58: Give starting item                       │  │
│  │   ld a, POTION                                       │  │
│  │   ld a, 1 (quantity)                                │  │
│  │   call AddItemToInventory                           │  │
│  │   → Player gets 1 Potion in bag                     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Line 59-61: Set destination map                      │  │
│  │   ld [wDestinationMap], a                           │  │
│  │   call PrepareForSpecialWarp                        │  │
│  │   → Player will spawn in Pallet Town                │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Line 62-65: SKIP INTRO (Our modification)           │  │
│  │   ; SKIP INTRO - Always skip speech for RL          │  │
│  │   jp .skipSpeech                                    │  │
│  │   → Jumps past Oak dialog and name selection        │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  .skipSpeech - Line 102                                     │
│  Game continues to actual gameplay                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Code Walkthrough

### Step 1: PrepareOakSpeech (Lines 1-40)
**File**: `engine/movie/oak_speech/oak_speech.asm`

```asm
PrepareOakSpeech:
; Lines 2-5: Save current settings
    ld a, [wLetterPrintingDelayFlags]  ; Save text speed setting
    push af
    ld a, [wOptions]                   ; Save game options
    push af
    
; Lines 11-22: Save debug mode status
    ld a, [wStatusFlags6]
    push af
    
; Lines 13-16: Clear player name memory
    ld hl, wPlayerName                 ; Point to player name
    ld bc, wBoxDataEnd - wPlayerName   ; Calculate size
    xor a                              ; Set a = 0
    call FillMemory                    ; Fill memory with zeros
    
; Lines 17-20: Clear sprite data memory
    ld hl, wSpriteDataStart            ; Point to sprite data
    ld bc, wSpriteDataEnd - wSpriteDataStart
    xor a                              ; Set a = 0
    call FillMemory                    ; Fill memory with zeros
    
; Lines 21-22: Restore debug mode
    pop af
    ld [wStatusFlags6], a              ; Restore debug flag
    
; Lines 23-26: Restore options
    pop af
    ld [wOptions], a                   ; Restore options
    
; Lines 27-29: Initialize options if needed
    ld a, [wOptionsInitialized]
    and a                              ; Check if initialized
    call z, InitOptions                ; Init if not done yet
    
; Lines 33-36: Copy "NINTEN" to wPlayerName
    ld hl, DebugNewGamePlayerName      ; Source address
    ld de, wPlayerName                 ; Destination address
    ld bc, NAME_LENGTH                 ; Length (11 bytes)
    call CopyData                      ; Copy data
    
; Lines 37-40: Copy "SONY" to wRivalName
    ld hl, DebugNewGameRivalName       ; Source address
    ld de, wRivalName                  ; Destination address
    ld bc, NAME_LENGTH                 ; Length (11 bytes)
    jp CopyData                        ; Copy data and return
```

### Step 2: CopyData Function (Lines 15-24)
**File**: `pokered/home/copy.asm`

```asm
CopyData::
; Copy bc bytes from hl to de.
    ld a, [hli]       ; Load byte from [HL], then increment HL
    ld [de], a        ; Store byte to [DE]
    inc de            ; Increment DE (point to next byte)
    dec bc            ; Decrement BC (decrease counter)
    ld a, c           ; Load lower byte of counter
    or b              ; Check if counter is 0 (b OR c)
    jr nz, CopyData   ; Loop if not zero
    ret                ; Return when done
```

**How it works:**
1. `ld a, [hli]` - Load byte from source, auto-increment HL
2. `ld [de], a` - Write byte to destination
3. `inc de` - Move to next destination byte
4. `dec bc` - Decrement counter
5. Check if BC = 0, loop if not
6. Repeat until all bytes copied

### Step 3: OakSpeech Function (Lines 42-65)
**File**: `engine/movie/oak_speech/oak_speech.asm`

```asm
OakSpeech:
; Line 43-44: Stop all music
    ld a, SFX_STOP_ALL_MUSIC
    call PlaySound
    
; Line 45-48: Start route music
    ld a, BANK(Music_Routes2)     ; Get music bank
    ld c, a
    ld a, MUSIC_ROUTES2           ; Get music ID
    call PlayMusic                ; Start music
    
; Line 49-50: Clear screen and load graphics
    call ClearScreen              ; Clear the screen
    call LoadTextBoxTilePatterns  ; Load text box graphics
    
; Line 51: Prepare player data
    call PrepareOakSpeech         ; Set names and clear memory
    
; Line 52: Initialize player stats
    predef InitPlayerData2        ; Set money, position, etc.
    
; Lines 53-58: Give starting Potion
    ld hl, wNumBoxItems           ; Point to inventory
    ld a, POTION                  ; Item: Potion
    ld [wCurItem], a
    ld a, 1                       ; Quantity: 1
    ld [wItemQuantity], a
    call AddItemToInventory       ; Add to bag
    
; Lines 59-61: Set starting map
    ld a, [wDefaultMap]           ; Get Pallet Town
    ld [wDestinationMap], a
    call PrepareForSpecialWarp    ; Prepare to warp there
    
; Lines 62-65: SKIP INTRO (Our modification)
    xor a
    ldh [hTileAnimations], a
    ; SKIP INTRO - Always skip speech for RL training
    jp .skipSpeech                ; Jump past intro dialog
```

---

## Memory Locations

### Source Data (ROM)
**File**: `engine/movie/title.asm, Line 412-416`

```asm
DebugNewGamePlayerName:
    db "NINTEN@"      ; 6 characters + '@' terminator

DebugNewGameRivalName:
    db "SONY@"        ; 4 characters + '@' terminator
```

### Destination (RAM)
**File**: `ram/wram.asm`

```asm
Line 1710: wPlayerName:: ds NAME_LENGTH    ; 11 bytes in RAM
Line 1758: wRivalName:: ds NAME_LENGTH     ; 11 bytes in RAM
```

**Result in RAM:**
```
wPlayerName = "NINTEN\0\0\0\0\0"   ; 11 bytes
wRivalName  = "SONY\0\0\0\0\0\0\0" ; 11 bytes
```

---

## Constants

**File**: `constants/text_constants.asm, Line 1`

```asm
DEF NAME_LENGTH EQU 11    ; All names are 11 bytes
```

**Why 11 bytes?**
- Game Boy screen: 10 characters per line
- Plus 1 byte for null terminator or padding
- Stores names like "CHARIZARD", "NINTEN", etc.

---

## What Gets Copied (Byte by Byte)

### Player Name: "NINTEN"
```
Source:  'N' 'I' 'N' 'T' 'E' 'N' '@' '\0' '\0' '\0' '\0'
Address: +0  +1  +2  +3  +4  +5  +6   +7    +8    +9   +10

Copy to wPlayerName in RAM
```

### Rival Name: "SONY"
```
Source:  'S' 'O' 'N' 'Y' '@' '\0' '\0' '\0' '\0' '\0' '\0'
Address: +0  +1  +2  +3  +4   +5    +6    +7    +8    +9   +10

Copy to wRivalName in RAM
```

---

## Summary: Pre-Oak Speech Initialization

1. **Save Current Settings** - Preserve game options
2. **Clear Memory** - Zero out player and sprite data
3. **Copy Names** - Set "NINTEN" and "SONY" as defaults
4. **Initialize Game** - Set money, stats, inventory
5. **Give Items** - Add 1 Potion to inventory
6. **Set Map** - Prepare to spawn in Pallet Town
7. **Skip Intro** - Jump to gameplay (our modification)

**Result**: Player spawns in Pallet Town named "NINTEN" with 1 Potion, ready for RL training.

