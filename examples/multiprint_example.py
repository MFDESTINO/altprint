from altprint.printable.standart import StandartPrint, StandartProcess
from altprint.printable.multi import MultiPrint, MultiProcess
from altprint.printable.flex import FlexPrint, FlexProcess

process1 = StandartProcess(model_file="stl/test1.stl",
                           infill_angle=90,
                           external_adjust=0.5,
                           center_model=False)
part1 = StandartPrint(process1)
part1.slice()
part1.make_layers()

process2_t = StandartProcess(model_file="stl/test2.stl",
                      infill_angle=-45,
                      raster_gap=0.5,
                      overlap=0.0,
                      center_model=False,
                      start_script="scripts/start.gcode",
                      end_script="scripts/end.gcode")

# process2 = FlexProcess(model_file="stl/test2.stl",
#                       flex_model_file="stl/test2_flex.stl",
#                       infill_angle=-45,
#                       raster_gap=0.5,
#                       overlap=0.1,
#                       center_model=False)
part2 = StandartPrint(process2_t)
part2.slice()
part2.make_layers()
#part2.export_gcode("bug.gcode")

multiprocess = MultiProcess(parts=[part1, part2],
                            start_script="scripts/start.gcode",
                            end_script="scripts/end.gcode")
#
# import matplotlib.pyplot as plt
# fig, ax = plt.subplots()
#
# infill = part2.layers[9.6].infill
# for raster in infill:
#     x, y = raster.path.xy
#     ax.plot(x, y, lw=2)
#
# plt.axis("equal")
# plt.show()


multiprint = MultiPrint(multiprocess)
multiprint.make_layers()
multiprint.export_gcode("test1.gcode")
