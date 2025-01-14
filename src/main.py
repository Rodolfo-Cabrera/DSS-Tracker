#Calling the required packages
import re
import os
import pickle
import pandas as pd
import json
import dss_utils as utils
import PySimpleGUI as sg
from Mouse_Class import Mouse

# Loading the User list
f = open("users_list.json", 'r')
lab_members_dict = json.load(f)
lab_members = lab_members_dict['Users']
current_user = lab_members[0]

# Making the dictionary for the images

face_dict = {"0Face": "0_loss.png",
             "5Face": "5_loss.png",
             "10Face": "10_loss.png",
             "15Face": "15_loss.png"}

# Checking if the program folder exists or needs to be created
working_directory = os.getcwd()
program_folder = os.path.join(working_directory, 'DSS Experiments')
if not os.path.exists(program_folder):
    os.makedirs(program_folder)

# Making the start window of the program

# Layout object
layout = utils.intro_layout(lab_members=lab_members, current_user=current_user)

# Window object
window = sg.Window(title="DSS Tracker - by RICS", layout=layout)

## EVENT HANDLING

while True:  # Infinite loop to have the GUI working until break is called
    event, values = window.read()  # Recovering all the events and values from the window to use

    # Closing Program
    if event in (sg.WIN_CLOSED, '-Quit-'):
        break

# Handling starting a new experiment

    # If a new experiment is called
    if event == '-NewExp-':

        # Updating Current User info, in case they cancel and go back to intro window
        current_user = values['-User-']

        # Getting the groups information from user
        groups = sg.popup_get_text("How many groups do you have?")

        # Checking that the user provided an integer number above 0
        if groups is not None and groups != "" and groups != "0":
            # Making a quick window to get the information of how many mice each group has
            if utils.check_integer(groups):
                # Running function to create the folders where to save the experiment
                experiment_file_folder, experiment_results_folder, experiment_folder_name = utils.create_folders(program_folder=program_folder,
                                     current_user=current_user)
                group_keys = []
                group_name_keys = []
                groups = int(groups)
                for i in range(groups):
                    keys = f"-Group{i}-"
                    name_keys = f"-Group{i}Name-"
                    group_keys.append(keys)
                    group_name_keys.append(name_keys)
                # Layout to ask for the amount of mice per group
                new_layout = [
                    [sg.Push(), sg.Text('Indicate the Amount of Mice in each Group and the Group Name'), sg.Push()],
                    [sg.HorizontalSeparator()],
                    [[sg.Text('Group {num} Mice #'.format(num=j + 1), font=("Arial Bold", 10), pad=(5, 15)),
                      sg.Input(k=group_keys[j], s=(6, 7)), sg.Text('Group {num} Name'.format(num=j + 1), font=("Arial Bold", 10), pad=(5, 15)),
                      sg.Input(k=group_name_keys[j], s=(25, 7))]
                     for j in range(groups)],
                    [sg.Push(), sg.Text('Indicate the DSS% for this Experiment'), sg.Push()],
                    [sg.HorizontalSeparator()],
                    [sg.Push(),sg.Text("DSS %", font=('Arial Bold', 10), pad=(9.2, 15)), sg.Input(s=(6, 7), k='-DSSPER-'),sg.Push()],
                    [[sg.Button("Confirm", k="-Confirm-"), sg.Button("Cancel", k="-Cancel-")]]]
                # Closing the intro window
                window.close()
                # Opening the window for asking mice numbers
                window = sg.Window(title="DSS Tracker - by RICS", layout=new_layout)
            else:  # If user provided value that cannot be made an integer show error
                utils.show_error()
        else:  # If user did not type anything, hit cancel or type 0, showing error message
            utils.show_error()

    # If user cancel after creating the windows for asking mice numbers, returning to intro window
    if event == '-Cancel-':
        # Remaking the intro window
        return_layout = utils.intro_layout(lab_members=lab_members, current_user=current_user)
        # Closing the window asking for mice number
        window.close()
        # Opening intro window again
        window = sg.Window(title="DSS Tracker - by RICS", layout=return_layout)

    # If user confirms the number of mice. Creating the experiment window
    if event == '-Confirm-':
        # Checking and saving if a value for DSS% was provided or placing a generic text if left empty
        if values['-DSSPER-'] == "":
            dss_percentage = "No DSS% Registered"
        else:
            dss_percentage = values['-DSSPER-']

        # Providing a Day value for user to know which day they are at
        day = 0

        # Saving the amount of mice on each group in a list
        num_mice = []
        group_names = []
        # Boolean to verify that user did not typed 0
        no_empty_mice = True
        for i in group_keys:
            if values[i] == "0":
                no_empty_mice = False
            else:
                num_mice.append(values[i])
        for name in group_name_keys:
            if values[name] == "":
                default_name = f'Group {group_name_keys.index(name) + 1}'
                group_names.append(default_name)
            else:
                group_names.append(values[name])

        # Checking that all the values provided by user are numbers
        if utils.check_integer(num_mice) and no_empty_mice:
            num_mice = [int(i) for i in num_mice]

            # Closing the window asking for mice number
            window.close()

            # Making the layout and the keys required for the experiment window
            plate_layout, weight_keys, feces_keys, blood_keys, note_keys, gender_keys, eartag_keys = utils.experiment_maker(groups=groups,
                                                                                                                      num_mice=num_mice,
                                                                                                                      group_names=group_names,
                                                                                                                      day=day,
                                                                                                                      first=True)
            # Showing the window
            window = sg.Window(title="DSS Tracker - by RICS", layout=plate_layout)
        # If user provide 0 or a number that cannot be an integer, showing error
        else:
            utils.show_error()

# Handling the saving of the experiment file or creating the plots and csv files

    # Saving the information of each mice for the day
  
    # Checking if the experiment object exist  
    if event == '-Save-':
      try:
        experiment
      except NameError:
        experiment_exist = False
      else:
        experiment_exist = True

        if experiment_exist:  # If experiment exist, adding information to existing Mouse Classes
            # Boolean holder to revert to previous experiment file in case one of the mouse have issues
            error_happened = False
            # Saving the experiment before any changes in case an error happens
            experiment_copy = experiment
            # Doing to the loop to add info to existing mouse Classes
            # If statement in case the experiment is only with one group
            if isinstance(num_mice, int):
                for groups in range(groups):
                    for mouse in range(num_mice):
                        # Getting the DSS Info
                        dss_value = values['-DSS-']

                        # Making none in case user provided anything that isn't a number
                        weight_value = utils.make_none(values[f'-Group{group + 1}Weight{mouse + 1}-'], weight=True)

                        feces_value = utils.make_none(values[f'-Group{group + 1}Feces{mouse + 1}-'])

                        blood_value = utils.make_none(values[f'-Group{group + 1}Blood{mouse + 1}-'])

                        note_values = utils.make_none(values[f'-Group{group + 1}Notes{mouse + 1}-'])

                        # Making a list of all values to verify all values are integers, or floats in case of weight
                        checking_all_values = [weight_value, feces_value, blood_value]

                        wrong_info = []

                        # Loop to verify all values are numbers
                        # None is allowed here because user can decide to not provide a day
                        for value in checking_all_values:
                            if value is None:
                                wrong_info.append(True)
                            else:
                                wrong_info.append(check_integer([value]))

                        # If all values are valid, saving the information on each Mouse Class
                        if all(wrong_info) and weight_value is not None:
                            if note_values is None:
                                # Choosing the adequate Mouse Object in the experiment and saving data
                                experiment[f'Group{group + 1}Mouse{mouse + 1}'].add_day(dss=dss_value,
                                                                                        weight=weight_value,
                                                                                        feces=feces_value,
                                                                                        blood=blood_value)
                                # Getting mouse group and number to include in the warning if needed
                                mice_name = f'Group{group + 1} Mouse{mouse + 1}'
                                # Checking if a warning should be shown to user
                                utils.loss_weight_warning(mouse=experiment[f'Group{group + 1}Mouse{mouse + 1}'],
                                                    name=mice_name)
                            else:
                                # Choosing the adequate Mouse Object in the experiment and saving data
                                experiment[f'Group{group + 1}Mouse{mouse + 1}'].add_day(dss=dss_value,
                                                                                        weight=weight_value,
                                                                                        feces=feces_value,
                                                                                        blood=blood_value)
                                # Saving notes to the same Mouse Object
                                experiment[f'Group{group + 1}Mouse{mouse + 1}'].add_notes(note_values)
                                # Getting mouse group and number to include in the warning if needed
                                mice_name = f'Group{group + 1} Mouse{mouse + 1}'
                                # Checking if a warning should be shown to user
                                utils.loss_weight_warning(mouse=experiment[f'Group{group + 1}Mouse{mouse + 1}'],
                                                    name=mice_name)
                        else:  # If one or more values are note valid showing error message
                            if weight_value == None:
                                # If error was due to a mice missing the weight value. Making custom error message
                                error_message = f'Mouse {mouse + 1} from Group {group + 1} has no weight value'
                                # Updating the error_happened variable
                                error_happened = True
                                # Showing error message to user
                                sg.popup_error(error_message)
                            else:  # If the error was not because of weight, showing generic error message
                                error_happened = True
                                utils.show_error()
                if error_happened:
                    # Because error happened at least one, the experiment will be reverted to before any change
                    experiment = experiment_copy
                else:
                    #Saving the experiment all info required to re-open later
                    utils.saving_file(experiment=experiment,
                                day=day,
                                groups=groups,
                                group_names=group_names,
                                num_mice=num_mice,
                                experiment_file_folder=experiment_file_folder,
                                experiment_results_folder=experiment_results_folder,
                                experiment_folder_name=experiment_folder_name)
            # If experiment exist and there is more than one group
            else:
                # Looping per each group and doing one mouse at a time
                for group in range(groups):
                    mice = num_mice[group]
                    for mouse in range(mice):
                        # Getting the DSS Info
                        dss_value = values['-DSS-']

                        # Making none in case user provided anything that isn't a number
                        weight_value = utils.make_none(values[f'-Group{group + 1}Weight{mouse + 1}-'], weight=True)

                        feces_value = utils.make_none(values[f'-Group{group + 1}Feces{mouse + 1}-'])

                        blood_value = utils.make_none(values[f'-Group{group + 1}Blood{mouse + 1}-'])

                        note_values = utils.make_none(values[f'-Group{group + 1}Notes{mouse + 1}-'])

                        # Making a list of all values to verify all values are integers, or floats in case of weight
                        checking_all_values = [weight_value, feces_value, blood_value]

                        wrong_info = []

                        # Loop to verify all values are numbers
                        # None is allowed here because user can decide to not provide a day
                        for value in checking_all_values:
                            if value is None:
                                wrong_info.append(True)
                            else:
                                utils.check_integer([value])
                        # If all values are valid, saving the information on each Mouse Class
                        if all(wrong_info) and weight_value is not None:
                            if note_values is None:
                                # Choosing the adequate Mouse Object in the experiment and saving data
                                experiment[f'Group{group + 1}Mouse{mouse + 1}'].add_day(dss=dss_value,
                                                                                        weight=weight_value,
                                                                                        feces=feces_value,
                                                                                        blood=blood_value)
                                # Getting mouse group and number to include in the warning if needed
                                mice_name = f'Group{group + 1} Mouse{mouse + 1}'
                                # Checking if a warning should be shown to user
                                utils.loss_weight_warning(mouse=experiment[f'Group{group + 1}Mouse{mouse + 1}'],
                                                    name=mice_name)
                            else:
                                # Choosing the adequate Mouse Object in the experiment and saving data
                                experiment[f'Group{group + 1}Mouse{mouse + 1}'].add_day(dss=dss_value,
                                                                                        weight=weight_value,
                                                                                        feces=feces_value,
                                                                                        blood=blood_value)
                                # Saving notes to the same Mouse Object
                                experiment[f'Group{group + 1}Mouse{mouse + 1}'].add_notes(note_values)
                                # Getting mouse group and number to include in the warning if needed
                                mice_name = f'Group{group + 1} Mouse{mouse + 1}'
                                # Checking if a warning should be shown to user
                                utils.loss_weight_warning(mouse=experiment[f'Group{group + 1}Mouse{mouse + 1}'],
                                                    name=mice_name)
                        else:  # If one or more values are note valid showing error message
                            if weight_value == None:
                                # If error was due to a mice missing the weight value. Making custom error message
                                error_message = f'Mouse {mouse + 1} from Group {group + 1} has no weight value'
                                # Updating the error_happened variable
                                error_happened = True
                                # Showing error message to user
                                sg.popup_error(error_message)
                            else:  # If the error was not because of weight, showing generic error message
                                error_happened = True
                                utils.show_error()
                if error_happened:
                    # Because error happened at least one, the experiment will be reverted to before any change
                    experiment = experiment_copy
                else:
                    # Saving the experiment all info required to re-open later
                    utils.saving_file(experiment=experiment,
                                groups=groups,
                                day=day,
                                group_names=group_names,
                                num_mice=num_mice,
                                experiment_file_folder=experiment_file_folder,
                                experiment_results_folder=experiment_results_folder,
                                experiment_folder_name=experiment_folder_name)

        # Creating a new experiment if experiment object doest not exist
        else:
            # Boolean holder to revert to previous experiment file in case one of the mouse have issues
            error_happened = False
            # Making the object that will save the whole experiment
            experiment = {}

            # Doing to the loop to create all the Mouse Objects needed

            # If statement in case the experiment is only with one group
            if isinstance(num_mice, int):
                for group in range(groups):
                    for mouse in range(num_mice):
                        # Getting the DSS Info
                        dss_value = values['-DSS-']
                        # Making none in case user provided anything that isn't a number
                        weight_value = utils.make_none(values[f'-Group{group + 1}Weight{mouse + 1}-'], weight=True)

                        feces_value = utils.make_none(values[f'-Group{group + 1}Feces{mouse + 1}-'])

                        blood_value = utils.make_none(values[f'-Group{group + 1}Blood{mouse + 1}-'])

                        note_values = utils.make_none(values[f'-Group{group + 1}Notes{mouse + 1}-'])

                        gender_value = values[f'-Group{group + 1}Gender{mouse + 1}-']

                        eartag_value = values[f'-Group{group + 1}Eartag{mouse + 1}-']

                        # Making a list of all values to verify all values are integers, or floats in case of weight
                        checking_all_values = [weight_value, feces_value, blood_value]

                        wrong_info = []

                        # Loop to verify all values are numbers
                        # None is allowed here because user can decide to not provide a day
                        for value in checking_all_values:
                            if value is None:
                                wrong_info.append(True)
                            else:
                                utils.check_integer([value])

                        # If all values are valid, saving the information on each Mouse Class
                        # Because it is the first day, there should not be any Mouse with weight 0 or dead
                        if all(wrong_info) and weight_value is not None and weight_value != 0:
                            # Making the Mouse Object
                            current = Mouse(dss=dss_value,
                                            weight=weight_value,
                                            feces=feces_value,
                                            blood=blood_value,
                                            group=group_names[group],
                                            mouse_name=f'Mouse {mouse + 1}',
                                            gender=gender_value,
                                            eartag=eartag_value,
                                            dss_percentage=dss_percentage
                                            )
                            # If there are notes for the Mouse, added them to the Object
                            # Before saving the Mouse in the experiment dictionary

                            if note_values is None:
                                experiment[f'Group{group + 1}Mouse{mouse + 1}'] = current
                            else:
                                current.add_notes(note_values)
                                experiment[f'Group{group + 1}Mouse{mouse + 1}'] = current
                        else:  # If one or more values are note valid showing error message
                            if weight_value is None or weight_value == 0:
                                # If error was due to a mice missing the weight value. Making custom error message
                                error_message = f'Mouse {mouse + 1} from Group {group + 1} has no weight value'
                                # Updating the error_happened variable
                                error_happened = True
                                # Showing error message to user
                                sg.popup_error(error_message)
                            else:  # If the error was not because of weight, showing generic error message
                                error_happened = True
                                utils.show_error()
                if error_happened:
                    # Because this is the first day. If any error happened, the experiment object gets deleted
                    del(experiment)
                else:
                    # Saving the experiment all info required to re-open later
                    utils.saving_file(experiment=experiment,
                                groups=groups,
                                day=day,
                                group_names=group_names,
                                num_mice=num_mice,
                                experiment_file_folder=experiment_file_folder,
                                experiment_results_folder=experiment_results_folder,
                                experiment_folder_name=experiment_folder_name)

            # If experiment does not exist and there are more than one group
            else:
                # Looping per each group and doing one mouse at a time
                for group in range(groups):
                    mice = num_mice[group]
                    for mouse in range(mice):
                        # Getting the DSS Info
                        dss_value = values['-DSS-']

                        # Making none in case user provided anything that isn't a number
                        weight_value = utils.make_none(values[f'-Group{group + 1}Weight{mouse + 1}-'], weight=True)

                        feces_value = utils.make_none(values[f'-Group{group + 1}Feces{mouse + 1}-'])

                        blood_value = utils.make_none(values[f'-Group{group + 1}Blood{mouse + 1}-'])

                        note_values = utils.make_none(values[f'-Group{group + 1}Notes{mouse + 1}-'])

                        gender_value = values[f'-Group{group + 1}Gender{mouse + 1}-']

                        eartag_value = values[f'-Group{group + 1}Eartag{mouse + 1}-']

                        # Making a list of all values to verify all values are integers, or floats in case of weight
                        checking_all_values = [weight_value, feces_value, blood_value]

                        wrong_info = []

                        # Loop to verify all values are numbers
                        # None is allowed here because user can decide to not provide a day
                        for value in checking_all_values:
                            if value is None:
                                wrong_info.append(True)
                            else:
                                utils.check_integer([value])

                        # If all values are valid, saving the information on each Mouse Class
                        # Because it is the first day, there should not be any Mouse with weight 0 or dead
                        if all(wrong_info) and weight_value is not None and weight_value != 0:
                            # Making the Mouse Object
                            current = Mouse(dss=dss_value,
                                            weight=weight_value,
                                            feces=feces_value,
                                            blood=blood_value,
                                            group=group_names[group],
                                            mouse_name=f'Mouse {mouse + 1}',
                                            gender=gender_value,
                                            eartag=eartag_value,
                                            dss_percentage=dss_percentage
                                            )
                            # If there are notes for the Mouse, added them to the Object
                            # Before saving the Mouse in the experiment dictionary
                            if note_values is None:
                                experiment[f'Group{group + 1}Mouse{mouse + 1}'] = current
                            else:
                                current.add_notes(note_values)
                                experiment[f'Group{group + 1}Mouse{mouse + 1}'] = current

                        else:  # If one or more values are note valid showing error message
                            if weight_value == None or weight_value == 0:
                                # If error was due to a mice missing the weight value. Making custom error message
                                error_message = f'Mouse {mouse + 1} from Group {group + 1} has no weight value'
                                # Updating the error_happened variable
                                error_happened = True
                                # Showing error message to user
                                sg.popup_error(error_message)
                            else:  # If the error was not because of weight, showing generic error message
                                # Updating the error_happened variable
                                error_happened = True
                                utils.show_error()
                if error_happened:
                    # Because this is the first day. If any error happened, the experiment object get deleted
                    del(experiment)
                else:
                    # Saving the experiment all info required to re-open later
                    utils.saving_file(experiment=experiment,
                                groups=groups,
                                day=day,
                                group_names=group_names,
                                num_mice=num_mice,
                                experiment_file_folder=experiment_file_folder,
                                experiment_results_folder=experiment_results_folder,
                                experiment_folder_name=experiment_folder_name)

    # Creating the csv file and the plots for the experiment
    if event == '-Generate-':
        # Verifying that an experiment was created
        try:
        experiment
      except NameError:
        experiment_exist = False
      else:
        experiment_exist = True

        if experiment_exist:
            # Making the holder of all the dataframes
            dataframes = []
            # Looping per mice to get their information
            for mouse in experiment.values():
                # Getting the info and notes apart
                dataframes.append(mouse.export_data())
                notes_df, notes_name = mouse.export_notes()
                # Making the pathway to save the notes the mouse individually
                notes_pathway = os.path.join(experiment_results_folder, 'Notes', f'{notes_name}.csv')
                # Saving the notes
                notes_df.to_csv(notes_pathway)

            # Once all the info of each mouse was recovered, combining all of them in a big dataframe
            dataframes = pd.concat(dataframes)
            # Making the pathway where to save the dataframe and the plots
            csv_pathway = os.path.join(experiment_results_folder,f'{experiment_folder_name}.csv')
            weight_pathway = os.path.join(experiment_results_folder,'Weight_Percentage')
            dai_pathway = os.path.join(experiment_results_folder, 'DAI_Score')
            feces_pathway = os.path.join(experiment_results_folder, 'Feces_Score')
            blood_pathway = os.path.join(experiment_results_folder, 'Blood_Score')
            # Saving the dataframe
            dataframes.to_csv(csv_pathway)

            # Making the Plots

            # Getting the last day on the experiment to adjust the x ticks accordingly
            days_recorded = dataframes["Day"].max()

            # Making a dataframe for the plots combining each mice per group and day
            # And getting the mean for Weight Percentage, DAI Score, Feces Score, and Blood Score
            plot_df = dataframes.groupby(['Day', 'Group']).mean(['Weight_Percentage','DAI_Score','Feces','Blood']).unstack()

            #Making the Weight Percentage plot and saving the file
            (plot_df['Weight_Percentage'].
             plot(title="Weight Change (%)", xlabel= "Days", xticks=range(1,days_recorded+1,1), ylabel="% Weight", yticks=range(70, 101, 2), figsize=(9, 7)).
             get_figure().savefig(weight_pathway, dpi=400))

            #Making the DAI Score plot and saving the file
            (plot_df['DAI_Score'].
             plot(title="DAI Score", xlabel="Days", xticks=range(1,days_recorded+1,1), ylabel="DAI Score", yticks=range(1, 6, 1), figsize=(9,7)).
             get_figure().savefig(dai_pathway, dpi=400))

            # Making the Feces Score plot and saving the file
            (plot_df['Feces'].
             plot(title="Feces Score", xlabel="Days", xticks=range(1, days_recorded + 1, 1), ylabel="Feces Score", yticks=range(1, 6, 1), figsize=(9, 7)).
             get_figure().savefig(feces_pathway, dpi=400))

            # Making the Blood Score plot and saving the file
            (plot_df['Blood'].
             plot(title="Blood Score", xlabel="Days", xticks=range(1, days_recorded + 1, 1), ylabel="Blood Score", yticks=range(1, 6, 1), figsize=(9, 7)).
             get_figure().savefig(blood_pathway, dpi=400))

        # If there is not an experiment object, showing an error
        else:
            sg.popup_error("Experiment information has not being saved yet")

# Handling the continuing with a previously existing experiment

    # Re-opening a saved experiment to continue
    if event == '-Continue-':
        # Obtaining the folder location from user
        recovery_path = sg.popup_get_folder('Please choose experiment to open')

        #If user hits cancel close popup and return to home window

        if recovery_path is not None:
            # Checking if the space was left empty or that the info provided is a valid directory
            if recovery_path != "" and os.path.isdir(recovery_path):
                # In case the user choose the experiment folder rather than the overall
                # Normalizing to the overall experiment folder
                recovery_path = re.sub('(/Experiment$)', "", recovery_path)
                recovery_path = os.path.join(recovery_path, 'Experiment')

                # Getting all the files in the Experiment folder
                folder_files = os.listdir(recovery_path)

                # Keeping only the pickle file in case more files are in the folder
                pickle_file = [x for x in folder_files if re.search('(pkl$)', x)]

                # Canceling and preventing the opening if more than 1 pickle file is found

                if len(pickle_file) > 1 or len(pickle_file) == 0:
                    if len(pickle_file) == 0:
                        sg.popup_error("No file was found in the Experiment Folder.\\n Was the file Removed or Deleted?")
                    else:
                        sg.popup_error("More than 1 pkl file detected. Remove all the extra files and try again")
                else:
                    # Remaking the variable of folder name to save the file with the same name when user hits "Save"
                    # Calling pickle_file[0] directly as there should only be one .pkl file in that folder
                    experiment_folder_name = pickle_file[0].strip('.pkl')

                    # Making the pathway to load the file
                    pickle_file = os.path.join(recovery_path, pickle_file[0])

                    # Opening the pickle file
                    with open(pickle_file, 'rb') as file:
                        experiment_info = pickle.load(file)

                    # Putting all the values in their respective variable
                    experiment = experiment_info['Experiment']
                    groups = experiment_info['Groups']
                    group_names = experiment_info['Group_names']
                    num_mice = experiment_info['Mice_num']
                    experiment_file_folder = experiment_info['Experiment_folder']
                    experiment_results_folder = experiment_info['Results_folder']
                    day = experiment_info['Day'] + 1

                    # Obtaining the ID information of each mouse
                    eartag_info = {}

                    # Obtaining the mouse picture information
                    picture_info = {}

                    # Checking if there is only one group or many

                    if isinstance(num_mice, int):
                        for group in range(groups):
                            for mouse in range(num_mice):
                                name = f'Group{group + 1}Mouse{mouse + 1}'
                                ID = experiment[name].eartag # Extracting the eartag from mouse class
                                eartag_info[name] = ID # Saving in list to pass to make_eperiment()
                                image = experiment[name].picture # Extracting the picture from mouse class
                                picture_info[name] = image # Saving in list to pass to make_eperiment()

                    else:
                        for group in range(groups):
                            mice = num_mice[group]
                            for mouse in range(mice):
                                name = f'Group{group + 1}Mouse{mouse + 1}'
                                ID = experiment[name].eartag # Extracting the eartag from mouse class
                                eartag_info[name] = ID # Saving in list to pass to make_eperiment()
                                image = experiment[name].picture # Extracting the picture from mouse class
                                print(image)
                                picture_info[name] = image # Saving in list to pass to make_eperiment()

                    print(len(picture_info))

                    for picture in picture_info.values():
                        print(picture)

                    # Closing the intro window
                    window.close()

                    # Making the experiment window
                    plate_layout, weight_keys, feces_keys, blood_keys, note_keys = utils.experiment_maker(groups=groups,
                                                                                                    num_mice=num_mice,
                                                                                                    eartag_info=eartag_info,
                                                                                                    group_names=group_names,
                                                                                                    images_list=picture_info,
                                                                                                    day=day)
                    # Showing the experiment window
                    window = sg.Window(title="DSS Tracker - by RICS", layout=plate_layout)


            else:
                sg.popup_error("Directory Not Found")

    # Handling the Creation of a new User

    # Creating a new User and saving it in the json file of lab members
    if event == '-User-':
        if values['-User-'] == "New User":
            new_user = sg.popup_get_text("Please pick a name")
            current_user = new_user
            # Placing the new value just above "New User"
            lab_members.remove("New User")
            lab_members.append(new_user)
            lab_members.append("New User")

            # Making the dictionary and saving the json again with new user
            lab_members_dict = {'Users': lab_members}
            f = open("users_list.json", "w")
            json.dump(lab_members_dict, f)
            f.close()

            return_layout = utils.intro_layout(lab_members=lab_members, current_user=current_user)

            window.close()

            window = sg.Window(title="DSS Tracker - by RICS", layout=return_layout)
