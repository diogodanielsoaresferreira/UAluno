import re
import datetime
import django

# Parse the xml document of Ementa to a dictionary
def parse_ementa(ementa):
    if ementa is None:
        return []

    menu_List = {}
    menus = ementa.find('.//menus')

    for menu in menus:
        canteen = menu.get('canteen')
        meal = menu.get('meal')
        weekday = menu.get('weekday')
        disabled = False if menu.get('disabled')=='0' else True

        if(weekday in menu_List):
            if(canteen in menu_List[weekday]):
                menu_List[weekday][canteen][meal] = {}

            else:
                menu_List[weekday][canteen] = {}
                menu_List[weekday][canteen][meal] = {}
        else:
            menu_List[weekday] = {}
            menu_List[weekday][canteen] = {}
            menu_List[weekday][canteen][meal] = {}

        if(not disabled):
            item = menu.findall('items/item')
            for i in item:
                name = i.get('name')
                content = i.text
                menu_List[weekday][canteen][meal][name] = content

    return menu_List

# Parse the xml document of the news of a list
def parse_newsXml(news):
    if news is None:
        return []

    channel = news.findall('.//channel[title=\'Universidade de Aveiro\']/item')

    news = []

    for item in channel:
        news += [{'link': item.find("link").text, 'title': item.find("title").text, 'description': get_description(item.find("description").text)}]

    return news

# Aux function
def get_description(text):
    imgsearch = re.search('<img(.+?)/>', text)
    if imgsearch:
        imgtag = imgsearch.group(0)
        return (text.replace(imgtag, ""), imgtag)
    return (text, "")

# Parse the 7 day forecast xml document to a dictionary
def parse_weekly_forecast(weather):
    if weather is None:
        return []

    city = weather.find('.//location')
    sun = weather.find('.//sun')

    name = city.find('name').text
    lon = city.find('location').get('latitude')
    lat = city.find('location').get('longitude')
    rise = django.utils.dateparse.parse_datetime(sun.get('rise')).time()
    set = django.utils.dateparse.parse_datetime(sun.get('set')).time()

    forecast = weather.findall('.//forecast/time')

    forecastl = {"name": name, "lat": lat, "lon": lon, "rise": rise, "set": set, "forecast": []}
    for time in forecast:
        symbol = time.find('symbol').get('var')
        desc = time.find('symbol').get('name')
        precipitation = time.find('precipitation').get('value')
        winddirectiondeg = time.find('windDirection').get('deg')
        winddirectionname = time.find('windDirection').get('name')
        windspeedmps = time.find('windSpeed').get('mps')
        windspeedname = time.find('windSpeed').get('name')
        temp = time.find('temperature').get('day')
        maxtemp = time.find('temperature').get('max')
        mintemp = time.find('temperature').get('min')
        nighttemp = time.find('temperature').get('night')
        evetemp = time.find('temperature').get('eve')
        morntemp = time.find('temperature').get('morn')
        pressure = time.find('pressure').get('value')
        humidity = time.find('humidity').get('value')
        clouds = time.find('clouds').get('value')
        day = time.get('day')

        precverbose = translatePrecipitation(precipitation)
        descriptionVerbose = translateDescription(desc)
        winddirectionname = translateCoordinate(winddirectionname)
        clouds = translateDescription(clouds)

        date = datetime.datetime.strptime(day, '%Y-%m-%d')
        forecastl["forecast"] += [{"symbol": symbol, "winddirectiondeg": winddirectiondeg,
                                   "winddirectionname": winddirectionname, "windspeedmps": windspeedmps,
                                   "windspeedname": windspeedname,"desc": descriptionVerbose, "day_year": day,
                                   "temp": temp, "maxtemp": maxtemp, "mintemp": mintemp, "pressure": pressure,
                                   "humidity": humidity, "clouds": clouds, "precipitation": precverbose,
                                   "nighttemp": nighttemp, "evetemp": evetemp, "morntemp": morntemp, "day_week": date.weekday()}]

    return forecastl

# Parse notas xml
def getParsedCourses(xml_courses):

    course_list = []

    if xml_courses is None:
        return []

    courses = xml_courses.findall('.//course')

    for course in courses:
        name = course.get('name')
        ects = course.get('ects')
        area = course.get('area')
        year = course.get('year')
        semester = course.get('semester')
        grade = course.find('grade')
        course_list.append({'name': name, 'ects': ects, 'area': area, 'year': year, 'semester': semester})
        if(grade!=None):
            course_list[-1].update({'grade':int(grade.text)})

    return course_list

# Translate a description to portuguese
def translatePrecipitation(precipitation):
    precverbose = precipitation

    if (precipitation == None):
        precverbose = "Sem chuva"
    elif (float(precipitation) / 3 < 0.25):
        precverbose = "Possibilidade de aguaceiros leves"
    elif (float(precipitation) / 3 < 1):
        precverbose = "Precipitação fraca"
    elif (float(precipitation) / 3 < 4):
        precverbose = "Precipitação moderada"
    elif (float(precipitation) / 3 < 16):
        precverbose = "Precipitação forte"
    else:
        precverbose = "Precipitação muito forte"

    return precverbose

# Translate a description to portuguese
def translateDescription(description):
    descriptionVerbose = description

    if (description == "clear sky" or description == "sky is clear"):
        descriptionVerbose = "Céu limpo"
    elif (description == "few clouds"):
        descriptionVerbose = "Algumas nuvens"
    elif (description == "scattered clouds"):
        descriptionVerbose = "Céu nublado"
    elif (description == "broken clouds" or description=="overcast clouds"):
        descriptionVerbose = "Céu muito nublado"
    elif (description == "shower rain" or description == "light rain"):
        descriptionVerbose = "Aguaceiros"
    elif (description == "rain" or description == "moderate rain"):
        descriptionVerbose = "Chuva"
    elif (description == "thunderstorm"):
        descriptionVerbose = "Trovoada"
    elif (description == "snow"):
        descriptionVerbose = "Neve"
    elif (description == "mist"):
        descriptionVerbose = "Variações ao longo do dia"

    return descriptionVerbose

# Translate a description to portuguese
def translateCoordinate(coordinate):
    if (coordinate == "North"):
        coordinate = "Norte"
    elif (coordinate == "East"):
        coordinate = "Este"
    elif (coordinate == "South"):
        coordinate = "Sul"
    elif (coordinate == "West"):
        coordinate = "Oeste"

    elif (coordinate == "Northeast"):
        coordinate = "Nordeste"
    elif (coordinate == "SouthEast"):
        coordinate = "Sudeste"
    elif (coordinate == "Southwest"):
        coordinate = "Sudoeste"
    elif (coordinate == "Northwest"):
        coordinate = "Noroeste"
    elif (coordinate == "North-northeast"):
        coordinate = "Norte-nordeste"
    elif (coordinate == "North-northwest"):
        coordinate = "Norte-noroeste"
    elif (coordinate == "East-northeast"):
        coordinate = "Este-Nordeste"
    elif (coordinate == "East-southeast"):
        coordinate = "Este-sudeste"
    elif (coordinate == "South-southeast"):
        coordinate = "Sul-sudeste"
    elif (coordinate == "South-southwest"):
        coordinate = "Sul-sudoeste"
    elif (coordinate == "West-southwest"):
        coordinate = "Oeste-sudoeste"
    elif (coordinate == "West-northwest"):
        coordinate = "Oeste-noroeste"

    return coordinate