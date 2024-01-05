# -*- coding: utf-8 -*-

import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from math import sin, cos, pi,radians

# 全局變量，用於儲存視角位置
menu_id = None
camera_radius = 10.0
angle_x, angle_y = 0.0, 0.0
mouse_x, mouse_y = 0, 0
left_mouse_down, right_mouse_down = False, False
action_walk, action_run= False, False
walk_cycle = 0
max_walk_cycle = 2000
run_cycle = 0
max_run_cycle = 1000

# 初始化GLUT
def init_glut():
    
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutInitWindowPosition(200, 200)
    
# 初始化材質
def init_material():
    ambient_material = [0.5, 0.5, 0.5, 1.0] # 環境光材質
    diffuse_material = [1.0, 1.0, 1.0, 1.0] # 擴散光材質
    specular_material = [1.0, 1.0, 1.0, 1.0] # 鏡面光材質
    shininess = [50.0] # 鏡面反射指數

    glMaterialfv(GL_FRONT, GL_AMBIENT, ambient_material)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse_material)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular_material)
    glMaterialfv(GL_FRONT, GL_SHININESS, shininess)

# 初始化光源
def init_light():
    light_position0 = [1.0, 1.0, 1.0, 0.0] # 光源位置
    light_position1 = [-1.0, -1.0, -1.0, 0.0] # 光源位置

    ambient_light = [0.2, 0.2, 0.2, 1.0] # 環境光
    diffuse_light = [0.8, 0.8, 0.8, 1.0] # 擴散光
    specular_light = [1.0, 1.0, 1.0, 1.0] # 鏡面光

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)

    glDisable(GL_LIGHT1)
    glLightfv(GL_LIGHT1, GL_POSITION, light_position1)
    glLightfv(GL_LIGHT1, GL_AMBIENT, ambient_light)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, diffuse_light)
    glLightfv(GL_LIGHT1, GL_SPECULAR, specular_light)

# 初始化OpenGL
def init_opengl():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_DEPTH_TEST)
    init_light()
    init_material()
   

def mouse(button, state, x, y):
    global left_mouse_down, right_mouse_down, mouse_x, mouse_y,menu_id
    
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            left_mouse_down = True
            if menu_id:
                glutDestroyMenu(menu_id)
                menu_id = None
            mouse_x, mouse_y = x, y
        elif state == GLUT_UP:
            left_mouse_down = False
    
    if button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            right_mouse_down = True
            if not left_mouse_down: 
                create_menu()               

            mouse_x, mouse_y = x, y 
        elif state == GLUT_UP:
            right_mouse_down = False

# 滑鼠移動事件處理函數
def mouse_motion(x, y):
    global camera_radius, angle_x, angle_y, mouse_x, mouse_y
    
    if left_mouse_down and right_mouse_down:
        # 根据滑鼠移?距离???整 camera_radius
        dy = y - mouse_y
        camera_radius += dy * 0.1
        mouse_x, mouse_y = x, y # 現在的位置要回傳給mouse來算偏移量
    elif left_mouse_down:
        dx, dy = x - mouse_x, y - mouse_y
        angle_x += dy * 0.2
        angle_y += dx * 0.2
        mouse_x, mouse_y = x, y

    glutPostRedisplay()  # 确保??更新

# 更新視角位置
def update_view():
    global angle_x, angle_y, camera_radius
    x = camera_radius * sin(radians(angle_y)) * cos(radians(angle_x))
    y = camera_radius * sin(radians(angle_x))
    z = camera_radius * cos(radians(angle_y)) * cos(radians(angle_x))
    gluLookAt(x, y, z, 0, 0, 0, 0, 1, 0)  
    
# 機器人的部件尺寸和顏色
body_parts = {
    "head": {"size": [0.8, 0.8, 0.8], "color": [0.0, 0.0, 1.0]},  # 膚色
    "torso": {"size": [1.5, 2, 0.5], "color": [0.0, 0.0, 1.0]},  # 藍色
    "upper_arm": {"size": [0.5, 1, 0.5], "color": [0.0, 0.0, 1.0]},  # 灰色
    "lower_arm": {"size": [0.4, 0.8, 0.4], "color": [0.0, 0.0, 1.0]},  # 灰色
    "upper_leg": {"size": [0.6, 1.2, 0.6], "color": [0.0, 0.0, 1.0]},  # 深灰色
    "lower_leg": {"size": [0.5, 1, 0.5], "color": [0.0, 0.0, 1.0]}   # 深灰色
}


def draw_circle(center, radius, segments, color):
     # 設置環境光和擴散光的顏色
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)

    # 設置鏡面光的顏色
    glMaterialfv(GL_FRONT, GL_SPECULAR, color)
    glMaterialfv(GL_FRONT, GL_SHININESS, [100.0])
    glBegin(GL_POLYGON)
    for i in range(segments):
        angle = 2 * pi * i / segments
        glVertex3f(center[0] + cos(angle) * radius, center[1] + sin(angle) * radius,center[2])
    glEnd()

def draw_triangle(center, size, color):
     # 設置環境光和擴散光的顏色
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)

    # 設置鏡面光的顏色
    glMaterialfv(GL_FRONT, GL_SPECULAR, color)
    glMaterialfv(GL_FRONT, GL_SHININESS, [100.0])
    glBegin(GL_TRIANGLES)
    glVertex3f(center[0], center[1] + size / 2,center[2])
    glVertex3f(center[0] - size / 2, center[1] - size / 2,center[2])
    glVertex3f(center[0] + size / 2, center[1] - size / 2,center[2])
    glEnd()

# 畫長方體
def draw_cube(size, color):
    # 設置環境光和擴散光的顏色
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, color)

    # 設置鏡面光的顏色
    glMaterialfv(GL_FRONT, GL_SPECULAR, color)
    glMaterialfv(GL_FRONT, GL_SHININESS, [100.0])

    glPushMatrix()
    glScalef(*size)
    glutSolidCube(1)
    glPopMatrix()

# 畫機器人的部件
def draw_body_part(part, position):
    glPushMatrix()
    glTranslatef(*position)
    draw_cube(body_parts[part]["size"], body_parts[part]["color"])
    glPopMatrix()

def draw_arm(side):
    glPushMatrix()

    arm_offset = body_parts["torso"]["size"][0] / 2 + body_parts["upper_arm"]["size"][0] / 2
    # -1 for left, 1 for right
    # 上臂
    upper_arm_pos = [arm_offset * side, body_parts["torso"]["size"][1] / 4, 0]
    draw_body_part("upper_arm", upper_arm_pos)
    # 下臂
    lower_arm_pos = [arm_offset * side, -body_parts["upper_arm"]["size"][1] / 2, 0]
    if(action_walk):
        glRotatef(-10,1,0,0)  
    if(action_run):
        glRotatef(-70,1,0,0)  
    draw_body_part("lower_arm", lower_arm_pos)
    glPopMatrix()


def draw_leg(side):
    glPushMatrix()

    leg_offset = body_parts["torso"]["size"][1] / 2 + body_parts["upper_leg"]["size"][1] / 2
    leg_distance = body_parts["torso"]["size"][0] / 4
    # -1 for left, 1 for right
    # 大腿
    upper_leg_pos = [leg_distance * side, -leg_offset, 0]
    draw_body_part("upper_leg", upper_leg_pos)
    # 小腿
    lower_leg_pos = [leg_distance * side, -leg_offset - body_parts["upper_leg"]["size"][1], 0]
    if(action_walk):
        glRotatef(5,1,0,0)  
    if(action_run):
        glRotatef(10,1,0,0)  

    draw_body_part("lower_leg", lower_leg_pos)

    glPopMatrix()


# 畫機器人
def draw_robot():
    glPushMatrix()
    if(action_walk):
        glRotatef(5,1,0,0)  
    if(action_run):
        glRotatef(10,1,0,0) 
    # 畫頭部
    head_pos = [0, body_parts["torso"]["size"][1] / 2 + body_parts["head"]["size"][1] / 2, 0]
    draw_body_part("head", head_pos)

    # 畫軀幹
    draw_body_part("torso", [0, 0, 0])

    # 畫眼睛
    eye_color = [1.0, 1.0, 1.0]
    eye_radius = 0.05
    eye_distance = 0.2
    eye_y_position = head_pos[1] + 0.1
    draw_circle([head_pos[0] - eye_distance, eye_y_position,body_parts["head"]["size"][2] / 2+0.01], eye_radius, 32, eye_color)
    draw_circle([head_pos[0] + eye_distance, eye_y_position,body_parts["head"]["size"][2] / 2+0.01], eye_radius, 32, eye_color)

    # 畫嘴巴
    mouth_color = [1.0, 1.0, 1.0]
    mouth_size = 0.1
    mouth_y_position = head_pos[1] - 0.1
    draw_triangle([head_pos[0], mouth_y_position, body_parts["head"]["size"][2] / 2+0.01], mouth_size, mouth_color)

    
    # 畫上臂、下臂、大腿、小腿
    if(not action_walk and not action_run):
        for side in [-1,1]:
            draw_arm(side)        
        for side in [-1,1]:
            draw_leg(side)

    glPopMatrix()
    
def draw_robot_walking():
    # 走路動作的參數
    global walk_cycle, max_walk_cycle
    leg_swing_angle = 30  # 腿部擺動的最大角度
    arm_swing_angle = 20  # 手臂擺動的最大角度
       
    # 根據走路周期計算腿部和手臂的擺動角度
    leg_angle = leg_swing_angle * sin(walk_cycle * 2 * pi / max_walk_cycle)
    arm_angle = arm_swing_angle * sin(walk_cycle * 2 * pi / max_walk_cycle)

    glPushMatrix()
    glRotatef(leg_angle, 1, 0, 0)  # 根據計算出的角度旋轉左腿
    draw_leg(-1)  # 您的函數來繪製左腿
    glPopMatrix()

    # 更新右腿 - 可能與左腿相反的擺動
    glPushMatrix()
    glRotatef(-leg_angle, 1, 0, 0)  # 相反角度
    draw_leg(1)  # 繪製右腿
    glPopMatrix()

    glPushMatrix()
    glRotatef(-arm_angle, 1, 0, 0)  
    draw_arm(-1)  
    glPopMatrix()

    glPushMatrix()
    glRotatef(arm_angle, 1, 0, 0)  
    draw_arm(1)  
    glPopMatrix()


def draw_robot_running():
    # 走路動作的參數
    global run_cycle, max_run_cycle
    leg_swing_angle = 45  # 腿部??的角度
    arm_swing_angle = 35  # 手臂??的角度  
       
    # 根據走路周期計算腿部和手臂的擺動角度
    leg_angle = leg_swing_angle * sin(run_cycle * 2 * pi / max_run_cycle)
    arm_angle = arm_swing_angle * sin(run_cycle * 2 * pi / max_run_cycle)

    glPushMatrix()
    glRotatef(leg_angle, 1, 0, 0)  # 根據計算出的角度旋轉左腿
    draw_leg(-1)  # 您的函數來繪製左腿
    glPopMatrix()

    # 更新右腿 - 可能與左腿相反的擺動
    glPushMatrix()
    glRotatef(-leg_angle, 1, 0, 0)  # 相反角度
    draw_leg(1)  # 繪製右腿
    glPopMatrix()

    glPushMatrix()
    glRotatef(-arm_angle, 1, 0, 0)  # 根據計算出的角度旋轉左腿
    draw_arm(-1)  # 您的函數來繪製左腿
    glPopMatrix()

    # 更新右腿 - 可能與左腿相反的擺動
    glPushMatrix()
    glRotatef(arm_angle, 1, 0, 0)  # 相反角度
    draw_arm(1)  # 繪製右腿
    glPopMatrix()

# 主顯示函數
def display():
    global camera_pos, walk_cycle, max_walk_cycle,run_cycle,max_run_cycle
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    update_view()

    # 畫機器人
    
    if action_walk:
        draw_robot_walking()
        walk_cycle += 1
        if walk_cycle >= max_walk_cycle:
            walk_cycle = 0
        glutPostRedisplay()
    if action_run:
        draw_robot_running()  
        run_cycle += 1
        if run_cycle >= max_run_cycle:
            run_cycle = 0
        glutPostRedisplay()
   
    draw_robot()

    glutSwapBuffers()

def reshape(width, height):
    # 防止除以零的錯誤
    if height == 0:
        height = 1

    # 設定視口尺寸
    glViewport(0, 0, width, height)

    # 切換到投影矩陣模式，重置投影矩陣
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    # 設定透視投影
    aspect_ratio = width / height
    gluPerspective(45.0, aspect_ratio, 0.1, 100.0)

    # 切換回模型視圖矩陣模式
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def main_menu(option):#for create_menu
    if option == 0:
        glutDestroyWindow(win)
        sys.exit()

def menu_light(value):
    if value == 1:
        glEnable(GL_LIGHT0)
    elif value == 2:
        glDisable(GL_LIGHT0)
    elif value == 3:
        glEnable(GL_LIGHT1)
    elif value == 4:
        glDisable(GL_LIGHT1)
    glutPostRedisplay()

def menu_light_SEL(value):
    pass

def menu_action(value):
    global action_walk, action_run
    if value == 1:
        action_run = False
        action_walk = False
    elif value == 2:
        action_walk = True
        action_run = False
    elif value == 3:
        action_run = True
        action_walk = False
    glutPostRedisplay()

def create_menu():
    global menu_id
    submenu0 = glutCreateMenu(menu_light)
    glutAddMenuEntry("ON", 1)
    glutAddMenuEntry("OFF", 2)
    submenu1 = glutCreateMenu(menu_light)
    glutAddMenuEntry("ON", 3)
    glutAddMenuEntry("OFF", 4)
    submenu2 = glutCreateMenu(menu_light_SEL)
    glutAddSubMenu("LIGHTING-0", submenu0)
    glutAddSubMenu("LIGHTING-1", submenu1)
    submenu3 = glutCreateMenu(menu_action)
    glutAddMenuEntry("STOP", 1)
    glutAddMenuEntry("WALK", 2)
    glutAddMenuEntry("RUN", 3)

    menu_id = glutCreateMenu(main_menu) #main menu
    glutAddSubMenu("LIGHTING CONTROL", submenu2)
    glutAddSubMenu("ROBOT ACITONS", submenu3)
    glutAddMenuEntry("EXIT", 0)

    glutAttachMenu(GLUT_RIGHT_BUTTON)


# 主函數
init_glut()
win = glutCreateWindow(b"S11059006")
init_opengl()
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutMouseFunc(mouse)
glutMotionFunc(mouse_motion)
 
    
glutMainLoop()




