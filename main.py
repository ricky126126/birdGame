import os
import asyncio
import pygame
import random
from pygame.locals import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def asset_path(*parts):
    return os.path.join(BASE_DIR, *parts)


# VARIABLES
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

SPEED = 20
GRAVITY = 2.5
GAME_SPEED = 15

GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100

PIPE_WIDTH = 80
PIPE_HEIGHT = 500

PIPE_GAP = 150


# AUDIO
wing = asset_path("assets", "audio", "wing.wav")
hit = asset_path("assets", "audio", "hit.wav")


pygame.init()

# Mixer
try:
    pygame.mixer.init()
except pygame.error:
    pass


class Bird(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        self.images = [
            pygame.image.load(
                asset_path("assets", "sprites", "bluebird-upflap.png")
            ).convert_alpha(),

            pygame.image.load(
                asset_path("assets", "sprites", "bluebird-midflap.png")
            ).convert_alpha(),

            pygame.image.load(
                asset_path("assets", "sprites", "bluebird-downflap.png")
            ).convert_alpha()
        ]

        self.speed = SPEED

        self.current_image = 0

        self.image = self.images[0]

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()

        self.rect[0] = SCREEN_WIDTH / 6
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):

        self.current_image = (self.current_image + 1) % 3

        self.image = self.images[self.current_image]

        self.speed += GRAVITY

        self.rect[1] += self.speed

    def bump(self):

        self.speed = -SPEED

    def begin(self):

        self.current_image = (self.current_image + 1) % 3

        self.image = self.images[self.current_image]


class Pipe(pygame.sprite.Sprite):

    def __init__(self, inverted, xpos, ysize):

        super().__init__()

        self.image = pygame.image.load(
            asset_path("assets", "sprites", "pipe-green.png")
        ).convert_alpha()

        self.image = pygame.transform.scale(
            self.image,
            (PIPE_WIDTH, PIPE_HEIGHT)
        )

        self.rect = self.image.get_rect()

        self.rect[0] = xpos

        if inverted:

            self.image = pygame.transform.flip(
                self.image,
                False,
                True
            )

            self.rect[1] = -(self.rect[3] - ysize)

        else:

            self.rect[1] = SCREEN_HEIGHT - ysize

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):

        self.rect[0] -= GAME_SPEED


class Ground(pygame.sprite.Sprite):

    def __init__(self, xpos):

        super().__init__()

        self.image = pygame.image.load(
            asset_path("assets", "sprites", "base.png")
        ).convert_alpha()

        self.image = pygame.transform.scale(
            self.image,
            (GROUND_WIDTH, GROUND_HEIGHT)
        )

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()

        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):

        self.rect[0] -= GAME_SPEED


def is_off_screen(sprite):

    return sprite.rect[0] < -(sprite.rect[2])


def get_random_pipes(xpos):

    size = random.randint(100, 300)

    pipe = Pipe(
        False,
        xpos,
        size
    )

    pipe_inverted = Pipe(
        True,
        xpos,
        SCREEN_HEIGHT - size - PIPE_GAP
    )

    return pipe, pipe_inverted


# SCREEN
screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption("Flappy Bird")


# BACKGROUND
BACKGROUND = pygame.image.load(
    asset_path(
        "assets",
        "sprites",
        "background-day.png"
    )
)

BACKGROUND = pygame.transform.scale(
    BACKGROUND,
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)


# START MESSAGE
BEGIN_IMAGE = pygame.image.load(
    asset_path(
        "assets",
        "sprites",
        "message.png"
    )
).convert_alpha()


# BIRD GROUP
bird_group = pygame.sprite.Group()

bird = Bird()

bird_group.add(bird)


# GROUND GROUP
ground_group = pygame.sprite.Group()

for i in range(2):

    ground = Ground(
        GROUND_WIDTH * i
    )

    ground_group.add(ground)


# PIPE GROUP
pipe_group = pygame.sprite.Group()

for i in range(2):

    pipes = get_random_pipes(
        SCREEN_WIDTH * i + 800
    )

    pipe_group.add(pipes[0])
    pipe_group.add(pipes[1])


clock = pygame.time.Clock()


async def play_sound(sound_file):

    try:

        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()

    except pygame.error:

        pass


async def main():

    # -------------------------
    # START SCREEN
    # -------------------------

    begin = True

    while begin:

        clock.tick(15)

        for event in pygame.event.get():

            if event.type == QUIT:

                pygame.quit()
                return

            if event.type == KEYDOWN:

                if event.key == K_SPACE or event.key == K_UP:

                    bird.bump()

                    await play_sound(wing)

                    begin = False

        screen.blit(
            BACKGROUND,
            (0, 0)
        )

        screen.blit(
            BEGIN_IMAGE,
            (120, 150)
        )

        if is_off_screen(
            ground_group.sprites()[0]
        ):

            ground_group.remove(
                ground_group.sprites()[0]
            )

            new_ground = Ground(
                GROUND_WIDTH - 20
            )

            ground_group.add(
                new_ground
            )

        bird.begin()

        ground_group.update()

        bird_group.draw(screen)

        ground_group.draw(screen)

        pygame.display.update()

        # IMPORTANT FOR PYGBAG
        await asyncio.sleep(0)


    # -------------------------
    # MAIN GAME
    # -------------------------

    running = True

    while running:

        clock.tick(15)

        for event in pygame.event.get():

            if event.type == QUIT:

                running = False

            if event.type == KEYDOWN:

                if event.key == K_SPACE or event.key == K_UP:

                    bird.bump()

                    await play_sound(wing)


        screen.blit(
            BACKGROUND,
            (0, 0)
        )


        # Ground movement
        if is_off_screen(
            ground_group.sprites()[0]
        ):

            ground_group.remove(
                ground_group.sprites()[0]
            )

            new_ground = Ground(
                GROUND_WIDTH - 20
            )

            ground_group.add(
                new_ground
            )


        # Pipe movement
        if is_off_screen(
            pipe_group.sprites()[0]
        ):

            pipe_group.remove(
                pipe_group.sprites()[0]
            )

            pipe_group.remove(
                pipe_group.sprites()[0]
            )

            pipes = get_random_pipes(
                SCREEN_WIDTH * 2
            )

            pipe_group.add(pipes[0])
            pipe_group.add(pipes[1])


        # UPDATE
        bird_group.update()

        ground_group.update()

        pipe_group.update()


        # DRAW
        bird_group.draw(screen)

        pipe_group.draw(screen)

        ground_group.draw(screen)


        pygame.display.update()


        # COLLISION
        collision = (

            pygame.sprite.groupcollide(
                bird_group,
                ground_group,
                False,
                False,
                pygame.sprite.collide_mask
            )

            or

            pygame.sprite.groupcollide(
                bird_group,
                pipe_group,
                False,
                False,
                pygame.sprite.collide_mask
            )
        )


        if collision:

            await play_sound(hit)

            # Instead of time.sleep()
            await asyncio.sleep(1)

            running = False


        # VERY IMPORTANT
        # Gives control back to browser
        await asyncio.sleep(0)


    pygame.quit()


# START GAME
asyncio.run(main())