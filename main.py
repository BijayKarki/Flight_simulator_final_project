#################
##
#################
from flask import Flask, request, Response
import json
import mysql.connector
import requests
from geopy import distance

connection = mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        database='flight_game_new',
        user='root',  # Check this and make changes here
        password='bijay123',  # Check this and make changes here
        autocommit=True)

app = Flask(__name__)


def get_all_goals():
    sql_read = f"SELECT id, name FROM goal"
    cursor = connection.cursor()
    cursor.execute(sql_read)
    result = cursor.fetchall()
    # print(result)
    return result


@app.route('/airports/<icao>')
def get_airport_by_icao(icao):

    prev_lat = request.args.get("prev_lat")
    prev_lon = request.args.get("prev_lon")

    print(prev_lat, prev_lon)

    try:
        sql = "SELECT airport.name AS airport_name, municipality, latitude_deg, longitude_deg, country.name AS country_name " \
              "FROM airport, country"
        sql += " WHERE ident ='" + icao + "'"
        sql += " AND country.iso_country = airport.iso_country "


        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        # print(result) # checking the result
        lat = result[0][2]
        lon = result[0][3]

        # communicating with an external data source to access weather parameters.
        # https://www.jodc.go.jp/data_format/weather-code.html

        url = 'https://api.open-meteo.com/v1/forecast?current_weather=True&windspeed_unit=ms&latitude=' + str(
            lat) + '&longitude=' + str(lon)
        response_API = requests.get(url)
        # print(response_API.status_code)
        data = response_API.text
        parse_json = json.loads(data)
        temp = parse_json['current_weather']['temperature']
        wind_speed = parse_json['current_weather']['windspeed']
        weather_code = parse_json['current_weather']['weathercode']

        all_goals = get_all_goals()

        goal_targets = {all_goals[i][0]: all_goals[i][1] for i in range(0, len(all_goals))}

        airports = []
        goals_achieved = set()

        temperature_goal_id = None
        weather_goal_id = None
        wind_speed_goal_id = None
        # goal_targets = {1: 'HOT', 2: 'COLD', 3: '0DEG', 4: '10DEG', 5: '20DEG', 6: 'CLEAR', 7: 'CLOUDY', 8: 'WINDY'}

        # conditions for temperature values
        if temp > 25:
            temperature_goal_id = 1  # HOT
        elif temp < -20:
            temperature_goal_id = 2  # COLD
        elif temp == 0:
            temperature_goal_id = 3  # 0DEG
        elif temp == 10:
            temperature_goal_id = 4  # 10DEG
        elif temp == 20:
            temperature_goal_id = 5  # 20DEG

        if temperature_goal_id is not None:
            goal_reached = goal_targets[temperature_goal_id]
            goals_achieved.add(goal_reached)

            # create_goal_reached(game_id, temperature_goal_id)
            # update goal_reached table with game_id and temperature_goal_id

        # condition for clear or cloudy sky
        if weather_code == 0:
            weather_goal_id = 6  # CLEAR
        else:
            weather_goal_id = 7  # CLOUDS

        if weather_goal_id is not None:
            goals_achieved.add(goal_targets[weather_goal_id])
            # create_goal_reached(game_id, weather_goal_id)
            # update goal_reached table with game_id and temperature_goal_id

        # condition for wind speed
        if wind_speed > 10:
            wind_speed_goal_id = 8
            goals_achieved.add(goal_targets[wind_speed_goal_id])  # WINDY

        # calculating the distance travelled
        distance_travelled = 0
        if prev_lat is not None and prev_lon is not None:
            previous_coord = (prev_lat, prev_lon)
            current_coord = (lat, lon)
            distance_travelled = round(distance.distance(previous_coord, current_coord).km, 2)

        response = {
            "icao": icao,
            "name": result[0][0],
            "city": result[0][1],
            "lat": lat,
            "lon": lon,
            "country": result[0][4],
            "temperature": temp,
            "wind_speed": wind_speed,
            "weather_code": weather_code,
            "distance_travelled": distance_travelled,
            "status": 200,
            "goals_achieved": list( goals_achieved)
        }
        return response


    except ValueError:
        response = {
            "message": "Invalid input, not a valid ICAO!",
            "status": 400
        }
        json_response = json.dumps(response)
        http_response = Response(response=json_response, status=400, mimetype="application/json")
        return http_response


@app.errorhandler(404)
def page_not_found(error_code):
    response = {
        "message": "Invalid endpoint",
        "status": 404
    }
    json_response = json.dumps(response)
    http_response = Response(response=json_response, status=404, mimetype="application/json")
    return http_response


if __name__ == '__main__':
    app.run(use_reloader=True, host='127.0.0.1', port=5000)
