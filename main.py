import sys
from machineclient import MachineClient as MC


def main(args):
    if len(args) != 2:
        show_usage()
        return 1

    print("args:", args)
    pgm_data = {}

    try:
        with open(args[1]) as f:
            parse_file(f, pgm_data)
    except OSError as err:
        print(f"Error: {err}.")
        return 1

    run_program(pgm_data)
    return 0


def run_program(pgm_data):
    machine = MC()
    display_program_info(pgm_data)

    for i, block in enumerate(pgm_data["commands"], start=1):
        display_block_info(i, block)
        execute_block(machine, block)


def display_program_info(pgm_data):
    print(f"Running the G-code program #{pgm_data['pgm_num']} "
          f"(total {pgm_data['num_commands']} commands).\n")


def display_block_info(i_block, block):
    command_count = len(block)
    print(f"Executing code block #{i_block} ({command_count} command{'s' if command_count > 1 else ''})")
    print("-" * 50)


def execute_block(machine, block):
    for command in block:
        print(command)
        execute_command(machine, command)


def execute_command(machine, cmd_data):
    command_map = {
        "G": handle_g_command,
        "M": handle_m_command,
        "T": handle_t_command,
        "S": handle_s_command,
    }

    cmd = cmd_data["cmd"]
    cmd_num = cmd[1:]

    handler = command_map.get(cmd[0])
    if handler:
        handler(machine, cmd_num, cmd_data.get("params"))
    else:
        print(f"Unknown command {cmd}")


def handle_g_command(machine, cmd_num, params):
    G_COMMANDS = {
        "00": machine.rapid_move,
        "01": machine.lin_move,
        "02": lambda p: machine.arc_move(p, clockwise=True),
        "03": lambda p: machine.arc_move(p, clockwise=False),
        "17": machine.set_plane_xy,
        "18": machine.set_plane_zx,
        "19": machine.set_plane_yz,
        "20": machine.set_unit_inch,
        "21": machine.set_unit_mm,
        "28": machine.home,
        "40": machine.set_cutter_comp_off,
        "49": machine.cancel_tool_length_comp,
        "54": machine.set_coord_system,
        "55": machine.set_coord_system,
        "56": machine.set_coord_system,
        "57": machine.set_coord_system,
        "58": machine.set_coord_system,
        "59": machine.set_coord_system,
        "80": machine.cancel_canned_cycle,
        "90": machine.set_dist_mode_abs,
        "91": machine.set_dist_mode_inc,
        "93": machine.set_feed_rate_mode_invtime,
        "94": machine.set_feed_rate_mode_upmin,
        "95": machine.set_feed_rate_mode_uprev,
    }
    if cmd_num in G_COMMANDS:
        G_COMMANDS[cmd_num](params)


def handle_m_command(machine, cmd_num, params):
    M_COMMANDS = {
        "03": machine.set_spindle_mode_cw,
        "04": machine.set_spindle_mode_ccw,
        "05": machine.set_spindle_mode_halt,
        "06": machine.manual_tool_change,
        "07": machine.coolant_on,
        "08": machine.coolant_on,
        "09": machine.coolant_off,
        "30": machine.program_end,
    }
    if cmd_num in M_COMMANDS:
        M_COMMANDS[cmd_num](params)


def handle_t_command(machine, cmd_num, params):
    machine.change_tool(f"TOOL #{cmd_num}")


def handle_s_command(machine, cmd_num, params):
    machine.set_spindle_speed(int(cmd_num))


def parse_file(f_obj, pgm_data):
    if not check_markers(f_obj):
        return

    pgm_data["commands"] = []
    pgm_data["num_commands"] = 0

    for txt_row in f_obj:
        txt_row = txt_row.strip()

        if is_comment(txt_row):
            continue

        pgm_num = get_program_number(txt_row)
        if pgm_num > 0:
            if pgm_data.get("pgm_num") is not None:
                print("Error: multiple program numbers found.")
                return
            pgm_data["pgm_num"] = pgm_num
            continue

        get_commands(txt_row, pgm_data)


def get_commands(txt_row, pgm_data):
    command_codes = {"G", "T", "S", "M"}
    parameter_codes = {"X", "Y", "Z", "F", "I", "J"}
    parts = txt_row.upper().split()
    codes = []
    num_commands = 0
    gcode_seen = False
    i = 0

    while i < len(parts):
        if parts[i][0] == "N":
            i += 1
            continue
        if gcode_seen and parts[i][0] in parameter_codes:
            if not codes[-1].get("params"):
                codes[-1]["params"] = []
            codes[-1]["params"].append(parts[i])
            i += 1
            continue
        if parts[i][0] in command_codes:
            if parts[i][0] == "G":
                gcode_seen = True
            codes.append({"cmd": parts[i]})
            num_commands += 1
        i += 1

    if codes:
        pgm_data["commands"].append(codes)
        pgm_data["num_commands"] += num_commands


def check_markers(f_obj):
    markers_seen = sum(1 for txt_row in f_obj if is_marker(txt_row))
    f_obj.seek(0)

    if markers_seen != 2:
        print(f"Error: invalid number of data markers ({markers_seen}, should have 2)")
        return False
    return True


def is_marker(txt_row):
    return txt_row.startswith("%")


def is_comment(txt_row):
    return len(txt_row) > 1 and txt_row.startswith("(") and txt_row.endswith(")")


def get_program_number(txt_row):
    if len(txt_row) < 2 or txt_row[0] != "O":
        return -9999
    try:
        return int(txt_row[1:])
    except ValueError:
        return -9999


def show_usage():
    print('Error: G-code file missing.')
    print('Usage: ./main.py <filename>')


if __name__ == '__main__':
    sys.exit(main(sys.argv))
