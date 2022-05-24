import pygame
from pygame import Vector2
import pygame.midi
from pygame import mixer
import numpy as np
import math
import pretty_midi
import time
import random

# TODO: use interpolation for pitch width and planet radius
# ______________________________
# must not have overlapping systems
#  star must be defined as first element in dict
# objects are stored as key, value pairs where key=name, value=instance of object class
# ______________________________
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
pygame.init()


# constants
# ______________________________
# WIDTH = HEIGHT = 800
WIDTH, HEIGHT = 1280, 746
# WIDTH, HEIGHT = 2040, 1100
FPS = 60  # never change FPS, used in velocity calculation as delta-t
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
PINK = (255, 192, 203)
LIME = (0, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
SILVER = (192, 192, 192)
MAROON = (128, 0, 0)
OLIVE = (128, 128, 0)
PURPLE = (128, 0, 128)
TEAL = (0, 128, 128)
NAVY = (0, 0, 128)
PLANET_COLORS = (WHITE, RED, GREEN, BLUE, ORANGE, PINK, LIME,
                 CYAN, MAGENTA, SILVER, PURPLE, TEAL, NAVY)
BACKGROUND_COLOR = BLACK

PYGAME_RIGHT_CLICK = 1
PYGAME_LEFT_CLICK = 2
PYGAME_ZOOM_OUT = 4
PYGAME_ZOOM_IN = 5
MUSIC_VOLUME = 1
MUSIC_START = 100
MIN_STAR_RADIUS = 10
MIN_SOLAR_RADIUS = 5
FONT_SIZE = WIDTH//80
DEFAULT_PLANET_COLOR = BACKGROUND_COLOR
DEFAULT_PLANET_RADIUS = 10
PLANET_SPACING = 25
G_CUSTOM = 0.0157  # experimentally calculated gravitational constant

ROTATION_ANGLE_CHANGE = 0.05
#______________________________


# star_distribution
#______________________________
STAR_COUNT = 10
MIN_STAR_RADIUS=2
DEFAULT_SMALL_STAR_RADIUS = 10
SMALL_GALAXY_RADIUS = 500
LARGE_GALAXY_RADIUS = 1500
GALAXY_ZOOM_THRESHOLD = 1.2

def find_nearest_star(x, y, galaxy):
    nearest_index = 0
    my_pos = Vector2(x, y)
    nearest_star_distance = my_pos.distance_to(Vector2(galaxy[0][0], galaxy[0][1]))
    for index, star in enumerate(galaxy):
        star_vec = Vector2(star[0], star[1])
        distance = my_pos.distance_to(star_vec)
        if distance < nearest_star_distance:
            nearest_index = index
            nearest_star_distance = distance
    return nearest_index


def create_galaxy(STAR_COUNT, SMALL_GALAXY_RADIUS, LARGE_GALAXY_RADIUS):
    galaxy = []
    for star in range(STAR_COUNT):
        rand_n = random.randint(1, 10)
        if rand_n in range(1, 4+1):
            x_coord = random.randint(-SMALL_GALAXY_RADIUS, SMALL_GALAXY_RADIUS)
            y_coord = random.randint(
                int(-(SMALL_GALAXY_RADIUS**2 - x_coord**2)**(1/2)), int((SMALL_GALAXY_RADIUS**2 - x_coord**2)**(1/2)))
            galaxy.append([x_coord+WIDTH//2, y_coord+HEIGHT//2])
        else:
            x_coord = random.randint(-LARGE_GALAXY_RADIUS, LARGE_GALAXY_RADIUS)
            y_coord = random.randint(
                int(-(LARGE_GALAXY_RADIUS**2 - x_coord**2)**(1/2)), int((LARGE_GALAXY_RADIUS**2 - x_coord**2)**(1/2)))
            galaxy.append([x_coord+WIDTH//2, y_coord+HEIGHT//2])
    return galaxy
# ______________________________


WIN = pygame.display.set_mode((WIDTH, HEIGHT))
space_background = pygame.image.load('space_bg.png').convert()
space_background = pygame.transform.scale(space_background, (WIDTH, HEIGHT))
space_background.set_alpha(100)

blue_star = pygame.image.load('blue_star.png')

pygame.display.set_caption("Solar Synesthesia")
clock = pygame.time.Clock()

THE_BOLD_FONT = 'THEBOLDFONT.ttf'
global font
font = pygame.font.Font(THE_BOLD_FONT, FONT_SIZE)

VIEW_OPTIONS = ('star', 'galaxy')
view_mode = VIEW_OPTIONS[0] # must only be 'star' or 'galaxy'

def write_text(text, location, color=(255, 255, 255)):
    WIN.blit(font.render(text, True, color), location)

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

midi_file = 'Schubert_-_Symphony_No.8._Mvt.1._D.759._Professional_production_full_score._Unfinished.mid'
mp3_file = 'Schubert_-_Symphony_No.8._Mvt.1._D.759._Professional_production_full_score._Unfinished.mp3'

# midi_file = 'Eine_Kleine_Nachtmusik_1st_Movement.mid'
# mp3_file = 'Eine_Kleine_Nachtmusik_1st_Movement.mp3'

# midi_file = '1812_Overture_Complete_Orchestral_Score.mid'
# mp3_file = '1812_Overture_Complete_Orchestral_Score.mp3'

# midi_file = 'LOUD_Mahler_8_finale_instrumentation_visualized.mid'
# mp3_file = 'LOUD_Mahler_8_finale_instrumentation_visualized.mp3'

# midi_file = 'Chorus_Mysticus_-_Mahler_Symphony_of_a_Thousand_WIP.mid'
# mp3_file = 'Chorus_Mysticus_-_Mahler_Symphony_of_a_Thousand_WIP.mp3'

# midi_file = 'REQUIEM_CONFUTATIS.mid'
# mp3_file = 'REQUIEM_CONFUTATIS.mp3'


midi_data = pretty_midi.PrettyMIDI(midi_file)
midi_data.remove_invalid_notes()

# array to keep track of path of celestial bodies
# TODO: change to local orbital path tracking rather than using a global variable since its impossible to have a large array to hold all system info
# background_orbit_paths_array = np.zeros((WIDTH, HEIGHT, 3), dtype=np.uint8)
# background_orbit_paths_array[0:, 0:, 0:] = BACKGROUND_COLOR


def rotate_axis(matrix, axis, theta):
    if axis == 'x':
        rotation_matrix = np.array([[1, 0, 0],
                                    [0, np.cos(theta), -np.sin(theta)],
                                    [0, np.sin(theta), np.cos(theta)]])
    elif axis == 'y':
        rotation_matrix = np.array([[np.cos(theta), 0, np.sin(theta)],
                                    [0, 1, 0],
                                    [-np.sin(theta), 0, np.cos(theta)]])
    elif axis == 'z':
        rotation_matrix =np.array([[np.cos(theta), -np.sin(theta), 0],
                                    [np.sin(theta), np.cos(theta), 0],
                                    [0, 0, 1]])
    return np.dot(matrix, rotation_matrix)


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

    def __rmul__(self, scalar):  # scalar must be on left side (scalar*Vector)
        return Vector(self.x*scalar, self.y*scalar)

    def distance(vec_1, vec_2):  # can be used for distance between points as well
        return (vec_2 - vec_1).magnitude()


class PlanetarySystem:
    MIN_RADIUS = 200
    MAX_RADIUS = min(WIDTH, HEIGHT)

    def __init__(self, bodies):
        self.bodies = bodies  # dict of CelestialBodies planets
        self.star = None  # will be the element where self.is_planet=False

        # set the initial velocity of circular orbits
        for body in self.bodies.values():
            if body.is_planet:  # use centripital motion equation for initial velocity
                body.vy = math.sqrt(
                    self.star.mass*G_CUSTOM/(Vector.distance(self.star.get_pos_vector(), body.get_pos_vector())))
            else:  # star must be defined first else error since star cannot be used in above equation
                self.star = body  # if not a planet it must be a star

    def next_frame(self):
        for body in self.bodies.values():
            body.next_frame(self.bodies)


class CelestialBody:
    def __init__(self, name, x, y=HEIGHT//2, instrument=None, song_duration=None, color=DEFAULT_PLANET_COLOR, radius=DEFAULT_PLANET_RADIUS, is_planet=True, vx=0, vy=0, mass=0, image=None):
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
        self.image = image
        self.x_rotation = self.x # used for rotation matrix implementation
        self.y_rotation = self.y


    # add to initial velocity vector
    def get_gravitational_velocity_vec(self, object_b):
        force_magnitude = object_b.mass / \
            Vector.distance(self.get_pos_vector(),
                            object_b.get_pos_vector())**2*(1/FPS)  # vf_a=M_b/r^2
        force_direction = object_b.get_pos_vector() - self.get_pos_vector()
        return force_magnitude/force_direction.magnitude()*force_direction

    def update_orbit_velocity(self, object_b):
        gravity_vec = self.get_gravitational_velocity_vec(object_b)
        self.vx += gravity_vec.x
        self.vy += gravity_vec.y

    def get_pos_vector(self):
        return Vector(self.x, self.y)

    # only returns True when center of planet is outside the screen, not the edge, used for orbit paths tracking array
    def check_out_of_bounds(self):
        if self.x <= 0 or self.x + self.radius >= WIDTH:
            return True
        if self.y <= 0 or self.y + self.radius >= HEIGHT:
            return True
        return False

    def update_position(self):
        self.x += self.vx
        self.y += self.vy
        if not self.check_out_of_bounds():  # don't draw orbit pixel if object not in frame
            # background_orbit_paths_array[int(self.x), int(self.y), 0:3] = self.color
            pass

    def change_planet_on_note(self):
        time_elapsed = (time.time() - start_time) % self.song_duration
        # initialize such that it is note referenced before assignment
        current_note = self.notes[0]
        for note in self.notes:
            if time_elapsed > note.start and time_elapsed < note.end:
                current_note = note
                break

        # between current note (start, end)
        if time_elapsed > current_note.start and time_elapsed < current_note.end:
            self.color = self.NOTE_COLOR
            self.radius = DEFAULT_PLANET_RADIUS*current_note.velocity/65
            self.border = int(current_note.pitch/10)

        # if self.note_index > 0:
        else:
            # if time_elapsed < current_note.start and time_elapsed > self.notes[self.note_index-1].end: # between pause of last note and current note
            self.color = DEFAULT_PLANET_COLOR
            self.radius = DEFAULT_PLANET_RADIUS

    def draw(self):
        global ZOOM_FACTOR

        if self.is_planet:
            self.change_planet_on_note()

        if self.color != DEFAULT_PLANET_COLOR:  # don't draw planet unless it changes color
            draw_x = WIDTH//2 - ZOOM_FACTOR*(WIDTH//2-self.x_rotation)
            draw_y = HEIGHT//2 - ZOOM_FACTOR*(HEIGHT//2-self.y_rotation)
            draw_radius = self.radius*ZOOM_FACTOR

            if self.image != None:
                transformed_image = pygame.transform.scale(
                    self.image, (draw_radius*2, draw_radius*2))
                WIN.blit(transformed_image, (self.x -
                         draw_radius, self.y-draw_radius))

            else:  # blit circle if no image is provided
                pygame.draw.circle(surface=WIN, color=self.color, center=(
                    draw_x, draw_y), radius=draw_radius, width=self.border)

    # combines all methods required to draw object to screen and interact with other objects
    def next_frame(self, planetary_system):  # pass entire solar system
        # used to exclude current body without changing global
        planetary_system_copy = planetary_system.copy()
        del planetary_system_copy[self.name]

        if self.is_planet:  # sun is not influenced by planets
            for body in planetary_system_copy.values():
                self.update_orbit_velocity(body)
            self.update_position()
        self.draw()

# create galaxy
#______________________________
galaxy = create_galaxy(STAR_COUNT, SMALL_GALAXY_RADIUS, LARGE_GALAXY_RADIUS)
x, y = 0, 0
x_center_offset, y_center_offset = 0, 0

curr_star_index=0
curr_star=galaxy[curr_star_index]
galaxy_draw_pos = galaxy
#______________________________


# create solar system
#______________________________
solar_system_dict = {'sun': CelestialBody(
    name='sun', x=WIDTH//2, is_planet=False, color=YELLOW, radius=90, mass=100000, image=blue_star)}
for index, instrument in enumerate(midi_data.instruments):
    solar_system_dict[index] = CelestialBody(name=index, instrument=instrument, song_duration=midi_data.get_end_time(
    ), x=WIDTH//2 - PlanetarySystem.MIN_RADIUS - (PLANET_SPACING)*(index+1))

solar_system = PlanetarySystem(solar_system_dict)
#______________________________


mixer.music.load(mp3_file)
mixer.music.play(loops=0, start=MUSIC_START)

start_time = time.time() - MUSIC_START
last_check_for_drift = time.time() - MUSIC_START  # account for midi and mp3 drifting

# _______rotation code_______

projection_matrix =np.array([[1, 0, 0],
                            [0, 1, 0], 
                            [0, 0, 0]])
x_axis_angle = y_axis_angle = z_axis_angle = 0 # keeps track of angles rotated along each axis
#____________________________


running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if view_mode == VIEW_OPTIONS[0]: # view check
                if event.button == PYGAME_ZOOM_OUT:
                    if ZOOM_FACTOR-ZOOM_CHANGE > 0:
                        ZOOM_FACTOR -= ZOOM_CHANGE
                        MUSIC_VOLUME = ZOOM_FACTOR
                        pygame.mixer.music.set_volume(MUSIC_VOLUME)
                    else:
                        MUSIC_VOLUME = 0
                        pygame.mixer.music.set_volume(MUSIC_VOLUME)
                if event.button == PYGAME_ZOOM_IN:
                    ZOOM_FACTOR += ZOOM_CHANGE
                    if ZOOM_FACTOR > 1:
                        MUSIC_VOLUME = 1
                    else:
                        MUSIC_VOLUME = ZOOM_FACTOR
                    pygame.mixer.music.set_volume(MUSIC_VOLUME)
            else:
                curr_star = galaxy[curr_star_index]
                x_center_offset = WIDTH//2-curr_star[0]
                y_center_offset = HEIGHT//2-curr_star[1]

                if event.button == PYGAME_RIGHT_CLICK:
                    x, y = pygame.mouse.get_pos()
                    curr_star_index = find_nearest_star(x, y, galaxy_draw_pos)
                    

                if event.button == PYGAME_ZOOM_OUT and ZOOM_FACTOR-ZOOM_CHANGE > 0 and ZOOM_FACTOR*DEFAULT_SMALL_STAR_RADIUS >= MIN_STAR_RADIUS:
                    ZOOM_FACTOR -= ZOOM_CHANGE
                if event.button == PYGAME_ZOOM_IN:
                    ZOOM_FACTOR += ZOOM_CHANGE

        keys = pygame.key.get_pressed()
        
        if view_mode == VIEW_OPTIONS[0]: # view check
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    ZOOM_FACTOR = 1
                    x_axis_angle = y_axis_angle = z_axis_angle = 0
            else:
                if keys[pygame.K_r]:
                    ZOOM_FACTOR = 1


    if view_mode == VIEW_OPTIONS[0]: # view check
        two_dim_projection = [[planet.x-WIDTH//2, planet.y-HEIGHT//2, 0] for planet in solar_system.bodies.values()]
        three_dim_points_copy = two_dim_projection.copy()


        # without using if statements
        y_axis_angle += ROTATION_ANGLE_CHANGE*(-int(keys[pygame.K_LEFT]) + int(keys[pygame.K_RIGHT]))
        x_axis_angle += ROTATION_ANGLE_CHANGE*(-int(keys[pygame.K_DOWN]) + int(keys[pygame.K_UP]))
        z_axis_angle += ROTATION_ANGLE_CHANGE*(-int(keys[pygame.K_q]) + int(keys[pygame.K_w]))

        # if keys[pygame.K_LEFT]: y_axis_angle -= ROTATION_ANGLE_CHANGE
        # if keys[pygame.K_RIGHT]: y_axis_angle += ROTATION_ANGLE_CHANGE
        # if keys[pygame.K_UP]: x_axis_angle += ROTATION_ANGLE_CHANGE
        # if keys[pygame.K_DOWN]: x_axis_angle -= ROTATION_ANGLE_CHANGE
        # if keys[pygame.K_q]: z_axis_angle -= ROTATION_ANGLE_CHANGE
        # if keys[pygame.K_w]: z_axis_angle += ROTATION_ANGLE_CHANGE

        three_dim_points_copy = rotate_axis(three_dim_points_copy, 'x', x_axis_angle)
        three_dim_points_copy = rotate_axis(three_dim_points_copy, 'y', y_axis_angle)
        three_dim_points_copy = rotate_axis(three_dim_points_copy, 'z', z_axis_angle)
        two_dim_projection = np.dot(three_dim_points_copy, projection_matrix)

    if view_mode == VIEW_OPTIONS[0]: # view check
        WIN.fill(BACKGROUND_COLOR)
        WIN.blit(space_background, (0, 0))
        # pygame.surfarray.blit_array(WIN, background_orbit_paths_array)
        if solar_system.star.radius*ZOOM_FACTOR <= MIN_SOLAR_RADIUS:
            view_mode = VIEW_OPTIONS[1]
            pygame.mixer.music.stop()
            # WIN.blit(pygame.transform.scale(blue_star, (MIN_STAR_RADIUS, MIN_STAR_RADIUS)),
                    # (solar_system.star.x-MIN_STAR_RADIUS, solar_system.star.y-MIN_STAR_RADIUS))  # make star a tiny point

        # if solar_system.star.radius*ZOOM_FACTOR <= 3: pygame.draw.circle(surface=WIN, color=YELLOW, center=(WIDTH//2, HEIGHT//2), radius=3) # make star a tiny point


        else:
            for planet, pos in zip(solar_system.bodies.values(), two_dim_projection):
                if planet.is_planet:
                    planet.x_rotation = pos[0] + WIDTH//2
                    planet.y_rotation = pos[1] + HEIGHT//2
            solar_system.next_frame()

        write_text(f'T={round(time.time()-start_time, 3)} s',
                (0, 0))  # update screen counter
        write_text(f'{midi_file}', (0, FONT_SIZE), GREY)

        # if time.time() - last_check_for_drift > 10:  # check for drift every 10 seconds
        #     new_start_time = (
        #         time.time() - start_time) % solar_system.bodies[0].song_duration
        #     mixer.music.play(loops=0, start=new_start_time)
        #     last_check_for_drift = time.time()
    else:
        WIN.fill(BLACK)
        galaxy_draw_pos = []
        for index, star in enumerate(galaxy):
            draw_x = curr_star[0]-ZOOM_FACTOR*(curr_star[0]-star[0]) + x_center_offset
            draw_y = curr_star[1]-ZOOM_FACTOR*(curr_star[1]-star[1]) + y_center_offset

            galaxy_draw_pos.append([draw_x, draw_y])

            if DEFAULT_SMALL_STAR_RADIUS*ZOOM_FACTOR >= MIN_STAR_RADIUS:
                # new_radius = DEFAULT_RADIUS*ZOOM_FACTOR
                new_radius = MIN_STAR_RADIUS
            else:
                new_radius = MIN_STAR_RADIUS

                
            if index == curr_star_index:
                pygame.draw.circle(WIN, RED, (draw_x, draw_y), new_radius)
            else:
                pygame.draw.circle(WIN, WHITE, (draw_x, draw_y), new_radius)
        if ZOOM_FACTOR >= GALAXY_ZOOM_THRESHOLD:
            mixer.music.load(mp3_file)
            mixer.music.play(loops=0, start=time.time() % list(solar_system.bodies.values())[1].song_duration)
            view_mode = VIEW_OPTIONS[0]
            ZOOM_FACTOR = 1

    pygame.display.flip()
pygame.quit()
