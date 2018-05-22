# Mechanical bed tilt calibration with multiple Z steppers
#
# Copyright (C) 2018  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging

class StepperBuzz:
    def __init__(self, config):
        self.printer = config.get_printer()
        # Register Z_TILT_ADJUST command
        self.gcode = self.printer.lookup_object('gcode')
        self.gcode.register_command(
            'STEPPER_BUZZ', self.cmd_STEPPER_BUZZ,
            desc=self.cmd_STEPPER_BUZZ_help)
    cmd_STEPPER_BUZZ_help = "Oscillate a given stepper to help id it"
    def cmd_STEPPER_BUZZ(self, params):
        # Lookup all configured steppers
        toolhead = self.printer.lookup_object('toolhead')
        all_steppers = {}
        steppers = toolhead.get_kinematics().get_steppers()
        for stepper in steppers:
            all_steppers[stepper.name] = stepper
            if hasattr(stepper, 'extras'):
                for stepper in stepper.extras:
                    all_steppers[stepper.name] = stepper
        # Parse command line
        buzz = self.gcode.get_str('STEPPER', params)
        if buzz not in all_steppers:
            raise self.gcode.error("Unable to find stepper %s" % (buzz,))
        logging.info("Stepper buzz %s", buzz)
        stepper = all_steppers[buzz]
        need_motor_enable = stepper.need_motor_enable
        # Move stepper
        toolhead.wait_moves()
        pos = stepper.mcu_stepper.get_commanded_position()
        print_time = toolhead.get_last_move_time()
        if need_motor_enable:
            stepper.motor_enable(print_time, 1)
            print_time += .1
        for i in range(10):
            stepper.step_const(print_time, pos, 1., 4., 0.)
            print_time += .3
            stepper.step_const(print_time, pos + 1., -1., 4., 0.)
            toolhead.reset_print_time(print_time + .7)
            print_time = toolhead.get_last_move_time()
        if need_motor_enable:
            print_time += .1
            stepper.motor_enable(print_time, 0)
            toolhead.reset_print_time(print_time)

def load_config(config):
    return StepperBuzz(config)
