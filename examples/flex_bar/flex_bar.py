from altprint.printable.flex import FlexPrint, FlexProcess

process = FlexProcess(settings_file='flex_bar.yml')

part = FlexPrint(process)
part.slice()
part.make_layers()
part.export_gcode("flex_bar.gcode")
