import os
import time
import numpy
import itertools
import PySimpleGUI as sg

from ParticipantRoster import ParticipantRoster

sg.theme('DarkGrey15')
FONT = 'bitstream charter'
CURRENT_ROUND = 0
ROUND_RESET_COUNTER = 0   # for keeping track of number of times a new round tab is created from customized pairings

PARTICIPANTS = ParticipantRoster()

file_participants = 'participants.csv'
if os.path.exists(file_participants):
    with open(file_participants, 'r') as fopen:
        for line in fopen.readlines():
            name, rating = line.strip('\n').split(',')
            if name.lower() == 'name':
                continue

            PARTICIPANTS.add_participant(name, int(rating))



def popupEditPlayer(current_name, current_rating):

    popup = sg.Window('Edit Player',
                      layout=[
                              [sg.Column(layout=[[sg.Text('Name', font=(FONT, 14))], 
                                                 [sg.InputText(size=(25, 3), default_text=current_name, border_width=2, font=(FONT, 14), key='-EDIT PLAYER NAME-')]]), 
                               sg.Column(layout=[[sg.Text('Rating', font=(FONT, 14))], 
                                                 [sg.InputText(size=(6, 3), default_text=int(current_rating), border_width=2, font=(FONT, 14), key='-EDIT PLAYER RATING-')]])], 
                              [sg.Button('Submit', font=(FONT, 14), key='-SUBMIT-'), 
                               sg.Button('Cancel', font=(FONT, 14), key='-CANCEL-')]
                             ]
                      )

    while True:

        event, values = popup.read()

        if event == '-SUBMIT-':
            try:
                new_name = values['-EDIT PLAYER NAME-']
                new_rating = int(values['-EDIT PLAYER RATING-'])
                popup.close()
                return (new_name, new_rating)

            except ValueError:
                sg.popup_no_titlebar('Invalid Inputs', 
                                     font=(FONT, 12), 
                                     auto_close=True, 
                                     auto_close_duration=3)

        elif (event == '-CANCEL-') or (event == sg.WIN_CLOSED):
            popup.close()
            return (current_name, current_rating)

def popupEnterScores(name1, name2):

    default_text1, disabled1 = '', False
    default_text2, disabled2 = '', False
    if name1 == 'BYE':
        default_text1, disabled1 = '0', True
    if name2 == 'BYE':
        default_text2, disabled2 = '0', True

    popup = sg.Window('Enter Scores', 
                      layout=[
                              [sg.Column(layout=[[sg.Text(name1, font=(FONT, 14))], 
                                                 [sg.Text(name2, font=(FONT, 14))]]), 
                               sg.Column(layout=[[sg.InputText(size=(4, 3), 
                                                               border_width=2, 
                                                               default_text=default_text1, 
                                                               disabled=disabled1, 
                                                               font=(FONT, 14), 
                                                               justification='center', 
                                                               key='-SUBMIT SCORE PLAYER 1-')], 
                                                 [sg.InputText(size=(4, 3), 
                                                               border_width=2, 
                                                               default_text=default_text2, 
                                                               disabled=disabled2, 
                                                               font=(FONT, 14), 
                                                               justification='center', 
                                                               key='-SUBMIT SCORE PLAYER 2-')]])], 
                              [sg.Button('Submit', font=(FONT, 14), key='-SUBMIT-'), 
                               sg.Button('Cancel', font=(FONT, 14), key='-CANCEL-')]
                             ]
                      )

    while True:

        event, values = popup.read()

        if event == '-SUBMIT-':
            try:
                score1 = float(values['-SUBMIT SCORE PLAYER 1-'])
                score2 = float(values['-SUBMIT SCORE PLAYER 2-'])
                popup.close()
                return (score1, score2)

            except ValueError:
                sg.popup_no_titlebar('Invalid Inputs', 
                                     font=(FONT, 12), 
                                     auto_close=True, 
                                     auto_close_duration=3)

        elif (event == '-CANCEL-') or (event == sg.WIN_CLOSED):
            popup.close()
            return (None, None)

def popupStandings():

    table_headings = ['', 'Name', 'Rating']
    table_widths = [3, 20, 7]
    table_values = PARTICIPANTS.get_roster_list(integer_rating=True)

    for idx in PARTICIPANTS.idx:

        for i_round in range(len(PARTICIPANTS.all_round_scores)):

            if idx == 0:
                table_headings += ['Round %i' % (i_round+1)]
                table_widths += [8]
            table_values[idx] += [PARTICIPANTS.all_round_scores[i_round][idx]]

        if idx == 0:
            table_headings += ['Total']
            table_widths += [10]
        table_values[idx] += [PARTICIPANTS.total_scores[idx]]

    ###  converting table_values to a structured array
    table_values_struc = numpy.array([tuple(row) for row in table_values], 
                                     dtype=[(field, 'U50') for field in table_headings])

    standings_table = sg.Table(values=numpy.sort(table_values_struc, order=['Total', 'Rating'])[::-1].tolist(), 
                               headings=table_headings, 
                               col_widths=table_widths,
                               size=(900, 250),
                               font=(FONT, 12),
                               auto_size_columns=False,
                               justification='center',
                               key='-STANDINGS TABLE-',
                               pad=0,
                               enable_events=True,
                               enable_click_events=True,
                               expand_x=False,
                               expand_y=False)


    window_standings = sg.Window(title='Standings', 
                                 layout=[[standings_table]], 
                                 size=(850, 670), 
                                 element_justification='center', 
                                 resizable=True)


    while True:

        event, values = window_standings.read()

        if event == sg.WIN_CLOSED:
            break

    window_standings.close()

def popupCustomPairings():


    ###  grabbing participant info
    ###  and instantiating custom pairing variables
    nominal_pairings = PARTICIPANTS.opponents[-1]
    player_list = ['%.1f   %s' % (score, name) for score, name in zip(PARTICIPANTS.total_scores, PARTICIPANTS.names)]
    candidate_pairing = []
    candidate_byes = []

    n_tables = len(nominal_pairings) // 2
    layout_pairings = []
    for idx in range(n_tables):

        t = sg.Table(values=[], 
                     headings=['Table %i' % (idx+1)], 
                     key='-HEADING TABLE%i-'%(idx+1), 
                     size=(300, 0),
                     font=(FONT, 12),
                     pad=0,
                     select_mode=sg.TABLE_SELECT_MODE_NONE,
                     col_widths=[26],
                     hide_vertical_scroll=True,
                     auto_size_columns=False,
                     justification='center',
                     expand_x=False,
                     expand_y=False)

        if idx%2 == 0:
            layout_pairings.append([])
            layout_pairings.append([])
            layout_pairings.append([])
            layout_pairings.append([])
        else:
            layout_pairings[-3].append(sg.Text(' '*20, pad=0, font=(FONT, 12), key='-WHITESPACE %iA-'%(idx+1)))
            layout_pairings[-2].append(sg.Text(' '*20, pad=0, font=(FONT, 12), key='-WHITESPACE %iB-'%(idx+1)))
            layout_pairings[-1].append(sg.Text(' '*20, pad=0, font=(FONT, 12), key='-WHITESPACE %iC-'%(idx+1)))


        layout_pairings[-4].append(sg.Text(' ', pad=0, font=(FONT, 12), key='-WHITESPACE %iD'%(idx+1)))
        layout_pairings[-3].append(t) 
        layout_pairings[-2].append(sg.ButtonMenu(button_text=' ', 
                                                 menu_def=['junk', [' ']+player_list], 
                                                 pad=0, 
                                                 key='-BUTTONMENU TABLE%i PLAYER1-'%(idx+1), 
                                                 size=(28, 1), 
                                                 border_width=0, 
                                                 text_color='white', 
                                                 font=(FONT, 12)))
        layout_pairings[-1].append(sg.ButtonMenu(button_text=' ', 
                                                 menu_def=['junk', [' ']+player_list], 
                                                 pad=0, 
                                                 key='-BUTTONMENU TABLE%i PLAYER2-'%(idx+1), 
                                                 size=(28, 1), 
                                                 border_width=0, 
                                                 text_color='white', 
                                                 font=(FONT, 12)))


    ###  table for assigning BYES
    values = [['X', ' '*10+cand] for cand in candidate_byes]
    bye_table = sg.Table(values=values, 
                         headings=['', 'BYE(s)'], 
                         key='-TABLE BYE ASSIGNMENT-', 
                         size=(300, 7),
                         font=(FONT, 12),
                         pad=15,
                         select_mode=sg.TABLE_SELECT_MODE_NONE,
                         col_widths=[2, 28],
                         hide_vertical_scroll=True,
                         auto_size_columns=False,
                         enable_events=True,
                         enable_click_events=True,
                         justification='left',
                         expand_x=False,
                         expand_y=False)

    assign_bye_button = sg.ButtonMenu(button_text='Assign BYE', 
                                      font=(FONT, 14), 
                                      item_font=(FONT, 12), 
                                      text_color='white', 
                                      key='-BUTTONMENU ASSIGN BYE-', 
                                      menu_def=['junk', player_list])

    buttons = [sg.Button('Submit Pairing', border_width=2, font=(FONT, 16), key='-SUBMIT CUSTOM PAIRINGS-'), 
               sg.Button('Nominal Pairings', border_width=2, font=(FONT, 16), key='-NOMINAL PAIRINGS-'), 
               sg.Button('Clear All', border_width=2, font=(FONT, 16), key='-CLEAR ALL PAIRINGS-'), 
               sg.Button('Cancel', border_width=2, font=(FONT, 16), key='-CANCEL CUSTOM PAIRINGS-')]

    layout_edit_parings = [sg.Column(layout=layout_pairings, 
                                     size=(650, 590), 
                                     pad=0, 
                                     scrollable=True, 
                                     vertical_scroll_only=True, 
                                     sbar_width=1, 
                                     element_justification='center'), 
                           sg.Column(layout=[[assign_bye_button], 
                                             [bye_table]], 
                                          element_justification='center')
                           ]

    window_custom_pairings = sg.Window('Generate Custom Pairings for Round %i' % CURRENT_ROUND, 
                                     [[buttons], [layout_edit_parings]], 
                                     location=(50, 0), 
                                     size=(1050, 670), 
                                     sbar_arrow_width=1,
                                     element_justification='center', 
                                     resizable=True)

    while True:

        event, values = window_custom_pairings.read()
        print('\n')
        print(time.ctime())
        print('THE EVENT IS:  ', event)
        if values is not None:
            for i, (k, v) in enumerate(values.items()):
                if i == 0:
                    print('THE VALUES:    "%s":' % k, v)
                else:
                    print('               "%s":' % k, v)

        if (event == sg.WIN_CLOSED) or (event == '-CANCEL CUSTOM PAIRINGS-'):
            break

        ###  add player to table assignment
        if ('BUTTONMENU TABLE' in event):

            ###  check if there was already a player assigned to this slot
            ###  and if so re-adding them to player_list
            current_player = window_custom_pairings[event].ButtonText
            if current_player != ' ':
                player_list.append(current_player)

            ###  removing chosen player from player_list
            p = values[event]
            if p != ' ':
                junk = player_list.pop(player_list.index(p))

            ###  assigning chosen player to slot
            window_custom_pairings[event].update(button_text=p)

            ###  updating buttonmenu options
            for k in values.keys():
                if 'BUTTONMENU TABLE' in k:
                    window_custom_pairings[k].update(menu_definition=['junk', [' ']+player_list])
                elif 'BUTTONMENU ASSIGN BYE' in k:
                    window_custom_pairings[k].update(menu_definition=['junk', player_list])

        ###  add player to BYE assignment table
        if (event == '-BUTTONMENU ASSIGN BYE-'):

            ###  removing chosen player from player_list
            p = values['-BUTTONMENU ASSIGN BYE-']
            if p != ' ':
                junk = player_list.pop(player_list.index(p))

            ###  adding to candidate_byes and updating BYE table
            candidate_byes.append(p)
            window_custom_pairings['-TABLE BYE ASSIGNMENT-'].update(values=[['X', ' '*10+cand] for cand in candidate_byes])

            ###  updating buttonmenu options
            for k in values.keys():
                if 'BUTTONMENU TABLE' in k:
                    window_custom_pairings[k].update(menu_definition=['junk', [' ']+player_list])
                elif 'BUTTONMENU ASSIGN BYE' in k:
                    window_custom_pairings[k].update(menu_definition=['junk', player_list])

        ###  remove player from BYE assignment table
        if isinstance(event, tuple) and (event[0] == '-TABLE BYE ASSIGNMENT-') and \
           (event[1] == '+CLICKED+') and (event[2][1] == 0) and (event[2][0] != -1):

            ###  removing player from BYE table
            idx_bye = event[2][0]
            p = candidate_byes.pop(idx_bye)
            window_custom_pairings['-TABLE BYE ASSIGNMENT-'].update(values=[['X', ' '*10+cand] for cand in candidate_byes])

            ###  re-adding player to player_list
            player_list.append(p)

            ###  updating buttonmenu options
            for k in values.keys():
                if 'BUTTONMENU' in k:
                    window_custom_pairings[k].update(menu_definition=['junk', player_list])

        ###  populate slots with the auto-generated pairings
        if (event == '-NOMINAL PAIRINGS-'):

            confirmation = sg.popup_yes_no('Populate fields with automated pairings?', 
                                           title='Retrieve Nominal Pairing', 
                                           font=(FONT, 14))

            if confirmation == 'No':
                continue

            ###  iterating over nominal table assignments
            candidate_byes = []
            for i_table in range(n_tables):

                idx_player1 = i_table
                idx_player2 = nominal_pairings[idx_player1]

                if idx_player2 == 'BYE':
                    candidate_byes.append('%.1f   %s' % (PARTICIPANTS.total_scores[idx_player1], PARTICIPANTS.names[idx_player1]))
                else:
                    window_custom_pairings['-BUTTONMENU TABLE%i PLAYER1-'%(i_table+1)].update(button_text='%.1f   %s' % (PARTICIPANTS.total_scores[idx_player1], PARTICIPANTS.names[idx_player1]))
                    window_custom_pairings['-BUTTONMENU TABLE%i PLAYER2-'%(i_table+1)].update(button_text='%.1f   %s' % (PARTICIPANTS.total_scores[idx_player2], PARTICIPANTS.names[idx_player2]))

                ###  updating buttonmenu options
                window_custom_pairings['-BUTTONMENU TABLE%i PLAYER1-'%(i_table+1)].update(menu_definition=['junk', [' ']])
                window_custom_pairings['-BUTTONMENU TABLE%i PLAYER2-'%(i_table+1)].update(menu_definition=['junk', [' ']])


            ###  populating BYE table
            window_custom_pairings['-TABLE BYE ASSIGNMENT-'].update(values=[['X', ' '*10+cand] for cand in candidate_byes])
            window_custom_pairings['-BUTTONMENU ASSIGN BYE-'].update(menu_definition=['junk', []])

            ###  depopulation player_list
            player_list = []

        ###  clear all current assignments
        if (event == '-CLEAR ALL PAIRINGS-'):

            confirmation = sg.popup_yes_no('Clear all current assignments?', 
                                           title='Clear Assignments', 
                                           font=(FONT, 14))

            if confirmation == 'No':
                continue

            ###  re-initializing player_list
            player_list = ['%.1f   %s' % (score, name) for score, name in zip(PARTICIPANTS.total_scores, PARTICIPANTS.names)]

            ###  removing names from buttonmenus and BYE table and updating options
            for k in values.keys():
                if 'BUTTONMENU TABLE' in k:
                    window_custom_pairings[k].update(button_text=' ', menu_definition=['junk', [' ']+player_list])
                elif 'BUTTONMENU ASSIGN BYE' in k:
                    window_custom_pairings[k].update(menu_definition=['junk', player_list])

            ###  clearing BYE table
            window_custom_pairings['-TABLE BYE ASSIGNMENT-'].update(values=[])

        ###  process submission of custom pairings
        if (event == '-SUBMIT CUSTOM PAIRINGS-'):

            ###  check that player_list is empty (i.e. all players have an assignment)
            if len(player_list) != 0:

                message = 'Still need assignment(s) for:\n'
                for player in player_list:
                    message += '\n%s' % player.split('   ')[1]

                sg.popup_no_titlebar(message, font=(FONT, 14))
                continue

            ###  recording pairings of players
            candidate_opponents = [None for i in range(PARTICIPANTS.n_participants)]
            candidate_pairings = []
            for i_table in range(n_tables):

                ###  extracting player names from buttonmenus
                player1 = window_custom_pairings['-BUTTONMENU TABLE%i PLAYER1-'%(i_table+1)].ButtonText
                player2 = window_custom_pairings['-BUTTONMENU TABLE%i PLAYER2-'%(i_table+1)].ButtonText

                ###  skip if table is completely empty (probably because muliple players are on BYE)
                if (player1 == ' ') and (player2 == ' '):
                    continue

                ###  if one slot is empty but the other is filled place the indicated player on BYE
                if (player2 == ' '):
                    player = player1.split('   ')[1]
                    idx_player = PARTICIPANTS.names.tolist().index(player)
                    candidate_opponents[idx_player] = 'BYE'
                    candidate_pairings.append('%ivBYE'%idx_player)

                elif (player1 == ' '):
                    player = player2.split('   ')[1]
                    idx_player = PARTICIPANTS.names.tolist().index(player)
                    candidate_opponents[idx_player] = 'BYE'
                    candidate_pairings.append('%ivBYE'%idx_player)

                ###  otherwise, both slots were filled
                else:
                    player1 = player1.split('   ')[1]
                    player2 = player2.split('   ')[1]
                    idx_player1 = PARTICIPANTS.names.tolist().index(player1)
                    idx_player2 = PARTICIPANTS.names.tolist().index(player2)
                    candidate_opponents[idx_player1] = idx_player2
                    candidate_opponents[idx_player2] = idx_player1
                    candidate_pairings.append('%iv%i'%(idx_player1, idx_player2))
                    candidate_pairings.append('%iv%i'%(idx_player2, idx_player1))

            ###  recording BYE assignments
            for player in candidate_byes:
                player = player.split('   ')[1]
                idx_player = PARTICIPANTS.names.tolist().index(player)
                candidate_opponents[idx_player] = 'BYE'
                candidate_pairings.append('%ivBYE'%idx_player)

            ###  check if any given pairs occurred in a past round and warn user
            overlap = set(candidate_pairings).intersection(PARTICIPANTS.all_prev_pairings)
            if len(overlap) > 0:

                message = 'WARNING\nThe following pairing(s) occurred in a previous round:\n'
                for pair in overlap:

                    opp1, opp2 = pair.split('v')
                    if opp1 == 'BYE':
                        message += '\n%s given BYE' % PARTICIPANTS.names[int(opp2)]
                    elif opp2 == 'BYE':
                        message += '\n%s given BYE' % PARTICIPANTS.names[int(opp1)]
                    else:
                        message += '\n%s vs. %s' % (PARTICIPANTS.names[int(opp1)], PARTICIPANTS.names[int(opp2)])

                message += '\n\nSubmit pairings anyway?'

            else:
                message = 'Ready to submit pairings?'


            confirmation = sg.popup_yes_no(message, 
                                           title='Submit Pairings', 
                                           font=(FONT, 14))

            ###  ready to return submitted pairings
            if confirmation == 'Yes':
                window_custom_pairings.close()
                return candidate_opponents


    window_custom_pairings.close()

def save_tournament_results_csv():

    ###  file name to store tournament results
    ctime = time.localtime()
    fname_results = 'TOURNAMENT_RESULTS__'
    fname_results += '%4i-%02i-%02i.csv' % (ctime.tm_year, ctime.tm_mon, ctime.tm_mday)

    with open(fname_results, 'w') as fopen:

        ###  writing column names
        fopen.write('seed,name,rating')
        for i_round in range(len(PARTICIPANTS.all_round_scores)):
            fopen.write(',opponent_%i,score_%i' % (i_round+1, i_round+1))
        fopen.write(',total\n')

        ###  writing a row for each participant
        for i_player in numpy.argsort(PARTICIPANTS.total_scores)[::-1]:

            fopen.write('%i,' % (PARTICIPANTS.idx[i_player]+1))
            fopen.write('%s,' % PARTICIPANTS.names[i_player])
            fopen.write('%i' % PARTICIPANTS.ratings[i_player])

            for i_round in range(len(PARTICIPANTS.all_round_scores)):
                if PARTICIPANTS.opponents[i_round][i_player] == 'BYE':
                    opp = 'BYE'
                else:
                    opp = PARTICIPANTS.opponents[i_round][i_player] + 1
                fopen.write(',%s,%.2f' % (opp, PARTICIPANTS.all_round_scores[i_round][i_player]))

            fopen.write(',%.2f\n' % PARTICIPANTS.total_scores[i_player])






right_click_menu = ['', ['edit player', 'remove player', 'do nothing']]

registration_table = sg.Table(values=PARTICIPANTS.get_roster_list(integer_rating=True), 
                              headings=['', 'Name', 'Rating'], 
                              size=(900, 250),
                              font=(FONT, 12),
                              col_widths=[3, 20, 7],
                              auto_size_columns=False,
                              justification='center',
                              key='-REGISTRATION TABLE-',
                              enable_events=True,
                              enable_click_events=True,
                              right_click_selects=True,
                              right_click_menu=right_click_menu,
                              expand_x=False,
                              expand_y=False)


registration_layout = [ [ registration_table, 
                          sg.Column(pad=50, 
                                    element_justification='left',
                                    vertical_alignment='top', 
                                    layout=[
                                            [sg.Button('Start Round 1', border_width=2, font=(FONT, 18), key='-START ROUND 1-'), 
                                             sg.Button('Clear Roster', border_width=2, font=(FONT, 18), key='-CLEAR ROSTER-')], 

                                            [sg.Text('', font=(FONT, 14))], 
                                            [sg.Text('', font=(FONT, 14))], 

                                            [sg.Text(' Name: ', font=(FONT, 14)), 
                                             sg.InputText(size=(20, 3), border_width=2, font=(FONT, 14), key='-NEW PLAYER NAME-')], 

                                            [sg.Text('Rating: ', font=(FONT, 14)), 
                                             sg.InputText(size=(6, 3), border_width=2, font=(FONT, 14), key='-NEW PLAYER RATING-')], 

                                            [sg.Text('     ', font=(FONT, 14)), 
                                             sg.Button('Add Player', border_width=2, font=(FONT, 14), key='-ADD NEW PLAYER-')]
                                            ])
                        ] ]


###  Instantiating TabGroup to contain tabs for registration and rounds
tab_group_layout = [[sg.Tab(' Registration ', registration_layout, key='-TAB REGISTRATION-')]]

# The window layout - defines the entire window
layout = [[sg.TabGroup(tab_group_layout,
                       enable_events=True,
                       font=(FONT, 14), 
                       expand_x=True, 
                       key='-TABGROUP-')]]


window = sg.Window('Swiss Tournament Manager', 
                   layout, 
                   location=(50, 0), 
                   size=(850, 670), 
                   element_justification='center', 
                   resizable=True)




###  Instantiating event loop for main window
while True:

    event, values = window.read()
    print('\n')
    print(time.ctime())
    print('THE EVENT IS:  ', event)
    if values is not None:
        for i, (k, v) in enumerate(values.items()):
            if i == 0:
                print('THE VALUES:    "%s":' % k, v)
            else:
                print('               "%s":' % k, v)


    if event == sg.WIN_CLOSED:
        break

    ###  add a new player
    elif (CURRENT_ROUND == 0) and (event == '-ADD NEW PLAYER-'):

        ###  only run if info entered
        if (values['-NEW PLAYER NAME-'] != '') and (values['-NEW PLAYER RATING-'] != ''): 

            try:
                name = values['-NEW PLAYER NAME-']
                rating = int(values['-NEW PLAYER RATING-'])
                PARTICIPANTS.add_participant(name, rating)

                window['-REGISTRATION TABLE-'].update(values=PARTICIPANTS.get_roster_list(integer_rating=True))

                ###  clearing input prompts
                junk = window['-NEW PLAYER NAME-'].update(value='')
                junk = window['-NEW PLAYER RATING-'].update(value='')
                window.refresh()

            except:
                sg.popup('Error Parsing Inputs', font=(FONT, 16))

    ###  edit an existing player
    elif (CURRENT_ROUND == 0) and (event == 'edit player') and (len(values['-REGISTRATION TABLE-']) == 1):

        idx_player = values['-REGISTRATION TABLE-'][0]
        new_name, new_rating = popupEditPlayer(PARTICIPANTS.names[idx_player], PARTICIPANTS.ratings[idx_player])

        PARTICIPANTS.remove_participant(idx_player)
        PARTICIPANTS.add_participant(new_name, int(new_rating))
        window['-REGISTRATION TABLE-'].update(values=PARTICIPANTS.get_roster_list(integer_rating=True))

    ###  remove an existing player
    elif (CURRENT_ROUND == 0) and (event == 'remove player') and (len(values['-REGISTRATION TABLE-']) == 1):

        idx_player = values['-REGISTRATION TABLE-'][0]
        confirmation = sg.popup_yes_no('Want to remove %s ?' % PARTICIPANTS.names[idx_player], 
                                       title='Remove Player', 
                                       font=(FONT, 14))

        if confirmation == 'Yes':
            PARTICIPANTS.remove_participant(idx_player)
            window['-REGISTRATION TABLE-'].update(values=PARTICIPANTS.get_roster_list(integer_rating=True))

    ###  start round 1
    elif (CURRENT_ROUND == 0) and (event == '-START ROUND 1-'):

        ###  confirm that user actually wants to start round 1
        confirmation = sg.popup_yes_no('Ready to start Round 1 ?', 
                                       title='Start Tournament', 
                                       font=(FONT, 18))

        if confirmation != 'Yes':
            continue


        ###  generating round 1 pairings
        ###  giving BYE to lowest ranked player (for odd number of participants)
        n = PARTICIPANTS.n_participants
        if n%2 == 1:
            pairings = numpy.arange(n-1).reshape((2, (n-1)//2)).T.tolist()
            opponents = [PARTICIPANTS.idx[j] for i, j in pairings] + [PARTICIPANTS.idx[i] for i, j in pairings]
            pairings.append([n-1, 'BYE'])
            opponents.append('BYE')
        else:
            pairings = numpy.arange(n).reshape((2, n//2)).T.tolist()
            opponents = [PARTICIPANTS.idx[j] for i, j in pairings] + [PARTICIPANTS.idx[i] for i, j in pairings]

        ###  recording pairings
        PARTICIPANTS.opponents.append(opponents)

        PARTICIPANTS.current_round_scores = numpy.array([numpy.nan]*PARTICIPANTS.n_participants)

        ###  generating layout for pairings
        layout_pairings = []
        for i_pair, (p0, p1) in enumerate(pairings):

            if (p1 == 'BYE'):
                vals = [[p0+1, PARTICIPANTS.names[p0], ''], ['', p1, '']]
            else:
                vals = [[p0+1, PARTICIPANTS.names[p0], ''], [p1+1, PARTICIPANTS.names[p1], '']]

            t = sg.Table(values=vals, 
                         headings=['', 'Table %i' % (i_pair+1), 'Score'], 
                         size=(300, 2),
                         font=(FONT, 12),
                         pad=10,
                         select_mode=sg.TABLE_SELECT_MODE_NONE,
                         col_widths=[3, 20, 6],
                         hide_vertical_scroll=True,
                         auto_size_columns=False,
                         justification='center',
                         key='-PAIRING R1T%i-' % (i_pair+1),
                         enable_events=True,
                         enable_click_events=True,
                         expand_x=False,
                         expand_y=False)

            if i_pair%2 == 0:
                layout_pairings.append([])

            layout_pairings[-1].append(t)

        ###  adding round 1 tab
        CURRENT_ROUND = 1
        window['-TABGROUP-'].add_tab(sg.Tab(' Round 1 ', 
                                            [[sg.Button('Standings', font=(FONT, 16), key='-GET STANDINGS %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER)), 
                                              sg.Button('Custom Pairings', font=(FONT, 16), key='-CUSTOM PAIRINGS %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER)), 
                                              sg.Button('Start Next Round', font=(FONT, 16), key='-START NEXT ROUND %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER))], 
                                             [sg.Column(layout=layout_pairings, 
                                                        size=(800, 400), 
                                                        scrollable=True, 
                                                        vertical_scroll_only=True, 
                                                        sbar_width=1, 
                                                        sbar_arrow_width=1, 
                                                        element_justification='center', 
                                                        expand_y=True)]], 
                                            key='-TAB ROUND 1_%i-' % ROUND_RESET_COUNTER, 
                                            element_justification='center'))

        ###  hiding registration tab
        window['-TAB REGISTRATION-'].update(visible=False)
        window['-TAB ROUND 1_%i-' % ROUND_RESET_COUNTER].select()

    ###  show standings table
    elif ('GET STANDINGS' in event):
        popupStandings()

    ###  prompt to edit round pairings
    elif ('CUSTOM PAIRINGS' in event):

        custom_opponents = popupCustomPairings()

        ###  skip if no custom pairings returned
        if custom_opponents is None:
            continue


        ###  updating the last pairing in PARTICIPANTS
        PARTICIPANTS.opponents[-1] = custom_opponents

        ###  generating layout for pairings
        layout_pairings = []

        i_table = 0
        str_pairings = []
        for idx_player1, idx_player2 in enumerate(custom_opponents):

            ###  extract opponent names for table info
            if idx_player2 == 'BYE':
                vals = [[idx_player1+1, PARTICIPANTS.names[idx_player1], ''], ['', 'BYE', '']]
                str1_pair = '%ivBYE' % idx_player1
                str2_pair = 'BYEv%i' % idx_player1
            else:
                vals = [[idx_player1+1, PARTICIPANTS.names[idx_player1], ''], [idx_player2+1, PARTICIPANTS.names[idx_player2], '']]
                str1_pair = '%iv%i' % (idx_player1, idx_player2)
                str2_pair = '%iv%i' % (idx_player2, idx_player1)


            ###  skip if this pair is already accounted for
            if (str1_pair in str_pairings) or (str2_pair in str_pairings):
                continue

            i_table += 1
            t = sg.Table(values=vals, 
                         headings=['', 'Table %i' % i_table, 'Score'], 
                         size=(300, 2),
                         font=(FONT, 12),
                         pad=10,
                         select_mode=sg.TABLE_SELECT_MODE_NONE,
                         col_widths=[3, 20, 6],
                         hide_vertical_scroll=True,
                         auto_size_columns=False,
                         justification='center',
                         key='-PAIRING R%iT%i-' % (CURRENT_ROUND, i_table),
                         enable_events=True,
                         enable_click_events=True,
                         expand_x=False,
                         expand_y=False)

            if i_table%2 == 1:
                layout_pairings.append([])

            layout_pairings[-1].append(t)
            str_pairings.append(str1_pair)
            str_pairings.append(str2_pair)


        ###  creating new tab for current round
        ROUND_RESET_COUNTER += 1
        window['-TABGROUP-'].add_tab(sg.Tab(' Round %i ' % CURRENT_ROUND, 
                                            [[sg.Button('Standings', font=(FONT, 16), key='-GET STANDINGS %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER)), 
                                              sg.Button('Custom Pairings', font=(FONT, 16), key='-CUSTOM PAIRINGS %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER)), 
                                              sg.Button('Start Next Round', font=(FONT, 16), key='-START NEXT ROUND %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER)), 
                                              sg.Button('End Tournament', font=(FONT, 16), key='-END TOURNAMENT %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER))], 
                                             [sg.Column(layout=layout_pairings, 
                                                        size=(800, 400), 
                                                        scrollable=True, 
                                                        vertical_scroll_only=True, 
                                                        sbar_width=1, 
                                                        sbar_arrow_width=1, 
                                                        element_justification='center', 
                                                        expand_y=True)]], 
                                            key='-TAB ROUND %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER), 
                                            element_justification='center'))



        ###  removing and replacing previous round tab
        window['-TAB ROUND %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER-1)].update(visible=False)
        window['-TAB ROUND %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER)].select()

    ###  prompt to enter scores from games
    elif isinstance(event, tuple) and ('PAIRING R' in event[0]):

        ###  parsing round and table numbers
        idx_round, idx_table = event[0].split('PAIRING ')[1].split('T')
        idx_round = int(idx_round.strip('R'))
        idx_table = int(idx_table.split('-')[0])

        ###  only continue if on round = CURRENT_ROUND
        if idx_round != CURRENT_ROUND:
            print('Round %i is complete' % idx_round)
            continue

        ###  grabing values from pairing table
        table_values = window[event[0]].Values
        idx1, name1, junk = table_values[0]
        idx2, name2, junk = table_values[1]

        ###  prompt to enter scores
        score1, score2 = popupEnterScores(name1, name2)

        ###  enter scores into standings if valid
        if score1 is not None:
            table_values[0][2] = score1
            table_values[1][2] = score2
            window[event[0]].update(values=table_values)

            if name1 != 'BYE':
                PARTICIPANTS.current_round_scores[idx1-1] = score1
            if name2 != 'BYE':
                PARTICIPANTS.current_round_scores[idx2-1] = score2

    ###  start next round
    elif ('START NEXT ROUND' in event):

        ###  confirm that all scores have been entered
        if numpy.isnan(PARTICIPANTS.current_round_scores).any():
            sg.popup_no_titlebar('Round not finished', 
                                 font=(FONT, 16), 
                                 auto_close=True, 
                                 auto_close_duration=3)
            continue


        ###  confirm that user actually wants to start next round
        confirmation = sg.popup_yes_no('Ready to start Round %i ?' % (CURRENT_ROUND+1), 
                                       title='Start Tournament', 
                                       font=(FONT, 18))

        if confirmation != 'Yes':
            continue

        ###  removing custom pairings and start round buttons from finished round
        window['-CUSTOM PAIRINGS %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER)].update(visible=False)
        window['-START NEXT ROUND %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER)].update(visible=False)

        ###  logging previous opponent pairings
        for p0, p1 in enumerate(PARTICIPANTS.opponents[CURRENT_ROUND-1]):
            PARTICIPANTS.all_prev_pairings.append('%sv%s' % (p0, p1))
            PARTICIPANTS.all_prev_pairings.append('%sv%s' % (p1, p0))

        ###  logging scores from finished round and prepping for next
        PARTICIPANTS.total_scores += PARTICIPANTS.current_round_scores
        PARTICIPANTS.all_round_scores.append(PARTICIPANTS.current_round_scores.tolist())
        PARTICIPANTS.current_round_scores = numpy.array([numpy.nan]*PARTICIPANTS.n_participants)

        ###  saving tournament results to csv
        save_tournament_results_csv()

        ###  updating round counters
        ROUND_RESET_COUNTER = 0
        CURRENT_ROUND += 1



        ###  GENERATING PAIRINGS - FIDE Dutch System
        ###  https://handbook.fide.com/chapter/C0403

        ###  start by simply pairng top half v. bottom half for all unique score groups

        ###  checking number of participants in each score group
        ###  For 12 participants, after round 1 with, four win/loss and two draws
        ###  >>> score_groups = [0., 0.5, 1.]
        scores = numpy.unique(PARTICIPANTS.total_scores)

        ###  reversing order so that highest score comes first
        scores = numpy.sort(scores)[::-1]

        ###  constructing score groups (SG)
        score_groups = [PARTICIPANTS.idx[PARTICIPANTS.total_scores==s].tolist() for s in scores]

        ###  empty array to hold candidate pairing
        candidate_pairing = (-numpy.ones(PARTICIPANTS.n_participants, dtype=int)).tolist()

        ###  iterating over score groups
        for i_score_group, score_group in enumerate(score_groups):

            ###  generating subgroups s1, s1 (top half, bottom half)
            max_pairs = len(score_group) // 2
            s1 = score_group[:max_pairs]
            s2 = score_group[max_pairs:]
            s1_candidate = []
            s2_candidate = []

            ###  iterating through all transpositions of s2 (i.e. permutations)
            for s2_t in itertools.permutations(s2, max_pairs):

                ###  checking if pairing with s1 is valid
                n_violations = 0

                ###  checking for pairings that occurred in a previous round
                for idx1, idx2 in zip(s1, s2_t):
                    if '%iv%i'%(idx1, idx2) in PARTICIPANTS.all_prev_pairings:
                        n_violations += 1

                ###  stop checking if no violations
                if n_violations == 0:
                    s1_candidate = s1
                    s2_candidate = s2_t
                    break

            ###  if no valid transposition of s2 exists, test swapping residents between s1 and s2
            if (len(score_group) > 1) and (n_violations > 0):
                found_valid_swapping = False

                ###  iterating over number of players to swap [1, 2, 3, ... ]
                for n_swap in range(1, max_pairs//2):

                    ###  generating all combinations of (s1, s2) with `n_swap` residents
                    for (s1_swap, s2_swap) in self._swap_residents_s1_s2(s1, s2, n_swap):

                        ###  iterating through all transpositions of s2_swap (i.e. permutations)
                        for s2_swap_t in itertools.permutations(s2_swap, max_pairs):

                            ###  checking if pairing with s1 is valid
                            n_violations = 0

                            ###  checking for pairings that occurred in a previous round
                            for idx1, idx2 in zip(s1_swap, s2_swap_t):
                                if '%iv%i'%(idx1, idx2) in PARTICIPANTS.all_prev_pairings:
                                    n_violations += 1

                            ###  stop checking if no violations
                            if n_violations == 0:
                                found_valid_swapping = True
                                s1_candidate = s1_swap
                                s2_candidate = s2_swap_t
                                break

                        ###  break swap combinations if a valid swapping of residents is found
                        if found_valid_swapping == True:
                            break

                    ###  break n_swap if a valid swapping of residents is found
                    if found_valid_swapping == True:
                        break


            ###  if only one participant in this scoregroup either downfloat or assign BYE
            if len(score_group) == 1:

                ###  downfloat to next scoregroup
                if i_score_group < len(score_groups)-1:
                    score_groups[i_score_group+1] = score_group + score_groups[i_score_group+1]

                ###  or assign BYE
                else:
                    candidate_pairing[score_group[0]] = 'BYE'


            ###  valid s2 transposition found, record candidate pairings
            elif n_violations == 0:

                ###  adding candidate pairings
                for idx, idx_opp in zip(s1_candidate, s2_candidate):
                    candidate_pairing[idx] = idx_opp
                    candidate_pairing[idx_opp] = idx

                ###  if odd number of players either downfloat or assign BYE
                if len(score_group)%2 == 1:
                    idx_downfloater = list(set(score_group) - set(s1_candidate) - set(s2_candidate))[0]

                    ###  downfloat to next scoregroup
                    if i_score_group < len(score_groups)-1:
                        score_groups[i_score_group+1] = [idx_downfloater] + score_groups[i_score_group+1]

                    ###  or assign BYE
                    else:
                        candidate_pairing[idx_downfloater] = 'BYE'


            ###  TESTING IDEA OF DOWNFLOATING ALL MEMBERS OF 
            ###  SCOREGROUP IF NO VALID CANDIDATE PAIRING IS FOUND
            else:

                ###  downfloat to next scoregroup
                if i_score_group < len(score_groups)-1:
                    for idx_downfloater in score_group:
                        score_groups[i_score_group+1] = [idx_downfloater] + score_groups[i_score_group+1]



        ###  adding valid candidate pairing to PARTICIPANTS
        PARTICIPANTS.opponents.append(candidate_pairing)


        ###  generating layout for pairings
        layout_pairings = []

        i_table = 0
        str_pairings = []
        for idx_player1, idx_player2 in enumerate(candidate_pairing):

            ###  extract opponent names for table info
            if (idx_player2 == 'BYE'):
                vals = [[idx_player1+1, PARTICIPANTS.names[idx_player1], ''], ['', 'BYE', '']]
            else:
                vals = [[idx_player1+1, PARTICIPANTS.names[idx_player1], ''], [idx_player2+1, PARTICIPANTS.names[idx_player2], '']]

            ###  skip if this pair is already accounted for
            str1_pair = '%sv%s' % (idx_player1, idx_player2)
            str2_pair = '%sv%s' % (idx_player2, idx_player1)
            if (str1_pair in str_pairings) or (str2_pair in str_pairings):
                continue

            i_table += 1
            t = sg.Table(values=vals, 
                         headings=['', 'Table %i' % i_table, 'Score'], 
                         size=(300, 2),
                         font=(FONT, 12),
                         pad=10,
                         select_mode=sg.TABLE_SELECT_MODE_NONE,
                         col_widths=[3, 20, 6],
                         hide_vertical_scroll=True,
                         auto_size_columns=False,
                         justification='center',
                         key='-PAIRING R%iT%i-' % (CURRENT_ROUND, i_pair+1),
                         enable_events=True,
                         enable_click_events=True,
                         expand_x=False,
                         expand_y=False)

            if i_table%2 == 1:
                layout_pairings.append([])

            layout_pairings[-1].append(t)
            str_pairings.append(str1_pair)
            str_pairings.append(str2_pair)



        ###  adding tab for next round
        window['-TABGROUP-'].add_tab(sg.Tab(' Round %i ' % CURRENT_ROUND, 
                                            [[sg.Button('Standings', font=(FONT, 16), key='-GET STANDINGS %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER)), 
                                              sg.Button('Custom Pairings', font=(FONT, 16), key='-CUSTOM PAIRINGS %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER)), 
                                              sg.Button('Start Next Round', font=(FONT, 16), key='-START NEXT ROUND %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER)), 
                                              sg.Button('End Tournament', font=(FONT, 16), key='-END TOURNAMENT %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER))], 
                                             [sg.Column(layout=layout_pairings, 
                                                        size=(800, 400), 
                                                        scrollable=True, 
                                                        vertical_scroll_only=True, 
                                                        sbar_width=1, 
                                                        sbar_arrow_width=1, 
                                                        element_justification='center', 
                                                        expand_y=True)]], 
                                            key='-TAB ROUND %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER), 
                                            element_justification='center'))



        ###  selecting current round tab
        window['-TAB ROUND %i_%i-' % (CURRENT_ROUND, ROUND_RESET_COUNTER)].select()

    ###  end tournament
    elif ('END TOURNAMENT' in event):

        ###  confirm that all scores have been entered
        if numpy.isnan(PARTICIPANTS.current_round_scores).any():
            sg.popup_no_titlebar('Round not finished', 
                                 font=(FONT, 16), 
                                 auto_close=True, 
                                 auto_close_duration=3)
            continue


        ###  confirm that user actually wants to end the tournament
        confirmation = sg.popup_yes_no('Are you sure you want to\nend the tournament ?', 
                                       title='End Tournament ?', 
                                       font=(FONT, 18))

        if confirmation != 'Yes':
            continue


        ###  logging scores from finished round and prepping for next
        PARTICIPANTS.total_scores += PARTICIPANTS.current_round_scores
        PARTICIPANTS.all_round_scores.append(PARTICIPANTS.current_round_scores.tolist())
        PARTICIPANTS.current_round_scores = numpy.array([numpy.nan]*PARTICIPANTS.n_participants)

        ###  saving tournament results to csv
        save_tournament_results_csv()

        ###  closing main window and opening standings window
        window.close()
        popupStandings()




window.close()
