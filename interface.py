import math
import tkinter as tk
from tkinter import filedialog, messagebox
from machineclient import MachineClient
from main import parse_file, execute_command, check_markers

class CNCVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("CNC Visualizer")

        # Create main frame with canvas and controls
        self.canvas = tk.Canvas(root, width=800, height=600, bg="gray70")
        self.canvas.grid(row=0, column=1, rowspan=3, sticky="nsew")

        self.control_frame = tk.Frame(root)
        self.control_frame.grid(row=0, column=0, sticky="n")

        # G-code related controls
        self.load_button = tk.Button(self.control_frame, text="Load G-Code", command=self.load_file)
        self.load_button.pack(pady=10)

        self.run_button = tk.Button(self.control_frame, text="Run Program", command=self.run_program, state=tk.DISABLED)
        self.run_button.pack(pady=10)

        # Navigation controls
        self.move_frame = tk.Frame(self.control_frame)
        self.move_frame.pack(pady=20)

        self.up_button = tk.Button(self.move_frame, text="Up", command=lambda: self.move_canvas(0, -20))
        self.up_button.grid(row=0, column=1)

        self.left_button = tk.Button(self.move_frame, text="Left", command=lambda: self.move_canvas(-20, 0))
        self.left_button.grid(row=1, column=0)

        self.right_button = tk.Button(self.move_frame, text="Right", command=lambda: self.move_canvas(20, 0))
        self.right_button.grid(row=1, column=2)

        self.down_button = tk.Button(self.move_frame, text="Down", command=lambda: self.move_canvas(0, 20))
        self.down_button.grid(row=2, column=1)

        # Zoom controls
        self.zoom_in_button = tk.Button(self.control_frame, text="Zoom In", command=self.zoom_in)
        self.zoom_in_button.pack(pady=10)

        self.zoom_out_button = tk.Button(self.control_frame, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_button.pack(pady=10)

        # MachineClient integration
        self.machine = MachineClient()
        self.pgm_data = {}
        self.current_pos = {"x": 400, "y": 300, "z": 0}
        self.scale_factor = 10
        self.bounds = {"x_min": None, "x_max": None, "y_min": None, "y_max": None}
        self.canvas_offset = {"x": 0, "y": 0}

        # Status display
        self.status_frame = tk.Frame(root)
        self.status_frame.grid(row=1, column=0, sticky="ew")

        self.status_label = tk.Label(self.status_frame, text="Status: Idle", anchor="w")
        self.status_label.pack(fill=tk.X)

    def update_status(self, message):
        self.status_label.config(text=f"Status: {message}")

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("G-Code Files", "*.txt *.nc *.gcode")])
        if not filepath:
            return
        try:
            with open(filepath) as f:
                if not check_markers(f):
                    raise ValueError("Invalid G-code file markers.")
                parse_file(f, self.pgm_data)

            self.calculate_bounds()
            messagebox.showinfo("Success", f"Loaded {len(self.pgm_data['commands'])} command blocks.")
            self.run_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load G-code file: {e}")

    def run_program(self):
        self.current_pos = {"x": 400, "y": 300, "z": 0}
        self.canvas.delete("all")
        self.update_status("Running program...")

        for block in self.pgm_data["commands"]:
            for command in block:
                try:
                    self.execute_visual_command(command)
                except Exception as e:
                    print(f"Error while executing command {command}: {e}")
        self.update_status("Program finished.")

    def execute_visual_command(self, cmd_data):
        cmd = cmd_data["cmd"]
        params = cmd_data.get("params", [])

        if cmd in ["G00", "G01"]:  # Movement commands
            self.handle_movement(cmd, params)
        elif cmd in ["G02", "G03"]:  # Arc commands
            self.handle_arc(cmd, params)
        elif cmd == "G92":  # Set offset command
            self.handle_offset(params)
        execute_command(self.machine, cmd_data)

    def handle_movement(self, cmd, params):
        x, y, z = self.current_pos["x"], self.current_pos["y"], self.current_pos["z"]

        for param in params:
            if param.startswith("X"):
                x = (float(param[1:]) - self.bounds["x_min"]) * self.scale_factor + self.canvas_offset["x"]
            elif param.startswith("Y"):
                y = (float(param[1:]) - self.bounds["y_min"]) * self.scale_factor + self.canvas_offset["y"]
            elif param.startswith("Z"):
                z = float(param[1:])

        if cmd == "G01":  # Linear movement
            self.canvas.create_line(
                self.current_pos["x"], self.current_pos["y"], x, y, fill="steel blue", width=2
            )

        self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="brown4")  # Mark position
        self.current_pos["x"], self.current_pos["y"], self.current_pos["z"] = x, y, z

    def handle_arc(self, cmd, params):
        x, y = self.current_pos["x"], self.current_pos["y"]
        i = j = None

        for param in params:
            if param.startswith("X"):
                x = (float(param[1:]) - self.bounds["x_min"]) * self.scale_factor + self.canvas_offset["x"]
            elif param.startswith("Y"):
                y = (float(param[1:]) - self.bounds["y_min"]) * self.scale_factor + self.canvas_offset["y"]
            elif param.startswith("I"):
                i = float(param[1:]) * self.scale_factor
            elif param.startswith("J"):
                j = float(param[1:]) * self.scale_factor

        if i is not None and j is not None:
            # Calculate center of the arc
            cx = self.current_pos["x"] + i
            cy = self.current_pos["y"] + j

            # Calculate radius
            radius = math.sqrt(i ** 2 + j ** 2)

            # Calculate start and end angles
            start_angle = self.calculate_angle(cx, cy, self.current_pos["x"], self.current_pos["y"])
            end_angle = self.calculate_angle(cx, cy, x, y)

            # Determine the extent of the arc
            if cmd == "G02":  # Clockwise
                extent = (end_angle - start_angle) % 360
            else:  # Counterclockwise
                extent = (start_angle - end_angle) % 360

            # Debugging information
            print(f"Debug: Arc center=({cx}, {cy}), start_angle={start_angle}, end_angle={end_angle}, extent={extent}")

            # Draw the arc
            self.canvas.create_arc(
                cx - radius, cy - radius, cx + radius, cy + radius,
                start=start_angle, extent=extent, style=tk.ARC, outline="steel blue", width=2
            )

        self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="brown4")  # Mark position
        self.current_pos["x"], self.current_pos["y"] = x, y

    def calculate_angle(self, cx, cy, x, y):
        angle = math.degrees(math.atan2(y - cy, x - cx))
        return (360 + angle) % 360

    def handle_offset(self, params):
        for param in params:
            axis = param[0]
            value = float(param[1:])
            if axis == "X":
                self.current_pos["x"] = (value - self.bounds["x_min"]) * self.scale_factor + self.canvas_offset["x"]
            elif axis == "Y":
                self.current_pos["y"] = (value - self.bounds["y_min"]) * self.scale_factor + self.canvas_offset["y"]
            elif axis == "Z":
                self.current_pos["z"] = value

    def calculate_bounds(self):
        x_coords = []
        y_coords = []

        for block in self.pgm_data["commands"]:
            for cmd in block:
                params = cmd.get("params", [])
                for param in params:
                    if param.startswith("X"):
                        x_coords.append(float(param[1:]))
                    if param.startswith("Y"):
                        y_coords.append(float(param[1:]))

        if x_coords and y_coords:
            self.bounds["x_min"] = min(x_coords)
            self.bounds["x_max"] = max(x_coords)
            self.bounds["y_min"] = min(y_coords)
            self.bounds["y_max"] = max(y_coords)

            x_range = self.bounds["x_max"] - self.bounds["x_min"]
            y_range = self.bounds["y_max"] - self.bounds["y_min"]

            if x_range > 0 and y_range > 0:
                self.scale_factor = min(700 / x_range, 500 / y_range)

    def zoom_in(self):
        self.scale_factor *= 1.2
        self.redraw_canvas()

    def zoom_out(self):
        self.scale_factor /= 1.2
        self.redraw_canvas()

    def move_canvas(self, dx, dy):
        self.canvas_offset["x"] += dx
        self.canvas_offset["y"] += dy
        self.redraw_canvas()

    def redraw_canvas(self):
        self.canvas.delete("all")
        self.run_program()

if __name__ == "__main__":
    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    app = CNCVisualizer(root)
    root.mainloop()