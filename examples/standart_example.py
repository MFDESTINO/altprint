from altprint.printable.standart import StandartPrint, StandartProcess

process = StandartProcess(model_file="stl/cube.stl",
                          infill_angle=[0,45,90,-45],
                          offset=(50, 50, 0),
                          perimeter_num=3,
                          perimeter_gap=0.5,
                          start_script="scripts/start.gcode",
                          end_script="scripts/end.gcode")

part = StandartPrint(process)
part.slice()
part.make_layers()
part.export_gcode("output/cube_injected.gcode", "output/cubo_simplify.gcode")
#part.export_gcode("output/cube.gcode")
