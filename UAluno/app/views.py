from datetime import datetime
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
import math
import app.data_logic as dl
import app.data_sources as ds
from app import xmldatabaseinterface
from .forms import NotaForm
from django.http import HttpResponse

'''
    Home page of UAluno
'''
@login_required(login_url='/login/')
def home(request):

    news = dl.parse_newsXml(ds.get_newsXml(0, 0))
    ementa = dl.parse_ementa(ds.get_ementaXml(date="week"))
    weekly_forecast = dl.parse_weekly_forecast(ds.get_weekly_forecastXml())
    main_plates = get_main_plates(ementa)
    chat = render_chat(request.user.id)

    return render(
        request,
        'app/home.html',
        {
            'title': 'Início',
            'ementa': ementa,
            'news': news,
            'year': datetime.now().year,
            'main_plates': main_plates,
            'forecast': weekly_forecast,
            'chat': chat,
            'datev':datetime.now()
        }
    )

'''
    Register page of UAluno
'''
def registar(request):

    # If form is valid, register new user
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')

    else:
        form = UserCreationForm()
    return render(request,
                  'app/registar.html',
                  { 'title': 'Registar',
                    'form': form
                   })


@login_required(login_url='/login/')
def ementas(request, day=None):
    ementa = dl.parse_ementa(ds.get_ementaXml(date="week"))
    chat = render_chat(request.user.id)

    if(day!=None and day not in ementa):
        raise Http404

    if(day==None):
        if (datetime.today().weekday()==0):
            day = "Monday"
        elif (datetime.today().weekday()==1):
            day = "Tuesday"
        elif (datetime.today().weekday()==2):
            day = "Wednesday"
        elif (datetime.today().weekday()==3):
            day = "Thursday"
        elif (datetime.today().weekday()==4):
            day = "Friday"
        elif (datetime.today().weekday()==5):
            day = "Saturday"
        elif (datetime.today().weekday()==6):
            day = "Sunday"


    return render(
        request,
        'app/ementas.html',
        {
            'title': 'Ementas',
            'year': datetime.now().year,
            'ementa': ementa,
            'chat': chat,
            'day': day
        }
    )


@login_required(login_url='/login/')
def metereologia(request, day=None):

    chat = render_chat(request.user.id)
    weekly_forecast = dl.parse_weekly_forecast(ds.get_weekly_forecastXml())

    if(day==None and 'forecast' in weekly_forecast and len(weekly_forecast['forecast'])>0):
        day = str(weekly_forecast['forecast'][0]['day_week'])

    return render(
        request,
        'app/metereologia.html',
        {
            'title': 'Metereologia',
            'year': datetime.now().year,
            'chat': chat,
            'forecast': weekly_forecast,
            'day_active': int(day)
        }
    )
	

@login_required(login_url='/login/')
def noticias(request, filter=None):
    if request.method=="POST":
        try:
            id = xmldatabaseinterface.getCategoryIdByName(str(request.body.decode('utf-8')))
            obj = {'status': "success", "id": id}
            return JsonResponse(obj)
        except:
            return JsonResponse({'status': "error"})
    else:
        if(filter==None):
            filter = 0
        news = dl.parse_newsXml(ds.get_newsXml(1, int(filter)))
        chat = render_chat(request.user.id)
        cat = xmldatabaseinterface.getAllNewsCategories()

        return render(
            request,
            'app/noticias.html',
            {
                'title': 'Notícias',
                'year': datetime.now().year,
                'news': news,
                'chat': chat,
                'categories':cat
            }
        )

@login_required(login_url='/login/')
def notas(request, status=None):
    if request.method == 'POST':
        notaform = NotaForm(request.POST)

        if notaform.is_valid():
            nome_cadeira = notaform.cleaned_data['nome_cadeira']
            ects = notaform.cleaned_data['ects']
            area = notaform.cleaned_data['area']
            year = notaform.cleaned_data['ano']
            semester = notaform.cleaned_data['semestre']
            grade = notaform.cleaned_data['nota']

            inserted = xmldatabaseinterface.insertCourse(request.user.id, nome_cadeira, ects, area, year, semester, grade)
            if inserted:
                # Show confirmation saying inserted
                return HttpResponseRedirect("/notas/status=success")
            else:
                # Show error saying not inserted
                return HttpResponseRedirect("/notas/status=error")
        else:
            return HttpResponseRedirect("/notas/status=error")
    else:
        chat = render_chat(request.user.id)
        grades = render_grades(request.user.id)
        form = NotaForm()

        return render(
            request,
            'app/notas.html',
            {
                'title': 'Notas',
                'year': datetime.now().year,
                'chat': chat,
                'notaform': form,
                'status': status,
                'grades': grades
            })

''' API to remove course from user '''
@login_required(login_url='/login/')
def remove_course(request):
    if request.method == 'POST':
        if 'name_remove' in request.POST:
            name_remove = request.POST['name_remove']
            if(xmldatabaseinterface.deleteCourse(request.user.id, name_remove)):
                return HttpResponse('success') # if everything is OK
            else:
                return HttpResponse('fail')

''' API to send message to user '''
@login_required(login_url='/login/')
def send_message(request):

    # If the request is a post, save message and send success json
    if (request.method=='POST'):
        try:
            user_id = request.user.id
            username = request.user.username
            date = datetime.now().strftime("%x %X")
            message = str(request.body.decode('utf-8'))
            inserted = xmldatabaseinterface.insertMessage(user_id, username, date, message)
            if inserted:
                obj = {'status': "success", "name": username, "timestamp": date}
                return JsonResponse(obj)
            else:
                return JsonResponse({'status': "error"})
        except:
            return JsonResponse({'status': "error"})

''' Transform the xml database using xslt to render the grades '''
def render_grades(user_id):
    # Get the xlst transform
    try:
        transform = ds.getGradesTransform()
    except:
        raise FileNotFoundError("Grades transform does not exist")

    tree = xmldatabaseinterface.getAllCoursesFromStudent(user_id)

    if tree != None:
        return transform(tree)

''' Transform the xml database using xslt to render the chat '''
def render_chat(user_id):
    # Get the xlst transform
    try:
        transform = ds.getChatTransform()
    except:
        raise FileNotFoundError("Chat transform does not exist")

    tree = xmldatabaseinterface.get_chat_database()

    return transform(tree, uid=str(user_id))

'''Returns the main plates for a week'''
def get_main_plates(ementa):
    main_p = [{}, {}, {}, {}, {}, {}, {}]

    if('Monday' in ementa):
        monday = ementa['Monday']
        for canteen in monday:
            for meal in monday[canteen]:
                for item in monday[canteen][meal]:
                    if "Prato" in item:
                        if (canteen not in main_p[0]):
                            main_p[0][canteen] = {}
                        if (meal not in main_p[0][canteen]):
                            main_p[0][canteen][meal] = {}
                        main_p[0][canteen][meal].update({item: monday[canteen][meal][item]})
    else:
        main_p[0] = {}

    if('Tuesday' in ementa):
        tuesday = ementa['Tuesday']
        for canteen in tuesday:
            for meal in tuesday[canteen]:
                for item in tuesday[canteen][meal]:
                    if "Prato" in item:
                        if (canteen not in main_p[1]):
                            main_p[1][canteen] = {}
                        if (meal not in main_p[1][canteen]):
                            main_p[1][canteen][meal] = {}
                        main_p[1][canteen][meal].update({item: tuesday[canteen][meal][item]})
    else:
        main_p[1] = {}

    if('Wednesday' in ementa):
        wednesday = ementa['Wednesday']
        for canteen in wednesday:
            for meal in wednesday[canteen]:
                for item in wednesday[canteen][meal]:
                    if "Prato" in item:
                        if (canteen not in main_p[2]):
                            main_p[2][canteen] = {}
                        if (meal not in main_p[2][canteen]):
                            main_p[2][canteen][meal] = {}
                        main_p[2][canteen][meal].update({item: wednesday[canteen][meal][item]})
    else:
        main_p[2] = {}

    if('Thursday' in ementa):
        thursday = ementa['Thursday']
        for canteen in thursday:
            for meal in thursday[canteen]:
                for item in thursday[canteen][meal]:
                    if "Prato" in item:
                        if (canteen not in main_p[3]):
                            main_p[3][canteen] = {}
                        if (meal not in main_p[3][canteen]):
                            main_p[3][canteen][meal] = {}
                        main_p[3][canteen][meal].update({item: thursday[canteen][meal][item]})
    else:
        main_p[3] = {}

    if('Friday' in ementa):
        friday = ementa['Friday']
        for canteen in friday:
            for meal in friday[canteen]:
                for item in friday[canteen][meal]:
                    if "Prato" in item:
                        if (canteen not in main_p[4]):
                            main_p[4][canteen] = {}
                        if (meal not in main_p[4][canteen]):
                            main_p[4][canteen][meal] = {}
                        main_p[4][canteen][meal].update({item: friday[canteen][meal][item]})
    else:
        main_p[4] = {}

    if('Saturday' in ementa):
        saturday = ementa['Saturday']
        for canteen in saturday:
            for meal in saturday[canteen]:
                for item in saturday[canteen][meal]:
                    if "Prato" in item:
                        if (canteen not in main_p[5]):
                            main_p[5][canteen] = {}
                        if (meal not in main_p[5][canteen]):
                            main_p[5][canteen][meal] = {}
                        main_p[5][canteen][meal].update({item: saturday[canteen][meal][item]})
    else:
        main_p[5] = {}

    if('Sunday' in ementa):
        sunday = ementa['Sunday']
        for canteen in sunday:
            for meal in sunday[canteen]:
                for item in sunday[canteen][meal]:
                    if "Prato" in item:
                        if (canteen not in main_p[6]):
                            main_p[6][canteen] = {}
                        if (meal not in main_p[6][canteen]):
                            main_p[6][canteen][meal] = {}
                        main_p[6][canteen][meal].update({item: sunday[canteen][meal][item]})
    else:
        main_p[6] = {}

    return main_p
