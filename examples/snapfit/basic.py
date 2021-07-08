from altprint.baseprints import BasePrint
from altprint.path.rectilinear_optimal import rectilinear_optimal

snap = BasePrint()
snap.model = 'snap.stl'
snap.flex_model = 'snapflex.stl'
snap.start_script = 'start.gcode'
snap.end_script = 'end.gcode'

snap.slice()
snap.make_layers(fill=rectilinear_optimal)
snap.output_gcode('snap')
