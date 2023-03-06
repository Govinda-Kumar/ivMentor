#from django.shortcuts import render
#from django.http import HttpResponse
import os
import base64
import tempfile
import datetime
from uuid import uuid4
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
#import pandas as pd
import random

from difflib import SequenceMatcher

from .models import *
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
from chatterbot import *

import pandas as pd
import random
from difflib import SequenceMatcher
from googlesearch import search
import json
import xlrd as xl
import openpyxl
import xlsxwriter




'''
def chatb(request):
    bot = ChatBot("Candice")
    conversation = [
        "Hello",
        "Hi there!",
        "How are you doing?",
        "I'm doing great.",
        "That is good to hear",
        "Thank you.",
        "You're welcome."
    ]

    trainer = ListTrainer(bot)
    trainer.train(conversation)

    # Training with English Corpus Data
    trainer_corpus = ChatterBotCorpusTrainer(bot)
    trainer_corpus.train(
        'chatterbot.corpus.english'
    )

    def get_bot_response():
        userText = request.GET.get('msg')
        print(userText)
        return str(bot.get_response(userText))
    map(get_bot_response(), '\get')

    return render(request, 'chatb.html') '''
def chatbox(request):
    print(request.POST.get('msg'))
    return render(request, 'chatboxx.html')

#Create your views here.
def home(request):
    return render(request, 'index.html')

def check_params(r, p):
    return all(list(map(lambda x: x in r and r[x].strip() != "", p)))


def registerpage(request):
    if request.method == "POST":
        if check_params(request.POST, ["email", "name", "phone", "dob", "password", "college"]):
            try:
                new_user = MyUser.objects.create_user(
                    request.POST["email"],
                    request.POST["password"],
                    request.POST["name"],
                    request.POST["phone"],
                    request.POST["dob"],
                    request.POST["college"],
                )
                if "profile" in request.FILES:
                    filename = os.path.join(tempfile.gettempdir(), str(uuid4())) + ".png"

                    with open(filename, "wb") as f:
                        for chunk in request.FILES["profile"].chunks():
                            f.write(chunk)
                    new_user.profile = base64.b64encode(open(filename, "rb").read()).decode()
                    new_user.save()
                    os.remove(filename)

                    new_user.generate_otp()
                    new_user.send_otp_in_mail()
                return redirect("/verify-otp")
            except ValidationError as e:
                for msg in e.messages:

                    messages.error(request, str(msg))
                return redirect("/register")
        else:
            return HttpResponse("<script>alert('Invalid Parameters!!'); window.location.href='/register'; </script>")
    elif request.method == "GET":
        return render(request, "register.html")
    else:
        return HttpResponse("<script>alert('Invalid HTTP method'); window.location.href='/register'; </script>")


def loginpage(request):
    if request.method == "GET":
        return render(request, "login.html")
    elif request.method == "POST":
        if check_params(request.POST, ["email", "password"]):
            u = authenticate(email=request.POST["email"], password=request.POST["password"])
            if u is not None:
                if u.verified == "Y":
                    login(request, u)
                    return redirect("/dashboard")
                else:
                    messages.error(request, "You need to verify your email address")
                    return redirect("/verify-otp")
            else:
                return HttpResponse("<script>alert('Invalid Credentials!!'); window.location.href='/login'; </script>")
        else:
            return HttpResponse("<script>alert('Invalid Parameters!!'); window.location.href='/login'; </script>")
    else:
        return HttpResponse("<script>alert('Invalid HTTP method'); window.location.href='/login'; </script>")


def logoutpage(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            logout(request)
            return HttpResponse("<script>alert('Logged out successfully!!'); window.location.href='/index'; </script>")
        else:
            return redirect("/login")
    else:
        return HttpResponse("<script>alert('Invalid HTTP method'); window.location.href='/logout'; </script>")


def verifypage(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/")
        else:
            return render(request, "verify-otp.html")
    elif request.method == "POST":
        if check_params(request.POST, ["email", "otp"]):
            try:
                u = MyUser.objects.get(email=request.POST["email"])
                if u.verified == "Y":
                    messages.error(request, "Already verified")
                    return redirect("/login")
                elif u.otp == "":
                    messages.error(request, "OTP not generated")
                    return redirect("/verify-otp")
                elif datetime.datetime.now() > u.otp_expire:
                    messages.error(request, "OTP expired")
                    return redirect("/verify-otp")
                elif u.otp == request.POST["otp"]:
                    u.verified = "Y"
                    u.otp = ""
                    u.otp_expire = datetime.datetime.now()
                    u.save()
                    messages.success(request, "Account verified")
                    return redirect("/login")
            except:
                pass
            messages.error(request, "Failed to verify OTP")
            return redirect("/verify-otp")
        if check_params(request.POST, ["email"]):
            try:
                u = MyUser.objects.get(email=request.POST["email"])
                if u.verified == "Y":
                    messages.error(request, "Already verified")
                    return redirect("<script>alert('Verified!!'); window.location.href='/login'; </script>")
                u.generate_otp()
                u.send_otp_in_mail()
                messages.success(request, "OTP generated")
                return redirect("/verify-otp")
            except:
                pass
            messages.error(request, "Failed to generate OTP")
            return redirect("/verify-otp")
        else:
            return HttpResponse("<script>alert('Invalid Parameters'); window.location.href='/verify-otp'; </script>")
    else:
        return HttpResponse("<script>alert('Invalid HTTP method'); window.location.href='/verify-otp'; </script>")


def feedbackpage(request):
    if request.method=='POST':
        name=request.POST['n']
        email=request.POST['e']
        feedback=request.POST['f']
        feed(name=name,email=email,feedback=feedback).save()
        return render(request,'save.html')
    else:
        return render(request,'feedback.html')

def dashboardpage(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return render(request, "dashboard.html")
        else:
            return redirect("/login")
    else:
        return HttpResponse("Invalid HTTP Response")

def placement(request):
    return render(request, 'placements.html')
def signin(request):
    return render(request, 'select.html')
def profile(request):
    return render(request, 'editProfile.html')
def college(request):
    return render(request, 'colleges.html')
def deloitte(request):
    return render(request, 'deloitte.html')
def wipro(request):
    return render(request, 'wipro.html')
def sap(request):
    return render(request, 'sap.html')
def tcs(request):
    return render(request, 'tcs.html')
def infosys(request):
    return render(request, 'infosys.html')
def cognizant(request):
    return render(request, 'cognizant.html')
def MBA(request):
    return render(request, 'MBA.html')
def MCA(request):
    return render(request, 'MCA.html')


def chatb(request):

    class iv:
        f = open(r"C:\Users\kumar\PycharmProjects\ivMentor\iv\static\basic.json")
        basic = json.load(f)
        q_a = pd.read_excel(r"C:\Users\kumar\PycharmProjects\ivMentor\iv\static\questions.xlsx", names=['question', 'answer'])
        questions = q_a['question']
        answers = q_a['answer']

        def data(self):
            data = pd.read_excel(r"C:\Users\kumar\PycharmProjects\ivMentor\iv\static\stocks.xlsx", index_col=False)
            return data

        def similar(self, measure):
            if len([i for i in measure if i > 0.7]):
                return True
            else:
                return False

        def measure(self, s, q):
            measure = []
            for que in q:
                measure.append(SequenceMatcher(None, s, que).ratio())
            return measure

        def output(self, que, query=None, types=None):
            if types == 'basic':
                topic = self.basic[query]
                value = self.measure(que, topic['patterns'])
                return (max(value), random.choice(self.basic[query]['responses']))
            else:
                value = self.measure(que, self.questions)
                return (max(value), self.answers[value.index(max(value))])

        def insert_excel(self, path, user, contact, text):
            wb = xl.open_workbook(path)
            s1 = wb.sheet_by_index(0)
            row = s1.nrows
            col = 0
            workbook = xlsxwriter.Workbook(path)
            worksheet = workbook.add_worksheet()
            worksheet.write(row, col, user)
            worksheet.write(row, col + 1, contact)
            worksheet.write(row, col + 2, text)
            workbook.close()

        def agent(self):
            user = input("\nBefore we start, I want to know your name: ")
            print("Thanks for being here, iv is ready to talk!")
            while True:
                print('\n')
                question = input(user + ': ')
                output = {}
                for query in self.basic.keys():
                    fitness, answer = self.output(question, query, "basic")
                    output[fitness] = answer
                # print(output)
                ind = max(output.keys())
                if ind >= 0.8:
                    print("iv:", output[ind])
                    if (output[ind] in self.basic['bye']['responses']):
                        break
                    elif (output[ind] in self.basic['order']['responses']):
                        data = self.data()
                        print(data.iloc[:, :4].to_string(index=False))
                    elif (output[ind] in self.basic['suggestion']['responses']):
                        contact = input("Mail Id: ")
                        suggestion = input("Suggestion: ")
                        loc = r"C:\Users\kumar\PycharmProjects\ivMentor\iv\static\suggestion.xlsx"
                        self.insert_excel(loc, user, contact, suggestion)

                        print("iv: Thanks for the feedback! Anything More i can help you..")
                    elif (output[ind] in self.basic['complaint']['responses']):
                        contact = input("Mail Id: ")
                        complain = input("Complaint: ")
                        loc = r"C:\Users\kumar\PycharmProjects\ivMentor\iv\static\complain.xlsx"
                        self.insert_excel(loc, user, contact, complain)
                else:
                    fitness, answer = self.output(question)
                    if fitness > 0.6:
                        print("iv: ", answer)
                    else:
                        print("iv: pata nahi")

    q = iv()
    q.agent()

    return render(request, 'chatb.html')
