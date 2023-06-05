from datetime import datetime
import os
import Calculations as cals
from sqlite3.dbapi2 import Cursor
import sys
import sqlite3
from flask import Flask , render_template , redirect, request, url_for
from twilio.rest import Client
import math 
import random as r
empty_string = ""
currentdirectory = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__) #creating the Flask class object   

@app.route('/', methods=['POST','GET'])   
def home():
    global userEmail_t
    global details_user
    if request.method == "POST":
        val = request.form['submit-button']
        if val[0]=='L':
            if val[7]=='U':
                useremail = request.form["loginEmail"]
                userEmail_t = useremail
                password = request.form["loginPassword"]
                connection = sqlite3.connect(currentdirectory + "\mydb3.db")
                cursor = connection.cursor()
                query1 = "SELECT password FROM user_details WHERE useremail = '{A}'".format(A=useremail)
                result = cursor.execute(query1)
                result = result.fetchall()[0][0]
                connection.commit()
                if(password == result):
                    query1 = "SELECT username FROM user_details WHERE useremail = '{A}'".format(A=useremail)
                    result = cursor.execute(query1)
                    result = result.fetchall()[0][0]
                    usr = result
                    error = ""
                    return redirect(url_for("login",useremail=userEmail_t,usr=usr))
                else:
                    error = 'Incorrect Password'
                    return render_template('login.html',useremail=useremail,error=error,admin_error="",hotel_error="",hotel_id="")

            elif val[7]=='A':
                password = request.form["loginPassword"]
                if password == "Admin@973":
                    return redirect(url_for("adminpage"))
                else:
                    error = 'Incorrect Password'
                    return render_template('login.html',error="",admin_error=error,hotel_error="",hotel_id="")
            else:
                hotelrecep_ID = request.form["loginID"]
                password = request.form["loginPassword"]
                connection = sqlite3.connect(currentdirectory + "\mydb3.db")
                cursor = connection.cursor()
                query1 = "SELECT * FROM hotel_details WHERE hotel_id = '{A}'".format(A=hotelrecep_ID)
                result = cursor.execute(query1)
                result = result.fetchall()[0][0]
                connection.commit()
                if(len(result)!=0):
                    query1 = "SELECT hotel_pwd FROM hotel_details WHERE hotel_id = '{A}'".format(A=hotelrecep_ID)
                    result = cursor.execute(query1)
                    result = result.fetchall()[0][0]
                    connection.commit()
                    if(password == result):
                        error = ""
                        return redirect(url_for("hotel_home_page",hotel_id=hotelrecep_ID))
                    else:
                        error = 'Incorrect Password'
                        return render_template('login.html',hotel_id=hotelrecep_ID,error="",admin_error="",hotel_error=error)
        else:
            if val[8]=='U':
                newusername = request.form["newUserName"]
                newuseremail = request.form["newUserEmail"]
                newuserpass = request.form["newUserPassword"]
                newusermobnum = request.form["newUserMobileNo"]
                newuser_dob = request.form["newUserDOB"]
                userEmail_t = newuseremail   
                connection = sqlite3.connect(currentdirectory + "\mydb3.db")
                cursor = connection.cursor()
                query1 = "INSERT INTO user_details VALUES('{A}','{B}','{C}',{D},'{E}','',0)".format(A=newuseremail,B=newusername,C=newuserpass,D=newusermobnum,E=newuser_dob)
                cursor.execute(query1)
                connection.commit()
                return redirect(url_for("login",usr=newusername))
    else:
        return render_template('login.html',useremail=empty_string,hotel_id=empty_string,error="",admin_error="",hotel_error="")    

@app.route('/<useremail>/<usr>',methods=['POST','GET'])   
def login(useremail,usr):
    connection = sqlite3.connect(currentdirectory + "\mydb3.db")
    cursor = connection.cursor()
    if request.method == "POST":
        date_time = request.form["time"]
        datetime1 = str(request.form["time"])
        pick_point = request.form["pickpoint"]
        drop_point = request.form["droppoint"]
        htl_id_str = request.form['proceed-button']
        htl_id_li = htl_id_str.split(",")
        adults = []
        kids = []
        for x in htl_id_li:
            st = str(int(x[2:]) - 1)
            adults.append(request.form["adults{A}".format(A=st)])
            kids.append(request.form["kids{A}".format(A=st)])
        temp = 0
        for i in range(len(adults)):
            temp = temp + int(adults[i])
        for i in range(len(kids)):
            temp = temp + int(kids[i])
        adults = ','.join(str(x) for x in adults)
        kids = ','.join(str(x) for x in kids)
        query3 = "INSERT INTO trips_booked VALUES('{A}','{F}','{B}','{C}','{D}',{E})".format(A=useremail,B=date_time,C=pick_point,D=drop_point,F=htl_id_str,E=temp)
        cursor.execute(query3)
        connection.commit()
        return redirect(url_for("booknow",useremail=useremail,usr=usr,htl_id_list=htl_id_str,adults=adults,kids=kids))
    else:
        query1 = "SELECT * FROM user_details WHERE useremail = '{A}'".format(A=useremail)
        result = cursor.execute(query1)
        result = result.fetchall()
        details_user = [str(x) for x in list(result[0])[:-2]]
        query0 = "SELECT DISTINCT(location) FROM tourist_places"
        result = cursor.execute(query0)
        result = result.fetchall()
        location = []
        for temp in result:
            location.append(list(temp)[0])
        query0 = "SELECT * FROM tourist_places"
        result = cursor.execute(query0)
        result = result.fetchall()
        list_list = []
        for temp in result:
            list_list.append(list(temp))
        return render_template("home.html",user=usr,list_list=list_list,len=len(list_list),location=location,len_location=len(location),details_user=details_user)  

@app.route('/booknow/<useremail>/<usr>/<htl_id_list>/<adults>/<kids>',methods=['POST','GET'])   
def booknow(useremail,usr,htl_id_list,adults,kids):
    global mobno
    if request.method=="POST":
        # # Your Account SID from twilio.com/console
        # account_sid = "ACbb42399a3a131fc72d09732d782a628e"
        # # Your Auth Token from twilio.com/console
        # auth_token  = "5ec600ede51b815b0b9cca126ec70206"

        # client = Client(account_sid, auth_token)

        # message = client.messages.create(
        #     to=str(mobno), 
        #     from_="+18454796752",
        #     body="Thank You for Selecting Bon Voyage Web App. You can pay the amount to the mobile number +91 6303781102 via PhonePe or Paytm or GooglePay ")
        connection = sqlite3.connect(currentdirectory + "\mydb3.db")
        cursor = connection.cursor()
        query1 = "UPDATE user_details set no_of_trips=no_of_trips+1 WHERE useremail = '{A}'".format(A=useremail)
        cursor.execute(query1)
        connection.commit()
        return redirect(url_for("login",useremail=useremail,usr=usr))
    else:
        connection = sqlite3.connect(currentdirectory + "\mydb3.db")
        cursor = connection.cursor()
        htl_id_list = htl_id_list.split(",")
        for x in htl_id_list:
            print(str(int(x[2:])))
        htl_names = []
        htl_locs = []
        for htl_id in htl_id_list:
            print(htl_id)
            query2 = "SELECT title,location FROM tourist_places WHERE place_id = '{A}'".format(A=htl_id)
            result = cursor.execute(query2)
            result = result.fetchall()[0]
            htl_names.append(result[0])
            htl_locs.append(result[1])
        query2 = "SELECT mobile_no FROM user_details WHERE useremail = '{A}'".format(A=useremail)
        result = cursor.execute(query2)
        mobno = result.fetchall()[0][0]
        result = str(mobno)
        firstno = result[:3]
        lastno = result[-4:]
        total = []
        prices = []
        
        #   Genetic Algorithm is used in parts which includes the 1)fitness algorithm
        #   Fitness algorithm is used in terms of mathematical equation which is used
        #   to maximize or minimize the budget values. 
        total_sum = 0
        adults = adults.split(",")
        kids = kids.split(",")
        for i in range(len(adults)):
            total.append(int(adults[i]) + int(kids[i]))
        connection = sqlite3.connect(currentdirectory + "\mydb3.db")
        cursor = connection.cursor()
        htls_selected = []
        type_of_room_selected = []
        temp = 0
        for x in htl_id_list:
            query3 = "SELECT price_per_person FROM tourist_places WHERE place_id = '{A}'".format(A=x)
            result = cursor.execute(query3)
            result = result.fetchall()[0][0]
            prices.append(result*total[temp])
            j = r.choice([0,1])
            if int(x[2:])<13:
                k = int(x[2:])*2 + j - 1
                if k<10:
                    query4 = "SELECT price_per_head_d,price_per_head_a,price_per_head_n FROM hotel_details WHERE hotel_id = '{A}'".format(A="".join(["HTL00",str(k)]))
                    htls_selected.append("".join(["HTL00",str(k)]))
                else:
                    query4 = "SELECT price_per_head_d,price_per_head_a,price_per_head_n FROM hotel_details WHERE hotel_id = '{A}'".format(A="".join(["HTL0",str(k)]))
                    htls_selected.append("".join(["HTL0",str(k)]))
            else:
                query4 = "SELECT price_per_head_d,price_per_head_a,price_per_head_n FROM hotel_details WHERE hotel_id = '{A}'".format(A="HTL025")
                htls_selected.append("HTL025")
            result = cursor.execute(query4)
            j = r.choice([0,1,2])
            result = result.fetchall()
            total_sum = total_sum + list(result[0])[j]*total[temp]
            cal = math.ceil(total[temp]/3)
            if j==0:
                query1 = "UPDATE hotel_details set no_of_deluxe_rooms=no_of_deluxe_rooms-{B} WHERE hotel_id = '{A}'".format(A=htls_selected[-1],B=cal)
                cursor.execute(query1)
                connection.commit()
                type_of_room_selected.append('D')
            elif j==1:
                query1 = "UPDATE hotel_details set no_of_ac_rooms=no_of_ac_rooms-{B} WHERE hotel_id = '{A}'".format(A=htls_selected[-1],B=cal)
                cursor.execute(query1)
                connection.commit()
                type_of_room_selected.append('A')
            else:
                query1 = "UPDATE hotel_details set no_of_nonac_rooms=no_of_nonac_rooms-{B} WHERE hotel_id = '{A}'".format(A=htls_selected[-1],B=cal)
                cursor.execute(query1)
                connection.commit()
                type_of_room_selected.append('N')
            temp = temp + 1

        total_sum = total_sum + sum(prices)*0.18
        return render_template("booking.html",user=usr,len = len(htl_names),htl_names=htl_names,htl_locs=htl_locs,firstno=firstno,lastno=lastno,total_sum=total_sum)  

@app.route('/adminpage/',methods=['POST','GET'])
def adminpage():
    if request.method=="POST":
       if(request.form["button-submit"]=="M"):
         title=request.form["Place-Title"]
         imgurl=request.form["Img-Url"]
         loc=request.form["Place-Loc"]
         prc=request.form["price"]
         print("place-title:",title)
         print("imgurl:",imgurl)
         print("loction:",loc)
         print("price:",prc)
         connection = sqlite3.connect(currentdirectory + "\mydb3.db")
         cursor = connection.cursor()
         query1 = "SELECT * FROM tourist_places"
         cursor.execute(query1)
         result = cursor.execute(query1)
         result = result.fetchall()
         connection.commit()
         length=len(result)+1
         id_temp="TP"
         if(length>=100):
           id_temp="".join([id_temp,str(length)])
         elif(length<100 or length>=10):
           id_temp=id_temp+'0'
           id_temp="".join([id_temp,str(length)])
         else:
           id_temp=id_temp+'00'
           id_temp="".join([id_temp,str(length)])  
         print("id_temp:",id_temp)
         query1 = "INSERT INTO tourist_places VALUES('{A}','{B}','{C}','{D}',{E})".format(A=id_temp,B=title,C=imgurl,D=loc,E=prc)
        #  cursor.execute(query1)
         result = cursor.execute(query1)
        #  result = result.fetchall()
         connection.commit()
         return render_template("adminhome.html") 
       else:
           hotel_name=request.form["Hotel-Name"]
           plc_loc=request.form["Place-Location"]
           dlxrmprc=request.form["Deluxe-Rooms-Price"]
           acrmprc=request.form["AC-Rooms-Price"]
           nonacrmprc=request.form["Non-AC-Rooms-Price"]
           dlxrm=request.form["Deluxe-Rooms"]
           acrm=request.form["AC-Rooms"]
           nonacrm=request.form["Non-AC-Rooms"]
           print("hotelnme:",hotel_name)
           print("location:",plc_loc)
           print("dlxrm:",dlxrmprc)
           print("acrm:",acrmprc)
           print("nonacrm:",nonacrmprc)
           print("dlxrms:",dlxrm)
           print("acrms:",acrm)
           print("nonacrms:",nonacrm)
           connection = sqlite3.connect(currentdirectory + "\mydb3.db")
           cursor = connection.cursor()
           query1 = "SELECT * FROM hotel_details"
           cursor.execute(query1)
           result = cursor.execute(query1)
           result = result.fetchall()
           connection.commit()
           length=len(result)+1
           id_temp="HTL"
           if(length>=100):
             id_temp="".join([id_temp,str(length)])
           elif(length<100 or length>=10):
             id_temp=id_temp+'0'
             id_temp="".join([id_temp,str(length)])
           else:
             id_temp=id_temp+'00'
             id_temp="".join([id_temp])  
           print("id_temp:",id_temp,str(length))
           query1 = "INSERT INTO hotel_details_ VALUES('{A}','{B}','{C}',{D},{E},{F},{G},{H},{I})".format(A=id_temp,B=hotel_name,C=plc_loc,E=dlxrmprc,G=acrmprc,I=nonacrmprc,D=dlxrm,F=acrm,H=nonacrm)
        #    cursor.execute(query1)
           result = cursor.execute(query1)
        #    result = result.fetchall()
           connection.commit()
           return render_template("adminhome.html")  
     
    else:
        return render_template("adminhome.html")

@app.route('/hotel_home_page/<hotel_id>', methods=["POST","GET"])
def hotel_home_page(hotel_id):
    connection = sqlite3.connect(currentdirectory + "\mydb3.db")
    cursor = connection.cursor()
    query1 = "SELECT total_no_of_deluxe_rooms,total_no_of_ac_rooms,total_no_of_nonac_rooms FROM hotel_details WHERE hotel_id='{A}'".format(A = hotel_id)
    result = cursor.execute(query1)
    result = result.fetchall()
    result = list(result[0])
    t_no_d = result[0]
    t_no_a = result[1]
    t_no_n = result[2]
    if request.method== "POST":
        deluxe_r_r = request.form["Deluxe-Rooms"]
        deluxe_p= request.form["Deluxe-Price"]
        ac_r_r = request.form["AC-Rooms"]
        ac_p= request.form["AC-Price"]
        nonac_r_r = request.form["Non-AC-Rooms"]
        nonac_p= request.form["Non-AC-Price"]
        
        query1 = "UPDATE hotel_details set no_of_deluxe_rooms={A},price_per_head_d={B},no_of_ac_rooms={C},price_per_head_a={D},no_of_nonac_rooms={E},price_per_head_n={F} WHERE hotel_id = '{G}'".format(A=deluxe_r_r,B=deluxe_p,C=ac_r_r,D=ac_p,E=nonac_r_r,F=nonac_p,G=hotel_id)
        cursor.execute(query1)
        connection.commit()
        return render_template("hotel_home_page.html",hotel_id=hotel_id,t_no_d = t_no_d, t_no_a = t_no_a, t_no_n = t_no_n)
    else:
        return render_template("hotel_home_page.html",hotel_id=hotel_id,t_no_d = t_no_d, t_no_a = t_no_a, t_no_n = t_no_n)  

if __name__ =='__main__':  
    app.run(debug = True)  