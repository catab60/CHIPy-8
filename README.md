# CHIPy-8

This is **CHIPy-8**, a Chip-8 emulator written entirely in Python. The project was developed in **2 days** as a lightweight exercise to learn how emulators work, manage memory, and interpret opcodes based on the original Chip-8 specification.

![CHIPy-8](https://github.com/catab60/CHIPy-8/blob/main/assets/logo.gif?raw=true)

## About the Project

**CHIPy-8 Version 1** faithfully implements the Chip-8 virtual machine’s instruction set, memory layout, timers, and display routines. By loading Chip-8 ROMs, it steps through each opcode cycle-by-cycle, updates registers and timers, and draws graphics on a simple window using Pygame.

### Key Highlights

* **Complete Opcode Support**: Implements all 35 original Chip-8 instructions.
* **Memory & Stack Management**: 4KB of RAM, 16 8-bit registers (V0–VF), index register, stack pointer, delay and sound timers.
* **Graphics & Input**: 64×32 black and white display, hex keypad mapping to computer keyboard.
* **Lightweight & Extensible**: Easy to read Python codebase, ideal for learning and further extension.

## Documentation & Inspiration

Based on the official Chip-8 technical reference:
[C8 Technical Reference by Hugh Devernay](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM)

## Usage Guide

1. **Clone the repository:**

   ```bash
   git clone https://github.com/catab60/CHIPy-8.git
   cd CHIPy-8
   ```
2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```
3. **Run the emulator:**

   ```bash
   python main.py
   ```
4. **Load a game ROM:**

   * Download .ch8 programs from the Chip-8 archive:
     [here](https://johnearnest.github.io/chip8Archive/)
     *(I do not endorse piracy—use at your own risk.)*
   * Place the `.ch8` file in the `games/` directory (create it if necessary).
   * Enjoy!

## Learning Experience

Building **CHIPy-8** was an invaluable deep dive into low-level emulation concepts. Parsing and executing each opcode taught me how real hardware interprets instructions, while managing memory and timing helped me appreciate the balance between accuracy and performance in emulator design.

## Contributions

Contributions are welcome! If you find bugs, want to add features, or improve accuracy, please open an issue or submit a pull request. Let’s build a better Chip-8 emulator together!
