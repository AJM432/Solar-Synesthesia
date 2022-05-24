import pygame
import random
from pygame import Vector2

pygame.init()
WIDTH = HEIGHT = 800
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Star Distribution")
clock = pygame.time.Clock()

# star_distribution

STAR_COUNT = 100
ZOOM_FACTOR = 1
PYGAME_RIGHT_CLICK = 1
PYGAME_LEFT_CLICK = 2
PYGAME_ZOOM_OUT = 4
PYGAME_ZOOM_IN = 5
ZOOM_CHANGE = 0.05
MIN_STAR_RADIUS=2
DEFAULT_RADIUS = 10
SMALL_GALAXY_RADIUS = 500
LARGE_GALAXY_RADIUS = 1500


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


x, y = 0, 0
x_center_offset, y_center_offset = 0, 0

curr_star_index=0
curr_star=galaxy[curr_star_index]
galaxy_draw_pos = galaxy

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


        if event.type == pygame.MOUSEBUTTONDOWN:
            curr_star = galaxy[curr_star_index]
            x_center_offset = WIDTH//2-curr_star[0]
            y_center_offset = HEIGHT//2-curr_star[1]

            if event.button == PYGAME_RIGHT_CLICK:
                x, y = pygame.mouse.get_pos()
                curr_star_index = find_nearest_star(x, y, galaxy_draw_pos)
                

            if event.button == PYGAME_ZOOM_OUT and ZOOM_FACTOR-ZOOM_CHANGE > 0 and ZOOM_FACTOR*DEFAULT_RADIUS >= MIN_STAR_RADIUS:
                ZOOM_FACTOR -= ZOOM_CHANGE
            if event.button == PYGAME_ZOOM_IN:
                ZOOM_FACTOR += ZOOM_CHANGE

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            ZOOM_FACTOR = 1


    WIN.fill(BLACK)
    galaxy_draw_pos = []
    for index, star in enumerate(galaxy):
        draw_x = curr_star[0]-ZOOM_FACTOR*(curr_star[0]-star[0]) + x_center_offset
        draw_y = curr_star[1]-ZOOM_FACTOR*(curr_star[1]-star[1]) + y_center_offset

        galaxy_draw_pos.append([draw_x, draw_y])

        if DEFAULT_RADIUS*ZOOM_FACTOR >= MIN_STAR_RADIUS:
            new_radius = DEFAULT_RADIUS*ZOOM_FACTOR
        else:
            new_radius = MIN_STAR_RADIUS

            
        if index == curr_star_index:
            pygame.draw.circle(WIN, RED, (draw_x, draw_y), new_radius)
        else:
            pygame.draw.circle(WIN, WHITE, (draw_x, draw_y), new_radius)

    pygame.display.flip()
pygame.quit()
