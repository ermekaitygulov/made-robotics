#!/usr/bin/env python


class PID:

    # TODO: Complete the PID class. You may add any additional desired functions

    def __init__(self, Kp, Ki=0.0, Kd=0.0):
        # TODO: Initialize PID coefficients (and errors, if needed)
        self.kp = Kp
        self.ki = Ki
        self.kd = Kd
        self.p = 0
        self.i = 0
        self.d = 0

    def UpdateError(self, cte):
        # TODO: Update PID errors based on cte
        self.d = cte - self.kp
        self.p = cte
        self.i += cte

    def TotalError(self):
        # TODO: Calculate and return the total error
        return - self.kp * self.p - self.ki * self.i - self.kd * self.d
