#!/usr/bin/env python
# -*- coding: utf-8
""" RUR-PLE: Roberge's Used Robot - a Python Learning Environment
    rur_start.py - "Main" file for RUR-PLE.
    Version 1.0
    Author: André Roberge    Copyright  2006
    andre.roberge@gmail.com
    Edited by: Robert Deloatch
"""
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# Run python in export VERSIONER_PYTHON_VERSIONER=2.5
# setenv VERSIONER_PYTHON_VERSION 2.5
# export VERSIONER_PYTHON_PREFER_32_BIT=yes

# Changes made by Robert Deloatch

# todo: consider adding support for translation of commands e.g.
# todo: ...  francais()  initialises commands equivalent like avance(), etc.
# todo: create easy install for windows (exe file)
# todo: create easy install for linux  (setup.py...)
# todo: consider adding new page in notebook for turtle graphics.

import os
import sys
import random
import wx.html as html

# Change directory so that rur-ple can be started from everywhere.
try:
    appdir = os.path.dirname(sys.argv[0])
    if appdir != '':
        os.chdir(appdir)
    sys.path.append(os.getcwd())
    from rur_py import conf
    conf.getSettings()
except OSError, e:
    print 'Cannot change to rur-ple directory.'
    sys.exit(1)

from rur_py.translation import _
import rur_py.conf as conf  # a few global variables
import rur_py.wxutils as wxutils

# do not check version when make a 'bundle' of the application
# ref: http://www.wxpython.org/docs/api/wxversion-module.html
if not hasattr(sys, 'frozen'):
    if wxutils.wxversiontuple() < (2,6):
        print _("wxPython versions less than 2.6 are not supported.")
        sys.exit(1)

import wx
import wx.lib.buttons
import wx.py as py           # For the interpreter

import rur_py.images as images # load all images
from rur_py.images import getImage
import rur_py.dialogs as dialogs # contains dialogs and exception classes
from rur_py.translation import _

from rur_py.sash import MySashWindow
from rur_py.lightning import EditorSashWindow
import rur_py.parser as parser
from rur_py.bouton import pythonChoiceWindow

from rur_py.cpu import rur_program
import rur_py.browser as browser
import rur_py.event_manager as event_manager
from rur_py.status_bar import rurStatusBar

# global variable defined for convenience; contains user program
code = ""
user_id = 0
SUBMITTED = 1
TEST_RUN = 2
STEP = 3
NUM_PROBLEMS = 8


class RURnotebook(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, -1)
        self.parent = parent
        wx.EVT_NOTEBOOK_PAGE_CHANGED(self, -1, self.OnPageChanged)

    def OnPageChanged(self, event):
        status_bar = self.parent.status_bar
        # status_bar is dead during shutdown so check if it's alive.
        if status_bar:
            arg = status_bar.notebook_new_page, event.GetSelection()
            event_manager.SendCustomEvent(self.parent, arg)
            event.Skip()

class RURApp(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 
                          _("RUR: a Python Learning Environment"),
                          size = (settings.SCREEN[0], settings.SCREEN[1]),
                          style=wx.DEFAULT_FRAME_STYLE)
        self.raw_code = ""
        self.filename = ""
        self.world_filename = ""
#        self.isPaused = False
#        self.isRunning = False
#        self.isStepped = False
        self.status_bar = rurStatusBar(self)
        self.SetStatusBar(self.status_bar)
        self.problemNumber = 0
        self.problem_choice = [0, 1, 2, 3, 4, 5, 6, 7]
        self.inst_screen = None

        # icon on top left of window
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(getImage(images.ICON))
        self.SetIcon(icon)
        #
        self.Show(True)
        self.window = RURnotebook(self)
        #
        win = browser.TestHtmlPanel(self.window, self)
        self.browser_win = browser.TestHtmlPanel(self.window, self)
        self.window.AddPage(win, _("  RUR: Read and Learn  "))
        #
        self.sash = MySashWindow(self.window, self)
        
        self.outputWindow = self.sash.output_window
        
        self.window.AddPage(self.sash, _("Robot: Code and Learn"))
        # See MySashWindow for the following 'shortcut' notation
        self.world = self.WorldDisplay.world
        # create a backup copy that will be used to "reset" the world
        self.backup_dict = {}
        self.backup_dict['avenues'] = self.world.av
        self.backup_dict['streets'] = self.world.st
        self.backup_dict['beepers'] = {}
        self.backup_dict['walls'] = []
        # add a robot to start
        self.world.addOneRobot(name='robot')
        self.backup_dict['robot'] = self.world.robot_dict[
                                                    'robot']._getInfoTuple()
        # create user_program object as a two-step process: create Singleton
        self.user_program = rur_program()
        # binds attributes explicitly
        self.user_program.myInit(self, self.world, self.WorldDisplay,
                               self.ProgramEditor, self.world.robot_dict)
        # We will then be able to "link" to the one rur_program() without
        # having to worry about changing attributes
        # recreate the image so that the robot shows up.
        self.world.DoDrawing()
        self.WorldDisplay.drawImage()
        self.WorldDisplay.Refresh()
        #
        win = py.shell.Shell(self.window, -1,
                            introText = "")
        self.window.AddPage(win, _("Python: Code and Learn"))

        self.sash2 = EditorSashWindow(self.window, grand_parent=self,
                                      controller=pythonChoiceWindow,
                 top_control=True, top_control_height=40)    
                # 40 = bouton "." btn_size[1] + 8
        self.window.AddPage(self.sash2, _("Python: simple editor"))

        self.SetSize((settings.SCREEN[0], settings.SCREEN[1]))
        self.window.SetFocus()
        self.SendSizeEvent()  # added to attempt to solve problem on MacOS
        wx.EVT_CLOSE(self, self.OnClose)

#----Helper functions
    #Modified from original Source
    def chooseWorld(self):
        #Make a dictionary corresponding to world names
        #Choose randomly from the dictionary index
        #used to parse the path for the problem to add to the name
        startingPoint = -7


        #Two dictionaries coresspond
        #May need to may one dictionary that corresponds to a class which
        #contains the problem .wld and the directions .htm
        dict = {0:'problem1.wld', 1:'problem2.wld', 2:'problem3.wld', 3:'problem4.wld', \
                    4:'problem5.wld', 5:'problem6.wld', 6:'problem7.wld', 7:'problem8.wld'}
        dict_ins = {0:'prob1.htm', 1:'prob2.htm', 2:'prob3.htm', 3:'prob4.htm', \
                        4:'prob5.htm', 5:'prob6.htm', 6:'prob7.htm', 7:'prob8.htm'}
        if len(self.problem_choice) > 0:
            temp = random.randint(0, len(self.problem_choice) - 1)
            n = self.problem_choice[temp]
            del(self.problem_choice[temp])
        

            if self.inst_screen:
                self.inst_screen.Close()
            
            self.inst_screen = InstructionScreen(None, -1, 'Instruction Screen')
            self.inst_screen.setInstructions(dict_ins[n])
     
            #Based on what problem it is change the browswer screen
            #Pass n to a function that changes the browser screen
            #May need to pass the dict
            #self.browser_win.problemChanged(dict_ins, n)
            self.browser_win.name = os.path.join(self.browser_win.lessons_dir,
                                                 'intro', dict_ins[n])
            


            if settings.USER_WORLDS_DIR[startingPoint:] != 'samples':
                openedFileName = os.path.join(settings.USER_WORLDS_DIR, 'samples', dict[n])
            else:
                openedFileName = os.path.join(settings.USER_WORLDS_DIR, dict[n])
            return openedFileName

    def OnClose(self, event):
        if self.ProgramEditor.GetModify():
                ret = dialogs.messageDialog(_(u'Save changes to %s?')
                    % unicode(self.filename), _("About to close"), wx.YES
                    | wx.NO | wx.CANCEL | wx.ICON_QUESTION | wx.STAY_ON_TOP)
                if ret == wx.ID_YES:
                    if len(self.filename) > 0:
                        try:
                            f = open(self.filename, 'w')
                            f.write(content)
                            f.close()
                        except IOError, e:
                            messageDialog(unicode(e[1]), (u'IO Error'),
                                wx.OK | wx.STAY_ON_TOP)
                    else:
                        self.SaveProgramFile(event)
                elif ret == wx.ID_NO:
                    self.Destroy()
        else:
            self.Destroy()

#---- World file methods
    def OpenWorldFile(self, dummy):
        #Changed to user_program.isRunning
        if self.user_program.isRunning:
            return

        #Will be some function that handles problem selection
        openedFileName = self.chooseWorld()
        self.problemNumber += 1
        arg = self.status_bar.problem_field, _("#" + str(self.problemNumber))
        event_manager.SendCustomEvent(self, arg)

        if openedFileName != "":
            self.world_filename = openedFileName
            self.ReadWorldFile()
            self.UpdateWorld()
            self.user_program.clear_trace()
            settings.USER_WORLDS_DIR = os.path.dirname(self.world_filename)
            arg = self.status_bar.world_field, \
                  os.path.basename(self.world_filename)
            event_manager.SendCustomEvent(self, arg)

    def ReadWorldFile(self):
        #Changed to user_program.isRunning
        if self.user_program.isRunning:
            return
        txt = open(self.world_filename, 'r').read()
        txt = parser.FixLineEnding(txt)
        flag = parser.ParseWorld(txt)
        if flag:
            self.backup_dict = {} # used to 'reset' the world
            exec txt in self.backup_dict # extracts avenues, streets, robot,
                                     # walls and beepers

    def Reset(self, dummy):
        #Changed to user_program.isRunning
        if self.user_program.isRunning:
            return
        self.UpdateWorld()

    def UpdateWorld(self):
        try:
            av = self.backup_dict['avenues']
        except:
            dialogs.messageDialog(
                   _("Problem with %s\nPlease recreate world file.")%
                   _("avenues"), 
                   _("Invalid world file format"))
            return
        try:
            st = self.backup_dict['streets']
        except:
            dialogs.messageDialog(
                   _("Problem with %s\nPlease recreate world file.")%
                   _("streets"), 
                   _("Invalid world file format"))
            return
        self.world.resetDimensions(av, st)
        try:
            if 'robot' in self.backup_dict:
                x, y, key, beep = self.backup_dict['robot']
                arg = self.status_bar.beeper_field, beep
                event_manager.SendCustomEvent(self, arg)
        except:
            dialogs.messageDialog(
                   _("Problem with %s\nPlease recreate world file.")%
                   _("robot"), 
                   _("Invalid world file format"))
            return
        # We might be reloading the world, to which robots may have been added
        # Remove all robots that have been added, if any; 
        # recall that "named" robots are added through a user-defined program, 
        # not in a world file.
        self.world.robot_dict = {}
        # Recreate the robot that was in the original file
        if 'robot' in self.backup_dict:
            self.world.addOneRobot(x, y, key, beep, name='robot')

        # world characteristics
        # note: we make shallow copies of rurApp.backup_dict as we 
        # may need it if we call ResetWorld().
        try:
            for corner in self.world.beepers_dict:
                del self.world.beepers_dict[corner] # empty, but keep reference
            for corner in self.backup_dict['beepers']:
                self.world.beepers_dict[corner] = self.backup_dict[
                                                            'beepers'][corner]
        except:
            dialogs.messageDialog(
                   _("Problem with %s\nPlease recreate world file.")%
                   _("beepers"), 
                   _("Invalid world file format"))
            return
        # We need to keep one reference only to walls_list
        try:
            for col, row in self.world.walls_list:
                self.world.walls_list.remove((col, row)) # empty, but keep ref.
            for col, row in self.backup_dict['walls']:
                self.world.walls_list.append((col, row))
        except:
            dialogs.messageDialog(
                   _("Problem with %s\nPlease recreate world file.")%
                   _("walls"), 
                   _("Invalid world file format"))
            return

        # prepare to recreate the background images
        self.world.background_images_created = False
        self.world.AdjustWorldSize()
        self.world.InitTileSizes()
        self.WorldDisplay.InitialiseVariables()
        self.world.DoDrawing()
        # create a new bitmap image
        self.WorldDisplay.buffer = wx.EmptyBitmap(self.world.maxWidth,
                                               self.world.maxHeight)
        self.WorldDisplay.drawImage()
	self.WorldDisplay.Refresh() # added to fix refresh bug (issue #23)

    #Added to submit the code and proceed to next question
    #Modified from original source
    def Submit(self, dummy):
        #Changed to user_program.isRunning
        if self.user_program.isRunning:
            return
        if self.problemNumber < NUM_PROBLEMS:
           self.SaveProgramFile(SUBMITTED)
           self.SaveWorldFile(SUBMITTED)
           self.OpenWorldFile(0)

           self.ProgramEditor.SetText("")
        else:
            self.inst_screen.Close()

            dlg = wx.MessageDialog(self, "You have completed all of the required problems." +
                                   " We invite you to give us feedback.", "Complete")
            dlg.ShowModal()
            dlg.Destroy()
            self.notes = Notes(None, -1, 'Notes')
            self.Close(True)

    def SaveWorldFile(self, dummy):
        '''Saves in .config
        '''
        #Changed to user_program.isRunning
        if self.user_program.isRunning:
            return
        txt = self.WorldDisplay.UpdateEditor()

        self.world_filename = str(user_id) + '_world_' + str(self.problemNumber) + '.txt'
        
        dirHome = os.getcwd()
        dir = conf.getUserDir()
        student_dirs = os.path.join(dir, 'StudentFiles', 'Worlds')
        try:
            os.makedirs(student_dirs)
        except OSError:
            pass

        os.chdir(student_dirs)
        file = open(self.world_filename, "a+")
        file.write(txt + "\n\n------------End of Run-----------\n\n")
        file.close()

        os.chdir(dirHome)


        arg = self.status_bar.world_field, \
              os.path.basename(self.world_filename)
        event_manager.SendCustomEvent(self, arg)
        settings.SAMPLE_WORLDS_DIR = os.path.dirname(self.world_filename)
        # save a backup copy to 'reset world'
        self.backup_dict = {}
        exec txt in self.backup_dict



#----- Program files methods

    def OpenProgramFile(self, dummy):
        #Changed to user_program.isRunning
        if self.user_program.isRunning:
            return

#        openedFileName = dialogs.openDialog(_("Choose a file"),
#           _("Program files (*.rur)|*.rur| All files (*.*)|*.*"),
#            "", settings.USER_PROGS_DIR)

        openedFileName = ""

        if openedFileName != "":
            global code
            self.filename = openedFileName
            arg = self.status_bar.program_field, \
                  os.path.basename(self.filename)
            event_manager.SendCustomEvent(self, arg)
            code = open(self.filename, 'r').read()
            code = parser.FixLineEnding(code)
            self.ProgramEditor.SetText(code)
            no_error, mesg = parser.ParseProgram(code)
            settings.USER_PROGS_DIR = os.path.dirname(self.filename)
            if no_error:
                self.raw_code = code
                self.ProgramEditor.SetSavePoint()
            else:
                code = ""
                dialogs.messageDialog(mesg, _("Program will not be used."))

    def SaveProgramFile(self, dummy):
        #IF NOT in step mode. Useful so that each step doesnt append
        #Changed to user_program.isRunning
        if self.user_program.isRunning or self.user_program.isStepped:
            return
        global code
        code = self.ProgramEditor.GetText()
        no_error, mesg = parser.ParseProgram(code)
        if no_error:
            self.filename = str(user_id) + '_code_' + str(self.problemNumber) + '.txt'


            
            dirHome = os.getcwd()
            dir = conf.getUserDir()
            student_dirs = os.path.join(dir, 'StudentFiles', 'SourceCode')
            try:
                os.makedirs(student_dirs)
            except OSError:
                pass

            os.chdir(student_dirs)
            if dummy == SUBMITTED:
                proc = "Submitted"
            elif dummy == TEST_RUN:
                proc = "Test Run"
            else:
                proc = "Step"
            file = open(self.filename, "a+")
            file.write(code + "\n\n--------------" + proc + "----------\n")
            file.write("--------------End of Run-----------\n\n")
            file.close()

            os.chdir(dirHome)
            arg = self.status_bar.program_field, \
                  os.path.basename(self.filename)

            event_manager.SendCustomEvent(self, arg)
            settings.USER_PROGS_DIR = os.path.dirname(self.filename)
            self.ProgramEditor.SetSavePoint()
        else:
            code = ""
            dialogs.messageDialog(mesg, _("Program will not be saved."))

#--- Program controls

    def RunProgram(self, dummy):
        self.SaveProgramFile(TEST_RUN)
        if self.user_program.isRunning:
            if self.user_program.isPaused or self.user_program.isStepped:
                self.user_program.isStepped = False
                self.Pause(None)
            return
        self.user_program.isRunning = True
        self.user_program.restart(self.world.robot_dict)

    def Pause(self, dummy):
        if not (self.user_program.isRunning or self.user_program.isStepped):
            return
        if self.user_program.isPaused:
            self.user_program.isPaused = False
            arg = self.status_bar.running_field, _("Program is running")
            event_manager.SendCustomEvent(self, arg)
        else:
            self.user_program.isPaused = True
            arg = self.status_bar.running_field, _("Program paused")
            event_manager.SendCustomEvent(self, arg)

    def Step(self, dummy):
        self.SaveProgramFile(STEP)
        self.user_program.isStepped = True
        if not self.user_program.isRunning:
#            pass
            self.RunProgram(None)
        else:
            self.Pause(None)
        self.SaveWorldFile(TEST_RUN)

    def StopProgram(self, dummy):
        self.user_program.StopProgram()
        arg = self.status_bar.running_field, _("Program not running")
        event_manager.SendCustomEvent(self, arg)
        self.user_program.stopped_by_user = True
        

#--- World controls

    def EditWalls(self, event):
        if self.user_program.isRunning:
            return
        self.user_program.clear_trace()
        if self.world.editWalls:
            self.world.editWalls = False
            self.world.DoDrawing()
        else:
            self.world.editWalls = True
            self.world.DoDrawing()
        self.WorldDisplay.drawImage()
        self.WorldDisplay.Refresh()

    def BeepersToRobot(self, dummy):
        if self.user_program.isRunning:
            return
        self.user_program.clear_trace()
        try:
            dummy = self.backup_dict['robot']
        except KeyError:
            msg = _("No robot in world to give beepers to.")
            dialogs.messageDialog(msg, 'error')
            return
        dialogs.RobotBeeperDialog(self, -1, _("Beepers!"))

    def BeepersUpdateStatusBar(self):
        arg = self.status_bar.beeper_field, \
              self.world.robot_dict['robot']._beeper_bag
        event_manager.SendCustomEvent(self, arg)
        # update the world window text at the same time
        self.rightWindow.DestroyChildren() # removes the old wx.StaticText
        wx.StaticText(self.rightWindow, -1,
                        self.WorldDisplay.UpdateEditor(), (10, 10))
                        
    def ResizeWorld(self, dummy):
        if self.user_program.isRunning:
            return
        self.user_program.clear_trace()
        dialogs.ResizeWorldDialog(self, -1, _("World size!"))

    def ToggleHighlight(self, dummy):
        if self.user_program.isRunning:
            return
        global code
        if settings.line_number_flag:
            settings.line_number_flag = False
            code = self.raw_code
        else:
            settings.line_number_flag = True
            code = parser.add_line_number_info(code)

    def ToggleWorldWindow(self, dummy):
        if self.user_program.isRunning:
            return
        if self.rightWindow.isVisible:
            self.rightWindow.SetDefaultSize(wx.Size(0, 600))
            self.rightWindow.isVisible = False
        else:
            self.rightWindow.SetDefaultSize(wx.Size(200, 600))
            self.rightWindow.isVisible = True

        wx.LayoutAlgorithm().LayoutWindow(self.sash, self.WorldDisplay)
        self.rightWindow.DestroyChildren() # removes the old wx.StaticText
        wx.StaticText(self.rightWindow, -1,
                        self.WorldDisplay.UpdateEditor(), (10, 10))

    def AddRemoveRobot(self, dummy):
        if self.user_program.isRunning:
            return
        if self.world.robot_dict:
            # remove all robots from non-empty dict
            self.world.robot_dict = {}
            arg = self.status_bar.beeper_field, self.status_bar.no_robot
        else:
            self.world.robot_dict = {}
            self.world.addOneRobot(name='robot')
            self.backup_dict['robot'] = self.world.robot_dict[
                                                       'robot']._getInfoTuple()
            arg = self.status_bar.beeper_field, \
                  self.world.robot_dict['robot']._beeper_bag
        event_manager.SendCustomEvent(self, arg)
        self.world.DoDrawing()
        self.WorldDisplay.drawImage()
        self.WorldDisplay.Refresh()
        
    def load_images(self, event):
        for heading in ("South", "North", "East", "West"):
            openedFileName = dialogs.openDialog(
                _("Choose an image: robot facing " + heading),
                _("All files (*.*)|*.*"),
                "", os.getcwd())
            if openedFileName != "":
                setattr(self, "file" + heading, openedFileName)
            else:
                return()

        image_south = getImage(images.GREY_ROBOT_S)
        image_north = getImage(images.GREY_ROBOT_N)
        image_east = getImage(images.GREY_ROBOT_E)
        image_west = getImage(images.GREY_ROBOT_W)
        try:
            image_south = wx.Image(self.fileSouth).ConvertToBitmap()
            image_north = wx.Image(self.fileNorth).ConvertToBitmap()
            image_east = wx.Image(self.fileEast).ConvertToBitmap()
            image_west = wx.Image(self.fileWest).ConvertToBitmap()
        except Exception, info:
            print "Conversion or loading problems: can not use new images."
            print "info = %", info
        images.setImage(images.GREY_ROBOT_S, image_south)
        images.setImage(images.GREY_ROBOT_N, image_north)
        images.setImage(images.GREY_ROBOT_E, image_east)
        images.setImage(images.GREY_ROBOT_W, image_west)
        self.AddRemoveRobot(event) # remove robot with old image
        self.AddRemoveRobot(event) # and add new one


##New User Screen
class NewUserScreen(wx.Frame):
    def __init__(self, parent, id, title):
        frameX = 900
        frameY = 700
        wx.Frame.__init__(self, parent, id, title, size=(frameX, frameY))
        largeFont = wx.Font(36, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD)        
        buttonFont = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD)
        labelFont = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD)

        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour('WHEAT')

        label = wx.StaticText(panel, -1, 'Welcome to the Playing')
        label2 = wx.StaticText(panel, -1, 'to Program System!')
        promptLabel = wx.StaticText(panel, -1, 'Please Enter your information below.')
        firstNameLabel =  wx.StaticText(panel, -1, 'First Name: ')
        lastNameLabel = wx.StaticText(panel, -1, 'Last Name: ')
        ageLabel = wx.StaticText(panel, -1, 'Age: ')
        umbcEmailLabel = wx.StaticText(panel, -1, 'UMBC Email: ')
        domainLabel =  wx.StaticText(panel, -1, '@umbc.edu')
        sexLabel = wx.StaticText(panel, -1, 'Sex: ')
        creditLabel = wx.StaticText(panel, -1, 'Credit Count: ')
        transferLabel = wx.StaticText(panel, -1, 'Are you a transfer student? ')
        courseLabel = wx.StaticText(panel, -1, "Please enter the computer science courses that you")
        courseLabel2 = wx.StaticText(panel, -1, "have completed and the grade that you earned in each.")
        courseNameLabel = wx.StaticText(panel, -1, "Course")
        courseGradeLabel = wx.StaticText(panel, -1, "Grade")
        languagesLabel = wx.StaticText(panel, -1, "Please list the programming languages that you")
        languagesLabel2 = wx.StaticText(panel, -1, "have experience with and how long: ")
        languageNameLabel = wx.StaticText(panel, -1, "Language")
        yearsLabel = wx.StaticText(panel, -1, "Years")
        majorLabel = wx.StaticText(panel, -1, "What is your major or intended major?")

        label2.SetFont(largeFont)
        label.SetFont(largeFont)
        promptLabel.SetFont(buttonFont)
        firstNameLabel.SetFont(labelFont)
        lastNameLabel.SetFont(labelFont)
        umbcEmailLabel.SetFont(labelFont)
        ageLabel.SetFont(labelFont)
        sexLabel.SetFont(labelFont)
        creditLabel.SetFont(labelFont)
        transferLabel.SetFont(labelFont)
        courseLabel.SetFont(labelFont)
        courseLabel2.SetFont(labelFont)
        courseNameLabel.SetFont(labelFont)
        courseGradeLabel.SetFont(labelFont)
        domainLabel.SetFont(labelFont)
        languagesLabel.SetFont(labelFont)
        languagesLabel2.SetFont(labelFont)
        yearsLabel.SetFont(labelFont)
        languageNameLabel.SetFont(labelFont)
        majorLabel.SetFont(labelFont)        

        self.firstName = wx.TextCtrl(panel, -1, '')
        self.lastName = wx.TextCtrl(panel, -1, '')
        self.email = wx.TextCtrl(panel, -1, '')
        self.age = wx.TextCtrl(panel, -1, '')
        self.sex = wx.Choice(panel, -1, choices = ["Male", "Female"])
        self.creditCount = wx.TextCtrl(panel, -1, '')
        self.isTransfer = wx.Choice(panel, -1, choices = ["Yes", "No"])
        self.major = wx.TextCtrl(panel, -1, '')

        self.course1 = wx.TextCtrl(panel, -1, '')
        self.course2 = wx.TextCtrl(panel, -1, '')
        self.course3 = wx.TextCtrl(panel, -1, '')
        self.course4 = wx.TextCtrl(panel, -1, '')
        self.course5 = wx.TextCtrl(panel, -1, '')
        self.course6 = wx.TextCtrl(panel, -1, '')

        grades = ["", "A", "B", "C", "D", "F", "P", "I", "Currently Enrolled"]
        #could loop
        self.grade1 = wx.Choice(panel, -1, choices = grades)
        self.grade2 = wx.Choice(panel, -1, choices = grades)
        self.grade3 = wx.Choice(panel, -1, choices = grades)
        self.grade4 = wx.Choice(panel, -1, choices = grades)
        self.grade5 = wx.Choice(panel, -1, choices = grades)
        self.grade6 = wx.Choice(panel, -1, choices = grades)

        #could loop
        self.language1 = wx.TextCtrl(panel, -1, '')
        self.language2 = wx.TextCtrl(panel, -1, '')
        self.language3 = wx.TextCtrl(panel, -1, '')
        self.language4 = wx.TextCtrl(panel, -1, '')
        self.language5 = wx.TextCtrl(panel, -1, '')
        self.language6 = wx.TextCtrl(panel, -1, '')

        years = ["", "1 or less", "1 year", "2 years", "3 years", "4 or more"] 
        self.year1 = wx.Choice(panel, -1, choices = years)
        self.year2 = wx.Choice(panel, -1, choices = years)
        self.year3 = wx.Choice(panel, -1, choices = years)
        self.year4 = wx.Choice(panel, -1, choices = years)
        self.year5 = wx.Choice(panel, -1, choices = years)
        self.year6 = wx.Choice(panel, -1, choices = years)

        

        button1 = wx.Button(panel, -1, 'Create')
        button1.SetFont(buttonFont)

        button2 = wx.Button(panel, -1, 'Cancel')
        button2.SetFont(buttonFont)

        self.Bind(wx.EVT_BUTTON, self.OnCreate, button1)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, button2)


        vbox = wx.BoxSizer(wx.VERTICAL)
        
        vbox.Add(label, 0, wx.ALIGN_CENTER | wx.ALL | wx.ALIGN_TOP, 5)
        vbox.Add(label2, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.ALIGN_TOP, 5)
        vbox.AddSpacer(20)
        vbox.Add(promptLabel, 0, wx.EXPAND | wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT | wx.ALIGN_TOP, 5)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(firstNameLabel, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)
        hbox1.Add(self.firstName, 0, wx.ALIGN_LEFT | wx.RIGHT, 300)
#        hbox1.AddSpacer(400)
        hbox1.Add(majorLabel, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        vbox.Add(hbox1)
        
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(lastNameLabel, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)
        hbox2.Add(self.lastName, 0, wx.ALIGN_LEFT | wx.RIGHT, 300)
#        hbox2.AddSpacer(400)
        hbox2.Add(self.major, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        vbox.Add(hbox2)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add(ageLabel, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)
        hbox3.Add(self.age, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.RIGHT, 5)
        vbox.Add(hbox3)

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4.Add(sexLabel, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)
        hbox4.Add(self.sex, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.RIGHT, 5)
        vbox.Add(hbox4)

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        hbox5.Add(umbcEmailLabel, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)
        hbox5.Add(self.email, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)
        hbox5.Add(domainLabel, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.RIGHT, 5)
        vbox.Add(hbox5)

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        hbox6.Add(creditLabel, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)
        hbox6.Add(self.creditCount, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.RIGHT, 5)
        vbox.Add(hbox6)

        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        hbox7.Add(transferLabel, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)
        hbox7.Add(self.isTransfer, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.RIGHT, 5)
        vbox.Add(hbox7)

        hbox8 = wx.BoxSizer(wx.HORIZONTAL)
        hbox8.Add(courseLabel, 0, wx.ALIGN_LEFT | wx.LEFT, 5)
#        hbox8.AddSpacer(100)
        hbox8.Add(languagesLabel, 0, wx.ALIGN_LEFT | wx.LEFT, 100)
        vbox.Add(hbox8)

        hbox9 = wx.BoxSizer(wx.HORIZONTAL)
        hbox9.Add(courseLabel2, 0, wx.ALIGN_LEFT | wx.LEFT, 5)
#        hbox9.AddSpacer(100)
        hbox9.Add(languagesLabel2, 0, wx.ALIGN_LEFT | wx.LEFT, 75)
        vbox.Add(hbox9)


        hbox10 = wx.BoxSizer(wx.HORIZONTAL)
        gSizer = wx.GridSizer(7, 2, 5, 40)
        gSizer.Add(courseNameLabel, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer.Add(courseGradeLabel, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer.Add(self.course1, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer.Add(self.grade1, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer.Add(self.course2, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer.Add(self.grade2, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer.Add(self.course3, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer.Add(self.grade3, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer.Add(self.course4, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer.Add(self.grade4, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer.Add(self.course5, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer.Add(self.grade5, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer.Add(self.course6, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer.Add(self.grade6, 0, wx.ALL | wx.ALIGN_LEFT)
        hbox10.Add(gSizer, 0, wx.ALIGN_LEFT | wx.LEFT, 5)

        gSizer2 = wx.GridSizer(7, 2, 5, 40)
        gSizer2.Add(languageNameLabel, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer2.Add(yearsLabel, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer2.Add(self.language1, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer2.Add(self.year1, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer2.Add(self.language2, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer2.Add(self.year2, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer2.Add(self.language3, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer2.Add(self.year3, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer2.Add(self.language4, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer2.Add(self.year4, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer2.Add(self.language5, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer2.Add(self.year5, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer2.Add(self.language6, 0, wx.ALL | wx.ALIGN_LEFT)
        gSizer2.Add(self.year6, 0, wx.ALL | wx.ALIGN_LEFT)
        hbox10.Add(gSizer2, 0, wx.ALIGN_LEFT | wx.LEFT, 140)

        vbox.Add(hbox10)


        vbox.Add(button1, 0, wx.ALIGN_CENTER | wx.ALL | wx.ALIGN_BOTTOM, 5)
        vbox.Add(button2, 0, wx.ALIGN_CENTER | wx.ALL | wx.ALIGN_BOTTOM, 5)




        panel.SetSizer(vbox)

        self.Show(True)
    
    def OnCreate(self, event):
        global user_id

        try:
            int_age = int(self.age.GetValue())
            int_creditCount = int(self.creditCount.GetValue())
        except ValueError:
            dlg = wx.MessageDialog(self, "Age and Credit count must be an integer values!",
                                   "Invalid Information!")            
            dlg.ShowModal()
            dlg.Destroy()
            event.Skip()

        directory = os.getcwd()
        os.chdir(conf.getUserDir())
        
        profiles = {}
        names = []

        try:
            logfile = open("key.txt", "r")
            for line in logfile:
                name, id = line.strip().split()
                profiles[id] = name
            logfile.close()
        except IOError:
            pass

        names = profiles.values()
        ids = profiles.keys()

        if self.email.GetValue().strip() in names:
            dlg = wx.MessageDialog(self, "This username is already in use.", 
                                       "Invalid username.")
            dlg.ShowModal()
            dlg.Destroy()
            event.Skip()

        #Error checking could be made more complete
        elif (self.lastName.GetValue() == "") or (self.firstName.GetValue() == ""):
            dlg = wx.MessageDialog(self, "Please complete the missing information", 
                                   "Missing Information!")
            dlg.ShowModal()
            dlg.Destroy()
            event.Skip()

        else:
            #Create the key file with the user_id for lookup

            logfile = open("key.txt", "a+")
            
            user_id = random.randint(0, 10 * ((len(ids)) + 1))
            while user_id in ids:
                user_id = random.randint(0, len(ids))

            logfile.write(self.email.GetValue() + "     " + str(user_id) + "\n")
            
            #Create the demographic file
            student_dirs = os.path.join(conf.getUserDir(), 'StudentFiles', 'Demographics')
            demo_filename = str(user_id) + '_demo' + '.txt'
            
            try:
                os.makedirs(student_dirs)
            except OSError:
                pass
            
            os.chdir(student_dirs)

            file = open(demo_filename, "w")
            file.write(self.lastName.GetValue().strip() + '\n')
            file.write(self.firstName.GetValue().strip() + '\n')
            file.write(self.email.GetValue().strip() + '\n')
            file.write(self.age.GetValue().strip() + '\n')
            file.write(self.sex.GetString(self.sex.GetSelection()).strip() + '\n')
            file.write(self.creditCount.GetValue().strip() + '\n')
            file.write(self.isTransfer.GetString(self.isTransfer.GetSelection()).strip() + '\n')

            #Temporary way for storing the couses and grades
            #May change to a separate panel to store each of these in an extendable array
            file.write(self.course1.GetValue().strip() + '\n')
            file.write(self.grade1.GetString(self.grade1.GetSelection()).strip() + '\n')
            file.write(self.course2.GetValue().strip() + '\n')
            file.write(self.grade2.GetString(self.grade2.GetSelection()).strip() + '\n')
            file.write(self.course3.GetValue().strip() + '\n')
            file.write(self.grade3.GetString(self.grade3.GetSelection()).strip() + '\n')
            file.write(self.course4.GetValue().strip() + '\n')
            file.write(self.grade4.GetString(self.grade4.GetSelection()).strip() + '\n')
            file.write(self.course5.GetValue().strip() + '\n')
            file.write(self.grade5.GetString(self.grade5.GetSelection()).strip() + '\n')
            file.write(self.course6.GetValue().strip() + '\n')
            file.write(self.grade6.GetString(self.grade6.GetSelection()).strip() + '\n')
            file.close()
            os.chdir(directory)


            #Run the program
            dummy = RURApp()
            self.Destroy()
#        event.Skip()
        
    
    def OnCancel(self, event):
        self.Close(True)

        
class ReturnUserScreen(wx.Frame):
    def __init__(self, parent, id, title):
        frameX = 500
        frameY = 500
        wx.Frame.__init__(self, parent, id, title, size=(frameX, frameY))
        largeFont = wx.Font(36, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD)        
        buttonFont = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD)
        labelFont = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD)

        label = wx.StaticText(self, -1, 'Welcome to the Playing', (30, 10))
        label2 = wx.StaticText(self, -1, 'to Program System!', (60, 50))
        label.SetFont(largeFont)
        label2.SetFont(largeFont)

        promptLabel = wx.StaticText(self, -1, 'Please Enter your information below.',
                                    (20, 150))
        umbcEmailLabel = wx.StaticText(self, -1, 'UMBC Email: ',
                                    (20, 180))
        domainLabel =  wx.StaticText(self, -1, '@umbc.edu',
                                    (300, 180))
        promptLabel.SetFont(buttonFont)
        umbcEmailLabel.SetFont(labelFont)
        domainLabel.SetFont(labelFont)
        
        self.email = wx.TextCtrl(self, -1, '', (120, 180), size = (150, 20))
        
        button1 = wx.Button(self, -1, 'Login', pos = wx.Point(70, 400), 
                            size = wx.Size(300, 1000))
        button1.SetFont(buttonFont)

        self.Bind(wx.EVT_BUTTON, self.OnLogin, id=button1.GetId())

        self.Show(True)
    
    def OnLogin(self, event):
        #Check if umbc name is in logfile
        global user_id

        directory = os.getcwd()
        os.chdir(conf.getUserDir())
        
        try:
            file = open("key.txt", "r")
            studentFound = False
            for line in file:
                student = line.split()
                if student[0] == self.email.GetValue():
                    studentFound = True
                    user_id = int(student[1])
            if studentFound:
                dummy = RURApp()
                self.Destroy()
                event.Skip()
            else:
                #todo: Clean this up, create a pop-up asking for a different loging
                dlg = wx.MessageDialog(self, "This username is not registered.", 
                                       "Username not found.")
                dlg.ShowModal()
                dlg.Destroy()
                event.Skip()

        except IOError:
            dlg = wx.MessageDialog(self, "You are not registered.", 
                                   "Please create a new account first.")
            dlg.ShowModal()
            dlg.Destroy()
            event.Skip()
        os.chdir(directory)

class Notes(wx.Frame):
    def __init__(self, parent, id, title):
        frameX = 500
        frameY = 500
        wx.Frame.__init__(self, parent, id, title, size=(frameX, frameY))
        largeFont = wx.Font(36, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD)        

        buttonFont = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD)

        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour('WHEAT')
        label = wx.StaticText(panel, -1, 'Notes')
        label2 = wx.StaticText(panel, -1, 'Please inform us of any suggestions or problems')
        self.box = wx.TextCtrl(panel, -1, '', size=(300, 300), style=wx.TE_MULTILINE)
        button = wx.Button(panel, -1, 'Submit')

        button.SetFont(buttonFont)
        label.SetFont(largeFont)
        label2.SetFont(buttonFont)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(label, 0, wx.ALIGN_CENTER | wx.ALL | wx.ALIGN_TOP, 5)
        vbox.Add(label2, 0, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND | wx.ALIGN_TOP, 5)
        vbox.Add(self.box, 0, wx.ALIGN_CENTER | wx.ALL | wx.ALIGN_TOP, 5)
        vbox.Add(button, 0, wx.ALIGN_CENTER | wx.ALL | wx.ALIGN_BOTTOM, 20)
        panel.SetSizer(vbox)

        wx.EVT_CLOSE(self, self.OnClose)

        self.Bind(wx.EVT_BUTTON, self.Submit, id=button.GetId())
        self.Show(True)


    def OnClose(self, event):
        self.Destroy()
        event.Skip()

    def Submit(self, ins):
        global user_id

        dirHome = os.getcwd()
        dir = conf.getUserDir()
        student_dirs = os.path.join(dir, 'StudentFiles', 'Notes')
        try:
            os.makedirs(student_dirs)
        except OSError:
            pass

        os.chdir(student_dirs)
        fileName = "Notes_" + str(user_id)
        file = open(fileName, "w")
        file.write(self.box.GetValue())
        file.close()
        os.chdir(dirHome)

        dlg = wx.MessageDialog(self, "Complete.", 
                               "Thank you for using the P2P Sytem.")
        dlg.ShowModal()
        dlg.Destroy()
        self.Close(True)

class InstructionScreen(wx.Frame):
    def __init__(self, parent, id, title):
        frameX = 500
        frameY = 500
        wx.Frame.__init__(self, parent, id, title, size=(frameX, frameY))
        self.lessons_dir = conf.getLessonsNlDir()

        self.html = html.HtmlWindow(self, id)

        self.labelFont = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD)

        wx.EVT_CLOSE(self, self.OnClose)

        self.Show(True)

    def OnClose(self, event):
        self.Destroy()
        event.Skip()

    def setInstructions(self, ins):
        htmlFiles = os.path.join(os.getcwd(), 'lessons', 'en', 'intro')
        
        page = os.path.join(htmlFiles, ins)

        self.html.LoadPage(page)
		


#Added for Login Screen
#Modified From original rur-ple code
class LoginScreen(wx.Frame):
    def __init__(self, parent, id, title):
        frameX = 500
        frameY = 500
        wx.Frame.__init__(self, parent, id, title, size=(frameX, frameY))

        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour('WHEAT')

        largeFont = wx.Font(36, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD)        

        buttonFont = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD)
        
        #panel was self
        label = wx.StaticText(panel, -1, 'Welcome to the Playing')#, (60, 50))
        label2 = wx.StaticText(panel, -1, 'to Program System!')#, (60, 50))
        label.SetFont(largeFont)
        label2.SetFont(largeFont)

        button1 = wx.Button(panel, -1, 'New User')#, pos = wx.Point(70, 200), 
                            #size = wx.Size(300, 1000))
        button2 = wx.Button(panel, -1, 'Returning User')#, pos = wx.Point(70, 300), 
                            #size = wx.Size(300, 1000))
        button1.SetFont(buttonFont)
        button2.SetFont(buttonFont)

        bmp = wx.BitmapFromImage(getImage(images.SPLASH_SCREEN).ConvertToImage())
        #print getImage(images.SPLASH_SCREEN)

        image = wx.StaticBitmap(panel, -1, size = (300,300), bitmap = bmp)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(label, 0, wx.ALIGN_CENTER | wx.ALL | wx.ALIGN_TOP, 5)
        vbox.Add(label2, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.ALIGN_TOP, 5)
 #       vbox.Add(getImage(images.SPLASH_SCREEN))
#        vbox.AddSpacer(300)
        vbox.Add(image, 0, wx.ALIGN_CENTER)
        vbox.Add(button1, 0, wx.ALIGN_CENTER | wx.ALL | wx.ALIGN_BOTTOM, 5)
        vbox.Add(button2, 0, wx.ALIGN_CENTER | wx.ALL | wx.ALIGN_BOTTOM, 5)

        panel.SetSizer(vbox)

        wx.EVT_CLOSE(self, self.OnClose)

        self.Bind(wx.EVT_BUTTON, self.OnNewUser, id=button1.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnReturnUser, id=button2.GetId())

        self.Show(True)

    def OnNewUser(self, event):
#        dummy = RURApp()
        self.Destroy()
        NewUserScreen(None, -1, 'New User')
        event.Skip()
        

    def OnReturnUser(self, event):
        self.Destroy()
        ReturnUserScreen(None, -1, 'Returning User')
        event.Skip()

    def OnClose(self, event):
        self.Destroy()
        event.Skip()


class MySplashScreen(wx.SplashScreen):
    def __init__(self):
        wx.SplashScreen.__init__(self, getImage(images.SPLASH_SCREEN),
                wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_TIMEOUT, 100, None, -1,
                style = wx.SIMPLE_BORDER|wx.FRAME_NO_TASKBAR|wx.STAY_ON_TOP)
        wx.EVT_CLOSE(self, self.OnClose)

    def OnClose(self, evt):
        #Change for creating loginScreen
        LoginScreen(None, -1, 'Login Screen')
        evt.Skip()

if __name__ == "__main__": 
    App = wx.PySimpleApp(0) # (1) redirects print output to window;
                            # (0) to terminal
                            
    settings = conf.getSettings()
    settings.SCREEN = wxutils.getscreen()

    Splash = MySplashScreen()
    Splash.Show()
    App.MainLoop()