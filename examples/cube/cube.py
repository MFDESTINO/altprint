from altprint.printable.standart import StandartPrint, StandartProcess

process = StandartProcess(settings_file='cube.yml')

part = StandartPrint(process)
part.slice()
part.make_layers()
part.export_gcode("cube.gcode")
