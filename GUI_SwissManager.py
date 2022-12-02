import PySimpleGUI as sg

from ParticipantRoster import ParticipantRoster


PARTICIPANTS = ParticipantRoster()

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


layout = [[row_add_player], 

          [sg.Button('Maximize', font=(FONT, 14), key='-MAXIMIZE-'), 
           sg.Button('Close', font=(FONT, 14), key='-CLOSE-')], 

          [sg.Column(layout=[[]], 
                     key='Player Table', 
                     size=(450, 300), 
                     scrollable=True,
                     vertical_scroll_only=True)]

           ]






window = sg.Window('My Cool Title', 
                   layout, 
                   size=(1100, 600), 
                   resizable=True)


while True:

    event, values = window.read()
    print('\n')
    print(event)
    print(values)

    if event == sg.WIN_CLOSED or event == '-CLOSE-':
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

                window.extend_layout(window['Player Table'], [[sg.Button('X'), sg.Text('Clicked Enter')],
                                                              [sg.Button('X'), sg.Text('Clicked Enter')],
                                                              [sg.Button('X'), sg.Text('Clicked Enter')],
                                                              [sg.Button('X'), sg.Text('Clicked Enter')],
                                                              [sg.Button('X'), sg.Text('Clicked Enter')]])

                window['Player Table'].contents_changed()
                junk = window['-NEW PLAYER NAME-'].update(value='')
                junk = window['-NEW PLAYER RATING-'].update(value='')

            except:
                sg.popup('Error Parsing Inputs', font=(FONT, 16))




window.close()