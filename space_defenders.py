import random
import os.path
import pygame
from pygame.locals import *

if not pygame.image.get_extended():
    raise SystemExit(
        "Need Extended Image Module. See https://www.pygame.org/docs/ref/image.html for more information")

SHOTS = 4
ALIENS_CHANCE = 22
BOMBS_CHANCE = 40
ALIEN_RESPAWN = 12
SCREENRECT = Rect(0, 0, 1280, 720)
SCORE = 0
BIG_KILLED = 0
MED_KILLED = 0
SML_KILLED = 0

# create variable for the directory that the game will run inside
main_dir = os.path.split(os.path.abspath(__file__))[0]


# loads a image if given a file name
def load_img(file):
    #
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit("Illegal file argument. Check load_img() call")
    return surface.convert()


# loads a series of images and returns an array with the images
def load_imgs(*files):
    imgs = []
    for file in files:
        imgs.append(load_img(file))
    return imgs


# class for playing sounds
class sound:
    # call the default play method
    def play(self): pass


# loads sounds into the game given file name
def load_snd(file):
    if not pygame.mixer:
        return sound()
    file = os.path.join(main_dir, 'data', file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print('Unable to load file %s' % file)
    return sound()


# This is the class for the spaceship that the user is allowed to control.
class Spaceship(pygame.sprite.Sprite):
    speed = 10
    bounce = 24
    gun_offset = 1
    images = []

    # initialize the spaceship with no images, starting at the bottom middle, with no reloading and facing the left side
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1

    # when send a direction, move the spaceship in that given direction.
    def move(self, direction):
        if direction:
            self.facing = direction
        self.rect.move_ip(direction*self.speed, 0)
        self.rect = self.rect.clamp(SCREENRECT)
        if direction < 0:
            self.image = self.images[0]
        elif direction > 0:
            self.image = self.images[1]
        self.rect.top = self.origtop - (self.rect.left // self.bounce % 2)

    # this sets the position of the gun since the gun is not in the center of the sprite
    def gunpos(self):
        pos = self.facing * self.gun_offset + self.rect.centerx
        return pos, self.rect.top


# there are three different types of aliens. The bigger the alien, the slower it is, but the more points it will give

# class for the big aliens. killing a big alien will give more points than the others.
class Big_Alien(pygame.sprite.Sprite):
    speed = 4
    animcycle = 12
    images = []

    # this will initialize the alien with the image of the sprite and a random side for it to appear
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.facing = random.choice((-1, 1)) * Big_Alien.speed
        self.frame = 0
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    # this updates the sprite with the speed and switching sides when reaching the ends
    def update(self):
        self.rect.move_ip(self.facing, 0)
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)
        self.frame = self.frame + 1
        self.image = self.images[self.frame//self.animcycle % 3]


# class for the medium alien. this will give more points than the small alien.
class Med_Alien(pygame.sprite.Sprite):
    speed = 8
    animcycle = 12
    images = []

    # this will initialize the alien with the image of the sprite and a random side for it to appear
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.facing = random.choice((-1, 1)) * Med_Alien.speed
        self.frame = 0
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    # this updates the sprite with the speed and switching sides when reaching the ends
    def update(self):
        self.rect.move_ip(self.facing, 0)
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)
        self.frame = self.frame + 1
        self.image = self.images[self.frame // self.animcycle % 3]


# class for the small alien. this will give the least amount of points.
class Sml_Alien(pygame.sprite.Sprite):
    speed = 12
    animcycle = 12
    images = []

    # this will initialize the alien with the image of the sprite and a random side for it to appear
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.facing = random.choice((-1, 1)) * Sml_Alien.speed
        self.frame = 0
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    # this updates the sprite with the speed and switching sides when reaching the ends
    def update(self):
        self.rect.move_ip(self.facing, 0)
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)
        self.frame = self.frame + 1
        self.image = self.images[self.frame//self.animcycle % 3]


# this class handles the explosion sprite that appears whenever a alien or a bomb is destroyed.
class Explosion(pygame.sprite.Sprite):
    defaultlife = 12
    animcycle = 3
    images = []

    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self):
        self.life = self.life - 1
        self.image = self.images[self.life // self.animcycle % 2]
        if self.life <= 0:
            self.kill()


# this class handles the bullet animation and properties for the gun
class Shot(pygame.sprite.Sprite):
    speed = -11
    images = []

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top < - 0:
            self.kill()


# this class handles the bomb class for the bombs that drop onto the player
class Bomb(pygame.sprite.Sprite):
    speed = 5
    images = []

    def __init__(self, alien):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(
            midbottom=alien.rect.move(0, 5).midbottom)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.bottom >= 710:
            Explosion(self)
            self.kill()


# this handles the score for the game
class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 20)
        self.font.set_bold(1)
        self.color = Color('white')
        self.lastscore = -1
        self.update()
        self.rect = self.image.get_rect().move(10, 700)

    def update(self):
        if SCORE != self.lastscore:
            self.lastscore = SCORE
            msg = "Score: %d" % SCORE
            self.image = self.font.render(msg, 0, self.color)


def main(winstyle=0):
    # Initialize pygame
    pygame.init()
    print("All images and sounds are used in fair use and for personal, non commerical use. Shoutout to pygames for the free framework.")
    if pygame.mixer and not pygame.mixer.get_init():
        print('Warning, no sound')
        pygame.mixer = None

    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # Load images, assign to sprite classes
    # (do this before the classes are used, after screen setup)
    img = load_img('player.gif')
    Spaceship.images = [img, img]
    img = load_img('explosion1.gif')
    Explosion.images = [img, pygame.transform.flip(img, 1, 1)]
    Sml_Alien.images = load_imgs(
        'small_white.png', 'small_white.png', 'small_white.png')
    Med_Alien.images = load_imgs(
        'big_pink.gif', 'big_pink.gif', 'big_pink.gif')
    Big_Alien.images = load_imgs(
        'big.gif', 'big.gif', 'big.gif')
    Bomb.images = [load_img('bombs.gif')]
    Shot.images = [load_img('bullet.gif')]

    # decorate the game window
    icon = pygame.transform.scale(Sml_Alien.images[0], (32, 32))
    pygame.display.set_icon(icon)
    pygame.display.set_caption('SPACE DEFENDERS')
    pygame.mouse.set_visible(0)

    # create the background, tile the bgd image
    background = pygame.Surface(SCREENRECT.size)

    # load the sound effects
    boom_sound = load_snd('boom.wav')
    shoot_sound = load_snd('car_door.wav')
    if pygame.mixer:
        music = os.path.join(main_dir, 'data', 'house_lo.wav')
        pygame.mixer.music.load(music)
        # pygame.mixer.music.play(-1)

    # Initialize Game Groups
    aliens = pygame.sprite.Group()
    med_aliens = pygame.sprite.Group()
    big_aliens = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()
    lastalien = pygame.sprite.GroupSingle()

    # assign default groups to each sprite class
    Spaceship.containers = all
    Sml_Alien.containers = aliens, all, lastalien
    Big_Alien.containers = aliens, big_aliens, all
    Med_Alien.containers = aliens, med_aliens, all
    Shot.containers = shots, all
    Bomb.containers = bombs, all
    Explosion.containers = all
    Score.containers = all

    # Create Some Starting Values
    global score
    alienreload = ALIEN_RESPAWN
    kills = 0
    clock = pygame.time.Clock()

    # initialize our starting sprites
    global SCORE
    player = Spaceship()
    Sml_Alien()  # note, this 'lives' because it goes into a sprite group
    Med_Alien()
    Big_Alien()
    if pygame.font:
        all.add(Score())

    while player.alive():

        # get input
        for event in pygame.event.get():
            if event.type == QUIT or \
                    (event.type == KEYDOWN and event.key == K_ESCAPE):
                print("Game quit by user")
                return
        keystate = pygame.key.get_pressed()

        # clear/erase the last drawn sprites
        all.clear(screen, background)

        # update all the sprites
        all.update()

        # handle player input
        direction = keystate[K_RIGHT] - keystate[K_LEFT]
        player.move(direction)
        firing = keystate[K_SPACE]
        if not player.reloading and firing and len(shots) < SHOTS:
            Shot(player.gunpos())
            shoot_sound.play()
        player.reloading = firing

        # Create new alien
        counter = 0
        if alienreload:
            alienreload = alienreload - 1
        elif not int(random.random() * ALIENS_CHANCE):
            Sml_Alien()
            if (bool(random.getrandbits(1))):
                Med_Alien()
                if (bool(random.getrandbits(1))):
                    Big_Alien()
            alienreload = ALIEN_RESPAWN

        # Drop bombs
        if lastalien and not int(random.random() * BOMBS_CHANCE):
            Bomb(lastalien.sprite)

        # Detect collisions
        for alien in pygame.sprite.spritecollide(player, aliens, 1):
            boom_sound.play()
            Explosion(alien)
            Explosion(player)
            SCORE = SCORE + 1
            player.kill()

        for alien in pygame.sprite.groupcollide(shots, aliens, 1, 1).keys():
            boom_sound.play()
            Explosion(alien)
            SCORE = SCORE + 1

        for bomb in pygame.sprite.spritecollide(player, bombs, 1):
            boom_sound.play()
            Explosion(player)
            Explosion(bomb)
            player.kill()

        # draw the scene
        dirty = all.draw(screen)
        pygame.display.update(dirty)

        # cap the framerate
        clock.tick(70)

    if pygame.mixer:
        pygame.mixer.music.fadeout(1000)
    pygame.time.wait(1000)
    pygame.quit()


# call the "main" function if running this script
if __name__ == '__main__':
    main()
