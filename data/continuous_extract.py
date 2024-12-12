from HinetPy import Client, win32
from datetime import datetime, timedelta
import os 

def cnt_extract(
    project_root: str,
    client: Client,
    starttime: datetime,
    span = 5):

    os.chdir(project_root)

    # the name of the target dir is the date of the extraction request
    # the final path is: "project/data/continuous_data/[date_of_request]"
    request_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "continuous_data",
        request_timestamp
    )

    os.makedirs(target_dir)
    os.chdir(target_dir)

    # data retrival
    # network code is 0101 for HiNet
    data, ctable = client.get_continuous_waveform("0101", starttime, span)

    # data conversion (WIN32 -> SAC)
    win32.extract_sac(data, ctable) 
    win32.extract_sacpz(ctable)

    # metadata file writing
    with open("info.txt", "w") as f:
        f.write("Request Timestamp: " + str(request_timestamp) + "\n")
        f.write("Start Time: " + str(starttime) + "\n")
        f.write("End Time: " + str(starttime + timedelta(minutes=span)) + "\n")
        f.write("Time Span: " + str(span) + ("minute" if span == 1 else "minutes") + "\n")

    # go back to root
    os.chdir(project_root)