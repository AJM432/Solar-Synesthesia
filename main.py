import pygame
import pygame.midi
from pygame import mixer
import numpy as np
import math
import pretty_midi
import time
import random

# TODO: use interpolation for pitch width and planet radius
 #______________________________
 # must not have overlapping systems
#  star must be defined as first element in dict
# objects are stored as key, value pairs where key=name, value=instance of object class
#______________________________
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
pygame.init()
# constants
# ______________________________
# WIDTH = HEIGHT = 800
WIDTH = 1280
HEIGHT = 740
FPS = 60 # never change FPS, used in velocity calculation as delta-t
ZOOM_FACTOR = 1
ZOOM_CHANGE = 0.025

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 190, 0)
ORANGE = (255, 215, 0)
GREY = (125, 125, 125)
DARK_GREY = (50, 50, 50)
PALE_YELLOW = (240, 240, 0)
PINK = (255,192,203)
LIME = (0,255,0)
CYAN = (0,255,255)
MAGENTA = (255,0,255)
SILVER = (192,192,192)
MAROON = (128,0,0)
OLIVE = (128,128,0)
PURPLE = (128,0,128)
TEAL = (0,128,128)
NAVY = (0,0,128)
PLANET_COLORS = (WHITE, RED, GREEN, BLUE, ORANGE, PINK, LIME, CYAN, MAGENTA, SILVER, MAROON, OLIVE, PURPLE, TEAL, NAVY)
BACKGROUND_COLOR = BLACK

PYGAME_ZOOM_OUT = 4
PYGAME_ZOOM_IN = 5
MUSIC_VOLUME = 1
DEFAULT_PLANET_COLOR = BACKGROUND_COLOR
DEFAULT_PLANET_RADIUS = 10
PLANET_SPACING = 15
G_CUSTOM = 0.0157 # experimentally calculated gravitational constant

# ______________________________

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
space_background = pygame.image.load('space_bg.png').convert()
space_background = pygame.transform.scale(space_background, (WIDTH, HEIGHT))
space_background.set_alpha(100)



pygame.display.set_caption("Solar Synesthesia")
clock = pygame.time.Clock()

global font
font=pygame.font.Font(None,20)

def write_text(text,location,color=(255,255,255)):
    WIN.blit(font.render(text,True,color),location)

# midi_file = 'Beethoven__Symphony_No._5_Op.67_Mvt._1.mscz.mid'
# mp3_file = 'Beethoven__Symphony_No._5_Op.67_Mvt._1.mscz.mp3'

# midi_file = '_Symphony_No._41_in_C_major_K._551_Movement_4.mid'
# mp3_file = '_Symphony_No._41_in_C_major_K._551_Movement_4.mp3'

# midi_file = 'Antonin_Dvorak_Serenade_for_String_Orchestra_in_E_major_Op.22_II._Tempo_di_Valse.mid'
# mp3_file = 'Antonin_Dvorak_Serenade_for_String_Orchestra_in_E_major_Op.22_II._Tempo_di_Valse.mp3'

# midi_file = 'swan_lake-scene.mid'
# mp3_file = 'swan_lake-scene.mp3'

# midi_file = 'Mozart_Symphony_No._40_in_G_Minor_K._550_I._Molto_Allegro.mid'
# mp3_file = 'Mozart_Symphony_No._40_in_G_Minor_K._550_I._Molto_Allegro.mp3'

# midi_file = 'Requiem_in_D_Minor_K._626_III._Sequentia_Lacrimosa_By_W._A._Mozart.mid'
# mp3_file = 'Requiem_in_D_Minor_K._626_III._Sequentia_Lacrimosa_By_W._A._Mozart.mp3'

# midi_file = 'Schubert_-_Symphony_No.8._Mvt.1._D.759._Professional_production_full_score._Unfinished.mid'
# mp3_file = 'Schubert_-_Symphony_No.8._Mvt.1._D.759._Professional_production_full_score._Unfinished.mp3'

# midi_file = 'Eine_Kleine_Nachtmusik_1st_Movement.mid'
# mp3_file = 'Eine_Kleine_Nachtmusik_1st_Movement.mp3'

midi_file = '1812_Overture_Complete_Orchestral_Score.mid'
mp3_file = '1812_Overture_Complete_Orchestral_Score.mp3'

# midi_file = 'LOUD_Mahler_8_finale_instrumentation_visualized.mid'
# mp3_file = 'LOUD_Mahler_8_finale_instrumentation_visualized.mp3'

# midi_file = 'Chorus_Mysticus_-_Mahler_Symphony_of_a_Thousand_WIP.mid'
# mp3_file = 'Chorus_Mysticus_-_Mahler_Symphony_of_a_Thousand_WIP.mp3'

midi_data = pretty_midi.PrettyMIDI(midi_file)
midi_data.remove_invalid_notes()

# array to keep track of path of celestial bodies
# TODO: change to local orbital path tracking rather than using a global variable since its impossible to have a large array to hold all system info
# background_orbit_paths_array = np.zeros((WIDTH, HEIGHT, 3), dtype=np.uint8)
# background_orbit_paths_array[0:, 0:, 0:] = BACKGROUND_COLOR

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def magnitude(self):
        return (self.x**2 + self.y**2)**(1/2)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return self + -1*other

    def __repr__(self):
        return f"({self.x}, {self.y})"

    def __rmul__(self, scalar): # scalar must be on left side (scalar*Vector)
        return Vector(self.x*scalar, self.y*scalar)

    def distance(vec_1, vec_2): # can be used for distance between points as well
        return (vec_2 - vec_1).magnitude()


class PlanetarySystem:
    MIN_RADIUS = 200
    MAX_RADIUS = min(WIDTH, HEIGHT)
    def __init__(self, bodies):
        self.bodies = bodies # dict of CelestialBodies planets
        self.star = None # will be the element where self.is_planet=False

        # set the initial velocity of circular orbits
        for body in self.bodies.values():
            if body.is_planet: # use centripital motion equation for initial velocity
                body.vy = math.sqrt(self.star.mass*G_CUSTOM/(Vector.distance(self.star.get_pos_vector(), body.get_pos_vector())))
            else: # star must be defined first else error since star cannot be used in above equation
                self.star = body # if not a planet it must be a star
    
    def next_frame(self):
        for body in self.bodies.values():
            body.next_frame(self.bodies)


class CelestialBody:
    def __init__(self, name, x, y=HEIGHT//2, instrument=None, song_duration=None, color=DEFAULT_PLANET_COLOR, radius=DEFAULT_PLANET_RADIUS, is_planet=True, vx=0, vy=0, mass=0):
        if is_planet:
            self.instrument = instrument
            self.song_duration = song_duration
            self.notes = instrument.notes
            self.num_notes = len(self.instrument.notes)
            self.note_index = 0
            self.NOTE_COLOR = random.choice(PLANET_COLORS)

        self.name = name
        self.mass = mass
        self.name = name
        self.vx = vx
        self.x = x
        self.y = y
        self.vy = vy
        self.color = color
        self.radius = radius
        self.is_planet = is_planet
        self.border = 0

    def get_gravitational_velocity_vec(self, object_b): # add to initial velocity vector
        force_magnitude = object_b.mass/Vector.distance(self.get_pos_vector(), object_b.get_pos_vector())**2*(1/FPS) # vf_a=M_b/r^2
        force_direction = object_b.get_pos_vector() - self.get_pos_vector()
        return force_magnitude/force_direction.magnitude()*force_direction


    def update_orbit_velocity(self, object_b):
        gravity_vec = self.get_gravitational_velocity_vec(object_b)
        self.vx += gravity_vec.x
        self.vy += gravity_vec.y

    def get_pos_vector(self):
        return Vector(self.x, self.y)

    def check_out_of_bounds(self): # only returns True when center of planet is outside the screen, not the edge, used for orbit paths tracking array
        if self.x <= 0 or self.x + self.radius >= WIDTH:
            return True
        if self.y <= 0 or self.y + self.radius >= HEIGHT:
            return True
        return False
    
    def update_position(self):
        self.x += self.vx
        self.y += self.vy
        if not self.check_out_of_bounds(): # don't draw orbit pixel if object not in frame
            # background_orbit_paths_array[int(self.x), int(self.y), 0:3] = self.color
            pass

    def change_planet_on_note(self):
        time_elapsed = (time.time() - start_time) % self.song_duration
        current_note = self.notes[0] # initialize such that it is note referenced before assignment
        for note in self.notes:
            if time_elapsed > note.start and time_elapsed < note.end:
                current_note = note
                break

        if time_elapsed > current_note.start and time_elapsed < current_note.end: # between current note (start, end)
            self.color = self.NOTE_COLOR
            self.radius = DEFAULT_PLANET_RADIUS*current_note.velocity/65
            self.border = int(current_note.pitch/10)

            # if self.note_index < self.num_notes-1:
                # self.note_index += 1
            # else:
                # self.note_index = 0
                # self.color = DEFAULT_PLANET_COLOR
                # self.radius = DEFAULT_PLANET_RADIUS

        # if self.note_index > 0:
        else:
            # if time_elapsed < current_note.start and time_elapsed > self.notes[self.note_index-1].end: # between pause of last note and current note
            self.color = DEFAULT_PLANET_COLOR
            self.radius = DEFAULT_PLANET_RADIUS

    def draw(self):
        global ZOOM_FACTOR
        if self.is_planet:
            self.change_planet_on_note()
        if self.color != DEFAULT_PLANET_COLOR: # don't draw planet unless it changes color
            draw_x = WIDTH//2 - ZOOM_FACTOR*(WIDTH//2-self.x)
            draw_y = HEIGHT//2 - ZOOM_FACTOR*(HEIGHT//2-self.y)
            draw_radius = self.radius*ZOOM_FACTOR
            pygame.draw.circle(surface=WIN, color=self.color, center=(draw_x, draw_y), radius=draw_radius, width=self.border)
            # pygame.draw.circle(surface=WIN, color=self.color, center=(self.x, self.y), radius=self.radius)

    # combines all methods required to draw object to screen and interact with other objects
    def next_frame(self, planetary_system): # pass entire solar system
        planetary_system_copy = planetary_system.copy() # used to exclude current body without changing global 
        del planetary_system_copy[self.name]

        if self.is_planet: # sun is not influenced by planets
            for body in planetary_system_copy.values():
                self.update_orbit_velocity(body)
            self.update_position()
        self.draw()

    


solar_system_dict = {'sun': CelestialBody(name='sun', x=WIDTH//2, is_planet=False, color=YELLOW, radius=90, mass=100000)}
for index, instrument in enumerate(midi_data.instruments):
    solar_system_dict[index] = CelestialBody(name=index, instrument=instrument, song_duration=midi_data.get_end_time(), x=WIDTH//2 - PlanetarySystem.MIN_RADIUS - (PLANET_SPACING)*(index+1))


solar_system = PlanetarySystem(solar_system_dict)

mixer.music.load(mp3_file)
mixer.music.play(loops=0, start=0)

start_time = time.time()
last_check_for_drift = time.time() # account for midi and mp3 drifting


running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == PYGAME_ZOOM_OUT:
                if ZOOM_FACTOR-ZOOM_CHANGE>0:
                    ZOOM_FACTOR-=ZOOM_CHANGE
                    MUSIC_VOLUME = ZOOM_FACTOR
                    pygame.mixer.music.set_volume(MUSIC_VOLUME)
                else:
                    MUSIC_VOLUME = 0
                    pygame.mixer.music.set_volume(MUSIC_VOLUME)
            if event.button == PYGAME_ZOOM_IN: 
                ZOOM_FACTOR+=ZOOM_CHANGE
                if ZOOM_FACTOR > 1:
                    MUSIC_VOLUME = 1
                else:
                    MUSIC_VOLUME = ZOOM_FACTOR
                pygame.mixer.music.set_volume(MUSIC_VOLUME)
            
        # keys = pygame.key.get_pressed()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                ZOOM_FACTOR = 1

    
    WIN.fill(BACKGROUND_COLOR)
    WIN.blit(space_background, (0, 0))
    # pygame.surfarray.blit_array(WIN, background_orbit_paths_array)
    if solar_system.star.radius*ZOOM_FACTOR <= 3: pygame.draw.circle(surface=WIN, color=YELLOW, center=(WIDTH//2, HEIGHT//2), radius=3) # make star a tiny point

    else: solar_system.next_frame()

    write_text(f'T={round(time.time()-start_time, 3)} s', (0, 0)) # update screen counter
    write_text(f'{midi_file}', (0, 15), GREY)

    if time.time() - last_check_for_drift > 10: # check for drift every 10 seconds
        new_start_time = (time.time() - start_time) % solar_system.bodies[0].song_duration
        mixer.music.play(loops=0, start=new_start_time)
        last_check_for_drift = time.time()

    pygame.display.flip()
pygame.quit()
