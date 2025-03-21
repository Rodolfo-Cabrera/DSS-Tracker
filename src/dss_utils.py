# Calling the required packages
import re
import os
import pickle
from datetime import datetime
import FreeSimpleGUI as sg


# Function to create all the key labels used by PySimpleGUI based on the amount of groups and mice
def key_maker(groups, num_mice, first = False):
    # Making the list where the keys for each variable are going to be saved
    weight_keys = []
    feces_keys = []
    blood_keys = []
    notes_keys = []
    gender_keys = []
    eartag_keys = []
    # In case there is only 1 group in the experiment only 1 num_mice will be provided, rather than the list
    # Making an If statement to loop around a 1 group only experiment
    if isinstance(num_mice, int):
        for group in range(groups):
            for mouse in range(num_mice):
                #Saving all the keys for each mice one group at a time
                weight_keys.append(f'-Group{group + 1}Weight{mouse + 1}-')
                feces_keys.append(f'-Group{group + 1}Feces{mouse + 1}-')
                blood_keys.append(f'-Group{group + 1}Blood{mouse + 1}-')
                notes_keys.append(f'-Group{group + 1}Notes{mouse + 1}-')
                gender_keys.append(f'-Group{group + 1}Gender{mouse + 1}-')
                eartag_keys.append(f'-Group{group + 1}Eartag{mouse + 1}-')
    else:  # Doing list of keys when more than one value for the num_mice was provided
        for group in range(groups):
            mice = num_mice[group]
            for mouse in range(mice):
                # Saving all the keys for each mice one group at a time
                weight_keys.append(f'-Group{group + 1}Weight{mouse + 1}-')
                feces_keys.append(f'-Group{group + 1}Feces{mouse + 1}-')
                blood_keys.append(f'-Group{group + 1}Blood{mouse + 1}-')
                notes_keys.append(f'-Group{group + 1}Notes{mouse + 1}-')
                gender_keys.append(f'-Group{group + 1}Gender{mouse + 1}-')
                eartag_keys.append(f'-Group{group + 1}Eartag{mouse + 1}-')

    if first:
        return weight_keys, feces_keys, blood_keys, notes_keys, gender_keys, eartag_keys
    else:
        return weight_keys, feces_keys, blood_keys, notes_keys

# Making the start window of the program
def intro_layout(lab_members, current_user):

    intro_layout = [
        [sg.Push(), sg.Text('Welcome to DSS Tracker'), sg.Push()],
        [sg.HorizontalSeparator()],
        [sg.Text("Please Choose User:"), sg.Combo(lab_members,default_value=current_user, k="-User-",
                                                  change_submits=True, readonly=True)],
        [sg.HorizontalSeparator()],
        [sg.Push(), sg.Text("Start or Continue an Experiment"), sg.Push()],
        [sg.Push(), sg.Button('New Experiment', k='-NewExp-'), sg.Push()],
        [sg.Push(), sg.Button('Open Previous Experiment', k='-Continue-'), sg.Push()],
        [sg.Push(),sg.Button('Quit', k='-Quit-')]
    ]
    return intro_layout

# Function to create the GUI with the information of each mice
# Each group will be a different tab
def experiment_maker(groups, num_mice, day, first=False, eartag_info=None, group_names=None, images_list = None):
    if first:
        # Getting all the keys needed to make the GUI and get all values
        weight_keys, feces_keys, blood_keys, note_keys, gender_keys, eartag_keys = key_maker(groups=groups, num_mice=num_mice, first=True)

        # Placing a title on the left side of what value is expected on each cell
        variable_labels = ["Gender", "ID", "Weight", "Feces", "Blood", "Notes", ""] # Empty filler to make a gap for images

        # Object where to save the information of all the tabs
        tabs = []

        # Doing each group tab at a time
        for group in range(groups):
            # Making the pattern to extract the keys only needed for the current group
            pattern = f'-Group{group + 1}'
            # Making the group name to place in the tab title
            name = group_names[group]
            # First column in the GUI will always have the title of the values on the left
            first = [[sg.Text(name)]] + \
                    [[sg.Text(variable_labels[j], font=("Arial Bold", 11), p=((0,0),(0,7)))] for j in range(len(variable_labels))]
            # First is a loop to create multiple instance of sg.Text with each of the labels to be shown at the left
            # Saving the full colum in the object that will hold all the information of the tab
            full_tab_layout = [sg.Column(first, element_justification='left'), sg.VerticalSeparator()]

            # Getting the keys associated with the current group
            weight_keys_to_use = [x for x in weight_keys if re.match(pattern, x)]
            feces_keys_to_use = [x for x in feces_keys if re.match(pattern, x)]
            blood_keys_to_use = [x for x in blood_keys if re.match(pattern, x)]
            note_keys_to_use = [x for x in note_keys if re.match(pattern, x)]
            gender_keys_to_use = [x for x in gender_keys if re.match(pattern, x)]
            eartag_keys_to_use = [x for x in eartag_keys if re.match(pattern, x)]

            # Using one of the keys length to know how many mice we have to create as many cell as required
            num_of_mice = len(weight_keys_to_use)

            # Making a list for each variable with the sg.Input that will hold the user input
            # Placing a different key argument on each sg.Input

            gender_layout = [[sg.Combo(['Female', 'Male'], k=j, s=(7, 1), p=((0, 0), (3, 9)))] for j in
                             gender_keys_to_use]
            eartag_layout = [[sg.Input(k=j, s=(7, 1), p=((0, 0), (0, 9)))] for j in eartag_keys_to_use]
            weight_layout = [[sg.Input(k=j, s=(7, 1), p=((0, 0), (0, 9)))] for j in weight_keys_to_use]
            feces_layout = [[sg.Input(k=j, s=(7, 1), p=((0, 0), (0, 9)))] for j in feces_keys_to_use]
            blood_layout = [[sg.Input(k=j, s=(7, 1), p=((0, 0), (0, 9)))] for j in blood_keys_to_use]
            notes_layout = [[sg.Input(k=j, s=(7, 1), p=((0, 0), (0, 9)))] for j in note_keys_to_use]
            picture_layout = [[sg.Image(filename="0_loss.png", subsample=3)] for j in weight_keys_to_use]

            # With every sg.Input created, looping to make the column of each mice in the group
            for mouse in range(num_of_mice):
                mouse_column_layout = [
                    [sg.Text(f'Mouse {mouse + 1}', p=((0,0),(19,0)) )],
                    gender_layout[mouse],
                    eartag_layout[mouse],
                    weight_layout[mouse],
                    feces_layout[mouse],
                    blood_layout[mouse],
                    notes_layout[mouse],
                    picture_layout[mouse]
                ]
                # Adding the information to the layout holder
                full_tab_layout.append(sg.Column(mouse_column_layout, element_justification="left"))

            # Adding each layout as a tab
            tabs.append(sg.Tab(name, [full_tab_layout]))

        # Making the window layout with a title on top, A section of the day and the buttons to save and export data
        layout = [[sg.Push(), sg.Text(f"DSS Experiment Day {day}"), sg.Push()],
                  [sg.Text("DSS/Water"), sg.Combo(['DSS', 'Water'], k="-DSS-", default_value='DSS'), sg.Push(), sg.Button('Save', k='-Save-'),
                   sg.Button('Export', k='-Generate-')],
                  [sg.HorizontalSeparator()],
                  [sg.TabGroup([tabs])]  # Adding all the tabs in the lower part of the window
                  ]
        # Returning the layout to show and the key information for manipulation in the Event Handling section
        return [layout], weight_keys, feces_keys, blood_keys, note_keys, gender_keys, eartag_keys

    else:


        # Getting all the keys needed to make the GUI and get all values
        weight_keys, feces_keys, blood_keys, note_keys = key_maker(groups=groups, num_mice=num_mice)

        # Placing a title on the left side of what value is expected on each cell
        variable_labels = ["ID", "Weight", "Feces", "Blood", "Notes", ""] # Empty filler to make a gap for images

        # Object where to save the information of all the tabs
        tabs = []

        # Doing each group tab at a time
        for group in range(groups):
            # Making the pattern to extract the keys only needed for the current group
            pattern = f'-Group{group + 1}'
            # Making the group name to place in the tab title
            name = group_names[group]
            # First column in the GUI will always have the title of the values on the left
            first = [[sg.Text(name)]] + \
                    [[sg.Text(variable_labels[j], font=("Arial Bold", 11), p=((0,0),(0,7)))] for j in range(len(variable_labels))]
            # First is a loop to create multiple instance of sg.Text with each of the labels to be shown at the left
            # Saving the full colum in the object that will hold all the information of the tab
            full_tab_layout = [sg.Column(first, element_justification='left'), sg.VerticalSeparator()]

            # Getting the keys associated with the current group
            weight_keys_to_use = [x for x in weight_keys if re.match(pattern, x)]
            feces_keys_to_use = [x for x in feces_keys if re.match(pattern, x)]
            blood_keys_to_use = [x for x in blood_keys if re.match(pattern, x)]
            note_keys_to_use = [x for x in note_keys if re.match(pattern, x)]

            # Using one of the keys length to know how many mice we have to create as many cell as required
            num_of_mice = len(weight_keys_to_use)

            # Making a list for each variable with the sg.Input that will hold the user input
            # Placing a different key argument on each sg.Input
            weight_layout = [[sg.Input(k=j, s=(7, 1), p=((0, 0), (0, 9)))] for j in weight_keys_to_use]
            feces_layout = [[sg.Input(k=j, s=(7, 1), p=((0, 0), (0, 9)))] for j in feces_keys_to_use]
            blood_layout = [[sg.Input(k=j, s=(7, 1), p=((0, 0), (0, 9)))] for j in blood_keys_to_use]
            notes_layout = [[sg.Input(k=j, s=(7, 1), p=((0, 0), (0, 9)))] for j in note_keys_to_use]

            # With every sg.Input created, looping to make the column of each mice in the group
            for mouse in range(num_of_mice):
                mouse_column_layout = [
                    [sg.Text(f'Mouse {mouse + 1}', p=((0, 0), (18, 2)))],
                    [sg.Text(eartag_info[f'Group{group + 1}Mouse{mouse + 1}'], p=((0, 0), (0, 9)))],
                    weight_layout[mouse],
                    feces_layout[mouse],
                    blood_layout[mouse],
                    notes_layout[mouse],
                    [sg.Image(images_list[f'Group{group + 1}Mouse{mouse + 1}'], subsample=3)]
                ]
                # Adding the information to the layout holder
                full_tab_layout.append(sg.Column(mouse_column_layout, element_justification="left"))

            # Adding each layout as a tab
            tabs.append(sg.Tab(name, [full_tab_layout]))

        # Making the window layout with a title on top, A section of the day and the buttons to save and export data
        layout = [[sg.Push(), sg.Text(f"DSS Experiment Day {day}"), sg.Push(),
                   sg.Button("", k="-Egg-", border_width=0, button_color="#64778d")],
                  [sg.Text("DSS/Water"), sg.Combo(['DSS', 'Water'], k="-DSS-", default_value='DSS'), sg.Push(), sg.Button('Save', k='-Save-'),
                   sg.Button('Export', k='-Generate-')],
                  [sg.HorizontalSeparator()],
                  [sg.TabGroup([tabs])]  # Adding all the tabs in the lower part of the window
                  ]
        # Returning the layout to show and the key information for manipulation in the Event Handling section
        return [layout], weight_keys, feces_keys, blood_keys, note_keys


# Function to save the experiment in the folder
def saving_file(experiment, day,
                groups, group_names,num_mice,
                experiment_file_folder,
                experiment_results_folder,
                experiment_folder_name):
    # If no error happened, saving the experiment with the new information added
    # Making a dictionary with all the information required to continue the experiment
    experiment_info = {'Experiment': experiment,  # The experiment itself
                       'Day': day,  # The last day recorded
                       'Groups': groups,  # The amount of groups to re-create the experiment window
                       'Group_names': group_names,  # The name of the Groups
                       'Mice_num': num_mice,  # The amount of mice to re-create the experiment window
                       'Experiment_folder': experiment_file_folder,  # The experiment folder info
                       'Results_folder': experiment_results_folder}  # The results folder info
    # Making the saving pathway
    saving_name = os.path.join(experiment_file_folder, f'{experiment_folder_name}.pkl')
    # Saving the file
    with open(saving_name, 'wb') as handle:
        pickle.dump(experiment_info, handle, protocol=pickle.HIGHEST_PROTOCOL)

# Function to check if a warning needs to be shown to user depending on how much weight the mouse loss
def loss_weight_warning(mouse, name):
    if mouse.warning == "Yellow":
        return sg.popup(f'WARNING: {name} has lost 18% of weight')
    elif mouse.warning == "Red":
        return sg.popup(f'WARNING: {name} has lost 20% of weight. Mouse should be euthanized')
    else:
        return



# As the error in multiple section is the same. Function to improve visualization in the Event/Handling Section
def show_error():
    return sg.popup_error("Enter Non-Zero Numbers without decimals",title="Wrong Value")


# Checking that the value provided is an integer
# For internal use inside make_none() function
def check_integer(list):
    results = []  # Making the list of boolean values to return
    for i in list:  # Looping through every value in the list provided
        try:  # Attempting to make it an integer value
            int(i)
        except ValueError:  # If failed, attempting to make a float value
            try:
                float(i)
            except ValueError:  # If both failed, appending False
                results.append(False)
            else:  # If any test passed, appending True
                results.append(True)
        else:
            results.append(True)
    if all(results):  # Verify that all the elements provided where integers or floats
        # If all passed, returning True
        return True
    else:
        # If at least one did not passed, returning False to show error to user
        return False

# Function to check that a valid value was provided
# As Weight is the only value that could be float, returning float always for weight
def make_none(value, weight = False):
    if weight:  # If the value provided is not for weight returning the float form if check_integer() is True
        if value == "":  # Returning None if the value provided is empty
            return None
        else:
            if check_integer([value]):
                return float(value)
    else:  # If the value provided is not for weight returning the integer form if check_integer() is True
        if value == "":
            return None
        else:
            if check_integer([value]):
                return int(value)
            else:
                return value

# Function to create the folders where to save the experiment
def create_folders(program_folder, current_user):
    # Creating the folders to save the new experiment based on the date of creation
    # Getting the date and make it US format
    date_folder = datetime.now()
    date_folder = date_folder.strftime("%m-%d-%Y")

    # Making the overall name of the experiment
    experiment_folder_name = f'{date_folder} DSS Experiment'

    # Making the pathway to the user and creating a user folder if it does not exist
    user_folder = os.path.join(program_folder, current_user)

    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    # Making the path to mother folder where the experiment pickle file and the results will be saved
    saving_folder = os.path.join(user_folder, experiment_folder_name)

    # Making the path the results and experiment folder inside mother folder
    experiment_file_folder = os.path.join(saving_folder, 'Experiment')
    experiment_results_folder = os.path.join(saving_folder, 'Results')

    # Notes will be saved inside Results in a separate folder as they will be many files
    experiment_results_notes_folder = os.path.join(experiment_results_folder, 'Notes')
    # Checking if folders already exist before creating to prevent os error
    if not os.path.exists(saving_folder):
        os.makedirs(saving_folder)
        os.makedirs(experiment_file_folder)
        os.makedirs(experiment_results_folder)
        os.makedirs(experiment_results_notes_folder)
    return experiment_file_folder,experiment_results_folder,experiment_folder_name

