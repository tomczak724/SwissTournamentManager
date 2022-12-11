import os
import time
import numpy
import PySimpleGUI as sg

from ParticipantRoster import ParticipantRoster

sg.theme('DarkGrey15')
FONT = 'bitstream charter'
CURRENT_ROUND = 0

PARTICIPANTS = ParticipantRoster()

file_participants = 'registrant_list.csv'
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

    popup = sg.Window('Enter Scores', 
                      layout=[
                              [sg.Column(layout=[[sg.Text(name1, font=(FONT, 14))], 
                                                 [sg.Text(name2, font=(FONT, 14))]]), 
                               sg.Column(layout=[[sg.InputText(size=(4, 3), border_width=2, font=(FONT, 14), justification='center', key='-SUBMIT SCORE PLAYER 1-')], 
                                                 [sg.InputText(size=(4, 3), border_width=2, font=(FONT, 14), justification='center', key='-SUBMIT SCORE PLAYER 2-')]])], 
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


    standings_table = sg.Table(values=table_values, 
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




right_click_menu = ['', ['edit player', 'remove player', 'do nothing']]

registration_table = sg.Table(values=PARTICIPANTS.get_roster_list(integer_rating=True), 
                              headings=['', 'Name', 'Rating'], 
                              size=(900, 250),
                              font=(FONT, 12),
                              col_widths=[3, 20, 6],
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
                          sg.Column(pad=10, layout=[[sg.Text(' Name: ', font=(FONT, 14)), 
                                                     sg.InputText(size=(20, 3), border_width=2, font=(FONT, 14), key='-NEW PLAYER NAME-')], 

                                                    [sg.Text('Rating: ', font=(FONT, 14)), 
                                                     sg.InputText(size=(6, 3), border_width=2, font=(FONT, 14), key='-NEW PLAYER RATING-')], 

                                                    [sg.Text('     ', font=(FONT, 14)), 
                                                     sg.Button('Add Player', border_width=2, font=(FONT, 13), key='-ADD NEW PLAYER-')], 

                                                    [sg.Text('', font=(FONT, 20))], 

                                                    [sg.Text('Number of Rounds : ', font=(FONT, 14)), 
                                                     sg.DropDown(values=[1, 2, 3, 4, 5], default_value=5, font=(FONT, 16), readonly=True, key='-DROPDOWN N ROUNDS-')], 

                                                    [sg.Text('', font=(FONT, 20))], 

                                                    [sg.Button('Start Round 1', border_width=2, font=(FONT, 18), key='-START ROUND 1-')]

                                                    
                                                      ])
                        ]
                      ]


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
        confirmation = sg.popup_yes_no('Want to start Round 1 ?', 
                                       title='Start Tournament', 
                                       font=(FONT, 18))

        if confirmation != 'Yes':
            continue


        ###  generating round 1 pairings
        ###  giving BYE to lowest ranked player (for odd number of participants)
        n = PARTICIPANTS.n_participants
        if n%2 == 1:
            pairings = numpy.arange(n-1).reshape((2, (n-1)//2)).T.tolist()
            pairings.append([n-1, 'BYE'])
        else:
            pairings = numpy.arange(n).reshape((2, n//2)).T.tolist()

        PARTICIPANTS.all_prev_pairings += ['%sv%s' % (p0, p1) for (p0, p1) in pairings]
        PARTICIPANTS.all_prev_pairings += ['%sv%s' % (p1, p0) for (p0, p1) in pairings]

        opponents = [PARTICIPANTS.idx[j] for i, j in pairings] + [PARTICIPANTS.idx[i] for i, j in pairings]
        PARTICIPANTS.opponents.append(opponents)

        PARTICIPANTS.current_round_scores = numpy.array([numpy.nan]*PARTICIPANTS.n_participants)

        ###  generating layout for pairings
        layout_pairings = []
        for i_pair, (p0, p1) in enumerate(pairings):

            t = sg.Table(values=[[p0+1, PARTICIPANTS.names[p0], ''], [p1+1, PARTICIPANTS.names[p1], '']], 
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
        window['-TABGROUP-'].add_tab(sg.Tab(' Round 1 ', 
                                            [[sg.Button('Standings', font=(FONT, 16), key='-GET STANDINGS-'), 
                                              sg.Button('Start Next Round', font=(FONT, 16), key='-START NEXT ROUND-'), 
                                              sg.Button('End Tournament', font=(FONT, 16), key='-END TOURNAMENT-')], 
                                             [sg.Column(layout=layout_pairings, 
                                                        size=(800, 400), 
                                                        scrollable=True, 
                                                        vertical_scroll_only=True, 
                                                        sbar_width=1, 
                                                        sbar_arrow_width=1, 
                                                        element_justification='center', 
                                                        expand_y=True)]], 
                                            key='-TAB ROUND 1-', 
                                            element_justification='center'))



        ###  hiding registration tab
        window['-TAB REGISTRATION-'].update(visible=False)
        window['-TAB ROUND 1-'].select()

        CURRENT_ROUND = 1

    ###  show standings table
    elif (event == '-GET STANDINGS-'):
        popupStandings()

    ###  prompt to enter scores from games
    elif isinstance(event, tuple) and ('PAIRING R' in event[0]):

        ###  parsing round and table numbers
        idx_round, idx_table = event[0].split('PAIRING ')[1].split('T')
        idx_round = int(idx_round.strip('R'))
        idx_table = int(idx_table.strip('-'))

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

            PARTICIPANTS.current_round_scores[idx1-1] = score1
            PARTICIPANTS.current_round_scores[idx2-1] = score2

    ###  start next round
    elif (event == '-START NEXT ROUND-'):

        ###  confirm that all scores have been entered
        if numpy.isnan(PARTICIPANTS.current_round_scores).any():
            sg.popup_no_titlebar('Round not finished', 
                                 font=(FONT, 16), 
                                 auto_close=True, 
                                 auto_close_duration=3)
            continue


        ###  confirm that user actually wants to start next round
        confirmation = sg.popup_yes_no('Want to start Round %i ?' % (CURRENT_ROUND+1), 
                                       title='Start Tournament', 
                                       font=(FONT, 18))

        if confirmation != 'Yes':
            continue


        ###  logging scores from finished round and prepping for next
        PARTICIPANTS.total_scores += PARTICIPANTS.current_round_scores
        PARTICIPANTS.all_round_scores.append(PARTICIPANTS.current_round_scores.tolist())
        PARTICIPANTS.current_round_scores = numpy.array([numpy.nan]*PARTICIPANTS.n_participants)
        CURRENT_ROUND += 1


window.close()
