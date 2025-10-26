What is RGBDS?
RGBDS (Rednex Game Boy Development System) is a complete toolchain for developing software on the Nintendo Game Boy and Game Boy Color. It consists of four main tools:
rgbasm - An assembler that converts assembly source code (.asm files) into object files (.o files)
rgblink - A linker that combines multiple object files into a single ROM image (.gbc files)
rgbfix - A utility that fixes and finalizes the ROM header, ensuring compatibility with Game Boy hardware
rgbgfx - A converter that transforms PNG images into the Game Boy's tile format (.2bpp, .1bpp files)
How RGBDS was used in building pokeblue.gbc
Looking at your project structure and the Makefile, here's exactly what happened when you built pokeblue.gbc:
1. Assembly Phase (rgbasm)
The Makefile shows that RGBDS assembled multiple source files into object files:
audio.asm → audio_blue.o
home.asm → home_blue.o
main.asm → main_blue.o
maps.asm → maps_blue.o
ram.asm → ram_blue.o
text.asm → text_blue.o
Plus graphics files: gfx/pics.asm → gfx/pics_blue.o, etc.
Each .asm file was compiled with specific flags:
The -D _BLUE flag tells the assembler to include Blue version-specific code.
2. Graphics Processing (rgbgfx)
RGBDS also processed PNG images into Game Boy tile formats:
Pokemon sprites (gfx/pokemon/*.png → .2bpp files)
Battle graphics (gfx/battle/*.png → .2bpp files)
Overworld sprites (gfx/sprites/*.png → .2bpp files)
And many more graphics assets
3. Linking Phase (rgblink)
All the object files were linked together using rgblink:
This created:
pokeblue.gbc (the final ROM)
pokeblue.map (memory map file)
pokeblue.sym (symbol table for debugging)
4. ROM Finalization (rgbfix)
Finally, rgbfix was used to fix the ROM header:
With these specific options for Pokemon Blue:
"
This sets up the proper Game Boy Color header with:
MBC3+RAM+BATTERY memory bank controller
Proper checksums
Game title "POKEMON BLUE"
The pokered Project Context
The pokered project is a disassembly of the original Pokemon Red game - meaning someone reverse-engineered the original ROM back into human-readable assembly code. This disassembly serves as the foundation for creating modified Pokemon games.
When you ran make, RGBDS took all those assembly source files (which represent the complete Pokemon game logic, graphics, maps, etc.) and assembled them into a working Game Boy ROM that you can run in an emulator or on real hardware.
This is particularly powerful for your RL project because you can now modify the game's maps, events, and mechanics by editing the assembly source files, then rebuild the ROM with RGBDS to create custom training environments for your Pokemon-playing AI agent!