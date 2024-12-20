# Constant value definitions for parameters.
UNDEFINED = 0
PLANE_XY = 1
PLANE_ZX = 2
PLANE_YZ = 3
PLANE_UV = 4
PLANE_WU = 5
PLANE_VW = 6
SPINDLE_MODE_CW = 7
SPINDLE_MODE_CCW = 8
SPINDLE_MODE_HALT = 9
MOTION_MODE_RAPID = 10
MOTION_MODE_LINEAR = 11
UNIT_MM = 12
UNIT_INCH = 13
DIST_MODE_ABS = 14
DIST_MODE_INC = 15
FEED_MODE_INVTIME = 16
FEED_MODE_UPMIN = 17
FEED_MODE_UPREV = 18

# Descriptive texts for the parameters.
NAMES = [
    "UNDEFINED",
    "X/Y", "X/Z", "Y/Z", "U/V", "W/U", "V/W",
    "CLOCKWISE", "COUNTER-CLOCKWISE", "HALT",
    "RAPID", "LINEAR",
    "MILLIMETRES", "INCHES",
    "ABSOLUTE", "INCREMENTAL",
    "INVERSE TIME", "UNITS/MIN", "UNITS/REV"
]


class MachineClient:
    _plane = UNDEFINED
    _pos = {"x": 0.0, "y": 0.0, "z": 0.0}
    _tool_name = ""
    _spindle_params = {"is_active": False, "speed": 0, "mode": UNDEFINED}
    _feed_rate_params = {"rate": 0, "mode": UNDEFINED}
    _coolant_on = False
    _unit = UNDEFINED
    _dist_mode = UNDEFINED
    _motion_mode = UNDEFINED

    def __init__(self):
        self.statusprint("CNC machine initializing.")

    def __del__(self):
        """ Displays a message on MachineClient deletion. """
        self.statusprint("CNC machine shutting down.")

    def rapid_move(self, params):
        self._motion_mode = MOTION_MODE_RAPID

        if params is None:
            self.statusprint("Setting motion mode to {}".format(NAMES[self._motion_mode]))
            return

        new_x = self._pos["x"]
        new_y = self._pos["y"]
        new_z = self._pos["z"]

        for par in params:
            if par[0] == "X":
                new_x = float(par[1: len(par)])
            if par[0] == "Y":
                new_y = float(par[1: len(par)])
            if par[0] == "Z":
                new_z = float(par[1: len(par)])

        self.move(new_x, new_y, new_z)

    def lin_move(self, params):
        self._motion_mode = MOTION_MODE_LINEAR
        if (params is None):
            self.statusprint("Setting motion mode to {}".format(NAMES[self._motion_mode]))
            return
        new_x = self._pos["x"]
        new_y = self._pos["y"]
        new_z = self._pos["z"]
        for par in params:
            if par[0] == "F":
                self.set_feed_rate(float(par[1: len(par)]))
            if par[0] == "X":
                new_x = float(par[1: len(par)])
            if par[0] == "Y":
                new_y = float(par[1: len(par)])
            if par[0] == "Z":
                new_z = float(par[1: len(par)])
        self.move(new_x, new_y, new_z)

    def arc_move(self, params, clockwise):
        if not params:
            self.statusprint("Arc move command received without parameters.")
            return

        # Extract parameters
        x = self._pos["x"]
        y = self._pos["y"]
        z = self._pos["z"]
        i = j = r = None  # Arc center offsets or radius
        for param in params:
            if param[0] == "X":
                x = float(param[1:])
            elif param[0] == "Y":
                y = float(param[1:])
            elif param[0] == "Z":
                z = float(param[1:])
            elif param[0] == "I":
                i = float(param[1:])
            elif param[0] == "J":
                j = float(param[1:])
            elif param[0] == "R":
                r = float(param[1:])

        # Calculate center
        if i is not None and j is not None:
            cx = self._pos["x"] + i
            cy = self._pos["y"] + j
        elif r is not None:
            raise NotImplementedError("Radius-based arc not implemented yet.")
        else:
            self.statusprint("Error: Arc move requires either I/J or R parameters.")
            return

        # Perform arc movement
        self.statusprint(
            f"Moving in an {'clockwise' if clockwise else 'counter-clockwise'} arc to X={x}, Y={y} with center ({cx}, {cy}).")
        self._pos.update({"x": x, "y": y, "z": z})

    def set_plane_xy(self, params={}):
        self._plane = PLANE_XY
        self.statusprint("Plane set to {}".format(NAMES[self._plane]))

    def set_plane_zx(self, params={}):
        self._plane = PLANE_ZX
        self.statusprint("Plane set to {}".format(NAMES[self._plane]))

    def set_plane_yz(self, params={}):
        self._plane = PLANE_YZ
        self.statusprint("Plane set to {}".format(NAMES[self._plane]))

    def set_unit_mm(self, params={}):
        self._unit = UNIT_MM
        self.statusprint("Unit of measure set to {}"
                         .format(NAMES[self._unit]))

    def set_unit_inch(self, params={}):
        self._unit = UNIT_INCH
        self.statusprint("Unit of measure set to {}"
                         .format(NAMES[self._unit]))

    def set_cutter_comp_off(self, params={}):
        self.statusprint("Cutter compensation turned OFF")


    def cancel_tool_length_comp(self, params={}):
        self.statusprint("Tool length compensation CANCELED")

    def cancel_canned_cycle(self, params={}):
        self.statusprint("Canned cycles CANCELED")


    def set_feed_rate_mode_upmin(self, params={}):
        self._feed_rate_params["mode"] = FEED_MODE_UPMIN
        self.statusprint("Feed rate mode set to {}"
                         .format(NAMES[self._feed_rate_params["mode"]]))

    def set_feed_rate_mode_invtime(self, params={}):
        self._feed_rate_params["mode"] = FEED_MODE_INVTIME
        self.statusprint("Feed rate mode set to {}"
                         .format(NAMES[self._feed_rate_params["mode"]]))

    def set_feed_rate_mode_uprev(self, params={}):
        self._feed_rate_params["mode"] = FEED_MODE_UPREV
        self.statusprint("Feed rate mode set to UNITS/REVOLUTION"
                         .format(self._feed_rate_params["mode"]))

    def home(self, params):
        if self._motion_mode == DIST_MODE_INC:
            for par in params:
                amount = float(par[1: len(par)])
                if par[0] == "X":
                    self.move_x(self._pos["x"] + amount)
                if par[0] == "Y":
                    self.move_y(self._pos["y"] + amount)
                if par[0] == "Z":
                    self.move_z(self._pos["z"] + amount)

        elif (self._motion_mode == DIST_MODE_ABS):
            for par in params:
                amount = float(par[1: len(par)])
                if par[0] == "X":
                    self.move_x(amount)
                if par[0] == "Y":
                    self.move_y(amount)
                if par[0] == "Z":
                    self.move_z(amount)

        # Homing.
        self.statusprint("Moving selected axes to home.")
        for par in params:
            if par[0] == "Z":
                self.move_z(0.0)
            if par[0] == "X":
                self.move_x(0.0)
            if par[0] == "Y":
                self.move_y(0.0)

    def move(self, x, y, z):
        if self._dist_mode == DIST_MODE_INC:
            new_x = self._pos["x"] + x
            new_y = self._pos["y"] + y
            new_z = self._pos["z"] + z

        elif self._dist_mode == DIST_MODE_ABS:
            new_x = x
            new_y = y
            new_z = z

        else:
            self.statusprint("move(): Error, distance mode not set.")
            return

        self.statusprint("Moving to X={:.3f} Y={:.3f} Z={:.3f} [{}]."
                         .format(new_x, new_y, new_z, NAMES[self._unit]))

        if self._motion_mode == MOTION_MODE_LINEAR:
            rate = self._feed_rate_params["rate"]
            mode = self._feed_rate_params["mode"]
            self.statusprint("Using feed rate F={:.3f} {}".format(rate, NAMES[mode]))

        if (new_z >= self._pos["z"]):
            # Mill bit must raise before changing position.
            if abs(new_z - self._pos["z"]) >= 0.001:
                self.move_z(new_z)
            if abs(new_x - self._pos["x"]) >= 0.001:
                self.move_x(new_x)
            if abs(new_y - self._pos["y"]) >= 0.001:
                self.move_y(new_y)

        else:
            if abs(new_x - self._pos["x"]) >= 0.001:
                self.move_x(new_x)
            if abs(new_y - self._pos["y"]) >= 0.001:
                self.move_y(new_y)
            if abs(new_z - self._pos["z"]) >= 0.001:
                self.move_z(new_z)

    def move_x(self, value):
        self.statusprint("Moving X to {:.3f} [{}]."
                         .format(value, NAMES[self._unit]))
        self._pos["x"] = value

    def move_y(self, value):
        self.statusprint("Moving Y to {:.3f} [{}]."
                         .format(value, NAMES[self._unit]))
        self._pos["y"] = value

    def move_z(self, value):
        self.statusprint("Moving Z to {:.3f} [{}]."
                         .format(value, NAMES[self._unit]))
        self._pos["z"] = value

    def set_feed_rate(self, value):
        """ Sets spindle feed rate.
        Args:
        value (float): Feed rate [mm/s]
        """
        if self._feed_rate_params["mode"] == UNDEFINED:
            self.statusprint("set_feed_rate(): Error, unknown feed rate mode.")
            return

        # "Official" CNC feed rate is units/min
        elif self._feed_rate_params["mode"] == FEED_MODE_UPMIN:
            self._feed_rate_params["rate"] = value * 60.0

        else:
            self.statusprint("set_feed_rate(): Error, feed rate mode not implemented.")
            return

    def set_spindle_speed(self, value):
        if (value < 0):
            self.statusprint("set_spindle_speed(): Error, speed must be non-negative.")
            return

        self._spindle_params["speed"] = value
        self.statusprint("Using spindle speed {} [rpm].".format(value))

    def set_spindle_mode_cw(self, params={}):
        self._spindle_params["mode"] = SPINDLE_MODE_CW
        self._spindle_params["state"] = True

        self.statusprint("Setting spindle mode to {}"
                         .format(NAMES[self._spindle_params["mode"]]))

    def set_spindle_mode_ccw(self, params={}):
        self._spindle_params["mode"] = SPINDLE_MODE_CCW
        self._spindle_params["state"] = True

        self.statusprint("Setting spindle mode to {}"
                         .format(NAMES[self._spindle_params["mode"]]))

    def set_spindle_mode_halt(self, params={}):
        self._spindle_params["mode"] = SPINDLE_MODE_HALT
        self._spindle_params["state"] = False

        self.statusprint("Setting spindle mode to {}"
                         .format(NAMES[self._spindle_params["mode"]]))

    def set_dist_mode_abs(self, params={}):
        """ Sets distance mode to absolute.
        Args:
          params (dict): unused
        """
        self._dist_mode = DIST_MODE_ABS
        self.statusprint("Setting distance mode to {}"
                         .format(NAMES[self._dist_mode]))

    def set_dist_mode_inc(self, params={}):
        self._dist_mode = DIST_MODE_INC
        self.statusprint("Setting distance mode to {}"
                         .format(NAMES[self._dist_mode]))

    def set_coord_system(self, num):
        self.statusprint("Selecting coordinate system #{}".format(num))

    def change_tool(self, tool_name):
        self._tool_name = tool_name
        self.statusprint("Changing tool '{:s}'.".format(self._tool_name))

    def manual_tool_change(self):
        self.statusprint("Manual tool change to '{}' requested".format(self._tool_name))

    def coolant_on(self):
        self.statusprint("Coolant turned on.")
        _coolant_on = True

    def coolant_off(self):
        self.statusprint("Coolant turned off.")
        _coolant_on = False

    def program_end(self):
        self.statusprint("Program end reached.")
        self.set_coord_system(1)
        self.set_plane_xy()
        self.set_dist_mode_abs()
        self.set_feed_rate_mode_upmin()
        self.set_spindle_mode_halt()
        self.lin_move(None)
        self.coolant_off()

    def statusprint(self, message):
        print(4 * "-" + "> ", end="")
        print(message)
