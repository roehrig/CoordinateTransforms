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

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pylab import *
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *
class XRFBoundary(QWidget):
    roiChangedSig = pyqtSignal(list, name = "roiChangedSig" )
    def __init__(self):
        super(XRFBoundary, self).__init__()

        # def __init__(self):

        self.file_names = {}
        self.theta = []             #  A list of rotation stage positions from the scan.
        self.hdf_files = []         #  A list of hdf5 files that make up the scan data.
        self.element = None
        self.element_index = 0
        self.element_list = []
        self.bounds = {}
        self.bounds_positions = []
        self.coarse_positions = []
        self.projections = []

        return

    #  Searches for path, files, and projection angles.
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

        #  Create a list of files in the given directory
        file_names = {}
        file_names[0], file_names[1], theta_array, hdf_files = [], [], [], []

        #  Encode the stage_pv value into binary format.
        byte_stage_pv = stage_pv.encode('ascii')

        #  Iterate through each file in the list
        for file in files:
            #  If the file has the extension .h5, add the file name to a list and add
            #  the file name with full path to another list.
            if file.endswith('.h5'):
                full_path = os.path.join(path, file)
                file_names[0].append(file)
                file_names[1].append(full_path)
                #  Create a File object for each file, make it read only.
                temp_file = h5py.File(full_path, 'r')
                hdf_files.append(temp_file)
                #  Search for the angle of the sample stage for this data set.
                #  Add that value to an array.
                data_set = temp_file['MAPS']['extra_pvs']
                pv_index = np.where(data_set[0]==byte_stage_pv)
                if len(pv_index[0]) > 0:
                    theta = float(data_set[1][pv_index[0][0]])
                    theta_array = np.append(theta_array, theta)

        sortedindx = np.argsort(theta_array)
        theta = theta_array[sortedindx]
        file_names[0] = np.array(file_names[0])[sortedindx]
        file_names[1] = np.array(file_names[1])[sortedindx]

        self.file_names = file_names
        self.theta = theta
        self.hdf_files = hdf_files
        return

    def create_element_list(self):
        """
        This function creates a list of element names for which data was saved.

        :return:
        """
        self.element_list = []
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

        return self.coarse_positions

    def get_boundaries(self):
        """
        This function returns a dictionary containing the interpolated motor position boundaries

        :return:
        """
        return self.bounds_positions

    def calc_xy_bounds(self, coefficient, element_index, bound_y = True):

        """
        This function will find the outer boundaries of the sample in each of the scan files that are selected by the
        user. Boundaries are in pixel units. 

        :param coefficient: 
        :type  coefficient: int
        :param element_index:
        :type  element_index: int
        :return:
        """

        bounds = {}
        theta_array_length = len(self.theta)
        bounds[0] = np.zeros(theta_array_length)  #  x left edge
        bounds[1] = np.zeros(theta_array_length)  #  x right edge
        bounds[2] = np.zeros(theta_array_length)  #  y top edge
        bounds[3] = np.zeros(theta_array_length)  #  y bottom edge

        #  Creates a 2D array of dimension (number of lines) x (number of pixels)
        tmp = self.hdf_files[0]["MAPS"]["XRF_roi"][element_index]
        dim_x = len(tmp[0])
        dim_y = len(tmp)

        count = 0
        self.projections = []
        self.bounds = []
        #  This block loops once for each scan angle.
        #  The loops counts over an array of indices that represent the
        #  self.theta list in sorted order by angle.
        for i in range(len(self.theta)):
            count += 1
            #  Replace all values of NaN with a zero.
            projection = np.nan_to_num(self.hdf_files[i]["MAPS"]["XRF_roi"][element_index])
            self.projections.append(projection)
            #  Create two arrays of the x and y positions from the scan.
            x_positions = self.hdf_files[i]["MAPS"]["x_axis"][:]
            y_positions = self.hdf_files[i]["MAPS"]["y_axis"][:]

            #  Calculate background noise/coeff, edges, width, and center
            #  Create an array where each element is a sum of a column in the scan data.
            #  It will be a 1D array of size equal to the number of columns.
            column_sums = np.sum(projection, axis=0) / dim_y
            #  Create an array where each element is a sum of a row in the scan data.
            #  It will be a 1D array of size equal to the number of rows.
            row_sums = np.sum(projection, axis=1) / dim_x
            #  Find the mean of the first two elements of the sum of columns.
            smallest_column_sum = np.sort(column_sums[column_sums>0])[:1]
            #  Find the mean of the first two elements of the sum of columns.
            smallest_row_sum = np.sort(row_sums[row_sums>0])[:1]

            # set the noise level equal to the smallest of column_sums or row_sums
            if smallest_column_sum <= smallest_row_sum:
                noise = smallest_column_sum
            else:
                noise = smallest_row_sum
                
            scale_factor = coefficient / 100

            #  Find the largest value in column_sum
            largest_column_sum = np.sort(column_sums)[::-1][:1]
            #  difference between largest_column_sum and noise
            diff_col = largest_column_sum - noise
            #  set vertical boundary threshold equal to the noise plus a fraction of diff_col
            thresh_col = diff_col * scale_factor + noise

            #  Find the largest value in row_sum
            largest_row_sum = np.sort(row_sums)[::-1][:1]
            # difference between largest_row_sum and noise
            diff_row = largest_row_sum - noise
            #  set horizontal boundary threshold equal to the noise plus a fraction of diff_row
            thresh_row = diff_row * scale_factor + noise

            left_boundary = 0
            right_boundary = 0
            top_boundary = 0
            bottom_boundary = 0

            #  Find left edge of the image.
            for j in range(len(column_sums)):

                if column_sums[j] > thresh_col:
                    left_boundary = j
                    #  Save the column index for the left boundary of the image.
                    bounds[0][i] = left_boundary
                    break
            #  Find right edge image.
            for k in range(len(column_sums)):
                if column_sums[len(column_sums) - k - 1] > thresh_col:
                    right_boundary = len(column_sums) - k - 1
                    #  Save the column index of the right boundary of the image.
                    bounds[1][i] = right_boundary
                    break
            #  Find top edge of the image.
            if bound_y:
                for l in range(len(row_sums)):
                    if row_sums[l] > thresh_row:
                        top_boundary = l
                        bounds[2][i] = top_boundary
                        break
            #  Find bottom edge of the image.
                for m in range(len(row_sums)):
                    if row_sums[len(row_sums) - m - 1] > thresh_row:
                        bottom_boundary = len(row_sums) - m - 1
                        bounds[3][i] = bottom_boundary
                        break
            else:
                for l in range(len(row_sums)):
                    top_boundary = 0
                    bounds[2][i] = top_boundary
                for m in range(len(row_sums)):
                    bottom_boundary = len(row_sums)-1
                    bounds[3][i] = bottom_boundary

        self.bounds = bounds
        return

    def calc_coarse_bounds(self):
        """
        This function finds the bounding regions of each coarse scan in physical position units.
        :return:

        """
        x_positions = self.hdf_files[0]["MAPS"]["x_axis"][:]
        y_positions = self.hdf_files[0]["MAPS"]["y_axis"][:]
        self.coarse_positions = []
        for i in range(len(self.theta)):

            x_left = round(x_positions[int(self.bounds[0][i])], 5)
            x_right = round(x_positions[int(self.bounds[1][i])], 5)
            x_center = round((x_right + x_left) / 2, 5)
            x_width = round(x_right - x_left, 5)
            y_top = round(y_positions[int(self.bounds[2][i])], 5)
            y_bottom = round(y_positions[int(self.bounds[3][i])], 5)
            y_center = round((y_top + y_bottom) / 2, 5)
            y_width = round(y_bottom - y_top, 5)
            x_pos_temp = list([self.theta[i], x_center, x_width, y_center, y_width])
            self.coarse_positions.append(x_pos_temp)        

        return self.coarse_positions

    def interpolate_bounds(self, dtheta):
        '''
        This function interpolates boundary parameters for fine scans from coarse
        scan boundary information. It selects parameters from a lookup table regardless
        of whether or not the sampeld values were original or interpolated values.

        :param dtheta: Incremental angle value between tomography scans
        :type  dtheta: float

        :return:
        '''
        self.dtheta = dtheta
        theta_coarse = self.theta
        ExFine = np.round(np.arange(self.theta[0],self.theta[-1]+0.1,0.1),2)
        fine = np.arange(self.theta[0],self.theta[-1], dtheta)
        fine = np.round(fine, 2)
        num_projections = len(fine)
        num_exFine = len(ExFine)

        self.bounds_positions = []
        x_positions = self.hdf_files[0]["MAPS"]["x_axis"][:]
        y_positions = self.hdf_files[0]["MAPS"]["y_axis"][:]

        # thes are the interpolated edges at 0.1 degree increments, they will serve as a lookup table.
        left_edge = np.zeros(num_exFine)  #  x left edge
        right_edge = np.zeros(num_exFine)  #  x right edge
        top_edge = np.zeros(num_exFine)  #  y top edge
        bottom_edge = np.zeros(num_exFine)  #  y bottom edge

        # these are the interpolated edges at the user defined angle increments.
        left_edge2 = np.zeros(num_projections)  #  x left edge
        right_edge2 = np.zeros(num_projections)  #  x right edge
        top_edge2 = np.zeros(num_projections)  #  y top edge
        bottom_edge2 = np.zeros(num_projections)  #  y bottom edge

        angle_index = []

        # pupulates scan_parameters with non-interpolated values
        for i in range(len(self.theta)):
            temp_index = int(np.where(ExFine == self.theta[i])[0])
            angle_index.append(temp_index)
            left_edge[temp_index] = x_positions[int(self.bounds[0][i])]
            right_edge[temp_index] = x_positions[int(self.bounds[1][i])]
            top_edge[temp_index] = y_positions[int(self.bounds[2][i])]
            bottom_edge[temp_index] = y_positions[int(self.bounds[3][i])]

        for i in range(num_exFine):
            if i>0 and i in angle_index:
                # calculates incremental boundary shift in position units between adjacent coarse scans.
                temp_index = int(np.where(np.array(angle_index) == i)[0][0])
                frame_difference = angle_index[temp_index] - angle_index[temp_index-1]

                diffx1 = (left_edge[i]-left_edge[angle_index[temp_index-1]])/frame_difference
                diffx2 = (right_edge[i]-right_edge[angle_index[temp_index-1]])/frame_difference
                diffy1 = (top_edge[i]-top_edge[angle_index[temp_index-1]])/frame_difference
                diffy2 = (bottom_edge[i]-bottom_edge[angle_index[temp_index-1]])/frame_difference

                for j in range(1,frame_difference):
                    # adds incremental boundary shift to frames in between coarse scans.
                    indx = i - frame_difference + j
                    left_edge[indx] = left_edge[i-frame_difference] + diffx1*j
                    right_edge[indx] = right_edge[i-frame_difference] + diffx2*j
                    top_edge[indx] = top_edge[i-frame_difference] + diffy1*j
                    bottom_edge[indx] = bottom_edge[i-frame_difference] + diffy2*j

        for i in range(num_projections):
            idx = int(np.where(ExFine == fine[i])[0][0])
            left_edge2[i] = left_edge[idx]
            right_edge2[i] = right_edge[idx]
            top_edge2[i] = top_edge[idx]
            bottom_edge2[i] = bottom_edge[idx]

        for i in range(num_projections):
            x_center = (right_edge2[i] + left_edge2[i])/2
            x_width = right_edge2[i] - left_edge2[i]
            y_center = (bottom_edge2[i] + top_edge2[i])/2
            y_width = bottom_edge2[i] - top_edge2[i]
            pos_temp = list([fine[i],x_center,x_width,y_center,y_width])
            self.bounds_positions.append(pos_temp)

        return self.bounds_positions

    def offset_bounds(self, angle_offset, left_offset, right_offset, top_offset, bottom_offset):
        for i in range(1, len(self.bounds_positions)):
            # [angle, xcenter, xwidth, ycenter, ywidth]
            self.bounds_positions[i-1][0] += angle_offset
            self.bounds_positions[i-1][1] += (self.bounds_positions[i][1] - self.bounds_positions[i-1][1])*angle_offset + (right_offset - left_offset)
            self.bounds_positions[i-1][2] += (self.bounds_positions[i][2] - self.bounds_positions[i-1][2])*angle_offset + (right_offset + left_offset)
            self.bounds_positions[i-1][3] += (self.bounds_positions[i][3] - self.bounds_positions[i-1][3])*angle_offset + (top_offset - bottom_offset)
            self.bounds_positions[i-1][4] += (self.bounds_positions[i][4] - self.bounds_positions[i-1][4])*angle_offset + (top_offset + bottom_offset)
        self.bounds_positions[-1][0] += angle_offset
        self.bounds_positions[-1][1] += (self.bounds_positions[-1][1] - self.bounds_positions[-2][1])*angle_offset + (right_offset - left_offset)
        self.bounds_positions[-1][2] += (self.bounds_positions[-1][2] - self.bounds_positions[-2][2])*angle_offset + (right_offset + left_offset)
        self.bounds_positions[-1][3] += (self.bounds_positions[-1][3] - self.bounds_positions[-2][3])*angle_offset + (top_offset - bottom_offset)
        self.bounds_positions[-1][4] += (self.bounds_positions[-1][4] - self.bounds_positions[-2][4])*angle_offset + (top_offset + bottom_offset)

        for i in range(len(self.bounds_positions)):
            self.bounds_positions[i][0] = round(self.bounds_positions[i][0], 4)
            self.bounds_positions[i][1] = round(self.bounds_positions[i][1], 4)
            self.bounds_positions[i][2] = round(self.bounds_positions[i][2], 4)
            self.bounds_positions[i][3] = round(self.bounds_positions[i][3], 4)
            self.bounds_positions[i][4] = round(self.bounds_positions[i][4], 4)
        return

    def offset_ROI_bounds(self, left_offset, right_offset, top_offset, bottom_offset):
        coarse_bounds = self.calc_coarse_bounds()
        x_pixel_size = round(coarse_bounds[0][2]/(self.projections[0].shape[1]-1), 4)
        y_pixel_size = round(coarse_bounds[0][4]/(self.projections[0].shape[0]-1), 4)

        for i in range(len(self.bounds[0])):

            self.bounds[0][i] -= int(left_offset/x_pixel_size)
            self.bounds[1][i] += int(right_offset/x_pixel_size)
            self.bounds[2][i] -= int(top_offset/y_pixel_size)
            self.bounds[3][i] += int(bottom_offset/y_pixel_size)

        return

    def show_roi_box(self):

        """
        Display images from scan data and add a box to indicate the sample boundaries found in calc_xy_bounds().

        :return:
        """
        box_width = list(np.array(self.bounds[1]) - np.array(self.bounds[0]))
        box_height = list(np.array(self.bounds[3]) - np.array(self.bounds[2]))
        theta = np.sort(self.theta)
        #  Create new window for every 30 images, applies bounding box
        rows, columns = 5,6
        frames = rows*columns
        figs = {}
        counter = 0
        for i in range(len(self.theta)):
            counter += 1
            projection = self.projections[i]
            for j in range(int(len(theta) / frames) + (len(theta) % frames > 0)):

                j += 1
                ax = plt.subplot(rows,columns, counter - (int((counter - 1) / frames)) * frames)
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
                    plt.title(str(theta[i]))
                ax.set_aspect(projection.shape[1]/projection.shape[0])
        plt.show()
        return

    def show_roi_box2(self):
        """
        Display images from scan data and add a box to indicate the sample boundaries found in calc_xy_bounds().

        :return:
        """
        #open new window containing coasre scan projections. 
        pg.setConfigOptions(imageAxisOrder='row-major')
        # app = QtGui.QApplication([])
        num_coarse_scans = len(self.theta)
        proj_w = self.projections[0].shape[1]
        proj_h = self.projections[0].shape[0]
        sqrt_length = np.sqrt(num_coarse_scans)
        cols = int(np.ceil(sqrt_length))
        rows = int(np.ceil(sqrt_length))
        xovery_scale = proj_h/proj_w

        if proj_w >= proj_h:
            ratio = proj_w//proj_h
            cols -= 1
            rows += 1
            if ratio > 3:
                ratio = 3
            screen_w = 110*ratio*cols
            screen_h = 110*rows

        if proj_w <proj_h:
            ratio = proj_h//proj_w
            cols += 1
            rows -= 1
            if ratio > 3:
                ratio = 3
            screen_w = 110*proj_w
            screen_h = 110*ratio*rows


        self.w = pg.GraphicsWindow(size=(screen_w,screen_h), border=True)
        self.w.setWindowTitle('Coarse scan ROIs')

        # self.w.scene().sigMouseClicked.connect(self.get_window)


        self.windowz = {}
        views = {}
        cntr = 0
        theta = np.sort(self.theta)
        self.box_width = list(np.array(self.bounds[1]) - np.array(self.bounds[0]))
        self.box_height = list(np.array(self.bounds[3]) - np.array(self.bounds[2]))

        for i in range(rows):
            for j in range(cols):
                if cntr == num_coarse_scans:
                    break
                else:
                    projection = self.projections[cntr]
                    self.windowz[cntr] = self.w.addLayout(row=i, col=j)
                    views[cntr,0] = self.windowz[cntr].addLabel(str(cntr)+": "+ str(theta[cntr]), row=0, col=0)
                    views[cntr,1] = self.windowz[cntr].addViewBox(row=1, col=0, lockAspect=True, enableMouse=False)
                    views[cntr,1].setAspectLocked(lock=True, ratio=xovery_scale)
                    img = pg.ImageItem(projection)
                    # img.rotate(90)
                    views[cntr,1].addItem(img)
                    views[cntr,1].disableAutoRange('xy')
                    views[cntr,1].autoRange()
                    roi = pg.RectROI([self.bounds[0][cntr], self.bounds[2][cntr]], [self.box_width[cntr], self.box_height[cntr]], pen=pg.mkPen(width=4.5, color='r'), translateSnap=True, scaleSnap=True)
                    ## handles scaling vertically from opposite edge
                    roi.addScaleHandle([0.5, 0], [0.5, 1])
                    roi.addScaleHandle([0.5, 1], [0.5, 0])
                    ## handles scaling horizonatally from opposite edge
                    roi.addScaleHandle([0, 0.5], [1, 0.5])
                    roi.addScaleHandle([1, 0.5], [0, 0.5])
                    ## handles scaling both vertically and horizontally
                    roi.addScaleHandle([1, 1], [0, 0])
                    roi.addScaleHandle([0, 0], [1, 1])
                    roi.addScaleHandle([0, 1], [1, 0])
                    roi.addScaleHandle([1, 0], [0, 1])
                    roi.sigRegionChangeFinished.connect(self.update_roi)
                    pg.mkPen(width=2)
                    views[cntr,1].addItem(roi)
                    cntr += 1

        return self.w 
        
    def update_roi(self, roi):
        self.current_x = self.w.scene().clickEvents[0].scenePos().x()
        self.current_y = self.w.scene().clickEvents[0].scenePos().y()
        self.indx = self.get_window(self.current_x, self.current_y)

        roi_left =roi.pos().x()
        roi_right = roi.pos().x() + roi.size().x()
        roi_top = roi.pos().y() + roi.size().y()
        roi_bottom = roi.pos().y()

        #check whether any of the ROI edges are out of bounds, if they are, set the ROI box
        # edge to the edge boundary and update self.bounds accordingly.

        max_x = self.projections[0].shape[1]
        max_y = self.projections[0].shape[0]
        valid_flag = True

        ## if way far left or way far right
        if ((roi_left <= 0 and roi_right<=0) or (roi_left >= max_x and roi_right>= max_x)):
            print("case 1")
            roi_left = 0
            roi_right = max_x-1
            valid_flag = False
        ## if way far above or way far below.
        if ((roi_top <= 0 and roi_bottom<=0) or (roi_top >= max_y and roi_bottom>=max_y)):
            print("case 2")
            roi_top = max_y-1
            roi_bottom = 0
            valid_flag = False
        ## if partially left
        if roi_left < 0:
            print("case 3")
            roi_left = 0
            valid_flag = False
        ##if partially right
        if roi_right >= max_x:
            print("case 4")
            roi_right = max_x-1
            valid_flag = False
        ##if partially above
        if roi_top >= max_y:
            print("case 5")
            roi_top = max_y-1
            valid_flag = False
        #if partially below
        if roi_bottom < 0:
            print("case 6")
            roi_bottom = 0
            valid_flag = False

        try:
            if valid_flag == False:
                roi.setSize([roi_right-roi_left,roi_top-roi_bottom], finish=False)
                roi.setPos(roi_left,roi_bottom, finish=False)
        except e:
            print(e)

        self.bounds[0][self.indx] = roi_left
        self.bounds[1][self.indx] = roi_right
        self.bounds[2][self.indx] = roi_bottom
        self.bounds[3][self.indx] = roi_top

        new_bounds = self.interpolate_bounds(self.dtheta)
        new_bounds = np.round(new_bounds,4).tolist()
        self.roiChangedSig.emit(new_bounds)
        return self.w

    def get_window(self, x, y):
        self.height = self.w.viewRect().height()
        self.width = self.w.viewRect().width()

        self.rows = len(self.w.ci.rows)
        self.cols = len(self.w.ci.rows[0])
        
        self.grid_x_size = self.width/self.cols
        self.grid_y_size = self.height/self.rows

        self.win_coord_x = x//self.grid_x_size
        self.win_coord_y = y//self.grid_y_size

        #gettting index from coordinates:
        indx = int(self.win_coord_y*self.cols+self.win_coord_x)
        return indx
