# Pokemon Red/Blue Experimental Changes Documentation

This document tracks all modifications made to the `pokered_experimental` disassembly for RL training purposes. It includes both the original game flow documentation and all experimental changes.

---

## Table of Contents

1. [Pre-Oak Speech Flow - Game Initialization (Original Documentation)](#pre-oak-speech-flow---game-initialization-original-documentation)
   - [Overview](#overview)
   - [Files Involved](#files-involved)
   - [Visual Flow Diagram](#visual-flow-diagram)
   - [Detailed Code Walkthrough](#detailed-code-walkthrough)
   - [Memory Locations](#memory-locations)
   - [Constants](#constants)
   - [What Gets Copied (Byte by Byte)](#what-gets-copied-byte-by-byte)
   - [Summary: Pre-Oak Speech Initialization](#summary-pre-oak-speech-initialization)
   - [Memory Layout Explanation](#memory-layout-explanation)

2. [Experimental Changes for RL Training](#experimental-changes-for-rl-training)
   - [Change 1: Skip Oak's Speech Intro](#change-1-skip-oaks-speech-intro)
   - [Change 2: Skip Intro Battle Animation](#change-2-skip-intro-battle-animation)
   - [Change 3: Skip Title Screen and Main Menu](#change-3-skip-title-screen-and-main-menu)
   - [Change 4: Export StartNewGameDebug Function](#change-4-export-startnewgamedebug-function)
   - [Change 5: Set Debug Player Names](#change-5-set-debug-player-names)
   - [Change 6: Skip End Dialogue and Shrinking Sprite Animation](#change-6-skip-end-dialogue-and-shrinking-sprite-animation)
   - [Side Effect: Starting Location Changed by Debug Mode](#side-effect-starting-location-changed-by-debug-mode)
   - [How Starting Location is Determined](#how-starting-location-is-determined)
   - [Summary of All Changes](#summary-of-all-changes)
   - [Notes for Future Changes](#notes-for-future-changes)

---

# Pre-Oak Speech Flow - Game Initialization (Original Documentation)

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

---

## Memory Layout Explanation

### Understanding `ds NAME_LENGTH` in WRAM

When you see this in `wram.asm`:

```asm
wPlayerName:: ds NAME_LENGTH  ; Line 1710
wRivalName::  ds NAME_LENGTH  ; Line 1758
```

**What `ds` means:**
- `ds` = "Define Storage" - allocate uninitialized memory
- `NAME_LENGTH` = 11 (from `text_constants.asm`)
- This creates **11-byte buffers** in RAM
- Memory is **not initialized** with values

**Why you see `db NAME_LENGTH` looking at it:**

`wPlayerName` and `wRivalName` are just **empty 11-byte memory locations** when the game starts.

The actual data comes from:
- **Source**: `title.asm` lines 412-416 (ROM data)
- **Destination**: `wram.asm` lines 1710, 1758 (RAM buffers)

**How data flows:**

```
ROM (title.asm):
  DebugNewGamePlayerName: db "NINTEN@"    ← Source data
  DebugNewGameRivalName:  db "SONY@"      ← Source data
  
  ↓ CopyData function copies this data ↓
  
RAM (wram.asm):
  wPlayerName: ds 11                      ← Destination buffer
  wRivalName:  ds 11                      ← Destination buffer
```

**Before CopyData:**
```
wPlayerName = [uninitialized garbage memory - 11 bytes]
wRivalName  = [uninitialized garbage memory - 11 bytes]
```

**After CopyData (PrepareOakSpeech):**
```
wPlayerName = "NINTEN\0\0\0\0\0"   (11 bytes, padded with zeros)
wRivalName  = "SONY\0\0\0\0\0\0\0" (11 bytes, padded with zeros)
```

**Key Point**: The `ds` directive only allocates space. The actual string copying happens during `PrepareOakSpeech()` via the `CopyData` function in `copy.asm` (lines 15-24).

### Data Definition vs. Storage Allocation

| Directive | Purpose | Example |
|-----------|---------|---------|
| `db` | Define bytes with specific values | `db "NAME@"` → stores exact bytes |
| `ds` | Define storage (allocate space) | `ds 11` → reserves 11 bytes, no values |
| `dw` | Define words (2-byte values) | `dw $1234` → stores 16-bit value |

So when you see:
```asm
wPlayerName:: ds NAME_LENGTH  ; Allocates 11 empty bytes
```

It's **not** storing "NINTEN" there yet. That data gets copied from ROM later by `CopyData`.

---

# Experimental Changes for RL Training

This section documents all modifications made to `pokered_experimental` to optimize the game for reinforcement learning training.

---

## Change 1: Skip Oak's Speech Intro

**Purpose**: Skip Professor Oak's introductory speech and name selection to start gameplay immediately.

**File**: `pokered_experimental/engine/movie/oak_speech/oak_speech.asm`

**Location**: Lines 64-67

**Original Code**:
```asm
    xor a
    ldh [hTileAnimations], a
    ld a, [wStatusFlags6]
    bit BIT_DEBUG_MODE, a
    jp nz, .skipSpeech
```

**Modified Code**:
```asm
    xor a
    ldh [hTileAnimations], a
    ; ld a, [wStatusFlags6] ; If debug mode, then skip
    ; bit BIT_DEBUG_MODE, a ; Make it so that we skip anyway
    ; jp nz, .skipSpeech
    jp .skipSpeech
```

**Effect**: 
- Unconditionally jumps to `.skipSpeech` label
- Skips all Oak dialog, name selection, and intro sequences
- Player spawns directly in Pallet Town with default names

**Technical Details**:
- The original code checked `BIT_DEBUG_MODE` flag in `wStatusFlags6`
- If debug mode was set, it would skip the speech
- Our change makes it always skip, regardless of debug mode
- This saves significant time during RL training episodes

---

## Change 2: Skip Intro Battle Animation

**Purpose**: Skip the Gengar vs Nidorino intro battle animation that plays when the game first starts.

**File**: `pokered_experimental/home/init.asm`

**Location**: Line 99

**Original Code**:
```asm
    predef PlayIntro
```

**Modified Code**:
```asm
    ; predef PlayIntro  ; Skip intro battle animation
```

**Effect**:
- Skips the animated intro sequence
- Game proceeds directly to title screen initialization
- Saves ~10-15 seconds per game start

**Technical Details**:
- `PlayIntro` is a predef (predefined function) that handles the intro animation
- Commenting it out prevents the animation from playing
- The game continues with normal initialization after this point

---

## Change 3: Skip Title Screen and Main Menu

**Purpose**: Skip the title screen display and main menu selection, jumping directly to game start.

**File**: `pokered_experimental/engine/movie/title.asm`

**Location**: Lines 28-48 (after `PrepareTitleScreen` initialization)

**Original Flow**:
```asm
PrepareTitleScreen::
    ; ... initialization code ...
    ld a, BANK(Music_TitleScreen)
    ld [wAudioROMBank], a
    ld [wAudioSavedROMBank], a

DisplayTitleScreen:
    ; ... title screen graphics and menu ...
```

**Modified Code**:
```asm
PrepareTitleScreen::
    ; ... initialization code (lines 9-26) ...
    ld a, BANK(Music_TitleScreen)
    ld [wAudioROMBank], a
    ld [wAudioSavedROMBank], a
    
    ; Do essential display initialization (from DisplayTitleScreen)
    ; but skip the actual title screen graphics and menu
    call GBPalWhiteOut
    ld a, $1
    ldh [hAutoBGTransferEnabled], a
    xor a
    ldh [hTileAnimations], a
    ldh [hSCX], a
    ldh [hSCY], a
    ldh [hWY], a
    call ClearScreen
    call DisableLCD
    call LoadFontTilePatterns    ; Critical: loads font for text display
    call ClearBothBGMaps
    call EnableLCD
    call GBPalNormal             ; Set up palettes
    
    ; Now jump to game (skip title screen display and main menu)
    ld hl, wStatusFlags6
    set BIT_DEBUG_MODE, [hl]
    farjp StartNewGameDebug
```

**Effect**:
- Performs essential display initialization (fonts, palettes, screen clearing)
- Skips title screen graphics rendering
- Skips main menu display and selection
- Jumps directly to `StartNewGameDebug` which starts the game

**Technical Details**:
- `PrepareTitleScreen` still runs for initialization (name copying, flags, audio)
- We add critical display setup: `LoadFontTilePatterns` (required for text rendering)
- `GBPalWhiteOut` and `GBPalNormal` set up color palettes
- `farjp StartNewGameDebug` performs a cross-bank jump to start the game
- Without `LoadFontTilePatterns`, the screen would be white (no text rendering)

---

## Change 4: Export StartNewGameDebug Function

**Purpose**: Make `StartNewGameDebug` accessible from other ROM banks (required for `farjp` call).

**File**: `pokered_experimental/engine/menus/main_menu.asm`

**Location**: Line 321

**Original Code**:
```asm
StartNewGameDebug:
```

**Modified Code**:
```asm
StartNewGameDebug::
```

**Effect**:
- Exports the function label (makes it globally accessible)
- Allows `farjp StartNewGameDebug` to work from other ROM banks
- Required for cross-bank function calls in RGBDS

**Technical Details**:
- In RGBDS assembly, labels ending with `::` are exported (global)
- Labels ending with `:` are local to the current file/bank
- `StartNewGameDebug` is in ROM bank 1 (`main.asm`), but we call it from ROM0 (`init.asm`)
- The `::` makes it accessible via `farjp` macro

---

## Change 5: Set Debug Player Names

**Purpose**: Set custom default player and rival names for RL training.

**File**: `pokered_experimental/engine/movie/title.asm`

**Location**: Lines 434-438

**Original Code**:
```asm
DebugNewGamePlayerName:
    db "NINTEN@"

DebugNewGameRivalName:
    db "SONY@"
```

**Modified Code**:
```asm
DebugNewGamePlayerName:
    db "GENE AI@"

DebugNewGameRivalName:
    db "GARY@"
```

**Effect**:
- Player name is set to "GENE AI" when starting a new game
- Rival name is set to "GARY"
- These names are copied to `wPlayerName` and `wRivalName` during `PrepareTitleScreen` and `PrepareOakSpeech`

**Technical Details**:
- These debug names are used during game initialization
- Copied via `CopyDebugName` function in `PrepareTitleScreen` (lines 9-14)
- Also copied in `PrepareOakSpeech` (lines 33-40)
- The `@` character is the string terminator in Pokemon Red/Blue
- Names are padded to `NAME_LENGTH` (11 bytes) when copied to RAM

---

## Change 6: Skip End Dialogue and Shrinking Sprite Animation

**Purpose**: Skip the end dialogue (OakSpeechText3) and the shrinking sprite animation that plays after skipping Oak's speech, going straight into gameplay.

**File**: `pokered_experimental/engine/movie/oak_speech/oak_speech.asm`

**Location**: Lines 103-123 (`.skipSpeech` section)

**Original Code**:
```asm
.skipSpeech
	call GBFadeOutToWhite
	call ClearScreen
	ld de, RedPicFront
	lb bc, BANK(RedPicFront), $00
	call IntroDisplayPicCenteredOrUpperRight
	call GBFadeInFromWhite
	ld a, [wStatusFlags3]
	and a ; ???
	jr nz, .next
	ld hl, OakSpeechText3
	call PrintText
.next
	ldh a, [hLoadedROMBank]
	push af
	ld a, SFX_SHRINK
	call PlaySound
	pop af
	ldh [hLoadedROMBank], a
	ld [rROMB], a
	ld c, 4
	call DelayFrames
	ld de, RedSprite
	ld hl, vSprites
	lb bc, BANK(RedSprite), $0C
	call CopyVideoData
	ld de, ShrinkPic1
	lb bc, BANK(ShrinkPic1), $00
	call IntroDisplayPicCenteredOrUpperRight
	ld c, 4
	call DelayFrames
	ld de, ShrinkPic2
	lb bc, BANK(ShrinkPic2), $00
	call IntroDisplayPicCenteredOrUpperRight
	call ResetPlayerSpriteData
	ldh a, [hLoadedROMBank]
	push af
	ld a, BANK(Music_PalletTown)
	ld [wAudioROMBank], a
	ld [wAudioSavedROMBank], a
	ld a, 10
	ld [wAudioFadeOutControl], a
	ld a, SFX_STOP_ALL_MUSIC
	ld [wNewSoundID], a
	call PlaySound
	pop af
	ldh [hLoadedROMBank], a
	ld [rROMB], a
	ld c, 20
	call DelayFrames
	hlcoord 6, 5
	ld b, 7
	ld c, 7
	call ClearScreenArea
	call LoadTextBoxTilePatterns
	ld a, 1
	ld [wUpdateSpritesEnabled], a
	ld c, 50
	call DelayFrames
	call GBFadeOutToWhite
	jp ClearScreen
```

**Modified Code**:
```asm
.skipSpeech
	; Skip all animations - do minimal setup and return
	call ResetPlayerSpriteData
	ldh a, [hLoadedROMBank]
	push af
	ld a, BANK(Music_PalletTown)
	ld [wAudioROMBank], a
	ld [wAudioSavedROMBank], a
	ld a, 10
	ld [wAudioFadeOutControl], a
	ld a, SFX_STOP_ALL_MUSIC
	ld [wNewSoundID], a
	call PlaySound
	pop af
	ldh [hLoadedROMBank], a
	ld [rROMB], a
	call LoadTextBoxTilePatterns
	ld a, 1
	ld [wUpdateSpritesEnabled], a
	call ClearScreen
	ret
```

**Effect**:
- Skips Red's picture display (`RedPicFront`)
- Skips end dialogue (`OakSpeechText3`)
- Skips shrinking animation (`ShrinkPic1`, `ShrinkPic2`)
- Skips shrinking sound effect (`SFX_SHRINK`)
- Skips all fade animations (`GBFadeOutToWhite`, `GBFadeInFromWhite`)
- Skips most delay frames
- Performs only essential setup:
  - `ResetPlayerSpriteData` - initializes player sprite data
  - Music setup - prepares Pallet Town music
  - `LoadTextBoxTilePatterns` - loads text box graphics (required for text)
  - `wUpdateSpritesEnabled` - enables sprite updates
  - `ClearScreen` - clears the screen
- Returns immediately to `StartNewGameDebug`, which proceeds to `SpecialEnterMap` and starts gameplay

**Technical Details**:
- The original code had ~60 lines of animation and dialogue
- Reduced to ~20 lines of essential initialization
- Removed all visual effects (fades, picture displays, shrinking animation)
- Removed dialogue text display
- Kept only what's necessary for the game to function properly
- The `ret` instruction returns to `StartNewGameDebug` line 323, which continues with `SpecialEnterMap`

**Time Saved**: ~15-20 seconds per episode (skips shrinking animation, dialogue, and fade effects)

---

## Side Effect: Starting Location Changed by Debug Mode

**Important Note**: Setting `BIT_DEBUG_MODE` (Change 3) inadvertently changed the starting location from inside Red's House 2F to outside in Pallet Town.

### Original Starting Location (Without Debug Mode)

**File**: `pokered_experimental/data/maps/special_warps.asm`

**Lines 47-48**:
```asm
NewGameWarp:
    special_warp_spec REDS_HOUSE_2F, 3, 6, REDS_HOUSE_2
```

**Result**: Player starts inside Red's House 2nd Floor at coordinates (3, 6).

### Current Starting Location (With Debug Mode)

**File**: `pokered_experimental/data/maps/special_warps.asm`

**Line 79**:
```asm
.PalletTown:     fly_warp PALLET_TOWN,      5,  6
```

**Result**: Player starts outside in Pallet Town at coordinates (5, 6) - in front of Red's house.

### Why This Happened

**File**: `pokered_experimental/engine/overworld/special_warps.asm`

**Lines 51-57**: When `BIT_DEBUG_MODE` is set, the code skips `NewGameWarp`:
```asm
    bit BIT_DEBUG_MODE, a
    ; warp to wLastMap (PALLET_TOWN) for StartNewGameDebug
    jr nz, .notNewGameWarp  ; ← Jumps here if debug mode!
    bit BIT_FLY_OR_DUNGEON_WARP, a
    jr nz, .notNewGameWarp
    ld hl, NewGameWarp       ; ← This is SKIPPED in debug mode!
```

**Lines 112-129**: Instead, it uses `FlyWarpDataPtr` to look up the warp data for `PALLET_TOWN`:
```asm
.otherDestination
    ld a, [wDestinationMap]  ; PALLET_TOWN (set in line 17)
.usedFlyWarp
    ld b, a
    ld [wCurMap], a
    ld hl, FlyWarpDataPtr
    ; ... looks up PALLET_TOWN in FlyWarpDataPtr ...
    ; ... finds .PalletTown: fly_warp PALLET_TOWN, 5, 6 ...
```

### Flow Comparison

**Normal Path (No Debug Mode)**:
1. `PrepareForSpecialWarp` → `LoadSpecialWarpData`
2. Uses `NewGameWarp` → `REDS_HOUSE_2F` at (3, 6)

**Debug Mode Path (Current)**:
1. `PrepareForSpecialWarp` → Sets map to `PALLET_TOWN` (line 17)
2. `LoadSpecialWarpData` → Skips `NewGameWarp` (line 52)
3. Uses `FlyWarpDataPtr` → Finds `.PalletTown` → `PALLET_TOWN` at (5, 6)

### How to Change Starting Location

See [How Starting Location is Determined](#how-starting-location-is-determined) section below for detailed instructions.

---

## How Starting Location is Determined

### Code Flow for Starting Location

The starting location is determined through this sequence:

1. **Set Default Map** (`main_menu.asm` line 23)
   - `wDefaultMap` is set to 0 (PALLET_TOWN)

2. **Copy to Destination** (`oak_speech.asm` lines 59-60)
   - `wDestinationMap` = `wDefaultMap`

3. **Prepare Warp** (`oak_speech.asm` line 61)
   - Calls `PrepareForSpecialWarp`

4. **Load Warp Data** (`special_warps.asm`)
   - **If debug mode**: Uses `FlyWarpDataPtr` for `PALLET_TOWN` → (5, 6)
   - **If normal mode**: Uses `NewGameWarp` → `REDS_HOUSE_2F` at (3, 6)

5. **Copy to Memory** (`special_warps.asm` lines 59-66)
   - Copies warp data to:
     - `wCurMap` - Current map ID
     - `wYCoord` - Y coordinate (RAM address 0xD361)
     - `wXCoord` - X coordinate (RAM address 0xD362)

### Key Files

- **Warp Data**: `pokered_experimental/data/maps/special_warps.asm`
  - `NewGameWarp` (line 47) - Normal starting location
  - `FlyWarpDataPtr` (line 64) - Debug mode starting locations

- **Warp Logic**: `pokered_experimental/engine/overworld/special_warps.asm`
  - `PrepareForSpecialWarp` (line 1) - Main warp preparation
  - `LoadSpecialWarpData` (line 31) - Loads warp coordinates

- **Map Constants**: `pokered_experimental/constants/map_constants.asm`
  - Defines all map IDs (PALLET_TOWN = $00, VIRIDIAN_CITY = $01, etc.)

### How to Change Starting Location

#### Option 1: Modify FlyWarpData for Pallet Town (Debug Mode)

**File**: `pokered_experimental/data/maps/special_warps.asm`

**Line 79**: Change coordinates:
```asm
.PalletTown:     fly_warp PALLET_TOWN,      10,  10  ; New position
```

#### Option 2: Make Debug Mode Use NewGameWarp

**File**: `pokered_experimental/engine/overworld/special_warps.asm`

**Lines 51-57**: Comment out debug mode check:
```asm
    ; bit BIT_DEBUG_MODE, a  ; Comment this out
    ; jr nz, .notNewGameWarp ; Comment this out
    bit BIT_FLY_OR_DUNGEON_WARP, a
    jr nz, .notNewGameWarp
    ld hl, NewGameWarp       ; Now used even in debug mode
```

#### Option 3: Change NewGameWarp Location

**File**: `pokered_experimental/data/maps/special_warps.asm`

**Line 47-48**: Change to desired map and coordinates:
```asm
NewGameWarp:
    special_warp_spec PALLET_TOWN, 5, 6, OVERWORLD  ; Start outside
```

Then use Option 2 to make debug mode use it.

**Format**: `special_warp_spec MAP_ID, X_COORD, Y_COORD, TILESET`

---

## Summary of All Changes

| Change | File | Lines | Effect |
|--------|------|-------|--------|
| Skip Oak Speech | `oak_speech/oak_speech.asm` | 64-67 | Unconditional jump past intro dialog |
| Skip Intro Animation | `home/init.asm` | 99 | Comment out `PlayIntro` |
| Skip Title/Menu | `movie/title.asm` | 28-48 | Initialize display, jump to game |
| Export Function | `menus/main_menu.asm` | 321 | Make `StartNewGameDebug` global |
| Custom Names | `movie/title.asm` | 434-438 | Set player/rival names |
| Skip End Animations | `oak_speech/oak_speech.asm` | 103-123 | Skip dialogue and shrinking animation |

**Current Game Flow After Changes**:
1. Game starts → Skip intro battle animation (Gengar vs Nidorino)
2. → Initialize display (fonts, palettes, screen)
3. → Copy debug names ("GENE AI" and "GARY") to player/rival name memory
4. → Skip title screen graphics and main menu
5. → Set `BIT_DEBUG_MODE` flag (Change 3)
6. → Jump to `StartNewGameDebug`
7. → Calls `OakSpeech` (which skips the speech due to Change 1)
8. → Skips end dialogue and shrinking animation (Change 6)
9. → `PrepareForSpecialWarp` detects debug mode
10. → Uses `FlyWarpDataPtr` for `PALLET_TOWN` (instead of `NewGameWarp`)
11. → Game starts immediately in Pallet Town at (5, 6) with player name "GENE AI"

**Note**: The starting location changed from Red's House 2F (3, 6) to Pallet Town (5, 6) due to debug mode using fly warp data instead of `NewGameWarp`. See [Side Effect: Starting Location Changed by Debug Mode](#side-effect-starting-location-changed-by-debug-mode) for details.

**Time Saved Per Episode**:
- Intro animation: ~10-15 seconds
- Title screen + menu: ~5-10 seconds
- Oak speech: ~30-60 seconds
- End dialogue + shrinking animation: ~15-20 seconds
- **Total: ~60-105 seconds saved per RL training episode**

---

## Python Environment Improvements

### Optimized Debug Runner (ppew_debug_optimized.py)

**Purpose**: High-performance game runner with modular overlay system for development, debugging, and training.

**File**: `env/ppew_debug_optimized.py`

**Key Features**:

1. **Performance Optimizations**:
   - Headless mode by default (no PyBoy SDL2 window overhead)
   - Configurable overlay refresh rate (not every frame)
   - Fast matplotlib updates using `set_data()` instead of recreating plots
   - Optional unlimited FPS mode for maximum speed
   - ~10-20x faster than original ppew_debug.py

2. **Two Display Modes**:
   - **Interactive Mode** (`--pyboy-window`): PyBoy SDL2 window handles arrow key input naturally
   - **Headless Mode** (default): No window, no controls, maximum speed for training

3. **Modular Overlay System**:
   Three independent visualization overlays that can be enabled individually or in combination:

   - **Info Panel** (`--info`): Stats panel on right side with:
     - FPS counter and frame count
     - Player position (X, Y in tiles)
     - Map ID
     - Steps taken
     - Maps visited count
     - Movement statistics
     - Controls guide
     - Dark theme with green monospace text
     - Box-drawing characters for professional look

   - **Tile Grid** (`--tiles`): Visual grid overlay showing:
     - 16x16 pixel tile boundaries (10 tiles wide × 9 tiles tall)
     - Green semi-transparent grid lines matching info panel color
     - **Dynamic world-aligned grid**: Uses scroll registers (SCX/SCY) to keep grid aligned with world tiles
     - Grid moves with the background as player walks, showing actual tile boundaries
     - Helps understand game's visual tile-based coordinate system
     - Useful for debugging movement and collision detection

   - **Direction Arrows** (`--dir`): Movement history visualization:
     - Green arrows showing recent movements (last 100)
     - One arrow per tile (latest movement overrides previous)
     - **Arrows precisely centered within grid tiles** using:
       - Geometric midpoint calculation (arrow_start = tile_center - arrow_length/2)
       - Direction-based offset compensation (ARROW_DIRECTION_OFFSET = -2)
     - Fade effect based on recency (older = more transparent)
     - Only shows arrows for current map
     - Scrolls with player position as screen moves
     - Magenta dashed rectangle shows current player tile for alignment verification
     - Helps visualize exploration patterns and navigation behavior

4. **Command Line Interface**:
   ```bash
   # Default: headless, no overlays, 60fps
   python3 env/ppew_debug_optimized.py

   # Interactive mode with PyBoy window (use arrow keys in PyBoy window)
   python3 env/ppew_debug_optimized.py --pyboy-window

   # Interactive with info panel
   python3 env/ppew_debug_optimized.py --pyboy-window --info

   # Interactive with tile grid overlay
   python3 env/ppew_debug_optimized.py --pyboy-window --tiles

   # Interactive with direction arrows
   python3 env/ppew_debug_optimized.py --pyboy-window --dir

   # All overlays combined
   python3 env/ppew_debug_optimized.py --pyboy-window --info --tiles --dir

   # Debug overlay without PyBoy window (for watching RL agent)
   python3 env/ppew_debug_optimized.py --info --tiles --dir

   # Maximum speed for training (no display at all)
   python3 env/ppew_debug_optimized.py --fps 0

   # Timed runs for benchmarking
   python3 env/ppew_debug_optimized.py --duration 60 --fps 0
   python3 env/ppew_debug_optimized.py --frames 10000 --fps 0
   ```

   **Available Arguments**:
   - `--rom PATH`: ROM file path (default: pokered_experimental/pokeblue.gbc)
   - `--pyboy-window`: Show PyBoy SDL2 window for interactive play with arrow keys
   - `--info`: Show info panel with game statistics
   - `--tiles`: Show tile grid overlay (16x16 pixel grid)
   - `--dir`: Show movement direction arrows
   - `--overlay-rate N`: Update overlay every N frames (default: 2)
   - `--fps N`: Max FPS, 0=unlimited (default: 60)
   - `--duration SECONDS`: Run for N seconds then exit
   - `--frames N`: Run for N frames then exit

5. **Performance Metrics**:
   - Automatic FPS monitoring
   - Console statistics every 5 seconds
   - Final report on exit with total stats

**Performance Comparison**:
| Configuration | FPS | Speed vs Original |
|--------------|-----|-------------------|
| Original ppew_debug.py | ~20-25 FPS | 1x baseline |
| Optimized (default) | ~60 FPS | 2.5x faster |
| Optimized (no overlay, 60fps) | ~60 FPS | 2.5x faster |
| Optimized (no overlay, unlimited) | ~300-500 FPS | 15-20x faster |

**Technical Implementation**:

1. **Two Display Modes**:
   ```python
   # Interactive Mode: PyBoy SDL2 window handles keyboard input naturally
   window_mode = "SDL2" if show_pyboy_window else "null"

   # Headless Mode: No window, no controls (for training)
   # PyBoy runs entirely in memory with no rendering overhead
   ```

2. **Fast Plot Updates**:
   ```python
   # Pre-create image plot once during initialization
   self.img_plot = self.ax_game.imshow(dummy_img, interpolation='nearest')

   # Update only data (10-20x faster than ax.clear() + ax.imshow())
   self.img_plot.set_data(screen_array)
   ```

3. **GridSpec Layout**:
   ```python
   # 2:1 width ratio for game:stats
   gs = GridSpec(1, 2, figure=self.fig, width_ratios=[2, 1], wspace=0.1)
   ```

4. **Headless Mode Benefits**:
   - No GPU rendering overhead
   - No SDL2 window management
   - PyBoy runs entirely in memory
   - Perfect for parallel training instances

**Usage in Training**:
```python
from env.ppew_debug_optimized import OptimizedDebugRunner

# For development/testing
runner = OptimizedDebugRunner(
    rom_path="pokered_experimental/pokeblue.gbc",
    show_overlay=True,
    max_fps=60
)
runner.run()

# For training (maximum speed)
runner = OptimizedDebugRunner(
    rom_path="pokered_experimental/pokeblue.gbc",
    show_overlay=False,
    max_fps=0,
    print_stats=True
)
runner.run(max_frames=10000)
```

**Comparison with Original ppew_debug.py**:

| Feature | ppew_debug.py | ppew_debug_optimized.py |
|---------|---------------|-------------------------|
| Display Mode | SDL2 + matplotlib | Headless (default) or SDL2 (optional) |
| Overlay | On screen (clutters gameplay) | Modular system (info/tiles/dir flags) |
| Visualization | Debug info only | Info panel + tile grid + direction arrows |
| Controls | PyBoy SDL2 window (arrow keys) | PyBoy SDL2 window when `--pyboy-window` used |
| Input Method | PyBoy handles naturally | PyBoy handles naturally (when window shown) |
| Plot Updates | ax.clear() + ax.imshow() | img_plot.set_data() |
| FPS | ~20-25 | ~60 (default) or unlimited |
| PIL Conversions | Every frame | Only when overlay enabled |
| Configurability | Limited | Extensive CLI options + modular overlays |
| Training Suitability | Poor (slow, always shows SDL2) | Excellent (fast, headless mode) |
| Interactive Play | Yes (SDL2 window) | Yes (`--pyboy-window` flag) |
| Debugging Tools | Basic info | Tile grid + movement tracking + stats |

---

## Notes for Future Changes

When making additional modifications to `pokered_experimental`:

1. **Document all changes** in this file with:
   - Purpose/Reason
   - File and line numbers
   - Original code
   - Modified code
   - Effect/Impact
   - Technical details

2. **Test changes** by rebuilding:
   ```bash
   cd pokered_experimental
   make clean
   make pokeblue.gbc
   ```

3. **Verify functionality** with PyBoy before committing

4. **Keep this documentation updated** as the project evolves

5. **For Python environment changes**: Test performance with benchmarks before and after modifications

---

## Quick Reference: Running the Optimized Debug Runner

### Common Commands

```bash
# Interactive play (use arrow keys in PyBoy window)
python3 env/ppew_debug_optimized.py --pyboy-window

# Interactive with all debug overlays
python3 env/ppew_debug_optimized.py --pyboy-window --info --tiles --dir

# Headless with visualization (watch RL agent learn)
python3 env/ppew_debug_optimized.py --info --tiles --dir

# Debug movement and tiles (no info panel)
python3 env/ppew_debug_optimized.py --pyboy-window --tiles --dir

# Maximum speed training mode (no display)
python3 env/ppew_debug_optimized.py --fps 0

# Benchmark for 10,000 frames
python3 env/ppew_debug_optimized.py --frames 10000 --fps 0
```

### Use Cases

| Use Case | Command | Why |
|----------|---------|-----|
| **Playing the game** | `--pyboy-window` | Shows PyBoy window, use arrow keys to play |
| **Debugging movement** | `--pyboy-window --tiles --dir` | See tile boundaries and movement history |
| **Watching RL agent** | `--info --tiles --dir` | Visualize agent exploration with stats |
| **Understanding tiles** | `--pyboy-window --tiles` | See how the game divides screen into tiles |
| **Training RL agent** | `--fps 0` | Maximum speed, no visual output |
| **Performance testing** | `--frames 10000 --fps 0` | Benchmark mode |

