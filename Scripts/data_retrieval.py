import os
import csv
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def get_history_weather(latitude, longitude, start):
    """
    Get history weather data from OpenWeatherMap API
    :param latitude: Latitude
    :param longitude: Longitude
    :param start: Start date
    :param end: End date
    :return: JSON data
    """
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": os.getenv("API_KEY"),
        "units": "metric",
        "start": start,
        "cnt": 169,
    }
    r = requests.get(url=os.getenv("API_URL"), params=params)
    return r.json()


def format_data(data, start):
   # The data is formatted to be written to a file
   # new array and json object are created
    new_data = []
    for i in range(len(data[0])):
        if i != 0:
            start += 3600000

        if data[0][i]["faixa"] == 0:
            continue

        day_of_week = datetime.fromtimestamp(start/1000).weekday()

        new_item = {"timestamp": start, "day_of_week": day_of_week,
                    "faixa": data[0][i]["faixa"], "hour": data[0][i]["hour"], "vehicle": data[0][i]["vehicle"]}

        # csv_writer.writerow([start, data[0][i]["vehicle"]])

        new_data.append(new_item)

    return new_data


def format_data_csv(data, start):
    # format data to be written to csv file
    # one column for timestamp and one for the number of vehicles of the two faixas combined
    dict = {}  # key: timestamp, value: number of vehicles both faixas combined
    for i in range(len(data[0])):
        if data[0][i]["faixa"] == 0:
            continue

        hour = start + data[0][i]["hour"]*3600000
        if hour in dict:
            dict[hour] += data[0][i]["vehicle"]
        else:
            dict[hour] = data[0][i]["vehicle"]

    for key in dict:
        csv_writer.writerow([key, dict[key]])


def format_data_ow(data, start, final_array):
    # The data is formatted to be written to a file
    # new array and json object are created
    new_data = []
    for i in range(len(data["list"])):
        day_of_week = datetime.fromtimestamp(start).weekday()
        new_item = {"timestamp": start, "day_of_week": day_of_week, "hour": data["list"][i]["dt"],
                    "weather": data["list"][i]["weather"][0]["main"]}
        new_data.append(new_item)
        # print(new_item)
    return new_data


def get_data(start, end, day):
    end_1 = start + day
    i = 0
    # the api calls are made in a loop, each loop will retrieve the data for one day
    while end_1 <= end:
        url1 = "https://aveiro-living-lab.it.pt/api/ch/radars/daily?entity_id=p35&type=light&start=" + \
            str(start) + "&end=" + str(end_1)

        response = requests.get(url1)
        data = response.json()

        format_data_csv(data, start)
        data = format_data(data, start)

        if len(data) > 0:
            json.dump(data, file1, indent=4)

        start = end_1
        end_1 = start + day


def get_data_ow(start, end):
    final_array = []
    while start <= end:
        data = get_history_weather(lat, lon, start)
        data = format_data_ow(data, start, final_array)
        start += 169*3600
        final_array.extend(data)
    return final_array


def join_data(file_csv, data_ow):
    # join the data from the two apis
    # read csv compara timestamp com timestamp do json, if equal add the vehicle number to the json

    line_count = 0
    new_data = []
    for row in file_csv:

        if line_count == 0:
            line_count += 1
        else:
            row = row.split(",")
            for i in range(len(data_ow)):
                if str(int(int(row[0])/1000)) == str(data_ow[i]["hour"]):
                    print("GOT IT")
                    data_ow[i]["vehicle"] = float(row[1].replace("\n", ""))
                    new_data.append(data_ow[i])
                    break
            line_count += 1

    json.dump(new_data, file_ow_join, indent=4)


if __name__ == "__main__":
    start = 1655251200000  # 15/06/2022 00:00:00
    end = 1684108800000  # 15/05/2023 00:00:00
    day = 86400000

    # Aveiro
    lat = 40.64427
    lon = -8.64554

    # open files
    file1 = open("out/data.json", "w")
    file_csv = open("out/data_time_vehicles.csv", "w", newline='')
    file_ow = open("out/data_ow.json", "w")
    file_ow_join = open("out/data_ow_join.json", "w")

    csv_writer = csv.writer(file_csv)
    csv_writer.writerow(["timestamp", "vehicle"])

    data = get_data(start, end, day)
    data_ow = get_data_ow(1655251200, end/1000)
    json.dump(data_ow, file_ow, indent=4)

    file1.close()
    file_csv.close()
    file_ow.close()

    file_csv_read = open("out/data_time_vehicles.csv", "r")

    join_data(file_csv_read, data_ow)

    file_ow_join.close()
