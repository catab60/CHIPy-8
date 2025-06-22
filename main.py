import pygame
import sys
import time
import random
from tkinter import *
from tkinter import filedialog
import webbrowser
import os
from PIL import ImageTk, Image, ImageSequence


screenW = 64
screenH = 32
pixelscale = 20
memory_size = 4096
start_address = 0x200
font_start_address = 0x50


font = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
    0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
    0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
    0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
    0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
    0xF0, 0x80, 0xF0, 0x80, 0x80   # F
]

keys = {
    pygame.K_x: 0x0,
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_q: 0x4,
    pygame.K_w: 0x5,
    pygame.K_e: 0x6,
    pygame.K_a: 0x7,
    pygame.K_s: 0x8,
    pygame.K_d: 0x9,
    pygame.K_z: 0xA,
    pygame.K_c: 0xB,
    pygame.K_4: 0xC,
    pygame.K_r: 0xD,
    pygame.K_f: 0xE,
    pygame.K_v: 0xF
}

class Chip8:
    def __init__(self):
        self.memory = [0] * memory_size
        self.V = [0] * 16
        self.I = 0
        self.pc = start_address
        self.stack = []
        self.delay_timer = 0
        self.sound_timer = 0
        self.display = [0] * (screenW * screenH)
        self.keys = [0] * 16
        self.draw_flag = False

        for i in range(len(font)):
            self.memory[font_start_address + i] = font[i]

    def load_rom(self, rom_path):
        with open(rom_path, 'rb') as f:
            rom = f.read()
        for i in range(len(rom)):
            self.memory[start_address + i] = rom[i]

    def cycle(self):
        high_byte = self.memory[self.pc]
        low_byte = self.memory[self.pc + 1]
        opcode = (high_byte * 256) + low_byte

        self.execute_opcode(opcode)

        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def execute_opcode(self, opcode):
        self.pc += 2
        nnn = opcode % 0x1000

        n = opcode % 0x10
        x = (opcode // 0x100) % 0x10
        y = (opcode // 0x10) % 0x10
        kk = opcode % 0x100

        if opcode == 0x00E0:
            self.display = [0] * (screenW * screenH)
            self.draw_flag = True

        elif opcode == 0x00EE:
            self.pc = self.stack.pop()

        elif opcode & 0xF000 == 0x1000:
            self.pc = nnn

        elif opcode & 0xF000 == 0x2000:
            self.stack.append(self.pc)
            self.pc = nnn

        elif opcode & 0xF000 == 0x3000:
            if self.V[x] == kk:
                self.pc += 2

        elif opcode & 0xF000 == 0x4000:
            if self.V[x] != kk:
                self.pc += 2

        elif opcode & 0xF000 == 0x5000:
            if self.V[x] == self.V[y]:
                self.pc += 2

        elif opcode & 0xF000 == 0x6000:
            self.V[x] = kk

        elif opcode & 0xF000 == 0x7000:
            result = self.V[x] + kk
            self.V[x] = result % 256

        elif opcode & 0xF000 == 0x8000:
            if n == 0x0:
                self.V[x] = self.V[y]
            elif n == 0x1:
                self.V[x] = self.V[x] + self.V[y]
                if self.V[x] > 255:
                    self.V[x] = 255
            elif n == 0x2:
                self.V[x] = min(self.V[x], self.V[y])
            elif n == 0x3:
                self.V[x] ^= self.V[y]
            elif n == 0x4:
                sum_ = self.V[x] + self.V[y]
                self.V[0xF] = 1 if sum_ > 0xFF else 0
                self.V[x] = sum_ & 0xFF
            elif n == 0x5:
                self.V[0xF] = 1 if self.V[x] > self.V[y] else 0
                self.V[x] = (self.V[x] - self.V[y]) & 0xFF
            elif n == 0x6:
                self.V[0xF] = self.V[x] & 0x1
                self.V[x] >>= 1
            elif n == 0x7:
                self.V[0xF] = 1 if self.V[y] > self.V[x] else 0
                self.V[x] = (self.V[y] - self.V[x]) & 0xFF
            elif n == 0xE:
                self.V[0xF] = (self.V[x] & 0x80) >> 7
                self.V[x] = (self.V[x] << 1) & 0xFF

        elif opcode & 0xF000 == 0x9000:
            if self.V[x] != self.V[y]:
                self.pc += 2

        elif opcode & 0xF000 == 0xA000:
            self.I = nnn

        elif opcode & 0xF000 == 0xB000:
            self.pc = nnn + self.V[0]

        elif opcode & 0xF000 == 0xC000:
            self.V[x] = random.randint(0, 255) & kk

        elif opcode & 0xF000 == 0xD000:
            vx = self.V[x] % screenW
            vy = self.V[y] % screenH
            self.V[0xF] = 0
            for row in range(n):
                sprite = self.memory[self.I + row]
                for col in range(8):
                    if (sprite & (0x80 >> col)) != 0:
                        idx = (vx + col + ((vy + row) * screenW))
                        if idx >= len(self.display):
                            continue
                        if self.display[idx] == 1:
                            self.V[0xF] = 1
                        self.display[idx] ^= 1
            self.draw_flag = True

        elif opcode & 0xF000 == 0xE000:
            if kk == 0x9E:
                if self.keys[self.V[x]] == 1:
                    self.pc += 2
            elif kk == 0xA1:
                if self.keys[self.V[x]] == 0:
                    self.pc += 2

        elif opcode & 0xF000 == 0xF000:
            if kk == 0x07:
                self.V[x] = self.delay_timer
            elif kk == 0x0A:
                key_pressed = False
                for i in range(16):
                    if self.keys[i] == 1:
                        self.V[x] = i
                        key_pressed = True
                        break
                if not key_pressed:
                    self.pc -= 2
            elif kk == 0x15:
                self.delay_timer = self.V[x]
            elif kk == 0x18:
                self.sound_timer = self.V[x]
            elif kk == 0x1E:
                self.I = (self.I + self.V[x]) & 0xFFF
            elif kk == 0x29:
                self.I = font_start_address + (self.V[x] * 5)
            elif kk == 0x33:
                val = self.V[x]
                self.memory[self.I] = val // 100
                self.memory[self.I + 1] = (val // 10) % 10
                self.memory[self.I + 2] = val % 10
            elif kk == 0x55:
                for i_ in range(x + 1):
                    self.memory[self.I + i_] = self.V[i_]
            elif kk == 0x65:
                for i_ in range(x + 1):
                    self.V[i_] = self.memory[self.I + i_]

        else:
            print(f"Unknown opcode: {opcode:04X}")
    def get_first_frame_photo(self, rom_path, scale=4, max_cycles=500):
        self.__init__()          
        self.load_rom(rom_path)
        frames = []
        for _ in range(max_cycles):
            self.cycle()
            if self.draw_flag:
                frames.append(self.display.copy())
                self.draw_flag = False
        if not frames:
            frames.append(self.display.copy())
        buf = random.choice(frames)
        img = Image.new('RGB', (screenW, screenH), 'black')
        px = img.load()
        for y in range(screenH):
            for x in range(screenW):
                c = 255 if buf[y * screenW + x] else 0
                px[x, y] = (c, c, c)
        img = img.resize((screenW * scale, screenH * scale), Image.NEAREST)
        return ImageTk.PhotoImage(img)
    


def main(rom_path):
    pygame.init()
    window = pygame.display.set_mode((screenW * pixelscale, screenH * pixelscale))
    pygame.display.set_caption("Chipy-8 Emulator")
    clock = pygame.time.Clock()

    chip8 = Chip8()
    chip8.load_rom(rom_path)

    running = True
    while running:
        chip8.cycle()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in keys:
                    chip8.keys[keys[event.key]] = 1
                elif event.key == pygame.K_ESCAPE:
                    running = False

            elif event.type == pygame.KEYUP:
                if event.key in keys:
                    chip8.keys[keys[event.key]] = 0

        if chip8.draw_flag:
            window.fill((0, 0, 0))
            for y in range(screenH):
                for x in range(screenW):
                    if chip8.display[x + (y * screenW)] == 1:
                        pygame.draw.rect(window, (255, 255, 255), 
                                         (x * pixelscale, y * pixelscale, pixelscale, pixelscale))
            pygame.display.flip()
            chip8.draw_flag = False

        clock.tick(1000)

    pygame.quit()
    sys.exit()


class AnimatedGIF:
    def __init__(self, canvas, gif_path, x=0, y=0, scale=1):
        self.canvas = canvas
        self.gif_path = gif_path
        self.x = x
        self.y = y
        self.scale = scale
        self.frames = []
        self.load_frames()
        self.image_id = None
        self.frame_index = 0
        self.animate()

    def load_frames(self):
        im = Image.open(self.gif_path)
        for frame in ImageSequence.Iterator(im):
            resized = frame.resize((int(frame.width * self.scale), int(frame.height * self.scale)))
            self.frames.append(ImageTk.PhotoImage(resized))

    def animate(self):
        if self.frames:
            if self.image_id is None:
                self.image_id = self.canvas.create_image(self.x, self.y, anchor=NW, image=self.frames[self.frame_index])
            else:
                self.canvas.itemconfig(self.image_id, image=self.frames[self.frame_index])
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.canvas.after(40, self.animate)

class GameCard:
    def __init__(self, parent, game_name, game_path, row, col, image):
        self.frame = Frame(parent, relief="raised", borderwidth=2)
        self.frame.grid(row=row, column=col, padx=10, pady=10)
        self.image = image 
        self.image_label = Label(self.frame, image=self.image)
        self.image_label.image = self.image
        self.image_label.pack(pady=(5, 2))

        self.title_label = Label(self.frame, text=game_name, font=("Helvetica", 10))
        self.title_label.pack(pady=(0, 5))

        self.button = Button(
            self.frame, text="Start", width=12,
            command=lambda: self.launch_game(game_path),
            cursor="hand2"
        )
        self.button.pack(pady=(0, 5))

    def launch_game(self, game_path):
        root.destroy()
        main(game_path)

root = Tk()
root.title("Chipy-8")
root.geometry("900x520")
root.maxsize(900, 520)
root.minsize(900, 520)


bg_canvas = Canvas(root, width=900, height=520, highlightthickness=0, bd=0, relief='flat')
bg_canvas.place(x=0, y=0)




bg_animation = AnimatedGIF(bg_canvas, 'assets/background.gif', x=-40, y=0, scale=1.3)


spacer = Frame(root, height=0, borderwidth=0, highlightthickness=0)
spacer.pack(pady=90)
logo_im = Image.open("assets/logo.png")
logo_photo = ImageTk.PhotoImage(logo_im)




bg_canvas.create_image((900 - logo_im.width) // 2, 0, anchor=NW, image=logo_photo)


bg_canvas.logo_photo = logo_photo


def show_game_list():
    start_button.pack_forget()
    github_button.pack_forget()


    canvas = Canvas(root)
    scrollbar = Scrollbar(root, orient=VERTICAL, command=canvas.yview)
    scrollable_frame = Frame(canvas)

    def on_mousewheel(event):
        if os.name == 'nt':
            canvas.yview_scroll(-1 * int(event.delta / 120), "units")


    scrollable_frame.bind_all("<MouseWheel>", on_mousewheel)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)
    chip8 = Chip8()


    for index, game in enumerate(games):
        row = index // 4
        col = index % 4
        game_path = os.path.join(games_folder, game)
        
        chip8.load_rom(game_path)
        GameCard(scrollable_frame, game, game_path, row, col, chip8.get_first_frame_photo(game_path, scale=3))

    if len(games) == 0:
        k = Label(scrollable_frame, text=" - No games found! :(", font=("Helvetica", 20))
        k.pack(pady=150)



def opem_github():
    webbrowser.open("https://github.com/catab60")

start_button = Button(root, text="Start", font=("Helvetica", 14), width=20, height=2, command=show_game_list, cursor="hand2")
start_button.pack(pady=(100,30))

github_button = Button(root, text="Github", font=("Helvetica", 14), width=20, height=2, command=opem_github, cursor="hand2")
github_button.pack()


games_folder = "games"
os.makedirs(games_folder, exist_ok=True)


games = [f for f in os.listdir(games_folder) if os.path.isfile(os.path.join(games_folder, f))]

root.mainloop()