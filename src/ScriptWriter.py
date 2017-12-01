import datetime

class FlyScanScriptWriter(object):

    def __init__(self):

        self.file_template = "/home/beams/USERBNP/scripts/roehrig/CoordinateTransforms/src/BNP_batch_flyscan_with_z_template.py"
        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def write_script(self, file_name, coord_list, x_width_list, y_width_list, x_step_list, y_step_list, dwell_list):
        """
        This function will create a python script for executing a series of fly scans.
        It uses a template file and adds scan parameters that the user has entered.

        :param file_name:    The name of the python file to create, including path.
        :type  file_name:    str
        :param coord_list:   A list of positions to be used for the scan.
        :type  coord_list:   list of float tuples
        :param x_width_list: The width of the scan in the X direction.
        :type  x_width_list: list of floats
        :param y_width_list: The width of the scan in the Y direction.
        :type  y_width_list: list of floats
        :param x_step_list:  The size of each pixel in the X direction.
        :type  x_step_list:  list of floats
        :param y_step_list:  The size of each pixel in the Y direction.
        :type  y_step_list:  list of floats
        :param dwell_list:   The amount of time to collect data at each pixel.
        :type  dwell_list:   list of floats
        :return:             None
        """

        try:
            with open(file_name, 'w') as script, open(self.file_template, 'r') as template:
                for line in template:
                    script.write(line)
                    if line == "scans = [\n":
                        for positions, row in zip(coord_list, range(len(x_width_list))):
                            script.write('        [{}, {}, {}, {}, {}, {}, {}, {}],\n'.format(positions[4],
                                                                                              positions[5],
                                                                                              positions[2],
                                                                                              x_width_list[row],
                                                                                              y_width_list[row],
                                                                                              x_step_list[row],
                                                                                              y_step_list[row],
                                                                                              dwell_list[row]))

        except IOError as e:
            print(e)
            return

        return


class ScriptLogWriter(object):

    def __init__(self):

        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def add_scans(self, file_name, coord_list, x_width_list, y_width_list, x_step_list, y_step_list, dwell_list):
        """
        This function will create a log file of scan parameters.

        :param file_name:    The name of the file to create, including path.
        :type  file_name:    str
        :param coord_list:   A list of positions to be used for the scan.
        :type  coord_list:   list of float tuples
        :param x_width_list: The width of the scan in the X direction.
        :type  x_width_list: list of floats
        :param y_width_list: The width of the scan in the Y direction.
        :type  y_width_list: list of floats
        :param x_step_list:  The size of each pixel in the X direction.
        :type  x_step_list:  list of floats
        :param y_step_list:  The size of each pixel in the Y direction.
        :type  y_step_list:  list of floats
        :param dwell_list:   The amount of time to collect data at each pixel.
        :type  dwell_list:   list of floats
        :return:             None
        """

        try:
            with open(file_name, 'a') as log_file:
                log_file.write('{}\n'.format(datetime.datetime.now()))
                for positions, row in zip(coord_list, range(len(x_width_list))):
                    log_file.write('[{}, {}, {}, {}, {}, {}, {}, {}],\n'.format(positions[4],
                                                                                positions[5],
                                                                                positions[2],
                                                                                x_width_list[row],
                                                                                y_width_list[row],
                                                                                x_step_list[row],
                                                                                y_step_list[row],
                                                                                dwell_list[row]))

        except IOError:
            return

        return
