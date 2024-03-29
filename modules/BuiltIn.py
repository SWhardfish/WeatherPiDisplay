# pylint: disable=invalid-name, too-many-locals
"""Built-in modules
"""

import datetime
import logging
import time
import csv
import pandas
from modules.WeatherModule import WeatherModule, Utils

class Alerts(WeatherModule):
    """Any severe weather alerts pertinent
    """

    def draw(self, screen, weather, updated):
        if weather is None:
            message = "Waiting data..."
        else:
            return

        self.clear_surface()
        if message:
            logging.info("%s: %s", __class__.__name__, message)
            for size in ("large", "medium", "small"):
                width, height = self.text_size(message, size, bold=True)
                if width <= self.rect.width and height <= self.rect.height:
                    break
            self.draw_text(message, (0, 0),
                           size,
                           "red",
                           bold=True,
                           align="center")
        self.update_screen(screen)


class Clock(WeatherModule):
    """Current Date and Time
    """

    def draw(self, screen, weather, updated):
        timestamp = time.time()
        locale_date = Utils.strftime(timestamp, "%A - %d %b %Y")
        locale_time = Utils.strftime(timestamp, "%H:%M:%S")

        self.clear_surface()
        self.draw_text(locale_date, (0, 0), "medium", "white", align="center")
        (right, _bottom) = self.draw_text(locale_time, (16, 20),
                                          "xlarge",
                                          "white",
                                          bold=True,
                                          align="center")
        self.update_screen(screen)


class Location(WeatherModule):
    """Current Location
    """

    def draw(self, screen, weather, updated):
        if not self.location["address"]:
            return

        message = self.location["address"]

        self.clear_surface()
        #for size in ("large", "medium", "small"):
        #    width, height = self.text_size(message, size)
        #    if width <= self.rect.width and height <= self.rect.height:
        #        break
        #if width > self.rect.width:
        #    message = message.split(",")[0]
        self.draw_text(message, (0, 0), "smallmedium", "white", align="right")
        self.update_screen(screen)


class Weather(WeatherModule):
    """Current Weather
    """

    def __init__(self, fonts, location, language, units, config):
        super().__init__(fonts, location, language, units, config)
        self.icon_size = config["icon_size"] if "icon_size" in config else 100

    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        current = weather["current"]
        daily = weather["daily"][0]

        short_summary = _(current["weather"][0]["main"])
        icon = current["weather"][0]["icon"]
        temperature = current["temp"]
        humidity = current["humidity"]
        feels_like = current["feels_like"]
        pressure = current["pressure"]
        uv_index = int(current["uvi"])
        try:
            rain_1h = current["rain"]["1h"]
        except KeyError:
            rain_1h = '0'
        print(rain_1h)
        try:
            snow_1h = current["snow"]["1h"]
        except KeyError:
            snow_1h = '0'
        print(snow_1h)
        windspeed = current["wind_speed"]
        print(windspeed)
        try:
            windgust = current["wind_gust"]
        except KeyError:
            windgust = 'nan'
        print(windgust)
        long_summary = daily["weather"][0]["description"]
        temperature_high = daily["temp"]["max"]
        temperature_low = daily["temp"]["min"]
        heat_color = Utils.heat_color(temperature, humidity, self.units)
        uv_color = Utils.uv_color(uv_index)
        weather_icon = Utils.weather_icon(icon, self.icon_size)

        #temperature = Utils.temperature_text(int(temperature), self.units)
        temperature = Utils.temperature_text(round(temperature, 1), self.units)
        feels_like = Utils.temperature_text(int(feels_like), self.units)
        temperature_low = Utils.temperature_text(int(temperature_low),
                                                 self.units)
        temperature_high = Utils.temperature_text(int(temperature_high),
                                                  self.units)
        humidity = Utils.percentage_text(humidity)
        uv_index = str(uv_index)
        pressure = Utils.pressure_text(int(pressure))

        """
        HistoryGraphLog - log data to GraphDatalog.txt
        """
        # TODO: Add maintenance of GraphDataLog.txt for removing old data to keep file small.
        xtemperature = temperature
        xtemperature = xtemperature[:-2]
        xpressure = pressure
        xpressure = xpressure[:-2]
        xtimestamp = time.strftime('%m-%d-%Y %H:%M:%S')
        #snow_1h = snow_1h

        graph = "GraphDataLog.txt"
        file = open(graph, "a", newline='')

        with file:
            myfields = ['xdate', 'temp', 'press', 'rain_1h', 'windspeed', 'windgust', 'snow_1h']
            writer = csv.DictWriter(file, fieldnames=myfields)
            #writer.writeheader()
            writer.writerow({'xdate': xtimestamp, 'temp': xtemperature, 'press': xpressure, 'rain_1h': rain_1h, 'windspeed': windspeed, 'windgust': windgust, 'snow_1h': snow_1h})
        #file.close()
        df = pandas.read_csv(graph)

        # convert to datetime
        df['xdate'] = pandas.to_datetime(df['xdate'], utc=True)
        # calculate mask
        m1 = df['xdate'] >= (pandas.to_datetime('now', utc=True) - pandas.DateOffset(days=1))
        m2 = df['xdate'] <= pandas.to_datetime('now', utc=True)
        #mask = m1 & m2
        mask = m1
        # output masked dataframes
        # df[~mask].to_csv('out1.csv', index=False)
        #Remove time from datetime
        #df['xdate'] = pandas.to_datetime(df['xdate']).dt.date
        df[mask].to_csv('GraphData.csv', index=False)
        """
        END GraphLog
        """
        #Trim file
        from datetime import datetime, timedelta

        # Read the contents of the GraphDataLog.txt file
        with open("GraphDataLog.txt", "r") as f:
            data = f.readlines()

        # Parse the data and find the date that is 2 days before the current date
        two_days_ago = datetime.now() - timedelta(days=2)
        filtered_data = [row for row in data if not row.startswith("xdate") and
                            datetime.strptime(row.split(",")[0],
                                                    "%m-%d-%Y %H:%M:%S") >= two_days_ago]

        # Write the remaining rows back to the GraphDataLog.txt file to keep only two days in log
        with open("GraphDataLog.txt", "w") as f:
            f.write("xdate,temp,press,rain_1h,windspeed,windgust,snow_1h\n")
            f.writelines(filtered_data)


        text_x = weather_icon.get_size()[0]
        text_width = self.rect.width - text_x

        message1 = self.text_warp("{} {}".format(temperature, short_summary),
                                  text_width,
                                  "medium",
                                  bold=True,
                                  max_lines=1)[0]
        message2 = "{} {}   {} {} {} {}".format(_("Feels Like"), feels_like,
                                                _("Low"), temperature_low,
                                                _("High"), temperature_high)
        if self.text_size(message2, "small")[0] > text_width:
            message2 = "Feel {}  {} - {}".format(feels_like, temperature_low,
                                                 temperature_high)
        message3 = "{} {}  {} {}  {} {}".format(_("Humidity"), humidity,
                                                _("Pressure"), pressure,
                                                _("UVindex"), uv_index)
        if self.text_size(message3, "small")[0] > text_width:
            message3 = "{}  {}  UV {}".format(humidity, pressure, uv_index)
        max_lines = int((self.rect.height - 55) / 15)
        message4s = self.text_warp(long_summary,
                                   text_width,
                                   "small",
                                   bold=True,
                                   max_lines=max_lines)

        self.clear_surface()
        self.draw_image(weather_icon, (15, 28))
        self.draw_text(message1, (text_x+28, 15), "large", heat_color, bold=True)
        self.draw_text(message2, (text_x+28, 52), "small", "white")
        i = message3.index("UV")
        (right, _bottom) = self.draw_text(message3[:i], (text_x+28, 70), "small",
                                          "white")
        self.draw_text(message3[i:], (right, 70), "small", uv_color, bold=True)
        height = 70 + (15 * (max_lines - len(message4s))) / 2
        for message in message4s:
            self.draw_text(message, (text_x+28, height),
                           "small",
                           "blue",
                           bold=True)
            height += 15
        self.update_screen(screen)


class DailyWeatherForecast(WeatherModule):
    """Daily weather forecast
    """

    def __init__(self, fonts, location, language, units, config):
        super().__init__(fonts, location, language, units, config)
        self.icon_size = config["icon_size"]
        self.day = config["day"]

    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        daily = weather["daily"][self.day]
        temperature_high = daily["temp"]["max"]
        temperature_low = daily["temp"]["min"]
        icon = daily["weather"][0]["icon"]

        weather_icon = Utils.weather_icon(icon, self.icon_size)
        day_of_week = Utils.strftime(daily["dt"], "%a")
        temperature_low = Utils.temperature_text(int(temperature_low),
                                                 self.units)
        temperature_high = Utils.temperature_text(int(temperature_high),
                                                  self.units)
        message = "{} I {}".format(temperature_low, temperature_high)

        self.clear_surface()
        self.draw_text(day_of_week, (0, 0), "small", "orange", align="center")
        self.draw_text(message, (0, 17), "xsmall", "gray", align="center")
        self.draw_image(weather_icon,
                        ((self.rect.width - self.icon_size) / 2, 30 +
                         (self.rect.height - 30 - self.icon_size) / 2))
        self.update_screen(screen)


class WeatherForecast(WeatherModule):
    """Weather Forecast
    """

    def __init__(self, fonts, location, language, units, config):
        super().__init__(fonts, location, language, units, config)

        self.forecast_days = config["forecast_days"]
        self.forecast_modules = []
        width = self.rect.width / self.forecast_days
        for i in range(self.forecast_days):
            if "icon_size" not in config:
                config["icon_size"] = 50
            config["day"] = i + 1
            config["rect"] = [
                self.rect.x + i * width, self.rect.y, width, self.rect.height
            ]
            self.forecast_modules.append(
                DailyWeatherForecast(fonts, location, language, units, config))

    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        for i in range(self.forecast_days):
            self.forecast_modules[i].draw(screen, weather, updated)


class SunriseSuset(WeatherModule):
    """Sunrise, Sunset time
    """

    def __init__(self, fonts, location, language, units, config):
        super().__init__(fonts, location, language, units, config)
        self.icon_size = config["icon_size"] if "icon_size" in config else 40

    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        current = weather["current"]
        sunrise = current["sunrise"]
        sunset = current["sunset"]

        sunrise = "{} \u2197".format(Utils.strftime(sunrise, "%H:%M"))
        sunset = "\u2199 {}".format(Utils.strftime(sunset, "%H:%M"))
        sun_icon = Utils.weather_icon("01d", self.icon_size)


        self.clear_surface()
        self.draw_image(sun_icon, ((self.rect.width - self.icon_size) / 2,
                                   (self.rect.height - self.icon_size + 9) / 2))
        self.draw_text(sunrise, (0, 5), "small", "white", align="center")
        self.draw_text(sunset, (0, self.rect.height - 20),
                       "small",
                       "white",
                       align="center")
        self.update_screen(screen)

class MoonriseMoonset(WeatherModule):
    """Moonrise, Moonset time
    """

    def __init__(self, fonts, location, language, units, config):
        super().__init__(fonts, location, language, units, config)
        self.icon_size = config["icon_size"] if "icon_size" in config else 40

    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        daily = weather["daily"][0]
        moonrise = daily["moonrise"]
        moonset = daily["moonset"]

        moonrise = "{} \u2197".format(Utils.strftime(moonrise, "%H:%M"))
        moonset = "\u2199 {}".format(Utils.strftime(moonset, "%H:%M"))
        moon_icon = Utils.weather_icon("01n", self.icon_size)
        print(moonrise)
        print(moonset)

        self.clear_surface()
        self.draw_image(moon_icon, ((self.rect.width - self.icon_size) / 2,
                                   (self.rect.height - self.icon_size + 9) / 2))
        self.draw_text(moonrise, (0, 5), "small", "white", align="center")
        self.draw_text(moonset, (0, self.rect.height - 20),
                       "small",
                       "white",
                       align="center")
        self.update_screen(screen)


class MoonPhase(WeatherModule):
    """Moon Phase
    """

    def __init__(self, fonts, location, language, units, config):
        super().__init__(fonts, location, language, units, config)
        self.icon_size = config["icon_size"] if "icon_size" in config else 50

    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        current = weather["current"]
        dt = datetime.datetime.fromtimestamp(int(current["dt"]))
        moon_age = (
            ((dt.year - 11) % 19) * 11 +
            [0, 2, 0, 2, 2, 4, 5, 6, 7, 8, 9, 10][dt.month - 1] + dt.day) % 30

        moon_icon = Utils.moon_icon(moon_age, self.icon_size)
        moon_age = str(moon_age)

        self.clear_surface()
        self.draw_image(moon_icon, ((self.rect.width - self.icon_size) / 2, 5))
        self.draw_text(moon_age, (0, self.rect.height - 20),
                       "small",
                       "white",
                       align="center")
        self.update_screen(screen)


class Wind(WeatherModule):
    """Wind direction, speed
    """

    def __init__(self, fonts, location, language, units, config):
        super().__init__(fonts, location, language, units, config)
        self.icon_size = config["icon_size"] if "icon_size" in config else 30

    def draw(self, screen, weather, updated):
        if weather is None or not updated:
            return

        daily = weather["current"]
        wind_speed = daily["wind_speed"]
        wind_deg = daily["wind_deg"]

        wind_icon = Utils.wind_arrow_icon(wind_deg, self.icon_size)
        wind_speed = Utils.speed_text(wind_speed, self.units)
        wind_deg = Utils.wind_bearing_text(wind_deg)

        self.clear_surface()
        self.draw_text(wind_deg, (0, 5), "small", "white", align="center")
        self.draw_image(wind_icon,
                        ((self.rect.width - self.icon_size) / 2, 20 +
                         (self.rect.height - 40 - self.icon_size) / 2))
        self.draw_text(wind_speed, (0, self.rect.height - 20),
                       "small",
                       "white",
                       align="center")
        self.update_screen(screen)
