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

def createMetadataFile(request_timestamp, start_time, span, end_time: bool = True, name = "info.txt"):

    with open(name, "w") as f:
        f.write("Request Timestamp: " + str(request_timestamp) + "\n")
        f.write("Start Time: " + str(start_time) + "\n")
        if end_time:
            f.write("End Time: " + str(start_time + timedelta(minutes=span)) + "\n")
        f.write("Time Span: " + str(span) + (" minute" if span == 1 else " minutes") + "\n")

def cntExtract(
    project_root: str,
    client: Client,
    starttime: datetime,
    span = 5):

    request_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    createTargetDir(project_root, "continuous", request_timestamp)

    # data retrival
    # network code is 0101 for HiNet
    data, ctable = client.get_continuous_waveform("0101", starttime, span)

    createMetadataFile(request_timestamp, starttime, span)

    # data conversion (WIN32 -> SAC)
    win32.extract_sac(data, ctable) 
    win32.extract_sacpz(ctable)

    # go back to root
    os.chdir(project_root)

def evtExtract(
    project_root: str,
    client: Client,
    min_magnitude: float,
    starttime,
    span,
    region = 0):

    request_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    createTargetDir(project_root, "event", request_timestamp)

    endtime = starttime + timedelta(minutes=span)

    # data retrival
    client.get_event_waveform(
        starttime,
        endtime,
        region,
        min_magnitude
    )

    createMetadataFile(request_timestamp, starttime, span)

    for event in os.listdir("."):
        print(os.getcwd())
        if os.path.isdir(event):
            os.chdir(event)
            data = event + ".evt"
            ctable = event + ".ch"
            win32.extract_sac(data, ctable)
            os.chdir("..")
        # break # for extracting 1 event only for now

    # go back to root
    os.chdir(project_root)