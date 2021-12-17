'''
    Below is all the imports that are used throughout this module 
'''
import json,sched,time
import logging
from flask import Flask,url_for,render_template,redirect,request,Markup
from covid_data_handler import parse_csv_data,process_covid_csv_data,covid_API_request,schedule_covid_updates
from covid_news_handling import news_API_request
from datetime import datetime,timedelta

''' This opens the config file '''
with open("./static/config.json") as file:
    data = json.load(file)

''' Creating the flask app so we can edit and render the hmtl file '''
app = Flask(__name__)

''' 
    Creates a scheduler object
    Create a list to hold the data about a scheduled event and a dictionary to store the sched event
    Creates a list to hold all the news that has been removed
'''
s = sched.scheduler(time.time,time.sleep)
ScheduleList,SchedDict = [],{}
RemovedNews = []

UpdateNews = True
UpdateData = True

''' A function that will use a try to check if a value can be converted to an integer '''
def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False

''' app.route will link when the page is loaded with that route and load this function '''
@app.route("/")
@app.route("/index")
def index():
    ''' Runs the sched event so items will be scheduled '''
    s.run(blocking = False)
    
    ''' Gets all the data from the csv '''
    csv_7day_infections,current_hospital_cases_csv,total_deaths_csv = process_covid_csv_data(parse_csv_data('nation_2021-10-28.csv'))
    ''' Gets the data from the api '''
    covid_dictionary = covid_API_request(data["LocationData"]["location"],data["LocationData"]["location-type"])

    ''' Creates a list with the raw articles so we can remove the ones the user does not want '''
    articles_without_removed = news_API_request()
    articles = []

    ''' Gets the schdule time and update label from the html websites and checks if they have been ticked as one of them has to if we need something to update'''
    schedule_time = request.args.get("update")
    update_label = request.args.get("two")
    if schedule_time and update_label :

        ''' Gets the real time and converts it to seconds and also does the same with the time interval set by the user '''
        now = str(datetime.now().time())
        hours,minutes = schedule_time.split(":")
        hours_now,minutes_now,seconds_now =  now.split(":")
        hours_Num, valid_Num_h, = intTryParse(hours)
        minutes_Num, valid_Num_m = intTryParse(minutes)
        if valid_Num_h and valid_Num_m:
            seconds = (int(hours_Num) * 3600) + (int(minutes_Num) * 60)
            secondsnow = (int(hours_now) * 3600) + (int( minutes_now) * 60) + float(seconds_now)
            ''' Gets the user input and the sends it to get all the information '''
            repeat = request.args.get("repeat")
            covid_data = request.args.get("covid-data")
            news = request.args.get("news")
            content = ""
            if covid_data or news:
                ScheduleList.append(schedule_covid_updates(schedule_time,update_label))
                
                # Schedule the next run of this function, but only if it'll be before 't_end'
                print(str(secondsnow + seconds))
                ''' Schedules the event '''
                SchedDict[update_label] = s.enterabs(secondsnow + seconds,1,print,("test"))
                
                for item in ScheduleList:
                    if item["title"] == update_label:
                        item["content"] = Markup(item["content"])
            
            if repeat:
                print("repeat is ticked")
                content += "\n" + repeat

            
            

            
            
    ''' Cancels the sched event when the user wants to '''
    if request.args.get("update_item"):
        print(SchedDict[request.args.get("update_item")])
        
        
        
        for item in ScheduleList:
            if item["title"] == request.args.get("update_item"):
                ScheduleList.remove(item)
        SchedDict[request.args.get("update_item")] = None
        print(ScheduleList)
        #s.cancel(SchedDict[update_label])
        
    ''' Removes a news widget when a user wants to '''
    if request.args.get("notif"):
        print(request.args.get("notif"))
        if not(request.args.get("notif") in RemovedNews):
            RemovedNews.append(request.args.get("notif"))

        
    ''' Filters through the news_articles and removes the ones the user has removed '''
    for news_article in articles_without_removed:
        if not(news_article["title"] in RemovedNews):
            
            contentSplit = str(news_article["content"]).split("… [+")
            if str(news_article["content"]) == "None":
                news_article["content"] = Markup('<a href = "'+ news_article["url"] + '"> Read More </a>')
            else:
                news_article["content"] = Markup(contentSplit[0] + '...<br> <a href = "'+ news_article["url"] + '"> Read More </a>')
            articles.append(news_article)
            
    
    
    print("bout to update")
    ''' Sends the data to the user and updates the html '''
    return render_template(
        "index.html", 
        local_7day_infections = covid_dictionary["local_infection_sum"],
        national_7day_infections = covid_dictionary["national_infection_sum"],
        location = covid_dictionary["location"],
        nation_location = covid_dictionary["nation"],
        news_articles = articles,
        updates = ScheduleList,
        image = "image.png"
    )



if __name__ == "__main__":
    app.run(debug=True)



