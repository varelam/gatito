import datetime
from enum import IntEnum
from modules import scheduling

class Week(IntEnum):
    EMPTY = -2
    TODAY = -1
    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6

def convert_footer_to_dow(dow_footer):
    dow_footer = dow_footer.lower()
    dow=Week.EMPTY
    if(dow_footer=="hoje"):
        dow= Week.TODAY
    elif (dow_footer=="2a" or dow_footer== "segunda" or dow_footer== "2a-feira" or dow_footer== "segunda-feira"):
        dow = Week.MON
    elif(dow_footer=="3a" or dow_footer== "terca" or dow_footer== "terça" or dow_footer== "3a-feira" or dow_footer== "terca-feira" or dow_footer== "terça-feira"):
        dow = Week.TUE
    elif(dow_footer=="4a" or dow_footer== "quarta" or dow_footer== "4a-feira" or dow_footer== "quarta-feira"):
        dow = Week.WED
    elif(dow_footer=="5a" or dow_footer== "quinta" or dow_footer== "5a-feira" or dow_footer== "quinta-feira"):
        dow = Week.THU
    elif(dow_footer=="6a" or dow_footer== "sexta" or dow_footer== "6a-feira" or dow_footer== "sexta-feira"):
        dow = Week.FRI
    elif(dow_footer=="sabado" or dow_footer== "sábado"):
        dow = Week.SAT
    elif(dow_footer=="domingo"):
        dow = Week.SUN
    else:
        dow= Week.EMPTY

    return dow

def convert_weekday_to_str(weekday):
    weekday_str = ""
    if(weekday==Week.MON):
        weekday_str="2a feira"
    elif(weekday==Week.TUE):
        weekday_str="3a feira"
    elif(weekday==Week.WED):
        weekday_str="4a feira"
    elif(weekday==Week.THU):
        weekday_str="5a feira"
    elif(weekday==Week.FRI):
        weekday_str="6a feira"
    elif(weekday==Week.SAT):
        weekday_str="Sábado"
    elif(weekday==Week.SUN):
        weekday_str="Domingo"

    return weekday_str

def interpret_time(nota_dow, ref_datetime):
    current_dow = ref_datetime.weekday()
    if (nota_dow == Week.TODAY):
        days_until_event = 0
    else:
        days_until_event = nota_dow-current_dow
        if(days_until_event<=0):
            days_until_event=days_until_event+7

    event_datetime = ref_datetime + datetime.timedelta(days=days_until_event)
    weekday = event_datetime.weekday()
    return event_datetime, weekday

def parse_nota_time(message):
    header = "!nota"
    if(message.strip() == header):
        raise Exception("A sua !nota está vazia")

    message_parts = message.split(header)
    if(len(message_parts)>2):
        raise Exception("Lamentamos mas só conseguimos uma nota de cada vez")

    message_payload=message_parts[len(message_parts)-1].strip()
    parts = message_payload.split()
    dow_key = parts[len(parts)-1].strip()
    nota  = message_payload.split(dow_key);
    if(nota == ""):
        raise Exception("A sua nota está vazia")

    nota_str = nota[0].strip()
    dow = convert_footer_to_dow(dow_key)
    return nota_str, dow_key, dow

def parse_nota(message):
    feedback_str = ""
    nota, dow_key, nota_dow = parse_nota_time(message)
    try:
        if nota_dow == Week.EMPTY:
            nota = nota + " " + dow_key
            event_id = scheduling.add_event(nota, "")
            feedback_str = "Agendei a seguinte nota: **\"{}\"**. Para cancelar usar o comando !cancelar {}".format(nota, event_id)
        else:
            event_datetime, weekday = interpret_time(nota_dow, datetime.datetime.now())
            output_format = "%d-%m"
            formatted_datetime = event_datetime.strftime(output_format)
            weekday_str = convert_weekday_to_str(weekday)
            event_id = scheduling.add_event(nota, formatted_datetime)
            feedback_str = "Agendei a seguinte nota: **\"{}\"** para **{}, dia {}**. Para cancelar usar o comando !cancelar {}".format(
                nota, weekday_str,
                formatted_datetime,
                event_id
            )
    except Exception as e:
        feedback_str = "Houve um problema com a sua nota! O que se passou: " + str(e)

    return feedback_str

#TODO: add days of week
def list_notas():
    try:
        feedback_str = ""
        json_data = scheduling.get_sched()
        for event_str, event in json_data.items():
                event_number = -1
                if(event_str.startswith("event_")):
                    event_number = int(event_str.split('_')[1])
                    nota = event["nota"]
                    formatted_datetime = event["event_datetime"]
                    if len(formatted_datetime):
                        feedback_str = feedback_str + "\nNota **{}**: **\"{}\"**, no dia **{}**".format(
                            event_number,
                            nota,
                            formatted_datetime
                            )

        for event_str, event in json_data.items():
                event_number = -1
                if(event_str.startswith("event_")):
                    event_number = int(event_str.split('_')[1])
                    nota = event["nota"]
                    formatted_datetime = event["event_datetime"]
                    if len(formatted_datetime) == 0:
                        feedback_str = feedback_str + "\nNota **{}**: **\"{}\"**".format(
                            event_number,
                            nota)

    except Exception as e:
        feedback_str = "Houve um problema! O que se passou: " + str(e)
    return feedback_str

def erase_nota(message):
    header = "!cancelar"
    feedback_str = ""
    try:
        if(message.strip() == header):
           raise Exception("O seu !cancelar precisa de um número de nota")

        message_parts = message.split(header)
        event_id=message_parts[len(message_parts)-1].strip()

        if(event_id.isdigit()):
            nota, formatted_datetime = scheduling.erase_event(event_id)
        elif (event_id == "todas" or event_id == "tudo"):
            scheduling.erase_all()
            return "Todos os eventos foram apagados!"
        else:
            raise Exception("O seu número de nota não é um número!")

        if len(formatted_datetime):
            feedback_str = "O evento número {}: **\"{}\"**, dia **{}**, foi cancelado com sucesso".format(
                event_id,
                nota,
                formatted_datetime
                )
        else:
            feedback_str = "A nota número {}: **\"{}\"**, foi cancelada com sucesso".format(
                event_id, nota)

    except Exception as e:
        feedback_str = "Houve um problema com o cancelamento da sua nota! O que se passou: " + str(e)

    return feedback_str

def update_streak(message):
    header = "!streak"
    feedback_str = ""
    try:
        if(message.strip() == header):
           raise Exception("A sua !streak precisa de um tópico! Exemplo: !streak sax")

        message_parts = message.split(header)
        topic=message_parts[len(message_parts)-1].strip()
        current_date = datetime.datetime.now()
        current_dow = current_date.weekday()

        streak_datetime, _ = interpret_time(convert_footer_to_dow("hoje"), datetime.datetime.now())
        output_format = "%d-%m"
        formatted_datetime = streak_datetime.strftime(output_format)
        json_data = scheduling.get_sched()
        json_data = scheduling.increment_streak(topic, formatted_datetime, json_data)
        scheduling.commit_file(json_data)
        days = json_data["streaks"][topic]["days"]

        if days > 0:
            feedback_str = "Renovamos a sua streak de {}! Já vai em {} dias! :fire:".format(
                topic,
                days
                )
        else:
            feedback_str = "Já renovaste a streak de {} hoje!!! Tenta amanhã outra vez :sweat_smile:".format(topic)
    except Exception as e:
        feedback_str = "Houve um problema com a sua streak! O que se passou: " + str(e)

    return feedback_str