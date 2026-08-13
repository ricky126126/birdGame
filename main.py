import os
import asyncio
import random
import pygame

from pygame.locals import (
    QUIT,
    KEYDOWN,
    K_SPACE,
    K_UP,
    MOUSEBUTTONDOWN
)


# =========================================================
# PATH
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def asset_path(*parts):
    return os.path.join(BASE_DIR, *parts)


# =========================================================
# GAME SETTINGS
# =========================================================

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

FPS = 60

# Bird physics
BIRD_SPEED = 8
GRAVITY = 0.5

# Pipe / ground speed
GAME_SPEED = 4

GROUND_WIDTH = SCREEN_WIDTH * 2
GROUND_HEIGHT = 100

PIPE_WIDTH = 80
PIPE_HEIGHT = 500

PIPE_GAP = 150


# =========================================================
# PYGAME INITIALIZATION
# =========================================================

pygame.init()

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption("Flappy Bird")

clock = pygame.time.Clock()


# =========================================================
# AUDIO
# =========================================================

audio_available = False

try:
    pygame.mixer.init()
    audio_available = True
except pygame.error:
    audio_available = False


wing_sound = None
hit_sound = None


if audio_available:

    try:

        wing_sound = pygame.mixer.Sound(
            asset_path(
                "assets",
                "audio",
                "wing.ogg"
            )
        )

        hit_sound = pygame.mixer.Sound(
            asset_path(
                "assets",
                "audio",
                "hit.ogg"
            )
        )

    except pygame.error:

        wing_sound = None
        hit_sound = None


# =========================================================
# LOAD BACKGROUND
# =========================================================

BACKGROUND = pygame.image.load(
    asset_path(
        "assets",
        "sprites",
        "background-day.png"
    )
).convert()

BACKGROUND = pygame.transform.scale(
    BACKGROUND,
    (
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )
)


# =========================================================
# LOAD START IMAGE
# =========================================================

BEGIN_IMAGE = pygame.image.load(
    asset_path(
        "assets",
        "sprites",
        "message.png"
    )
).convert_alpha()


# =========================================================
# LOAD GAME OVER IMAGE
# =========================================================

GAMEOVER_IMAGE = pygame.image.load(
    asset_path(
        "assets",
        "sprites",
        "gameover.png"
    )
).convert_alpha()


# =========================================================
# BIRD CLASS
# =========================================================

class Bird(pygame.sprite.Sprite):

    def __init__(self):

        super().__init__()

        self.images = [

            pygame.image.load(
                asset_path(
                    "assets",
                    "sprites",
                    "bluebird-upflap.png"
                )
            ).convert_alpha(),

            pygame.image.load(
                asset_path(
                    "assets",
                    "sprites",
                    "bluebird-midflap.png"
                )
            ).convert_alpha(),

            pygame.image.load(
                asset_path(
                    "assets",
                    "sprites",
                    "bluebird-downflap.png"
                )
            ).convert_alpha()
        ]

        self.current_image = 0

        self.image = self.images[
            self.current_image
        ]

        self.rect = self.image.get_rect()

        self.rect.x = SCREEN_WIDTH // 6

        self.rect.y = SCREEN_HEIGHT // 2

        self.speed = 0

        self.mask = pygame.mask.from_surface(
            self.image
        )


    # -----------------------------------------------------
    # UPDATE BIRD
    # -----------------------------------------------------

    def update(self):

        # Bird animation

        self.current_image = (
            self.current_image + 1
        ) % len(self.images)

        self.image = self.images[
            self.current_image
        ]

        # Gravity

        self.speed += GRAVITY

        self.rect.y += self.speed

        # Update mask

        self.mask = pygame.mask.from_surface(
            self.image
        )


    # -----------------------------------------------------
    # FLAP
    # -----------------------------------------------------

    def flap(self):

        self.speed = -BIRD_SPEED

        if wing_sound:

            wing_sound.play()


    # -----------------------------------------------------
    # START SCREEN ANIMATION
    # -----------------------------------------------------

    def animate_start(self):

        self.current_image = (
            self.current_image + 1
        ) % len(self.images)

        self.image = self.images[
            self.current_image
        ]

        self.mask = pygame.mask.from_surface(
            self.image
        )


    # -----------------------------------------------------
    # RESET
    # -----------------------------------------------------

    def reset(self):

        self.rect.x = SCREEN_WIDTH // 6

        self.rect.y = SCREEN_HEIGHT // 2

        self.speed = 0

        self.current_image = 0

        self.image = self.images[0]

        self.mask = pygame.mask.from_surface(
            self.image
        )


# =========================================================
# PIPE CLASS
# =========================================================

class Pipe(pygame.sprite.Sprite):

    def __init__(
        self,
        inverted,
        xpos,
        ysize
    ):

        super().__init__()

        self.image = pygame.image.load(
            asset_path(
                "assets",
                "sprites",
                "pipe-green.png"
            )
        ).convert_alpha()

        self.image = pygame.transform.scale(
            self.image,
            (
                PIPE_WIDTH,
                PIPE_HEIGHT
            )
        )

        self.rect = self.image.get_rect()

        self.rect.x = xpos


        # -------------------------------------------------
        # TOP PIPE
        # -------------------------------------------------

        if inverted:

            self.image = pygame.transform.flip(
                self.image,
                False,
                True
            )

            self.rect.y = -(
                self.rect.height - ysize
            )


        # -------------------------------------------------
        # BOTTOM PIPE
        # -------------------------------------------------

        else:

            self.rect.y = (
                SCREEN_HEIGHT - ysize
            )


        self.mask = pygame.mask.from_surface(
            self.image
        )


    # -----------------------------------------------------
    # UPDATE PIPE
    # -----------------------------------------------------

    def update(self):

        self.rect.x -= GAME_SPEED


# =========================================================
# GROUND CLASS
# =========================================================

class Ground(pygame.sprite.Sprite):

    def __init__(self, xpos):

        super().__init__()

        self.image = pygame.image.load(
            asset_path(
                "assets",
                "sprites",
                "base.png"
            )
        ).convert_alpha()

        self.image = pygame.transform.scale(
            self.image,
            (
                GROUND_WIDTH,
                GROUND_HEIGHT
            )
        )

        self.rect = self.image.get_rect()

        self.rect.x = xpos

        self.rect.y = (
            SCREEN_HEIGHT - GROUND_HEIGHT
        )

        self.mask = pygame.mask.from_surface(
            self.image
        )


    # -----------------------------------------------------
    # UPDATE GROUND
    # -----------------------------------------------------

    def update(self):

        self.rect.x -= GAME_SPEED


# =========================================================
# RANDOM PIPE GENERATOR
# =========================================================

def get_random_pipes(xpos):

    size = random.randint(
        100,
        300
    )

    bottom_pipe = Pipe(
        False,
        xpos,
        size
    )

    top_pipe = Pipe(
        True,
        xpos,
        SCREEN_HEIGHT
        - size
        - PIPE_GAP
    )

    return (
        bottom_pipe,
        top_pipe
    )


# =========================================================
# OFF SCREEN CHECK
# =========================================================

def is_off_screen(sprite):

    return (
        sprite.rect.right < 0
    )


# =========================================================
# SPRITE GROUPS
# =========================================================

bird_group = pygame.sprite.Group()

bird = Bird()

bird_group.add(bird)


ground_group = pygame.sprite.Group()

ground_group.add(
    Ground(0),
    Ground(GROUND_WIDTH)
)


pipe_group = pygame.sprite.Group()

pipes1 = get_random_pipes(
    SCREEN_WIDTH + 200
)

pipes2 = get_random_pipes(
    SCREEN_WIDTH + 600
)

pipe_group.add(
    pipes1[0],
    pipes1[1],
    pipes2[0],
    pipes2[1]
)


# =========================================================
# RESET GAME
# =========================================================

def reset_game():

    # Reset bird

    bird.reset()


    # Reset pipes

    pipe_group.empty()

    pipes1 = get_random_pipes(
        SCREEN_WIDTH + 200
    )

    pipes2 = get_random_pipes(
        SCREEN_WIDTH + 600
    )

    pipe_group.add(
        pipes1[0],
        pipes1[1],
        pipes2[0],
        pipes2[1]
    )


    # Reset ground

    ground_group.empty()

    ground_group.add(
        Ground(0),
        Ground(GROUND_WIDTH)
    )


# =========================================================
# DRAW START SCREEN
# =========================================================

def draw_start_screen():

    screen.blit(
        BACKGROUND,
        (0, 0)
    )


    screen.blit(
        BEGIN_IMAGE,
        (
            (SCREEN_WIDTH - BEGIN_IMAGE.get_width()) // 2,
            150
        )
    )


    bird_group.draw(screen)

    ground_group.draw(screen)

    pygame.display.flip()


# =========================================================
# DRAW GAME OVER
# =========================================================

def draw_game_over():

    screen.blit(
        BACKGROUND,
        (0, 0)
    )


    pipe_group.draw(screen)

    bird_group.draw(screen)

    ground_group.draw(screen)


    screen.blit(
        GAMEOVER_IMAGE,
        (
            (SCREEN_WIDTH - GAMEOVER_IMAGE.get_width()) // 2,
            200
        )
    )


    pygame.display.flip()


# =========================================================
# START SCREEN
# =========================================================

async def start_screen():

    while True:

        # -------------------------------------------------
        # EVENTS
        # -------------------------------------------------

        for event in pygame.event.get():

            # Close window

            if event.type == QUIT:

                return False


            # Keyboard

            if event.type == KEYDOWN:

                if (
                    event.key == K_SPACE
                    or event.key == K_UP
                ):

                    bird.flap()

                    return True


            # Mouse / Touch

            if event.type == MOUSEBUTTONDOWN:

                bird.flap()

                return True


        # -------------------------------------------------
        # BIRD ANIMATION
        # -------------------------------------------------

        bird.animate_start()


        # -------------------------------------------------
        # GROUND MOVEMENT
        # -------------------------------------------------

        ground_group.update()


        grounds = ground_group.sprites()


        if len(grounds) > 0:

            if is_off_screen(
                grounds[0]
            ):

                ground_group.remove(
                    grounds[0]
                )

                ground_group.add(
                    Ground(
                        GROUND_WIDTH - 20
                    )
                )


        # -------------------------------------------------
        # DRAW
        # -------------------------------------------------

        draw_start_screen()


        # -------------------------------------------------
        # GIVE CONTROL TO BROWSER
        # -------------------------------------------------

        await asyncio.sleep(
            1 / FPS
        )


# =========================================================
# MAIN GAME LOOP
# =========================================================

async def game_loop():

    running = True


    while running:

        # -------------------------------------------------
        # EVENTS
        # -------------------------------------------------

        for event in pygame.event.get():

            # Close

            if event.type == QUIT:

                return False


            # Keyboard

            if event.type == KEYDOWN:

                if (
                    event.key == K_SPACE
                    or event.key == K_UP
                ):

                    bird.flap()


            # Mouse / Touch

            if event.type == MOUSEBUTTONDOWN:

                bird.flap()


        # -------------------------------------------------
        # UPDATE BIRD
        # -------------------------------------------------

        bird_group.update()


        # -------------------------------------------------
        # UPDATE GROUND
        # -------------------------------------------------

        ground_group.update()


        # -------------------------------------------------
        # UPDATE PIPES
        # -------------------------------------------------

        pipe_group.update()


        # -------------------------------------------------
        # INFINITE GROUND
        # -------------------------------------------------

        grounds = ground_group.sprites()


        if len(grounds) > 0:

            if is_off_screen(
                grounds[0]
            ):

                ground_group.remove(
                    grounds[0]
                )

                ground_group.add(
                    Ground(
                        GROUND_WIDTH - 20
                    )
                )


        # -------------------------------------------------
        # INFINITE PIPES
        # -------------------------------------------------

        pipes = pipe_group.sprites()


        if len(pipes) >= 2:

            if is_off_screen(
                pipes[0]
            ):

                pipe_group.remove(
                    pipes[0]
                )

                pipe_group.remove(
                    pipes[0]
                )

                new_pipes = get_random_pipes(
                    SCREEN_WIDTH * 2
                )

                pipe_group.add(
                    new_pipes[0],
                    new_pipes[1]
                )


        # -------------------------------------------------
        # COLLISION
        # -------------------------------------------------

        ground_collision = pygame.sprite.groupcollide(
            bird_group,
            ground_group,
            False,
            False,
            pygame.sprite.collide_mask
        )


        pipe_collision = pygame.sprite.groupcollide(
            bird_group,
            pipe_group,
            False,
            False,
            pygame.sprite.collide_mask
        )


        # Bird hits top

        top_collision = (
            bird.rect.top <= 0
        )


        # Bird hits bottom

        bottom_collision = (
            bird.rect.bottom >= SCREEN_HEIGHT
        )


        # -------------------------------------------------
        # GAME OVER
        # -------------------------------------------------

        if (
            ground_collision
            or pipe_collision
            or top_collision
            or bottom_collision
        ):

            if hit_sound:

                hit_sound.play()


            # Wait without blocking browser

            await asyncio.sleep(1)

            return True


        # -------------------------------------------------
        # DRAW
        # -------------------------------------------------

        screen.blit(
            BACKGROUND,
            (0, 0)
        )


        pipe_group.draw(screen)

        ground_group.draw(screen)

        bird_group.draw(screen)


        pygame.display.flip()


        # -------------------------------------------------
        # IMPORTANT FOR PYGBAG
        # -------------------------------------------------

        await asyncio.sleep(
            1 / FPS
        )


# =========================================================
# GAME OVER SCREEN
# =========================================================

async def game_over_screen():

    while True:

        # -------------------------------------------------
        # EVENTS
        # -------------------------------------------------

        for event in pygame.event.get():

            # Close

            if event.type == QUIT:

                return False


            # Keyboard

            if event.type == KEYDOWN:

                if (
                    event.key == K_SPACE
                    or event.key == K_UP
                ):

                    return True


            # Mouse / Touch

            if event.type == MOUSEBUTTONDOWN:

                return True


        # -------------------------------------------------
        # DRAW
        # -------------------------------------------------

        draw_game_over()


        # -------------------------------------------------
        # GIVE CONTROL TO BROWSER
        # -------------------------------------------------

        await asyncio.sleep(
            1 / FPS
        )


# =========================================================
# MAIN GAME
# =========================================================

async def main():

    while True:

        # Reset

        reset_game()


        # -------------------------------------------------
        # START SCREEN
        # -------------------------------------------------

        start = await start_screen()


        if not start:

            break


        # -------------------------------------------------
        # GAME
        # -------------------------------------------------

        game_finished = await game_loop()


        if not game_finished:

            break


        # -------------------------------------------------
        # GAME OVER
        # -------------------------------------------------

        restart = await game_over_screen()


        if not restart:

            break


    pygame.quit()


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    asyncio.run(main())