# Making the class Mouse to save the information of each mouse in the experiment
from datetime import datetime
import numpy as np
import pandas as pd
import calendar

class Mouse:

    # When creating a Mouse Class, the first day will always be day 0
    # If omitted, the class will infer that is the first, or following day to the max day value it has
    # The values required are the weight, feces score, blood score, mouse number, and the group it belongs
    # Group and mouse number will be feed by the program when calling the keys
    def __init__(self, dss, weight, feces, blood, group, mouse_name, gender, eartag, dss_percentage):

        day = 0

        #Making the keys for each dictionary
        day_title = f'Day {day}'
        weight_title = f'Day {day} Weight'
        feces_title = f'Day {day} Feces'
        blood_title = f'Day {day} Blood'
        weight_loss_title = f'Day {day} Weight Loss'
        weight_loss_score_title = f'Day {day} Weight Loss Score'
        weight_percentage_title = f'Day {day} Weight Percentage'
        dai_title = f'Day {day} DAI'
        dss_title = f'Day {day} DSS'


        # For future weight comparison, isolating the first weight on each mouse
        self.first_weight = weight

        # Saving the information of the Mouse ID, Group Name and the DSS% of the experiment
        self.group = group
        self.mouse_name = mouse_name
        self.dss_percentage = dss_percentage

        # Adding the picture value
        self.picture = "0_loss.png"

        # Getting the percentage of weight loss. This should be 1 on the first day
        loss = weight / self.first_weight

        # Checking the amount of weight loss and choosing the respective score value
        # Because is the first day, the score is always 0

        score = 0

        # Creating the dictionaries to hold the information
        self.day = {day_title: day}
        # self.date = {date_title : date} #Omitted by the time being but could be included
        self.weight = {weight_title: weight}
        self.feces = {feces_title: feces}
        self.blood = {blood_title: blood}
        self.weight_loss = {weight_loss_title: loss}
        self.weight_loss_score = {weight_loss_score_title: score}
        self.weight_percentage = {weight_percentage_title: loss * 100}
        self.dss = {dss_title: dss}

        if gender == "":
            self.gender = "No Gender"
        else:
            self.gender = gender

        if eartag == "":
            self.eartag = "No Mouse ID"
        else:
            self.eartag = eartag

        # Making the DAI Score and saving the DAI
        # Verifying that the values provided are integers or floats
        # The verification is done outside of the class by function "make_none()"
        if feces is not None and blood is not None:
            dai = (score + feces + blood) / 3
            self.dai_score = {dai_title: dai}
        else:
            self.dai_score = {dai_title: np.nan}  # Using numpy NaN to prevent errors when getting mean values for plots

        # Making a warning variable to read in case a warning needs to be provided to the user
        self.warning = "NA"

        # Making a note section in case the user wants to add more information

        # Getting the date the note was created to use it as the dictionary key
        date = datetime.now()
        weekday = calendar.day_name[date.weekday()]
        date = date.strftime("%m/%d/%Y")  # adjusted to US format
        full_date = f'{date}, {weekday}'

        self.notes = {'Initial note': f'This is {mouse_name} from {group}',
                      'Experiment Started': full_date,
                      'Mouse Gender': self.gender,
                      'Mouse Eartag': self.eartag,
                      'Experiment DSS%': dss_percentage}


    # Methods Section of the Class Mouse
    # As notes are not created in everytime, a unique method was created
    def add_notes(self, notes):
        # Getting the date the note was created to use it as the dictionary key
        date = datetime.now()
        weekday = calendar.day_name[date.weekday()]
        date = date.strftime("%m/%d/%Y")  # adjusted to US format
        full_date = f'{date}, {weekday}'

        #Saving in the note section of the class
        self.notes[full_date] = notes

    # Method to add a new day to the Mouse class
    # No need to add the group information or day
    # User can include the day
    # If user forgets to add day, it will infer that it is the following day
    def add_day(self, dss, weight, feces, blood):
        # Checking if user provided day information
        new_day = max(self.day.values()) + 1

        # Making the keys to save the information
        day_title = f'Day {new_day}'
        weight_title = f'Day {new_day} Weight'
        feces_title = f'Day {new_day} Feces'
        blood_title = f'Day {new_day} Blood'
        weight_loss_title = f'Day {new_day} Weight Loss'
        weight_loss_score_title = f'Day {new_day} Weight Loss Score'
        weight_percentage_title = f'Day {new_day} Weight Percentage'
        dai_title = f'Day {new_day} DAI'
        dss_title = f'Day {new_day} DSS'

        # A weight of 0 means that the mouse died or was removed from the experiment
        # Checking that the weight was registered to save all the information of the day
        if weight != 0:
            # Getting the percentage of weight loss
            loss = weight / self.first_weight

            # Checking the amount of weight loss and choosing the respective score value
            if loss >= 0.99:
                score = 0
            elif loss >= 0.95:
                score = 1
                self.picture = "5_loss.png"
            elif loss >= 0.90:
                score = 2
                self.picture = "10_loss.png"
            elif loss >= 0.80:
                score = 3
                self.picture = "15_loss.png"
            else:
                score = 4

            # Doing DAI scoring
            # Verifying that the values provided are integers or floats
            # The verification is done outside of the class by function "make_none()"
            if feces is not None and blood is not None:
                dai = (score + feces + blood) / 3
                self.dai_score[dai_title] = dai
            else:
                self.dai_score[dai_title] = np.nan  # Using numpy NaN to being removed when making the plots

            # Adding all the values to the object in their respective dictionaries
            self.day[day_title] = new_day
            self.weight[weight_title] = weight
            self.feces[feces_title] = feces
            self.blood[blood_title] = blood
            self.weight_loss[weight_loss_title] = loss
            self.weight_loss_score[weight_loss_score_title] = score
            self.weight_percentage[weight_percentage_title] = loss * 100
            self.dss[dss_title] = dss

            # Checking if the warning variable should de changed to report to the user.
            if loss <= 0.80:
                self.warning = "Red"
            elif loss <= 0.82:
                self.warning = "Yellow"

        else:
            # If mouse weight is 0, Mouse is considered Death.
            # All values are registered as NaN for easily removal when getting the mean at the end
            self.day[day_title] = new_day
            self.weight[weight_title] = np.nan
            self.feces[feces_title] = np.nan
            self.blood[blood_title] = np.nan
            self.weight_loss[weight_loss_title] = np.nan
            self.weight_loss_score[weight_loss_score_title] = np.nan
            self.weight_percentage[weight_percentage_title] = np.nan
            self.dai_score[dai_title] = np.nan
            self.dss[dss_title] = dss

            # Changing the warning to "Death" the first day weight is 0
            # To register the day the mouse was removed from the experiment
            if self.warning != "Death":  # If statement to prevent multiple registers in the note section
                date = datetime.now()
                weekday = calendar.day_name[date.weekday()]
                date = date.strftime("%m/%d/%Y")  # adjusted to US format
                full_date = f'{date}, {weekday}'
                self.notes[full_date] = f'The {self.mouse_name} from {self.group} register as death on {full_date}'
                self.warning = "Death"

    # Method to extract the information as a dataframe for plotting and csv saving
    def export_data(self):
        dataframe = pd.DataFrame({'Day': self.day.values(),
                                  'Weight': self.weight.values(),
                                  'Feces': self.feces.values(),
                                  'Blood': self.blood.values(),
                                  'Weight_Loss': self.weight_loss.values(),
                                  'Weight_Loss_Score': self.weight_loss_score.values(),
                                  'Weight_Percentage': self.weight_percentage.values(),
                                  'DAI_Score': self.dai_score.values(),
                                  'Group': self.group,
                                  'Mouse': self.mouse_name,
                                  'Gender': self.gender,
                                  'Eartag': self.eartag,
                                  'DSS_Water': self.dss.values()}
                                 ,index=self.day.keys())
        return dataframe

    # As notes are of different length per mouse, method to extract the notes by themselves for individual saving
    def export_notes(self):
        dataframe = pd.DataFrame({'Notes':self.notes.values()}, index=self.notes.keys())
        name = f'{self.group}_{self.mouse_name}_Notes'
        return dataframe, name

# End of Class Mouse

if __name__ == '__main__':
    x = Mouse(2,12,0,0,1,1,"Female",1235,2.5)
    x.add_day(dss ="DSS", weight=2,blood= 0,feces=0)
    x.add_notes("test_NOTE")
    x.export_data()
    x.export_notes()

    print(x.picture)