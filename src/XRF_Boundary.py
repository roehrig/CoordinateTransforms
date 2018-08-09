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


import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class XRFBoundary(object):

    def __init__(self):

        self.file_names = {}
        self.theta = []             # A list of rotation stage positions from the scan.
        self.hdf_files = []         # A list of hdf5 files that make up the scan data.
        self.element = None
        self.element_index = 0
        self.element_list = []
        self.bounds = {}
        self.bounds_positions = []
        self.projections = []

        return

    # Searches for path, files, and projection angles.
    def open_files(self, path, files, stage_pv):
        """
        This function will iterate over all .hd5 files in the supplied path and will create three lists.
        These lists are of those same file names, h5py file objects, and sample rotation stage angles.

        :param path:     A string that contains the full path to the files of interest.
        :type  path:     str
        :param files:    A list of files selected by the user.
        :type  files:    list
        :param stage_pv: The EPICS PV that is associated with the rotation stage.
        :type  stage_pv: str
        :return:
        """

        # Create a list of files in the given directory
        file_names = {}
        file_names[0], file_names[1], theta_array, hdf_files = [], [], [], []

        # Encode the stage_pv value into binary format.
        byte_stage_pv = stage_pv.encode('ascii')

        # Iterate through each file in the list
        for file in files:
            # If the file has the extension .h5, add the file name to a list and add
            # the file name with full path to another list.
            if file.endswith('.h5'):
                full_path = os.path.join(path, file)
                file_names[0].append(file)
                file_names[1].append(full_path)
                # Create a File object for each file, make it read only.
                temp_file = h5py.File(full_path, 'r')
                hdf_files.append(temp_file)
                # Search for the angle of the sample stage for this data set.
                # Add that value to an array.
                data_set = temp_file['MAPS']['extra_pvs']
                pv_index = np.where(data_set[0]==byte_stage_pv)
                if len(pv_index[0]) > 0:
                    theta = float(data_set[1][pv_index[0][0]])
                    theta_array = np.append(theta_array, theta)

        self.file_names = file_names
        self.theta = theta_array
        self.hdf_files = hdf_files

        return

    def create_element_list(self):
        """
        This function creates a list of element names for which data was saved.

        :return:
        """

        if self.hdf_files:
            elem_list = list(self.hdf_files[0]['MAPS']['channel_names'][:])
            for elem in elem_list:
                self.element_list.append(elem.decode('ascii'))
        else:
            print('No files to create list from.')

        return

    def get_element_list(self):
        """
        This function returns the element list generated by create_element_list().

        :return:
        """

        return self.element_list

    def get_element_index(self, element):
        """
        This function will find the position in the list of channel names saved in the hdf file that
        corresponds to the desired element and return that value.

        :param element: The element to find.
        :type  element: str
        :return:
        """

        elem_list = list(self.hdf_files[0]['MAPS']['channel_names'][:])
        elem_index = elem_list.index(element.encode('ascii'))

        return elem_index

    def get_hdf_file_list(self):
        """
        This function returns the list of hdf file objects.

        :return:
        """

        return self.hdf_files

    def get_image_boundaries(self):
        """
        This function returns the 2 dimensional list of boundary positions and the corresponding rotation stage
        position.

        :return:
        """

        return self.bounds_positions

    def calc_xy_bounds(self, coefficient, element_index):

        """
        This function will find the outer boundaries of the sample in each of the scan files that are selected by the
        user.

        :param coefficient:
        :type  coefficient: int
        :param element_index:
        :type  element_index: int
        :return:
        """

        bounds = {}
        theta_array_length = len(self.theta)
        bounds[0] = np.zeros(theta_array_length)  # x left edge
        bounds[1] = np.zeros(theta_array_length)  # x right edge
        bounds[2] = np.zeros(theta_array_length)  # y top edge
        bounds[3] = np.zeros(theta_array_length)  # y bottom edge
        bounds[4] = self.theta

        # Creates a 2D array of dimension (number of lines) x (number of pixels)
        tmp = self.hdf_files[0]["MAPS"]["XRF_roi"][element_index]
        dim_x = len(tmp[0])
        dim_y = len(tmp)

        count = 0

        # This block loops once for each scan angle.
        # The loops counts over an array of indices that represent the
        # self.theta list in sorted order by angle.
        for i in np.argsort(self.theta):
            count = count + 1
            # Replace all values of NaN with a zero.
            projection = np.nan_to_num(self.hdf_files[i]["MAPS"]["XRF_roi"][element_index])
            self.projections.append(projection)
            # Create two arrays of the x and y positions from the scan.
            x_positions = self.hdf_files[i]["MAPS"]["x_axis"][:]
            y_positions = self.hdf_files[i]["MAPS"]["y_axis"][:]

            # Calculate background noise/coeff, edges, width, and center

            # Create an array where each element is a sum of a column in the scan data.
            # It will be a 1D array of size equal to the number of columns.
            column_sums = np.sum(projection, axis=0) / dim_y
            # Create an array where each element is a sum of a row in the scan data.
            # It will be a 1D array of size equal to the number of rows.
            row_sums = np.sum(projection, axis=1) / dim_x
            # Find the mean of the first two elements of the sum of columns.
            noise = np.mean(np.sort(column_sums[column_sums > 0])[:2])

            scale_factor = coefficient / 100

            # Create an array that is the columnsort array in reverse order.
            temp_column_array = np.sort(column_sums)[::-1]
            # Find the mean of the first two elements of the temp_column_array array.
            upper_thresh_col = np.mean(temp_column_array[:2])
            diff_col = upper_thresh_col - noise
            thresh_col = diff_col * scale_factor + noise

            # Create an array that is the rowsort array in reverse order.
            temp_row_array = np.sort(row_sums)[::-1]
            # Find the mean of the first two elements of the temp_row_array array.
            upper_thresh_row = np.mean(temp_row_array[:2])
            diff_row = upper_thresh_row - noise
            thresh_row = diff_row * scale_factor + noise

            left_boundary = 0
            right_boundary = 0
            top_boundary = 0
            bottom_boundary = 0

            # Find left edge of the image.
            for j in range(len(column_sums)):
                if column_sums[j] > thresh_col:
                    left_boundary = j
                    # Save the column index for the left boundary of the image.
                    bounds[0][i] = left_boundary
                    break
            # Find right edge image.
            for k in range(len(column_sums)):
                if column_sums[len(column_sums) - k - 1] > thresh_col:
                    right_boundary = len(column_sums) - k - 1
                    # Save the column index of the right boundary of the image.
                    bounds[1][i] = right_boundary
                    break
            # Find top edge of the image.
            for l in range(len(row_sums)):
                if row_sums[l] > thresh_row:
                    top_boundary = l
                    bounds[2][i] = top_boundary
                    break
            # Find bottom edge of the image.
            for m in range(len(row_sums)):
                if row_sums[len(row_sums) - m - 1] > thresh_row:
                    bottom_boundary = len(row_sums) - m - 1
                    bounds[3][i] = bottom_boundary
                    break

            # boundary points
            x_left = round(x_positions[left_boundary], 4)
            x_right = round(x_positions[right_boundary], 4)
            x_center = round((x_right + x_left) / 2, 4)
            x_width = round(x_right - x_left, 4)
            y_top = round(y_positions[top_boundary], 4)
            y_bottom = round(y_positions[bottom_boundary], 4)
            y_center = round((y_top + y_bottom) / 2, 4)
            y_width = round(y_bottom - y_top, 4)
            x_pos_temp = list([self.theta[i], x_center, x_width, y_center, y_width])
            self.bounds_positions.append(x_pos_temp)

        # Creates and writes to file
        out_pos = open('xyBounds.txt', 'w')
        out_pos.write('angle x_center x_width y_center y_width \n')
        format_string = '{angle:.3f}, {x_center:.3f}, {x_width:.3f}, {y_center:.3f}, {y_width:.3f},\n'
        for i in self.bounds_positions:
            format_dict = {'angle': i[0], 'x_center': i[1], 'x_width': i[2],
                           'y_center': i[3], 'y_width': i[4]}
            out_pos.write(format_string.format(**format_dict))
        out_pos.close()

        theta_text = open('theta_text.txt', 'w')
        for i in np.argsort(self.theta):
            theta_text.write((str(self.file_names[0][i]) + ', '))
            theta_text.write(str(self.theta[i]))
            theta_text.write('\n')
        theta_text.close()

        self.bounds = bounds

        return

    def show_roi_box(self):

        """
        Display images from scan data and add a box to indicate the sample boundaries found in calc_xy_bounds().

        :return:
        """
        x_pos = self.hdf_files[0]["MAPS"]["x_axis"][:]
        y_pos = self.hdf_files[0]["MAPS"]["y_axis"][:]
        temp_list1, temp_list2 = [], []
        for i in range(1, len(x_pos)):
            diff = x_pos[i] - x_pos[i - 1]
            temp_list1.append(diff)
        for i in range(1, len(y_pos)):
            diff = y_pos[i] - y_pos[i - 1]
            temp_list2.append(diff)

        box_width = list(np.array(self.bounds[1]) - np.array(self.bounds[0]))
        box_height = list(np.array(self.bounds[3]) - np.array(self.bounds[2]))
        theta = np.sort(self.theta)

        # Create new window for every 30 images, applies bounding box
        frames = 5 * 6
        figs = {}
        counter = 0
        for i in np.argsort(self.theta):
            counter = counter + 1
            projection = self.projections[i]
            for j in range(int(len(theta) / frames) + (len(theta) % frames > 0)):
                j = j + 1
                ax = plt.subplot(5, 6, counter - (int((counter - 1) / frames)) * frames)
                if counter == (j - 1) * frames:
                    figs['fig{}'.format(j)] = plt.subplots(1)
                if frames * (j - 1) < counter <= frames * j:
                    plt.imshow(projection, interpolation='nearest')
                    rect = patches.Rectangle((self.bounds[0][i], self.bounds[2][i]), box_width[i], box_height[i],
                                              linewidth=2, edgecolor='r', facecolor='none')
                    ax.add_patch(rect)
                    plt.axis('off')
                    plt.tight_layout()
                    plt.subplots_adjust(wspace=0.1, hspace=0.2)
                    plt.title(str(self.theta[i]))
        plt.show()

        return
