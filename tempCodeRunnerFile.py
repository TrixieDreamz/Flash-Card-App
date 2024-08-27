import os
import pygame

# Initialize Pygame mixer
pygame.mixer.init()

# Set base path for sounds
base_path = os.path.dirname(os.path.abspath(__file__))

# Initialize sound files with absolute paths
typing_sound = pygame.mixer.Sound(os.path.join(base_path, 'sounds', 'typing.mp3'))
right_sound = pygame.mixer.Sound(os.path.join(base_path, 'sounds', 'right.mp3'))
wrong_sound = pygame.mixer.Sound(os.path.join(base_path, 'sounds', 'wrong.mp3'))

# Test sound playback directly
try:
    print("Playing typing sound...")
    typing_sound.play()
    pygame.time.delay(2000)  # Delay to allow sound to play completely

    print("Playing right sound...")
    right_sound.play()
    pygame.time.delay(2000)  # Delay to allow sound to play completely

    print("Playing wrong sound...")
    wrong_sound.play()
    pygame.time.delay(2000)  # Delay to allow sound to play completely

except pygame.error as e:
    print(f"Pygame error: {e}")
