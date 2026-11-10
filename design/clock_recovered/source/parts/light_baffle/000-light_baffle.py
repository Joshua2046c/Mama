j=part("dial")
width=param("baffle_width",76.0)
height=param("baffle_height",28.0)
thickness=param("baffle_thickness",1.15)
back_z=param("baffle_back_z",24.8)
edge_gap=param("baffle_light_edge_clearance",0.2)
cell_window=j.window_size+2*edge_gap
center_y=j.led_lower_y+j.led_pitch/2
s=Pos(0,center_y,back_z)*extrude(RectangleRounded(width,height,2.0),thickness)
s=s.cut(*[Pos(x,y,back_z-0.01)*extrude(RectangleRounded(cell_window,cell_window,0.6),thickness+0.02) for x,y in j.led_centers])
assert s.is_valid and len(s.solids())==1
s.color=srgb("#242628")
publish("light_baffle",s,"十灯遮光隔仓",material="petg")
