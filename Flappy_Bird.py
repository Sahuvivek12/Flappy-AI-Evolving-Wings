import neat
import pygame
import time
import os
import random
pygame.font.init()

PHASE = 0
WIN_WIDTH = 500
WIN_HEIGHT = 800
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Flappy Bird")
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("Flappy bird with AI/imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("Flappy bird with AI/imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("Flappy bird with AI/imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Flappy bird with AI/imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Flappy bird with AI/imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("Flappy bird with AI/imgs", "bg.png")).convert_alpha())

STAT_FONT = pygame.font.SysFont('Comic Sans MS', 30)

class FlappyBird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 16
    ANIMATION_TIME = 5

    def get_rect(self):
        return self.img.get_rect(topleft=(self.x, self.y))

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.velocity = -10
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.velocity * self.tick_count + 1.5 * self.tick_count ** 2

        if d >= 6:
            d = 6
        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 30:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 5:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 6:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 6:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rectangle = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    
class Pipe:
    GAP = 200
    VEL = 3

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_rect = bird.get_rect()
        pipe_top_rect = self.PIPE_TOP.get_rect(topleft=(self.x, self.top))
        pipe_bottom_rect = self.PIPE_BOTTOM.get_rect(topleft=(self.x, self.bottom))

        if bird_rect.colliderect(pipe_top_rect) or bird_rect.colliderect(pipe_bottom_rect):
            bird_mask = bird.get_mask()
            top_mask = pygame.mask.from_surface(self.PIPE_TOP)
            bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

            top_offset = (self.x - bird.x, self.top - round(bird.y))
            bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

            if bird_mask.overlap(top_mask, top_offset) or bird_mask.overlap(bottom_mask, bottom_offset):
                return True

        return False

class Base:
    VEL = 3.5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def draw_window(win, birds, pipes, base, score, phase):
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render('Score: ' + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render('Phase: ' + str(PHASE), 1, (255, 255, 255))
    win.blit(text, (10, 10))
    
    base.draw(win)

    for bird in birds:
        bird.draw(win)

    pygame.display.update()

def main(genomes, config):
    global PHASE
    nets = []
    GE = []
    flappy_birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        flappy_birds.append(FlappyBird(230, 350))
        g.fitness = 0   
        GE.append(g)

    base = Base(730)
    pipes = [Pipe(600)]
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        if len(flappy_birds) == 0:
            PHASE += 1
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(flappy_birds) > 0:
            if len(pipes) > 1 and flappy_birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break
        for x, flappy_bird in enumerate(flappy_birds):
            flappy_bird.move()
            GE[x].fitness += 0.05

            output = nets[x].activate((flappy_bird.y, abs(flappy_bird.y - pipes[pipe_ind].height), abs(flappy_bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                flappy_bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, flappy_bird in enumerate(flappy_birds):
                if pipe.collide(flappy_bird):
                    GE[x].fitness = -1
                    flappy_birds.pop(x)
                    nets.pop(x)
                    GE.pop(x)

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
                
            pipe.move()
            if not pipe.passed and pipe.x < flappy_bird.x:
                pipe.passed = True
                add_pipe = True
        if add_pipe:
            score += 1
            for g in GE:
                g.fitness += 5
            pipes.append(Pipe(700))

        for r in rem:
            pipes.remove(r)
        for x, flappy_bird in enumerate(flappy_birds):
            if flappy_bird.y + flappy_bird.img.get_height() >= 730 or flappy_bird.y < 0:
                flappy_birds.pop(x)
                nets.pop(x)
                GE.pop(x)

        base.move()
        draw_window(WIN, flappy_birds, pipes, base, score, PHASE)

def Run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                 neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 30)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-NEAT.txt')
    Run(config_path)
