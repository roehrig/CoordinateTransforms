import epics
from math import cos, sin, pi

class XZT_Transform(object):

    def __init__(self):

        self.cosine_factor = 0
        self.sine_factor = 0

        self.x_axis = 0
        self.z_axis = 0
        self.y_axis = 0
        self.fine_x_axis = 0
        self.t_axis = 0

        self.x_drive = 0
        self.z_drive = 0
        self.y_drive = 0
        self.fine_x_drive = 0
        self.t_drive = 0

        self.x_motor = 0
        self.z_motor = 0
        self.t_motor = 0
        self.fine_x_motor = 0

        # Offsets between the center of rotation and the sample origin.
        self.xo_offset_pv = epics.PV('9idbTAU:SM:SXO.VAL')
        self.zo_offset_pv = epics.PV('9idbTAU:SM:SZO.VAL')

        # Offsets between the center of rotation at the home positions and the optical axis.
        self.xa_offset_pv = epics.PV('9idbTAU:SM:SXA.VAL')
        self.za_offset_pv = epics.PV('9idbTAU:SM:SZA.VAL')

        # Axes for coarse X, Z, and fine X
        self.cx_pv = epics.PV('9idbTAU:SM:CX:RqsPos.VAL')
        self.cz_pv = epics.PV('9idbTAU:SM:CZ:RqsPos.VAL')
        self.fx_pv = epics.PV('9idbTAU:SM:FX:RqsPos.VAL')

        # Drives for coarse X, Z, and fine X
        self.sx_pv = epics.PV('9idbTAU:SM:SX:RqsPos.VAL')
        self.sz_pv = epics.PV('9idbTAU:SM:SZ:RqsPos.VAL')
        self.px_pv = epics.PV('9idbTAU:SM:PX:RqsPos.VAL')

        # Motors for coarse X, Z, and fine X
        self.mx_pv = None
        self.mz_pv = None
        self.tz_pv = None
        self.mpx_pv = None

        self.x_offset_pv = epics.PV('9idbTAU:SM:SX:Offset.VAL')
        self.x_scale_pv = epics.PV('9idbTAU:SM:SX:Scale.VAL')
        self.z_offset_pv = epics.PV('9idbTAU:SM:SZ:Offset.VAL')
        self.z_scale_pv = epics.PV('9idbTAU:SM:SZ:Scale.VAL')
        self.t_offset_pv = epics.PV('9idbTAU:SM:ST:Offset.VAL')
        self.t_scale_pv = epics.PV('9idbTAU:SM:ST:Scale.VAL')
        self.fine_x_offset_pv = epics.PV('9idbTAU:SM:PX:Offset.VAL')
        self.fine_x_scale_pv = epics.PV('9idbTAU:SM:PX:Scale.VAL')

        return

    def transform_axes(self, angle=0, x=0, z=0, fine_x=0, use_offsets=True):
        """"
        This method takes values that represent axis positions (as defined in
        the tpmac module) and calculates the values of the corresponding
        drive positions
        
        :param angle: The position value of the rotation axis.
        :type angle: float
        :param x: The position value of the coarse X axis.
        :type x: float
        :param z: The position value of the Z axis.
        :type z: float
        :param fine_x: The position of the fine X axis.
        :type fine_x: float
        """

        # Get all of the offset values.
        xo_offset = self.xo_offset_pv.get()
        zo_offset = self.zo_offset_pv.get()
        xa_offset = self.xa_offset_pv.get()
        za_offset = self.za_offset_pv.get()
        x_offset = self.x_offset_pv.get()
        x_scale = self.x_scale_pv.get()
        z_offset = self.z_offset_pv.get()
        z_scale = self.z_scale_pv.get()
        t_offset = self.t_offset_pv.get()
        t_scale = self.t_scale_pv.get()
        fine_x_offset = self.fine_x_offset_pv.get()
        fine_x_scale = self.fine_x_scale_pv.get()
	
        x_axis = self.cx_pv.get()
        z_axis = self.cz_pv.get()
        fine_x_axis = self.fx_pv.get()
        t_axis = angle

        self.set_axis_positions(t_axis, x_axis, z_axis, fine_x_axis)

        cosine_factor = cos(t_axis * (pi/180.0))
        sine_factor = sin(t_axis * (pi/180.0))

        # Caluclate the drive positions
        x_drive = -(xo_offset * cosine_factor) - (x_axis * cosine_factor) - (z_axis * sine_factor)\
                          - (zo_offset * sine_factor) + xa_offset

        z_drive = -(zo_offset * cosine_factor) + (fine_x_axis * sine_factor) - (z_axis * cosine_factor)\
                          + (xo_offset * sine_factor) + za_offset

        fine_x_drive = -(xo_offset * cosine_factor) - (fine_x_axis * cosine_factor) - (z_axis * sine_factor)\
                              - (zo_offset * sine_factor) + xa_offset


        t_drive = t_axis

        self.set_drive_positions(t_drive, x_drive, z_drive, fine_x_drive)

        # Calculate the motor positions
        if use_offsets:

            x_motor = x_drive / x_scale
            z_motor = z_drive / z_scale
            t_motor = t_drive / t_scale
            fine_x_motor = x_drive / fine_x_scale

        else:

            x_motor = (x_drive - x_offset) / x_scale
            z_motor = (z_drive - z_offset) / z_scale
            t_motor = (t_drive - t_offset) / t_scale
            fine_x_motor = (fine_x_drive - fine_x_offset) / fine_x_scale

        self.set_motor_positions(t_motor, x_motor, z_motor, fine_x_motor)

        return

    def transform_drives(self, angle=0, x=0, z=0, fine_x=0, use_offsets=True):
        """"
        This method takes values that represent axis positions (as defined in
        the tpmac module) and calculates the values of the corresponding
                drive positions

        :param angle: The position value of the rotation drive.
        :type angle: float
        :param x: The position value of the coarse X drive.
        :type x: float
        :param z: The position value of the Z drive.
        :type z: float
        :param fine_x: The position of the fine X drive.
        :type fine_x: float
        """

        # Get all of the offset values.
        xo_offset = self.xo_offset_pv.get()
        zo_offset = self.zo_offset_pv.get()
        xa_offset = self.xa_offset_pv.get()
        za_offset = self.za_offset_pv.get()
        x_offset = self.x_offset_pv.get()
        x_scale = self.x_scale_pv.get()
        z_offset = self.z_offset_pv.get()
        z_scale = self.z_scale_pv.get()
        t_offset = self.t_offset_pv.get()
        t_scale = self.t_scale_pv.get()
        fine_x_offset = self.fine_x_offset_pv.get()
        fine_x_scale = self.fine_x_scale_pv.get()

        t_drive = angle
        x_drive = x
        z_drive = z
        fine_x_drive = fine_x

        self.set_drive_positions(t_drive, x_drive, z_drive, fine_x_drive)

        cosine_factor = cos(t_drive * (pi / 180))
        sine_factor = sin(t_drive * (pi / 180))

        # Calculate the motor positions
        if use_offsets:

            x_motor = x_drive / x_scale
            z_motor = z_drive / z_scale
            t_motor = t_drive / t_scale
            fine_x_motor = fine_x_drive / fine_x_scale

        else:

            x_motor = (x_drive - x_offset) / x_scale
            z_motor = (z_drive - z_offset) / z_scale
            t_motor = (t_drive - t_offset) / t_scale
            fine_x_motor = (fine_x_drive - fine_x_offset) / fine_x_scale

        self.set_motor_positions(t_motor, x_motor, z_motor, fine_x_motor)

        x_axis = -(x_drive * cosine_factor) + (z_drive * sine_factor) - xo_offset + \
                 (xa_offset * cosine_factor) + (za_offset * sine_factor)

        z_axis = -(fine_x_drive * sine_factor) - (z_drive * cosine_factor) - zo_offset + \
                 (xa_offset * sine_factor) + (za_offset * cosine_factor)

        t_axis = t_drive

        fine_x_axis = -(fine_x_drive * cosine_factor) + (z_drive * sine_factor) - xo_offset +\
                      (xa_offset * cosine_factor) + (za_offset * sine_factor)

        self.set_axis_positions(t_axis, x_axis, z_axis, fine_x_axis)

        return

    def transform_motors(self, angle=0, x=0, y=0, z=0, fine_x=0, use_offsets=True):

        return

    def get_axis_positions(self):

        return self.x_axis, self.z_axis, self.t_axis, self.fine_x_axis

    def get_drive_positions(self):

        return self.x_drive, self.z_drive, self.t_drive, self.fine_x_drive

    def get_motor_positions(self):

        return self.x_motor, self.z_motor, self.t_motor, self.fine_x_motor

    def set_axis_positions(self, angle, x, z, fine_x):

        self.t_axis = angle
        self.x_axis = x
        self.z_axis = z
        self.fine_x_axis = fine_x

        return

    def set_drive_positions(self, angle, x, z, fine_x):

        self.t_drive = angle
        self.x_drive = x
        self.z_drive = z
        self.fine_x_drive = fine_x

        return

    def set_motor_positions(self, angle, x, z, fine_x):

        self.t_motor = angle
        self.x_motor = x
        self.z_motor = z
        self.fine_x_motor = fine_x

        return
