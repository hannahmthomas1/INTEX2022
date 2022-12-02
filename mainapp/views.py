from decimal import Decimal
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .funcs import searchAPI, getById, getList
from .models import MealClass, FoodItem, FoodEntry, WaterEntry, UserInfo
from .models import Actuals
from .forms import LoginForm

import pandas as pd
import psycopg2
import json
import requests
from .forms import UserForm



# Create your views here.
def indexPageView(request) :
    
    userid = request.user.id
    print(userid)
    return render( request, 'index.html', {'id':userid})

def searchFoodView(request):
    foods = []
    food = request.GET['food']
    data = FoodItem.objects.filter(FoodName__contains=food).distinct('FoodName')[:5]
    for i in data:
        foods.append({
            'name':str(i.FoodName),
            'id':i.id
        })
    context = {
        'foods':foods
    }
    return render(request, 'searchresults.html', context)

def addFoodItem(request):
    return render(request, 'addfood.html')

def submitFoodItem(request):
    if request.method == 'POST':
        name = request.POST['name'].lower()
        sodium = request.POST['sodium']
        potassium = request.POST['potassium']
        phosphorus = request.POST['phosphorus']
        protein = request.POST['protein']

        food = FoodItem()
        food.FoodName = name
        food.Protein_g = protein
        food.Sodium_mg = sodium
        food.Potassium_mg = potassium
        food.Phosphate_mg = phosphorus
        food.save()

    return redirect(journalPageView)

def addFoodEntry(request):
    if request.method == 'POST':
        currentUser = UserInfo.objects.get(user=request.user.id).id
        
        user = request.user.id
        date = request.POST['EntryDate']
        meal = request.POST['meal']
        food = request.POST['foodID']
        servings = request.POST['servings']

        actuals = Actuals.objects.get(UserID=currentUser)
        foodInfo = FoodItem.objects.get(id=food)
        actuals.Protein_g += foodInfo.Protein_g * Decimal(servings)
        actuals.Phosphorous_mg += foodInfo.Phosphate_mg * Decimal(servings)
        actuals.Potassium_mg += foodInfo.Potassium_mg * Decimal(servings)
        actuals.Sodium_mg += foodInfo.Sodium_mg * Decimal(servings)
        actuals.save()

        entry = FoodEntry()
        entry.UserID = UserInfo.objects.get(user=user)
        entry.DateTime = date
        entry.FoodID = foodInfo
        entry.MealName = MealClass.objects.get(MealName=meal)
        entry.NumServings = servings
        entry.save()

    return redirect(displayjournalPageView)

def addWaterEntry(request):
    return render(request, 'addwaterentry.html')

def submitWaterEntry(request):
    if request.method == 'POST':
        userid = request.POST['userid']
        date = request.POST['EntryDate']
        amount = request.POST['amount']

        currentUser = UserInfo.objects.get(user=request.user.id).id
        actuals = Actuals.objects.get(UserID=currentUser)

        actuals.Water_L += Decimal(amount)
        actuals.save()

        waterEntry = WaterEntry()
        waterEntry.UserID = UserInfo.objects.get(user=request.user.id)
        waterEntry.DateTime = date
        waterEntry.Amount = amount
        waterEntry.save()
    return redirect(displayjournalPageView)

def editWaterEntry(request, id):
    entry = WaterEntry.objects.get(id=id)
    context = {
        'entry': entry
    }
    return render(request, 'editwaterentry.html', context)

def submitWaterChanges(request, id):
    entry = WaterEntry.objects.get(id=id)

    if request.method == 'POST':
        entry.DateTime = request.POST['EntryDate']
        entry.Amount = request.POST['amount']
        entry.save()

    return redirect(displayjournalPageView)
    

def deleteWaterEntry(request, id):
    amount = WaterEntry.objects.get(id=id).Amount
    currentUser = UserInfo.objects.get(user=request.user.id).id
    actuals = Actuals.objects.get(UserID=currentUser)

    actuals.Water_L -= Decimal(amount)
    actuals.save()

    WaterEntry.objects.get(id=id).delete()
    return redirect(displayjournalPageView)

def deleteFoodEntry(request, id):
    currentUser = UserInfo.objects.get(user=request.user.id).id
    actuals = Actuals.objects.get(UserID=currentUser)
    entry = FoodEntry.objects.get(id=id)
    food = entry.FoodID

    actuals.Protein_g -= food.Protein_g * entry.NumServings
    actuals.Phosphorous_mg -= food.Phosphate_mg * entry.NumServings
    actuals.Potassium_mg -= food.Potassium_mg * entry.NumServings
    actuals.Sodium_mg -= food.Sodium_mg * entry.NumServings
    actuals.save()

    FoodEntry.objects.get(id=id).delete()
    return redirect(displayjournalPageView)

def editFoodEntry(request, id):
    entry = FoodEntry.objects.get(id=id)
    
    context = {
        'entry' : entry,
        'meals':MealClass.objects.all()
    }
    return render(request, 'editfoodentry.html', context)

def foodChanges(request, id):
    entry = FoodEntry.objects.get(id=id)

    if request.method == 'POST':
        date = request.POST['EntryDate']
        meal = request.POST['meal']
        food = request.POST['foodID']
        servings = request.POST['servings']

        entry.DateTime = date
        entry.MealName = MealClass.objects.get(MealName=meal)
        entry.FoodID = FoodItem.objects.get(id=food)
        entry.NumServings = servings
        entry.save()

    return redirect(displayjournalPageView)



def getAPIList(request):
    getList(200)
    return HttpResponse('data')

def journalPageView(request) :
    meals = MealClass.objects.all()
    context = {'meals':meals}

    return render(request, 'journal.html', context)

def displayjournalPageView(request) :
    print(request.user)
    currentUser = UserInfo.objects.get(user=request.user.id).id
    waterEntries = WaterEntry.objects.all().values()
    foodEntries = FoodEntry.objects.all().values()
    food = []
    for i in foodEntries:
        rec = {}
        for key in dict(i):
            if key in ['id', 'NumServings']:
                if key == 'NumServings':
                    rec[key] = float(dict(i)[key])
                else:
                    rec[key] = dict(i)[key]
            elif key == 'UserID_id':
                rec[key] = UserInfo.objects.get(id=dict(i)[key]).id
            elif key == 'MealName_id':
                rec[key] = MealClass.objects.get(id=dict(i)[key]).MealName
            elif key == 'FoodID_id':
                rec[key] = FoodItem.objects.get(id=dict(i)[key]).FoodName
        food.append(rec)
    print(food)
    context = {
        'water':waterEntries,
        'food':food
    }
    return render( request, 'displayjournal.html', context)


def profilePageView(request) :
    UserInfo.objects.get(user = request.user.id).id
    obj = get_object_or_404(UserInfo, pk = UserInfo.objects.get(user = request.user.id).id)
    form = UserForm(request.POST or None, instance = obj)

    # if form.is_valid:
    #     form.save()
    return render( request, 'profile.html', {'form':form})

def updateProfile(request):
    UserInfo.objects.get(user = request.user.id).id
    obj = get_object_or_404(UserInfo, pk = UserInfo.objects.get(user = request.user.id).id)
    userinfo = obj
    if request.method == 'POST':
        FirstName = request.POST['FirstName']
        LastName = request.POST['LastName']
        DOB = request.POST['DOB']
        HeightFt = request.POST['HeightFt']
        HeightIn = request.POST['HeightIn']
        Weight = request.POST['Weight']
        Sex = request.POST['Sex']

        userinfo.FirstName = FirstName
        userinfo.LastName = LastName
        userinfo.DOB = DOB
        userinfo.HeightFt = HeightFt
        userinfo.HeightIn = HeightIn
        userinfo.Weight = Weight
        userinfo.Sex = Sex

        userinfo.save()
    return redirect(profilePageView)

def register(request):
    if request.method == "POST" :
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            
            # print(request.session['_auth_user_id'])
            # username = form.cleaned_data.get('username')
            # messages.success(request, f'Hi {username}, your account was created successfully')
            return HttpResponseRedirect('/login/')
    else :
        form = UserCreationForm

    return render(request, 'register.html', {'form': form})

def createuserPageView(request) :
    print(request.user.id)
    submitted = False
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            actualsEntry = Actuals()
            actualsEntry.UserID = UserInfo.objects.get(user = request.user.id)
            actualsEntry.Protein_g = 0
            actualsEntry.Sodium_mg = 0
            actualsEntry.Phosphorous_mg = 0
            actualsEntry.Potassium_mg = 0
            actualsEntry.Water_L = 0
            actualsEntry.save()
            return HttpResponseRedirect('/profile/')
    else:
        form = UserForm
        if 'submitted' in request.GET:
            submitted = True
    form = UserForm
    return render( request, 'createuser.html', {'form': form, 'submitted':submitted})

def login_redirect(request) :
    try:
        if UserInfo.objects.get(user = request.user.id) :
            return HttpResponseRedirect('/journal/')
    except:
        return HttpResponseRedirect('/createuser/')


def dashboardPageView(request):
    data = {}
    pdata = {}
    newvals = {}
    npvals = {}
    pkeys = []
    pvals = []
    keys = []
    values = []
    male = True
    obj = get_object_or_404(UserInfo, pk = UserInfo.objects.get(user = request.user.id).id)
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="nacho",
                                    host="localhost",
                                    port="5050",
                                    database="kidney_health")
        cursor = connection.cursor()
        postgreSQL_select_Query = f"select * from actuals inner join userinfo on userinfo.id = actuals.\"UserID_id\" where userinfo.id = {obj.id}"

        cursor.execute(postgreSQL_select_Query)
        print("Selecting rows from mobile table using cursor.fetchall")
        mobile_records = cursor.fetchall()

        print("Print each row and it's columns values")

        for row in mobile_records:
            print("Sodium = ", row[3])
            print("Potassium  = ", row[4])
            print("Phosphorous  = ", row[5])
            print("Protein g/kg  = ", row[1])
            print("Water L/Day  = ", row[2])
            Sodium = row[3]
            Potasium = row[4]
            Phosphorus = row[5]
            Protein = float(row[1])/(float(row[13])/float(2.205))
            Water = float(row[2])

        newvals = {'Sodium': row[3],
        "Potassium": row[4],
        "Phosphorous": row[5],
        }

        npvals = {"Protien g/kg": Protein,
        "Water L/Day": Water,}
        print('Sodium: ', Sodium)
        print('Protein: ', Protein)
    
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    data.update(newvals)
    pdata.update(npvals)
    for key, value in data.items():
        keys.append(key)
        values.append(value)
    for key, value in pdata.items():
        pkeys.append(key)
        pvals.append(value)
    if row[14] == 'W':
        male = False
    context = {
         'keys': keys,
         'values': values,
         'data': data,
         'pvals': pvals,
         'pkeys': pkeys,
         'Sodium': Sodium,
         'Potasium': Potasium,
         'Phosphorus': Phosphorus,
         'Protein': Protein,
         'Water': Water,
         'Gender': male
     }

    print(context)
    return render(request, 'dashboard.html', context)

def navView(request):
    return render( request, 'nav.html')

