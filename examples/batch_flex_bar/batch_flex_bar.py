from altprint.printable.flex import FlexPrint, FlexProcess
from altprint.printable.multi import MultiPrint, MultiProcess

flex_process1 = FlexProcess(settings_file='flex_bar1.yml')
flex_process2 = FlexProcess(settings_file='flex_bar2.yml')
flex_process3 = FlexProcess(settings_file='flex_bar3.yml')


flex_part1 = FlexPrint(flex_process1)
flex_part1.slice()
flex_part1.make_layers()

flex_part2 = FlexPrint(flex_process2)
flex_part2.slice()
flex_part2.make_layers()

flex_part3 = FlexPrint(flex_process3)
flex_part3.slice()
flex_part3.make_layers()

multi_process = MultiProcess(parts=[flex_part1, flex_part2, flex_part3],
                             start_script="scripts/start.gcode",
                             end_script="scripts/end.gcode")
multi_part = MultiPrint(multi_process)
multi_part.slice()
multi_part.make_layers()
multi_part.export_gcode("batch.gcode")