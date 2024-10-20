import json
import pandas as pd
import math
import os
from glob import glob
from params import *



'''
Core methods
'''

# Calculate the average interaction time for keyboard and mouse events within a test
def calculate_average_interaction_time(data):
    key_events = data['key_events']
    mouse_events = data['mouse_events']

    # Initialize lists for dwell, flight, and trajectory times
    dwell_times = []
    flight_times = []
    traj_distances = []

    # Extract key event times
    for event in key_events:
        if event['Event'] == 'pressed':
            # Find the corresponding 'release' event for dwell time calculation
            corresponding_release = next((e for e in key_events if e['Key'] == event['Key'] and e['Event'] == 'released'), None)
            if corresponding_release:
                dwell_times.append(corresponding_release['Epoch'] - event['Epoch'])

        if event['Event'] == 'released':
            # Find the next 'press' event for flight time calculation
            next_press = next((e for e in key_events if e['Key'] != event['Key'] and e['Event'] == 'pressed' and e['Epoch'] > event['Epoch']), None)
            if next_press:
                flight_times.append(next_press['Epoch'] - event['Epoch'])

    # Extract mouse event times
    for movement in mouse_events:
        traj_distances.append(movement['Coordinates'])  # This assumes coordinates are movement distances

    # Compute averages
    dwell_avg = sum(dwell_times) / len(dwell_times) if dwell_times else 0
    flight_avg = sum(flight_times) / len(flight_times) if flight_times else 0
    traj_avg = sum(traj_distances) / len(traj_distances) if traj_distances else 0

    # Return as DataFrame
    return pd.DataFrame({'dwell_avg': [dwell_avg], 'flight_avg': [flight_avg], 'traj_avg': [traj_avg]})
#///////////////
# CONVERTS DICTIONARIES TAKEN FROM .JSON FILES INTO DATAFRAMES FOR THE KEY EVENTS
def dict_key_conversion(data):
    temp_df = pd.DataFrame(columns=['test_number', 'dwell_time', 'flight_time', 'key_pressed'])
    temp_flight_df = pd.DataFrame(columns=['test_number', 'flight_time', 'key_released'])

    temp_df_count = 0 # indicates which row of the df the next row of data should be appeneded into
    temp_flight_df_count = 0

    for i in range(1, 11): # loops through each of the tests in true_data
        k_data = data['test_'+str(i)]['key_events']
        # removes tabs from the data, as kivy, which is the library used for data collection, doesn't register tab releases, only presses
        tabless_k_data = []
        for k in k_data:
            if k['Key'] != 'tab':
                tabless_k_data.append(k)

        count = 0 #counter for how many iterations into the for loop it is
        f_count = 0 #counter for how many iterations into the loop the flight section has done
        prev_key_press = 0
        prev_key_release = 0
        for j in tabless_k_data:
            if j['Event'] == 'pressed': # THIS EXECUTES TO FIND THE DWELL TIME
                flight_impute = 0 # imputes flight time as 0 for now, as there are instances of key presses not having releases at the end of the test
                key_id = j['Key'] # this is what the actual key that is being pressed/released is
                key_press_time = j['Epoch'] # the epoch time of the key press
                key_release = False # is true when the release of the key has been found
                cont_count = 1 # keeps track of counting from the current key press, as it loops from

                while key_release == False: # continues
                    c = cont_count + count
                    start_row = tabless_k_data[count]
                    next_row = tabless_k_data[c]
                    # executes if the row is the release of the key that was pressed, and exits the while loop
                    if next_row['Key'] == key_id and next_row['Event'] == 'released':
                        key_release_time = next_row['Epoch']
                        dwell_time = float(key_release_time) - float(key_press_time)
                        key_release = True
                    # executes if the next row is a press event for a different key
                    elif next_row['Key'] != key_id and next_row['Event'] == 'pressed':
                        cont_count += 1
                    elif next_row['Key'] != key_id and next_row['Event'] == 'released':
                        cont_count += 1
                    else:
                        key_release = True
                        dwell_time = 0
                        key_release_time = start_row['Epoch']

                temp_df.loc[temp_df_count] = [i, dwell_time, flight_impute, key_id]

                prev_key_press = key_press_time
                prev_key_release = key_release_time
                temp_df_count += 1

            count += 1

            if j['Event'] == 'released': # THIS EXECUTES TO FIND THE FLIGHT TIME
                key_id = j['Key']
                f_cont_count = 1
                flight_time = []
                flight_found = False
                while flight_found == False:
                    f_c = f_count + f_cont_count
                    if f_c < len(tabless_k_data):
                        next_row = tabless_k_data[f_c]
                        if next_row['Event'] == 'pressed' and next_row['Key'] != key_id:
                            flight_time = float(next_row['Epoch']) - float(j['Epoch'])
                            temp_flight_df.loc[temp_flight_df_count] = [i, flight_time, key_id]
                            temp_flight_df_count += 1
                            flight_found = True
                        f_cont_count += 1
                    else:
                        flight_found = True
            f_count += 1

    # Now merges the flight time df with the rest of the features
    for i in range(1, 11):
        fh_count = 0
        flight_hold = []
        for j in temp_flight_df.index:
            if temp_flight_df.at[j, 'test_number'] == i:
                flight_hold.append(temp_flight_df.at[j, 'flight_time'])
        fh_count = 0

        for j in temp_df.index:
            if temp_df.at[j, 'test_number'] == i and fh_count < len(flight_hold):
                temp_df.at[j, 'flight_time'] = flight_hold[fh_count]
                fh_count += 1

    true_k_df = temp_df
    return true_k_df
#\\\\\\\\\\\\\\\\
# CONVERTS DICTIONARIES TAKEN FROM .JSON FILES INTO DATAFRAMES FOR THE MOUSE EVENTS
def get_distance(a, b): # method used to calculate distance between two coordinates
    distance = math.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2))
    return distance

def dict_mouse_conversion(data):
    m_df = pd.DataFrame(columns = ['test_number', 'movement_id', 'trajectory', 'single_coor'])
    row_count = 0
    for i in range(1, 11):
        m_data = data['test_'+str(i)]['mouse_events']
        m_movements = []
        for j in m_data[:len(m_data)-1]:
            if j['Event'] == 'movement':
                m_movements.append(j)

        # creates dictionary that passes all the movement coordinates to the each movement ID in the test
        movement_coor_dict = {}
        for j in m_movements:
            movement_coor_dict[j['Movement ID']] = []
        for j in m_movements:
            movement_coor_dict[j['Movement ID']].append(j['Coordinates'])

        # calculates the overall trajectory length for each of the movement IDs
        for j in movement_coor_dict:
            coor_list = movement_coor_dict[j]
            motion_start = False
            trajectory = 0
            if len(coor_list) > 1:
                trajectory_list = []
                if motion_start == True:
                    motion_start = False
                else:
                    count = 0
                    for k in coor_list:
                        trajectory_list.append(get_distance(coor_list[count-1], coor_list[count]))
                        count += 1
                    movement_id = j
                    trajectory = sum(trajectory_list)
                    single_coor = False
            else:
                movement_id = 1
                trajectory_list = [0]
                trajectory = 0
                single_coor = False
            m_df.loc[row_count] = [i, movement_id, trajectory, single_coor]
            row_count += 1
    m_df = m_df.sort_values(by=['test_number', 'movement_id'])

    for j in m_df['single_coor'].tolist():
        if j == True:
            m_df = movement_df.drop[count]
        count += 1
    m_df = m_df.reset_index(drop=True)
    return m_df
#\\\\\\\\\\\\\\\\\\
# determine wether the day is weekday or weekend
# determine wether the day is weekday or weekend
def dict_days(data):
    temp_days = []

    for i in range(1, 11):
        k_data = data['test_' + str(i)]['key_events']
        for row in k_data:
            temp_days.append({'id': i, 'date': row['Timestamp']})

    temp_days_df = pd.DataFrame(temp_days, columns=['id', 'date'])

    # Extracting the date
    temp_days_df['shorted_date'] = pd.to_datetime(temp_days_df['date']).dt.date

    # Getting the day name
    temp_days_df['day'] = pd.to_datetime(temp_days_df['shorted_date']).dt.strftime("%A")

    # Calculating the day type (0 for weekdays, 1 for weekends)
    temp_days_df['day_type'] = pd.to_datetime(temp_days_df['shorted_date']).dt.dayofweek // 5

    return temp_days_df
#\\\\\\\\\\\\\\\\\\\\\\
# GENERATES FEATURES FOR EACH TEST FROM THE DFS GENERATED IN THE PREVIOUS TWO CELLS
def feature_gen(k_data, m_data, d_data):
    #columns = ['dwell_avg', 'flight_avg', 'traj_avg']
    columns = ['dwell_avg', 'flight_avg', 'traj_avg', 'keyboard_avg', 'mouse_avg', 'day_type', 'freq_mouse', 'freq_key']

    df = pd.DataFrame(columns=columns)

    # for loop calculates average value for the dwell time, flight time and trajectory for each test
    for i in range(1, 11):
        dwell_list = []
        flight_list = []
        traj_list = []

        # Store total interaction times for keyboard and mouse
        total_keyboard_time = 0
        total_mouse_time = 0
        num_keyboard_events = 0
        num_mouse_events = 0

        for j in k_data.index:
            if k_data.at[j, 'test_number'] == i:
                dwell_list.append(k_data.at[j, 'dwell_time'])
                flight_list.append(k_data.at[j, 'flight_time'])
                total_keyboard_time += k_data.at[j, 'dwell_time'] + k_data.at[j, 'flight_time']
                num_keyboard_events += 1

        for j in m_data.index:
            if m_data.at[j, 'test_number'] == i:
                traj_list.append(m_data.at[j, 'trajectory'])
                total_mouse_time += m_data.at[j, 'trajectory']  # Ensure this represents the correct time
                num_mouse_events += 1


        dwell_list = [j for j in dwell_list if j != 0]
        flight_list = [j for j in flight_list if j != 0]
        traj_list = [j for j in traj_list if j != 0]

        #calculate the frequency of keyboard, mouse
        freq_mouse = len(traj_list)
        freq_key = len(dwell_list)

        dwell_avg = sum(dwell_list)/len(dwell_list)
        flight_avg = sum(flight_list)/len(dwell_list)
        traj_avg = sum(traj_list)/len(traj_list)
        day_type = d_data.groupby('id')['day_type'].agg(lambda x: x.mode().iloc[0]).loc[i]

        # Calculate average interaction time for keyboard and mouse events
        keyboard_avg = total_keyboard_time / num_keyboard_events
        mouse_avg = total_mouse_time / num_mouse_events
        agg_data = [dwell_avg, flight_avg, traj_avg, keyboard_avg, mouse_avg, day_type, freq_mouse, freq_key]

        df.loc[i] = agg_data
    return df
#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'''
EXPERIMENT AND RESULT
'''

# Temporary list storage for visualisation
# RUNS THE MODEL ON EACH OF THE USER'S DATA
def extract_data():

    for file_path in glob.glob(LOCAL_DATA_PATH, 'original_data', '*.json'):
        # stores each of the true data as dictionaries
        with open(file_path, 'r') as f:
            data = json.load(f)
            user_details = data['details'] # stores the fabricated card details entered for the user
            true_data = data['true_data'] # stores the true data of the .json file
            false_data = data['false_data']

            #----------------------------------
            true_k_df = dict_key_conversion(true_data) # gets the key events from the json files
            false_k_df = dict_key_conversion(false_data)
            #----------------------------------
            true_m_df = dict_mouse_conversion(true_data) # gets the mouse events from the json files
            false_m_df = dict_mouse_conversion(false_data)
            #----------------------------------
            true_d_df = dict_days(true_data) # gets the mouse events from the json files
            false_d_df = dict_days(false_data)
            #----------------------------------
            true_df = feature_gen(true_k_df, true_m_df, true_d_df) # gets the average dwell, flight and traj for each test
            false_df = feature_gen(false_k_df, false_m_df, false_d_df)
            true_df['label'] = 1 # adds true or false label to the df for the ML algorithm, 1 == true, 0 == false
            false_df['label'] = 0
            final_df = pd.concat([true_df, false_df])
            final_df = final_df.reset_index(drop=True) # final df that will be used within the ML algorithm
            #----------------------------------

            # export as csv files
            output_folder = 'extracted_features'
            output_folder_path = os.path.join(LOCAL_DATA_PATH, output_folder)
            if not os.path.exists(output_folder_path):
                os.makedirs(output_folder_path)

            file_name = os.path.basename(file_path).replace('.json', '.csv')
            file_path = os.path.join(output_folder_path, file_name)
            final_df.to_csv(file_path, index=False)

    return output_folder_path
