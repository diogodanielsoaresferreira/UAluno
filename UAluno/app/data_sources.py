import requests
from django.conf import settings
from lxml import etree
from app import xmldatabaseinterface

# Get ementa for the next days
def get_ementaXml(place=None, date=None):
    url = "http://services.web.ua.pt/sas/ementas"
    params = ""
    newData = False

    if (place == "santiago" or place == "rest" or place == "all" or place == "esan" or place == "estga"):
        params += "?place=" + place

    if (date == "day" or date == "week"):
        if params != "":
            params += "&date=" + date
        else:
            params += "?date=" + date

    try:
        r = requests.get(url + params)
        r.encoding = 'utf-8'
        content = r.text

        parser = etree.XMLParser(encoding='utf-8')
        ementa = etree.fromstring(content.encode('utf-8'), parser=parser)

        if r.status_code != 200:
            # If it could not get from the web, get the data from the database
            print("Could not fetch the ementa. Getting ementa from database...")
            content = xmldatabaseinterface.getAllDatabase("ementas", settings.XML_FILES + "/ementas.xsd")
            parser = etree.XMLParser(encoding='utf-8')
            ementa = etree.fromstring(content, parser=parser)

        else:
            # There is new data to be updated
            newData = True
    except:
        # If it could not get from the web, get the data from the database
        print("Could not fetch the ementa. Getting ementa from database...")
        content = xmldatabaseinterface.getAllDatabase("ementas", settings.XML_FILES + "/ementas.xsd")
        parser = etree.XMLParser(encoding='utf-8')
        ementa = etree.fromstring(content, parser=parser)


    # Validate xml with schema
    try:
        with open(settings.XML_FILES + '/ementas.xsd') as ifile:
            xmlschema_doc = etree.parse(ifile)
            xmlschema = etree.XMLSchema(xmlschema_doc)

            if xmlschema.validate(ementa):

                # Update the database with new content
                if (newData):
                    xmldatabaseinterface.updateDatabase('ementas', settings.XML_FILES + '/ementas.xsd', content)
                return ementa
            else:
                return None
    except:
        raise FileNotFoundError("Could not find ementa schema file")

# Get weekly forecast simplified as xml file
def get_weekly_forecastXml():
    url = "http://api.openweathermap.org/data/2.5/forecast/daily?q="
    city = "Aveiro"
    app_id = "bd5e378503939ddaee76f12ad7a97608"

    newData = False

    try:
        r = requests.get(url + city + "&APPID=" + app_id + "&mode=xml&cnt=7&units=metric")

        r.encoding = 'utf-8'
        content = r.text

        parser = etree.XMLParser(encoding='utf-8')
        weather = etree.fromstring(content.encode('utf-8'), parser=parser)

        if r.status_code != 200:
            # If it could not get from the web, get the data from the database
            print("Could not fetch the weather. Getting weather from database...")
            content = xmldatabaseinterface.getAllDatabase("weather", settings.XML_FILES + "/weather.xsd")
            parser = etree.XMLParser(encoding='utf-8')
            weather = etree.fromstring(content, parser=parser)

        else:
            # There is new data to be updated
            newData = True

    except:
        # If it could not get from the web, get the data from the database
        print("Could not fetch the weather. Getting weather from database...")
        content = xmldatabaseinterface.getAllDatabase("weather", settings.XML_FILES + "/weather.xsd")
        parser = etree.XMLParser(encoding='utf-8')
        weather = etree.fromstring(content, parser=parser)

    # Validate xml with schema
    try:
        with open(settings.XML_FILES + '/weather.xsd') as ifile:
            xmlschema_doc = etree.parse(ifile)
            xmlschema = etree.XMLSchema(xmlschema_doc)

            if xmlschema.validate(weather):

                # Update the database with new content
                if (newData):
                    xmldatabaseinterface.updateDatabase('weather', settings.XML_FILES + '/weather.xsd', content)
                return weather
            else:
                return None
    except:
        raise FileNotFoundError("Could not validate the weather schema")

# Get XML for UA news highlights
def get_newsXml(dt, d):
    url = "http://services.sapo.pt/UA/Online/contents_xml?dt="+str(dt)+"&d="+str(d)

    newData = False

    try:
        r = requests.get(url)
        r.encoding = 'utf-8'
        content = r.text

        parser = etree.XMLParser(encoding='utf-8')
        news = etree.fromstring(content.encode('utf-8'), parser=parser)

        if r.status_code != 200:
            # If it could not get from the web, get the data from the database
            print("Could not fetch the news. Getting news from database...")
            content = xmldatabaseinterface.getAllDatabase("news", settings.XML_FILES + "/news.xsd")
            parser = etree.XMLParser(encoding='utf-8')
            news = etree.fromstring(content, parser=parser)
        else:
            # There is new data to be updated
            newData = True

    except:
        # If it could not get from the web, get the data from the database
        print("Could not fetch the news. Getting news from database...")
        content = xmldatabaseinterface.getAllDatabase("news", settings.XML_FILES + "/news.xsd")
        parser = etree.XMLParser(encoding='utf-8')
        news = etree.fromstring(content, parser=parser)

    # Validate xml with schema
    try:
        with open(settings.XML_FILES + '/news.xsd') as ifile:
            xmlschema_doc = etree.parse(ifile)
            xmlschema = etree.XMLSchema(xmlschema_doc)

            if xmlschema.validate(news):

                # Update the database with new content
                if(newData):
                    xmldatabaseinterface.updateDatabase('news', settings.XML_FILES + '/news.xsd', content)
                return news

            else:
                return None
    except:
        raise FileNotFoundError("Could not validate the news schema")

# Get chat xslt transform
def getChatTransform():
    try:
        xslt_file = etree.parse(settings.XML_FILES + '/chattransform.xslt')
    except:
        raise FileNotFoundError('Could not find the chat transform')

    transform = etree.XSLT(xslt_file)
    return transform

# Get grades xslt transform
def getGradesTransform():
    try:
        xslt_file = etree.parse(settings.XML_FILES + '/notas.xslt')
    except Exception as e:
        raise FileNotFoundError('Could not find the grades transform')

    transform = etree.XSLT(xslt_file)
    return transform