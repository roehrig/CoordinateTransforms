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
