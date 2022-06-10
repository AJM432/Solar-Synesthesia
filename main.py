import pygame
import numpy as np
import pretty_midi
import time
import random
import os
import pickle

from pygments import highlight
from constants import *
import datetime

# constants
# ______________________________
# ______________________________
# WIDTH = HEIGHT = 800
WIDTH, HEIGHT = 1280, 746
# WIDTH, HEIGHT = 2048, 1099
FPS = 60  # never change FPS, used in velocity calculation as delta-t
ZOOM_FACTOR = 1
ZOOM_CHANGE = 0.05

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

DRIFT_CHECK_DELAY = 5  # updates song play time every x seconds to remove errors
PYGAME_LEFT_CLICK = 1
PYGAME_RIGHT_CLICK = 2
PYGAME_ZOOM_OUT = 4
PYGAME_ZOOM_IN = 5
MUSIC_VOLUME = 1
MUSIC_START = 0
MIN_STAR_RADIUS = 10
MIN_SOLAR_RADIUS = 5
FONT_SIZE = WIDTH//80
DEFAULT_PLANET_COLOR = BACKGROUND_COLOR
DEFAULT_PLANET_RADIUS = 10
PLANET_SPACING = 40
G_CUSTOM = 0.0157  # experimentally calculated gravitational constant
SOLAR_ZOOM_FACTOR = 1

ROTATION_ANGLE_CHANGE = 0.05
MUSIC_SKIP_INCREMENT = 2.5


# ______________________________


# star_distribution
# ______________________________
MIN_STAR_RADIUS = 2
DEFAULT_SMALL_STAR_RADIUS = 10
SMALL_GALAXY_RADIUS = 500
LARGE_GALAXY_RADIUS = 1500
GALAXY_ZOOM_THRESHOLD = 1.1
GALAXY_ZOOM_FACTOR = 1

VIEW_OPTIONS = ('star', 'galaxy')
view_mode = VIEW_OPTIONS[0]  # must only be 'star' or 'galaxy'
# ______________________________

# ______________________________


# TODO: use interpolation for pitch width and planet radius
# ______________________________
# must not have overlapping systems
#  star must be defined as first element in dict
# objects are stored as key, value pairs where key=name, value=instance of object class
# ______________________________
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solar Synesthesia")
clock = pygame.time.Clock()

# Font Setup __________________________________________
THE_BOLD_FONT_FILE = os.path.join("assets", "font", "THEBOLDFONT.ttf")
font = pygame.font.Font(THE_BOLD_FONT_FILE, FONT_SIZE)
# Font Setup __________________________________________


# load assets
# each time you import a new song you have to update pickle dictionary
# ______________________________
star_images = [pygame.image.load(os.path.join('assets', 'images', 'stars', x)) for x in os.listdir(
    os.path.join('assets', 'images', 'stars')) if x != '.DS_Store']
planet_images = [pygame.image.load(os.path.join('assets', 'images', 'planets', x)) for x in os.listdir(
    os.path.join('assets', 'images', 'planets')) if x != '.DS_Store']

# use if you want to add a new song
# ______________________________
# song_pretty_midi_files = {x: pretty_midi.PrettyMIDI(os.path.join('music', x, x+'.mid')) for x in os.listdir('music') if x != '.DS_Store'}
# midi_pickle_file = open('pretty_midi', 'wb')
# pickle.dump(song_pretty_midi_files, midi_pickle_file)
# midi_pickle_file.close()
# ______________________________

midi_data_file = 'pretty_midi'
with open(midi_data_file, 'rb') as midi_pickle_file:
    # load midi data from pickle object created beforehand
    song_pretty_midi_files = pickle.load(midi_pickle_file)

# ______________________________


def find_nearest_star(x, y, galaxy):
    nearest_index_name = list(galaxy.keys())[0]  # get random index to compare
    my_pos = Vector(x, y)
    nearest_star_distance = my_pos.distance(
        Vector(galaxy[nearest_index_name][0], galaxy[nearest_index_name][1]))
    for key, value in galaxy.items():
        star_vec = Vector(value[0], value[1])
        distance = my_pos.distance(star_vec)
        if distance < nearest_star_distance:
            nearest_index_name = key
            nearest_star_distance = distance
    return nearest_index_name


def create_galaxy(SMALL_GALAXY_RADIUS, LARGE_GALAXY_RADIUS, music_folder='music'):
    galaxy = {}
    for folder_name in os.listdir(music_folder):
        if not folder_name.startswith('.'):  # make sure its not a .ds file
            rand_n = random.randint(1, 10)
            if rand_n in range(1, 4+1):
                x_coord = random.randint(-SMALL_GALAXY_RADIUS,
                                         SMALL_GALAXY_RADIUS)
                y_coord = random.randint(
                    int(-(SMALL_GALAXY_RADIUS**2 - x_coord**2)**(1/2)), int((SMALL_GALAXY_RADIUS**2 - x_coord**2)**(1/2)))
                galaxy[folder_name] = [x_coord+WIDTH//2, y_coord+HEIGHT//2]
            else:
                x_coord = random.randint(-LARGE_GALAXY_RADIUS,
                                         LARGE_GALAXY_RADIUS)
                y_coord = random.randint(
                    int(-(LARGE_GALAXY_RADIUS**2 - x_coord**2)**(1/2)), int((LARGE_GALAXY_RADIUS**2 - x_coord**2)**(1/2)))
                galaxy[folder_name] = [x_coord+WIDTH//2, y_coord+HEIGHT//2]
    return galaxy

# ______________________________


def play_song(duration, change=0):
    global last_check_for_drift
    global new_start_time
    global start_time
    start_time += change
    new_start_time = (time.time() - start_time) % duration
    pygame.mixer.music.play(loops=0, start=new_start_time)
    last_check_for_drift = time.time()


space_background_file = os.path.join(
    "assets", "images", "space_background.png")
space_background = pygame.image.load(space_background_file).convert()
space_background = pygame.transform.scale(space_background, (WIDTH, HEIGHT))
space_background.set_alpha(100)

background_surf = pygame.Surface((WIDTH, HEIGHT))
background_surf.fill(BACKGROUND_COLOR)
background_surf.blit(space_background, (0, 0))

# classes_____________________________________________


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
                body.vy = np.sqrt(
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
        self.height_offset = 0  # for pitch
        self.image = image
        self.x_rotation = self.x  # used for rotation matrix implementation
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
            self.radius = DEFAULT_PLANET_RADIUS*current_note.velocity/60
            self.height_offset = int(current_note.pitch//5)

        # if self.note_index > 0:
        else:
            # if time_elapsed < current_note.start and time_elapsed > self.notes[self.note_index-1].end: # between pause of last note and current note
            self.color = DEFAULT_PLANET_COLOR
            self.radius = DEFAULT_PLANET_RADIUS

    def draw(self):
        global SOLAR_ZOOM_FACTOR
        global solar_system
        x_solar_center_offset = WIDTH//2 - solar_system.star.x
        y_solar_center_offset = HEIGHT//2 - solar_system.star.y
        if self.is_planet:
            self.change_planet_on_note()

        if self.color != DEFAULT_PLANET_COLOR:  # don't draw planet unless it changes color

            draw_x = WIDTH//2 - SOLAR_ZOOM_FACTOR*(WIDTH//2-self.x_rotation)
            draw_y = HEIGHT//2 - SOLAR_ZOOM_FACTOR*(HEIGHT//2-self.y_rotation)

            draw_radius = self.radius*SOLAR_ZOOM_FACTOR

            if self.image != None:
                transformed_image = pygame.transform.scale(
                    self.image, (draw_radius*2, draw_radius*2))
                WIN.blit(transformed_image, (draw_x-draw_radius,
                         draw_y-draw_radius + self.height_offset))

            else:  # blit circle if no image is provided
                pygame.draw.circle(surface=WIN, color=self.color, center=(
                    draw_x, draw_y+self.height_offset), radius=draw_radius, width=0)

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

# classes_____________________________________________


def write_text(text, location, color=(255, 255, 255)):
    WIN.blit(font.render(text, True, color), location)

def find_menu():
    global curr_star_name
    song_list = list(galaxy.keys())
    highlight_index = song_list.index(curr_star_name)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    initialize_new_song()
                    return

                if event.key == pygame.K_UP and highlight_index > 0:
                    highlight_index -= 1

                if event.key == pygame.K_DOWN and highlight_index < len(song_list)-1:
                    highlight_index += 1

                curr_star_name = song_list[highlight_index]
        
        WIN.fill(BLACK)
        for index, song in enumerate(song_list):
            if index == highlight_index:
                write_text(f'{index}: {song}', (0, FONT_SIZE*index), GREEN)
            else:
                write_text(f'{index}: {song}', (0, FONT_SIZE*index))

        pygame.display.update()


def initialize_new_song():
    global mp3_file, midi_data, solar_system_dict, curr_star_name, solar_system
    mp3_file = os.path.join(
        'music', curr_star_name, curr_star_name + '.mp3')

    midi_data = song_pretty_midi_files[curr_star_name]
    midi_data.remove_invalid_notes()

    solar_system_dict = {'sun': CelestialBody(
        name='sun', x=WIDTH//2, is_planet=False, color=YELLOW, radius=90, mass=100000, image=random.choice(star_images))}

    for index, instrument in enumerate(midi_data.instruments):
        solar_system_dict[index] = CelestialBody(name=index, instrument=instrument, song_duration=midi_data.get_end_time(
        ), x=WIDTH//2 - PlanetarySystem.MIN_RADIUS - (PLANET_SPACING)*(index+1), image=random.choice(planet_images))

    solar_system = PlanetarySystem(solar_system_dict)

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
        rotation_matrix = np.array([[np.cos(theta), -np.sin(theta), 0],
                                   [np.sin(theta), np.cos(theta), 0],
                                   [0, 0, 1]])
    return np.dot(matrix, rotation_matrix)


# create galaxy
# ______________________________
galaxy = create_galaxy(SMALL_GALAXY_RADIUS=SMALL_GALAXY_RADIUS,
                       LARGE_GALAXY_RADIUS=LARGE_GALAXY_RADIUS)
x, y = 0, 0
x_center_offset, y_center_offset = 0, 0

curr_star_name = random.choice(
    [x for x in os.listdir('music') if x != '.DS_Store'])

initialize_new_song()

galaxy_draw_pos = galaxy  # to scale the galaxy cluster
curr_star_pos = galaxy[curr_star_name]


pygame.mixer.music.load(mp3_file)
pygame.mixer.music.play(loops=0, start=MUSIC_START)


# _______rotation code_______
projection_matrix = np.array([[1, 0, 0],
                              [0, 1, 0],
                              [0, 0, 0]])
# keeps track of angles rotated along each axis
x_axis_angle = y_axis_angle = z_axis_angle = 0
# ____________________________

# time variables initialized later to allow for minimal sync issues
start_time = time.time() - MUSIC_START
# account for midi and mp3 drifting
last_check_for_drift = time.time() - MUSIC_START

running = True
while running:

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if view_mode == VIEW_OPTIONS[0]:  # view check
                if event.button == PYGAME_ZOOM_OUT:
                    if SOLAR_ZOOM_FACTOR-ZOOM_CHANGE > 0:
                        SOLAR_ZOOM_FACTOR -= ZOOM_CHANGE
                        MUSIC_VOLUME = SOLAR_ZOOM_FACTOR
                        pygame.mixer.music.set_volume(MUSIC_VOLUME)
                    else:
                        MUSIC_VOLUME = 0
                        pygame.mixer.music.set_volume(MUSIC_VOLUME)
                if event.button == PYGAME_ZOOM_IN:
                    SOLAR_ZOOM_FACTOR += ZOOM_CHANGE
                    if SOLAR_ZOOM_FACTOR > 1:
                        MUSIC_VOLUME = 1
                    else:
                        MUSIC_VOLUME = SOLAR_ZOOM_FACTOR
                    pygame.mixer.music.set_volume(MUSIC_VOLUME)
            elif view_mode == VIEW_OPTIONS[1]:
                curr_star_pos = galaxy[curr_star_name]
                x_center_offset = WIDTH//2-curr_star_pos[0]
                y_center_offset = HEIGHT//2-curr_star_pos[1]

                if event.button == PYGAME_LEFT_CLICK:
                    x, y = pygame.mouse.get_pos()

                    curr_star_name = find_nearest_star(x, y, galaxy_draw_pos)
                    initialize_new_song()

                if event.button == PYGAME_ZOOM_OUT and GALAXY_ZOOM_FACTOR-ZOOM_CHANGE > 0 and GALAXY_ZOOM_FACTOR*DEFAULT_SMALL_STAR_RADIUS >= MIN_STAR_RADIUS:
                    GALAXY_ZOOM_FACTOR -= ZOOM_CHANGE
                if event.button == PYGAME_ZOOM_IN:
                    GALAXY_ZOOM_FACTOR += ZOOM_CHANGE

        keys = pygame.key.get_pressed()

        if view_mode == VIEW_OPTIONS[0]:  # view check
            if keys[pygame.K_r]:
                SOLAR_ZOOM_FACTOR = 1
                x_axis_angle = y_axis_angle = z_axis_angle = 0

            if keys[pygame.K_EQUALS]:
                play_song(
                    duration=solar_system.bodies[1].song_duration, change=-MUSIC_SKIP_INCREMENT)

            elif keys[pygame.K_MINUS]:
                play_song(
                    duration=solar_system.bodies[1].song_duration, change=MUSIC_SKIP_INCREMENT)

        elif view_mode == VIEW_OPTIONS[1]:
            if keys[pygame.K_r]:
                GALAXY_ZOOM_FACTOR = 1
            if keys[pygame.K_f]:
                find_menu()

    if view_mode == VIEW_OPTIONS[0]:  # view check planetary
        two_dim_projection = [[planet.x-WIDTH//2, planet.y-HEIGHT//2, 0]
                              for planet in solar_system.bodies.values()]
        three_dim_points_copy = two_dim_projection.copy()

        # without using if statements
        y_axis_angle += ROTATION_ANGLE_CHANGE * \
            (-int(keys[pygame.K_LEFT]) + int(keys[pygame.K_RIGHT]))
        x_axis_angle += ROTATION_ANGLE_CHANGE * \
            (-int(keys[pygame.K_DOWN]) + int(keys[pygame.K_UP]))
        z_axis_angle += ROTATION_ANGLE_CHANGE * \
            (-int(keys[pygame.K_q]) + int(keys[pygame.K_w]))

        three_dim_points_copy = rotate_axis(
            three_dim_points_copy, 'x', x_axis_angle)
        three_dim_points_copy = rotate_axis(
            three_dim_points_copy, 'y', y_axis_angle)
        three_dim_points_copy = rotate_axis(
            three_dim_points_copy, 'z', z_axis_angle)
        two_dim_projection = np.dot(three_dim_points_copy, projection_matrix)

    if view_mode == VIEW_OPTIONS[0]:  # view check
        WIN.blit(background_surf, (0, 0))
        # pygame.surfarray.blit_array(WIN, background_orbit_paths_array)
        if solar_system.star.radius*SOLAR_ZOOM_FACTOR <= MIN_SOLAR_RADIUS:
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

        if time.time() - last_check_for_drift > DRIFT_CHECK_DELAY:  # check for drift every couple seconds
            play_song(solar_system.bodies[1].song_duration)

    elif view_mode == VIEW_OPTIONS[1]:
        WIN.blit(background_surf, (0, 0))
        galaxy_draw_pos = {}
        for key, value in galaxy.items():
            draw_x = curr_star_pos[0]-GALAXY_ZOOM_FACTOR * \
                (curr_star_pos[0]-value[0]) + x_center_offset
            draw_y = curr_star_pos[1]-GALAXY_ZOOM_FACTOR * \
                (curr_star_pos[1]-value[1]) + y_center_offset

            galaxy_draw_pos[key] = [draw_x, draw_y]

            if DEFAULT_SMALL_STAR_RADIUS*GALAXY_ZOOM_FACTOR >= MIN_STAR_RADIUS:
                # new_radius = DEFAULT_RADIUS*ZOOM_FACTOR
                new_radius = MIN_STAR_RADIUS
            else:
                new_radius = MIN_STAR_RADIUS

            if key == curr_star_name:
                pygame.draw.circle(WIN, RED, (draw_x, draw_y), new_radius)
            else:
                pygame.draw.circle(WIN, WHITE, (draw_x, draw_y), new_radius)
        if GALAXY_ZOOM_FACTOR >= GALAXY_ZOOM_THRESHOLD:
            pygame.mixer.music.load(mp3_file)
            play_song(solar_system.bodies[1].song_duration)
            view_mode = VIEW_OPTIONS[0]
            # GALAXY_ZOOM_FACTOR = GALAXY_ZOOM_THRESHOLD

    write_text(f'T={str(datetime.timedelta(seconds=time.time()-start_time))}',
               (0, 0))  # update screen counter
    write_text(f'{curr_star_name}', (0, FONT_SIZE), GREY)

    pygame.display.flip()
pygame.quit()
