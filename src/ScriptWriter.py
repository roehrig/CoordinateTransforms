class FlyScanScriptWriter(object):

    def __init__(self):

        self.file_template = "BNP_batch_flyscan_with_z_template.py"
        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        return

    def write_script(self, file_name, coord_list, x_width=1, y_width=1, x_step=1, y_step=1, dwell=1):
        """
        This function will create a python script for executing a series of fly scans.
        It uses a template file and adds scan parameters that the user has entered.

        :param file_name:    The name of the python file to create, including path.
        :type  file_name:    str
        :param coord_list:   A list of positions to be used for the scan.
        :type  coord_list:   list of float tuples
        :param x_width:      The width of the scan in the X direction.
        :type  x_width:      float
        :param y_width:      The width of the scan in the Y direction.
        :type  y_width:      float
        :param x_step:       The size of each pixel in the X direction.
        :type  x_step:       float
        :param y_step:       The size of each pixel in the Y direction.
        :type  y_step        float
        :param dwell:        The amount of time to collect data at each pixel.
        :type  dwell:        float
        :return:             None
        """

        try:
            with open(file_name, 'w') as script, open(self.file_template, 'r') as template:
                for line in template:
                    script.write(line)
                    if line == "scans = [\n":
                        for positions in coord_list:
                            script.write('        [{}, {}, {}, {}, {}, {}, {}, {}],\n'.format(positions[4],
                                                                                              positions[1],
                                                                                              positions[2],
                                                                                              x_width, y_width,
                                                                                              x_step, y_step,
                                                                                              dwell))

        except IOError:
            return

        return
