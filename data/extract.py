from HinetPy import Client, win32
from datetime import datetime, timedelta
import os 
from typing_extensions import Literal

def createTargetDir(project_root: str, data_type: Literal["continuous", "event"], request_timestamp: str):

    os.chdir(project_root)

    # the name of the target dir is the date of the extraction request
    # the final path is: "project/data/continuous_data/[date_of_request]"
    target_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        data_type + "_data",
        request_timestamp
    )
    os.makedirs(target_dir)
    os.chdir(target_dir)

    return target_dir

def createMetadataFile(request_timestamp, start_time, span, max_span = 0, end_time: bool = True, name = "info.txt"):

    with open(name, "w") as f:
        f.write("Request Timestamp: " + str(request_timestamp) + "\n")
        f.write("Start Time: " + str(start_time) + "\n")
        if end_time:
            f.write("End Time: " + str(start_time + timedelta(minutes=span)) + "\n")
        f.write("Time Span: " + str(span) + (" minute" if span == 1 else " minutes") + "\n")
        if max_span > 0:
            f.write("Sub-request Max Span: " + str(max_span) + (" minute" if span == 1 else " minutes") + "\n")

def cntExtract(
    project_root: str,
    client: Client,
    starttime: datetime,
    span,
    max_span=5):

    request_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    createTargetDir(project_root, "continuous", request_timestamp)

    # data retrival
    # network code is 0101 for HiNet and 0103 for F-net
    data, ctable = client.get_continuous_waveform("0103", starttime, span, max_span, threads=8, cleanup=False)

    createMetadataFile(request_timestamp, starttime, span, max_span)

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
    target_dir = os.path.join(target_dir, )

    endtime = starttime + timedelta(minutes=span)
    # data retrival
    events = client.get_event_waveform(
        starttime,
        endtime,
        region,
        min_magnitude,
        max_magnitude
    )

    createMetadataFile(request_timestamp, starttime, span)

    # list of paths to each event to guide the continuous extraction
    events_path_list = []

    for event in os.listdir("."):
        print(os.getcwd())
        if os.path.isdir(event):
            events_path_list.append(os.path.join(os.getcwd,event))
            os.chdir(event)
            data = event + ".evt"
            ctable = event + ".ch"
            win32.extract_sac(data, ctable)
            os.chdir("..")
        # break # for extracting 1 event only for now

    # go back to root
    os.chdir(project_root)

    return events_path_list