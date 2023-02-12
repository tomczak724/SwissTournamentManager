import time
import numpy
import PySimpleGUI as sg


def get_standings_as_structured_array(participants):
    '''
    Returns the standings table as a structured array
    '''

    table_info = {'headings': ['', 'Name', 'Rating'], 
                  'fields': [('', 'U50'), ('Name', 'U50'), ('Rating', 'i')], 
                  'widths': [3, 20, 7], 
                  'struct_array': None}

    values = participants.get_roster_list(integer_rating=True)
    for idx in participants.idx:

        for i_round in range(len(participants.all_round_scores)):

            if idx == 0:
                table_info['headings'] += ['Round %i' % (i_round+1)]
                table_info['fields'] += [('Round %i'%(i_round+1), 'f')]
                table_info['widths'] += [8]
            values[idx] += [participants.all_round_scores[i_round][idx]]

        if idx == 0:
            table_info['headings'] += ['Total', 'Tie Break']
            table_info['fields'] += [('Total', 'f'), ('Tie Break', 'f')]
            table_info['widths'] += [8, 10]

        values[idx] += [participants.total_scores[idx]]
        values[idx] += [participants.tie_break_scores[idx]]

    table_info['struct_array'] = numpy.array([tuple(row) for row in values], dtype=table_info['fields'])

    return table_info

def popupEditPlayer(current_name, current_rating, font='bitstream charter'):

    popup = sg.Window('Edit Player',
                      keep_on_top=True, 
                      modal=True, 
                      layout=[
                              [sg.Column(layout=[[sg.Text('Name', font=(font, 14))], 
                                                 [sg.InputText(size=(25, 3), default_text=current_name, border_width=2, font=(font, 14), key='-EDIT PLAYER NAME-')]]), 
                               sg.Column(layout=[[sg.Text('Rating', font=(font, 14))], 
                                                 [sg.InputText(size=(6, 3), default_text=int(current_rating), border_width=2, font=(font, 14), key='-EDIT PLAYER RATING-')]])], 
                              [sg.Button('Submit', font=(font, 14), key='-SUBMIT-'), 
                               sg.Button('Cancel', font=(font, 14), key='-CANCEL-')]
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
                                     font=(font, 14), 
                                     auto_close=True, 
                                     auto_close_duration=3)

        elif (event == '-CANCEL-') or (event == sg.WIN_CLOSED):
            popup.close()
            return (current_name, current_rating)

def popupEnterScores(name1, name2, font='bitstream charter'):

    default_text1, disabled1 = '', False
    default_text2, disabled2 = '', False
    if name1 == 'BYE':
        default_text1, disabled1 = '0', True
    if name2 == 'BYE':
        default_text2, disabled2 = '0', True

    popup = sg.Window('Enter Scores', 
                      keep_on_top=True, 
                      modal=True, 
                      layout=[
                              [sg.Column(layout=[[sg.Text(name1, font=(font, 14))], 
                                                 [sg.Text(name2, font=(font, 14))]]), 
                               sg.Column(layout=[[sg.InputText(size=(4, 3), 
                                                               border_width=2, 
                                                               default_text=default_text1, 
                                                               disabled=disabled1, 
                                                               font=(font, 14), 
                                                               justification='center', 
                                                               key='-SUBMIT SCORE PLAYER 1-')], 
                                                 [sg.InputText(size=(4, 3), 
                                                               border_width=2, 
                                                               default_text=default_text2, 
                                                               disabled=disabled2, 
                                                               font=(font, 14), 
                                                               justification='center', 
                                                               key='-SUBMIT SCORE PLAYER 2-')]])], 
                              [sg.Button('Submit', font=(font, 14), key='-SUBMIT-'), 
                               sg.Button('Cancel', font=(font, 14), key='-CANCEL-')]
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
                                     font=(font, 14), 
                                     auto_close=True, 
                                     auto_close_duration=3)

        elif (event == '-CANCEL-') or (event == sg.WIN_CLOSED):
            popup.close()
            return (None, None)

def popupStandings(participants, font='bitstream charter'):

    table_info = get_standings_as_structured_array(participants)

    standings_table = sg.Table(values=numpy.sort(table_info['struct_array'], 
                                                 order=['Total', 'Tie Break', 'Rating'])[::-1].tolist(), 
                               headings=table_info['headings'], 
                               col_widths=table_info['widths'],
                               size=(1000, 250),
                               font=(font, 14),
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
                                 size=(1100, 670), 
                                 element_justification='center', 
                                 resizable=True, 
                                 modal=True)


    while True:

        event, values = window_standings.read()

        if event == sg.WIN_CLOSED:
            break

    window_standings.close()

def popupCustomPairings(participants, current_round, font='bitstream charter'):

    ###  grabbing participant info
    ###  and instantiating custom pairing variables
    nominal_pairings = participants.opponents[-1]

    table_info = get_standings_as_structured_array(participants)
    player_list = ['%.1f   %s' % (row['Total'], row['Name']) for row in numpy.sort(table_info['struct_array'], order=['Total', 'Tie Break', 'Rating'])[::-1]]

    candidate_pairing = []
    candidate_byes = []

    n_tables = len(nominal_pairings) // 2

    layout_pairings = [[sg.Text('Table',    font=(font, 14), border_width=0, size=(7, 1),  pad=(0, 3), justification='center'), 
                        sg.Text('Player 1', font=(font, 14), border_width=0, size=(25, 1), pad=(0, 3), justification='center'), 
                        sg.Text(' ',        font=(font, 14), border_width=0, size=(5, 1),  pad=(0, 3), justification='center'), 
                        sg.Text('Player 2', font=(font, 14), border_width=0, size=(25, 1), pad=(0, 3), justification='center')]]
    layout_pairings.append([sg.HorizontalSeparator()])

    for i_table in range(n_tables):

        row = [sg.Text('%i'%(i_table+1), font=(font, 14), size=(7, 1), border_width=0, pad=(0, 3), justification='center'), 
               sg.ButtonMenu(button_text=' ', 
                             menu_def=['junk', ['remove player']+player_list], 
                             pad=(0, 3), 
                             key='-BUTTONMENU TABLE%i PLAYER1-'%(i_table+1), 
                             size=(25, 1), 
                             border_width=0, 
                             text_color='white', 
                             font=(font, 14)), 
               sg.Text('vs.', font=(font, 14), size=(5, 1), border_width=0, pad=(0, 3), justification='center'), 
               sg.ButtonMenu(button_text=' ', 
                             menu_def=['junk', ['remove player']+player_list], 
                             pad=(0, 3), 
                             key='-BUTTONMENU TABLE%i PLAYER2-'%(i_table+1), 
                             size=(25, 1), 
                             border_width=0, 
                             text_color='white', 
                             font=(font, 14))]

        layout_pairings.append(row)
        layout_pairings.append([sg.HorizontalSeparator()])



    ###  table for assigning BYES
    values = [['X', ' '*10+cand] for cand in candidate_byes]
    bye_table = sg.Table(values=values, 
                         headings=['', 'BYE(s)'], 
                         key='-TABLE BYE ASSIGNMENT-', 
                         size=(200, 7),
                         font=(font, 12),
                         pad=15,
                         select_mode=sg.TABLE_SELECT_MODE_NONE,
                         col_widths=[2, 25],
                         hide_vertical_scroll=True,
                         auto_size_columns=False,
                         enable_events=True,
                         enable_click_events=True,
                         justification='left',
                         expand_x=False,
                         expand_y=False)

    assign_bye_button = sg.ButtonMenu(button_text='Assign BYE', 
                                      font=(font, 14), 
                                      item_font=(font, 12), 
                                      text_color='white', 
                                      key='-BUTTONMENU ASSIGN BYE-', 
                                      menu_def=['junk', player_list])

    buttons = [sg.Button('Submit Pairing', border_width=2, font=(font, 16), key='-SUBMIT CUSTOM PAIRINGS-'), 
               sg.Button('Nominal Pairings', border_width=2, font=(font, 16), key='-NOMINAL PAIRINGS-'), 
               sg.Button('Clear All', border_width=2, font=(font, 16), key='-CLEAR ALL PAIRINGS-'), 
               sg.Button('Cancel', border_width=2, font=(font, 16), key='-CANCEL CUSTOM PAIRINGS-')]

    layout_edit_parings = [sg.Column(layout=layout_pairings, 
                                     size=(750, 590), 
                                     pad=0, 
                                     scrollable=True, 
                                     vertical_scroll_only=True, 
                                     sbar_width=1, 
                                     element_justification='center'), 
                           sg.Column(layout=[[assign_bye_button], 
                                             [bye_table]], 
                                          element_justification='center')
                           ]

    window_custom_pairings = sg.Window('Generate Custom Pairings for Round %i' % current_round, 
                                       [[buttons], [layout_edit_parings]], 
                                       location=(50, 0), 
                                       size=(1100, 670), 
                                       sbar_arrow_width=1,
                                       element_justification='center', 
                                       resizable=True, 
                                       modal=True)

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
            if p != 'remove player':
                junk = player_list.pop(player_list.index(p))

            ###  assigning chosen player to slot
            if p == 'remove player':
                window_custom_pairings[event].update(button_text=' ')
            else:
                window_custom_pairings[event].update(button_text=p)

            ###  updating buttonmenu options
            for k in values.keys():
                if 'BUTTONMENU TABLE' in k:
                    window_custom_pairings[k].update(menu_definition=['junk', ['remove player']+numpy.sort(player_list)[::-1].tolist()])
                elif 'BUTTONMENU ASSIGN BYE' in k:
                    window_custom_pairings[k].update(menu_definition=['junk', numpy.sort(player_list)[::-1].tolist()])

        ###  add player to BYE assignment table
        if (event == '-BUTTONMENU ASSIGN BYE-'):

            ###  removing chosen player from player_list
            p = values['-BUTTONMENU ASSIGN BYE-']
            if p != ' ':
                junk = player_list.pop(player_list.index(p))

            ###  adding to candidate_byes and updating BYE table
            candidate_byes.append(p)
            window_custom_pairings['-TABLE BYE ASSIGNMENT-'].update(values=[['X', ' '+cand] for cand in candidate_byes])

            ###  updating buttonmenu options
            for k in values.keys():
                if 'BUTTONMENU TABLE' in k:
                    window_custom_pairings[k].update(menu_definition=['junk', ['remove player']+numpy.sort(player_list)[::-1].tolist()])
                elif 'BUTTONMENU ASSIGN BYE' in k:
                    window_custom_pairings[k].update(menu_definition=['junk', numpy.sort(player_list)[::-1].tolist()])

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
                    window_custom_pairings[k].update(menu_definition=['junk', numpy.sort(player_list)[::-1].tolist()])

        ###  populate slots with the auto-generated pairings
        if (event == '-NOMINAL PAIRINGS-'):

            confirmation = sg.popup_yes_no('Populate fields with automated pairings?', 
                                           title='Retrieve Nominal Pairing', 
                                           font=(font, 14))

            if confirmation == 'No':
                continue


            ###  iterating over nominal table assignments
            i_table = 0
            str_pairings = []
            candidate_byes = []
            for idx_player1, idx_player2 in enumerate(nominal_pairings):

                ###  skip if this pair is already accounted for
                str1_pair = '%sv%s' % (idx_player1, idx_player2)
                str2_pair = '%sv%s' % (idx_player2, idx_player1)
                if (str1_pair in str_pairings) or (str2_pair in str_pairings):
                    continue

                if idx_player2 == 'BYE':
                    candidate_byes.append('%.1f   %s' % (participants.total_scores[idx_player1], participants.names[idx_player1]))
                else:
                    i_table += 1

                    window_custom_pairings['-BUTTONMENU TABLE%i PLAYER1-'%i_table].update(button_text='%.1f   %s' % (participants.total_scores[idx_player1], participants.names[idx_player1]))
                    window_custom_pairings['-BUTTONMENU TABLE%i PLAYER2-'%i_table].update(button_text='%.1f   %s' % (participants.total_scores[idx_player2], participants.names[idx_player2]))

                    ###  updating buttonmenu options
                    window_custom_pairings['-BUTTONMENU TABLE%i PLAYER1-'%i_table].update(menu_definition=['junk', ['remove player']])
                    window_custom_pairings['-BUTTONMENU TABLE%i PLAYER2-'%i_table].update(menu_definition=['junk', ['remove player']])


                str_pairings += [str1_pair, str2_pair]

            ###  populating BYE table
            window_custom_pairings['-TABLE BYE ASSIGNMENT-'].update(values=[['X', ' '*10+cand] for cand in candidate_byes])
            window_custom_pairings['-BUTTONMENU ASSIGN BYE-'].update(menu_definition=['junk', []])

            ###  depopulating player_list
            player_list = []

        ###  clear all current assignments
        if (event == '-CLEAR ALL PAIRINGS-'):

            confirmation = sg.popup_yes_no('Clear all current assignments?', 
                                           title='Clear Assignments', 
                                           font=(font, 14))

            if confirmation == 'No':
                continue

            ###  re-initializing player_list and candidate_byes
            candidate_byes = []
            player_list = ['%.1f   %s' % (row['Total'], row['Name']) for row in numpy.sort(table_info['struct_array'], order=['Total', 'Tie Break', 'Rating'])[::-1]]

            ###  removing names from buttonmenus and BYE table and updating options
            for k in values.keys():
                if 'BUTTONMENU TABLE' in k:
                    window_custom_pairings[k].update(button_text=' ', menu_definition=['junk', ['remove player']+player_list])
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

                sg.popup_no_titlebar(message, font=(font, 14))
                continue

            ###  recording pairings of players
            candidate_opponents = [None for i in range(participants.n_participants)]
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
                    idx_player = participants.names.tolist().index(player)
                    candidate_opponents[idx_player] = 'BYE'
                    candidate_pairings.append('%ivBYE'%idx_player)

                elif (player1 == ' '):
                    player = player2.split('   ')[1]
                    idx_player = participants.names.tolist().index(player)
                    candidate_opponents[idx_player] = 'BYE'
                    candidate_pairings.append('%ivBYE'%idx_player)

                ###  otherwise, both slots were filled
                else:
                    player1 = player1.split('   ')[1]
                    player2 = player2.split('   ')[1]
                    idx_player1 = participants.names.tolist().index(player1)
                    idx_player2 = participants.names.tolist().index(player2)
                    candidate_opponents[idx_player1] = idx_player2
                    candidate_opponents[idx_player2] = idx_player1
                    candidate_pairings.append('%iv%i'%(idx_player1, idx_player2))
                    candidate_pairings.append('%iv%i'%(idx_player2, idx_player1))

            ###  recording BYE assignments
            for player in candidate_byes:
                player = player.split('   ')[1]
                idx_player = participants.names.tolist().index(player)
                candidate_opponents[idx_player] = 'BYE'
                candidate_pairings.append('%ivBYE'%idx_player)

            ###  check if any given pairs occurred in a past round and warn user
            overlap = set(candidate_pairings).intersection(participants.all_prev_pairings)
            if len(overlap) > 0:

                message = 'WARNING\nThe following pairing(s) occurred in a previous round:\n'
                for pair in overlap:

                    opp1, opp2 = pair.split('v')
                    if opp1 == 'BYE':
                        message += '\n%s given BYE' % participants.names[int(opp2)]
                    elif opp2 == 'BYE':
                        message += '\n%s given BYE' % participants.names[int(opp1)]
                    else:
                        message += '\n%s vs. %s' % (participants.names[int(opp1)], participants.names[int(opp2)])

                message += '\n\nSubmit pairings anyway?'

            else:
                message = 'Ready to submit pairings?'


            confirmation = sg.popup_yes_no(message, 
                                           title='Submit Pairings', 
                                           font=(font, 14))

            ###  ready to return submitted pairings
            if confirmation == 'Yes':
                window_custom_pairings.close()
                return candidate_opponents


    window_custom_pairings.close()
