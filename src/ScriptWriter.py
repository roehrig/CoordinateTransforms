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

import datetime
import os


class FlyScanScriptWriter(object):

    def __init__(self):

        self.file_template = "/home/beams/USERBNP/scripts/roehrig/CoordinateTransforms/src/BNP_batch_flyscan_with_z_template.py"

        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def set_template_file(self, file_name):

        self.file_template = file_name

        return

    def set_file_permissions(self, file_name, mask):

        os.chmod(file_name, mask)

    def write_script(self, file_name, coord_list, x_width_list, y_width_list, x_step_list, y_step_list, dwell_list,
                     use_theta=False, use_z=False):
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
        :param use_theta:    Should the theta value be included in the scan script.
        :type  use_theta:    bool
        :param use_z         Should the Z value be included in the scan script.
        :type  use_z         bool
        :return:             None
        """

        format_string = '        [{X:.3f}, {Y:.3f}, {x_width}, {y_width}, {x_step}, {y_step}, {dwell}],\n'

        if use_z:
            index = format_string.find('{x_width}')
            format_string = format_string[:index] + '{Z:.3f}, ' + format_string[index:]

        if use_theta:
            index = format_string.find('{x_width}')
            format_string = format_string[:index] + '{Theta:.3f}, ' + format_string[index:]

        try:
            with open(file_name, 'w') as script, open(self.file_template, 'r') as template:
                for line in template:
                    script.write(line)
                    if line == "scans = [\n":
                        for positions, row in zip(coord_list, range(len(x_width_list))):
                            format_dict = {'X': positions[4], 'Y': positions[5], 'x_width': x_width_list[row],
                                           'y_width': y_width_list[row], 'x_step': x_step_list[row],
                                           'y_step': y_step_list[row], 'dwell': dwell_list[row]}

                            if use_z:
                                format_dict['Z'] = positions[2]

                            if use_theta:
                                format_dict['Theta'] = positions[3]

                            script.write(format_string.format(**format_dict))

        except IOError as e:
            print(e)
            return
        except FileNotFoundError as e:
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

    def add_scans(self, file_name, coord_list, x_width_list, y_width_list, x_step_list, y_step_list, dwell_list,
                  use_theta=False, use_z=False):
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
        :param use_theta:    Should the theta value be included in the scan script.
        :type  use_theta:    bool
        :param use_z         Should the Z value be included in the scan script.
        :type  use_z         bool
        :return:             None
        """

        format_string = '        [{X:.3f}, {Y:.3f}, {x_width}, {y_width}, {x_step}, {y_step}, {dwell}],\n'

        if use_z:
            index = format_string.find('{x_width}')
            format_string = format_string[:index] + '{Z:.3f}, ' + format_string[index:]

        if use_theta:
            index = format_string.find('{x_width}')
            format_string = format_string[:index] + '{Theta:.3f}, ' + format_string[index:]

        try:
            with open(file_name, 'a') as log_file:
                log_file.write('{}\n'.format(datetime.datetime.now()))
                for positions, row in zip(coord_list, range(len(x_width_list))):
                    format_dict = {'X': positions[4], 'Y': positions[5], 'x_width': x_width_list[row],
                                   'y_width': y_width_list[row], 'x_step': x_step_list[row],
                                   'y_step': y_step_list[row], 'dwell': dwell_list[row]}

                    if use_z:
                        format_dict['Z'] = positions[2]

                    if use_theta:
                        format_dict['Theta'] = positions[3]

                    log_file.write(format_string.format(**format_dict))

        except IOError:
            return

        return
