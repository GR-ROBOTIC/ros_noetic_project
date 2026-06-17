# ==============================================================================
# 1. CRÉATION DU WORKSPACE CATKIN ET DES PACKAGES ROS
# ==============================================================================
# Création de la structure des dossiers
mkdir -p ~/Desktop/ROS_noetic_project/moveit_arm_bot/catkin_ws/src
cd ~/Desktop/ROS_noetic_project/moveit_arm_bot/catkin_ws/src

# Initialisation de l'espace de travail ROS
catkin_init_workspace

# Création du package principal avec ses dépendances indispensables
catkin_create_pkg mon_robot_moveit rospy std_msgs sensor_msgs geometry_msgs moveit_commander moveit_msgs

# Retour à la racine et compilation initiale du workspace
cd ~/Desktop/ROS_noetic_project/moveit_arm_bot/catkin_ws
catkin_make

# Sourcing de l'environnement pour enregistrer les nouveaux packages
source devel/setup.bash


# ==============================================================================
# 2. CONFIGURATION DE L'ASSISTANT MOVEIT & STRUCTURE DES SCRIPTS
# ==============================================================================
# Lancement de l'assistant graphique pour générer le package 'mon_robot_moveit_config'
roslaunch moveit_setup_assistant setup_assistant.launch

# Création du dossier qui va contenir tes scripts de contrôle Python
mkdir -p ~/Desktop/ROS_noetic_project/moveit_arm_bot/catkin_ws/src/mon_robot_moveit/scripts
cd ~/Desktop/ROS_noetic_project/moveit_arm_bot/catkin_ws/src/mon_robot_moveit/scripts/

# Création des fichiers de script vides
touch hand_track_control.py
touch qrcode_vr_track.py
touch slider_control_teste.py


# ==============================================================================
# 3. INSTALLATION DES DÉPENDANCES (SYSTÈME & ANACONDA PYTHON)
# ==============================================================================
# Mise à jour et installation de la bibliothèque système Linux pour les QR Codes
sudo apt-get update
sudo apt-get install -y libzbar0

# Installation de toutes les bibliothèques Python requises dans ton environnement Anaconda
pip install pyzbar
pip install cv-bridge
pip install mediapipe
pip install opencv-python
pip install pygame


# ==============================================================================
# 4. RÉSOLUTION DES CONFLITS D'ENVIRONNEMENT (TROUBLESHOOTING ANACONDA/ROS)
# ==============================================================================
# Lier les paquets Python de ROS Noetic à ton environnement Anaconda
export PYTHONPATH=$PYTHONPATH:/opt/ros/noetic/lib/python3/dist-packages

# Sourcer à nouveau le workspace pour être certain que tout est synchronisé
source ~/Desktop/ROS_noetic_project/moveit_arm_bot/catkin_ws/devel/setup.bash

# Test de validation pour l'import de la bibliothèque de QR Code
python -c "from pyzbar.pyzbar import decode; print('✅ Pyzbar est prêt !')"

# Forcer le chargement de la bonne version de libffi (Supprime l'erreur ffi_type_pointer)
export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libffi.so.7


# ==============================================================================
# 5. GESTION DES FICHIERS ET DROITS D'EXÉCUTION
# ==============================================================================
# Edition du fichier pour corriger le Shebang (#!/usr/bin/env python3) si besoin
nano ~/Desktop/ROS_noetic_project/moveit_arm_bot/catkin_ws/src/mon_robot_moveit/scripts/hand_track_control.py

# Rendre les scripts exécutables par le système Linux
chmod +x ~/Desktop/ROS_noetic_project/moveit_arm_bot/catkin_ws/src/mon_robot_moveit/scripts/hand_track_control.py
chmod +x ~/Desktop/ROS_noetic_project/moveit_arm_bot/catkin_ws/src/mon_robot_moveit/scripts/qrcode_vr_track.py


# ==============================================================================
# 6. LANCEMENT DE LA SIMULATION ET DES DIFFÉRENTS MODES DE CONTRÔLE
# ==============================================================================
# [Terminal 1] : Lancer l'environnement virtuel RViz + MoveIt du robot
roslaunch mon_robot_moveit_config demo.launch

# --- MÉTHODE A : Lancement via ROS (rosrun) ---
rosrun mon_robot_moveit hand_track_control.py
rosrun mon_robot_moveit qrcode_vr_track.py 
rosrun mon_robot_moveit slider_control_teste.py

# --- MÉTHODE B : Lancement en Python direct (Recommandé avec Anaconda) ---
cd ~/Desktop/ROS_noetic_project/moveit_arm_bot/catkin_ws/src/mon_robot_moveit/scripts/
python hand_track_control.py
python qrcode_vr_track.py
python qrcode_vr_3d_screen.py
python slider_control.py
