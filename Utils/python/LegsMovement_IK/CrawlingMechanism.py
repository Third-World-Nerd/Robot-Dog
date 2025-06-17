import os
import sys
import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import serial



# Add the parent directory to the system path
config_dir = os.path.abspath(os.path.join(__file__, "../../../.."))
sys.path.append(config_dir)

# Import the config module
from config import BAUD_RATE_SEND
from config import SERIAL_PORT_SEND

try:
    ser = serial.Serial(SERIAL_PORT_SEND, BAUD_RATE_SEND, timeout=1)
    time.sleep(2)
except Exception as e:
    ser = None
    print(f"⚠️ Could not connect to serial port: {e}")



LEG1 = 100
LEG2 = 156
PIVOTx = 30
PIVOTy = 150
START = (50, -25)
STEP_LENGTH = 100


class WalkingMechanism:

    def __init__(self, arm1, arm2, pivotX, pivotY, start, step_length, ax, fig, offset):
        self.arm1 = arm1
        self.arm2 = arm2
        self.pivotX = pivotX
        self.pivotY = pivotY
        self.x0, self.y0 = start[0], start[1]
        self.step_length = step_length
        self.ax = ax
        self.is_animating = False
        self.fig = fig
        self.offset = offset
        self.current_phase = 0

        self.cycloidal_between()


    def subplots(self, x, y, pX, pY):

        self.ax.clear()
        self.ax.plot([pX, self.elbowX], [pY, self.elbowY], 'ro-', linewidth=4, label='Arm')
        self.ax.plot([self.elbowX, self.wristX], [self.elbowY, self.wristY], 'ro-', linewidth=4)
        self.ax.plot(x, y, 'gx', markersize=10, label='Foot')
        self.ax.text(0, 180, f"x: {x:.2f}, y: {y:.2f}\nα: {np.rad2deg(self.alpha):.1f}, β: {np.rad2deg(self.beta):.1f}")
        self.ax.axhline(-25, color='gray', linestyle='--')
        self.ax.set_xlim(-200, 200)
        self.ax.set_ylim(-200, 200)
        self.ax.set_aspect('equal')
        self.ax.legend()
        self.fig.canvas.draw_idle()



    """Cyclodial Path for forward Movement"""
    def cycloidal_between(self, steps=30, lift_ratio=0.5):
        t = np.linspace(0, 1, steps)

        dx, dy = self.step_length, 0
        distance = np.hypot(dx, dy)
        height = lift_ratio * distance
        x = self.x0 + dx * (t - (1 / (2 * np.pi)) * np.sin(2 * np.pi * t))
        y_base = self.y0 + dy * t
        y = y_base + height * np.sin(np.pi * t)
        return x, y

    """Bobbing Shape"""
    def stance_phase_fixed_pivot(self, steps=30):
        t = np.linspace(0, 1, steps)
        
        pivot_x = (1 - t) * (self.x0 + self.step_length) + t * self.x0

        vertical_bob = 3 * np.sin(np.pi * t)
        pivot_y = self.y0 + vertical_bob

        return pivot_x, pivot_y


    def ik(self, x, y, pX, pY):
        dx, dy = x - pX, y - pY
        b = np.hypot(dx, dy)
        max_dist = self.arm1 + self.arm2

        if b > max_dist:
            x = pX + dx * max_dist / b
            y = pY + dy * max_dist / b
            dx, dy = x - pX, y - pY
            b = max_dist

        cos_beta = (b**2 - self.arm1**2 - self.arm2**2) / (2 * self.arm1 * self.arm2)
        self.beta = np.arccos(np.clip(cos_beta, -1, 1))
        k1 = self.arm1 + self.arm2 * np.cos(self.beta)
        k2 = self.arm2 * np.sin(self.beta)
        self.alpha = np.arctan2(dy, dx) - np.arctan2(k2, k1)

        self.elbowX = pX + self.arm1 * np.cos(self.alpha)
        self.elbowY = pY + self.arm1 * np.sin(self.alpha)
        self.wristX = self.elbowX + self.arm2 * np.cos(self.alpha + self.beta)
        self.wristY = self.elbowY + self.arm2 * np.sin(self.alpha + self.beta)

        self.alpha = np.rad2deg(self.alpha)
        self.beta = np.rad2deg(self.beta)
        return [f"{int(self.alpha.item())}", f"{int(self.beta.item())}", f"{0}"]
        # self.subplots(x, y, pX, pY)

    def swing_phase(self):
        swing_x, swing_y = self.cycloidal_between()

        return swing_x, swing_y, self.pivotX, self.pivotY
        # for x, y in zip(swing_x, swing_y):
        #     # x_slider.set_val(x)
        #     # y_slider.set_val(y)
        #     # self.ik(x, y, self.pivotX, self.pivotY)  #ELBOW DOWN
        #     self.ik(self.pivotX, self.pivotY, x, y)   #ELBOW UP
        #     plt.pause(0.01)

        # self.x0 += self.step_length
        # self.y0 = self.y0


    def stance_phase(self):
        stance_pivot_x, stance_pivot_y = self.stance_phase_fixed_pivot()
        return stance_pivot_x, stance_pivot_y, self.pivotX, self.pivotY
        # for px, py in zip(stance_pivot_x, stance_pivot_y):
        #     # x_slider.set_val(self.x0 + s[0])
        #     # y_slider.set_val(end_foot[1])
        #     self.ik(px, py, self.x0, self.y0)      #ELBOW UP
        #     # self.ik(self.x0, self.y0, px, py)   # ELBOW DOWN
        #     plt.pause(0.01)


    def working_pipeline(self, global_step):

        if (global_step + self.offset) % 2 == 0:
            self.swing_phase()

        else:
            self.stance_phase()


class LegMovement():

    def __init__(self, legs):
        self.legs = legs


    def start(self):


        steps = 0
        # mylst = []


        while 1:
            current_phase = steps%4
            a, b, c, d = current_phase, (current_phase+1)%4, (current_phase+2)%4, (current_phase+3)%4
        # Swing Phase
            firstLegswingX, firstLegswingY, firstpivotX, firstpivotY = self.legs[a].swing_phase()
            # Stance Phase
            secondLegswingX, secondLegswingY, secondpivotX, secondpivotY = self.legs[b].stance_phase()
            thirdLegswingX, thirdLegswingY, thirdpivotX, thirdpivotY = self.legs[c].stance_phase()
            fourthLegswingX, fourthLegswingY, fourthpivotX, fourthpivotY = self.legs[d].stance_phase()

            for (a1, b1, a2, b2, a3, b3, a4, b4) in zip(firstLegswingX, firstLegswingY, secondLegswingX, secondLegswingY, thirdLegswingX, thirdLegswingY, fourthLegswingX, fourthLegswingY):

                mylst = [None] * 4

                angles_a = self.legs[a].ik(a1, b1, firstpivotX, firstpivotY)
                angles_b = self.legs[b].ik(a2, b2, secondpivotX, secondpivotY)
                angles_c = self.legs[c].ik(a3, b3, thirdpivotX, thirdpivotY)
                angles_d = self.legs[d].ik(a4, b4, fourthpivotX, fourthpivotY)

                mylst[a] = angles_a
                mylst[b] = angles_b
                mylst[c] = angles_c
                mylst[d] = angles_d

                mine_list = [angle for leg_angles in mylst for angle in leg_angles]
                command = f"<{','.join(mine_list)}>"
                print(f"{command}")

                if ser and ser.is_open:
                    try:
                        ser.write(command.encode())
                        now = datetime.now()
                        minute = now.strftime("%M")
                        second = now.strftime("%S")
                        millisecond = int(now.microsecond / 1000)
                        print(f"Sent: {minute}:{second}:{millisecond}:- {command}")
                    except Exception as e:
                        print(f"Serial error: {e}")
                else:

                    print(f"Error: Serial port {SERIAL_PORT_SEND} not available")

            steps += 1




fig, ax = plt.subplots(2, 2)
wm = [WalkingMechanism(LEG1, LEG2, PIVOTx, PIVOTy, START, STEP_LENGTH, ax[0][0], fig, 0),
      WalkingMechanism(LEG1, LEG2, PIVOTx, PIVOTy, START, STEP_LENGTH, ax[0][1], fig, 1),
      WalkingMechanism(LEG1, LEG2, PIVOTx, PIVOTy, START, STEP_LENGTH, ax[1][0], fig, 1),
      WalkingMechanism(LEG1, LEG2, PIVOTx, PIVOTy, START, STEP_LENGTH, ax[1][1], fig, 0),
    ]


Lm = LegMovement(wm)
Lm.start()


