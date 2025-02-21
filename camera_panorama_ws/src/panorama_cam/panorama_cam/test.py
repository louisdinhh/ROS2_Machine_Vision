import pygame
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import cv2
import numpy as np

# Initialize pygame and OpenGL
pygame.init()
window_size = (1800, 800)  # Adjust this to your desired window size
screen = pygame.display.set_mode(window_size, pygame.DOUBLEBUF | pygame.OPENGL)

# Set up OpenGL
glClearColor(0.0, 0.0, 0.0, 1.0)
glEnable(GL_TEXTURE_2D)

# Initialize the two V4L2 cameras using OpenCV
cap0 = cv2.VideoCapture("/dev/video0")
cap1 = cv2.VideoCapture("/dev/video2")

if not cap0.isOpened() or not cap1.isOpened():
    print("Error: Unable to open one or both cameras.")
    exit()

# Function to create an OpenGL texture from a frame
def create_texture(frame):
    height, width, _ = frame.shape
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    
    # Convert BGR to RGB as OpenGL expects RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Upload texture to OpenGL
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, frame_rgb)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    return texture

# Function to render a texture as a quad in OpenGL
def render_texture(texture, x_offset, y_offset, width, height):
    glBindTexture(GL_TEXTURE_2D, texture)
    
    # Flip the texture vertically by swapping texture coordinates
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1)  # Flip Y coordinate here
    glVertex2f(x_offset, y_offset)
    
    glTexCoord2f(1, 1)  # Flip Y coordinate here
    glVertex2f(x_offset + width, y_offset)
    
    glTexCoord2f(1, 0)  # Flip Y coordinate here
    glVertex2f(x_offset + width, y_offset + height)
    
    glTexCoord2f(0, 0)  # Flip Y coordinate here
    glVertex2f(x_offset, y_offset + height)
    glEnd()

# Main rendering loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    glClear(GL_COLOR_BUFFER_BIT)
    
    # Capture frames from the cameras
    ret0, frame0 = cap0.read()
    ret1, frame1 = cap1.read()

    if ret0 and ret1:
        # Get the resolution of both camera frames
        height0, width0, _ = frame0.shape
        height1, width1, _ = frame1.shape
        
        # Ensure both frames have the same height for consistent rendering
        aspect_ratio0 = height0 / width0
        aspect_ratio1 = height1 / width1

        # You can adjust the display size of each frame here based on the aspect ratio
        window_width = window_size[0]//2
        window_height = window_size[1]

        # Resize frames to maintain aspect ratio (scale the width and adjust height accordingly)
        frame0_resized = cv2.resize(frame0, (window_width, int(window_width * aspect_ratio0)))
        frame1_resized = cv2.resize(frame1, (window_width, int(window_width * aspect_ratio1)))

        # Create OpenGL textures from resized frames
        texture0 = create_texture(frame0_resized)
        texture1 = create_texture(frame1_resized)
        
        # Render the textures as quads side by side
        render_texture(texture0, -0.5, -0.5, 1.0, 1.0)  # Left camera
        render_texture(texture1, 0.0, -0.5, 1.0, 1.0)   # Right camera

    pygame.display.flip()

# Release resources
cap0.release()
cap1.release()
pygame.quit()
