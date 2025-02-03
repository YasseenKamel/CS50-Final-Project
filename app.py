import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
from functools import wraps
import os
import json
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3 as sql
import sys
from datetime import datetime
from datetime import date

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

con = None
con = sql.connect('data.db',check_same_thread=False)
db = con.cursor()
request_number_flag = 0

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/myorders", methods=["GET", "POST"])
@login_required
def myorders():
    if session["type"] != 'users':
        return render_template("error.html",error1 = 'Page not found.',username_display=session["username"])
    db.execute('SELECT * FROM orders WHERE user_id = ?;',(session["user_id"],))
    rows = db.fetchall()
    x = len(rows)
    data = [[] for i in range(x)]
    i = 0
    #id, status, priority, due date, equipment ID
    for a in rows:
        db.execute('SELECT * FROM equipment WHERE id = ?;',(a[12],))
        rows3 = db.fetchall()
        db.execute('SELECT * FROM managers WHERE id = ?;',(a[11],))
        rows4 = db.fetchall()
        y = 0
        for b in a:
            if y == 11:
                data[i].append(rows4[0][1])
            else:
                data[i].append(b)
            y += 1
        data[i][12]=rows3[0][1]
        db.execute('SELECT * FROM requests WHERE id = ?;',(a[0],))
        rows2 = db.fetchall()
        data[i].append(datetime.strptime(str(rows2[0][5]),'%d.%m.%Y').date())
        data[i].append(rows2[0][2])
        i += 1
    data.reverse()
    if request.method == "POST":
        if request.form.get("orderopen") != None:
            # I: stands for accepting or rejecting an incoming request (I14) accepts request number 14-10=4
            # I: and request (I-14) rejects request number 14-10=4
            s = request.form.get("orderopen")
            x = int(s[1:])
            x -= 10
            db.execute('SELECT * FROM orders WHERE id = ?;',(abs(x),))
            rows = db.fetchall()
            if x > 0:
                db.execute('SELECT * FROM steps WHERE order_id = ?;',(abs(x),))
                steps = db.fetchall()
                request_id = x
                db.execute('SELECT * FROM requests WHERE id = ?;',(abs(x),))
                reqdata1 = db.fetchall()
                reqdata = []
                reqdata.append(reqdata1[0][0])
                reqdata.append(reqdata1[0][1])
                reqdata.append(reqdata1[0][2])
                db.execute('SELECT * FROM users WHERE id = ?;',(reqdata1[0][3],))
                requsers = db.fetchall()
                reqdata.append(requsers[0][1])
                db.execute('SELECT * FROM managers WHERE id = ?;',(reqdata1[0][4],))
                reqmanagers = db.fetchall()
                db.execute('SELECT * FROM equipment WHERE id = ?;',(reqdata1[0][6],))
                reqeq = db.fetchall()
                reqdata.append(reqmanagers[0][1])
                reqdata.append(datetime.strptime(str(reqdata1[0][5]),'%d.%m.%Y').date())
                reqdata.append(reqeq[0][1])
                reqdata.append(reqdata1[0][7])
                db.execute('SELECT * FROM partsorder WHERE order_id = ?;',(abs(x),))
                partorder = db.fetchall()
                lenparts = len(partorder)
                #code,desc,quantity,price
                parts = [[] for i in range(lenparts)]
                i = 0
                for a in partorder:
                    db.execute('SELECT * FROM parts WHERE id = ?;',(a[2],))
                    part = db.fetchall()
                    parts[i].append(part[0][2])
                    parts[i].append(part[0][1])
                    parts[i].append(a[3])
                    parts[i].append(part[0][3])
                    i += 1
                db.execute('SELECT * FROM parts')
                allparts = db.fetchall()
                return render_template("order.html",username_display=session["username"],stat = "Update",description=rows[0][13],steps=steps,parts=parts,allparts=allparts,reqdata = reqdata,status = rows[0][1],orderdata=rows)
        elif request.form.get("options") == None:
            return render_template("myorders.html",username_display=session["username"])
        else:
            if int(request.form.get("options")) == 0:
                data.sort(key=lambda x:x[0])
            elif int(request.form.get("options")) == 1:
                data.sort(key=lambda x:x[1])
            elif int(request.form.get("options")) == 2:
                data.sort(key=lambda x:x[15])
            elif int(request.form.get("options")) == 3:
                data.sort(key=lambda x:x[14])
            elif int(request.form.get("options")) == 4:
                data.sort(key=lambda x:x[12])
            return render_template("myorders.html",data=data,username_display=session["username"],default=int(request.form.get("options")))
    else:
        return render_template("myorders.html",data=data,username_display=session["username"])



@app.route("/maker", methods=["GET", "POST"])
@login_required
def maker():
    if session["type"] != 'managers':
        return render_template("error.html",error1 = 'Page not found.',username_display=session["username"])
    db.execute('SELECT * FROM equipment;')
    rows = db.fetchall()
    db.execute('SELECT * FROM users;')
    rows1 = db.fetchall()
    equipment1=[]
    users1 = []
    for a in rows:
        equipment1.append(a[1])
        for b in rows1:
            if a[2] == b[0]:
                users1.append(b[1])
    db.execute('SELECT * FROM users;')
    rows2 = db.fetchall()
    users2=[]
    for a in rows2:
        users2.append(a[1])
    if request.method == "POST":
        description = request.form.get("description")
        now = datetime.today().strftime('%Y-%m-%d')
        date = request.form.get("due")
        priority = request.form.get("priority")
        equipment = request.form.get("equipment")
        user = request.form.get("user")
        if now > date:
            return render_template("error.html",error1 = "Please enter a valid due date.",username_display=session["username"])
        if equipment not in equipment1:
            return render_template("error.html",error1 = "Please enter a valid equipment code.",username_display=session["username"])
        if user not in users2:
            return render_template("error.html",error1 = "Please enter a valid maintenence engineer username.",username_display=session["username"])
        if int(priority) < 1:
            return render_template("error.html",error1 = "Please enter a positive number for priority.",username_display=session["username"])
        db.execute("SELECT * FROM users WHERE username = ?",(user,))
        useridq = db.fetchall()
        userid = useridq[0][0]
        db.execute("SELECT * FROM equipment WHERE name = ?",(equipment,))
        equipmentidq = db.fetchall()
        equipmentid = equipmentidq[0][0]
        year = ''
        day = ''
        month = ''
        i = 0
        for c in date:
            if c == '-':
                i += 1
            else:
                if i == 0:
                    year += c
                elif i == 1:
                    month += c
                else:
                    day += c
        date = day+'.'+month+'.'+year
        db.execute('INSERT INTO requests (status, priority, user_id, manager_id, due, equipment_id, description) VALUES (?,?,?,?,?,?,?);',("Pending",priority,userid,session["user_id"],date,equipmentid,description,))
        con.commit()
        db.execute('SELECT * FROM requests WHERE id = (SELECT MAX(id) FROM requests);')
        newreq = db.fetchall()
        session["newreq"] = newreq[0][0]
        return redirect("/")
    else:
        return render_template("maker.html",equipment=rows,users=rows1,equipment1=json.dumps(equipment1),users1=json.dumps(users1),username_display=session["username"],users2=users2)

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    db.execute('SELECT * FROM requests WHERE manager_id = ?;',(session["user_id"],))
    rows = db.fetchall()
    if request.method == "POST":
        if session["type"] == "managers":
            if request.form.get("delete") != None:
                idx = int(request.form.get("delete")) - 10
                db.execute('SELECT * FROM requests WHERE id = ?;',(idx,))
                target = db.fetchall()
                if target[0][1] != 'Pending':
                    return render_template("error.html",error1 = "Cannot delete request as it has been accepted. Please contact the maintenence engineer personally.",username_display=session["username"])
                db.execute('DELETE FROM requests WHERE id=?',(idx,))
                con.commit()
                return redirect("/")
            elif request.form.get("options") == None:
                db.execute('SELECT * FROM requests WHERE manager_id = ?;',(session["user_id"],))
                rows = db.fetchall()
                x = len(rows)
                data = [[] for i in range(x)]
                i = 0
                for a in rows:
                    db.execute('SELECT * FROM users WHERE id = ?;',(a[3],))
                    rows2 = db.fetchall()
                    db.execute('SELECT * FROM equipment WHERE id = ?;',(a[6],))
                    rows3 = db.fetchall()
                    y = 0
                    for b in a:
                        if y == 5:
                            data[i].append(datetime.strptime(str(b),'%d.%m.%Y').date())
                        else:
                            data[i].append(b)
                        y += 1
                    data[i][6]=rows3[0][1]
                    data[i][3] = rows2[0][1]
                    i += 1
                data.reverse()
                return render_template("index.html",data=data,username_display=session["username"],reqnum=0)
            elif int(request.form.get("options")) == 7:
                return redirect("/maker")
            else:
                db.execute('SELECT * FROM requests WHERE manager_id = ?;',(session["user_id"],))
                rows = db.fetchall()
                x = len(rows)
                data = [[] for i in range(x)]
                i = 0
                for a in rows:
                    db.execute('SELECT * FROM users WHERE id = ?;',(a[3],))
                    rows2 = db.fetchall()
                    db.execute('SELECT * FROM equipment WHERE id = ?;',(a[6],))
                    rows3 = db.fetchall()
                    y = 0
                    for b in a:
                        if y == 5:
                            data[i].append(datetime.strptime(str(b),'%d.%m.%Y').date())
                        else:
                            data[i].append(b)
                        y += 1
                    data[i][6]=rows3[0][1]
                    data[i][3] = rows2[0][1]
                    i += 1
                data.reverse()
                data.sort(key=lambda x:x[int(request.form.get("options"))])
                return render_template("index.html",data=data,default=int(request.form.get("options")),username_display=session["username"],reqnum=0)
        else:
            # I: stands for accepting or rejecting an incoming request (I14) accepts request number 14-10=4
            # I: and request (I-14) rejects request number 14-10=4
            db.execute('SELECT * FROM requests WHERE user_id = ? AND status = "Pending";',(session["user_id"],))
            rows = db.fetchall()
            x = len(rows)
            data = [[] for i in range(x)]
            i = 0
            for a in rows:
                db.execute('SELECT * FROM managers WHERE id = ?;',(a[4],))
                rows2 = db.fetchall()
                db.execute('SELECT * FROM equipment WHERE id = ?;',(a[6],))
                rows3 = db.fetchall()
                y = 0
                for b in a:
                    if y == 5:
                        data[i].append(datetime.strptime(str(b),'%d.%m.%Y').date())
                    else:
                        data[i].append(b)
                    y += 1
                data[i][6]=rows3[0][1]
                data[i][4] = rows2[0][1]
                i += 1
            data.reverse()
            if request.form.get("accept") != None:
                # I: stands for accepting or rejecting an incoming request (I14) accepts request number 14-10=4
                # I: and request (I-14) rejects request number 14-10=4
                s = request.form.get("accept")
                x = int(s[1:])
                if x < 0:
                    x += 10
                else:
                    x -= 10
                db.execute('SELECT * FROM requests WHERE id = ?;',(abs(x),))
                rows = db.fetchall()
                income = []
                income.append(abs(x))
                if x < 0:
                    income.append("Rejected")
                else:
                    income.append("Accepted")
                y = 0
                for a in rows[0]:
                    if y > 1:
                        income.append(a)
                    y += 1
                if x < 0:
                    db.execute('DELETE FROM requests WHERE id = ?;',(abs(x),))
                    con.commit()
                    db.execute('INSERT INTO requests (id, status, priority, user_id, manager_id, due, equipment_id, description) VALUES (?,?,?,?,?,?,?,?);',(income[0],income[1],income[2],income[3],income[4],income[5],income[6],income[7],))
                    con.commit()
                if x > 0:
                    db.execute('SELECT * FROM steps WHERE order_id = ?;',(abs(x),))
                    steps = db.fetchall()
                    request_id = x
                    db.execute('SELECT * FROM requests WHERE id = ?;',(abs(x),))
                    reqdata1 = db.fetchall()
                    reqdata = []
                    reqdata.append(reqdata1[0][0])
                    reqdata.append(reqdata1[0][1])
                    reqdata.append(reqdata1[0][2])
                    db.execute('SELECT * FROM users WHERE id = ?;',(reqdata1[0][3],))
                    requsers = db.fetchall()
                    reqdata.append(requsers[0][1])
                    db.execute('SELECT * FROM managers WHERE id = ?;',(reqdata1[0][4],))
                    reqmanagers = db.fetchall()
                    db.execute('SELECT * FROM equipment WHERE id = ?;',(reqdata1[0][6],))
                    reqeq = db.fetchall()
                    reqdata.append(reqmanagers[0][1])
                    reqdata.append(datetime.strptime(str(reqdata1[0][5]),'%d.%m.%Y').date())
                    reqdata.append(reqeq[0][1])
                    reqdata.append(reqdata1[0][7])
                    db.execute('SELECT * FROM partsorder WHERE order_id = ?;',(abs(x),))
                    partorder = db.fetchall()
                    lenparts = len(partorder)
                    #code,desc,quantity,price
                    parts = [[] for i in range(lenparts)]
                    i = 0
                    for a in partorder:
                        db.execute('SELECT * FROM parts WHERE id = ?;',(a[2],))
                        part = db.fetchall()
                        parts[i].append(part[0][2])
                        parts[i].append(part[0][1])
                        parts[i].append(a[3])
                        parts[i].append(part[0][3])
                        i += 1
                    db.execute('SELECT * FROM parts')
                    allparts = db.fetchall()
                    return render_template("order.html",username_display=session["username"],stat = "Create",description=income[7],steps=steps,parts=parts,allparts=allparts,reqdata = reqdata,status = 'Draft')
                return redirect("/")
            elif request.form.get("ordersubmit") != None:
                order = []
                #order[0] -> id
                order.append(request.form.get("ordersubmit"))
                #order[1] -> status
                order.append(request.form.get("status"))
                db.execute('SELECT * FROM requests WHERE id = ?;',(request.form.get("ordersubmit"),))
                reqdata1 = db.fetchall()
                #order[2] -> user_id
                order.append(reqdata1[0][3])
                #order[3] -> manager_id
                order.append(reqdata1[0][4])
                #order[4] -> equipment_id
                order.append(reqdata1[0][6])
                #order[5] -> description
                order.append(request.form.get("description"))

                db.execute('DELETE FROM steps WHERE order_id = ?;',(order[0],))
                con.commit()
                step_no = 1
                timecnt = 0
                wagecost = 0
                partcost = 0
                while request.form.get("step"+str(step_no+1)) != None:
                    stepdata=[]
                    stepdata.append(request.form.get("ordersubmit"))
                    stepdata.append(step_no)
                    if request.form.get("time"+str(step_no)) != '':
                        stepdata.append(request.form.get("time"+str(step_no)))
                    else:
                        stepdata.append(0)
                    timecnt += int(stepdata[2])
                    if request.form.get("workers"+str(step_no)) != '':
                        stepdata.append(request.form.get("workers"+str(step_no)))
                    else:
                        stepdata.append(0)
                    if request.form.get("wage"+str(step_no)) != '':
                        stepdata.append(request.form.get("wage"+str(step_no)))
                    else:
                        stepdata.append(0)
                    wagecost += int(stepdata[4]) * int(stepdata[2]) * int(stepdata[3])
                    if request.form.get("desc"+str(step_no)) != '':
                        stepdata.append(request.form.get("desc"+str(step_no)))
                    else:
                        stepdata.append('')
                    db.execute('INSERT INTO steps (order_id, number, time, workers, wage, description) VALUES (?,?,?,?,?,?);',(stepdata[0],stepdata[1],stepdata[2],stepdata[3],stepdata[4],stepdata[5],))
                    con.commit()
                    step_no += 1
                
                
                db.execute('DELETE FROM partsorder WHERE order_id = ?;',(order[0],))
                con.commit()
                part_no = 1
                while request.form.get("code"+str(part_no)) != None and request.form.get("code"+str(part_no)) != '':
                    partdata=[]
                    partdata.append(part_no)
                    db.execute('SELECT * FROM parts WHERE code = ?;',(request.form.get("code"+str(part_no)),))
                    curpart = db.fetchall()
                    partdata.append(curpart[0][0])
                    if request.form.get("quantity"+str(part_no)) != '':
                        partdata.append(request.form.get("quantity"+str(part_no)))
                    else:
                        partdata.append(0)
                    partcost += int(partdata[2]) * int(curpart[0][3])
                    partdata.append(request.form.get("ordersubmit"))
                    db.execute('INSERT INTO partsorder (number, part_id, quantity, order_id) VALUES (?,?,?,?);',(partdata[0],partdata[1],partdata[2],partdata[3],))
                    con.commit()
                    part_no += 1
                
                #order[6] -> tpc
                order.append(wagecost + partcost)
                #order[7] -> spc
                order.append(partcost)
                #order[8] -> wpc
                order.append(wagecost)
                #order[9] -> tpt
                order.append(timecnt)
                if order[1] == 'Completed':
                    #order[10] -> tat
                    order.append(int(request.form.get("tat")))
                    #order[11] -> tac
                    order.append(int(request.form.get("tac")))
                    #order[12] -> sac
                    order.append(int(request.form.get("sac")))
                    #order[13] -> wac
                    order.append(int(request.form.get("wac")))
                else:
                    order.append(0)
                    order.append(0)
                    order.append(0)
                    order.append(0)
                
                db.execute('DELETE FROM orders WHERE id = ?;',(order[0],))
                con.commit()
                db.execute('INSERT INTO orders (id, status, tpc, spc, wpc, tpt, tat, tac, sac, wac, user_id, manager_id, equipment_id, description) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);',(order[0],order[1],order[6],order[7],order[8],order[9],order[10],order[11],order[12],order[13],order[2],order[3],order[4],order[5],))
                con.commit()

                db.execute('SELECT * FROM requests WHERE id = ?;',(order[0],))
                rows = db.fetchall()
                income = []
                income.append(order[0])
                if order[1] == "Draft":
                    income.append("Accepted")
                else:
                    income.append(order[1])
                y = 0
                for a in rows[0]:
                    if y > 1:
                        income.append(a)
                    y += 1
                db.execute('DELETE FROM requests WHERE id = ?;',(order[0],))
                con.commit()
                db.execute('INSERT INTO requests (id, status, priority, user_id, manager_id, due, equipment_id, description) VALUES (?,?,?,?,?,?,?,?);',(income[0],income[1],income[2],income[3],income[4],income[5],income[6],income[7],))
                con.commit()
                return redirect("/myorders")

            elif request.form.get("options") == None:
                return render_template("index.html",data=data,username_display=session["username"])
            else:
                data.sort(key=lambda x:x[int(request.form.get("options"))])
                return render_template("index.html",data=data,username_display=session["username"],default=int(request.form.get("options")),reqnum=0)
    else:
        if session["type"] == "managers":
            db.execute('SELECT * FROM requests WHERE manager_id = ?;',(session["user_id"],))
            rows = db.fetchall()
            x = len(rows)
            data = [[] for i in range(x)]
            i = 0
            for a in rows:
                db.execute('SELECT * FROM users WHERE id = ?;',(a[3],))
                rows2 = db.fetchall()
                db.execute('SELECT * FROM equipment WHERE id = ?;',(a[6],))
                rows3 = db.fetchall()
                y = 0
                for b in a:
                    if y == 5:
                        data[i].append(datetime.strptime(str(b),'%d.%m.%Y').date())
                    else:
                        data[i].append(b)
                    y += 1
                data[i][6] = rows3[0][1]
                data[i][3] = rows2[0][1]
                i += 1
            banana = session["newreq"]
            session["newreq"] = 0
            data.reverse()
            return render_template("index.html",data=data,username_display=session["username"],reqnum = banana)
        else:
            db.execute('SELECT * FROM requests WHERE user_id = ? AND status = "Pending";',(session["user_id"],))
            rows = db.fetchall()
            x = len(rows)
            data = [[] for i in range(x)]
            i = 0
            for a in rows:
                db.execute('SELECT * FROM managers WHERE id = ?;',(a[4],))
                rows2 = db.fetchall()
                db.execute('SELECT * FROM equipment WHERE id = ?;',(a[6],))
                rows3 = db.fetchall()
                y = 0
                for b in a:
                    if y == 5:
                        data[i].append(datetime.strptime(str(b),'%d.%m.%Y').date())
                    else:
                        data[i].append(b)
                    y += 1
                data[i][6]=rows3[0][1]
                data[i][4] = rows2[0][1]
                i += 1
            data.reverse()
            return render_template("index.html",data=data,username_display=session["username"],reqnum=0)

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        type = 'managers'
        b = 0
        db.execute('SELECT * FROM "{}" WHERE username = ?;'.format(type.replace('"', '""')),(request.form.get("username"),))
        rows = db.fetchall()
        if len(rows) == 0:
            type = 'users'
            db.execute('SELECT * FROM "{}" WHERE username = ?;'.format(type.replace('"', '""')),(request.form.get("username"),))
            rows = db.fetchall()
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return render_template("login.html",error1 = True)

        session["user_id"] = rows[0][0]
        session["username"] = request.form.get("username")
        session["type"] = type
        session["newreq"] = 0
        return redirect("/")

    else:
        return render_template("login.html",error1 = False)

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    if request.method == "POST":
        type = request.form.get("type")
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html",error1 = True, error2 = False)

        db.execute('SELECT * FROM "{}" WHERE username = ?;'.format(type.replace('"', '""')),(request.form.get("username"),))
        rows = db.fetchall()
        if len(rows) > 0:
            return render_template("register.html",error1 = False, error2 = True)


        db.execute('INSERT INTO "{}" (username, hash) VALUES (?,?);'.format(type.replace('"', '""')),(request.form.get("username"),generate_password_hash(request.form.get("password"))))
        con.commit()
        db.execute('SELECT * FROM "{}" WHERE username = ?;'.format(type.replace('"', '""')),(request.form.get("username"),))
        rows = db.fetchall()
        session["user_id"] = rows[0][0]
        session["username"] = request.form.get("username")
        session["type"] = request.form.get("type")
        session["newreq"] = 0
        return redirect("/")

    else:
        return render_template("register.html",error1 = False, error2 = False)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="localhost",port=5500)