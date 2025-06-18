#include <LegControl.h>  // your existing servo handling library

#define NUM_LEGS 4
#define NUM_JOINTS 3
#define TOTAL_JOINTS (NUM_LEGS * NUM_JOINTS)
#define INTERPOLATION_STEPS 50
#define STEP_DELAY 100  // ms between steps

int currentAngles[NUM_LEGS][NUM_JOINTS] = {
  {105, -60, 0},  // Leg 0
  {105, -60, 0},
  {105, -60, 0},
  {105, -60, 0}
};

void setup() {
  Serial.begin(9600);
  while (!Serial);
  Serial.println("Ready to receive joint angles...");
  initializeLeg();  // Your function to attach and configure all servos
}

// Easing function for smooth motion (cosine ease-in-out)
float easeInOut(float t) {
  return 0.5 * (1 - cos(t * PI));
}

void loop() {
  static bool receiving = false;
  static String inputString = "";

  while (Serial.available()) {
    char ch = Serial.read();

    if (ch == '<') {
      receiving = true;
      inputString = "";
    }

    else if (ch == '>' && receiving) {
      receiving = false;

      int values[TOTAL_JOINTS];
      int index = 0;
      char* token = strtok((char*)inputString.c_str(), ",");

      while (token != NULL && index < TOTAL_JOINTS) {
        values[index++] = atoi(token);
        token = strtok(NULL, ",");
      }

      if (index == TOTAL_JOINTS) {
        int targetAngles[NUM_LEGS][NUM_JOINTS];
        int k = 0;
        for (int i = 0; i < NUM_LEGS; i++) {
          targetAngles[i][KNEE_JOINT]     = values[k++];
          targetAngles[i][HIP_LEG_JOINT]  = values[k++];
          targetAngles[i][HIP_BODY_JOINT] = values[k++];
        }

        // Interpolate smoothly from current to target
        for (int step = 0; step <= INTERPOLATION_STEPS; step++) {
          float t = (float)step / INTERPOLATION_STEPS;
          float eased = easeInOut(t);

          for (int leg = 0; leg < NUM_LEGS; leg++) {
            for (int joint = 0; joint < NUM_JOINTS; joint++) {
              int start = currentAngles[leg][joint];
              int end   = targetAngles[leg][joint];
              int interpolated = start + (end - start) * eased;
              moveLeg(leg, joint, interpolated);
            }
          }
          delay(STEP_DELAY);
        }

        // Update current angles
        for (int leg = 0; leg < NUM_LEGS; leg++) {
          for (int joint = 0; joint < NUM_JOINTS; joint++) {
            currentAngles[leg][joint] = targetAngles[leg][joint];
          }
        }

      } else {
        Serial.println("Invalid angle data.");
      }
    }

    else if (receiving) {
      inputString += ch;
    }
  }
}
