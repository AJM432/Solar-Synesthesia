import pygame
import numpy as np
import math

 #______________________________
 # must not have overlapping systems
#  star must be defined as first element in dict
# objects are stored as key, value pairs where key=name, value=instance of object class
#______________________________

pygame.init()

# constants
# ______________________________
# WIDTH = HEIGHT = 800
WIDTH, HEIGHT = 1400, 800
FPS = 60 # never change FPS, used in velocity calculation as delta-t
ZOOM_FACTOR = 1

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 190, 0)
ORANGE = (255, 215, 0)
GREY = (125, 125, 125)
PALE_YELLOW = (240, 240, 0)
PINK = (255,192,203)
BACKGROUND_COLOR = GREY

G_CUSTOM = 0.0157 # experimentally calculated gravitational constant
# ______________________________

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Simulation")
clock = pygame.time.Clock()

# array to keep track of path of celestial bodies
# TODO: change to local orbital path tracking rather than using a global variable since its impossible to have a large array to hold all system info
background_orbit_paths_array = np.zeros((WIDTH, HEIGHT, 3), dtype=np.uint8)
background_orbit_paths_array[0:, 0:, 0:] = BACKGROUND_COLOR

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
    def __init__(self, name, x, y, color, radius, is_planet=True, vx=0, vy=0, mass=0):
        self.mass = mass
        self.name = name
        self.vx = vx
        self.x = x
        self.y = y
        self.vy = vy
        self.color = color
        self.radius = radius
        self.is_planet = is_planet

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
            background_orbit_paths_array[int(self.x), int(self.y), 0:3] = self.color

    def draw(self):
        pygame.draw.circle(WIN, self.color, (self.x, self.y), self.radius)


    # combines all methods required to draw object to screen and interact with other objects
    def next_frame(self, planetary_system): # pass entire solar system
        planetary_system_copy = planetary_system.copy() # used to exclude current body without changing global 
        del planetary_system_copy[self.name]

        if self.is_planet: # sun is not influenced by planets
            for body in planetary_system_copy.values():
                self.update_orbit_velocity(body)
            self.update_position()
        self.draw()


solar_system_dict = {
    'sun': CelestialBody(name='sun', mass=1000000, x=WIDTH//2, y=HEIGHT//2, color=PALE_YELLOW, radius=25, is_planet=False),
    'mercury' : CelestialBody(name='mercury', x=WIDTH//2-50, y=HEIGHT//2, color=WHITE, radius=3),
    'venus' : CelestialBody(name='venus', x=WIDTH//2-100, y=HEIGHT//2, color=PINK, radius=3),
    'earth' : CelestialBody(name='earth', x=WIDTH//2-150, y=HEIGHT//2, color=BLUE, radius=7),
    'mars' : CelestialBody(name='mars', x=WIDTH//2-200, y=HEIGHT//2, color=RED, radius=5),
    'jupiter' : CelestialBody(name='jupiter', x=WIDTH//2-300, y=HEIGHT//2, color=RED, radius=15),
    'saturn' : CelestialBody(name='saturn', x=WIDTH//2-400, y=HEIGHT//2, color=GREEN, radius=13),
    'uranus' : CelestialBody(name='uranus', x=WIDTH//2-500, y=HEIGHT//2, color=BLUE, radius=11),
    'neptune' : CelestialBody(name='neptune', x=WIDTH//2-600, y=HEIGHT//2, color=BLUE, radius=11)
}

solar_system = PlanetarySystem(solar_system_dict)

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    WIN.fill(BACKGROUND_COLOR)
    pygame.surfarray.blit_array(WIN, background_orbit_paths_array)

    solar_system.next_frame()

    pygame.display.flip()
pygame.quit()
