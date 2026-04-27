import RPi.GPIO as GPIO
import time
import threading
import os
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from collections import deque
import statistics

os.environ["QT_QPA_PLATFORM"] = "xcb"

# --- Hardware Setup ---
SENSORS = {
    "Front": {"trig": 17, "echo": 27},
    "Back":  {"trig": 22, "echo": 23},
    "Left":  {"trig": 16, "echo": 20},
    "Right": {"trig": 5,  "echo": 6},
}
sensor_buffers = {name: deque(maxlen=5) for name in SENSORS}
distances = {name: 400.0 for name in SENSORS}

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for name, pins in SENSORS.items():
    GPIO.setup(pins["trig"], GPIO.OUT)
    GPIO.setup(pins["echo"], GPIO.IN)

def read_ultrasonic(name, trig, echo):
    while True:
        GPIO.output(trig, False); time.sleep(0.01)
        GPIO.output(trig, True); time.sleep(0.00001); GPIO.output(trig, False)
        t0 = time.time(); ps, pe = t0, t0; timeout = t0 + 0.04
        while GPIO.input(echo) == 0:
            ps = time.time()
            if ps > timeout: break
        while GPIO.input(echo) == 1:
            pe = time.time()
            if pe > timeout: break
        raw = ((pe - ps) * 34300) / 2
        sensor_buffers[name].append(raw if 2 < raw < 400 else 400.0)
        distances[name] = round(statistics.median(sensor_buffers[name]), 1)
        time.sleep(0.06)

for name, pins in SENSORS.items():
    threading.Thread(target=read_ultrasonic, args=(name, pins["trig"], pins["echo"]), daemon=True).start()

# --- 3D Solid Cube Logic ---
def draw_solid_cube(x, y, z, size, color):
    r, g, b = color
    h = size / 2
    glBegin(GL_QUADS)
    glColor3f(r, g, b); glVertex3f(x+h,y+h,z-h); glVertex3f(x-h,y+h,z-h); glVertex3f(x-h,y+h,z+h); glVertex3f(x+h,y+h,z+h) # Top
    glColor3f(r*0.7,g*0.7,b*0.7); glVertex3f(x+h,y+h,z+h); glVertex3f(x-h,y+h,z+h); glVertex3f(x-h,y-h,z+h); glVertex3f(x+h,y-h,z+h) # Front
    glColor3f(r*0.5,g*0.5,b*0.5); glVertex3f(x-h,y+h,z+h); glVertex3f(x-h,y+h,z-h); glVertex3f(x-h,y-h,z-h); glVertex3f(x-h,y-h,z+h) # Left
    glColor3f(r*0.5,g*0.5,b*0.5); glVertex3f(x+h,y+h,z-h); glVertex3f(x+h,y+h,z+h); glVertex3f(x+h,y-h,z+h); glVertex3f(x+h,y-h,z-h) # Right
    glEnd()

# --- Stable Text Rendering (Texture Method) ---
def render_text_to_texture(text, font):
    surf = font.render(text, True, (0, 255, 136), (20, 20, 20))
    data = pygame.image.tostring(surf, "RGBA", True)
    w, h = surf.get_size()
    
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    return tex, w, h

def main():
    pygame.init()
    win_w, win_h = 1000, 700
    pygame.display.set_mode((win_w, win_h), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Samfred Robotics - 3D HUD")
    font = pygame.font.SysFont('monospace', 24, bold=True)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    rot_y = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # --- 1. Draw 3D Scene ---
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (win_w/win_h), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, -2.5, -15)
        glRotatef(20, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)

        # Ground
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_LINES)
        for i in range(-10, 11):
            glVertex3f(i,0,-10); glVertex3f(i,0,10); glVertex3f(-10,0,i); glVertex3f(10,0,i)
        glEnd()

        # Robot (Solid Blue)
        draw_solid_cube(0, 0.5, 0, 1.2, (0.0, 0.4, 1.0))

        # Obstacles
        dirs = {"Front":(0,0,-1), "Back":(0,0,1), "Left":(-1,0,0), "Right":(1,0,0)}
        for name, (dx, dy, dz) in dirs.items():
            d = distances[name]; d_gl = d * 0.05
            color = (0,1,0) if d > 100 else (1,0.5,0) if d > 40 else (1,0,0)
            draw_solid_cube(dx*d_gl, 0.5, dz*d_gl, 0.8, color)
            glBegin(GL_LINES); glColor3f(*color); glVertex3f(0,0.5,0); glVertex3f(dx*d_gl, 0.5, dz*d_gl); glEnd()

        # --- 2. Draw 2D HUD (The Reliable Way) ---
        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
        gluOrtho2D(0, win_w, 0, win_h)
        glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

        y_offset = win_h - 40
        for name in ["Front", "Back", "Left", "Right"]:
            txt = f"{name.upper()}: {distances[name]} cm"
            tex, tw, th = render_text_to_texture(txt, font)
            glBindTexture(GL_TEXTURE_2D, tex)
            glBegin(GL_QUADS)
            glColor3f(1,1,1)
            glTexCoord2f(0,0); glVertex2f(20, y_offset)
            glTexCoord2f(1,0); glVertex2f(20+tw, y_offset)
            glTexCoord2f(1,1); glVertex2f(20+tw, y_offset+th)
            glTexCoord2f(0,1); glVertex2f(20, y_offset+th)
            glEnd()
            glDeleteTextures(1, [tex]) # Clean up memory
            y_offset -= 40

        glDisable(GL_TEXTURE_2D); glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW); glPopMatrix()

        rot_y += 0.5
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    try: main()
    finally: GPIO.cleanup(); pygame.quit()