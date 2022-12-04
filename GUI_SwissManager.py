import os
import PySimpleGUI as sg

from ParticipantRoster import ParticipantRoster


PARTICIPANTS = ParticipantRoster()

file_participants = 'registrant_list.csv'
if os.path.exists(file_participants):
    with open(file_participants, 'r') as fopen:
        for line in fopen.readlines():
            name, rating = line.strip('\n').split(',')
            if name.lower() == 'name':
                continue

            PARTICIPANTS.add_participant(name, int(rating))


sg.theme('DarkGrey15')
FONT = 'bitstream charter'
dx, dy = 25, 2





row_add_player = [sg.Frame(title='', 
                           size=(1000, 80), 
                           border_width=3, 
                           layout=[[sg.Frame(title='', 
                                             border_width=0, 
                                             layout=[[sg.Text('', font=(FONT, 12))],
                                                     [sg.Button('Add', size=(3, 1), border_width=2, font=(FONT, 12), key='-ADD NEW PLAYER-')]]), 
                                    sg.Frame(title='', 
                                             border_width=0, 
                                             layout=[[sg.Text('Name', font=(FONT, 14))], 
                                                     [sg.InputText(size=(25, 3), border_width=2, font=(FONT, 14), key='-NEW PLAYER NAME-')]]), 
                                    sg.Frame(title='', 
                                             border_width=0, 
                                             layout=[[sg.Text('Rating', font=(FONT, 14))], 
                                                     [sg.InputText(size=(6, 3), border_width=2, font=(FONT, 14), key='-NEW PLAYER RATING-')]])
                                     ]])]

right_click_menu = ['', ['edit player', 'remove player', 'do nothing']]

registration_table = sg.Table(values=PARTICIPANTS.get_roster_list(integer_rating=True), 
                              headings=['', 'Name', 'Rating'], 
                              size=(900, 250),
                              font=(FONT, 12),
                              col_widths=[3, 20, 6],
                              auto_size_columns=False,
                              justification='center',
                              key='-TABLE-',
                              enable_events=True,
                              enable_click_events=True,
                              right_click_selects=True,
                              right_click_menu=right_click_menu,
                              expand_x=False,
                              expand_y=False)


layout = [[row_add_player], 
          [registration_table]
          ]






window = sg.Window('Swiss Tournament Manager', 
                   layout, 
                   location=(50, 0),
                   size=(500, 670), 
                   resizable=True)


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

    event, values = popup.read()

    popup.close()
    if event == '-SUBMIT-':
        return (values['-EDIT PLAYER NAME-'], int(values['-EDIT PLAYER RATING-']))
    elif event == '-CANCEL-':
        return (current_name, current_rating)



while True:

    event, values = window.read()
    print('\n')
    print('THE EVENT IS:  ', event)
    if values is not None:
        for i, (k, v) in enumerate(values.items()):
            if i == 0:
                print('THE VALUES:    "%s":' % k, v)
            else:
                print('               "%s":' % k, v)


    if event == sg.WIN_CLOSED:
        break

    elif event == '-MAXIMIZE-':
        window.maximize()

    elif event == '-ADD NEW PLAYER-':

        ###  only run if info entered
        if (values['-NEW PLAYER NAME-'] != '') and (values['-NEW PLAYER RATING-'] != ''): 

            try:
                name = values['-NEW PLAYER NAME-']
                rating = int(values['-NEW PLAYER RATING-'])
                PARTICIPANTS.add_participant(name, rating)

                window['-TABLE-'].update(values=PARTICIPANTS.get_roster_list(integer_rating=True))

                ###  clearing input prompts
                junk = window['-NEW PLAYER NAME-'].update(value='')
                junk = window['-NEW PLAYER RATING-'].update(value='')

            except:
                sg.popup('Error Parsing Inputs', font=(FONT, 16))


    ###  edit a player
    elif (event == 'edit player') and (len(values['-TABLE-']) == 1):

        idx_player = values['-TABLE-'][0]
        new_name, new_rating = popupEditPlayer(PARTICIPANTS.names[idx_player], PARTICIPANTS.ratings[idx_player])

        PARTICIPANTS.remove_participant(idx_player)
        PARTICIPANTS.add_participant(new_name, int(new_rating))
        window['-TABLE-'].update(values=PARTICIPANTS.get_roster_list(integer_rating=True))


    ###  remove a player
    elif (event == 'remove player') and (len(values['-TABLE-']) == 1):

        idx_player = values['-TABLE-'][0]
        confirmation = sg.popup_yes_no('Want to remove %s ?' % PARTICIPANTS.names[idx_player], 
                                       title='Remove Player', 
                                       font=(FONT, 14))

        if confirmation == 'Yes':
            PARTICIPANTS.remove_participant(idx_player)
            window['-TABLE-'].update(values=PARTICIPANTS.get_roster_list(integer_rating=True))



window.close()
