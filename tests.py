import datetime
from modules import scheduling

def test_empty_streak():
    streak_data = {}
    json_data = scheduling.increment_streak("test", "02-01", streak_data)
    assert("streaks" in json_data)

    streak_dic = json_data["streaks"]["test"]
    assert("days" in streak_dic)
    assert("streak_freezes" in streak_dic)
    assert("last_update" in streak_dic)
    assert(streak_dic["days"] == 0)
    assert(streak_dic["streak_freezes"] == 0)
    assert(streak_dic["last_update"] == "02-01")

def test_increment_streak():
    streak_data = {"streaks": {"test": {"days": 1, "streak_freezes": 0, "last_update": "01/01"}}}
    json_data = scheduling.increment_streak("test", "02-01", streak_data)

    streak_dic = json_data["streaks"]["test"]
    assert(streak_dic["days"] == 2)
    assert(streak_dic["streak_freezes"] == 0)
    assert(streak_dic["last_update"] == "02-01")

def test_2weeks_streak():
    streak_data = {"streaks": {"test": {"days": 14, "streak_freezes": 0, "last_update": "01/01"}}}
    json_data = scheduling.increment_streak("test", "02-01", streak_data)

    streak_dic = json_data["streaks"]["test"]
    assert(streak_dic["days"] == 15)
    assert(streak_dic["streak_freezes"] == 1)
    assert(streak_dic["last_update"] == "02-01")

def test_test_streak_empty():
    streak_data, _ = scheduling.test_streak({}, "01-01", "test")
    assert(streak_data == {})

def test_test_streak_ok():
    test_time = datetime.datetime.strptime("23:50:00-01-01-2026", "%H:%M:%S-%d-%m-%Y")
    current_streak = {
        "days": 15,
        "streak_freezes": 0,
        "last_update": "01-01"
    }
    streak_data, msg = scheduling.test_streak(current_streak, test_time, "test")
    assert("days" in streak_data)
    assert("streak_freezes" in streak_data)
    assert("last_update" in streak_data)
    assert(streak_data["days"] == current_streak["days"])
    assert(streak_data["streak_freezes"] == current_streak["streak_freezes"])
    assert(streak_data["last_update"] == current_streak["last_update"])
    assert(msg == "")

def test_test_streak_freeze():
    test_time = datetime.datetime.strptime("23:50:00-02-01-2026", "%H:%M:%S-%d-%m-%Y")
    current_streak = {
        "days": 15,
        "streak_freezes": 1,
        "last_update": "01-01"
    }
    streak_data, msg = scheduling.test_streak(current_streak, test_time, "test")
    assert("days" in streak_data)
    assert("streak_freezes" in streak_data)
    assert("last_update" in streak_data)
    assert(streak_data["days"] == current_streak["days"])
    assert(streak_data["streak_freezes"] == 0)
    assert(streak_data["last_update"] == current_streak["last_update"])

def test_test_streak_lost():
    test_time = datetime.datetime.strptime("23:50:00-02-01-2026", "%H:%M:%S-%d-%m-%Y")
    current_streak = {
        "days": 15,
        "streak_freezes": 0,
        "last_update": "01-01"
    }
    streak_data, _ = scheduling.test_streak(current_streak, test_time, "test")
    assert("days" in streak_data)
    assert("streak_freezes" in streak_data)
    assert("last_update" in streak_data)
    assert(streak_data["days"] == 0)
    assert(streak_data["streak_freezes"] == 0)
    assert(streak_data["last_update"] == current_streak["last_update"])

def test_test_streak_lost_3days():
    test_time = datetime.datetime.strptime("23:50:00-04-01-2026", "%H:%M:%S-%d-%m-%Y")
    current_streak = {
        "days": 15,
        "streak_freezes": 0,
        "last_update": "01-01"
    }
    streak_data, _ = scheduling.test_streak(current_streak, test_time, "test")
    assert(streak_data == {})

def test_test_streak_many():
    test_time = datetime.datetime.strptime("23:50:00-02-01-2026", "%H:%M:%S-%d-%m-%Y")
    json_data = {
        "streaks": {
            "test1" : {
                "days": 10,
                "streak_freezes": 0,
                "last_update": "01-01"
            },
            "test2" : {
                "days": 15,
                "streak_freezes": 0,
                "last_update": "01-01"
            }
        }
    }
    json_data_new, msg_list = scheduling.test_streaks(json_data, test_time)
    assert("streaks" in json_data_new)
    for key, streak_data in json_data["streaks"].items():
        assert("days" in streak_data)
        assert("streak_freezes" in streak_data)
        assert("last_update" in streak_data)

        assert(streak_data["days"] == json_data["streaks"][key]["days"])
        assert(streak_data["last_update"] == json_data["streaks"][key]["last_update"])
    assert(len(msg_list) == 2)

if __name__ == "__main__":
    test_empty_streak()
    test_increment_streak()
    test_2weeks_streak()
    test_test_streak_empty()
    test_test_streak_ok()
    test_test_streak_freeze()
    test_test_streak_lost()
    test_test_streak_lost_3days()
    test_test_streak_many()