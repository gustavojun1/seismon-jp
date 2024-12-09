from HinetPy import Client, win32

with open("../hinet.cred", 'r') as f:
    client = Client(f.readline().strip(), f.readline().strip())

year = "2012"
month = "01"
day = "01"
hour = "00"
minute = "00"
second = "01"

starttime = f"{year}{month}{day}{hour}{minute}{second}"

data, ctable = client.get_continuous_waveform("0101", starttime, 5)
print("data: " + data)
print("ctable: " + ctable)

win32.extract_sac(data, ctable) 

win32.extract_sacpz(ctable)