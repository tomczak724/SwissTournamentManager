import os
import time
import numpy
import itertools
import PySimpleGUI as sg

import Popups

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


def save_tournament_results_csv():

    ###  extracting results
    table_headings = ['seed', 'name', 'rating']
    table_fields = [('seed', 'U50'), ('name', 'U50'), ('rating', 'f')]
    table_values = PARTICIPANTS.get_roster_list(integer_rating=True)

    for idx in PARTICIPANTS.idx:

        for i_round in range(len(PARTICIPANTS.all_round_scores)):

            if idx == 0:
                table_headings += ['opponent_%i'%(i_round+1), 'score_%i'%(i_round+1)]
                table_fields += [('opponent_%i'%(i_round+1), 'i'), ('score_%i'%(i_round+1), 'f')]
            table_values[idx] += [PARTICIPANTS.opponents[i_round][idx], PARTICIPANTS.all_round_scores[i_round][idx]]

        if idx == 0:
            table_headings += ['total', 'tie_break']
            table_fields += [('total', 'f'), ('tie_break', 'f')]

        table_values[idx] += [PARTICIPANTS.total_scores[idx]]
        table_values[idx] += [PARTICIPANTS.tie_break_scores[idx]]

    ###  converting table_values to a structured array
    table_values_struc = numpy.array([tuple(row) for row in table_values], dtype=table_fields)


    ###  file name to store tournament results
    ctime = time.localtime()
    fname_results = 'TOURNAMENT_RESULTS__'
    fname_results += '%4i-%02i-%02i.csv' % (ctime.tm_year, ctime.tm_mon, ctime.tm_mday)

    ###  writing to file
    with open(fname_results, 'w') as fopen:

        ###  writing column names
        fopen.write(','.join(table_headings))
        fopen.write('\n')

        ###  writing a row for each participant
        for row in numpy.sort(table_values_struc, order=['total', 'tie_break', 'rating'])[::-1]:
            row_str = [str(val) for val in row]
            fopen.write(','.join(row_str))
            fopen.write('\n')





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

    ###  clear roster
    elif (CURRENT_ROUND == 0) and (event == '-CLEAR ROSTER-'):

        confirmation = sg.popup_yes_no('Clear entire roster ?', 
                                       title='Clear Roster', 
                                       font=(FONT, 16))

        if confirmation != 'Yes':
            continue

        ###  removing all participants
        for idx in PARTICIPANTS.idx:
            PARTICIPANTS.remove_participant(0)

        window['-REGISTRATION TABLE-'].update(values=PARTICIPANTS.get_roster_list(integer_rating=True))
        window.refresh()

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
        new_name, new_rating = Popups.popupEditPlayer(PARTICIPANTS.names[idx_player], PARTICIPANTS.ratings[idx_player])

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
        Popups.popupStandings(PARTICIPANTS)

    ###  prompt to edit round pairings
    elif ('CUSTOM PAIRINGS' in event):

        custom_opponents = Popups.popupCustomPairings(PARTICIPANTS, CURRENT_ROUND)

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
        score1, score2 = Popups.popupEnterScores(name1, name2)

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

        ###  logging scores from finished round and prepping for next
        PARTICIPANTS.total_scores += PARTICIPANTS.current_round_scores
        PARTICIPANTS.all_round_scores.append(PARTICIPANTS.current_round_scores.tolist())
        PARTICIPANTS.current_round_scores = numpy.array([numpy.nan]*PARTICIPANTS.n_participants)
        PARTICIPANTS.calc_tie_break_scores()

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

        ###  check that all scores have been entered
        ###  if not then ask to discard current round
        if numpy.isnan(PARTICIPANTS.current_round_scores).any():

            confirmation = sg.popup_yes_no('Round not finished\nDiscard current round and end tournament ?', 
                                           title='End Tournament ?', 
                                           font=(FONT, 18))

            if confirmation != 'Yes':
                continue

        else:

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
            PARTICIPANTS.calc_tie_break_scores()

            ###  saving tournament results to csv
            save_tournament_results_csv()

        ###  closing main window and opening standings window
        window.close()
        Popups.popupStandings(PARTICIPANTS)


window.close()
