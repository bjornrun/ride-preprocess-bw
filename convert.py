import os
import sys
from pathlib import Path
import natsort
import re
import json
from collections import namedtuple
import csv


def _preprocess_bw_data(src_path: str, dst_path: str) -> int:
    pathlist = Path(src_path).glob('**/*.json')

    list1 = []
    list2 = []
    for path in pathlist:
        # because path is object not string
        path_in_str = str(path)
        list1.append(path_in_str)

    list2 = natsort.natsorted(list1)

    with open(dst_path, 'w', newline='') as file_out:
        csv_out = csv.writer(file_out)
        csv_out.writerow(["year", "month", "day", "hour", "minute", "second", "lte_modem_latency", "5G_modem_latency",
                          "5G_mobil_latency", "IP", "bw_down", "bw_up", "lat", "lon", "ping", "test_server"])

        row = 0

        for path in list2:
            bw_awail = False
            timestamp_str = re.findall(r'\d+', path)
            try:
                year = timestamp_str[0]
                month = timestamp_str[1]
                day = timestamp_str[2]
                hour = timestamp_str[3]
                minutes = timestamp_str[4]
                seconds = timestamp_str[5]
            except IndexError:
                pass
            else:
                with open(path) as f:
                    try:
                        data = json.load(f)
                    except ValueError:
                        pass
                    else:
                        if len(data) == 5:
                            _str = data[4]['bandwidth']
                            str2 = _str.rstrip("\n")
                            try:
                                data[4]['bandwidth'] = json.loads(str2)
                                bw_awail = True
                            except ValueError:
                                pass
                            else:
                                if data[0]["eno1"]["latency"] > 0 or data[1]["usb0"]["latency"] > 0 or data[2]["usb1"]["latency"] > 0:
                                    if len(data) > 3:
                                        IP = data[3].get("ip", "")
                                    else:
                                        IP = ""
                                    if bw_awail:
                                        bw_down = int(data[4]["bandwidth"]["download"])
                                        bw_up = int(data[4]["bandwidth"]["upload"])
                                        bw_srv_lat = float(data[4]["bandwidth"]["server"]["lat"])
                                        bw_srv_lon = float(data[4]["bandwidth"]["server"]["lon"])
                                        bw_ping = float(data[4]["bandwidth"]["ping"])
                                        bw_host = data[4]["bandwidth"]["server"]["host"]
                                    else:
                                        bw_down = bw_up = 0
                                        bw_srv_lat = bw_srv_lon = bw_ping = 0
                                        bw_host = ""

                                    csv_out.writerow(
                                        [year, month, day, hour, minutes, seconds, float(data[0]["eno1"]["latency"]),
                                         float(data[1]["usb0"]["latency"]), float(data[2]["usb1"]["latency"]),
                                         IP, bw_down, bw_up, bw_srv_lat,
                                         bw_srv_lon, bw_ping, bw_host])

                                    row += 1
    return row


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Num bw measurements: ", _preprocess_bw_data("/mnt/smb/bandwidth", "/mnt/bandwidth.csv"))
    else:
        print("Src:", sys.argv[1], " Dst:", sys.argv[2], " Num bw measurements:",
              _preprocess_bw_data(sys.argv[1], sys.argv[2]))
