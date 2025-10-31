""""
This sample takes snapshots of the model using mv2 in the
various view modes available.

All files are saved in the current project folder (default behaviour)

"""

import iesve        # the VE api

mv = iesve.Mv2()

# Take snapshot in shaded mode:
mv.take_snapshot(file_name="mv2_shaded", view_mode=iesve.mv2_viewmode.shaded)

# Take snapshot in textured mode:
mv.take_snapshot(file_name="mv2_textured", view_mode=iesve.mv2_viewmode.textured)

# Take snapshot in hidden line mode:
mv.take_snapshot(file_name="mv2_hidden_line", view_mode=iesve.mv2_viewmode.hidden_line, components=True)

# Take snapshot in xray mode:
mv.take_snapshot(file_name="mv2_xray", view_mode=iesve.mv2_viewmode.xray, components=True)

# Take snapshot in component mode:
# note - this will implicitly force components on...
mv.take_snapshot(file_name="mv2_component", view_mode=iesve.mv2_viewmode.component)

