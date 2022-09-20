
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
X_TABLE = 0.07
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
                                           zorder=3, 
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
                                           zorder=3, 
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
                                             zorder=3, 
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
                                                            zorder=3, 
                                                            label='button_remove_player_%i'%(idx+1))
        x, y = self._get_center(self.button_remove_player)
        self.text_x = self.ax.text(x, y, 'x', ha='center', va='center', size=12, color='none', weight='bold', label='text_remove_player_%i'%(idx+1))
        self.ax.add_artist(self.button_remove_player)

        ###  dictionary to hold opponent ids and scores for future rounds
        self.dict_rounds = {}


    def _get_center(self, patch):
        x = patch.get_x()
        y = patch.get_y()
        w = patch.get_width()
        h = patch.get_height()
        return (x+w/2., y+h/2.)


    def add_new_round_columns(self, i_round):


        box_opp = patches.Rectangle([X_TABLE+0.03+0.25+0.05+0.08*(i_round-1), Y_TABLE-self.idx*CELL_HEIGHT],
                                     width=0.04,
                                     height=CELL_HEIGHT,
                                     facecolor='none', 
                                     lw=0.5, 
                                     zorder=3, 
                                     edgecolor='k', 
                                     label='box_opp_idx_%i_round_%i'%(self.idx, i_round))
        x0, y0 = self._get_center(box_opp)
        text_opp = self.ax.text(x0, y0, '', size=9, ha='center', va='center', zorder=3)

        box_score = patches.Rectangle([X_TABLE+0.03+0.25+0.05+0.08*(i_round-1)+0.04, Y_TABLE-self.idx*CELL_HEIGHT],
                                     width=0.04,
                                     height=CELL_HEIGHT,
                                     facecolor='none', 
                                     lw=0.5, 
                                     zorder=3, 
                                     edgecolor='k', 
                                     label='box_score_idx_%i_round_%i'%(self.idx, i_round))
        x0, y0 = self._get_center(box_score)
        text_score = self.ax.text(x0, y0, '', size=9, ha='center', va='center', zorder=4)

        self.ax.add_artist(box_opp)
        self.ax.add_artist(box_score)

        self.dict_rounds['round_%i'%i_round] = {'box_opp': box_opp, 
                                                'text_opp': text_opp, 
                                                'box_score': box_score, 
                                                'text_score': text_score}






class SwissManager(object):



    def __init__(self, file_participants=''):


        self.fig, self.ax = pyplot.subplots(figsize=(11., 6.))
        self.fig.subplots_adjust(left=0, top=1, right=1, bottom=0)
        self.ax.set_label('main')
        self.ax.set_zorder(0)
        self.ax.axis([0, 1, 0, 1])
        self.ax.axhline(0.9, color='k', lw=2, zorder=1)

        ###  adding whitspace to deliniate tabs
        self.whitespace = patches.Rectangle([-0.01, -0.01], 
                                             width=1.02, 
                                             height=0.907, 
                                             fc='w', 
                                             lw=0, 
                                             zorder=3)
        self.ax.add_artist(self.whitespace)

        ###  establishing interactive connections
        cid0 = self.fig.canvas.mpl_connect('button_press_event', self._onClick)
        cid1 = self.fig.canvas.mpl_connect('key_press_event', self._onKeyPress)


        ###  button params
        self.current_round = 0
        self.list_buttons = []


        ###  flag to determine which display the user is currently viewing
        ###  ['registration', start_round_1_prompt', 'standings', 'round_i']
        self.active_display = 'registration'



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
        self.button_standings = patches.FancyBboxPatch([0.03, 0.9], 
                                                        width=BUTTON_WIDTH, 
                                                        height=BUTTON_HEIGHT+0.03, 
                                                        boxstyle=patches.BoxStyle('round', pad=0.01), 
                                                        facecolor='w', 
                                                        lw=2, 
                                                        ec='k', 
                                                        zorder=2, 
                                                        label='button_standings')

        x, y = self._get_center(self.button_standings)
        self.text_button_standings = self.ax.text(x, y, 'Registration', ha='center', va='center', size=14, weight='bold')
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
                                                        zorder=3, 
                                                        label='button_add_player')
        self.ax.text(0.055, 0.815, '+', ha='center', va='center', size=20, weight='bold', label='text_new_player_add')
        self.ax.add_artist(self.button_add_player)

        ###  "add player name" button
        self.button_add_player_name = patches.Rectangle([0.11, 0.79],
                                                        width=0.25,
                                                        height=0.05,
                                                        facecolor='none', 
                                                        lw=2, 
                                                        edgecolor='k', 
                                                        zorder=3, 
                                                        label='button_add_player_name')
        self.ax.text(0.12, 0.85, 'Player Name', size=12, style='italic', label='text_new_player_name')
        self.ax.add_artist(self.button_add_player_name)
        self.new_player_name = ''
        x, y = self._get_center(self.button_add_player_name)
        self.text_new_player_name = self.ax.text(x, y, '', ha='center', va='center', size=12, weight='bold', label='text_new_player_name')


        ###  "add player rating" button
        self.button_add_player_rating = patches.Rectangle([0.39, 0.79],
                                                          width=0.07,
                                                          height=0.05,
                                                          facecolor='none', 
                                                          lw=2, 
                                                          edgecolor='k', 
                                                          zorder=3, 
                                                          label='button_add_player_rating')
        self.ax.text(0.4, 0.85, 'Rating', size=12, style='italic', label='text_new_player_rating')
        self.ax.add_artist(self.button_add_player_rating)
        self.new_player_rating = ''
        x, y = self._get_center(self.button_add_player_rating)
        self.text_new_player_rating = self.ax.text(x, y, '', ha='center', va='center', size=12, weight='bold', label='text_new_player_rating')



    def _onClick(self, event):


        if self._was_clicked(self.button_standings, event):
            print('standings')


        ###  Registraion: add player
        if (self.active_display == 'registration') and (self._was_clicked(self.button_add_player, event)):

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


        ###  Registraion: add player name
        if (self.active_display == 'registration') and (self._was_clicked(self.button_add_player_name, event)):
            self.active_button = self.button_add_player_name
            self.active_button.set_facecolor('#ffff99')
            self.button_add_player_rating.set_facecolor('w')
            self._redraw()


        ###  Registraion: add player rating
        if (self.active_display == 'registration') and (self._was_clicked(self.button_add_player_rating, event)):
            self.active_button = self.button_add_player_rating
            self.active_button.set_facecolor('#ffff99')
            self.button_add_player_name.set_facecolor('w')
            self._redraw()


        ###  Registraion: remove player
        if self.active_display == 'registration':
            for row in self.list_standings_rows:

                ###  remove if button is clicked and row is occupied
                if self._was_clicked(row.button_remove_player, event) and (row.idx < self.participants.n_participants):
                    self.participants.remove_participant(row.idx)
                    self._redraw_standings_table()
                    self._redraw()


        ###  Registraion: start round 1
        if (self.active_display == 'registration') and (self._was_clicked(self.button_start_round_1, event)):

            ###  confirmation prompt
            self.ax.fill_between([0, 1], 0, 1, color='w', alpha=0.75, zorder=5)

            self.prompt_box = patches.FancyBboxPatch([0.3, 0.3], 
                                                 width=0.4, 
                                                 height=0.4, 
                                                 boxstyle=patches.BoxStyle('round', pad=0.02), 
                                                 facecolor='w', 
                                                 lw=4, 
                                                 ec='k', 
                                                 zorder=5)
            x, y = self._get_center(self.prompt_box)
            self.ax.text(x, y+0.08, 'Ready to start Round 1 ?', size=18, ha='center', va='bottom', weight='bold', zorder=6)
            self.ax.text(x, y, 'Currently %i participants' % self.participants.n_participants, size=14, color='#666666', ha='center', va='bottom', zorder=6)

            self.prompt_box_yes = patches.FancyBboxPatch([0.35, 0.35], 
                                                     width=0.12, 
                                                     height=0.08, 
                                                     boxstyle=patches.BoxStyle('round', pad=0.01), 
                                                     facecolor='w', 
                                                     lw=2, 
                                                     ec='k', 
                                                     zorder=5)
            x, y = self._get_center(self.prompt_box_yes)
            self.ax.text(x, y, 'Yes', size=18, ha='center', va='center', weight='bold', zorder=6)

            self.prompt_box_no = patches.FancyBboxPatch([0.53, 0.35], 
                                                    width=0.12, 
                                                    height=0.08, 
                                                    boxstyle=patches.BoxStyle('round', pad=0.01), 
                                                    facecolor='w', 
                                                    lw=2, 
                                                    ec='k', 
                                                    zorder=5)
            x, y = self._get_center(self.prompt_box_no)
            self.ax.text(x, y, 'No', size=18, ha='center', va='center', weight='bold', zorder=6)

            self.ax.add_artist(self.prompt_box)
            self.ax.add_artist(self.prompt_box_yes)
            self.ax.add_artist(self.prompt_box_no)
            self.active_display = 'start_round_1_prompt'
            self._redraw()


        ###  Start Round 1 Prompt: start round 1 YES
        if (self.active_display == 'start_round_1_prompt') and (self._was_clicked(self.prompt_box_yes, event)):

            self.ax.collections[-1].remove()
            self.ax.patches[-1].remove()
            self.ax.patches[-1].remove()
            self.ax.patches[-1].remove()
            self.ax.texts[-1].remove()
            self.ax.texts[-1].remove()
            self.ax.texts[-1].remove()
            self.ax.texts[-1].remove()
            self.current_round = 1
            self._redraw()

            self.start_round_1()


        ###  Start Round 1 Prompt: start round 1 NO
        if (self.active_display == 'start_round_1_prompt') and (self._was_clicked(self.prompt_box_no, event)):

            self.ax.collections[-1].remove()
            self.ax.patches[-1].remove()
            self.ax.patches[-1].remove()
            self.ax.patches[-1].remove()
            self.ax.texts[-1].remove()
            self.ax.texts[-1].remove()
            self.ax.texts[-1].remove()
            self.ax.texts[-1].remove()
            self.active_display = 'registration'
            self._redraw()


        ###  Round X: adding score
        if (self.active_display == 'round_%i'%self.current_round):
            for row in self.list_standings_rows:
                if (row.idx < self.participants.n_participants) and (self._was_clicked(row.dict_rounds[self.active_display]['box_score'], event)):
                    self.active_button.set_facecolor('w')
                    self.active_button = row.dict_rounds[self.active_display]['box_score']
                    self.active_button.set_facecolor('#ffff99')
                    self._redraw()




        ###  Round X: start next round
        if (self.active_display == 'round_%i'%self.current_round) and (self._was_clicked(self.button_add_next_round, event)):
            self.active_button = self.button_add_next_round


            ###  checking that all score entries for this round are valid
            valid_scores = True
            scores = []
            for row in self.list_standings_rows:
                if (row.idx < self.participants.n_participants):

                    s = row.dict_rounds[self.active_display]['text_score'].get_text()
                    if (s == '') or (s.count('.') > 1):
                        row.dict_rounds[self.active_display]['box_score'].set_facecolor('r')
                        valid_scores = False

                    else:
                        scores.append(float(s))
                        row.dict_rounds[self.active_display]['box_score'].set_facecolor('w')

            ###  if scores are valid, record them and start next round
            if valid_scores:
                scores = numpy.array(scores, dtype=float)
                self.participants.round_scores.append(scores)
                self.participants.total_scores += scores

                self.start_next_round()

            self._redraw()








        ###  Round X: end tournament
        if (self.active_display == 'round_%i'%self.current_round) and (self._was_clicked(self.button_end_tournament, event)):
            print('end tournament')





    def start_round_1(self):

        ###  discading "remove player buttons"
        for i_button in range(len(self.ax.patches))[::-1]:
            if 'button_remove_player' in self.ax.patches[i_button].get_label():
                self.ax.patches[i_button].remove()

        ###  discarding add new player buttons
        for i_button in range(len(self.ax.patches))[::-1]:
            if 'button_add_player' in self.ax.patches[i_button].get_label():
                self.ax.patches[i_button].remove()

        for i_text in range(len(self.ax.texts))[::-1]:
            if 'text_remove_player' in self.ax.texts[i_text].get_label():
                self.ax.texts[i_text].remove()

        for i_text in range(len(self.ax.texts))[::-1]:
            if 'text_new_player' in self.ax.texts[i_text].get_label():
                self.ax.texts[i_text].remove()

        self.button_start_round_1.set_width(0.1)
        x, y = self._get_center(self.button_start_round_1)
        self.text_button_start_round_1.set_x(x)
        self.text_button_start_round_1.set_y(y)

        self.text_button_standings.set_text('Standings')
        self.text_button_start_round_1.set_text('Round 1')


        ###  adding "add next round" button
        self.button_add_next_round = patches.FancyBboxPatch([0.2+(BUTTON_WIDTH+0.03), 0.93], 
                                                              width=0.025, 
                                                              height=BUTTON_HEIGHT, 
                                                              boxstyle=patches.BoxStyle('round', pad=0.01), 
                                                              facecolor='none', 
                                                              lw=2, 
                                                              label='button_add_next_round')
        x, y = self._get_center(self.button_add_next_round)
        self.text_button_add_next_round = self.ax.text(x, y, '+', ha='center', va='center', size=18, weight='bold')
        self.list_buttons.append(self.button_add_next_round)
        self.ax.add_artist(self.button_add_next_round)

        ###  adding "end tournament" button
        self.button_end_tournament = patches.FancyBboxPatch([0.2+(BUTTON_WIDTH+0.03+0.055), 0.93], 
                                                              width=0.04, 
                                                              height=BUTTON_HEIGHT, 
                                                              boxstyle=patches.BoxStyle('round', pad=0.01), 
                                                              facecolor='none', 
                                                              lw=2, 
                                                              label='button_end_tournament')
        x, y = self._get_center(self.button_end_tournament)
        self.text_button_end_tournament = self.ax.text(x, y, 'end', ha='center', va='center', size=14, weight='bold')
        self.list_buttons.append(self.button_end_tournament)
        self.ax.add_artist(self.button_end_tournament)



        ###  adding new round columns to standings table
        for i, row in enumerate(self.list_standings_rows):
            if i < self.participants.n_participants:
                row.add_new_round_columns(i_round=1)


        ###  adding column titles for round 1
        box = self.list_standings_rows[0].dict_rounds['round_1']['box_opp']
        x, y = box.get_x(), box.get_y()
        w, h = box.get_width(), box.get_height()
        box_opp_title = patches.Rectangle([x, y+h],
                                           width=w,
                                           height=h,
                                           facecolor='none', 
                                           lw=0.5, 
                                           zorder=3, 
                                           edgecolor='k', 
                                           label='title_opp_round_1')
        x0, y0 = self._get_center(box_opp_title)
        self.ax.text(x0, y0, 'Opp.', size=9, ha='center', va='center')

        box_score_title = patches.Rectangle([x+w, y+h],
                                             width=w,
                                             height=h,
                                             facecolor='none', 
                                             lw=0.5, 
                                             zorder=3, 
                                             edgecolor='k', 
                                           label='title_score_round_1')
        x0, y0 = self._get_center(box_score_title)
        self.ax.text(x0, y0, 'Score', size=9, ha='center', va='center')

        box_title = patches.Rectangle([x, y+2*h],
                                       width=2*w,
                                       height=h,
                                       facecolor='none', 
                                       lw=0.5, 
                                       zorder=3, 
                                       edgecolor='k', 
                                       label='title_round_1')
        x0, y0 = self._get_center(box_title)
        self.ax.text(x0, y0, 'Round 1', size=9, ha='center', va='center', weight='bold')

        self.ax.add_artist(box_opp_title)
        self.ax.add_artist(box_score_title)
        self.ax.add_artist(box_title)



        ###  generating pairings
        n = self.participants.n_participants
        pairings = numpy.append(numpy.arange(n//2, n), numpy.arange(n//2))
        self.participants.opponents.append(pairings)

        for idx, idx_opp in enumerate(pairings):
            text_opp = self.list_standings_rows[idx].dict_rounds['round_1']['text_opp']
            text_opp.set_text('%i'%(idx_opp+1))




        self.active_display = 'round_1'
        self._redraw()


    def start_next_round(self):

        self.current_round += 1
        self.text_button_start_round_1.set_text('Round %i' % self.current_round)



        ###  adding new round columns to standings table
        for i, row in enumerate(self.list_standings_rows):
            if i < self.participants.n_participants:
                row.add_new_round_columns(i_round=self.current_round)


        ###  adding column titles for round
        box = self.list_standings_rows[0].dict_rounds['round_%i'%self.current_round]['box_opp']
        x, y = box.get_x(), box.get_y()
        w, h = box.get_width(), box.get_height()
        box_opp_title = patches.Rectangle([x, y+h],
                                           width=w,
                                           height=h,
                                           facecolor='none', 
                                           lw=0.5, 
                                           zorder=3, 
                                           edgecolor='k', 
                                           label='title_opp_round_%i'%self.current_round)
        x0, y0 = self._get_center(box_opp_title)
        self.ax.text(x0, y0, 'Opp.', size=9, ha='center', va='center')

        box_score_title = patches.Rectangle([x+w, y+h],
                                             width=w,
                                             height=h,
                                             facecolor='none', 
                                             lw=0.5, 
                                             zorder=3, 
                                             edgecolor='k', 
                                           label='title_score_round_%i'%self.current_round)
        x0, y0 = self._get_center(box_score_title)
        self.ax.text(x0, y0, 'Score', size=9, ha='center', va='center')

        box_title = patches.Rectangle([x, y+2*h],
                                       width=2*w,
                                       height=h,
                                       facecolor='none', 
                                       lw=0.5, 
                                       zorder=3, 
                                       edgecolor='k', 
                                       label='title_round_%i'%self.current_round)
        x0, y0 = self._get_center(box_title)
        self.ax.text(x0, y0, 'Round %i'%self.current_round, size=9, ha='center', va='center', weight='bold')

        self.ax.add_artist(box_opp_title)
        self.ax.add_artist(box_score_title)
        self.ax.add_artist(box_title)

        self.active_display = 'round_%i' % self.current_round



    def _onKeyPress(self, event):


        ###  add new player name
        if (self.active_display == 'registration') and (self.active_button.get_label() == 'button_add_player_name'):

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


        if (self.active_display == 'registration') and (self.active_button.get_label() == 'button_add_player_rating'):

            if event.key in string.digits + '.':
                self.new_player_rating += event.key

            elif (self.new_player_rating != '') and (event.key.lower() == 'backspace'):
                self.new_player_rating = self.new_player_rating[:-1]


            self.text_new_player_rating.set_text(self.new_player_rating)
            self._redraw()


        ###  add new player with "enter"
        if (self.active_display == 'registration') and (event.key.lower() == 'enter'):

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


        ###  Round X: adding score
        if (self.active_display == 'round_%i'%self.current_round) and ('box_score_' in self.active_button.get_label()):

            #box_score_idx_4_round_1
            idx = int(self.active_button.get_label().split('_')[3])
            text_obj = self.list_standings_rows[idx].dict_rounds[self.active_display]['text_score']
            text_text = text_obj.get_text()

            if event.key in string.digits + '.':
                text_text += event.key

            elif (text_text != '') and (event.key.lower() == 'backspace'):
                text_text = text_text[:-1]

            text_obj.set_text(text_text)
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

                seed = self.participants.idx[idx]+1
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





