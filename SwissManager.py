
import os
import pdb
import numpy
import string
from matplotlib import patches
from matplotlib import pyplot

from ParticipantRoster import ParticipantRoster

###  removing default keyboard shortcuts from pyplot
for key, vals in pyplot.rcParams.items():
    if 'keymap' in key:
        for val in vals:
            pyplot.rcParams[key].remove(val)


BUTTON_HEIGHT = 0.04
BUTTON_WIDTH = 0.12
X_TABLE = 0.11
Y_TABLE = 0.69
CELL_HEIGHT = 0.032



class StandingsRow():

    def __init__(self, idx, ax):

        self.idx = idx
        self.ax = ax

        ###  seed
        self.box_seed = patches.Rectangle([X_TABLE, Y_TABLE-idx*CELL_HEIGHT],
                                           width=0.03,
                                           height=CELL_HEIGHT,
                                           facecolor='none', 
                                           lw=0.5, 
                                           edgecolor='none')
        self.ax.add_artist(self.box_seed)
        x, y = self._get_center(self.box_seed)
        self.text_seed = self.ax.text(x, y, '', ha='center', va='center', size=10)

        ###  name
        self.box_name = patches.Rectangle([X_TABLE+0.03, Y_TABLE-idx*CELL_HEIGHT],
                                           width=0.25,
                                           height=CELL_HEIGHT,
                                           facecolor='none', 
                                           lw=0.5, 
                                           edgecolor='none')
        self.ax.add_artist(self.box_name)
        x, y = self._get_center(self.box_name)
        self.text_name = self.ax.text(x, y, '', ha='center', va='center', size=10)

        ###  rating
        self.box_rating = patches.Rectangle([X_TABLE+0.03+0.25, Y_TABLE-idx*CELL_HEIGHT],
                                             width=0.05,
                                             height=CELL_HEIGHT,
                                             facecolor='none', 
                                             lw=0.5, 
                                             edgecolor='none')
        self.ax.add_artist(self.box_rating)
        x, y = self._get_center(self.box_rating)
        self.text_rating = self.ax.text(x, y, '', ha='center', va='center', size=10)

        ###  "remove player" button
        self.button_remove_player = patches.FancyBboxPatch([X_TABLE-0.04, Y_TABLE-idx*CELL_HEIGHT+(CELL_HEIGHT-0.015)/2.], 
                                                            width=0.02, 
                                                            height=0.015, 
                                                            boxstyle=patches.BoxStyle('round', pad=0.005), 
                                                            facecolor='none', 
                                                            lw=1.5, 
                                                            edgecolor='none', 
                                                            label='button_remove_player_%i'%(idx+1))
        x, y = self._get_center(self.button_remove_player)
        self.text_x = self.ax.text(x, y, 'x', ha='center', va='center', size=12, color='none', weight='bold')
        self.ax.add_artist(self.button_remove_player)


    def _get_center(self, patch):
        x = patch.get_x()
        y = patch.get_y()
        w = patch.get_width()
        h = patch.get_height()
        return (x+w/2., y+h/2.)





class SwissManager(object):

    def __init__(self, file_participants=''):


        self.fig, self.ax = pyplot.subplots(figsize=(11., 6.))
        self.fig.subplots_adjust(left=0, top=1, right=1, bottom=0)
        self.ax.set_label('main')
        self.ax.set_zorder(0)
        self.ax.axis([0, 1, 0, 1])
        self.ax.axhline(0.9, color='k', lw=2)

        ###  establishing interactive connections
        cid0 = self.fig.canvas.mpl_connect('button_press_event', self._onClick)
        cid1 = self.fig.canvas.mpl_connect('key_press_event', self._onKeyPress)

        ###  button params
        self.list_buttons = []



        ###  adding invisible cells to contain standings table
        self.list_standings_rows = [StandingsRow(idx, self.ax) for idx in range(22)]







        ###  loading participant list if provided
        self.participants = ParticipantRoster()
        if os.path.exists(file_participants):

            with open(file_participants, 'r') as fopen:

                for line in fopen.readlines():

                    name, rating = line.strip('\n').split(',')
                    if name.lower() == 'name':
                        continue

                    self.participants.add_participant(name, int(rating))


            ###  generating standings table
            self._redraw_standings_table()







        ###  standings button
        self.button_standings = patches.FancyBboxPatch([0.03, 0.93], 
                                                        width=BUTTON_WIDTH, 
                                                        height=BUTTON_HEIGHT, 
                                                        boxstyle=patches.BoxStyle('round', pad=0.01), 
                                                        facecolor='none', 
                                                        lw=2, 
                                                        label='button_standings')
        x, y = self._get_center(self.button_standings)
        self.text_button_standings = self.ax.text(x, y, 'Standings', ha='center', va='center', size=14, weight='bold')
        self.list_buttons.append(self.button_standings)
        self.active_button = self.button_standings
        self.ax.add_artist(self.button_standings)


        ###  generate round 1 button
        self.button_start_round_1 = patches.FancyBboxPatch([0.2, 0.93], 
                                                          width=BUTTON_WIDTH+0.04, 
                                                          height=BUTTON_HEIGHT, 
                                                          boxstyle=patches.BoxStyle('round', pad=0.01), 
                                                          facecolor='none', 
                                                          lw=2, 
                                                          label='button_start_round_1')
        x, y = self._get_center(self.button_start_round_1)
        self.text_button_start_round_1 = self.ax.text(x, y, 'Start Round 1', ha='center', va='center', size=14, weight='bold')
        self.list_buttons.append(self.button_start_round_1)
        self.ax.add_artist(self.button_start_round_1)


        ###  "add player" button
        self.button_add_player = patches.FancyBboxPatch([0.03, 0.79], 
                                                        width=0.05, 
                                                        height=0.05, 
                                                        boxstyle=patches.BoxStyle('round', pad=0.005), 
                                                        facecolor='none', 
                                                        lw=2, 
                                                        label='button_add_player')
        self.ax.text(0.055, 0.815, '+', ha='center', va='center', size=20, weight='bold')
        self.ax.add_artist(self.button_add_player)

        ###  "add player name" button
        self.button_add_player_name = patches.Rectangle([0.11, 0.79],
                                                        width=0.25,
                                                        height=0.05,
                                                        facecolor='none', 
                                                        lw=2, 
                                                        edgecolor='k', 
                                                        label='button_add_player_name')
        self.ax.text(0.12, 0.85, 'Player Name', size=12, style='italic')
        self.ax.add_artist(self.button_add_player_name)
        self.new_player_name = ''
        x, y = self._get_center(self.button_add_player_name)
        self.text_new_player_name = self.ax.text(x, y, '', ha='center', va='center', size=12, weight='bold')


        ###  "add player rating" button
        self.button_add_player_rating = patches.Rectangle([0.39, 0.79],
                                                          width=0.07,
                                                          height=0.05,
                                                          facecolor='none', 
                                                          lw=2, 
                                                          edgecolor='k', 
                                                          label='button_add_player_rating')
        self.ax.text(0.4, 0.85, 'Rating', size=12, style='italic')
        self.ax.add_artist(self.button_add_player_rating)
        self.new_player_rating = ''
        x, y = self._get_center(self.button_add_player_rating)
        self.text_new_player_rating = self.ax.text(x, y, '', ha='center', va='center', size=12, weight='bold')



    def _onClick(self, event):


        if self._was_clicked(self.button_standings, event):
            print('standings')


        if self._was_clicked(self.button_add_player, event):

            ###  pass if no new name or rating is provided
            if self.new_player_name == '':
                pass
            elif self.new_player_rating == '':
                pass

            else:

                self.participants.add_participant(self.new_player_name, float(self.new_player_rating))
                self.active_button.set_facecolor('w')
                self.active_button = self.button_standings

                self.new_player_name = ''
                self.new_player_rating = ''
                self.text_new_player_name.set_text('')
                self.text_new_player_rating.set_text('')

                self._redraw_standings_table()
                self._redraw()






        if self._was_clicked(self.button_add_player_name, event):
            self.active_button = self.button_add_player_name
            self.active_button.set_facecolor('#ffffb3')
            self.button_add_player_rating.set_facecolor('w')
            self._redraw()

        if self._was_clicked(self.button_add_player_rating, event):
            self.active_button = self.button_add_player_rating
            self.active_button.set_facecolor('#ffffb3')
            self.button_add_player_name.set_facecolor('w')
            self._redraw()

        for row in self.list_standings_rows:

            ###  remove if button is clicked and row is occupied
            if self._was_clicked(row.button_remove_player, event) and (row.idx < self.participants.n_participants):
                self.participants.remove_participant(row.idx)
                self._redraw_standings_table()
                self._redraw()




    def _onKeyPress(self, event):



        if self.active_button.get_label() == 'button_add_player_name':

            if event.key.lower() == 'tab':
                self.active_button = self.button_add_player_rating
                self.active_button.set_facecolor('#ffffb3')
                self.button_add_player_name.set_facecolor('w')

            elif event.key in string.ascii_letters + string.digits:
                self.new_player_name += event.key

            elif event.key == ' ':
                self.new_player_name += ' '

            elif (self.new_player_name != '') and (event.key.lower() == 'backspace'):
                self.new_player_name = self.new_player_name[:-1]


            self.text_new_player_name.set_text(self.new_player_name)
            self._redraw()


        if self.active_button.get_label() == 'button_add_player_rating':

            if event.key in string.digits + '.':
                self.new_player_rating += event.key

            elif (self.new_player_rating != '') and (event.key.lower() == 'backspace'):
                self.new_player_rating = self.new_player_rating[:-1]


            self.text_new_player_rating.set_text(self.new_player_rating)
            self._redraw()


        ###  add new player with "enter"
        if event.key.lower() == 'enter':

            if self.new_player_name == '':
                pass
            elif self.new_player_rating == '':
                pass

            else:
                self.participants.add_participant(self.new_player_name, float(self.new_player_rating))
                self.active_button.set_facecolor('w')
                self.active_button = self.button_standings
                self.new_player_name = ''
                self.new_player_rating = ''
                self.text_new_player_name.set_text('')
                self.text_new_player_rating.set_text('')
                self._redraw_standings_table()
                self._redraw()




    def _was_clicked(self, button, event):

        xlo = button.get_x()
        ylo = button.get_y()
        xhi = xlo + button.get_width()
        yhi = ylo + button.get_height()

        if (xlo < event.xdata < xhi) and (ylo < event.ydata < yhi):
            return True
        else:
            return False


    def _get_center(self, patch):
        x = patch.get_x()
        y = patch.get_y()
        w = patch.get_width()
        h = patch.get_height()
        return (x+w/2., y+h/2.)


    def _redraw(self):
        self.fig.canvas.draw()


    def _redraw_standings_table(self):

        for idx in range(22):
            row = self.list_standings_rows[idx]

            if idx < self.participants.n_participants:

                seed = self.participants.seeds[idx]
                name = self.participants.names[idx]
                rating = self.participants.ratings[idx]

                row.box_seed.set_ec('k')
                row.text_seed.set_text('%i'%seed)

                row.box_name.set_ec('k')
                row.text_name.set_text('%s'%name)

                row.box_rating.set_ec('k')
                row.text_rating.set_text('%i'%rating)

                row.button_remove_player.set_ec('k')
                row.text_x.set_color('k')

            else: 

                row.box_seed.set_ec('none')
                row.text_seed.set_text('')

                row.box_name.set_ec('none')
                row.text_name.set_text('')

                row.box_rating.set_ec('none')
                row.text_rating.set_text('')

                row.button_remove_player.set_ec('none')
                row.text_x.set_color('none')





