# Animated eyes, based (very) loosely on Adafruit / Phillip Burgess (Paint Your Dragon)'s Animated Snake Eyes for Raspberry Pi
# https://learn.adafruit.com/animated-snake-eyes-bonnet-for-raspberry-pi/software-installation

import time
import math
import gc
from picographics import PicoGraphics, PEN_P5
from picovector import PicoVector, Polygon, Rectangle, ANTIALIAS_X16

eyeRadius = 48
pupilRadiusMin = 12
pupilRadiusMax = 22
irisRadius = 28

# Define the wander of the iris
wanderX = 20
wanderY = 16
numWanderSteps = 100
wanderSteps = []
for s in range(numWanderSteps):
    wanderSteps.append(math.pi * 2 * s / numWanderSteps)
wanderStep = 0

# From: https://github.com/adafruit/Pi_Eyes
# This is graphics/eye.svg scaled to a radius of ~48 and inverted in Y
# Upper lid is defined left to right. Lower lid is defined right to left. This is handy when creating Polygons
upperLidClosedPts = [(-50, 13), (-48, 15), (-44, 14), (-42, 14), (-40, 14), (-37, 14), (-35, 15), (-31, 15),
                     (-27, 16), (-22, 17), (-15, 19), (-10, 20), (-6, 21), (-2, 22), (2, 22), (6, 23),
                     (10, 23), (13, 23), (17, 23), (20, 22), (23, 22), (26, 21), (29, 20), (32, 19),
                     (36, 17), (39, 14), (42, 12), (44, 9), (46, 6), (47, 3), (48, 0), (48, -5)]
upperLidOpenPts =   [(-50, 13), (-50, 6), (-49, 1), (-49, -3), (-47, -7), (-44, -10), (-42, -14), (-40, -18),
                     (-38, -21), (-36, -25), (-33, -28), (-29, -32), (-24, -36), (-18, -40), (-13, -43), (-8, -45),
                     (-2, -46), (3, -46), (8, -46), (13, -45), (17, -44), (21, -43), (25, -41), (28, -39),
                     (31, -37), (34, -34), (37, -30), (40, -26), (43, -21), (45, -16), (47, -11), (48, -5)]
lowerLidClosedPts = [(48, -5), (48, -3), (48, 0), (47, 4), (45, 7), (43, 10), (40, 13), (36, 15),
                     (32, 17), (29, 18), (26, 19), (22, 20), (18, 20), (15, 21), (11, 21), (7, 21),
                     (3, 20), (-1, 20), (-4, 19), (-8, 19), (-12, 18), (-15, 17), (-20, 16), (-25, 14),
                     (-30, 13), (-33, 12), (-36, 11), (-38, 11), (-41, 11), (-44, 12), (-49, 14), (-50, 13)]
lowerLidOpenPts =   [(48, -5), (48, 2), (48, 7), (47, 11), (46, 16), (45, 20), (43, 24), (40, 28),
                     (38, 31), (35, 34), (32, 37), (27, 40), (23, 42), (18, 44), (14, 45), (9, 46),
                     (5, 46), (0, 45), (-4, 45), (-8, 44), (-11, 43), (-17, 40), (-25, 37), (-30, 34),
                     (-35, 30), (-38, 27), (-40, 25), (-42, 22), (-43, 21), (-45, 20), (-48, 19), (-50, 13)]

# Define blink steps
numBlinkSteps = 16
closeLids = []
openLids = []
for s in range(numBlinkSteps + 1):
    closeLids.append(s / numBlinkSteps)
    openLids.append(1.0 - (s / numBlinkSteps))

# Set up the display
graphics = PicoGraphics(pen_type=PEN_P5, width=320, height=240)

vector = PicoVector(graphics)
vector.set_antialiasing(ANTIALIAS_X16)

WIDTH, HEIGHT = graphics.get_bounds()

BLACK = graphics.create_pen(0, 0, 0)
WHITE = graphics.create_pen(255, 255, 255)
IRIS = graphics.create_pen(255, 0, 0)

screen = (0,0,WIDTH,HEIGHT)

leftEyeCoords = (int(WIDTH / 2) + int(2 * eyeRadius), int(HEIGHT / 2))
rightEyeCoords = (int(WIDTH / 2) - int(2 * eyeRadius), int(HEIGHT / 2))

# Center (Translate) the left lids
leftUpperLidClosedPts = []
for p in range(len(upperLidClosedPts)):
    leftUpperLidClosedPts.append(((upperLidClosedPts[p][0] + leftEyeCoords[0], upperLidClosedPts[p][1] + leftEyeCoords[1])))
leftUpperLidOpenPts = []
for p in range(len(upperLidOpenPts)):
    leftUpperLidOpenPts.append(((upperLidOpenPts[p][0] + leftEyeCoords[0], upperLidOpenPts[p][1] + leftEyeCoords[1])))
leftLowerLidClosedPts = []
for p in range(len(lowerLidClosedPts)):
    leftLowerLidClosedPts.append(((lowerLidClosedPts[p][0] + leftEyeCoords[0], lowerLidClosedPts[p][1] + leftEyeCoords[1])))
leftLowerLidOpenPts = []
for p in range(len(lowerLidOpenPts)):
    leftLowerLidOpenPts.append(((lowerLidOpenPts[p][0] + leftEyeCoords[0], lowerLidOpenPts[p][1] + leftEyeCoords[1])))

# Find the left lid extremities
leftTop = HEIGHT
for point in leftUpperLidOpenPts:
    if point[1] < leftTop:
        leftTop = point[1]
leftBottom = 0
for point in leftLowerLidOpenPts:
    if point[1] > leftBottom:
        leftBottom = point[1]
leftLeft = WIDTH
for point in leftUpperLidOpenPts:
    if point[0] < leftLeft:
        leftLeft = point[0]
leftRight = 0
for point in leftUpperLidOpenPts:
    if point[0] > leftRight:
        leftRight = point[0]

leftEyeRect = (leftLeft,leftTop,leftRight-leftLeft,leftBottom-leftTop)

# Center (Translate) and mirror the right lids
rightUpperLidClosedPts = []
num = len(upperLidClosedPts)
for p in range(num):
    rightUpperLidClosedPts.append((((upperLidClosedPts[num - 1 - p][0] * -1) + rightEyeCoords[0], upperLidClosedPts[num - 1 - p][1] + rightEyeCoords[1])))
rightUpperLidOpenPts = []
num = len(upperLidOpenPts)
for p in range(num):
    rightUpperLidOpenPts.append((((upperLidOpenPts[num - 1 - p][0] * -1) + rightEyeCoords[0], upperLidOpenPts[num - 1 - p][1] + rightEyeCoords[1])))
rightLowerLidClosedPts = []
num = len(lowerLidClosedPts)
for p in range(num):
    rightLowerLidClosedPts.append((((lowerLidClosedPts[num - 1 - p][0] * -1) + rightEyeCoords[0], lowerLidClosedPts[num - 1 - p][1] + rightEyeCoords[1])))
rightLowerLidOpenPts = []
num = len(lowerLidOpenPts)
for p in range(num):
    rightLowerLidOpenPts.append((((lowerLidOpenPts[num - 1 - p][0] * -1) + rightEyeCoords[0], lowerLidOpenPts[num - 1 - p][1] + rightEyeCoords[1])))

# Find the right lid extremities
rightTop = HEIGHT
for point in rightUpperLidOpenPts:
    if point[1] < rightTop:
        rightTop = point[1]
rightBottom = 0
for point in rightLowerLidOpenPts:
    if point[1] > rightBottom:
        rightBottom = point[1]
rightLeft = WIDTH
for point in rightUpperLidOpenPts:
    if point[0] < rightLeft:
        rightLeft = point[0]
rightRight = 0
for point in rightUpperLidOpenPts:
    if point[0] > rightRight:
        rightRight = point[0]

rightEyeRect = (rightLeft, rightTop, rightRight - rightLeft, rightBottom - rightTop)

eyeRect = (rightLeft, rightTop, leftRight - rightLeft, rightBottom - rightTop)

def clear_screen():
    '''Clear screen: set whole screen to BLACK'''
    graphics.clear()
    graphics.set_pen(BLACK)
    graphics.rectangle(*screen)
    update_screen()

def fill_eyes():
    '''Set the whole eye area to WHITE'''
    graphics.set_pen(WHITE)
    graphics.rectangle(*leftEyeRect)
    graphics.rectangle(*rightEyeRect)

def draw_left_upper_lid(blink_fraction):
    '''Draw the eye lid. Use interpolation to blink the lid between open (blink_fraction = 0.0) and closed (1.0)'''

    lid = []
    for point in range(len(leftUpperLidOpenPts)):
        x = leftUpperLidOpenPts[point][0] + round((leftUpperLidClosedPts[point][0] - leftUpperLidOpenPts[point][0]) * blink_fraction)
        y = leftUpperLidOpenPts[point][1] + round((leftUpperLidClosedPts[point][1] - leftUpperLidOpenPts[point][1]) * blink_fraction)
        lid.append((x,y))
    lid.append((leftRight, leftTop))
    lid.append((leftLeft, leftTop))        

    graphics.set_pen(BLACK)
    lidPoly = Polygon(*lid)
    vector.draw(lidPoly)

def draw_left_lower_lid(blink_fraction):
    '''Draw the eye lid. Use interpolation to blink the lid between open (blink_fraction = 0.0) and closed (1.0)'''

    lid = []
    for point in range(len(leftLowerLidOpenPts)):
        x = leftLowerLidOpenPts[point][0] + round((leftLowerLidClosedPts[point][0] - leftLowerLidOpenPts[point][0]) * blink_fraction)
        y = leftLowerLidOpenPts[point][1] + round((leftLowerLidClosedPts[point][1] - leftLowerLidOpenPts[point][1]) * blink_fraction)
        lid.append((x,y))
    lid.append((leftLeft, leftBottom))
    lid.append((leftRight, leftBottom))        

    graphics.set_pen(BLACK)
    lidPoly = Polygon(*lid)
    vector.draw(lidPoly)

def draw_right_upper_lid(blink_fraction):
    '''Draw the eye lid. Use interpolation to blink the lid between open (blink_fraction = 0.0) and closed (1.0)'''

    lid = []
    for point in range(len(rightUpperLidOpenPts)):
        x = rightUpperLidOpenPts[point][0] + round((rightUpperLidClosedPts[point][0] - rightUpperLidOpenPts[point][0]) * blink_fraction)
        y = rightUpperLidOpenPts[point][1] + round((rightUpperLidClosedPts[point][1] - rightUpperLidOpenPts[point][1]) * blink_fraction)
        lid.append((x,y))
    lid.append((rightRight, rightTop))
    lid.append((rightLeft, rightTop))        

    graphics.set_pen(BLACK)
    lidPoly = Polygon(*lid)
    vector.draw(lidPoly)

def draw_right_lower_lid(blink_fraction):
    '''Draw the eye lid. Use interpolation to blink the lid between open (blink_fraction = 0.0) and closed (1.0)'''

    lid = []
    for point in range(len(rightLowerLidOpenPts)):
        x = rightLowerLidOpenPts[point][0] + round((rightLowerLidClosedPts[point][0] - rightLowerLidOpenPts[point][0]) * blink_fraction)
        y = rightLowerLidOpenPts[point][1] + round((rightLowerLidClosedPts[point][1] - rightLowerLidOpenPts[point][1]) * blink_fraction)
        lid.append((x,y))
    lid.append((rightLeft, rightBottom))
    lid.append((rightRight, rightBottom))        

    graphics.set_pen(BLACK)
    lidPoly = Polygon(*lid)
    vector.draw(lidPoly)

def draw_iris(pupil_fraction, x, y):
    '''Draw the iris with pupil at x,y'''
    
    graphics.set_pen(IRIS)
    graphics.circle(round(x),round(y),irisRadius)
    graphics.set_pen(BLACK)
    graphics.circle(round(x),round(y),round(pupilRadiusMin + ((pupilRadiusMax - pupilRadiusMin) * pupil_fraction)))

def update_screen():
    graphics.update()
    gc.collect()

clear_screen()
graphics.set_clip(*eyeRect)

while True:
    
    for b in closeLids:
        fill_eyes()
        draw_iris(math.sin((2 * wanderSteps[wanderStep]) + 1) / 2, leftEyeCoords[0] + (math.sin(wanderSteps[wanderStep]) * wanderX), leftEyeCoords[1] + (math.cos(wanderSteps[wanderStep]) * wanderY))
        draw_left_lower_lid(b)
        draw_left_upper_lid(b)
        draw_iris(math.sin((2 * wanderSteps[wanderStep]) + 1) / 2, rightEyeCoords[0] + (math.cos(wanderSteps[wanderStep]) * wanderY), rightEyeCoords[1] + (math.sin(wanderSteps[wanderStep]) * wanderX))
        draw_right_lower_lid(b)
        draw_right_upper_lid(b)
        update_screen()
        wanderStep += 1
        wanderStep %= numWanderSteps
        #time.sleep(0.1)
        
    #time.sleep(0.1)

    for b in openLids:
        fill_eyes()
        draw_iris(math.sin((2 * wanderSteps[wanderStep]) + 1) / 2, leftEyeCoords[0] + (math.sin(wanderSteps[wanderStep]) * wanderX), leftEyeCoords[1] + (math.cos(wanderSteps[wanderStep]) * wanderY))
        draw_left_lower_lid(b)
        draw_left_upper_lid(b)
        draw_iris(math.sin((2 * wanderSteps[wanderStep]) + 1) / 2, rightEyeCoords[0] + (math.cos(wanderSteps[wanderStep]) * wanderY), rightEyeCoords[1] + (math.sin(wanderSteps[wanderStep]) * wanderX))
        draw_right_lower_lid(b)
        draw_right_upper_lid(b)
        update_screen()
        wanderStep += 1
        wanderStep %= numWanderSteps
        #time.sleep(0.1)
        
    for t in range(100):
        fill_eyes()
        draw_iris(math.sin((2 * wanderSteps[wanderStep]) + 1) / 2, leftEyeCoords[0] + (math.sin(wanderSteps[wanderStep]) * wanderX), leftEyeCoords[1] + (math.cos(wanderSteps[wanderStep]) * wanderY))
        draw_left_lower_lid(b)
        draw_left_upper_lid(b)
        draw_iris(math.sin((2 * wanderSteps[wanderStep]) + 1) / 2, rightEyeCoords[0] + (math.cos(wanderSteps[wanderStep]) * wanderY), rightEyeCoords[1] + (math.sin(wanderSteps[wanderStep]) * wanderX))
        draw_right_lower_lid(b)
        draw_right_upper_lid(b)
        update_screen()
        wanderStep += 1
        wanderStep %= numWanderSteps
        #time.sleep(0.1)
        