import json
import os
import datetime

sched_filename = "sched.json"

def parse_events_by_day(lower_bound_days, upper_bound_days):
    json_data = get_sched()
    date_format = "%d-%m"
    current_year = datetime.datetime.now().year

    event_nr_list = []
    nota_list = []
    formatted_datetime_list = []
    for event_str, event in json_data.items():
        event_number = -1
        if(event_str.startswith("event_")):
            event_number = int(event_str.split('_')[1])
            nota = event["nota"]
            formatted_datetime = event["event_datetime"]
            if len(formatted_datetime):
                date_obj = datetime.datetime.strptime(formatted_datetime, date_format)
                date_obj = date_obj.replace(year=current_year)
                current_time = datetime.datetime.now()
                time_difference = (date_obj - current_time)
                if (lower_bound_days-1) <= time_difference.days<= (upper_bound_days-1):
                    event_nr_list.append(event_number)
                    nota_list.append(nota)
                    formatted_datetime_list.append(formatted_datetime)
    return event_nr_list, nota_list, formatted_datetime_list

def build_reminder_message(event_nr_list, nota_list, formatted_datetime_list):
    message = ""
    for i in range(len(event_nr_list)):
        message = message + "Nota **{}**: **\"{}\"**, no dia **{}**\n".format(
            event_nr_list[i],nota_list[i],formatted_datetime_list[i]
            )
    return message

def get_morning_message():
    event_nr_list, nota_list, formatted_datetime_list = parse_events_by_day(0, 0)
    if len(event_nr_list):
        message = "Bom dia! Não esquecer o que há para fazer hoje!\n"
        message = message + build_reminder_message(event_nr_list, nota_list, formatted_datetime_list)
        message = message + "\nEstá na hora de sair da camita!"
    else:
        message = "Bom dia senhores bubz!"
    return message

def get_night_message():
    event_nr_list, nota_list, formatted_datetime_list = parse_events_by_day(1, 1)
    if len(event_nr_list):
        message = "Boas! Não esquecer o que há para fazer amanhã!\n"
        message = message + build_reminder_message(event_nr_list, nota_list, formatted_datetime_list)
        message = message + "\nHora de ir para a camita! Bons soninhos!"
    else:
        message = None
    return message

def compute_new_id(json_data):
    new_id = -1
    for key in json_data.keys():
        if(key.startswith("event_")):
            event_number = int(key.split('_')[1])
            if(event_number>new_id):
                new_id=event_number
    return new_id+1

def add_event(nota, formatted_datetime):
    json_data = get_sched()
    latest_id = compute_new_id(json_data)
    event_key = "event_" + str(latest_id)

    if event_key not in json_data:
        json_data[event_key] = {}

    json_data[event_key]
    json_data[event_key]["nota"] = nota
    json_data[event_key]["event_datetime"] = formatted_datetime
    commit_file(json_data)
    return latest_id

def increment_streak(topic, formatted_datetime):
    json_data = get_sched()
    if "streaks" not in json_data:
        json_data["streaks"] = {}

    streaks = json_data["streaks"]
    days = 0
    streak_freezes = 0
    if topic not in streaks:
        json_data["streaks"][topic] = {}
    else:
        days = int(json_data["streaks"][topic]["days"])
        streak_freezes = int(json_data["streaks"][topic]["streak_freezes"])
        prev_formatted_time = json_data["streaks"][topic]["last_update"]

    if(prev_formatted_time != formatted_datetime):
        days = days+1
    else:
        return -1

    if((days % 15) == 0 and streak_freezes < 5):
        streak_freezes = streak_freezes+1

    json_data["streaks"][topic]["days"] = days
    json_data["streaks"][topic]["streak_freezes"] = streak_freezes
    json_data["streaks"][topic]["last_update"] = formatted_datetime
    commit_file(json_data)
    return days

def test_streaks():
    json_data = get_sched()
    date_format = "%d-%m"
    message = ""
    if "streaks" not in json_data:
        json_data["streaks"] = {}
        return None

    streaks = json_data["streaks"]
    current_year = datetime.datetime.now().year
    for key, topic in streaks.items():
        formatted_datetime = topic["last_update"]
        days = topic["days"]
        streak_freezes = topic["streak_freezes"]
        date_obj = datetime.datetime.strptime(formatted_datetime, date_format)
        date_obj = date_obj.replace(year=current_year)
        current_time = datetime.datetime.now()
        time_difference = (date_obj - current_time)
        if time_difference.days < -1:
            if streak_freezes > 0:
                streak_freezes = streak_freezes-1
                message = message + "Usou um streak freeze na streak de {}!\n".format(key)
            else:
                days=0
                streak_freezes=0
                message = message + "Perdeste a streak de {}!!!!\n".format(key)

        json_data["streaks"][key]["days"] = days
        json_data["streaks"][key]["streak_freezes"] = streak_freezes
    commit_file(json_data)
    return message

def get_sched():
    if not os.path.exists(sched_filename):
        with open(sched_filename, 'w') as file:
            file.write('{}')
    with open(sched_filename, 'r') as file:
        json_data = json.load(file)
    return json_data

def commit_file(json_data):
    if not os.path.exists(sched_filename):
        with open(sched_filename, 'w') as file:
            file.write('{}')
    with open(sched_filename, 'w') as file:
        json.dump(json_data, file, indent=4)

def erase_event(event_id):
    json_data = get_sched()

    event_key = "event_" + str(event_id)
    if event_key not in json_data:
        raise Exception("Tal evento não foi encontrado!")
    else:
        nota = json_data[event_key]["nota"]
        formatted_datetime = json_data[event_key]["event_datetime"]
        del json_data[event_key]

    commit_file(json_data)
    return nota, formatted_datetime

def cleanup_events():
    erase_log = ""
    events_to_erase, _, formatted_datetime = parse_events_by_day(-365, -2)
    json_data = get_sched()
    for i in range(len(events_to_erase)):
        event_str = "event_" + str(events_to_erase[i])
        del json_data[event_str]
        erase_log = erase_log + "Erased \"{}\" at {}. ".format(
            event_str,
            formatted_datetime[i])
    commit_file(json_data)
    return erase_log

def erase_all():
    json_data = {}
    commit_file(json_data)