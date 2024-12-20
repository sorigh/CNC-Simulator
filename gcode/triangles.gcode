
O0001
(TWO STARS PATTERN)
(UNITS: MM, ABSOLUTE POSITIONING)
G21 G90 G17 G40  (Set units to mm, absolute mode, XY plane, no cutter compensation)
G00 Z5.0         (Lift tool to a safe height)

(STAR 1 - TOP LEFT)
G00 X10.0 Y80.0  (Move to starting position of first star)
G01 Z-1.0 F100.0 (Lower tool to cutting depth)
G01 X20.0 Y60.0  (Draw first line)
G01 X0.0  Y60.0  (Draw second line)
G01 X10.0 Y80.0  (Draw third line, completing one arm)
G01 X15.0 Y70.0  (Start inner arm)
G01 X5.0  Y70.0  (Finish inner arm)
G01 X10.0 Y80.0  (Return to center)

(Lift Tool)
G00 Z5.0         (Lift tool)

(STAR 2 - BOTTOM RIGHT)
G00 X70.0 Y20.0  (Move to starting position of second star)
G01 Z-1.0 F100.0 (Lower tool to cutting depth)
G01 X80.0 Y0.0   (Draw first line)
G01 X60.0 Y0.0   (Draw second line)
G01 X70.0 Y20.0  (Draw third line, completing one arm)
G01 X75.0 Y10.0  (Start inner arm)
G01 X65.0 Y10.0  (Finish inner arm)
G01 X70.0 Y20.0  (Return to center)

(Lift Tool)
G00 Z5.0         (Lift tool to safe height)

(END OF PROGRAM)
G28 Z0.0         (Return Z to home position)
M30               (End program)
