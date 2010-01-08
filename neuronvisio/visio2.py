# * Copyright (C) Wed Jan  6 10:17:03 GMT 2010 - Michele Mattioni:
# *  
# * This file is part of NeuronVisio
# * 
# * NeuronVisio is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
#
# * NeuronVisio is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
#
# * You should have received a copy of the GNU General Public License
# * along with NeuronVisio.  If not, see <http://www.gnu.org/licenses/>.

""":synopsis: 3D Visual operations

Contain all the 3D operations.
"""

from PyQt4 import QtGui

from enthought.mayavi import mlab
from enthought.tvtk.tools import visual

from neuron import h

class Visio(object):
    
    def __init__(self):
        
        self.fig = mlab.figure(size=(500,500))
        # Tell visual to use this as the viewer.
        visual.set_viewer(self.fig)
        
        # Needed when user pick the cylinder from visio and 
        # we need to get the section
        self.cyl2sec = {}
        
        # Needed to update the value of a cyl bound to a section
        self.sec2cyl = {}
        
        self.selected_cyl = None # Used for storing the cyl when picked
        self.vecRefs = []
        
        
    def draw_model(self, color, selected_sec=None, selected_color=None):
        """Draw the model.
        Params:
        controls - the main gui obj."""
        
        # Draw the new one
        h.define_shape()
        num_sections = 0

        # Redraw the model
        
        # Delete all the object
        # for all the cyl
        #    cyl.visibility = False
        # del cylinder list
        
        
        for sec in h.allsec():
            if selected_sec is not None:
                if sec.name() == selected_sec.name():
                    self.draw_section(sec, selected_color)
            else:
                self.draw_section(sec, color)
    
    def draw_section(self, sec, color):
        """Draw the section with the optional color 
        and add it to the dictionary cyl2sec
        
        :param sec: Section to draw
        :param color: tuple for the color in RGB value. i.e.: (0,0,1) blue"""
        
        # If we already draw the model we don't have to get the coords anymore.
        cyl = None     
        # We need to retrieve only if it's not draw
        

        if sec not in self.sec2cyl.keys():
            
            print ("Drawing sec %s, %s" %(sec.name(), sec))
            coords = self.retrieve_coordinate(sec)
            x_ax = coords['x1'] -coords['x0']
            y_ax = coords['y1'] -coords['y0']
            z_ax = coords['z1'] -coords['z0']
             
            cyl = visual.Cylinder(pos=(coords['x0'],coords['y0'],coords['z0']), 
                      axis=(x_ax,y_ax,z_ax), radius=sec.diam/2., length=sec.L)
            
            self.sec2cyl[sec.name()] = cyl #Name for Hoc compability
            self.cyl2sec[cyl] = sec    
        else:
            cyl = self.sec2cyl[sec.name()]
            
        cyl.color = (color.red()/255., color.green()/255., color.blue()/255.)
    
    
    def calc_offset(self, start_v, end_v, v):
        """Calculate the offset for the gradient 
        according to the input variable"""
        
        range = abs(start_v - end_v)
        delta = abs(start_v - v)
        # range : delta = 1 : offset
        offset = delta/range
        return offset
    
    def calculate_gradient(self, var_value, start_value, start_col, 
                           end_value, end_col):
        """Calculate the color in a gradient given the start and the end
        
        params:
        var_value - The value read from the vector
        start_value - the initial value for the var
        end_value - the final value for the var
        start_col - the starting color for the linear gradient
        end_col - the final color for the linear gradient"""
        
        
        offset = self.calc_offset(start_value, end_value, var_value)
 
#        print "Start_value: %f, var_value: %f, end_value: %f, offset \
#        %f" %(start_value, var_value, end_value, offset)
        
        start_col = self._rgb(start_col)
        end_col = self._rgb(end_col)
        col = [0, 0, 0]
        for i, primary in enumerate(col):
            col[i] = (end_col[i] - start_col[i]) * offset + start_col[i] 
                                                                           
        #print "start %s, end %s Calculated color %s" % (start_col, end_col, col)
        return QtGui.QColor(col[0],col[1],col[2])
    
    def show_variable_timecourse(self, var, time_point, start_value, 
                                 start_col, end_value, end_col, vecRefs):
        """Show an animation of all the section that have 
        the recorded variable among time"""
        
        for vecRef in vecRefs:
            if vecRef.vecs.has_key(var):
                vec = vecRef.vecs[var]
                var_value = vec[time_point]
                
                ## Use it to retrieve the value from the gradient with the index
                color = self.calculate_gradient(var_value, start_value, 
                                                start_col, end_value, 
                                                end_col)
                
                self.draw_section(vecRef.sec, color=color)
        
    def retrieve_coordinate(self, sec):
        """Retrieve the coordinates of the section"""
        coords = {}
        sec.push()
        coords['x0'] = h.x3d((h.n3d()- h.n3d()))
        coords['x1'] = h.x3d((h.n3d()- 1))
        coords['y0'] = h.y3d((h.n3d()- h.n3d()))
        coords['y1'] = h.y3d((h.n3d()- 1))
        coords['z0'] = h.z3d((h.n3d()- h.n3d()))
        coords['z1'] = h.z3d((h.n3d()- 1))
        h.pop_section()
        return coords
    
    def _rgb(self, qcolor):
        return (qcolor.red(), qcolor.green(), qcolor.blue())