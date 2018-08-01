import os
import sys
import h5py
import numpy as np
import string
#from PIL import Image
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import argparse


class XRFBoundary(object):

    def __init__(self):

        self.file_names = {}
        self.theta = []
        self.hdf_files = []
        self.element = None
        self.element_index = 0
        self.element_list = []
        self.bounds = {}
        self.padding = {}
        self.projections = []

        return

    # Searches for path, files, and projection angles.
    def open_files(self, path, files, stage_pv):
        """
        This function will iterate over all .hd5 files in the supplied path and will create three lists.
        These lists are of those same file names, h5py file objects, and sample rotation stage angles.

        :param path:  A string that contains the full path to the files of interest.
        :type path:   str
        :return:
        """

        # Create a list of files in the given directory
#        files = os.listdir(path)
        file_names = {}
        file_names[0], file_names[1], theta_index, hdf_files = [], [], [], []

        # Iterate through each file in the list
        for file in files:
            # If the file has the extension .h5, add the file name to a list and add
            # the file name with full path to another list.
            if file.endswith('.h5'):
                file_names[0].append(file)
                file_names[1].append(os.path.join(path, file))

        # Iterate through each .h5 file.
        for i in range(0, len(file_names[1])):
            # Create a File object for each file, make it read only.
            temp_file = h5py.File(os.path.abspath(file_names[1][i]), 'r')
            hdf_files.append(temp_file)
            # Search for the angle of the sample stage for this data set.
            # Add that value to an array.
            data_set = temp_file['MAPS']['extra_pvs_as_csv']
            for item in data_set:
                # Data is stored in a binary format.  It must be decoded to get a string.
                item_string = item.decode('ascii')
                if stage_pv in item_string:
                    index = item_string.rfind(',')
                    theta_temp = round(float(item_string[index + 1:]))
                    theta_index = np.append(theta_index, theta_temp)

        self.file_names = file_names
        self.theta = theta_index
        self.hdf_files = hdf_files

        return

    def create_element_list(self):

        if self.hdf_files:
            elem_list = list(self.hdf_files[0]['MAPS']['channel_names'][:])
            for elem in elem_list:
                self.element_list.append(elem.decode('ascii'))
        else:
            print('No files to create list from.')

        return

    def get_element_list(self):

        return self.element_list

    def get_element_index(self, element):
        elem_list = list(self.hdf_files[0]['MAPS']['channel_names'][:])
        elem_index = elem_list.index(element.encode('ascii'))
        return elem_index

    def calc_xy_bounds(self, path, coefficient, stage_pv, element_index):
#        self.file_names, self.theta, self.hdf_files = self.open_files(path, stage_pv)

        # optional element argument bounds that element
#        element = ''.join(element).lower()
#        elemlst = list(self.hdf_files[0]['MAPS']['channel_names'][:])
#        for i in range(len(elemlst)):
#            elemlst[i] = str(elemlst[i]).lower()
#        if element == '':
#            elemindex = np.random.randint(len(elemlst))
#            element = elemlst[elemindex]
#            print('No element specified, random element: ')
#        if element in elemlst:
#            elemindex = elemlst.index(element)
#            print(elemlst[elemindex], 'is selected')
#            self.element = element
#        else:
#            print(element, 'xbounds', 'Not a valid option. List of channels are: ')
#            print(elemlst)
#            elemindex = np.random.randint(len(elemlst))
#            element = elemlst[elemindex]
#            print('random element :', element, ' is active')

        '''determines the largest dimensions of projection, applies padding to other all other
        smaller-sized projections to produce images of equal dimensions'''
        proj = []
        dimx, dimy = 0, 0
        xy_bounds = []
        padding = {}
        bounds = {}
        padding[0] = []  # x1 padding left
        padding[1] = []  # x2 padding right
        padding[2] = []  # y1 padding top
        padding[3] = []  # y2 padding bottom
        padding[4] = dimx  # maximum x dimension
        padding[5] = dimy  # maximum y dimension
        theta_array_length = len(self.theta)
        bounds[0] = np.zeros(theta_array_length)  # x left edge
        bounds[1] = np.zeros(theta_array_length)  # x right edge
        bounds[2] = np.zeros(theta_array_length)  # y top edge
        bounds[3] = np.zeros(theta_array_length)  # y bottom edge
        bounds[4] = self.theta

        for i in range(0, len(self.theta)):
            tmp = self.hdf_files[i]["MAPS"]["XRF_roi"][element_index]
            if dimx <= len(tmp[0]):
                dimx = len(tmp[0])
            if dimy <= len(tmp):
                dimy = len(tmp)

        for i in range(1, theta_array_length + 1):
            projection = self.hdf_files[i - 1]["MAPS"]["XRF_roi"][element_index]
            roi_length = len(projection[0])
            if roi_length <= dimx:
                dx = dimx - roi_length
                half_dx = int(dx / 2)
                projection = np.append(projection, np.zeros((len(projection), half_dx)), axis=1)
                projection = np.append(np.zeros((len(projection), half_dx + dx % 2)), projection, axis=1)
                padding[0].append(half_dx)
                padding[1].append(half_dx + dx % 2)

            if len(projection) <= dimy:
                dy = dimy - len(projection)
                half_dy = int(dy / 2)
                projection = np.append(np.zeros((half_dy, roi_length)), projection, axis=0)
                projection = np.append(projection, np.zeros((half_dy + dy % 2, roi_length)), axis=0)
                padding[2].append(half_dy)
                padding[3].append(half_dy + dy % 2)
            proj.append(projection)

        '''uses h5py for data handling, sort based on proj angle '''
        cnt = 0
        for i in np.argsort(self.theta):
            cnt = cnt + 1
            projections = np.nan_to_num(proj[i])
            xPos = self.hdf_files[i]["MAPS"]["x_axis"][:]
            yPos = self.hdf_files[i]["MAPS"]["y_axis"][:]

            '''	calculate background noise/coeff, edges, width, and center'''
            columnsums = np.sum(projections, axis=0) / (dimy - padding[2][i] - padding[3][i])
            rowsums = np.sum(projections, axis=1) / (dimx - padding[0][i] - padding[1][i])
            noise = np.mean(np.sort(columnsums[columnsums > 0])[:2])

            tmpcol = np.sort(columnsums)[::-1]
            upperThreshCol = np.mean(tmpcol[:2])
            diffcol = upperThreshCol - noise
            scale_factor = int(coefficient / 100)
            threshcol = diffcol * scale_factor + noise

            tmprow = np.sort(rowsums)[::-1]
            upperThreshRow = np.mean(tmprow[:2])
            diffrow = upperThreshRow - noise
            threshrow = diffrow * scale_factor + noise

            # find left edge
            for j in range(len(columnsums)):
                var = np.sort(projections[:, j])[::-1]
                px1 = np.max(projections[:, j])
                if columnsums[j] > threshcol:
                    boundx1 = j - padding[0][i]
                    bounds[0][i] = boundx1
                    break
            # find right edge
            for k in range(len(columnsums)):
                px2 = np.max(projections[:, -k - 1])
                if columnsums[len(columnsums) - k - 1] > threshcol:
                    boundx2 = len(columnsums) - k - 1 - padding[1][i]
                    bounds[1][i] = boundx2
                    break
            # find top edge
            for l in range(len(rowsums)):
                px3 = np.max(projections[l, :])
                if rowsums[l] > threshrow:
                    boundy1 = l - padding[2][i]
                    bounds[2][i] = boundy1
                    break
            # find bottom edge
            for m in range(len(rowsums)):
                px4 = np.max(projections[-m - 1, :])
                if rowsums[len(rowsums) - m - 1] > threshrow:
                    boundy2 = len(rowsums) - m - 1 - padding[3][i]
                    bounds[3][i] = boundy2
                    break

            # boundary points
            x_left = round(xPos[boundx1], 4)
            x_right = round(xPos[boundx2], 4)
            x_center = round((x_right + x_left) / 2, 4)
            x_width = round(x_right - x_left, 4)
            y_top = round(yPos[boundy1], 4)
            y_bottom = round(yPos[boundy2], 4)
            y_center = round((y_top + y_bottom) / 2, 4)
            y_width = round(y_bottom - y_top, 4)
            xpostemp = list([self.theta[i], x_center, x_width, y_center, y_width])
            xy_bounds.append(xpostemp)

        '''creates and writes to file'''
        outPos = open('xyBounds.txt', 'w')
        outPos.write('angle x_center x_width y_center y_width \n')
        for i in xy_bounds:
            outPos.write(str(i)[1:-1])
            outPos.write('\n')
        outPos.close()

        thetatxt = open('thetatxt.txt', 'w')
        for i in np.argsort(self.theta):
            thetatxt.write((str(self.file_names[0][i]) + ', '))
            thetatxt.write(str(self.theta[i]))
            thetatxt.write('\n')
        thetatxt.close()

        self.bounds = bounds
        self.padding = padding
        self.projections = proj

        return

    def show_roi_box(self, path=None, coeff=None, element=None):
#        file_names, theta_index, hdf_files = self.open_files(path)
#        element = ''.join(element).lower()
#        elemlst = list(hdf_files[0]["MAPS"]["channel_names"][:])
#        for i in range(len(elemlst)):
#            elemlst[i] = str(elemlst[i]).lower()

#        if element == '':
#            elemindex = np.random.randint(len(elemlst))
#            element = elemlst[elemindex]
#            print('No element specified, random element: ')
#        if element in elemlst:
#            elemindex = elemlst.index(element)
#            print(elemlst[elemindex], 'is selected')
#        else:
#            print(element, 'xbounds', "Not a valid option. List of channels are: ")
#            print(elemlst)
#            elemindex = np.random.randint(len(elemlst))
#            element = elemlst[elemindex]
#            print('random element :', element, ' is active')

#        bounds, padding, projections = xybound(path, coeff, element)

        '''calculate box parameters, display bounding box + figure '''
        xPos = self.hdf_files[0]["MAPS"]["x_axis"][:]
        yPos = self.hdf_files[0]["MAPS"]["y_axis"][:]
        tmplst1, tmplst2 = [], []
        for i in range(1, len(xPos)):
            diff = xPos[i] - xPos[i - 1]
            tmplst1.append(diff)
        for i in range(1, len(yPos)):
            diff = yPos[i] - yPos[i - 1]
            tmplst2.append(diff)

        dx = round(sum(tmplst1) / len(tmplst1), 5)
        dy = round(sum(tmplst2) / len(tmplst2), 5)
        boxWidth = list(np.array(self.bounds[1]) - np.array(self.bounds[0]))
        boxheight = list(np.array(self.bounds[3]) - np.array(self.bounds[2]))
        theta = np.sort(self.theta)

        '''create new window for every 30 images, applies bounding box'''
        frames = 5 * 6
        figs = {}
        counter = 0
        for i in np.argsort(self.theta):
            counter = counter + 1
            projection = self.projections[i]
            for j in range(int(len(theta) / frames) + (len(theta) % frames > 0)):
                j = j + 1
                ax = plt.subplot(5, 6, counter - ((counter - 1) / frames) * frames)
                if counter == (j - 1) * frames:
                    figs['fig{}'.format(j)] = plt.subplots(1)
                if frames * (j - 1) < counter <= frames * j:
                    # plt.imsave(str(fileNames[1][i])+'.tiff', projection,cmap='gray')
                    plt.imshow(projection, interpolation='nearest')
                    rect = patches.Rectangle(((self.bounds[0][i] + self.padding[0][i]), self.bounds[2][i] +
                                               self.padding[2][i]), boxWidth[i], boxheight[i], linewidth=2,
                                               edgecolor='r', facecolor='none')
                    ax.add_patch(rect)
                    plt.axis('off')
                    plt.tight_layout()
                    plt.subplots_adjust(wspace=0.1, hspace=0.2)
                    plt.title(str(self.theta[i]))
        plt.show()

        return
