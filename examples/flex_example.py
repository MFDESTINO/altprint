from altprint.printable.flex import FlexPrint, FlexProcess

process = FlexProcess(model_file="flex1.stl",
                      flex_model_file="flex2.stl",
                      infill_angle=0,
                      center_model=False,
                      start_script="scripts/start.gcode",
                      end_script="scripts/end.gcode")

part = FlexPrint(process)
part.slice()
part.make_layers()
part.export_gcode("flex.gcode")
