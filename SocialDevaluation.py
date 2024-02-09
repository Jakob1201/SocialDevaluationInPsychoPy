from psychopy import visual, data, gui, core, event, hardware, logging
import os, random, pandas as pd, numpy as np

#region - Eingabefenster
dlg = gui.Dlg(title="Experimentseinstellungen")
dlg.addField("Teilnehmer-ID:")
dlg.addField("Durchlauf-Nummer:")
dlg.addField("Vorname:")
dlg.show()

if dlg.OK == True:
    participant_id = dlg.data[0]
    run_number = dlg.data[1]
    vorname = dlg.data[2]
else:
    core.quit()
#endregion

#region - Initialisiere die Spieler
spieler_namen = {'spieler1': "Spieler 1",'spieler2': vorname, 'spieler3': "Spieler 3"}
spieler_accuracies = {spieler_namen[name]: [] for name in spieler_namen}
spieler_leistungen = {spieler_namen[name]: 0 for name in spieler_namen}
spieler_platzierungen = {spieler_namen[name]: 0 for name in spieler_namen}
proband = spieler_namen['spieler2']
vorherige_platzierung_sp2 = None # wird später in show_sorted_resulsts benötigt
#endregion

# Erstelle ein Fenster
win = visual.Window(size=(1536, 864), color=(0.75,0.75,0.75), fullscr=True)  # Use RGB tuple for gray color(0.75,0.75,0.75)
# setup fixation_cross
fix_cross = visual.TextStim(win=win, text="+", pos=[0,0], color='black', height = 0.4)

#region - Initialisiere die Parameter
num_trials_per_spieler = 4
num_spieler = len(spieler_namen) - 1 # Wieso denn nur 2 Spieler??
num_trials_gesamt = num_trials_per_spieler * num_spieler
num_trials_uebung = num_spieler * 1
trial_duration = 2.0  # 2000ms
dur_feedback = 4.0 # 4000ms
dur_hierarchie = 5.0 # 5000ms
picture_size = [0.6, 0.9]  # Adjust the size of the pictures as needed
spieler_pic_size = [0.25, 0.5]
sterne_size = [0.25, 0.1]
thumb_size = [0.2, 0.35]
background_color = [0.5, 0.5, 0.5]  # Background color as RGB tuple
# ein boolean 'scanner' ist verständlicher als setting 1 oder 2
scanner = False # oder eben True
if scanner:
    left_but = 'b'
    right_but = 'c'
else:
    left_but = 'left'
    right_but = 'right'
clock = core.Clock()
#endregion

#region - pictures
# relative path to picture files (in img subfolder)
picture_files_34 = ["img/34-dots-400x400.bmp"] + [f"img/34-dots-400x400({i}).bmp" for i in range(1,11)]
picture_files_36 = ["img/36-dots-400x400.bmp"] + [f"img/36-dots-400x400({i}).bmp" for i in range(1,11)]

last_left_picture = last_right_picture = None # wird später in get_rnd_picture benötigt

spieler_bildpfade = {
    spieler_namen['spieler1']: "img/Dummy5_blau.bmp",
    spieler_namen['spieler2']: "img/Dummy5_gruen.bmp",
    spieler_namen['spieler3']: "img/Dummy5_rot.bmp",
}

sterne_bildpfade = [
    "img/3sterne.bmp", 
    "img/2sterne.bmp", 
    "img/1stern.bmp"
]

thumbup_pfad = "img/thumbup.bmp"
thumbdown_pfad = "img/thumbdown.bmp"
#endregion

#region - Instruktionen Setup und Anzeige
instruktionsbilder = [
    "img/screenshot_initial.bmp",
    "img/screenshot_gegner.bmp",
    "img/screenshot_gegenueber.bmp",
    "img/screenshot_darstellung.bmp",
    "img/screenshot_hier_rel_up.bmp",
    "img/screenshot_hier_rel_dev.bmp",
    "img/screenshot_gleichI.bmp",
    "img/screenshot_missfeedback.bmp",
    "img/screenshot_abgestiegen.bmp",
    "img/screenshot_abgestiegen.bmp", #TODO: Warum zweimal? vlt soll's aufgestiegen sein?
                                        # screenshot_abgestiegen soll zweimal hintereinander mit unterschiedlichen instruktionstexten dargestellt werden.
]

instruktionstexte = [
    "Das Spiel spielen Sie zusammen mit zwei anderen Spielern. Über das gesamte Spiel wird entsprechend ihrer Leistung eine Rangreihe der Spieler gebildet.",
    "Jede Runde des Spiels beginnt, indem Ihnen der Spieler oder die Spielerin angezeigt wird, mit dem/der Sie die Runde absolvieren. Die Sterne unter dem Bild zeigen den Rang des Spielers an.",
    "Anschließend werden Sie dem/der anderen Spieler/-in gegenübergestellt. Spieler mit höheren Rängen werden links von Spielern mit niedrigeren Rängen dargestellt.",
    "Hier sehen Sie ein Beispiel dafür, wie später im Spiel die Punktewolken dargestellt werden. Wenn Sie später selbst das Spiel durchführen, müssten sie mithilfe der Tasten unter ihren Zeigefingern entscheiden, wo Sie mehr Punkte sehen.",
    "Es folgt eine Rückmeldung darüber, ob die Spieler richtig oder falsch geantwortet haben. Neben den Bildern der Spieler erscheint dementsprechend ein Daumen nach oben oder nach unten.",
    "<Richtig> oder <Falsch> bezieht sich dabei immer auf Ihre eigene Leistung.",
    "Beide Spieler können dasselbe Ergebnis erzielen.",
    "Wenn Sie nicht innerhalb von 3 Sekunden eine Antwort gegeben haben, wird Ihnen das zurückgemeldet. Wenn Sie zu oft nicht reagieren, wird das Spiel abgebrochen.",
    "In regelmäßigen Abständen wird die Platzierung der Spieler abhängig von Ihrer Leistung dargestellt. Spieler mit höherem Rang haben mehr Sterne und werden weiter links dargestellt.",
    "In den folgenden Übungsrunden gibt es noch keine Platzierungen. Daher werden keine Sterne angezeigt.Ihre Leistung in den Übungsrunden legt aber fest, mit welcher Platzierung sie das Spiel beginnen.\n\nHaben Sie alles verstanden? Wenn nicht, blättern Sie bitte zurück und lesen Sie erneut.",
]

# Initialisiere Text- und Bildstimuli für den Anweisungstext und -bilder
instruktion_text = visual.TextStim(win=win, pos=[0,-0.6], color = (-1,-1,-1), wrapWidth = 1.9)
instruktions_bild = visual.ImageStim(win=win, pos=[0,0.25], size=(1,1))

visual.TextStim(win=win, 
    text="Vielen Dank für ihre Teilnahme!\n\nIm Folgenden soll Ihnen anhand von Beispielbildern erklärt werden, wie das Spiel funktioniert.\n\nIn den Beispielen sind fiktive Spieler dargestellt und eine Aufgabe, die Sie nicht bearbeiten müssen.\nSie können durch diese Erklärungen vor und zurückblättern, bis Sie sie gut verstanden haben.\nDrücken Sie eine der Tasten unter ihren Zeigefingern um fortzufahren.",
    color = (-1,-1,-1), 
    wrapWidth = 1.8
).draw()
win.flip()
if 'q' in event.waitKeys(keyList=[left_but, right_but, "q"]): 
    win.close()
    core.quit()  

current_slide = 0  # Index des aktuellen Bildes
while current_slide < len(instruktionsbilder):
    instruktions_bild.image = instruktionsbilder[current_slide]
    instruktion_text.text = instruktionstexte[current_slide]
    instruktions_bild.draw()
    instruktion_text.draw()
    if current_slide < len(instruktionsbilder)-1:
        visual.TextStim(win=win, text="Weiter mit der rechten Taste ->", pos=[0.75,0.2],color=(0,0,5,1), height = 0.06).draw()
    else:
        visual.TextStim(win=win, text="Weiter zu den Übungsrunden ->", pos=[0.75,0.2],color=(0,0,5,1), height = 0.06).draw()
    if current_slide > 0:
        visual.TextStim(win=win, text="<- Zurück mit der linken Taste", pos=[-0.75,0.2],color=(0,0,5,1), height = 0.06).draw()
    win.flip()

    keys = event.waitKeys(keyList=[left_but, right_but, "q"])

    if left_but in keys and current_slide > 0:
        current_slide -= 1
    elif right_but in keys and current_slide <= len(instruktionsbilder) - 1:
        current_slide += 1
    elif "q" in keys:
        win.close()
        core.quit()
#endregion

#region - output filenames and function to save data about trials
date = data.getDateStr()
data_path = "trial_data/"
filename_trial_data = os.path.join(data_path, f"{date}_{participant_id}_{run_number}_trial_data.csv")

trial_data = []

def save_data(time=None, event='', opponent='', op_hier='', left_picture='', right_picture='', missing='', response_sp2='', accuracy_sp2='', accuracy_op='', Hier_rel='', Rank='', Rank_change=''):
    if time is None:
        time = clock.getTime()
    dict = {
        'Proband_in' : participant_id,
        'Date' : date,
        'Time' : time, 
        'Event' : event,
        'round_no' : spieler_index+1,
        'Opponent' : opponent,
        'Op_Hier' : op_hier,
        'linkesBild' : ((left_picture.replace('img/','')).replace('-dots-400x400','')).replace('.bmp',''), 
        'rechtesBild' : ((right_picture.replace('img/','')).replace('-dots-400x400','')).replace('.bmp',''), 
        'check_missing' : missing,
        'response_sp2' : response_sp2,
        'accuracy_sp2' : accuracy_sp2, 
        'accuracy_op' : accuracy_op,
        'Hier.rel' : Hier_rel,
        'Rank' : Rank, 
        'Rank_change' : Rank_change
    }
    trial_data.append(dict)
#endregion

#region - function definitions
event.globalKeys.clear()
event.globalKeys.add(key='s', func=save_data, func_kwargs=dict(event='pulse'), name = 'scannerpulse')

def check_q(acceptKeys):
    clock = core.Clock()
    key = event.waitKeys(keyList=acceptKeys, timeStamped=clock)
    if key:
        time = key [0][1]
    if "q" in key:
        win.close()
        core.quit()

def get_rnd_picture():
    global last_left_picture, last_right_picture

    if random.choice([True, False]): # Zufällige Auswahl aus den möglichen Bildern und zufällige Wahl der Position
        left_picture = random.choice([pic for pic in picture_files_34 if pic != last_left_picture])
        right_picture = random.choice([pic for pic in picture_files_36 if pic != last_right_picture])
    else:
        left_picture = random.choice([pic for pic in picture_files_36 if pic != last_right_picture])
        right_picture = random.choice([pic for pic in picture_files_34 if pic != last_left_picture])
    #Setzen der "last pictures" für den nächsten Durchgang
    last_left_picture = left_picture
    last_right_picture = right_picture

    return left_picture, right_picture

def get_and_show_stimuli(trial_run=False):
    
    #Mitspieler festlegen # Vorlage für conditionals der Sterne und Positionen siehe Editordatei "Sterne und Positionszuordnung"  
    opponent = spieler_namen['spieler1'] if spieler_index % 2 == 0 else spieler_namen['spieler3']
    opponent_pic = spieler_bildpfade[opponent]
    opponent_stars = sterne_bildpfade[spieler_platzierungen[opponent]]
    # using the global variable proband
    proband_pic = spieler_bildpfade[proband]
    proband_stars = sterne_bildpfade[spieler_platzierungen[proband]]
    # are we in the trial run or the real experiment
    condition = spieler_index % 2 == 0 if trial_run else spieler_platzierungen[proband] > spieler_platzierungen[opponent]

    if condition: 
        op_hier = 1 # für die Output-Datei
        right_name = proband
        right_spieler_pic = proband_pic
        right_stars = proband_stars
        left_name = opponent
        left_spieler_pic = opponent_pic
        left_stars = opponent_stars
    else: 
        op_hier = 0 # für die Output-Datei
        right_name = opponent
        right_spieler_pic = opponent_pic
        right_stars = opponent_stars
        left_name = proband
        left_spieler_pic = proband_pic
        left_stars = proband_stars

    # Stimuli erstellen 
    opponent_text_stim = visual.TextStim(win=win,text=f"Sie spielen mit {opponent}",color = (-1,-1,-1), pos=[0,0.5])
    opponent_pic_stim = visual.ImageStim(win=win,image=opponent_pic,size=spieler_pic_size,pos=[0,0])
    opponent_stars_stim = visual.ImageStim(win=win,image=opponent_stars,size=sterne_size,pos=[0,-0.205])
    
    left_stimulus = visual.ImageStim(win=win,image=left_picture,size=picture_size,pos=[-0.4, -0.3])  # Position auf der linken Seite
    right_stimulus = visual.ImageStim(win=win,image=right_picture,size=picture_size,pos=[0.4, -0.3])  # Position auf der rechten Seite
    
    left_spieler_stim = visual.ImageStim(win=win,image=left_spieler_pic,size = spieler_pic_size,pos=[-0.4, 0.48])
    right_spieler_stim = visual.ImageStim(win=win,image=right_spieler_pic,size = spieler_pic_size,pos=[0.4, 0.48])
        
    left_name_stim = visual.TextStim(win=win,text=left_name,color = (-1,-1,-1), pos=[-0.4, 0.8])
    right_name_stim = visual.TextStim(win=win,text=right_name,color = (-1,-1,-1),pos=[0.4, 0.8])

    left_sterne_stim = visual.ImageStim(win=win,image=left_stars,size=sterne_size,pos=[-0.4, 0.275])
    right_sterne_stim = visual.ImageStim(win=win,image=right_stars,size=sterne_size,pos=[0.4, 0.275])

    # Präsentiere die Bilder
    time_ev1 = clock.getTime()
    for frame in range(int(1.5 * 60)):  # 60 Hz Bildwiederholfrequenz
        opponent_text_stim.draw()
        opponent_pic_stim.draw()
        if not trial_run: opponent_stars_stim.draw()
        win.flip()
    
    for frame in range(int(1.5 * 60)):
        left_spieler_stim.draw()
        right_spieler_stim.draw()
        if not trial_run: right_sterne_stim.draw(); left_sterne_stim.draw()
        left_name_stim.draw()
        right_name_stim.draw()
        win.flip()
    
    for frame in range(int(trial_duration * 60)):  # 60 Hz Bildwiederholfrequenz
        left_stimulus.draw()
        right_stimulus.draw()
        left_spieler_stim.draw()
        right_spieler_stim.draw()
        if not trial_run: right_sterne_stim.draw(); left_sterne_stim.draw()
        left_name_stim.draw()
        right_name_stim.draw()
        win.flip()

    stimuli = {
        'left_name_stim' : left_name_stim,
        'left_spieler_stim' : left_spieler_stim,
        'left_sterne_stim' : left_sterne_stim,
        'right_name_stim' : right_name_stim,
        'right_spieler_stim' : right_spieler_stim,
        'right_sterne_stim' : right_sterne_stim
    }
    return time_ev1, opponent, op_hier, left_name, stimuli
    
def get_and_show_feedback(trial_run=False):
    #clock = core.Clock()
    #response_spieler2 = event.getKeys(keyList=[left_but, right_but, 'q'], timeStamped = clock)
    response_spieler2 = event.getKeys(keyList=[left_but, right_but, 'q'])
    if response_spieler2:
        #time = response_spieler2[0][1]
        dir = response_spieler2[0] # prüfe nur den ersten gedrückten Key
        return_response = dir
        if (dir == right_but and right_picture in picture_files_36) or (dir == left_but and left_picture in picture_files_36):
            accuracy_sp2 = 1  # Correct response
            missing = 0
            feedback_text = "Richtig!"
            feedback_color = (0, 1, 0)
        else:
            accuracy_sp2 = 0  # Incorrect response
            missing = 0
            feedback_text = "Falsch!"
            feedback_color = (1, 0, 0)
    else:
        accuracy_sp2 = 0  # No response #-1??
        missing = 1
        feedback_text = "Zu langsam!"
        return_response = feedback_text
        feedback_color = (1, 0, 0)
    # Überprüfe die 'q'-Taste, um das Experiment zu beenden
    if 'q' in response_spieler2:
        win.close()
        core.quit()  # Beendet das Experiment

    feedback_text_stim = visual.TextStim(win=win,text = feedback_text,color = feedback_color,pos = [0,-0.2])

    # Gegenspieler
    wuerfel_op = random.randint(1, 100)
    threshold = 81 if spieler_index % 2 == 0 else 41
    accuracy_op = 1 if wuerfel_op < threshold else 0

    # Daumenstimuli zuordnen
    condition = spieler_index % 2 == 0 if trial_run else left_name == opponent
    if condition: # proband rechts
        right_thumb = thumbup_pfad if accuracy_sp2 == 1 else thumbdown_pfad
        left_thumb = thumbup_pfad if accuracy_op == 1 else thumbdown_pfad
    else: #proband links
        left_thumb = thumbup_pfad if accuracy_sp2 == 1 else thumbdown_pfad
        right_thumb = thumbup_pfad if accuracy_op == 1 else thumbdown_pfad
    
    left_thumb_stim = visual.ImageStim(win=win,image = left_thumb,size = thumb_size,pos = [-0.7, 0.48])
    right_thumb_stim = visual.ImageStim(win=win,image= right_thumb,size = thumb_size,pos = [0.7, 0.48])
        
    # Zeige den Feedback-Bildschirm für eine kurze Dauer an (z. B. 1 Sekunde)
    time_ev2 = clock.getTime()
    for frame in range(int(dur_feedback * 60)):  # 60 Hz Bildwiederholfrequenz für 1,5 Sekunde
        feedback_text_stim.draw()
        left_thumb_stim.draw()
        right_thumb_stim.draw()
        stimuli['left_spieler_stim'].draw()
        stimuli['right_spieler_stim'].draw()
        stimuli['left_name_stim'].draw()
        stimuli['right_name_stim'].draw()
        if not trial_run: stimuli['right_sterne_stim'].draw(); stimuli['left_sterne_stim'].draw()
        win.flip()

    return time_ev2, return_response, missing, accuracy_sp2, accuracy_op

def get_sorted_results(round_number):
    # Aktualisiere die Leistungen
    # ist es absicht, dass bei spieler2 der Faktor 2 fehlt? # Ja, das ist absicht. spieler 2 spielt ja doppelt so viele Runden wie die die anderen Spieler.
    spieler_leistungen[spieler_namen['spieler1']] = round((sum(spieler_accuracies[spieler_namen['spieler1']])*2)/int(round_number)*100,2)
    spieler_leistungen[spieler_namen['spieler2']] = round((sum(spieler_accuracies[spieler_namen['spieler2']]))/int(round_number)*100,2)
    spieler_leistungen[spieler_namen['spieler3']] = round((sum(spieler_accuracies[spieler_namen['spieler3']])*2)/int(round_number)*100,2)
    # Sortiere die Spieler nach ihrer Leistung absteigend
    return sorted(spieler_leistungen.items(), key=lambda x: x[1], reverse=True)

def show_sorted_resulsts(trial_run=False):
    global vorherige_platzierung_sp2 #, vergleichs_variable

    first_name, first_leistung = sortierte_spieler[0]
    second_name, second_leistung = sortierte_spieler[1]
    third_name, third_leistung = sortierte_spieler[2]
    # Platzierungs-Dictionary füllen
    for index, (spieler, leistung) in enumerate(sortierte_spieler):
        spieler_platzierungen[spieler] = index

    platzierung_sp2 = spieler_platzierungen[proband]
    vergleichs_variable = ''
    if not trial_run:
        aktuelle_platzierung_sp2 = platzierung_sp2
        if vorherige_platzierung_sp2 is not None:
            if aktuelle_platzierung_sp2 < vorherige_platzierung_sp2:
                vergleichs_variable = "Aufgestiegen" # In der Output-Datei nutzen
            elif aktuelle_platzierung_sp2 > vorherige_platzierung_sp2:
                vergleichs_variable = "Abgestiegen" # In der Output-Datei nutzen

        vorherige_platzierung_sp2 = aktuelle_platzierung_sp2
        vergleichs_stim = visual.TextStim(win=win, text=vergleichs_variable, color = (-1,-1,-1), pos=[-0.6, -0.6])
    
    first_name_stim = visual.TextStim(win=win,text = first_name, color = (-1,-1,-1), pos=[-0.6,0.83])
    first_picture_stim = visual.ImageStim(win=win, image= spieler_bildpfade[first_name], size= spieler_pic_size, pos=[-0.6, 0.5])
    first_stars_stim = visual.ImageStim(win=win, image= sterne_bildpfade[0], size= sterne_size, pos=[-0.6, 0.3])
    first_leistung_stim = visual.TextStim(win=win,text = f"{first_leistung}%", color = (-1,-1,-1), pos=[-0.6,0.2])
    
    second_name_stim = visual.TextStim(win=win,text = second_name, color = (-1,-1,-1), pos=[0,0.33])
    second_picture_stim = visual.ImageStim(win=win, image= spieler_bildpfade[second_name], size= spieler_pic_size, pos=[0, 0])
    second_stars_stim = visual.ImageStim(win=win, image= sterne_bildpfade[1], size= sterne_size, pos=[0, -0.2])
    second_leistung_stim = visual.TextStim(win=win,text = f"{second_leistung}%", color = (-1,-1,-1), pos=[0,-0.3])
    
    third_name_stim = visual.TextStim(win=win,text = third_name, color = (-1,-1,-1), pos=[0.6,-0.17])
    third_picture_stim = visual.ImageStim(win=win, image= spieler_bildpfade[third_name], size= spieler_pic_size, pos=[0.6, -0.5])
    third_stars_stim = visual.ImageStim(win=win, image= sterne_bildpfade[2], size= sterne_size, pos=[0.6, -0.7])
    third_leistung_stim = visual.TextStim(win=win,text = f"{third_leistung}%", color = (-1,-1,-1), pos=[0.6,-0.8])
    
    time_ev3 = clock.getTime()
    for frame in range(int(dur_hierarchie * 60)):  # 60 Hz Bildwiederholfrequenz für 5 Sekunde
        first_name_stim.draw()
        first_picture_stim.draw()
        first_stars_stim.draw()
        first_leistung_stim.draw()
        second_name_stim.draw()
        second_picture_stim.draw()
        second_stars_stim.draw()
        second_leistung_stim.draw()
        third_name_stim.draw()
        third_picture_stim.draw()
        third_stars_stim.draw()
        third_leistung_stim.draw()
        if not trial_run: vergleichs_stim.draw()
        win.flip()
    return time_ev3, platzierung_sp2, vergleichs_variable
#endregion - function definitions

#region - Übungsrunden
visual.TextStim(win=win, text="Wenn Sie bereit sind in die Übungsrunden zu starten, drücken Sie eine der Tasten unter ihren Fingern.",color = (-1,-1,-1)).draw()
win.flip()
check_q([left_but, right_but, "q"])

for frame in range(int(5 * 60)):  # 60 Hz Bildwiederholfrequenz für 15 Sekunden
        fix_cross.draw()
        win.flip()

print('BEGINN der Übungsrunden ...')
for spieler_index in range(num_trials_uebung):
    print(f"beginne Übungsrunde {spieler_index+1} von {num_trials_uebung}")
    left_picture, right_picture = get_rnd_picture()
    time_ev1, opponent, op_hier, left_name, stimuli = get_and_show_stimuli(True) # arg = True, weil wir in den Übungsrunden sind
    time_ev2, response_spieler2, missing, accuracy_sp2, accuracy_op = get_and_show_feedback(True)

    spieler_accuracies[proband].append(accuracy_sp2)
    spieler_accuracies[opponent].append(accuracy_op)
    print(f"\taccuracis vom Probanden: {spieler_accuracies[proband]}")
    print(f"\taccuracis vom Computer ({opponent}): {spieler_accuracies[opponent]}")

visual.TextStim(win=win, text="Die Übungsrunden sind abgeschlossen.\n Drücken Sie eine beliebige Taste um sich die Rangreihe anzeigen zu lassen.", color = (-1,-1,-1)).draw()
win.flip()
check_q([left_but, right_but, "q"])

# Sortiere die Spieler nach ihrer Leistung absteigend
sortierte_spieler = get_sorted_results(num_trials_uebung)
print(f"sortierte Spieler: {sortierte_spieler}")
time_ev3, platzierung_sp2, vergleichs_variable = show_sorted_resulsts(True)
# save_data erwartet, dass es die Variable spieler_index gibt. Außerhalb des Loops gibt's sie aber nicht, also setzen wir sie hier explizit
spieler_index = -1 # -> in save_data wird +1 gerechnet, sodass die Übungsrunden jetzt als Runde 0 in der Output Datei steht
save_data(time = time_ev3,event = 'rank_feedback_uebungsrunden', Rank = platzierung_sp2, Rank_change = vergleichs_variable)
vorherige_platzierung_sp2 = platzierung_sp2
#check_q([left_but, right_but, "q"])
print('ENDE der Übungsrunden ...')
save_data(time = clock.getTime(), event='Ende Übungsrunden, warten auf Scanner')
#endregion - Übungsrunden
            
#region - richtiges Experiment
visual.TextStim(win=win,text=f"Nun beginnt das eigentliche Spiel.\n\n Warten Sie bitte bis der Versuchleiter das Spiel startet.",color = (-1,-1,-1)).draw()
win.flip()
check_q(['space', 'q']) # Warten Sie auf die Leertaste, um das Experiment zu starten

# Auf den ersten Puls des Scanners warten
visual.TextStim(win=win,text=f"Warten auf Signal des Scanners...",color=(-1,-1,-1)).draw()
win.flip()
core.wait(1)
#hardware.emulator.launchScan(win=win, TR=2, volumes=200, sync='s',globalClock=True, simResponses=True, mode='Test')# 
#event.waitKeys(keyList=['s'])#auf den ersten puls des scanners warten. Der Puls wird von der Stimulus Box als 's' weitergeleitet.
pulse_counter = 0
while pulse_counter < 5:
    pulse = event.waitKeys(keyList=['s'])
    if pulse:
        pulse_counter+=1


# Accuracies und Leistungen neu initialisieren
spieler_leistungen = {spieler_namen[name]: 0 for name in spieler_namen}
spieler_accuracies = {spieler_namen[name]: [] for name in spieler_namen}

clock.reset()
# Beginn der Trials
print('BEGINN des richtigen Experiments ...')
save_data(time = clock.getTime(), event='Beginn des richtigen Experiments')
for spieler_index in range(num_trials_gesamt):
    print(f"beginne Trial {spieler_index+1} von {num_trials_gesamt}...")
    left_picture, right_picture = get_rnd_picture()
    time_ev1, opponent, op_hier, left_name, stimuli = get_and_show_stimuli() # kein argument benötigt, da per Default die Stimuli des richtigen Experiments gezeigt werden
    save_data(time = time_ev1, event = 'gegenueberstellung',opponent = opponent, op_hier = op_hier, left_picture = left_picture, right_picture = right_picture)
    time_ev2, response_spieler2, missing, accuracy_sp2, accuracy_op = get_and_show_feedback()
    save_data(time = time_ev2,event = 'trial_feedback', missing = missing, response_sp2 = response_spieler2, accuracy_sp2 = accuracy_sp2, accuracy_op = accuracy_op, Hier_rel = str(op_hier)+str(accuracy_sp2)+str(accuracy_op))
    
    # Füge die Antwort und die Genauigkeit zur Liste der Spieler hinzu
    spieler_accuracies[proband].append(accuracy_sp2)
    spieler_accuracies[opponent].append(accuracy_op)
    print(f"\taccuracis vom Probanden: {spieler_accuracies[proband]}")
    print(f"\taccuracis vom Computer ({opponent}): {spieler_accuracies[opponent]}")

    # Nach jeder vierten Runde oder wenn alle Runden abgeschlossen sind, zeige die Rangfolge der Spieler an
    if (spieler_index+1) % 4 == 0 or spieler_index == num_trials_gesamt - 1:#  == num_trials_gesamt - 1: # Der spieler_index startet bei 0, sodass er nach 10 trials bei 9 (num_trials_gesamt - 1) steht.
        sortierte_spieler = get_sorted_results(spieler_index+1)
        print(f"\tsortierte Spieler: {sortierte_spieler}")
        time_ev3, platzierung_sp2, vergleichs_variable = show_sorted_resulsts()
        save_data(time = time_ev3,event = 'rank_feedback',Rank = platzierung_sp2, Rank_change = vergleichs_variable)

print('ENDE des richtigen Experiments ...')

for frame in range(int(15 * 60)):  # 60 Hz Bildwiederholfrequenz für 15 Sekunden
        fix_cross.draw()
        win.flip()

wartungs_text = visual.TextStim(win=win,text="Vielen Dank für ihre Teilnahme! \n\n Bitte warten Sie, bis der Versuchsleiter das Spiel beendet.",color = (-1,-1,-1))
wartungs_text.draw()
win.flip()

# Save data
#trials.saveAsWideText(filename_exp_data, delim=',', appendFile=False, fileCollisionMethod='overwrite')
df = pd.DataFrame(trial_data)
df.to_csv(filename_trial_data)

event.waitKeys(keyList=['q']) # Beende das Experiment mit q
win.close()
core.quit()
#endregion - richtiges Experiment