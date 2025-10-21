import sys
import termios
import fcntl
import os
from cpu import Cpu

def undefined(address, data):
    print(f'Undefined instruction at address 0x{address:02X}, {data:02X}')

def init_nonblocking_input():
    fd = sys.stdin.fileno()

    # Save original terminal settings
    original_termios = termios.tcgetattr(fd)
    new_termios = termios.tcgetattr(fd)

    # Turn off canonical mode and echo
    new_termios[3] &= ~(termios.ICANON | termios.ECHO)
    termios.tcsetattr(fd, termios.TCSANOW, new_termios)

    # Set stdin to non-blocking
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    return original_termios

def restore_input(original_termios):
    fd = sys.stdin.fileno()
    termios.tcsetattr(fd, termios.TCSANOW, original_termios)

def read_key():
    try:
        return sys.stdin.read(1)
    except IOError:
        return None

# 1) Wyczyścić zawartość rejestrów R0 i R1 wpisując do nich wartość 0,
# 2) Wyczyścić zawartość komórki pamięci o adresie 14 wpisując do niej wartość 0,
# 3) Do rejestru R0 wpisać liczbę 0x6
# 4) Dodać do rejestru R0 wartość przechowywaną w pamięci RAM pod adresem 13,
# 5) Umieścić zawartość rejestru R0 w pamięci RAM w komórce o adresie 14,
# 6) Powrócić do adresu 0, aby zapętlić się        

base_program = [\
  0x80, \
  0x90, \
  0x81, \
  0x92, \
  0xA0, \
  0x00, \
  0x00, \
  0x00, \
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

load_store_program = [
  0x80,  # MOV R0, #0
  0x90,  # MOV R1, #0
  0xEE,  # STR R0, [14]
  0x86,  # MOV R0, #6
  0xDD,  # LDR R1, [13]
  0x20,  # ADD R0, R1
  0xEE,  # STR R0, [14]
  0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x05, 0x01, 0x00]

# load_store_program = [\
#   0x80, \
#   0x90, \
#   0x86, \
#   0xCD, \
#   0xEE, \
#   0x83, \
#   0x92, \
#   0x30, \
#   0x00, 0x00, 0x00, 0x00, 0x00, 0x05, 0x00, 0x00]

add_to_r1_program = [
    0x80,  # MOV R0, #0
    0x92,  # MOV R1, #2
    0x86,  # MOV R0, #6
    0x30,  # ADD R1, R0
    0xEE,  # STR R0, [14]
    0x00,
    0x00,
    0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

multiply_program = [
    0x80,  # MOV R0, #0
    0x90,  # MOV R1, #0
    0x86,  # MOV R0, #6
    0x92,  # MOV R1, #3
    0x40,  # MUL R0, R1
    0xEE,  # STR R0, [14]
    0x00,
    0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

if __name__ == "__main__":
    cpu = Cpu(multiply_program,undefined)

    print("Press any key ('q' to quit, space for clock, d for debug dump)...")

    original_settings = init_nonblocking_input()
    try:
        while True:
            key = read_key()
            if key:
                # print(f"Key pressed: {repr(key)}") # uncomment to see what's pressed
                if key == 'q':
                    break
                if key == 'd':
                    cpu.debug_dump()
                if key == ' ':
                    cpu.next_cycle()
    finally:
        restore_input(original_settings)
        print("\nExit.")

