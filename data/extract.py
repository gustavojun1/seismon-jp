from HinetPy import Client, win32
from datetime import datetime, timedelta
import os 
from typing_extensions import Literal

def createTargetDir(project_root: str, data_type: Literal["continuous", "event"], request_timestamp: str):

    os.chdir(project_root)

    # the name of the target dir is the date of the extraction request
    # the final path is: "project_root/data/[data_type]_data/[date_of_request]"
    target_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        data_type + "_data",
        request_timestamp
    )
    os.makedirs(target_dir)
    os.chdir(target_dir)

    return target_dir

def createCntMetadataFile(request_timestamp, start_time, downloaded_event_list, not_downloaded_event_list, max_span = 0, name = "info.txt"):

    with open(name, "w") as f:

        f.write("Request Timestamp: " + str(request_timestamp) + "\n")
        
        total_downloaded_minutes = 0
        f.write("Downloaded events:\n")
        for de in downloaded_event_list:
            total_downloaded_minutes += de[1]
            f.write(f"From {de[0]} to {de[0] + timedelta(de[1])}")

        f.write("Not downloaded events:\n")
        for nde in not_downloaded_event_list:
            f.write(f"From {nde[0]} to {nde[0] + timedelta(nde[1])}")

        f.write("Start Time: " + str(start_time) + "\n")

        f.write("Total Downloaded Time Span: " + str(total_downloaded_minutes) + (" minute" if total_downloaded_minutes == 1 else " minutes") + "\n")

        if max_span > 0:
            f.write("Sub-request Max Span: " + str(max_span) + (" minute" if max_span == 1 else " minutes") + "\n")

def createEvtMetadataFile(request_timestamp, start_time, span, name = "info.txt"):
    with open(name, "w") as f:

        f.write(f"Request Timestamp: {str(request_timestamp)}\n")

        f.write(f"Start Time: {start_time}\n")

        f.write(f"Span: {span}\n")

        f.write(f"End Time: {start_time + timedelta(span)}\n")

# D format is the data format that HiNet uses to name the download folder and is basically D + date in question
# ex.: D20120101000394_20
def getDateFromDFormat(d_format_string):
    try:
        date = d_format_string[1:15]
        parsed_date = datetime.strptime(date, "%Y%m%d%H%M%S")
        return parsed_date
    except ValueError:
        raise ValueError(f"Invalid date string format: {date}")

def cntExtract(
    project_root: str,
    events_path_list,
    client: Client,
    starttime: datetime,
    span,
    max_span=5):

    request_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    createTargetDir(project_root, "continuous", request_timestamp)

    events_path_list.sort()
    prev_event_timestamp = starttime - timedelta(hours = 2 + 1)

    print("Continuous data download starting...")

    donwloaded_events_list = []
    not_donwloaded_events_list = []

    # To not overload the network, the continuous data downloaded only occurs in the two 2 previous hours (time period considered to have relevant information for the prediction) before each event.
    for event in events_path_list:

        event_timestamp = None

        with open(event, "r", encoding="shift_jis") as file:
            for line in file:
                if "ORIGIN_JST" in line:
                    event_timestamp = datetime.strptime(line.split(":", maxsplit=1)[1].strip(), "%Y/%m/%d %H:%M:%S.%f")
                    print(f"Event timestamp: {event_timestamp}")

        event_starttime = event_timestamp - timedelta(hours=2)
        event_relevant_span = 120

        # Guarantee it does not get data before starttime
        if event_starttime < starttime:
            event_starttime = starttime
            event_relevant_span  -= (starttime - event_starttime).total_seconds() / 60

        # Prevents downloading data from the same time period twice
        if event_starttime < prev_event_timestamp:
            event_starttime = prev_event_timestamp

        print(f"Downloading data from {event_starttime} to {event_starttime + timedelta(minutes=event_relevant_span)}")

        # data retrival
        # network code is 0101 for HiNet and 0103 for F-net
        data, ctable = client.get_continuous_waveform("0103", event_starttime, event_relevant_span, max_span, threads=8, cleanup=False)

        if data is not None and ctable is not None:
            donwloaded_events_list.append([event_starttime, event_relevant_span])
        else:
            not_donwloaded_events_list.append([event_starttime, event_relevant_span])

    createCntMetadataFile(request_timestamp, starttime, donwloaded_events_list, not_donwloaded_events_list, max_span)

    # data conversion (WIN32 -> SAC)
    win32.extract_sac(data, ctable) 
    win32.extract_sacpz(ctable)

    # go back to root
    os.chdir(project_root)

def evtExtract(
    project_root: str,
    client: Client,
    span,
    starttime,
    min_magnitude: float,
    max_magnitude = 9.9,
    region = 0):

    request_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    target_dir = createTargetDir(project_root, "event", request_timestamp)

    endtime = starttime + timedelta(minutes=span)

    print("Event download starting...")

    # data retrival
    events = client.get_event_waveform(
        starttime,
        endtime,
        region,
        min_magnitude,
        max_magnitude
    )

    createEvtMetadataFile(request_timestamp, starttime, span)

    # list of paths to each event to guide the continuous extraction
    events_path_list = []

    print("Extracting events files..")

    for event in os.listdir("."):
        if os.path.isdir(event):
            events_path_list.append(os.path.join(target_dir, event, f"{event}.txt"))
            os.chdir(event)
            data = event + ".evt"
            ctable = event + ".ch"
            win32.extract_sac(data, ctable)
            os.chdir("..")

    # go back to root
    os.chdir(project_root)

    return events_path_list