from itertools import cycle
import random
import sys
import pygame
from pygame.locals import *
frames_per_second = 30
screen_width = 288
screen_height = 512
pipe_gap_size = 100
base_y = screen_height * 0.79
images, sounds, hitmasks = {}, {}, {}
birds_list = (
    (
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
    ),
    (
        'assets/sprites/bluebird-upflap.png',
        'assets/sprites/bluebird-midflap.png',
        'assets/sprites/bluebird-downflap.png',
    ),
    (
        'assets/sprites/yellowbird-upflap.png',
        'assets/sprites/yellowbird-midflap.png',
        'assets/sprites/yellowbird-downflap.png',
    ),
)
backgrounds_list = (
    'assets/sprites/background-day.png',
    'assets/sprites/background-night.png',
)
pipes_list = (
    'assets/sprites/pipe-green.png',
    'assets/sprites/pipe-red.png',
)
frames_per_second_clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))
def main():
    global screen, frames_per_second_clock
    pygame.init()
    pygame.display.set_caption('Flappy Bird - Ayaan Hashmi')
    images['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )
    images['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    images['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
    images['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()
    if 'win' in sys.platform:
        sound_ext = '.wav'
    else:
        sound_ext = '.ogg'
    sounds['die'] = pygame.mixer.Sound('assets/audio/die' + sound_ext)
    sounds['hit'] = pygame.mixer.Sound('assets/audio/hit' + sound_ext)
    sounds['point'] = pygame.mixer.Sound('assets/audio/point' + sound_ext)
    sounds['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + sound_ext)
    sounds['wing'] = pygame.mixer.Sound('assets/audio/wing' + sound_ext)
    while True:
        random_background = random.randint(0, len(backgrounds_list) - 1)
        images['background'] = pygame.image.load(backgrounds_list[random_background]).convert()
        random_bird = random.randint(0, len(birds_list) - 1)
        images['player'] = (
            pygame.image.load(birds_list[random_bird][0]).convert_alpha(),
            pygame.image.load(birds_list[random_bird][1]).convert_alpha(),
            pygame.image.load(birds_list[random_bird][2]).convert_alpha(),
        )
        pipe_index = random.randint(0, len(pipes_list) - 1)
        images['pipe'] = (
            pygame.transform.flip(
                pygame.image.load(pipes_list[pipe_index]).convert_alpha(), False, True),
            pygame.image.load(pipes_list[pipe_index]).convert_alpha(),
        )
        hitmasks['pipe'] = (
            get_hitmask(images['pipe'][0]),
            get_hitmask(images['pipe'][1]),
        )
        hitmasks['player'] = (
            get_hitmask(images['player'][0]),
            get_hitmask(images['player'][1]),
            get_hitmask(images['player'][2]),
        )
        movement_info = showWelcomeAnimation()
        crash_info = mainGame(movement_info)
        showGameOverScreen(crash_info)
def showWelcomeAnimation():
    player_index = 0
    player_index_gen = cycle([0, 1, 2, 1])
    loop_iter = 0
    player_x = int(screen_width * 0.2)
    player_y = int((screen_height - images['player'][0].get_height()) / 2)
    message_x = int((screen_width - images['message'].get_width()) / 2)
    message_y = int(screen_height * 0.12)
    base_x = 0
    base_shift = images['base'].get_width() - images['background'].get_width()
    player_shm_vals = {'val': 0, 'dir': 1}
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                sounds['wing'].play()
                return {
                    'player_y': player_y + player_shm_vals['val'],
                    'basex': base_x,
                    'player_index_gen': player_index_gen,
                }
        if (loop_iter + 1) % 5 == 0:
            player_index = next(player_index_gen)
        loop_iter = (loop_iter + 1) % 30
        base_x = -((-base_x + 4) % base_shift)
        playerShm(player_shm_vals)
        screen.blit(images['background'], (0, 0))
        screen.blit(images['player'][player_index],
                    (player_x, player_y + player_shm_vals['val']))
        screen.blit(images['message'], (message_x, message_y))
        screen.blit(images['base'], (base_x, base_y))
        pygame.display.update()
        frames_per_second_clock.tick(frames_per_second)
def mainGame(movementInfo):
    score = playerIndex = loopIter = 0
    player_index_gen = movementInfo['player_index_gen']
    player_x, player_y = int(screen_width * 0.2), movementInfo['player_y']
    basex = movementInfo['basex']
    baseShift = images['base'].get_width() - images['background'].get_width()
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()
    upperPipes = [
        {'x': screen_width + 200, 'y': newPipe1[0]['y']},
        {'x': screen_width + 200 + (screen_width / 2), 'y': newPipe2[0]['y']},
    ]
    lowerPipes = [
        {'x': screen_width + 200, 'y': newPipe1[1]['y']},
        {'x': screen_width + 200 + (screen_width / 2), 'y': newPipe2[1]['y']},
    ]
    dt = frames_per_second_clock.tick(frames_per_second)/1000
    pipeVelX = -128 * dt
    playerVelY = -9
    playerMaxVelY = 10
    playerAccY = 1
    playerRot = 45
    playerVelRot = 3
    playerRotThr = 20
    playerFlapAcc = -9
    playerFlapped = False
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player_y > -2 * images['player'][0].get_height():
                    playerVelY = playerFlapAcc
                    playerFlapped = True
                    sounds['wing'].play()
        crashTest = checkCrash({'x': player_x, 'y': player_y, 'index': playerIndex},
                               upperPipes, lowerPipes)
        if crashTest[0]:
            return {
                'y': player_y,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperPipes': upperPipes,
                'lowerPipes': lowerPipes,
                'score': score,
                'playerVelY': playerVelY,
                'playerRot': playerRot
            }
        playerMidPos = player_x + images['player'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + images['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                sounds['point'].play()
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(player_index_gen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)
        if playerRot > -90:
            playerRot -= playerVelRot
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False
            playerRot = 45
        playerHeight = images['player'][playerIndex].get_height()
        player_y += min(playerVelY, base_y - player_y - playerHeight)
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX
        if 3 > len(upperPipes) > 0 and 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])
        if len(upperPipes) > 0 and upperPipes[0]['x'] < -images['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)
        screen.blit(images['background'], (0, 0))
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            screen.blit(images['pipe'][0], (uPipe['x'], uPipe['y']))
            screen.blit(images['pipe'][1], (lPipe['x'], lPipe['y']))
        screen.blit(images['base'], (basex, base_y))
        showScore(score)
        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot
        playerSurface = pygame.transform.rotate(images['player'][playerIndex], visibleRot)
        screen.blit(playerSurface, (player_x, player_y))
        pygame.display.update()
        frames_per_second_clock.tick(frames_per_second)
def showGameOverScreen(crashInfo):
    score = crashInfo['score']
    player_x = screen_width * 0.2
    player_y = crashInfo['y']
    playerHeight = images['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7
    basex = crashInfo['basex']
    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']
    sounds['hit'].play()
    if not crashInfo['groundCrash']:
        sounds['die'].play()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player_y + playerHeight >= base_y - 1:
                    return
        if player_y + playerHeight < base_y - 1:
            player_y += min(playerVelY, base_y - player_y - playerHeight)
        if playerVelY < 15:
            playerVelY += playerAccY
        if not crashInfo['groundCrash']:
            if playerRot > -90:
                playerRot -= playerVelRot
        screen.blit(images['background'], (0, 0))
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            screen.blit(images['pipe'][0], (uPipe['x'], uPipe['y']))
            screen.blit(images['pipe'][1], (lPipe['x'], lPipe['y']))
        screen.blit(images['base'], (basex, base_y))
        showScore(score)
        playerSurface = pygame.transform.rotate(images['player'][1], playerRot)
        screen.blit(playerSurface, (player_x, player_y))
        screen.blit(images['gameover'], (50, 180))
        frames_per_second_clock.tick(frames_per_second)
        pygame.display.update()
def playerShm(playerShm):
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1
    if playerShm['dir'] == 1:
        playerShm['val'] += 1
    else:
        playerShm['val'] -= 1
def getRandomPipe():
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(base_y * 0.6 - pipe_gap_size))
    gapY += int(base_y * 0.2)
    pipeHeight = images['pipe'][0].get_height()
    pipeX = screen_width + 10
    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + pipe_gap_size}, # lower pipe
    ]
def showScore(score):
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0
    for digit in scoreDigits:
        totalWidth += images['numbers'][digit].get_width()
    Xoffset = (screen_width - totalWidth) / 2
    for digit in scoreDigits:
        screen.blit(images['numbers'][digit], (Xoffset, screen_height * 0.1))
        Xoffset += images['numbers'][digit].get_width()
def checkCrash(player, upperPipes, lowerPipes):
    pi = player['index']
    player['w'] = images['player'][0].get_width()
    player['h'] = images['player'][0].get_height()
    if player['y'] + player['h'] >= base_y - 1:
        return [True, True]
    else:
        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
        pipeW = images['pipe'][0].get_width()
        pipeH = images['pipe'][0].get_height()
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)
            pHitMask = hitmasks['player'][pi]
            uHitmask = hitmasks['pipe'][0]
            lHitmask = hitmasks['pipe'][1]
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)
            if uCollide or lCollide:
                return [True, False]
    return [False, False]
def pixelCollision(rect1, rect2, mask1, mask2, offset=(0, 0)):
    # Calculateing the area where the masks will overlap
    x_offset = rect2.left - rect1.left + offset[0]
    y_offset = rect2.top - rect1.top + offset[1]
    # Check for overlap in masks
    overlap = mask1.overlap(mask2, (x_offset, y_offset))
    return overlap is not None
def get_hitmask(image):
    # Creating a mask from the image (image should be a Pygame surface)
    mask = pygame.mask.from_surface(image)
    return mask
if __name__ == '__main__':
    main()