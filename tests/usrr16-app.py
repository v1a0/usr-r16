#! /usr/bin/python3
# coding=utf-8
#
#-------------------------------------------------------------------------------
#  usrr16-app - USR-R16 Relay Conrol System
#
#  Copyright (c) 2022 George Farris - farrisg@gmsys.com
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#-------------------------------------------------------------------------------

# Release history
# Mar 5, 2022 - V1.0  Initial release

import os
import re
import sys
import time
import curses
import locale
import serial
import string
import socket
import datetime
from usrr16 import UsrR16

# This must be set to output unicode characters
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


# ************* USER MODIFIABLE SETTINGS ************************************
# 
# Array of control relays
ROW = 4
COL0 = 1
COL1 = 20
COL2 = 40
COL3 = 60
WIDTH = 10

# Relay board IP address
# My board actually got an IP address via DHCP but apparently the static 
# address is set to the following.  Once you know your IP address you can 
# connect to it with a browser, login with user->admin and pass-> admin,
# and can change your IP address and password.
# HOST = '192.168.0.7'
HOST = '192.168.10.79'

# Relays on USR-R16 relay board
relay = []
# Relays are numbered starting from 1 so we add a dummy relay 0
# which is not used.
relay.append([None,None,None,None])

# Change these labels to whatever you want
# Relay 1 
relay.append( [COL0,ROW,WIDTH,   'Relay 1 '] )
# Relay 2
relay.append( [COL0,ROW+4,WIDTH, 'Relay 2 '] )
# Relay 3 
relay.append( [COL0,ROW+8,WIDTH, 'Relay 3 '] )
# Relay 4 
relay.append( [COL0,ROW+12,WIDTH,'Relay 4 '] )
# Relay 5 
relay.append( [COL1,ROW,WIDTH,   'Relay 5 '] )
# Relay 6 
relay.append( [COL1,ROW+4,WIDTH, 'Relay 6 '] )
# Relay 7 
relay.append( [COL1,ROW+8,WIDTH, 'Relay 7 '] )
# Relay 8 
relay.append( [COL1,ROW+12,WIDTH,'Relay 8 '] )
# Relay 9 
relay.append( [COL2,ROW,WIDTH,   'Relay 9 '] )
# Relay 10 
relay.append( [COL2,ROW+4,WIDTH, 'Relay 10'] )
# Relay 11 
relay.append( [COL2,ROW+8,WIDTH, 'Relay 11'] )
# Relay 12
relay.append( [COL2,ROW+12,WIDTH,'Relay 12'] )
# Relay 13 
relay.append( [COL3,ROW,WIDTH,   'Relay 13'] )
# Relay 14 
relay.append( [COL3,ROW+4,WIDTH, 'Relay 14'] )
# Relay 15 
relay.append( [COL3,ROW+8,WIDTH, 'Relay 15'] )
# Relay 16
relay.append( [COL3,ROW+12,WIDTH,'Relay 16'] )

# Set cycle time for CYCLE operation to N seconds
CYCLE_TIME = 5

# ************  END OF USER MODIFIABLE SETTINGS *****************************

VERSION = 'V1.0 - Python 3'
VERSION_DATE = 'Mar 05, 2022'

CURSOR_INVISIBLE = 0    # no cursor
CURSOR_NORMAL = 1       # Underline cursor
CURSOR_BLOCK = 2        # Block cursor

NOCHAR = -1



class MBRTerm():

    def __init__(self,r16):
        self.screen = None
        self.status = None
        self.r16 = r16

    def setup_screen(self):
        self.cur = curses.initscr()  # Initialize curses.
        curses.start_color()

        if curses.termname() == b'linux':
            self.X0 = 0
            self.Y0 = 0
        else:
            self.X0 = 1
            self.Y0 = 1
            self.cur.box()
            self.cur.refresh()
            y, x = self.cur.getmaxyx()
            if y < 25 or x < 80:
                curses.endwin()
                print("\nYour screen is to small to run mbrcon, it must be")
                print("at least 25 lines by 80 columns...\n")
                print("Consider changing your terminal profile so you do not have")
                print("to resize the window all the time...\n")
                print("If you are using PUTTY, make sure you go to")
                print("Connection->Data and set your terminal type to \"linux\" as well\n\n\n")
                sys.exit(1)

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_WHITE)


        curses.cbreak()
        curses.raw()
        curses.noecho()
        curses.nonl()
        self.cur.refresh()
        self.screen = curses.newwin(20,78,self.X0, self.Y0)
        self.status = curses.newwin(4,78,22,self.Y0)
        self.screen.refresh()
        self.screen.nodelay(1)
        self.screen.keypad(1)
        self.screen.scrollok(True)
        self.screen.idlok(1)
        self.screen.setscrreg(0,19)
        return self.screen, self.status


    def reset(self):
        self.status.addstr(1, 40, "   ")
        self.status.addstr(1, 41, "-")
        self.status.refresh()
        self.visibleCursor = True
        self.screen.erase()
        #self.cursor_home()
        curses.curs_set(CURSOR_NORMAL)


    def terminate(self):
        curses.endwin() # End screen (ready to draw new one, but instead we exit)


    def show_intro(self):
        helptext = """
             Welcome to:
                _   _ ____  ____       ____  _  __   
               | | | / ___||  _ \     |  _ \/ |/ /_  
               | | | \___ \| |_) |____| |_) | | '_ \ 
               | |_| |___) |  _ <_____|  _ <| | (_) |
                \___/|____/|_| \_\    |_| \_\_|\___/    """
        # created with figlet


        self.screen.erase()
        self.screen.addstr(2, 2, helptext)
        self.screen.addstr(12,20, VERSION)
        self.screen.addstr(13,20, VERSION_DATE)
        self.screen.addstr(14,20,"By George Farris - VE7FRG")
        self.screen.addstr(17,14, "USR-R16 Relay Control System...")
        
        self.screen.refresh()

    def show_status_line(self):
        global BAUD_RATE
        y,x = self.screen.getyx()   # save cursor
        self.status.hline(0, 0, curses.ACS_HLINE, 80)
        self.status.hline(2, 0, curses.ACS_HLINE, 80)
        self.status.move(1,0)
        self.status.clrtoeol()
        self.status.addstr(1, 0, " EXIT:", curses.A_BOLD)
        self.status.addstr(" Q  |       Press <ENTER> for control screen")
        self.status.addstr(1, 58, "| ")
        self.status.addstr("IP: ", curses.A_BOLD)
        self.status.addstr(HOST)
        # Move to first selection
        self.screen.move(y,x)
        self.status.refresh()

    # Pop up the "On / Off / Cycle" selection for controlling relays
    def popup_run_stop(self, idx):
        cl = []
        cl.append('  On   ')
        cl.append('  Off  ')
        cl.append(' Cycle ')
        try:
            popup = curses.newwin(9, 26, 8, 20)
            popup.attrset(curses.color_pair(1))
            for i in range(len(cl)):
                popup.addstr(i+2, 9, cl[i],curses.color_pair(1))
                popup.addstr(7, 2, "<Enter> <UP> <DN> 'q'")

            popup.border('|','|','-','-','+','+','+','+')
            popup.addstr(0,3,'[Control Selection]')
            popup.nodelay(0)
            popup.keypad(1)
            curses.curs_set(0)
            popup.refresh()
        except:
            pass

        idx = 0
        popup.addstr(idx+2,9,cl[idx],curses.color_pair(idx+1)|curses.A_REVERSE)

        while True:
            c = popup.getch()

            if c == curses.KEY_DOWN:
                if idx + 1 < len(cl):
                    popup.addstr(idx+2,9,cl[idx],curses.color_pair(1)|curses.A_NORMAL)
                    idx += 1
                    popup.addstr(idx+2,9,cl[idx],curses.color_pair(1)|curses.A_REVERSE)
                    popup.refresh()
            elif c == curses.KEY_UP:
                if idx -1 >= 0:
                    popup.addstr(idx+2,9,cl[idx],curses.color_pair(1)|curses.A_NORMAL)
                    idx -= 1
                    popup.addstr(idx+2,9,cl[idx],curses.color_pair(1)|curses.A_REVERSE)
                    popup.refresh()

            elif curses.keyname(c) == b'^M':
                self.screen.touchwin()
                self.screen.refresh()
                #curses.curs_set(1)
                if idx == 0:
                    return('ON ')
                elif idx == 1:
                    return('OFF')
                elif idx == 2:
                    return('CYCLE')

            elif chr(c) == 'q':
                self.screen.touchwin()
                self.screen.refresh()
                #curses.curs_set(1)
                return('')

    def up_down_select(self):
        self.screen.nodelay(0)
        self.screen.keypad(1)
        curses.curs_set(0)

        idx = 1
        state = self.get_relay_state(idx)
        self.draw_box(relay[idx][0],relay[idx][1],relay[idx][2],relay[idx][3],state,True,str(idx))
        curses.curs_set(CURSOR_INVISIBLE)
        self.screen.refresh()

        while True:
            curses.flushinp()
            c = self.screen.getch()

            if c == curses.KEY_DOWN:
                if idx + 1 < len(relay):
                    state = self.get_relay_state(idx)
                    self.draw_box(relay[idx][0],relay[idx][1],relay[idx][2],relay[idx][3],state,False,str(idx))
                    idx += 1
                    state = self.get_relay_state(idx)
                    self.draw_box(relay[idx][0],relay[idx][1],relay[idx][2],relay[idx][3],state,True,str(idx))
                    self.screen.refresh()
            elif c == curses.KEY_UP:
                if idx -1 >= 1:
                    state = self.get_relay_state(idx)
                    self.draw_box(relay[idx][0],relay[idx][1],relay[idx][2],relay[idx][3],state,False,str(idx))
                    idx -= 1
                    state = self.get_relay_state(idx)
                    self.draw_box(relay[idx][0],relay[idx][1],relay[idx][2],relay[idx][3],state,True,str(idx))
                    self.screen.refresh()
            elif c == curses.KEY_RIGHT:
                if idx + 4 < len(relay):
                    state = self.get_relay_state(idx)
                    self.draw_box(relay[idx][0],relay[idx][1],relay[idx][2],relay[idx][3],state,False,str(idx))
                    idx += 4
                    state = self.get_relay_state(idx)
                    self.draw_box(relay[idx][0],relay[idx][1],relay[idx][2],relay[idx][3],state,True,str(idx))
                    self.screen.refresh()
            elif c == curses.KEY_LEFT:
                if idx - 4 < len(relay) and idx -4 > 0:
                    state = self.get_relay_state(idx)
                    self.draw_box(relay[idx][0],relay[idx][1],relay[idx][2],relay[idx][3],state,False,str(idx))
                    idx -= 4
                    state = self.get_relay_state(idx)
                    self.draw_box(relay[idx][0],relay[idx][1],relay[idx][2],relay[idx][3],state,True,str(idx))
                    self.screen.refresh()

            elif curses.keyname(c) == b'^M':
                self.set_relay_state(idx, self.popup_run_stop(idx))
                self.screen.touchwin()
                self.screen.refresh()

            # Turn all the relays off
            elif chr(c) == 'x' or chr(c) == 'X':
                self.r16.turn_off_all()
                for i in range(1,len(relay)):
                    if i == 1:
                        selected = True
                    else:
                        selected = False
                    state = 'OFF'
                    self.draw_box(relay[i][0],relay[i][1],relay[i][2],relay[i][3],state,selected,i)
                idx = 1

                self.screen.touchwin()
                self.screen.refresh()

            elif chr(c) == 'q' or chr(c) == 'Q':
                self.screen.touchwin()
                self.screen.refresh()
                curses.curs_set(1)
                sys.exit()

    def get_relay_state(self, relay):
        if self.r16.state(relay):
            return('ON ')
        else:
            return('OFF')

    # Get here from popup_run_stop()
    # state = 'ON ', 'OFF' or 'CYCLE'
    def set_relay_state(self, idx, state):
        if state == 'CYCLE':
            state = self.get_relay_state(idx)
            if state == 'OFF':
                self.draw_box(relay[idx][0],relay[idx][1],relay[idx][2],relay[idx][3],'ON ',True,str(idx))
                self.r16.turn_on(idx)
                time.sleep(CYCLE_TIME)
                self.draw_box(relay[idx][0],relay[idx][1],relay[idx][2],relay[idx][3],'OFF',True,str(idx))
            else:
                self.draw_box(relay[idx][0],relay[idx][1],relay[idx][2],relay[idx][3],'OFF',True,str(idx))
                self.r16.turn_off(idx)
                time.sleep(CYCLE_TIME)
                self.draw_box(relay[idx][0],relay[idx][1],relay[idx][2],relay[idx][3],'ON ',True,str(idx))
        if state == 'OFF':
            self.r16.turn_off(idx)
            self.draw_box(relay[idx][0],relay[idx][1],relay[idx][2],relay[idx][3],state,True,str(idx))
        else:
            self.r16.turn_on(idx)
            self.draw_box(relay[idx][0],relay[idx][1],relay[idx][2],relay[idx][3],state,True,str(idx))
      
    # Repeater control screen
    def show_control(self):
        curses.curs_set(CURSOR_INVISIBLE)
        self.screen.erase()
        title = "USR-R16 Relay Board"
        x = int((79 - len(title)) / 2)
        self.screen.addstr(0,x,title, curses.A_BOLD)
        title1 = "Control and Status Window"
        x1 = int((79 - len(title1)) / 2)
        self.screen.addstr(1,x1,title1, curses.A_BOLD)
        # update status line
        self.status.addstr(1, 0, " EXIT:", curses.A_BOLD)
        self.status.addstr(" Q  | Use Arrow keys, then press <ENTER> to control relay  ")
        self.status.addstr(1, 65, "| ")
        self.status.addstr("All Off: ", curses.A_BOLD)
        self.status.addstr('X ')
        self.status.refresh()

        state = 'OFF'
        # column 1
        #self.draw_box(10,4,15,'Camera1      ',status,True)
        for i in range(1,len(relay)):
            if i == 1:
                selected = True
            else:
                selected = False
            state = self.get_relay_state(i)
            self.draw_box(relay[i][0],relay[i][1],relay[i][2],relay[i][3],state,selected,i)


        # now process UP / DOWN arrows keys
        self.up_down_select()

    def draw_box(self,x,y,width,label,state,selected,relay):
        # draw box
        self.screen.addch(y,x,curses.ACS_ULCORNER)
        self.screen.hline(y,x+1,curses.ACS_HLINE,width)
        self.screen.addch(y,x+width,curses.ACS_URCORNER)
        self.screen.addch(y+1,x+width,curses.ACS_LTEE)
        self.screen.addch(y+2,x+width,curses.ACS_LRCORNER)
        self.screen.hline(y+2,x+1,curses.ACS_HLINE,width-1)
        self.screen.addch(y+2,x,curses.ACS_LLCORNER)
        self.screen.vline(y+1,x,curses.ACS_VLINE,1)
        if selected:
            self.screen.addstr(y+1,x+2,label,curses.A_REVERSE)
        else:
            self.screen.addstr(y+1,x+2,label)
        
        # When printing relay number move according to width
        if len(str(relay)) > 1:
            self.screen.addstr(y+1,x-2,str(relay))
        else:
            self.screen.addstr(y+1,x-1,str(relay))

        # draw state
        x += width+1
        width = 4
        self.screen.addch(y,x,curses.ACS_ULCORNER)
        self.screen.hline(y,x+1,curses.ACS_HLINE,width)
        self.screen.addch(y,x+width,curses.ACS_URCORNER)
        self.screen.vline(y+1,x+width,curses.ACS_VLINE,1)
        self.screen.addch(y+2,x+width,curses.ACS_LRCORNER)
        self.screen.hline(y+2,x+1,curses.ACS_HLINE,width-1)
        self.screen.addch(y+2,x,curses.ACS_LLCORNER)
        self.screen.addch(y+1,x,curses.ACS_RTEE)
        if state == 'OFF':
            self.screen.addstr(y+1,x+1,state,curses.color_pair(2)|curses.A_REVERSE|curses.A_STANDOUT)
        else:
            self.screen.addstr(y+1,x+1,state,curses.color_pair(7)|curses.A_REVERSE|curses.A_STANDOUT)
        self.screen.refresh()

    def process_key(self, c):
        if curses.keyname(c) == b'^A':  # Command Key
            self.parse_ctrl_a()
        elif chr(c) == 'q' or chr(c) == 'Q':
            sys.exit()
        elif curses.keyname(c) == b'^M':
            self.popup_run_stop()

    def parse_ctrl_a(self):
        c = NOCHAR
        while c == NOCHAR:
            c = self.screen.getch()
        s = chr(c)
        while True:
            if s == 'x' or s == 'X':    # Exit
                sys.exit(0)
            elif s == 'z' or s == 'Z':
                s = self.popup_help()
            else:
                break  # get out on ^M or any non command key


    def main(self, scr, term):
        scn, st = term.setup_screen()
        term.reset()
        
        # leave this here just in case.
        #self.r16.turn_off_all()

        # if curses.termname() == 'linux':
        self.BACKSPACE = curses.KEY_BACKSPACE
        #else:
        #    self.BACKSPACE = 127  # xterms do this
        
        first_char = True
        date_string = ''
        today = datetime.datetime.today()

        # Loop time makes sure process doesn't run wild
        loop_time = 0.0

        self.show_status_line()
        self.show_intro()
        curses.curs_set(CURSOR_INVISIBLE)
        
        while True:
            c = NOCHAR

            c = scn.getch()
            if c != NOCHAR:
                loop_time = 0.0

                if first_char:
                    term.screen.erase()
                    first_char = False
                    if chr(c) == 'q' or chr(c) == 'Q':
                        sys.exit()
                    if curses.keyname(c) != b'^A':  # Command Key
                        self.show_control()
                else:
                    self.process_key(c)

            if loop_time <= 0.1:
                loop_time += 0.000001
            else:
                time.sleep(loop_time)


if __name__ == "__main__":
    # Get an instance of USR-R16 relay control
    try:
        r16 = UsrR16(host=HOST, port=8899, password='admin')
    except:
        print("Cannot reach the USR-R16 relay board, exiting...")
        sys.exit()

    term = MBRTerm(r16)
    curses.wrapper(term.main, term)

