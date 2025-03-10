%
O0001
(DIA 20.0 END MILL - NO CUTTER RADIUS COMP USED)
(MACHINE OUTSIDE OF 100 X 200 RECTANGLE)
(X0.0 Y77.027 - BOTTOM LEFT CORNER)
N1 G00 G17 G21 G40 G49 G80 G94
(SET AND CHANGE TOOL 01)
N4 T01 M06
N5 S2000 M03
N6 G90 G54 G00 X50.000 Y50.000
(CUTTING STARTS)
N9 G01 Z-5.000 F100.
(LINEAR FEED TO XY WITH GIVEN FEED RATE)
N10 G01 X50.000 Y54.505 F600.
N11 G01 X324.775
N12 G01 Y550.000
N13 G01 X54.505
N14 G01 Y50.000
G1 x117.761 y161.943
G1 x117.010 y155.096
G1 x113.258 y156.034
G1 x114.196 y161.287
G1 x111.945 y161.287
G1 x107.818 y153.970
G1 x102.040 y159.973
G1 x93.935 y165.320
G1 x92.247 y165.414
G1 x91.403 y161.849
G1 x86.181 y159.223
G1 x68.234 y154.158
G1 x59.980 y150.687
G1 x57.541 y153.220
G1 x54.633 y159.786
G1 x44.484 y166.127
G1 x40.469 y172.355
G1 x48.818 y182.861
G1 x51.350 y191.115
G1 x44.972 y203.872
G1 x40.845 y231.637
G1 x40.657 y213.439
G1 x39.391 y224.695
G1 x40.094 y235.389


(LIFT SPINDLE)
N15 G00 Z10.000 M09
(STOP SPINDLE)
N16 G91 G28 Z0.0 M05
(PROGRAM END)
N18 M30
%