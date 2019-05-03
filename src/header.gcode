G90
M82
M106 S0
M104 S238 T0
M109 S238 T0
G28 ; home all axes
G1 Z5 F1000 ; move Z up 5mm
G32 S1 ; perform auto bed leveling
; process Process1
; layer 1, Z = 0.200
T0
M102
G92 E0.0000
G1 E-1.0000 F2400
M103
; feature outer perimeter
; tool H0.200 W0.480
G1 Z0.200 F1000
G1 X50 Y50 F6000
M101
G1 E0.0000 F588
G92 E0.0000
