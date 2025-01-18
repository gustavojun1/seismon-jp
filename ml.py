import os
import json

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

if __name__ == "__main__":
    base_path = "/home/gjnagatomo/seismon-jp/data/event_data/2025-01-15_14-22-35/"
    evtDataToJSON(base_path)
    os.chdir(base_path)
