from HinetPy import Client, win32
from datetime import datetime, timedelta
import os 

def cnt_extract(
    project_root: str,
    client: Client,
    starttime: datetime,
    span = 5):

    # by default, supposing the following file tree:
    # 
    # root
    # > data
    #   > continuous_data 
    #       > continuous_extract.py
    #   > hinet.cred

    #cred_path = getcwd() + "../hinet.cred",
    #with open(cred_path, 'r') as f:
    #    client = Client(f.readline().strip(), f.readline().strip())

    os.chdir(project_root)

    target_dir = os.path.dirname(os.path.abspath(__file__)) + "/continuous_data"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Target directory for continuous data does not exist yet, created at {target_dir}")

    # the name of the target dir is the date of the extraction request
    target_dir += "/" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.mkdir(target_dir)
    os.chdir(target_dir)

    # network code is 0101 for HiNet
    data, ctable = client.get_continuous_waveform("0101", starttime, span)

    win32.extract_sac(data, ctable) 

    win32.extract_sacpz(ctable)

    os.chdir(project_root)