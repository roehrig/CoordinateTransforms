import epics


class CoordinateSystem(object):

    def __init__(self, prefix):

        """

        :param prefix: The ioc specific prefix of the PVs
        :type  prefix: str
        """
    
        self.x_axis = 0
        self.z_axis = 0
        self.y_axis = 0
        self.t_axis = 0
        self.fine_x_axis = 0
        self.fine_y_axis = 0

        self.x_drive = 0
        self.z_drive = 0
        self.y_drive = 0
        self.t_drive = 0
        self.fine_x_drive = 0
        self.fine_y_drive = 0

        self.x_motor = 0
        self.y_motor = 0
        self.z_motor = 0
        self.t_motor = 0
        self.fine_x_motor = 0
        self.fine_y_motor = 0

        # Offsets between the center of rotation and the sample origin.
        self.xo_offset_pv = epics.PV('%s:SM:SXO.VAL' % prefix)
        self.yo_offset_pv = epics.PV('%s:SY:SYO.VAL' % prefix)
        self.zo_offset_pv = epics.PV('%s:SM:SZO.VAL' % prefix)

        # Offsets between the center of rotation at the home positions and the optical axis.
        self.xa_offset_pv = epics.PV('%s:SM:SXA.VAL' % prefix)
        self.ya_offset_pv = epics.PV('%s:SY:SYA.VAL' % prefix)
        self.za_offset_pv = epics.PV('%s:SM:SZA.VAL' % prefix)

        # Axes for coarse X, Y, Z, T, fine X, and fine Y
        self.cx_pv = epics.PV('%s:SM:CX:RqsPos.VAL' % prefix)
        self.cy_pv = epics.PV('%s:SY:CY:RqsPos.VAL' % prefix)
        self.cz_pv = epics.PV('%s:SM:CZ:RqsPos.VAL' % prefix)
        self.ct_pv = epics.PV('%s:SM:CT:RqsPos.VAL' % prefix)
        self.fx_pv = epics.PV('%s:SM:FX:RqsPos.VAL' % prefix)
        self.fy_pv = epics.PV('%s:SY:FY:RqsPos.VAL' % prefix)

        # Drives for coarse X, Y, Z, T, fine X, and fine Y
        self.sx_pv = epics.PV('%s:SM:SX:RqsPos.VAL' % prefix)
        self.sy_pv = epics.PV('%s:SY:SY:RqsPos.VAL' % prefix)
        self.sz_pv = epics.PV('%s:SM:SZ:RqsPos.VAL' % prefix)
        self.st_pv = epics.PV('%s:SM:ST:RqsPos.VAL' % prefix)
        self.px_pv = epics.PV('%s:SM:PX:RqsPos.VAL' % prefix)
        self.py_pv = epics.PV('%s:SY:PY:RqsPos.VAL' % prefix)

        # Motors for coarse X, Y, Z, T, fine X, and fine Y
        self.mx_pv = epics.PV('%s:SM:mx:RqsPos.VAL' % prefix)
        self.my_pv = epics.PV('%s:SY:my:RqsPos.VAL' % prefix)
        self.mz_pv = epics.PV('%s:SM:mz:RqsPos.VAL' % prefix)
        self.tz_pv = epics.PV('%s:SM:mt:RqsPos.VAL' % prefix)
        self.mpx_pv = epics.PV('%s:SM:mpx:RqsPos.VAL' % prefix)
        self.mpy_pv = epics.PV('%s:SY:mpy:RqsPos.VAL' % prefix)

        self.x_offset_pv = epics.PV('%s:SM:SX:Offset.VAL' % prefix)
        self.x_scale_pv = epics.PV('%s:SM:SX:Scale.VAL' % prefix)
        self.y_offset_pv = epics.PV('%s:SY:SY:Offset.VAL' % prefix)
        self.y_scale_pv = epics.PV('%s:SY:SY:Scale.VAL' % prefix)
        self.z_offset_pv = epics.PV('%s:SM:SZ:Offset.VAL' % prefix)
        self.z_scale_pv = epics.PV('%s:SM:SZ:Scale.VAL' % prefix)
        self.t_offset_pv = epics.PV('%s:SM:ST:Offset.VAL' % prefix)
        self.t_scale_pv = epics.PV('%s:SM:ST:Scale.VAL' % prefix)
        self.fine_x_offset_pv = epics.PV('%s:SM:PX:Offset.VAL' % prefix)
        self.fine_x_scale_pv = epics.PV('%s:SM:PX:Scale.VAL' % prefix)
        self.fine_y_offset_pv = epics.PV('%s:SY:PY:Offset.VAL' % prefix)
        self.fine_y_scale_pv = epics.PV('%s:SY:PY:Scale.VAL' % prefix)

        return

    def get_offsets(self):

        return self.x_offset_pv.get(), self.y_offset_pv.get(), self.z_offset_pv.get(), self.t_offset_pv.get(), self.fine_x_offset_pv.get(), self.fine_y_offset_pv.get()

    def get_scale_factors(self):

        return self.x_scale_pv.get(), self.y_scale_pv.get(), self.z_scale_pv.get(), self.t_scale_pv.get(), self.fine_x_scale_pv.get(), self.fine_y_scale_pv.get()

    def get_sample_origin_offsets(self):
    
        return self.xo_offset_pv.get(), self.yo_offset_pv.get(), self.zo_offset_pv.get()

    def get_optical_axis_offsets(self):
    
        return self.xa_offset_pv.get(), self.ya_offset_pv.get(), self.za_offset_pv.get()

    def get_axis_pv_positions(self):
    
        self.x_axis = self.cx_pv.get()
        self.y_axis = self.cy_pv.get()
        self.z_axis = self.cz_pv.get()
        self.t_axis = self.ct_pv.get()
        self.fine_x_axis = self.fx_pv.get()
        self.fine_y_axis = self.fy_pv.get()

        return self.x_axis, self.y_axis, self.z_axis, self.t_axis, self.fine_x_axis, self.fine_y_axis

    def get_drive_pv_positions(self):

        self.x_drive = self.sx_pv.get()
        self.y_drive = self.sy_pv.get()
        self.z_drive = self.sz_pv.get()
        self.t_drive = self.st_pv.get()
        self.fine_x_drive = self.px_pv.get()
        self.fine_y_drive = self.py_pv.get()

        return self.x_drive, self.y_drive, self.z_drive, self.t_drive, self.fine_x_drive, self.fine_y_drive

    def get_axis_positions(self):

        return self.x_axis, self.y_axis, self.z_axis, self.t_axis, self.fine_x_axis, self.fine_y_axis

    def get_drive_positions(self):

        return self.x_drive, self.y_drive, self.z_drive, self.t_drive, self.fine_x_drive, self.fine_y_drive

    def get_motor_positions(self):

        return self.x_motor, self.y_motor, self.z_motor, self.t_motor, self.fine_x_motor, self.fine_y_motor

    def set_axis_positions(self, angle, x, y, z, fine_x, fine_y):

        self.t_axis = angle
        self.x_axis = x
        self.y_axis = y
        self.z_axis = z
        self.fine_x_axis = fine_x
        self.fine_y_axis = fine_y

        return

    def set_drive_positions(self, angle, x, y, z, fine_x, fine_y):

        self.t_drive = angle
        self.x_drive = x
        self.y_drive = y
        self.z_drive = z
        self.fine_x_drive = fine_x
        self.fine_y_drive = fine_y

        return

    def set_motor_positions(self, angle, x, y, z, fine_x, fine_y):

        self.t_motor = angle
        self.x_motor = x
        self.y_motor = y
        self.z_motor = z
        self.fine_x_motor = fine_x
        self.fine_y_motor = fine_y

        return
