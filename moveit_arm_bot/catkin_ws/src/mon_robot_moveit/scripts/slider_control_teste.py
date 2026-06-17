#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import math
import rospy
import pygame
from sensor_msgs.msg import JointState
from std_msgs.msg import Header

# --- CONFIGURATION DES COULEURS STYLE "TECH GUY" ---
BACKGROUND_COLOR = (15, 20, 30)      # Bleu nuit très sombre
PANEL_COLOR = (25, 35, 50)           # Bleu acier pour les boîtes
TEXT_COLOR = (220, 240, 255)         # Blanc bleuté
SLIDER_BG = (40, 55, 75)             # Fond des rails de sliders
SLIDER_FILL = (0, 150, 255)          # Remplissage bleu fluo
THUMB_COLOR = (0, 255, 200)          # Bouton cyan fluo

class Slider:
    def __init__(self, x, y, w, h, name, min_val, max_val, default):
        self.rect = pygame.Rect(x, y, w, h)
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.val = default
        self.clicked = False
        
        # Calculer la position initiale du bouton (Thumb)
        self.thumb_width = 16
        self.update_thumb_pos()

    def update_thumb_pos(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.thumb_rect = pygame.Rect(
            self.rect.x + ratio * (self.rect.w - self.thumb_width),
            self.rect.y - 4,
            self.thumb_width,
            self.rect.h + 8
        )

    def draw(self, screen, font):
        # Dessiner le nom du joint et sa valeur textuelle
        txt_name = font.render(f"{self.name}:", True, TEXT_COLOR)
        txt_val = font.render(f"{math.degrees(self.val):.1f}°", True, THUMB_COLOR)
        screen.blit(txt_name, (self.rect.x - 170, self.rect.y - 2))
        screen.blit(txt_val, (self.rect.x + self.rect.w + 20, self.rect.y - 2))

        # Dessiner le rail du slider
        pygame.draw.rect(screen, SLIDER_BG, self.rect, border_radius=4)
        
        # Dessiner la partie remplie
        fill_w = self.thumb_rect.centerx - self.rect.x
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.h)
            pygame.draw.rect(screen, SLIDER_FILL, fill_rect, border_radius=4)

        # Dessiner le bouton de contrôle (Thumb)
        pygame.draw.rect(screen, THUMB_COLOR, self.thumb_rect, border_radius=4)

    def handle_event(self, mouse_pos, mouse_buttons):
        if mouse_buttons[0]: # Clic gauche enfoncé
            if self.rect.collidepoint(mouse_pos) or self.thumb_rect.collidepoint(mouse_pos) or self.clicked:
                self.clicked = True
                # Calculer la valeur en fonction de la souris
                rel_x = max(0, min(mouse_pos[0] - self.rect.x, self.rect.w))
                ratio = rel_x / self.rect.w
                self.val = self.min_val + ratio * (self.max_val - self.min_val)
                self.update_thumb_pos()
        else:
            self.clicked = False


def main():
    # --- INITIALISATION ROS ---
    rospy.init_node('py_slider_control', anonymous=True)
    joint_pub = rospy.Publisher('/move_group/fake_controller_joint_states', JointState, queue_size=1)
    # Note : Si le robot ne bouge pas dans RViz, change par : '/joint_states'
    
    # --- INITIALISATION PYGAME ---
    pygame.init()
    pygame.display.set_caption("🎛️ Robot Arm - Slider Control Studio")
    screen = pygame.display.set_mode((750, 480))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Helvetica", 18, bold=True)
    font_title = pygame.font.SysFont("Helvetica", 24, bold=True)

    # --- CRÉATION DES 6 SLIDERS (Valeurs en Radians) ---
    # Modifier les limites de min/max pour correspondre exactement à ton URDF si nécessaire
    sliders = [
        Slider(200, 100, 400, 14, "Waist Joint", -3.14, 3.14, 0.0),
        Slider(200, 150, 400, 14, "Shoulder Joint", -1.57, 1.57, 0.0),
        Slider(200, 200, 400, 14, "Elbow Joint", -2.09, 2.09, 0.0),
        Slider(200, 250, 400, 14, "Wrist Joint", -3.14, 3.14, 0.0),
        Slider(200, 300, 400, 14, "Joint 5", -1.57, 1.57, 0.0),
        Slider(200, 350, 400, 14, "Joint 6", -3.14, 3.14, 0.0)
    ]

    running = True
    while running and not rospy.is_shutdown():
        # Capturer la souris et les évènements
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Effacer l'écran
        screen.fill(BACKGROUND_COLOR)

        # Dessiner le titre du panneau supérieur
        pygame.draw.rect(screen, PANEL_COLOR, (0, 0, 750, 60))
        title_text = font_title.render("SYSTEM SLIDER CONTROL PANEL", True, THUMB_COLOR)
        screen.blit(title_text, (30, 16))

        # Mettre à jour et dessiner chaque Slider
        angles = []
        for slider in sliders:
            slider.handle_event(mouse_pos, mouse_buttons)
            slider.draw(screen, font)
            angles.append(slider.val)

        # --- PUBLICATION DIRECTE DANS ROS ---
        joint_state = JointState()
        joint_state.header = Header()
        joint_state.header.stamp = rospy.Time.now()
        # Remplace par les noms de tes joints du fichier URDF
        joint_state.name = ['waist_joint', 'shoulder_joint', 'elbow_joint', 'wrist_joint', 'joint_5', 'joint_6']
        joint_state.position = angles
        joint_pub.publish(joint_state)

        # Rafraîchir l'écran à 60 FPS pour une fluidité absolue
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()