from flask import request
import json,sched,time
from datetime import datetime,timedelta
from uk_covid19 import Cov19API




s = sched.scheduler(time.time,time.sleep)



def parse_csv_data(csv_filename):
    dataList = []
    with open(csv_filename, "r") as excelFile:
        for line in excelFile:
           dataList.append(line)
    return dataList

def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False

def process_covid_csv_data(covid_csv_data):
    count,Last7days,current_hospital_cases,total_deaths = 0,0,0,0
    
    for row in covid_csv_data:
        rowList = row.split(",")
        if count >= 3 and count <= 9:
            intValue,isInt = intTryParse(rowList[6])
            if isInt:
                Last7days += intValue
        elif count == 1:
            intValue,isInt = intTryParse(rowList[5])
            if isInt:
                current_hospital_cases = intValue
        if rowList[4] != "" and total_deaths == 0:
            intValue,isInt = intTryParse(rowList[4])
            if isInt:
                total_deaths = intValue
        
            
        count += 1
    return Last7days,current_hospital_cases,total_deaths


def covid_API_request(location='Exeter',location_type='ltla'):
    with open("./static/config.json") as file:
        data = json.load(file)
    nation = data["LocationData"]["nation"]

    national = [
    'areaType=nation',
    'areaName='+nation,
    ]

    national_structure = {
    "newCasesBySpecimenDate": "newCasesBySpecimenDate",
    "cumDailyNsoDeathsByDeathDate":"cumDailyNsoDeathsByDeathDate",
    "hospitalCases":"hospitalCases",
    }

    local = [
    'areaType='+location_type,
    'areaName='+location,
    ]

    local_structure = {
    "newCasesBySpecimenDate": "newCasesBySpecimenDate"
    }

    #getting and filtering data from API
    natapi = Cov19API(filters=national, structure=national_structure)
    locapi = Cov19API(filters=local, structure=local_structure)

    natData = natapi.get_json()['data']
    locData = locapi.get_json()['data']

    local_infection_sum,national_infection_sum,national_hosptital_cases,national_cumumlative_deaths,Count = 0,0,0,0,0
    for i in locData:
        if Count < 7 and i["newCasesBySpecimenDate"] != None:
            local_infection_sum += i["newCasesBySpecimenDate"]
            
            Count += 1
        elif Count >= 7:
            break
    Count = 0
    for i in natData:
        if Count < 7 and i["newCasesBySpecimenDate"] != None:
            national_infection_sum += i["newCasesBySpecimenDate"]
            print("count is " + str(Count) + " nfection is " + str(national_infection_sum))
            Count += 1
        elif Count >= 7:
            break
        if i["cumDailyNsoDeathsByDeathDate"] != None and national_cumumlative_deaths != None:
            if i["cumDailyNsoDeathsByDeathDate"] > national_cumumlative_deaths:
                national_cumumlative_deaths = i["cumDailyNsoDeathsByDeathDate"]
        if i["hospitalCases"] != None and national_hosptital_cases != None:
            national_hosptital_cases = i["hospitalCases"]
            
            


    data = {
            'local_infection_sum':local_infection_sum,
            'location':location,
            'nation':nation,
            'national_infection_sum':national_infection_sum,
            'national_hosptital_cases':national_hosptital_cases,
            'national_cumumlative_deaths':national_cumumlative_deaths
        }
    
    return data


    
def schedule_covid_updates(update_interval,update_name):
    content = ""
    if request.args.get("repeat"):
        content = "This schedule is repeating" + "<br>"
    else:
        content = "This schedule is not repeating" + "<br>"
    if request.args.get("covid-data"):
        content += "This schedule will update covid data" + "<br>"
    else:
        content += "This schedule will not update covid data" + "<br>"
    if request.args.get("news"):
        content += "This schedule will update the news" + "<br>"
    else:
        content += "This schedule will not update the news" + "<br>" 
    current_time = datetime.now()
    hours_interval_str,mins_interval_str = update_interval.split(":")
    hours_interval,hours_converted = intTryParse(hours_interval_str)
    mins_interval,minutes_converted = intTryParse(mins_interval_str)
    if minutes_converted and hours_converted:
        time_finish = current_time + timedelta(hours=hours_interval,minutes=mins_interval)
        String_Time = str(time_finish).split(".")
        content += " Scheduled for: " + String_Time[0]
    
    schedule_Dict = {
        "title" : update_name,
        "content" : content,
        
    }
    return schedule_Dict


    
    
    
    

