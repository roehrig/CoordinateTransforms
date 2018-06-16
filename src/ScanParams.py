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


class ScanParams(object):

    def __init__(self):

        self.x_center = 0
        self.y_center = 0
        self.z_position = 0
        self.x_width = 0
        self.x_pixel_size = 0
        self.y_width = 0
        self.y_pixel_size = 0
        self.dwell_time = 0

        return

    def set_parameters(self, x=0, y=0, z=0, x_width=0, x_size=0, y_width=0, y_size=0, dwell=0):
        """
        :param x:       The center of the scan in the x direction.
        :type  x:       float
        :param y:       The center of the scan in the y direction.
        :type  y:       float
        :param z:       The z position of the scan.
        :type  z:       float
        :param x_width: The width of the scan in the x direction.
        :type  x_width: float
        :param x_size:  The size of the pixel in the x direction.
        :type  x_size:  float
        :param y_width: The size of the scan in the y direction.
        :type  y_width: float
        :param y_size:  The size of the pixel in the y direction.
        :type  y_size:  float
        :param dwell:   The amount of time to collect data at each pixel, usually in milliseconds.
        :type  dwell:   float
        :return:        None
        """

        # Check to make sure that pixel sizes and the dwell time are all
        # greater than zero.  If not, raise an exception.

        if x_size <= 0:
            raise ValueError
        else:
            self.x_pixel_size = x_size

        if y_size <= 0:
            raise ValueError
        else:
            self.y_pixel_size = y_size

        if dwell <= 0:
            raise ValueError
        else:
            self.dwell_time = dwell

        self.x_center = x
        self.y_center = y
        self.z_position = z
        self.x_width = x_width
        self.y_width = y_width

        return

    def get_parameters(self):

        return (self.x_center, self.y_center, self.z_position, self.x_width, self.x_pixel_size, self.y_width,
                self.y_pixel_size, self.dwell_time)


class ScanParamsList(object):

    def __init__(self):

        return
