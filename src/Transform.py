'''
Copyright (c) 2018, UChicago Argonne, LLC. All rights reserved.
Copyright 2016. UChicago Argonne, LLC. This software was produced
under U.S. Government contract DE-AC02-06CH11357 for Argonne National
Laboratory (ANL), which is operated by UChicago Argonne, LLC for the
U.S. Department of Energy. The U.S. Government has rights to use,
reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR
UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
modified to produce derivative works, such modified software should
be clearly marked, so as not to confuse it with the version available
from ANL.
Additionally, redistribution and use in source and binary forms, with
or without modification, are permitted provided that the following
conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in
      the documentation and/or other materials provided with the
      distribution.
    * Neither the name of UChicago Argonne, LLC, Argonne National
      Laboratory, ANL, the U.S. Government, nor the names of its
      contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago
Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
'''

from math import cos, sin, pi
from CS import CoordinateSystem as CS


class XZT_Transform(object):

    def __init__(self):

        self.cosine_factor = 0
        self.sine_factor = 0

        self.coordsys = CS("9idbTAU")

        return

    def transform_axes(self, angle=0, x=0, y=0, z=0, fine_x=0, fine_y=0, use_offsets=True, use_pvs=True):
        """"
        This method takes values that represent axis positions (as defined in
        the tpmac module) and calculates the values of the corresponding
        drive and motor positions
        
        :param angle: The position value of the rotation axis.
        :type angle: float
        :param x: The position value of the coarse X axis.
        :type x: float
        :param y: The position of the coarse Y axis
        :type y: float
        :param z: The position value of the Z axis.
        :type z: float
        :param fine_x: The position of the fine X axis.
        :type fine_x: float
        :param fine_y: The position of the fine y drive.
        :type fine_y: float
        :param use_offsets: Use offsets in the calculation of motor values.
        :type use_offsets: bool
        :param use_pvs: Use current pv values or manually entered values.
        :type use_pvs: bool
        """

        # Get all of the offset values.
        xo_offset, yo_offset, zo_offset = self.coordsys.get_sample_origin_offsets()
        xa_offset, ya_offset, za_offset = self.coordsys.get_optical_axis_offsets()
        x_offset, y_offset, z_offset, t_offset, fine_x_offset, fine_y_offset = self.coordsys.get_offsets()
        x_scale, y_scale, z_scale, t_scale, fine_x_scale, fine_y_scale = self.coordsys.get_scale_factors()

        if use_pvs:
            x_axis, y_axis, z_axis, t_axis, fine_x_axis, fine_y_axis = self.coordsys.get_axis_pv_positions()
        else:
            x_axis = x
            y_axis = y
            z_axis = z
            fine_x_axis = fine_x
            fine_y_axis = fine_y

        t_axis = angle

        self.coordsys.set_axis_positions(t_axis, x_axis, y_axis, z_axis, fine_x_axis, fine_y_axis)

        cosine_factor = cos(t_axis * (pi/180.0))
        sine_factor = sin(t_axis * (pi/180.0))

        # Calculate the drive positions
        x_drive = -(xo_offset * cosine_factor) - (x_axis * cosine_factor) - (z_axis * sine_factor)\
                          - (zo_offset * sine_factor) + xa_offset

        y_drive = -yo_offset - y_axis + ya_offset

        z_drive = -(zo_offset * cosine_factor) + (fine_x_axis * sine_factor) - (z_axis * cosine_factor)\
                          + (xo_offset * sine_factor) + za_offset

        fine_x_drive = -(xo_offset * cosine_factor) - (fine_x_axis * cosine_factor) - (z_axis * sine_factor)\
                              - (zo_offset * sine_factor) + xa_offset

        fine_y_drive = -yo_offset - fine_y_axis + ya_offset

        t_drive = t_axis

        self.coordsys.set_drive_positions(t_drive, x_drive, y_drive, z_drive, fine_x_drive, fine_y_drive)

        # Calculate the motor positions
        if use_offsets:

            x_motor = x_drive / x_scale
            y_motor = y_drive / y_scale
            z_motor = z_drive / z_scale
            t_motor = t_drive / t_scale
            fine_x_motor = x_drive / fine_x_scale
            fine_y_motor = y_drive / fine_y_scale

        else:

            x_motor = (x_drive - x_offset) / x_scale
            y_motor = (y_drive - y_offset) / y_scale
            z_motor = (z_drive - z_offset) / z_scale
            t_motor = (t_drive - t_offset) / t_scale
            fine_x_motor = (fine_x_drive - fine_x_offset) / fine_x_scale
            fine_y_motor = (fine_y_drive - fine_y_offset) / fine_y_scale

        self.coordsys.set_motor_positions(t_motor, x_motor, y_motor, z_motor, fine_x_motor, fine_y_motor)

        return

    def transform_drives(self, angle=0, x=0, y=0, z=0, fine_x=0, fine_y=0, use_offsets=True, use_pvs=True):
        """"
        This method takes values that represent axis positions (as defined in
        the tpmac module) and calculates the values of the corresponding
        drive and motor positions

        :param angle: The position value of the rotation drive.
        :type angle: float
        :param x: The position value of the coarse X drive.
        :type x: float
        :param y: The position of the coarse Y drive
        :type y: float
        :param z: The position value of the Z drive.
        :type z: float
        :param fine_x: The position of the fine X drive.
        :type fine_x: float
        :param fine_y: The position of the fine y drive.
        :type fine_y: float
        :param use_offsets: Use offsets in the calculation of motor values.
        :type use_offsets: bool
        :param use_pvs: Use current pv values or manually entered values.
        :type use_pvs: bool
        """

        # Get all of the offset values.
        xo_offset, yo_offset, zo_offset = self.coordsys.get_sample_origin_offsets()
        xa_offset, ya_offset, za_offset = self.coordsys.get_optical_axis_offsets()
        x_offset, y_offset, z_offset, t_offset, fine_x_offset, fine_y_offset = self.coordsys.get_offsets()
        x_scale, y_scale, z_scale, t_scale, fine_x_scale, fine_y_scale = self.coordsys.get_scale_factors()

        if use_pvs:
            x_drive, y_drive, z_drive, t_drive, fine_x_drive, fine_y_drive = self.coordsys.get_drive_pv_positions()
        else:
            x_drive = x
            y_drive = y
            z_drive = z
            fine_x_drive = fine_x
            fine_y_drive = fine_y

        t_drive = angle

        self.coordsys.set_drive_positions(t_drive, x_drive, y_drive, z_drive, fine_x_drive, fine_y_drive)

        cosine_factor = cos(t_drive * (pi / 180))
        sine_factor = sin(t_drive * (pi / 180))

        # Calculate the motor positions
        if use_offsets:

            x_motor = x_drive / x_scale
            y_motor = y_drive / y_scale
            z_motor = z_drive / z_scale
            t_motor = t_drive / t_scale
            fine_x_motor = fine_x_drive / fine_x_scale
            fine_y_motor = fine_y_drive / fine_y_scale

        else:

            x_motor = (x_drive - x_offset) / x_scale
            y_motor = (y_drive - y_offset) / y_scale
            z_motor = (z_drive - z_offset) / z_scale
            t_motor = (t_drive - t_offset) / t_scale
            fine_x_motor = (fine_x_drive - fine_x_offset) / fine_x_scale
            fine_y_motor = (fine_y_drive - fine_y_offset) / fine_y_scale

        self.coordsys.set_motor_positions(t_motor, x_motor, y_motor, z_motor, fine_x_motor, fine_y_motor)

        x_axis = -(x_drive * cosine_factor) + (z_drive * sine_factor) - xo_offset + \
                 (xa_offset * cosine_factor) + (za_offset * sine_factor)

        y_axis = -yo_offset - y_drive + ya_offset

        z_axis = -(fine_x_drive * sine_factor) - (z_drive * cosine_factor) - zo_offset + \
                 (xa_offset * sine_factor) + (za_offset * cosine_factor)

        t_axis = t_drive

        fine_x_axis = -(fine_x_drive * cosine_factor) + (z_drive * sine_factor) - xo_offset +\
                      (xa_offset * cosine_factor) + (za_offset * sine_factor)

        fine_y_axis = -yo_offset - fine_y_drive + ya_offset

        self.coordsys.set_axis_positions(t_axis, x_axis, y_axis, z_axis, fine_x_axis, fine_y_axis)

        return

    def transform_motors(self, angle=0, x=0, y=0, z=0, fine_x=0, use_offsets=True):

        return

    def get_axis_positions(self):
        """
        This will return values of the axes in the coordinate system.

        :return: Returns a tuple of axis positions
        """

        return self.coordsys.get_axis_positions()

    def get_drive_positions(self):
        """
        This will return values of the drives in the coordinate system.

        :return: Returns a tuple of drive positions
        """

        return self.coordsys.get_drive_positions()

    def get_motor_positions(self):
        """
        This will return values of the motors in the coordinate system.

        :return: Returns a tuple of motor positions
        """

        return self.coordsys.get_motor_positions()

    def set_axis_positions(self, angle=0, x=0, y=0, z=0, fine_x=0, fine_y=0):
        """
        This function will set the axis values of the members of the
        coordinate system.

        :param angle:  The axis rotation angle of the coordinate system
        :type  angle:  float
        :param x:      The axis position of the X stage.
        :type  x:      float
        :param y:      The axis position of the Y stage.
        :type  y:      float
        :param z:      The axis position of the Z stage.
        :type  z:      float
        :param fine_x: The axis position of the fine X stage.
        :type  fine_x: float
        :param fine_y: The axis position of the fine Y stage.
        :type  fine_y: float
        :return:       None
        """

        self.coordsys.set_axis_positions(angle, x, y, z, fine_x, fine_y)

        return

    def set_drive_positions(self, angle=0, x=0, y=0, z=0, fine_x=0, fine_y=0):
        """
        This function will set the axis values of the members of the
        coordinate system.

        :param angle:  The drive rotation angle of the coordinate system
        :type  angle:  float
        :param x:      The drive position of the X stage.
        :type  x:      float
        :param y:      The drive position of the Y stage.
        :type  y:      float
        :param z:      The drive position of the Z stage.
        :type  z:      float
        :param fine_x: The drive position of the fine X stage.
        :type  fine_x: float
        :param fine_y: The drive position of the fine Y stage.
        :type  fine_y: float
        :return:       None
        """

        self.coordsys.set_drive_positions(angle, x, y, z, fine_x, fine_y)

        return

    def set_motor_positions(self, angle=0, x=0, y=0, z=0, fine_x=0, fine_y=0):
        """
        This function will set the axis values of the members of the
        coordinate system.

        :param angle:  The motor rotation angle of the coordinate system
        :type  angle:  float
        :param x:      The motor position of the X stage.
        :type  x:      float
        :param y:      The motor position of the Y stage.
        :type  y:      float
        :param z:      The motor position of the Z stage.
        :type  z:      float
        :param fine_x: The motor position of the fine X stage.
        :type  fine_x: float
        :param fine_y: The motor position of the fine Y stage.
        :type  fine_y: float
        :return:       None
        """

        self.coordsys.set_motor_positions(angle, x, y, z, fine_x, fine_y)

        return
