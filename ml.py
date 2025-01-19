import os
import json
import obspy
import numpy as np

def evtDataToJSON(base_path):
    os.chdir(base_path)
    earthquake_list = {}
    for dir in os.listdir("."):
        if os.path.isdir(dir):
            os.chdir(dir)
            for file_name in os.listdir("."):
                if file_name.endswith(".txt"):
                    with open(file_name, "r", encoding="shift_jis") as file:
                        evt_data = {}
                        for line in file:
                            key, value = map(str.strip, line.split(":", 1))
                            evt_data[key] = value
                        earthquake_list[file_name] = evt_data

            os.chdir(base_path) 

    output_file = "earthquake_data.json"
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(earthquake_list, json_file, ensure_ascii=False, indent=4)

    print(f"Earthquake data saved to {output_file}")
    return output_file

def evtResultantVectorByStation(event_dir_path):
    files_only = [f for f in os.listdir(event_dir_path) if os.path.isfile(os.path.join(event_dir_path, f))]
    magnitude_by_station = {}
    for f in files_only:
        if f.endswith(".SAC"):
            current_file = obspy.read(os.path.join(event_dir_path, f), debug_headers=True)
            station = f.split(".")[-3]

            # trace for a single direction of a single station for this event
            for trace in current_file:
                if station not in magnitude_by_station:
                    magnitude_by_station[station] = np.zeros(len(trace.data))
                for i, v in enumerate(trace.data):
                    magnitude_by_station[station][i] += v**2
    for key in magnitude_by_station:
        magnitude_by_station[key] = np.sqrt(magnitude_by_station[key])
    return magnitude_by_station

if __name__ == "__main__":
    # metadata
    base_path = "/home/gjnagatomo/seismon-jp/data/event_data/2025-01-15_14-22-35/"
    json_file = evtDataToJSON(base_path)
    os.chdir(base_path)

    with open(json_file, "r") as file:
        data = json.load(file)
    
    # data of the D20120101000394_20 event
    events = []
    for dir in os.listdir(base_path):
        events.append(evtResultantVectorByStation(os.path.join(base_path, dir)))
    print(events)