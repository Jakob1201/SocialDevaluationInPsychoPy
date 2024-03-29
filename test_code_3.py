## To Dos:
    # Es muss eine Outputdatei geben, in der die Zeiten aller Events (Responses, Accuracy,Feedback-Bildschirme, Aufstieg, Abstieg, Scannerpulse) erfasst werden
        # Siehe: C:/Privat/Forschung/Forschungsabteilung/Social Devaluation/PsychoPy Experimente/Outputdatei_Versuch/
    # Den fMRI-emulator einarbeiten
    # Fixationskreuze einarbeiten nach jeder Runde
    # Regelmäßig (nach jedem Rangreihen-Feedback) auf den Puls des Scanners warten
    # ggf. feedback und Leistungsmechanismus verändern: statt "richtig" und "falsch" eher "besser / schlechter / gleich"
    
## Erledigt:
    # Vor Start des Experiments soll ein Fenster erscheinen, in dem z.B. Patienten-ID und Datum erfasst werden sollen
    # Instructions-Screens und Übungsrunden
        #siehe C:/Privat/Forschung/Forschungsabteilung/Social Devaluation/PsychoPy Experimente/SocDev/screenshots_code.py
    # Den Rangreihenbildschirm verändern (siehe Übungsrunden)
    # Darstellung der Hierarchie (Sterne und Positionen) in den Runden dynamisch anpassen
    # Auf- und Abstiegsmechanismen einführen

from psychopy import visual, gui, core, event, hardware, logging
import random
import pandas as pd
import numpy as np

# Zeige ein Eingabefenster an
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
    
# Initialisiere die Spieler
spieler_namen = {'spieler1': "Spieler 1",'spieler2': vorname, 'spieler3': "Spieler 3"}
spieler_accuracies = {spieler_namen[name]: [] for name in spieler_namen}
spieler_leistungen = {spieler_namen[name]: 0 for name in spieler_namen}
spieler_platzierungen = {spieler_namen[name]: 0 for name in spieler_namen}

# Erstelle ein Fenster
win = visual.Window(size=(1536, 864), color=(0.75,0.75,0.75), fullscr=True)  # Use RGB tuple for gray color(0.75,0.75,0.75)

# Initialisiere die Parameter
num_trials_per_spieler = 10
num_spieler = len(spieler_namen) - 1
num_trials_gesamt = num_trials_per_spieler * num_spieler
num_trials_uebung = num_spieler * 2
trial_duration = 2.0  # 2000ms
dur_feedback = 4.0 # 4000ms
dur_hierarchie = 5.0 # 5000ms
picture_size = [0.6, 0.9]  # Adjust the size of the pictures as needed
spieler_pic_size = [0.25, 0.5]
sterne_size = [0.25, 0.1]
thumb_size = [0.2, 0.35]
background_color = [0.5, 0.5, 0.5]  # Background color as RGB tuple
main_path= "C:/Privat/Forschung/Forschungsabteilung/Social Devaluation/PsychoPy Experimente/SocDev/"
setting = 1 # 1 = ohne Scanner, 2 = mit Scanner
left_but = 'left'
right_but = 'right'

if setting == 1:
    left_but = 'left'
    right_but = 'right'
elif setting == 2:
    left_but = 'b'
    right_but = 'c'
    

# Paths to your picture files (replace these with your actual file paths)
picture_files_34 = [
    main_path + "StimFiles/34-dots-400x400.bmp",
    main_path + "StimFiles/34-dots-400x400(1).bmp",
    main_path + "StimFiles/34-dots-400x400(2).bmp",
    main_path + "StimFiles/34-dots-400x400(3).bmp",
    main_path + "StimFiles/34-dots-400x400(4).bmp",
    main_path + "StimFiles/34-dots-400x400(5).bmp",
    main_path + "StimFiles/34-dots-400x400(6).bmp",
    main_path + "StimFiles/34-dots-400x400(7).bmp",
    main_path + "StimFiles/34-dots-400x400(8).bmp",
    main_path + "StimFiles/34-dots-400x400(9).bmp",
    main_path + "StimFiles/34-dots-400x400(10).bmp",
]

picture_files_36 = [
    main_path + "StimFiles/36-dots-400x400.bmp",
    main_path + "StimFiles/36-dots-400x400(1).bmp",
    main_path + "StimFiles/36-dots-400x400(2).bmp",
    main_path + "StimFiles/36-dots-400x400(3).bmp",
    main_path + "StimFiles/36-dots-400x400(4).bmp",
    main_path + "StimFiles/36-dots-400x400(5).bmp",
    main_path + "StimFiles/36-dots-400x400(6).bmp",
    main_path + "StimFiles/36-dots-400x400(7).bmp",
    main_path + "StimFiles/36-dots-400x400(8).bmp",
    main_path + "StimFiles/36-dots-400x400(9).bmp",
    main_path + "StimFiles/36-dots-400x400(10).bmp",
]

# Pfade zu den Bildern der Spieler (ersetze diese mit den tatsächlichen Dateipfaden)
spieler_bildpfade = {
    spieler_namen['spieler1']: main_path + "StimFiles/Dummy5_blau.bmp",
    spieler_namen['spieler2']: main_path + "StimFiles/Dummy5_gruen.bmp",
    spieler_namen['spieler3']: main_path + "StimFiles/Dummy5_rot.bmp",
}

# Pfade zu den Sternen :)
sterne_bildpfade = [
    main_path + "StimFiles/3sterren.bmp", # sterne3_pfad = sterne_bildpfade[0]
    main_path + "StimFiles/2sterren.bmp", # sterne2_pfad = sterne_bildpfade[1]
    main_path + "StimFiles/1ster.bmp", # sterne1_pfad = sterne_bildpfade[2]
]

#Pfade zu den Daumen
thumbup_pfad = main_path + "StimFiles/thumbup.bmp"
thumbdown_pfad = main_path + "StimFiles/thumbdown.bmp"

# Pfade zu den Instruktionsbildern (ersetze diese mit den tatsächlichen Dateipfaden)
instruktionsbilder = [
    main_path + r"StimFiles/screenshot_initial.bmp",
    main_path + r"StimFiles/screenshot_gegner.bmp",
    main_path + r"StimFiles/screenshot_gegenueber.bmp",
    main_path + r"StimFiles/screenshot_darstellung.bmp",
    main_path + r"StimFiles/screenshot_hier_rel_up.bmp",
    main_path + r"StimFiles/screenshot_hier_rel_dev.bmp",
    main_path + r"StimFiles/screenshot_gleichI.bmp",
    main_path + r"StimFiles/screenshot_missfeedback.bmp",
    main_path + r"StimFiles/screenshot_abgestiegen.bmp",
    main_path + r"StimFiles/screenshot_abgestiegen.bmp",
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

# Initialisiere Textstimuli für den Anweisungstext
instruktion_text = visual.TextStim(win=win, pos=[0,-0.6], color = (0,0,0), wrapWidth = 1.9)

# Initialisiere Bildstimulus für die Instruktionsbilder
instruktions_bild = visual.ImageStim(win=win, pos=[0,0.25], size=(1,1))

# Zeige Instruktionen
current_slide = 0  # Index des aktuellen Bildes

visual.TextStim(win=win, 
    text="Vielen Dank für ihre Teilnahme!\n\n Im Folgenden soll Ihnen anhand von Beispielbildern erklärt werden wie das Spiel funktioniert.\n\nIn den Beispielen sind fiktive Spieler dargestellt und eine Aufgabe, die Sie nicht bearbeiten müssen. \n Sie können durch diese Erklärungen vor und zurückblättern, bis Sie sie gut verstanden haben. \n Drücken Sie eine der Tasten unter ihren Zeigefingern um fortzufahren.",
    color = (0,0,0), 
    wrapWidth = 1.8
).draw()
win.flip()
if 'q' in event.waitKeys(keyList=[left_but, right_but, "q"]): 
        win.close()
        core.quit()  

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

## Übungsrunden
visual.TextStim(win=win, text="Wenn Sie bereit sind in die Übungsrunden zu starten, drücken Sie eine der Tasten unter ihren Fingern.",color=(0,0,0)).draw()
win.flip()
if "q" in event.waitKeys(keyList=[left_but, right_but, "q"]):
    win.close()
    core.quit()

# Auswahl der möglichen Bilder definieren
available_34_pictures = list(picture_files_34)
available_36_pictures = list(picture_files_36)
last_left_picture = None
last_right_picture = None

# Beginn der Trials
for spieler_index in range(num_trials_uebung):
    if random.choice([True, False]): # Zufällige Auswahl aus den möglichen Bildern und zufällige Wahl der Position
        left_picture = random.choice([pic for pic in available_34_pictures if pic != last_left_picture])
        right_picture = random.choice([pic for pic in available_36_pictures if pic != last_right_picture])
    else:
        left_picture = random.choice([pic for pic in available_36_pictures if pic != last_right_picture])
        right_picture = random.choice([pic for pic in available_34_pictures if pic != last_left_picture])
    
    #Setzen der "last pictures" für den nächsten Durchgang
    last_left_picture = left_picture
    last_right_picture = right_picture
   
   #Mitspieler festlegen # Vorlage für conditionals der Sterne und Positionen siehe Editordatei "Sterne und Positionszuordnung"
    if spieler_index % 2 == 0:
        opponent = spieler_namen['spieler1']
        opponent_pic = spieler_bildpfade[spieler_namen['spieler1']]
        left_spieler_pic = spieler_bildpfade[spieler_namen['spieler1']]
        left_name = spieler_namen['spieler1']
        right_spieler_pic = spieler_bildpfade[spieler_namen['spieler2']]
        right_name = spieler_namen['spieler2']
    else:
        opponent = spieler_namen['spieler3']
        opponent_pic = spieler_bildpfade[spieler_namen['spieler3']]
        left_spieler_pic = spieler_bildpfade[spieler_namen['spieler2']]
        left_name = spieler_namen['spieler2']
        right_spieler_pic = spieler_bildpfade[spieler_namen['spieler3']]
        right_name = spieler_namen['spieler3']
    
    # Stimuli erstellen
    opponent_text_stim = visual.TextStim(win=win,text=f"Sie spielen mit {opponent}",color=(0, 0, 0), pos=[0,0.5])
    opponent_pic_stim = visual.ImageStim(win=win,image=opponent_pic,size=spieler_pic_size,pos=[0,0])
    
    left_stimulus = visual.ImageStim( win=win,image=left_picture,size=picture_size,pos=[-0.4, -0.3])  # Position auf der linken Seite
    right_stimulus = visual.ImageStim(win=win,image=right_picture,size=picture_size,pos=[0.4, -0.3])  # Position auf der rechten Seite
    
    left_spieler_stim = visual.ImageStim(win=win,image=left_spieler_pic,size = spieler_pic_size,pos=[-0.4, 0.48])
    right_spieler_stim = visual.ImageStim(win=win,image=right_spieler_pic,size = spieler_pic_size,pos=[0.4, 0.48])
        
    left_name_stim = visual.TextStim(win=win,text=left_name,color=(0, 0, 0), pos=[-0.4, 0.8])
    right_name_stim = visual.TextStim(win=win,text=right_name,color=(0, 0, 0),pos=[0.4, 0.8])

    # Präsentiere die Bilder
    for frame in range(int(1.5 * 60)):  # 60 Hz Bildwiederholfrequenz
        opponent_text_stim.draw()
        opponent_pic_stim.draw()
        win.flip()
    
    for frame in range(int(1.5 * 60)):
        left_spieler_stim.draw()
        right_spieler_stim.draw()
        left_name_stim.draw()
        right_name_stim.draw()
        win.flip()
    
    for frame in range(int(trial_duration * 60)):  # 60 Hz Bildwiederholfrequenz
        left_stimulus.draw()
        right_stimulus.draw()
        left_spieler_stim.draw()
        right_spieler_stim.draw()
        left_name_stim.draw()
        right_name_stim.draw()
        win.flip()
    
    # Sammle die Antworten und Genauigkeit
    # Experimentteilnehmer:in
    response_spieler2 = event.getKeys(keyList=[left_but, right_but, 'q'])
    if response_spieler2:
        if (right_but in response_spieler2 and left_picture in picture_files_34 and right_picture in picture_files_36) or \
           (left_but in response_spieler2 and left_picture in picture_files_36 and right_picture in picture_files_34):
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
        feedback_color = (1, 0, 0)
    # Überprüfe die 'q'-Taste, um das Experiment zu beenden
    if 'q' in response_spieler2:
        win.close()
        core.quit()  # Beendet das Experiment

    feedback_text_stim = visual.TextStim(win=win,text = feedback_text,color= feedback_color,pos = [0,-0.2])

    # Gegenspieler
    wuerfel_op = random.randint(1, 100)
    if spieler_index % 2 == 0: #opponent = spieler1
        if wuerfel_op < 81:
            accuracy_op = 1
        else:
            accuracy_op = 0
    else:
        if wuerfel_op < 41:
            accuracy_op = 1
        else:
            accuracy_op = 0

    # Daumenstimuli zuordnen
    if spieler_index % 2 == 0:
        if accuracy_sp2 == 1 and accuracy_op == 1:
            right_thumb = thumbup_pfad
            left_thumb = thumbup_pfad
        elif accuracy_sp2 == 1 and accuracy_op == 0:
            right_thumb = thumbup_pfad
            left_thumb = thumbdown_pfad
        elif accuracy_sp2 == 0 and accuracy_op == 0:
            right_thumb = thumbdown_pfad
            left_thumb = thumbdown_pfad
        elif accuracy_sp2 == 0 and accuracy_op == 1:
            right_thumb = thumbdown_pfad
            left_thumb = thumbup_pfad
    else:
        if accuracy_sp2 == 1 and accuracy_op == 1:
            right_thumb = thumbup_pfad
            left_thumb = thumbup_pfad
        elif accuracy_sp2 == 1 and accuracy_op == 0:
            right_thumb = thumbdown_pfad
            left_thumb = thumbup_pfad
        elif accuracy_sp2 == 0 and accuracy_op == 0:
            right_thumb = thumbdown_pfad
            left_thumb = thumbdown_pfad
        elif accuracy_sp2 == 0 and accuracy_op == 1:
            right_thumb = thumbup_pfad
            left_thumb = thumbdown_pfad
    
    left_thumb_stim = visual.ImageStim(win=win,image = left_thumb,size = thumb_size,pos = [-0.7, 0.48])
    right_thumb_stim = visual.ImageStim(win=win,image= right_thumb,size = thumb_size,pos = [0.7, 0.48])
    
    # Zeige den Feedback-Bildschirm für eine kurze Dauer an (z. B. 1 Sekunde)
    for frame in range(int(dur_feedback * 60)):  # 60 Hz Bildwiederholfrequenz für 1 Sekunde
        feedback_text_stim.draw()
        left_thumb_stim.draw()
        right_thumb_stim.draw()
        left_spieler_stim.draw()
        right_spieler_stim.draw()
        left_name_stim.draw()
        right_name_stim.draw()
        win.flip()
    
    # Füge die Antwort und die Genauigkeit zur Liste der Spieler hinzu
    spieler_accuracies[spieler_namen['spieler2']].append(accuracy_sp2)
    if spieler_index % 2 == 0:
        spieler_accuracies[spieler_namen['spieler1']].append(accuracy_op)
    else:
        spieler_accuracies[spieler_namen['spieler3']].append(accuracy_op)

    # Wenn alle Durchgänge abgeschlossen sind, zeige die Rangfolge der Spieler an
    if (spieler_index) == num_trials_uebung - 1:
        visual.TextStim(win=win, text="Die Übungsrunden sind abgeschlossen.\n Drücken Sie eine beliebige Taste um sich die Rangreihe anzeigen zu lassen.", color=(0,0,0)).draw()
        win.flip()
        if 'q' in event.waitKeys(keyList=[left_but, right_but, "q"]):
            win.close()
            core.quit()
        
        spieler_leistungen[spieler_namen['spieler1']] = round((sum(spieler_accuracies[spieler_namen['spieler1']])*2)/int(spieler_index+1)*100,2)
        spieler_leistungen[spieler_namen['spieler2']] = round((sum(spieler_accuracies[spieler_namen['spieler2']]))/int(spieler_index+1)*100,2)
        spieler_leistungen[spieler_namen['spieler3']] = round((sum(spieler_accuracies[spieler_namen['spieler3']])*2)/int(spieler_index+1)*100,2)
        
        # Sortiere die Spieler nach ihrer Leistung absteigend
        sortierte_spieler = sorted(spieler_leistungen.items(), key=lambda x: x[1], reverse=True)
        first_name, first_leistung = sortierte_spieler[0]
        second_name, second_leistung = sortierte_spieler[1]
        third_name, third_leistung = sortierte_spieler[2]
        
        # Platzierungs-Dictionary füllen
        for index, (spieler, leistung) in enumerate(sortierte_spieler):
            if spieler == spieler_namen['spieler1']:
                spieler_platzierungen[spieler_namen['spieler1']] = index
            elif spieler == spieler_namen['spieler2']:
                spieler_platzierungen[spieler_namen['spieler2']] = index
            elif spieler == spieler_namen['spieler3']:
                spieler_platzierungen[spieler_namen['spieler3']] = index
        
        vorherige_platzierung_sp2 = spieler_platzierungen[spieler_namen['spieler2']]

        first_name_stim = visual.TextStim(win=win,text = f"{first_name}", color = (0,0,0), pos=[-0.6,0.83])
        first_picture_stim = visual.ImageStim(win=win, image= spieler_bildpfade[first_name], size= spieler_pic_size, pos=[-0.6, 0.5])
        first_stars_stim = visual.ImageStim(win=win, image= sterne_bildpfade[0], size= sterne_size, pos=[-0.6, 0.3])
        first_leistung_stim = visual.TextStim(win=win,text = f"{first_leistung}%", color = (0,0,0), pos=[-0.6,0.2])
        
        second_name_stim = visual.TextStim(win=win,text = f"{second_name}", color = (0,0,0), pos=[0,0.33])
        second_picture_stim = visual.ImageStim(win=win, image= spieler_bildpfade[second_name], size= spieler_pic_size, pos=[0, 0])
        second_stars_stim = visual.ImageStim(win=win, image= sterne_bildpfade[1], size= sterne_size, pos=[0, -0.2])
        second_leistung_stim = visual.TextStim(win=win,text = f"{second_leistung}%", color = (0,0,0), pos=[0,-0.3])
        
        third_name_stim = visual.TextStim(win=win,text = f"{third_name}", color = (0,0,0), pos=[0.6,-0.17])
        third_picture_stim = visual.ImageStim(win=win, image= spieler_bildpfade[third_name], size= spieler_pic_size, pos=[0.6, -0.5])
        third_stars_stim = visual.ImageStim(win=win, image= sterne_bildpfade[2], size= sterne_size, pos=[0.6, -0.7])
        third_leistung_stim = visual.TextStim(win=win,text = f"{third_leistung}%", color = (0,0,0), pos=[0.6,-0.8])
        
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
        win.flip()
        
        if 'q' in event.waitKeys(keyList=[left_but, right_but, "q"]):
            win.close()
            core.quit()

# Display-Anweisungen
visual.TextStim(
    win=win,
    text=f"Nun beginnt das eigentliche Spiel.\n\n Warten Sie bitte bis der Versuchleiter das Spiel startet.",
    color=(0, 0, 0)  # Black color as RGB tuple
).draw()
win.flip()
if 'q' in event.waitKeys(keyList=['space', 'q']): # Warten Sie auf die Leertaste, um das Experiment zu starten
        win.close()
        core.quit()  


# Auf den ersten Puls des Scanners warten
visual.TextStim(win=win,text=f"Warten auf Signal des Scanners...",color=(0,0,0)).draw()
win.flip()
core.wait(1)
#hardware.emulator.launchScan(win=win, TR=2, volumes=200, sync='s',globalClock=True, simResponses=True, mode='Test')# 
event.waitKeys(keyList=['s'])#auf den ersten puls des scanners warten. Der Puls wird von der Stimulus Box als 's' weitergeleitet.


# Auswahl der möglichen Bilder definieren
available_34_pictures = list(picture_files_34)
available_36_pictures = list(picture_files_36)

last_left_picture = None
last_right_picture = None

# Accuracies und Leistungen neu initialisieren
spieler_leistungen = {spieler_namen[name]: 0 for name in spieler_namen}
spieler_accuracies = {spieler_namen[name]: [] for name in spieler_namen}

# Beginn der Trials
for spieler_index in range(num_trials_gesamt):
    if random.choice([True, False]): # Zufällige Auswahl aus den möglichen Bildern und zufällige Wahl der Position
        left_picture = random.choice([pic for pic in available_34_pictures if pic != last_left_picture])
        right_picture = random.choice([pic for pic in available_36_pictures if pic != last_right_picture])
    else:
        left_picture = random.choice([pic for pic in available_36_pictures if pic != last_right_picture])
        right_picture = random.choice([pic for pic in available_34_pictures if pic != last_left_picture])
    
    #Setzen der "last pictures" für den nächsten Durchgang
    last_left_picture = left_picture
    last_right_picture = right_picture
   
   #Mitspieler festlegen # Vorlage für conditionals der Sterne und Positionen siehe Editordatei "Sterne und Positionszuordnung"  
    if spieler_index % 2 == 0:
        opponent = spieler_namen['spieler1']
    else:
        opponent = spieler_namen['spieler3']

    opponent_pic = spieler_bildpfade[opponent]
    opponent_stars = sterne_bildpfade[spieler_platzierungen[opponent]]

    if spieler_platzierungen[spieler_namen['spieler2']] > spieler_platzierungen[opponent]:
        op_hier = 1 # für die Output-Datei
        left_spieler_pic = opponent_pic
        left_stars = opponent_stars
        left_name = opponent
        right_spieler_pic = spieler_bildpfade[spieler_namen['spieler2']]
        right_stars = sterne_bildpfade[spieler_platzierungen[spieler_namen['spieler2']]]
        right_name = spieler_namen['spieler2']
    else:
        op_hier = 0 # für die Output-Datei
        left_spieler_pic = spieler_bildpfade[spieler_namen['spieler2']]
        left_stars = sterne_bildpfade[spieler_platzierungen[spieler_namen['spieler2']]]
        left_name = right_name = spieler_namen['spieler2']
        right_spieler_pic = opponent_pic
        right_stars = opponent_stars
        right_name = opponent

    # Stimuli erstellen
    opponent_text_stim = visual.TextStim(win=win,text=f"Sie spielen mit {opponent}",color=(0, 0, 0), pos=[0,0.5])
    opponent_pic_stim = visual.ImageStim(win=win,image=opponent_pic,size=spieler_pic_size,pos=[0,0])
    opponent_stars_stim = visual.ImageStim(win=win,image=opponent_stars,size=sterne_size,pos=[0,-0.205])
    
    left_stimulus = visual.ImageStim(win=win,image=left_picture,size=picture_size,pos=[-0.4, -0.3])
    right_stimulus = visual.ImageStim(win=win,image=right_picture,size=picture_size,pos=[0.4, -0.3])
    
    left_spieler_stim = visual.ImageStim(win=win,image=left_spieler_pic,size = spieler_pic_size,pos=[-0.4, 0.48])
    right_spieler_stim = visual.ImageStim(win=win,image=right_spieler_pic,size = spieler_pic_size,pos=[0.4, 0.48])
    
    left_sterne_stim = visual.ImageStim(win=win,image=left_stars,size=sterne_size,pos=[-0.4, 0.275])
    right_sterne_stim = visual.ImageStim(win=win,image=right_stars,size = sterne_size,pos=[0.4, 0.275])
    
    left_name_stim = visual.TextStim(win=win,text=left_name,color=(0, 0, 0),pos=[-0.4, 0.8])
    right_name_stim = visual.TextStim(win=win,text=right_name,color=(0, 0, 0),pos=[0.4, 0.8])

    # Präsentiere die Bilder
    for frame in range(int(1.5 * 60)):  # 60 Hz Bildwiederholfrequenz
        opponent_text_stim.draw()
        opponent_pic_stim.draw()
        opponent_stars_stim.draw()
        win.flip()
    
    for frame in range(int(1.5 * 60)):
        left_spieler_stim.draw()
        right_spieler_stim.draw()
        right_sterne_stim.draw()
        left_sterne_stim.draw()
        left_name_stim.draw()
        right_name_stim.draw()
        win.flip()
    
    for frame in range(int(trial_duration * 60)):  # 60 Hz Bildwiederholfrequenz
        left_stimulus.draw()
        right_stimulus.draw()
        left_spieler_stim.draw()
        right_spieler_stim.draw()
        right_sterne_stim.draw()
        left_sterne_stim.draw()
        left_name_stim.draw()
        right_name_stim.draw()
        win.flip()
    
    # Sammle die Antworten und Genauigkeit
    # Experimentteilnehmer:in
    response_spieler2 = event.getKeys(keyList=[left_but, right_but, 'q'])
    if response_spieler2:
        if (right_but in response_spieler2 and left_picture in picture_files_34 and right_picture in picture_files_36) or \
           (left_but in response_spieler2 and left_picture in picture_files_36 and right_picture in picture_files_34):
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
        feedback_color = (1, 0, 0)
    # Überprüfe die 'q'-Taste, um das Experiment zu beenden
    if 'q' in response_spieler2:
        win.close()
        core.quit()  # Beendet das Experiment
    
    feedback_text_stim = visual.TextStim(win=win,text = feedback_text,color= feedback_color,pos = [0,-0.2])

    # Gegenspieler
    wuerfel_op = random.randint(1, 100)
    if spieler_index % 2 == 0: #opponent = spieler1
        if wuerfel_op < 81:
            accuracy_op = 1
        else:
            accuracy_op = 0
    else:
        if wuerfel_op < 41:
            accuracy_op = 1
        else:
            accuracy_op = 0

    # Daumenstimuli zuordnen
    if left_name == opponent:
        if accuracy_sp2 == 1 and accuracy_op == 1:
            right_thumb = thumbup_pfad
            left_thumb = thumbup_pfad
        elif accuracy_sp2 == 1 and accuracy_op == 0:
            right_thumb = thumbup_pfad
            left_thumb = thumbdown_pfad
        elif accuracy_sp2 == 0 and accuracy_op == 0:
            right_thumb = thumbdown_pfad
            left_thumb = thumbdown_pfad
        elif accuracy_sp2 == 0 and accuracy_op == 1:
            right_thumb = thumbdown_pfad
            left_thumb = thumbup_pfad
    elif right_name == opponent:
        if accuracy_sp2 == 1 and accuracy_op == 1:
            right_thumb = thumbup_pfad
            left_thumb = thumbup_pfad
        elif accuracy_sp2 == 1 and accuracy_op == 0:
            right_thumb = thumbdown_pfad
            left_thumb = thumbup_pfad
        elif accuracy_sp2 == 0 and accuracy_op == 0:
            right_thumb = thumbdown_pfad
            left_thumb = thumbdown_pfad
        elif accuracy_sp2 == 0 and accuracy_op == 1:
            right_thumb = thumbup_pfad
            left_thumb = thumbdown_pfad
    
    left_thumb_stim = visual.ImageStim(win=win,image = left_thumb,size = thumb_size,pos = [-0.7, 0.48])
    right_thumb_stim = visual.ImageStim(win=win,image= right_thumb,size = thumb_size,pos = [0.7, 0.48])
    
    # Zeige den Feedback-Bildschirm für eine kurze Dauer an (z. B. 1 Sekunde)
    for frame in range(int(dur_feedback * 60)):  # 60 Hz Bildwiederholfrequenz für 1,5 Sekunde
        feedback_text_stim.draw()
        left_thumb_stim.draw()
        right_thumb_stim.draw()
        left_spieler_stim.draw()
        right_spieler_stim.draw()
        right_sterne_stim.draw()
        left_sterne_stim.draw()
        left_name_stim.draw()
        right_name_stim.draw()
        win.flip()
    
    # Füge die Antwort und die Genauigkeit zur Liste der Spieler hinzu
    spieler_accuracies[spieler_namen['spieler2']].append(accuracy_sp2)
    if spieler_index % 2 == 0:
        spieler_accuracies[spieler_namen['spieler1']].append(accuracy_op)
    else:
        spieler_accuracies[spieler_namen['spieler3']].append(accuracy_op)
    
    # Aktualisiere die Leistungen
    spieler_leistungen[spieler_namen['spieler1']] = round((sum(spieler_accuracies[spieler_namen['spieler1']])*2)/int(spieler_index+1)*100,2)
    spieler_leistungen[spieler_namen['spieler2']] = round((sum(spieler_accuracies[spieler_namen['spieler2']]))/int(spieler_index+1)*100,2)
    spieler_leistungen[spieler_namen['spieler3']] = round((sum(spieler_accuracies[spieler_namen['spieler3']])*2)/int(spieler_index+1)*100,2)
    # Sortiere die Spieler nach ihrer Leistung absteigend
    sortierte_spieler = sorted(spieler_leistungen.items(), key=lambda x: x[1], reverse=True)
    
    # Wenn alle Durchgänge abgeschlossen sind, zeige die Rangfolge der Spieler an
    if (spieler_index+1) % 4 == 0 and spieler_index > 0 or spieler_index == num_trials_gesamt - 1:#  == num_trials_gesamt - 1: # Der spieler_index startet bei 0, sodass er nach 10 trials bei 9 (num_trials_gesamt - 1) steht.
        first_name, first_leistung = sortierte_spieler[0]
        second_name, second_leistung = sortierte_spieler[1]
        third_name, third_leistung = sortierte_spieler[2]
        # Platzierungs-Dictionary füllen
        for index, (spieler, leistung) in enumerate(sortierte_spieler):
            if spieler == spieler_namen['spieler1']:
                spieler_platzierungen[spieler_namen['spieler1']] = index
            elif spieler == spieler_namen['spieler2']:
                spieler_platzierungen[spieler_namen['spieler2']] = index
            elif spieler == spieler_namen['spieler3']:
                spieler_platzierungen[spieler_namen['spieler3']] = index
        
        aktuelle_platzierung_sp2 = spieler_platzierungen[spieler_namen['spieler2']]

        if aktuelle_platzierung_sp2 < vorherige_platzierung_sp2:
            vergleichs_variable = "Aufgestiegen" # In der Output-Datei nutzen
        elif aktuelle_platzierung_sp2 > vorherige_platzierung_sp2:
            vergleichs_variable = "Abgestiegen" # In der Output-Datei nutzen
        else:
            vergleichs_variable = "" # In der Output-Datei nutzen
    
        vorherige_platzierung_sp2 = aktuelle_platzierung_sp2
        
        vergleichs_stim = visual.TextStim(win=win, text=vergleichs_variable, color=(0,0,0), pos=[-0.6, -0.6])
        
        first_name_stim = visual.TextStim(win=win,text = f"{first_name}", color = (0,0,0), pos=[-0.6,0.83])
        first_picture_stim = visual.ImageStim(win=win, image= spieler_bildpfade[first_name], size= spieler_pic_size, pos=[-0.6, 0.5])
        first_stars_stim = visual.ImageStim(win=win, image= sterne_bildpfade[0], size= sterne_size, pos=[-0.6, 0.3])
        first_leistung_stim = visual.TextStim(win=win,text = f"{first_leistung}%", color = (0,0,0), pos=[-0.6,0.2])
        
        second_name_stim = visual.TextStim(win=win,text = f"{second_name}", color = (0,0,0), pos=[0,0.33])
        second_picture_stim = visual.ImageStim(win=win, image= spieler_bildpfade[second_name], size= spieler_pic_size, pos=[0, 0])
        second_stars_stim = visual.ImageStim(win=win, image= sterne_bildpfade[1], size= sterne_size, pos=[0, -0.2])
        second_leistung_stim = visual.TextStim(win=win,text = f"{second_leistung}%", color = (0,0,0), pos=[0,-0.3])
        
        third_name_stim = visual.TextStim(win=win,text = f"{third_name}", color = (0,0,0), pos=[0.6,-0.17])
        third_picture_stim = visual.ImageStim(win=win, image= spieler_bildpfade[third_name], size= spieler_pic_size, pos=[0.6, -0.5])
        third_stars_stim = visual.ImageStim(win=win, image= sterne_bildpfade[2], size= sterne_size, pos=[0.6, -0.7])
        third_leistung_stim = visual.TextStim(win=win,text = f"{third_leistung}%", color = (0,0,0), pos=[0.6,-0.8])
        
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
            vergleichs_stim.draw()
            win.flip()

# Zeige die Nachricht für die Teilnehmer an
wartungs_text = visual.TextStim(
    win=win,
    text="Vielen Dank für ihre Teilnahme! \n\n Bitte warten Sie, bis der Versuchsleiter das Spiel beendet.",
    color=(0, 0, 0)  # Schwarze Farbe für den Text (RGB-Tupel)
)
wartungs_text.draw()
win.flip()

event.waitKeys(keyList=['q'])

# Beende das Experiment
win.close()
core.quit()
