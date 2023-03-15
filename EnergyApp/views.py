import decimal
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required


from .forms import RegisterForm
from .models import Budget, ForumComment, ForumPost, UserProfile, EnergyProvider, Appliance, ApplianceUsage
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime, timezone, date
import json
from django.http import JsonResponse
from calendar import month_name
from django.db.models import Q
from django.urls import reverse
# Instantiate a storage client
from django.conf import settings
from google.cloud import storage


# Create your views here.


def login_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            userProfile = UserProfile(
                user=user, dob=form.cleaned_data['dob'], provider=form.cleaned_data['Energy_Provider'])
            userProfile.save()
            login(request, user)
            return redirect('/dashboard')

    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {"form": form})


@login_required(login_url="/login")
def profile(request):
    userProfile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        print('Printing POST:', request.POST)

        if request.POST.get('delete'):
            user = request.user
            user.delete()
            return redirect('homepage')
        
        if request.POST.get('delete_pic') and request.POST.get('username') == '' and request.POST.get('email') == '' and request.POST.get('dob') == '' and request.POST.get('provider') == '':
                storage_client = storage.Client(credentials=settings.GS_CREDENTIALS, project=settings.GS_PROJECT_ID)
                bucket = storage_client.bucket(settings.GS_BUCKET_NAME)
                print("shush")
                default_pic_path = 'static/images/defaultImage.svg'

                userProfile.picture = None
                userProfile.save()

        else:
            username = request.POST.get('username', '')
            email = request.POST.get('email', '')
            picture = request.FILES.get('profile_pic', '')
            dob = request.POST.get('dob', '')
            provider = request.POST.get('provider', '')

            user = User.objects.get(id=request.user.id)
            userProfile = user.userprofile

            if username:
                user.username = username
            if email:
                user.email = email
            if picture:
                # if userProfile.picture:
                    # os.remove(userProfile.picture.path)
                userProfile.picture = picture
            if dob:
                userProfile.dob = dob
            if provider:
                userProfile.provider = EnergyProvider.objects.get(name=provider)

            user.save()
            userProfile.save()

            return redirect('profile')

    return render(request, 'main/profile.html')


def homepage(request):
    return render(request, 'main/homepage.html')

def landing(request):
    return render(request, 'main/landing.html')


@login_required(login_url="/login")
def dashboard(request):
    userProfile = UserProfile.objects.get(user=request.user)
    todayAppliances = ApplianceUsage.objects.filter(date=date.today(), appliance__user=userProfile)
    providerInfo = userProfile.provider

    currentMonth = datetime.now().strftime("%B")
    currentYear = datetime.now().strftime("%Y")
    print(currentYear)  

    # Discussion forum display
    try:
        budget = Budget.objects.get(user=userProfile, month=currentMonth)
    except Budget.DoesNotExist:
        budget = None  # or set to a default value

    recentPosts = []
    sortedPosts = []
    for post in ForumPost.objects.all():
        try:
            latest_comment = post.comments.all().latest('createdAt')
            last_active = latest_comment.createdAt
        except ForumComment.DoesNotExist:
            last_active = post.createdAt
        recentPosts.append((post, last_active))

    sortedPosts = sorted(recentPosts, key=lambda x: x[1], reverse=True)
    # Discussion forum display end

    # Budget Display
    todayEDailyCost = 0
    todayGDailyCost = 0
    for usage in todayAppliances:
        if usage.appliance.applianceType == 'Electricity':
            wattage = usage.appliance.wattage
            duration = usage.duration

            print(todayEDailyCost, wattage, duration, providerInfo.elecPerKwh)
            todayEDailyCost = todayEDailyCost + (((wattage * duration)/1000) * providerInfo.elecPerKwh)

        elif usage.appliance.applianceType == 'Gas':
            wattage = usage.appliance.wattage
            duration = usage.duration

            todayGDailyCost = todayGDailyCost + (((wattage * duration)/1000) * providerInfo.gasPerKwh)


    todayEDailyCost = todayEDailyCost + (providerInfo.elecDailyCharge/100)
    todayGDailyCost = todayGDailyCost + (providerInfo.gasDailyCharge/100)
    
    if budget is not None:
        if budget.dailyElecCostBudget and budget.dailyElecCostBudget != 0.00 :
            eDailyPercent = round((todayEDailyCost / budget.dailyElecCostBudget) * 100)
        else:
            eDailyPercent = 0.00  

        if budget.dailyGasCostBudget and budget.dailyGasCostBudget !=0.00 :
            gDailyPercent = round((todayGDailyCost / budget.dailyGasCostBudget) * 100)
        else:
            gDailyPercent = 0.00
    else:
        eDailyPercent = 0.00
        gDailyPercent = 0.00

    todayEDailyCost = round(todayEDailyCost, 2)
    todayGDailyCost = round(todayGDailyCost, 2)
    # budget display end


    # Add Budget Button
    if request.method == 'POST':
        print(request.POST)
        try:
            addUpdatebudget = Budget.objects.get(user=userProfile, month=currentMonth)
            print(budget)
        except Budget.DoesNotExist:
            addUpdatebudget = Budget(user=userProfile, month=currentMonth)

        if request.POST.get('budgetType') == 'daily':
            if request.POST.get('dash_elec'):
                addUpdatebudget.dailyElecCostBudget = request.POST.get('daily_goal')
                print("sucessful??")
            if request.POST.get('dash_gas'):
                addUpdatebudget.dailyGasCostBudget = request.POST.get('daily_goal')
        
        elif request.POST.get('budgetType') == 'weekly':
            if request.POST.get('dash_elec'):
                addUpdatebudget.weeklyElecCostBudget = request.POST.get('weekly_goal')
            if request.POST.get('dash_gas'):
                addUpdatebudget.weeklyGasCostBudget = request.POST.get('weekly_goal')

        elif request.POST.get('budgetType') == 'monthly':
            if request.POST.get('dash_elec'):
                addUpdatebudget.monthlyElecCostBudget = request.POST.get('monthly_goal')
            if request.POST.get('dash_gas'):
                addUpdatebudget.monthlyGasCostBudget = request.POST.get('monthly_goal')
        
        addUpdatebudget.save()

        return redirect('/dashboard')
            
    # Add Budget button End

    # Charts display
    chartAppliances = Appliance.objects.filter(user=userProfile)
    applianceUsage = ApplianceUsage.objects.filter(appliance__in=chartAppliances).order_by('-date')
    # current_month = datetime.now().month
    labels = ['January', 'February', 'March', 'April', 'May', 'June']
    echartData = []
    gchartData = []

    gtotalMonthlyCosts = 0
    etotalMonthlyCosts = 0

    highestgDailyCost = 0
    highesteDailyCost = 0

    gasCostlyAppliance = ""
    elecCostlyAppliance = ""

    for month in range(1,13):
        etotalMonthlyCosts = 0
        gtotalMonthlyCosts = 0
        for usage in applianceUsage:
            if usage.appliance.applianceType == 'Electricity':
                if usage.date.month == month:
                    wattage = usage.appliance.wattage
                    duration = usage.duration

                    dailyCost = (((wattage * duration)/1000)* providerInfo.elecPerKwh)
                    weeklyCost = dailyCost * 7
                    monthlyCost = weeklyCost * 4

                    etotalMonthlyCosts = round(etotalMonthlyCosts + (((providerInfo.gasDailyCharge*28)/100)), 2)
                    etotalMonthlyCosts = etotalMonthlyCosts + monthlyCost

                    dailyCost = round(dailyCost, 2)
                    weeklyCost = round(weeklyCost, 2)
                    monthlyCost = round(monthlyCost, 2)

                    if dailyCost > highesteDailyCost:
                        highesteDailyCost = dailyCost

                        elecCostlyAppliance = f"{usage.appliance.name} ({usage.appliance.wattage} watts)"


            if usage.appliance.applianceType == 'Gas':
                if usage.date.month == month:
                    wattage = usage.appliance.wattage
                    duration = usage.duration

                    dailyCost = (((wattage * duration)/1000)* providerInfo.elecPerKwh)
                    weeklyCost = dailyCost * 7
                    monthlyCost = weeklyCost * 4

                    gtotalMonthlyCosts = round(etotalMonthlyCosts + (((providerInfo.gasDailyCharge*28)/100)), 2)
                    gtotalMonthlyCosts = gtotalMonthlyCosts + monthlyCost

                    if dailyCost > highestgDailyCost:
                        highestgDailyCost = dailyCost


                        gasCostlyAppliance = f"{usage.appliance.name} ({usage.appliance.wattage} watts)"

        echartData.append(etotalMonthlyCosts)
        gchartData.append(gtotalMonthlyCosts)
    
    v1, v2, v3, v4, v5, v6, averageeHighest, averagegHighest = getUsage(request)
    print(gasCostlyAppliance, "  ", elecCostlyAppliance)
    print(averageeHighest, averagegHighest)


    echartData = [float(x) if isinstance(x, decimal.Decimal) else x for x in echartData]
    gchartData = [float(x) if isinstance(x, decimal.Decimal) else x for x in gchartData]
    print(echartData)
    # End chart display

    context = {
        "todayEDailyCost": todayEDailyCost,
        "todayGDailyCost": todayGDailyCost,

        "budget": budget,
        "currentMonth": currentMonth,
        "currentYear": currentYear,
        "providerInfo": providerInfo,

        "eDailyPercent": eDailyPercent,
        "gDailyPercent": gDailyPercent,

        "sortedPosts": sortedPosts,

        "labels": labels,
        "echartData": echartData,
        "gchartData": gchartData,
        "averageeHighest": averageeHighest,
        "averagegHighest": averagegHighest,
        "gasCostlyAppliance": gasCostlyAppliance,
        "elecCostlyAppliance": elecCostlyAppliance,
    }
    return render(request, 'main/dashboard.html', context)


def switch_appliances(request, month, type):
    if request.method == "GET":
        userProfile = UserProfile.objects.get(user=request.user)
        providerInfo = userProfile.provider

        # create an empty list to store the data for the appliances for the specified month
        appliances_data = []
        totalDailyCosts = 0
        totalWeeklyCosts = 0
        totalMonthlyCosts = 0

        month_number = datetime.strptime(month, '%B').month
        if (type == "electricity"):
            appliances = Appliance.objects.filter(
                user=userProfile, applianceType="Electricity")
            applianceUsage = ApplianceUsage.objects.filter(
                appliance__in=appliances, date__month=month_number).order_by('-date')

            for usage in applianceUsage:
                appliance_data = {
                    "id": usage.appliance.id,
                    "name": usage.appliance.name,
                    "wattage": usage.appliance.wattage,
                    "duration": usage.duration,
                    "date": usage.date,
                }
                appliances_data.append(appliance_data)

                if (request.META.get('HTTP_X_CUSTOM_HEADER') == 'costs'):
                    dailyCost = ((usage.appliance.wattage *
                                 usage.duration)/1000) * providerInfo.elecPerKwh

                    weeklyCost = dailyCost * 7
                    monthlyCost = weeklyCost * 4

                    totalDailyCosts = totalDailyCosts + dailyCost
                    totalWeeklyCosts = totalWeeklyCosts + weeklyCost
                    totalMonthlyCosts = totalMonthlyCosts + monthlyCost

                    dailyCost = round(dailyCost, 2)
                    weeklyCost = round(weeklyCost, 2)
                    monthlyCost = round(monthlyCost, 2)

                    appliance_data.update({"dailyCosts": dailyCost})
                    appliance_data.update({"weeklyCosts": weeklyCost})
                    appliance_data.update({"monthlyCosts": monthlyCost})

            if (totalDailyCosts > 0):
                totalDailyCosts = round(
                    totalDailyCosts + (providerInfo.elecDailyCharge/100), 2)
                totalWeeklyCosts = round(
                    totalWeeklyCosts + (((providerInfo.elecDailyCharge*7)/100)), 2)
                totalMonthlyCosts = round(
                    totalMonthlyCosts + (((providerInfo.elecDailyCharge*28)/100)), 2)

                # appliances_data = sorted(
                #     appliances_data, key=lambda k: k['date'], reverse=True)

        elif (type == "gas"):
            appliances = Appliance.objects.filter(
                user=userProfile, applianceType="Gas")
            applianceUsage = ApplianceUsage.objects.filter(
                appliance__in=appliances, date__month=month_number).order_by('-date')

            for usage in applianceUsage:
                appliance_data = {
                    "id": usage.appliance.id,
                    "name": usage.appliance.name,
                    "wattage": usage.appliance.wattage,
                    "duration": usage.duration,
                    "date": usage.date
                }
                appliances_data.append(appliance_data)

                if (request.META.get('HTTP_X_CUSTOM_HEADER') == 'costs'):
                    dailyCost = ((usage.appliance.wattage *
                                 usage.duration)/1000) * providerInfo.elecPerKwh

                    weeklyCost = dailyCost * 7
                    monthlyCost = weeklyCost * 4

                    totalDailyCosts = totalDailyCosts + dailyCost
                    totalWeeklyCosts = totalWeeklyCosts + weeklyCost
                    totalMonthlyCosts = totalMonthlyCosts + monthlyCost

                    dailyCost = round(dailyCost, 2)
                    weeklyCost = round(weeklyCost, 2)
                    monthlyCost = round(monthlyCost, 2)

                    appliance_data.update({"dailyCosts": dailyCost})
                    appliance_data.update({"weeklyCosts": weeklyCost})
                    appliance_data.update({"monthlyCosts": monthlyCost})

            if (totalDailyCosts > 0):
                totalDailyCosts = round(
                    totalDailyCosts + (providerInfo.gasDailyCharge/100), 2)
                totalWeeklyCosts = round(
                    totalWeeklyCosts + (((providerInfo.gasDailyCharge*7)/100)), 2)
                totalMonthlyCosts = round(
                    totalMonthlyCosts + (((providerInfo.gasDailyCharge*28)/100)), 2)
                # appliances_data = sorted(
                #     appliances_data, key=lambda k: k['date'], reverse=True)

        else:
            return JsonResponse("ERRORR went into else statement", safe=False)

        if (request.META.get('HTTP_X_CUSTOM_HEADER') == 'costs'):
            costsDict = {'totalDailyCosts': totalDailyCosts,
                         'totalWeeklyCosts': totalWeeklyCosts, 'totalMonthlyCosts': totalMonthlyCosts}
            appliances_data.append(costsDict)

        print("APPLIANCE EDATA", appliances_data)

        return JsonResponse(appliances_data, safe=False)


def manage_appliances(request, appliance_id=None):
    if request.method == 'GET':
        userProfile = UserProfile.objects.get(user=request.user)
        appliances = Appliance.objects.filter(user=userProfile)

        appliances_data = []
        for appliance in appliances:
            applianceUsage = ApplianceUsage.objects.get(appliance=appliance)
            appliances_data.append({
                'id': appliance.id,
                'name': appliance.name,
                'wattage': appliance.wattage,
                'duration': applianceUsage.duration,
                'date': applianceUsage.date,
            })

        return JsonResponse(appliances_data, safe=False)

    elif (request.method == 'DELETE'):
        Appliance.objects.get(id=appliance_id).delete()
        return JsonResponse({'success': True})

    return JsonResponse(appliances_data, safe=False)


@login_required(login_url="/login")
def appliances(request):
    userProfile = UserProfile.objects.get(user=request.user)
    userAppliances = Appliance.objects.filter(
        user=userProfile)

    # where the field appliance, __in is in the appliances query set
    applianceUsage = ApplianceUsage.objects.filter(
        appliance__in=userAppliances).order_by('-date')

    currentMonth = datetime.now().strftime("%B")

    context = {
        "applianceUsage": applianceUsage,
        "userAppliances": userAppliances,
        "currentMonth": currentMonth,
    }

    if request.method == 'POST':
        print(request.POST)
        userProfile = UserProfile.objects.get(user=request.user)

        if (request.POST.get('appType') == 'electricity'):
            print("this is an electric appliance")

            elecAppliance = request.POST.get('electricity_appliance')
            elecApplianceName = request.POST.get('electricity_appliance_name')
            elecWattage = request.POST.get('electricity_wattage')
            elecDuration = request.POST.get('electricity_duration')
            elecDate = request.POST.get('electricity_date')

            if elecAppliance == "Other" or elecAppliance == "":
                if elecApplianceName == "":
                    createdAppliance = Appliance.objects.create(
                        applianceType="Electricity",
                        user=userProfile,
                        name="Other (Not Specified)",
                        wattage=elecWattage,
                    )
                else:
                    createdAppliance = Appliance.objects.create(
                        applianceType="Electricity",
                        user=userProfile,
                        name=elecApplianceName,
                        wattage=elecWattage,
                    )

                createdAppliance.save()
            else:
                createdAppliance = Appliance.objects.create(
                    applianceType="Electricity",
                    user=userProfile,
                    name=elecAppliance,
                    wattage=elecWattage,
                )
                createdAppliance.save()

            ApplianceUsage.objects.create(
                appliance=createdAppliance,
                duration=elecDuration,
                date=elecDate,
            ).save()

            if (request.POST.get('dash')):
                return redirect('/dashboard')
            
            return redirect('/appliances')

        if (request.POST.get('appType') == 'gas'):
            print("this is an gas appliance")

            gasAppliance = request.POST.get('gas_appliance')
            gasApplianceName = request.POST.get(
                'gas_appliance_name')
            gasWattage = request.POST.get('gas_wattage')
            gasDuration = request.POST.get('gas_duration')
            gasDate = request.POST.get('gas_date')

            if gasAppliance == "Other" or gasAppliance == "":
                if gasApplianceName == "":
                    createdAppliance = Appliance.objects.create(
                        applianceType="Gas",
                        user=userProfile,
                        name="Other (Not Specified)",
                        wattage=gasWattage,
                    )
                else:
                    createdAppliance = Appliance.objects.create(
                        applianceType="Gas",
                        user=userProfile,
                        name=gasApplianceName,
                        wattage=gasWattage,
                    )

                createdAppliance.save()
            else:
                createdAppliance = Appliance.objects.create(
                    applianceType="Gas",
                    user=userProfile,
                    name=gasAppliance,
                    wattage=gasWattage,
                )
                createdAppliance.save()

            ApplianceUsage.objects.create(
                appliance=createdAppliance,
                duration=gasDuration,
                date=gasDate,
            ).save()

            if (request.POST.get('dash')):
                return redirect('/dashboard')

            return redirect('/appliances')

        if request.POST.get('update'):
            updateName = request.POST.get('update_name', '')
            updateWattage = request.POST.get('update_wattage', '')
            updateDuration = request.POST.get('update_duration', '')
            updateDate = request.POST.get('update_date', '')

            specificAppliance = Appliance.objects.get(
                id=request.POST.get('id'))
            specificUsage = ApplianceUsage.objects.get(
                appliance=specificAppliance)

            print(specificAppliance)

            if updateName:
                specificAppliance.name = updateName
            if updateWattage:
                specificAppliance.wattage = updateWattage
            if updateDuration:
                specificUsage.duration = updateDuration
            if updateDate:
                specificUsage.date = updateDate

            specificUsage.save()
            specificAppliance.save()
            return render(request, 'main/appliances.html', context)

    return render(request, 'main/appliances.html', context)


@login_required(login_url="/login")
def usage(request):
    userProfile = UserProfile.objects.get(user=request.user)
    providerInfo = userProfile.provider

    userProfile = UserProfile.objects.get(user=request.user)
    appliances = Appliance.objects.filter(user=userProfile)
    # where the field appliance, __in is in the appliances query set
    applianceUsage = ApplianceUsage.objects.filter(appliance__in=appliances).order_by('-date')
    currentMonth = datetime.now().strftime("%B")

    applianceDailyCosts = {}
    applianceWeeklyCosts = {}
    applianceMonthlyCosts = {}

    etotalDailyCosts = 0
    etotalWeeklyCosts = 0
    etotalMonthlyCosts = 0

    gtotalDailyCosts = 0
    gtotalWeeklyCosts = 0
    gtotalMonthlyCosts = 0

    highesteDailyCost = 0
    highesteWeeklyCost = 0
    highesteMonthlyCost = 0
    highestgDailyCost = 0
    highestgWeeklyCost = 0
    highestgMonthlyCost = 0

    averageeHighest = 0
    averagegHighest = 0

    elecCostlyAppliance = ""
    gasCostlyAppliance = ""

    for usage in applianceUsage:
        if usage.appliance.applianceType == 'Electricity':
            if usage.date.strftime("%B") == currentMonth:
                wattage = usage.appliance.wattage
                duration = usage.duration

                dailyCost = (((wattage * duration)/1000)
                             * providerInfo.elecPerKwh)
                weeklyCost = dailyCost * 7
                monthlyCost = weeklyCost * 4

                etotalDailyCosts = etotalDailyCosts + dailyCost
                etotalWeeklyCosts = etotalWeeklyCosts + weeklyCost
                etotalMonthlyCosts = etotalMonthlyCosts + monthlyCost

                dailyCost = round(dailyCost, 2)
                weeklyCost = round(weeklyCost, 2)
                monthlyCost = round(monthlyCost, 2)

                if dailyCost > highesteDailyCost:
                    highesteDailyCost = dailyCost
                    highesteWeeklyCost = weeklyCost
                    highesteMonthlyCost = monthlyCost

                    elecCostlyAppliance = f"{usage.appliance.name} ({usage.appliance.wattage} watts)"

                applianceDailyCosts[usage.appliance.id] = dailyCost
                applianceWeeklyCosts[usage.appliance.id] = weeklyCost
                applianceMonthlyCosts[usage.appliance.id] = monthlyCost

        elif usage.appliance.applianceType == 'Gas':
            if usage.date.strftime("%B") == currentMonth:
                wattage = usage.appliance.wattage
                duration = usage.duration

                dailyCost = (((wattage * duration)/1000)
                             * providerInfo.gasPerKwh)
                weeklyCost = dailyCost * 7
                monthlyCost = weeklyCost * 4

                gtotalDailyCosts = gtotalDailyCosts + dailyCost
                gtotalWeeklyCosts = gtotalWeeklyCosts + weeklyCost
                gtotalMonthlyCosts = gtotalMonthlyCosts + monthlyCost

                dailyCost = round(dailyCost, 2)
                weeklyCost = round(weeklyCost, 2)
                monthlyCost = round(monthlyCost, 2)

                if dailyCost > highestgDailyCost:
                    highestgDailyCost = dailyCost
                    highestgWeeklyCost = weeklyCost
                    highestgMonthlyCost = monthlyCost

                    gasCostlyAppliance = f"{usage.appliance.name} ({usage.appliance.wattage} watts)"

                applianceDailyCosts[usage.appliance.id] = dailyCost
                applianceWeeklyCosts[usage.appliance.id] = weeklyCost
                applianceMonthlyCosts[usage.appliance.id] = monthlyCost

    if (etotalDailyCosts > 0):
        etotalDailyCosts = round(
            etotalDailyCosts + (providerInfo.gasDailyCharge/100), 2)
        etotalWeeklyCosts = round(
            etotalWeeklyCosts + (((providerInfo.gasDailyCharge*7)/100)), 2)
        etotalMonthlyCosts = round(
            etotalMonthlyCosts + (((providerInfo.gasDailyCharge*28)/100)), 2)

    if (gtotalDailyCosts > 0):
        gtotalDailyCosts = round(
            gtotalDailyCosts + (providerInfo.gasDailyCharge/100), 2)
        gtotalWeeklyCosts = round(
            gtotalWeeklyCosts + (((providerInfo.gasDailyCharge*7)/100)), 2)
        gtotalMonthlyCosts = round(
            gtotalMonthlyCosts + (((providerInfo.gasDailyCharge*28)/100)), 2)

    if (etotalDailyCosts > 0):
        averageeHighest = round(((((highesteDailyCost/etotalDailyCosts)*100) + (
            (highesteWeeklyCost/etotalWeeklyCosts)*100) + ((highesteMonthlyCost/etotalMonthlyCosts)*100)) / 3), 0)

    if (gtotalDailyCosts > 0):
        averagegHighest = round(((((highestgDailyCost/gtotalDailyCosts)*100) + (
            (highestgWeeklyCost/gtotalWeeklyCosts)*100) + ((highestgMonthlyCost/gtotalMonthlyCosts)*100)) / 3), 0)

    context = {
        "providerInfo": providerInfo,
        "userAppliances": appliances,
        "applianceUsage": applianceUsage,
        "currentMonth": currentMonth,

        "applianceDailyCosts": applianceDailyCosts,
        "applianceWeeklyCosts": applianceWeeklyCosts,
        "applianceMonthlyCosts": applianceMonthlyCosts,

        "etotalDailyCosts": etotalDailyCosts,
        "etotalWeeklyCosts": etotalWeeklyCosts,
        "etotalMonthlyCosts": etotalMonthlyCosts,

        "gtotalDailyCosts": gtotalDailyCosts,
        "gtotalWeeklyCosts": gtotalWeeklyCosts,
        "gtotalMonthlyCosts": gtotalMonthlyCosts,

        "averageeHighest": averageeHighest,
        "elecCostlyAppliance": elecCostlyAppliance,
        "averagegHighest": averagegHighest,
        "gasCostlyAppliance": gasCostlyAppliance,
    }
    return render(request, 'main/usage.html', context=context)


def getUsage(request):
    userProfile = UserProfile.objects.get(user=request.user)
    providerInfo = userProfile.provider

    userProfile = UserProfile.objects.get(user=request.user)
    appliances = Appliance.objects.filter(user=userProfile)
    # where the field appliance, __in is in the appliances query set
    applianceUsage = ApplianceUsage.objects.filter(
        appliance__in=appliances).order_by('-date')
    currentMonth = datetime.now().strftime("%B")

    applianceDailyCosts = {}
    applianceWeeklyCosts = {}
    applianceMonthlyCosts = {}

    etotalDailyCosts = 0
    etotalWeeklyCosts = 0
    etotalMonthlyCosts = 0

    averageeHighest = 0
    averagegHighest = 0

    gtotalDailyCosts = 0
    gtotalWeeklyCosts = 0
    gtotalMonthlyCosts = 0

    highesteDailyCost = 0
    highesteWeeklyCost = 0
    highesteMonthlyCost = 0
    highestgDailyCost = 0
    highestgWeeklyCost = 0
    highestgMonthlyCost = 0


    for usage in applianceUsage:
        if usage.appliance.applianceType == 'Electricity':
            if usage.date.strftime("%B") == currentMonth:
                wattage = usage.appliance.wattage
                duration = usage.duration

                dailyCost = (((wattage * duration)/1000)
                             * providerInfo.elecPerKwh)
                weeklyCost = dailyCost * 7
                monthlyCost = weeklyCost * 4

                etotalDailyCosts = etotalDailyCosts + dailyCost
                etotalWeeklyCosts = etotalWeeklyCosts + weeklyCost
                etotalMonthlyCosts = etotalMonthlyCosts + monthlyCost

                dailyCost = round(dailyCost, 2)
                weeklyCost = round(weeklyCost, 2)
                monthlyCost = round(monthlyCost, 2)

                if dailyCost > highesteDailyCost:
                    highesteDailyCost = dailyCost
                    highesteWeeklyCost = weeklyCost
                    highesteMonthlyCost = monthlyCost

                applianceDailyCosts[usage.appliance.id] = dailyCost
                applianceWeeklyCosts[usage.appliance.id] = weeklyCost
                applianceMonthlyCosts[usage.appliance.id] = monthlyCost

        elif usage.appliance.applianceType == 'Gas':
            if usage.date.strftime("%B") == currentMonth:
                wattage = usage.appliance.wattage
                duration = usage.duration

                dailyCost = (((wattage * duration)/1000)
                             * providerInfo.gasPerKwh)
                weeklyCost = dailyCost * 7
                monthlyCost = weeklyCost * 4

                gtotalDailyCosts = gtotalDailyCosts + dailyCost
                gtotalWeeklyCosts = gtotalWeeklyCosts + weeklyCost
                gtotalMonthlyCosts = gtotalMonthlyCosts + monthlyCost

                dailyCost = round(dailyCost, 2)
                weeklyCost = round(weeklyCost, 2)
                monthlyCost = round(monthlyCost, 2)

                if dailyCost > highestgDailyCost:
                    highestgDailyCost = dailyCost
                    highestgWeeklyCost = weeklyCost
                    highestgMonthlyCost = monthlyCost

                applianceDailyCosts[usage.appliance.id] = dailyCost
                applianceWeeklyCosts[usage.appliance.id] = weeklyCost
                applianceMonthlyCosts[usage.appliance.id] = monthlyCost

    if (etotalDailyCosts > 0):
        etotalDailyCosts = round(
            etotalDailyCosts + (providerInfo.gasDailyCharge/100), 2)
        etotalWeeklyCosts = round(
            etotalWeeklyCosts + (((providerInfo.gasDailyCharge*7)/100)), 2)
        etotalMonthlyCosts = round(
            etotalMonthlyCosts + (((providerInfo.gasDailyCharge*28)/100)), 2)

    if (gtotalDailyCosts > 0):
        gtotalDailyCosts = round(
            gtotalDailyCosts + (providerInfo.gasDailyCharge/100), 2)
        gtotalWeeklyCosts = round(
            gtotalWeeklyCosts + (((providerInfo.gasDailyCharge*7)/100)), 2)
        gtotalMonthlyCosts = round(
            gtotalMonthlyCosts + (((providerInfo.gasDailyCharge*28)/100)), 2)

    if (etotalDailyCosts > 0):
        averageeHighest = round(((((highesteDailyCost/etotalDailyCosts)*100) + (
            (highesteWeeklyCost/etotalWeeklyCosts)*100) + ((highesteMonthlyCost/etotalMonthlyCosts)*100)) / 3), 0)

    if (gtotalDailyCosts > 0):
        averagegHighest = round(((((highestgDailyCost/gtotalDailyCosts)*100) + (
            (highestgWeeklyCost/gtotalWeeklyCosts)*100) + ((highestgMonthlyCost/gtotalMonthlyCosts)*100)) / 3), 0)

    return etotalDailyCosts, etotalWeeklyCosts, etotalMonthlyCosts, gtotalDailyCosts, gtotalWeeklyCosts, gtotalMonthlyCosts, averageeHighest, averagegHighest


@login_required(login_url="/login")
def budget(request):

    etotalDailyCosts, etotalWeeklyCosts, etotalMonthlyCosts, gtotalDailyCosts, gtotalWeeklyCosts, gtotalMonthlyCosts, averageeHighest, averagegHighest = getUsage(request)

    print(etotalWeeklyCosts)
    userProfile = UserProfile.objects.get(user=request.user)
    currentDate = datetime.now()
    currentMonth = currentDate.strftime("%B")

    currentBudget = Budget.objects.filter(user=userProfile, month=currentMonth)

    eDailyPercent = 0
    gDailyPercent = 0

    eWeeklyPercent = 0
    gWeeklyPercent = 0

    eMonthlyPercent = 0
    gMonthlyPercent = 0

    if currentBudget:
        for budget in currentBudget:
            if budget.dailyElecCostBudget:
                eDailyPercent = round(etotalDailyCosts / budget.dailyElecCostBudget * 100)
                
            if budget.dailyGasCostBudget:
                gDailyPercent = round(gtotalDailyCosts / budget.dailyGasCostBudget * 100)
                
            if budget.weeklyElecCostBudget:
                eWeeklyPercent = round(etotalWeeklyCosts / budget.weeklyElecCostBudget * 100)
                
            if budget.weeklyGasCostBudget:
                gWeeklyPercent = round(gtotalWeeklyCosts / budget.weeklyGasCostBudget * 100)

            if budget.monthlyElecCostBudget:
                eMonthlyPercent = round(etotalMonthlyCosts / budget.monthlyElecCostBudget * 100)
                
            if budget.monthlyGasCostBudget:
                gMonthlyPercent = round(gtotalMonthlyCosts / budget.monthlyGasCostBudget * 100)

    if request.method == 'POST':
        if currentBudget:
            if request.POST.get('electricity'):
                for budget in currentBudget:

                    dailyBudget = request.POST.get('edaily_goal', '')
                    dailyBudget = decimal.Decimal(dailyBudget) if dailyBudget else None

                    weeklyBudget = request.POST.get('eweekly_goal', '')
                    weeklyBudget = decimal.Decimal(weeklyBudget) if weeklyBudget else None

                    monthlyBudget = request.POST.get('emonthly_goal', '')
                    monthlyBudget = decimal.Decimal(monthlyBudget) if monthlyBudget else None


                    if dailyBudget:
                        budget.dailyElecCostBudget = dailyBudget
                    if weeklyBudget:
                        budget.weeklyElecCostBudget = weeklyBudget
                    if monthlyBudget:
                        budget.monthlyElecCostBudget = monthlyBudget

                    budget.save()

            if request.POST.get('gas'):
                for budget in currentBudget:

                    dailyBudget = request.POST.get('gdaily_goal', '')
                    dailyBudget = decimal.Decimal(dailyBudget) if dailyBudget else None

                    weeklyBudget = request.POST.get('gweekly_goal', '')
                    weeklyBudget = decimal.Decimal(weeklyBudget) if weeklyBudget else None

                    monthlyBudget = request.POST.get('gmonthly_goal', '')
                    monthlyBudget = decimal.Decimal(monthlyBudget) if monthlyBudget else None

                    if dailyBudget:
                        budget.dailyGasCostBudget = dailyBudget
                    if weeklyBudget:
                        budget.weeklyGasCostBudget = weeklyBudget
                    if monthlyBudget:
                        budget.monthlyGasCostBudget = monthlyBudget

                    budget.save()

        else:

            dElecCostBudget = request.POST.get('edaily_goal', '')
            dElecCostBudget = decimal.Decimal(dElecCostBudget) if dElecCostBudget else 0

            wElecCostBudget = request.POST.get('eweekly_goal', '')
            wElecCostBudget = decimal.Decimal(wElecCostBudget) if wElecCostBudget else 0

            mElecCostBudget = request.POST.get('emonthly_goal', '')
            mElecCostBudget = decimal.Decimal(mElecCostBudget) if mElecCostBudget else 0

            dGasCostBudget = request.POST.get('gdaily_goal', '')
            dGasCostBudget = decimal.Decimal(dGasCostBudget) if dGasCostBudget else 0

            wGasCostBudget = request.POST.get('gweekly_goal', '')
            wGasCostBudget = decimal.Decimal(wGasCostBudget) if wGasCostBudget else 0

            mGasCostBudget = request.POST.get('gmonthly_goal', '')
            mGasCostBudget = decimal.Decimal(mGasCostBudget) if mGasCostBudget else 0

            Budget.objects.create(
                user=userProfile,
                month=currentMonth,

                dailyElecCostBudget=dElecCostBudget,
                weeklyElecCostBudget=wElecCostBudget,
                monthlyElecCostBudget=mElecCostBudget,

                dailyGasCostBudget=dGasCostBudget,
                weeklyGasCostBudget=wGasCostBudget,
                monthlyGasCostBudget=mGasCostBudget,
            ).save()

        return redirect('budget')

    context = {
        "currentMonth": currentMonth,
        "budgetCosts": currentBudget,

        "etotalDailyCosts": etotalDailyCosts,
        "gtotalDailyCosts": gtotalDailyCosts,
        "etotalWeeklyCosts": etotalWeeklyCosts,
        "gtotalWeeklyCosts": gtotalWeeklyCosts,
        "etotalMonthlyCosts": etotalMonthlyCosts,
        "gtotalMonthlyCosts": gtotalMonthlyCosts,

        "eDailyPercent": eDailyPercent,
        "gDailyPercent": gDailyPercent,
        "eWeeklyPercent": eWeeklyPercent,
        "gWeeklyPercent": gWeeklyPercent,
        "eMonthlyPercent": eMonthlyPercent,
        "gMonthlyPercent": gMonthlyPercent,

    }
    return render(request, 'main/budget.html', context)


@login_required(login_url="/login")
def comparison(request):
    return render(request, 'main/comparison.html')


@login_required(login_url="/login")
def forum(request):
    userProfile = UserProfile.objects.get(user=request.user)
    userPosts = ForumPost.objects.order_by('-createdAt')
    totalUserPosts = ForumPost.objects.all().count()
    totalMembers = UserProfile.objects.all().count()

    recentPosts = []
    sortedPosts = []
    for post in ForumPost.objects.all():
        try:
            latest_comment = post.comments.all().latest('createdAt')
            last_active = latest_comment.createdAt
        except ForumComment.DoesNotExist:
            last_active = post.createdAt
        recentPosts.append((post, last_active))

    sortedPosts = sorted(recentPosts, key=lambda x: x[1], reverse=True)

    if request.method == 'POST':
        print('Printing POST:', request.POST)

        postTitle = request.POST.get('post_title')
        postDesc = request.POST.get('post_description')

        ForumPost.objects.create(
            title = postTitle,
            description = postDesc,
            createdBy = userProfile,
        ).save()

        return redirect('/forum')

    context = {
        "userPosts": userPosts,
        "totalUserPosts": totalUserPosts,
        "totalMembers": totalMembers,
        "sortedPosts": sortedPosts,
    }

    return render(request, 'main/forum.html', context)


@login_required(login_url="/login")
def post(request, id):
    specificPost = get_object_or_404(ForumPost, id=id)
    postComments =  ForumComment.objects.filter(post=specificPost)
    userProfile = UserProfile.objects.get(user=request.user)

    if (request.method == 'POST'):

        if request.POST.get('delete'):
            specificPost.delete()
            return redirect('forum')


        print('Printing POST:', request.POST)
        replyDesc = request.POST.get('reply_body')

        ForumComment.objects.create(
            post = specificPost,
            body = replyDesc,
            createdBy = userProfile,
        ).save()

        return redirect(f'/post/{id}')


    context = {
        'specificPost' : specificPost,
        'postComments': postComments
    }

    return render(request, 'main/post.html', context)

