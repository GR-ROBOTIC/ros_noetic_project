#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import math
import rospy
import pygame
from sensor_msgs.msg import JointState
from visualization_msgs.msg import Marker
from std_msgs.msg import Header

# --- COULEURS STYLE "TECH GUY" ---
BACKGROUND_COLOR = (15, 20, 30)
PANEL_COLOR = (25, 35, 50)
TEXT_COLOR = (220, 240, 255)
SLIDER_BG = (40, 55, 75)
SLIDER_FILL = (0, 150, 255)
THUMB_COLOR = (0, 255, 200)
BUTTON_COLOR = (40, 80, 120)
BUTTON_ACTIVE = (0, 180, 120)

class Slider:
    def __init__(self, x, y, w, h, name, min_val, max_val, default):
        self.rect = pygame.Rect(x, y, w, h)
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.val = default
        self.clicked = False
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
        txt_name = font.render(f"{self.name}:", True, TEXT_COLOR)
        txt_val = font.render(f"{math.degrees(self.val):.1f}°", True, THUMB_COLOR)
        screen.blit(txt_name, (self.rect.x - 170, self.rect.y - 2))
        screen.blit(txt_val, (self.rect.x + self.rect.w + 20, self.rect.y - 2))
        pygame.draw.rect(screen, SLIDER_BG, self.rect, border_radius=4)
        fill_w = self.thumb_rect.centerx - self.rect.x
        if fill_w > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.h)
            pygame.draw.rect(screen, SLIDER_FILL, fill_rect, border_radius=4)
        pygame.draw.rect(screen, THUMB_COLOR, self.thumb_rect, border_radius=4)

    def handle_event(self, mouse_pos, mouse_buttons):
        if mouse_buttons[0]:
            if self.rect.collidepoint(mouse_pos) or self.thumb_rect.collidepoint(mouse_pos) or self.clicked:
                self.clicked = True
                rel_x = max(0, min(mouse_pos[0] - self.rect.x, self.rect.w))
                ratio = rel_x / self.rect.w
                self.val = self.min_val + ratio * (self.max_val - self.min_val)
                self.update_thumb_pos()
        else:
            self.clicked = False

def main():
    # --- INITIALISATION ROS ---
    rospy.init_node('py_slider_text_control', anonymous=True)
    joint_pub = rospy.Publisher('/move_group/fake_controller_joint_states', JointState, queue_size=1)
    marker_pub = rospy.Publisher('/visualization_marker', Marker, queue_size=10)
    
    # --- INITIALISATION PYGAME ---
    pygame.init()
    pygame.display.set_caption("🎛️ Robot Arm - Multi-Control Panel")
    
    # ÉCRAN PLUS GRAND POUR NE PAS COUPER LE BAS (Hauteur passée à 650)
    screen = pygame.display.set_mode((750, 650)) 
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Helvetica", 18, bold=True)
    font_title = pygame.font.SysFont("Helvetica", 24, bold=True)

    # --- CONFIGURATION DES SLIDERS ---
    sliders = [
        Slider(200, 100, 400, 14, "Waist Joint", -3.14, 3.14, 0.0),
        Slider(200, 150, 400, 14, "Shoulder Joint", -1.57, 1.57, 0.0),
        Slider(200, 200, 400, 14, "Elbow Joint", -2.09, 2.09, 0.0),
        Slider(200, 250, 400, 14, "Wrist Joint", -3.14, 3.14, 0.0),
        Slider(200, 300, 400, 14, "Joint 5", -1.57, 1.57, 0.0),
        Slider(200, 350, 400, 14, "Joint 6", -3.14, 3.14, 0.0)
    ]

    # --- POSITIONNEMENT CORRIGÉ DES BOUTONS (Remontés à Y=450) ---
    user_text = "CIBLE RVIZ"
    input_rect = pygame.Rect(200, 450, 220, 36)
    button_rect = pygame.Rect(440, 450, 160, 36)
    input_active = False
    text_tracking_mode = False

    # Position 3D du texte dans RViz
    text_x, text_y, text_z = 0.5, 0.3, 0.4

    running = True
    while running and not rospy.is_shutdown():
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False
                
                if button_rect.collidepoint(event.pos):
                    text_tracking_mode = not text_tracking_mode

            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif event.key == pygame.K_RETURN:
                    input_active = False
                else:
                    if len(user_text) < 15:
                        user_text += event.unicode

        screen.fill(BACKGROUND_COLOR)

        # Bandeau de titre
        pygame.draw.rect(screen, PANEL_COLOR, (0, 0, 750, 60))
        title_text = font_title.render("SYSTEM MASTER CONTROL PANEL", True, THUMB_COLOR)
        screen.blit(title_text, (30, 16))

        # Gestion des Sliders
        angles = []
        for i, slider in enumerate(sliders):
            if not text_tracking_mode:
                slider.handle_event(mouse_pos, mouse_buttons)
            slider.draw(screen, font)
            angles.append(slider.val)

        # --- MODE SUIVI DE TEXTE ---
        if text_tracking_mode:
            angle_waist = math.atan2(text_y, text_x)
            angle_shoulder = -0.3
            
            sliders[0].val = angle_waist
            sliders[1].val = angle_shoulder
            sliders[0].update_thumb_pos()
            sliders[1].update_thumb_pos()
            
            # Envoi à RViz
            marker = Marker()
            marker.header.frame_id = "base_link"
            marker.header.stamp = rospy.Time.now()
            marker.ns = "text_target"
            marker.id = 1
            marker.type = Marker.TEXT_VIEW_FACING
            marker.action = Marker.ADD
            marker.pose.position.x = text_x
            marker.pose.position.y = text_y
            marker.pose.position.z = text_z
            marker.scale.z = 0.08
            marker.color.r = 0.0; marker.color.g = 1.0; marker.color.b = 0.8; marker.color.a = 1.0
            marker.text = user_text
            marker_pub.publish(marker)

        # --- ZONE DE DESSIN INFÉRIEURE ---
        # Ligne de séparation visuelle
        pygame.draw.line(screen, PANEL_COLOR, (30, 410), (720, 410), 2)

        txt_label = font.render("Texte cible :", True, TEXT_COLOR)
        screen.blit(txt_label, (30, 458))
        color_box = THUMB_COLOR if input_active else SLIDER_BG
        pygame.draw.rect(screen, color_box, input_rect, 2, border_radius=4)
        rendered_text = font.render(user_text, True, TEXT_COLOR)
        screen.blit(rendered_text, (input_rect.x + 10, input_rect.y + 7))

        # Dessin du bouton
        btn_color = BUTTON_ACTIVE if text_tracking_mode else BUTTON_COLOR
        pygame.draw.rect(screen, btn_color, button_rect, border_radius=4)
        btn_label = "SUIVI ACTIF" if text_tracking_mode else "SUIVRE TEXTE"
        txt_btn = font.render(btn_label, True, BACKGROUND_COLOR if text_tracking_mode else TEXT_COLOR)
        screen.blit(txt_btn, (button_rect.x + 20, button_rect.y + 7))

        # Envoi des positions
        joint_state = JointState()
        joint_state.header = Header()
        joint_state.header.stamp = rospy.Time.now()
        joint_state.name = ['waist_joint', 'shoulder_joint', 'elbow_joint', 'wrist_joint', 'joint_5', 'joint_6']
        joint_state.position = angles
        joint_pub.publish(joint_state)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()