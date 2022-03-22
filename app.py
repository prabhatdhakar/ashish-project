import os 
from datetime import datetime
from wsgiref import validate 
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template_string,render_template, url_for ,request,redirect
from  pytz import timezone,utc
from sqlalchemy import null,and_ ,func
import time 
import numpy as np 
import matplotlib.dates as md
from matplotlib import pyplot as plt  
from matplotlib import dates as mpl_dates 
from flask import url_for 
import itertools

current_dir=os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+os.path.join("database.sqlite3")
db=SQLAlchemy()
db.init_app(app)
app.app_context().push()

class Registration(db.Model):
  __tablename__='registration'
  name=db.Column(db.String,nullable=False) 
  username=db.Column(db.String,nullable=False,unique=True,primary_key=True)
  password=db.Column(db.String,nullable=False)
class Tracker(db.Model):
  __tablename__ ='tracker'
  id= db.Column(db.Integer ,autoincrement = True ,primary_key=True) 
  name=db.Column(db.String,nullable=False, unique=True) 
  description =db.Column(db.String,nullable=False, unique=True) 	 
  setting=db.Column(db.String)
  uname=db.Column(db.String,nullable=False,primary_key=True) 
class Log(db.Model):
  __tablename__='log' 
  trackerid=db.Column(db.Integer, autoincrement = True,primary_key=True ) 
  id=db.Column(db.Integer,primary_key=True) 
  timestamp=db.Column(db.DateTime) 
  value=db.Column(db.String,nullable=False)
  note=db.Column(db.String,nullable=False) 

def get_past_date(dt): 
    dt=dt.split(' ') 
    d=list(dt[0].split('-'))  
    d=[int(i) for i in d]
    t=list((dt[1][0:5]).split(':') ) 
    t=[int(i) for i in t]
    print(d,t)
    curr = str(datetime.now())  
    curr=curr.split(' ') 
    curd=curr[0].split('-')  
    curd=[int(i) for i in curd] 
    curt=(curr[1][0:5]).split(':')   
    curt=[int(i) for i in curt]
    if curd[0]==d[0] :
        if curd[1]==d[1]:
          if curd[2]==d[2]:
            if curt[0]==t[0] : 
              if curt[1]==t[1]:  
                return "1 min ago" 
              else:
                return str(curt[1]-t[1])+ " min ago" 
            else:
              return str(curt[0]-t[0])+ " hour ago" 
          else:  
            if curd[2]-d[2]==1:
              return "yesterday" 
            else:
              return str(curd[2]-d[2])+ " day ago" 
        else:
          return str(curd[1]-d[1])+ " month ago"  
    else:
      return str(curd[0]-d[0])+ " year ago"
def period(dt): 
    dt=dt.split(' ') 
    d=list(dt[0].split('-'))  
    d=[int(i) for i in d]
    t=list((dt[1][0:5]).split(':') ) 
    t=[int(i) for i in t]
    print(d,t)
    curr = str(datetime.now())  
    curr=curr.split(' ') 
    curd=curr[0].split('-')  
    curd=[int(i) for i in curd] 
    curt=(curr[1][0:5]).split(':')   
    curt=[int(i) for i in curt]
    if curd[0]==d[0] :
        if curd[1]==d[1]:
          if curd[2]==d[2]:
            return "today"  
          elif (curd[2]-d[2])<7:   
            return "week"
          else:
            return "month"  

def validate(name,uname,passw):
   for i in name:
        if not ((i<='Z' and i>='A') or (i>='a' and i<='z') or i==' ') :   
          return 1,'character other than Uppercase,lowercase and spacebar not allowed' 
   a,nu,al=0,0,0
   for i in uname:
        if (i<='Z' and i>='A') or (i>='a' and i<='z'): 
          a=1
        elif (i<='9'and i>='0') :
          nu=1
        elif i=='@':
          al=1 
        else:
          return 2,'special characters other than "@" not allowed' 
   if a!=1: 
       return 2,"username should contain alphabet" 
   elif nu!=1:
       return 2,"username must contain numeric"
   elif al!=1:
       return 2,"username must contain '@'"   
   la,sa,nu,al=0,0,0,0 
   for i in passw:
        if (i<='Z' and i>='A') : 
          la+=1 
        elif (i>='a' and i<='z'): 
          sa+=1
        elif (i<='9'and i>='0') :
          nu+=1
        elif i in '@~!#$%^&*':
          al+=1 
        else:
          return i+'not allowed in password'  
   if la==0: 
      return 3,"Password must contain atleast one Uppercase"
   elif sa==0: 
      return 3,"Password must contain atleast one Lowercase"
   elif nu==0: 
      return 3,"Password must contain atleast one Numeric" 
   elif al==0: 
      return 3,"Password must contain atleast one Special character" 
   elif (la+sa+nu+al)<8:
     return 3,"password length must be 8 " 
   return "NULL"
      
   
       
    
@app.route("/",methods=["GET","POST"])
def login():  
  if request.method=='GET':
     return render_template("index.html",msg="") 
  if request.method=='POST':  
     uname=request.form.get("uname")
     passw=request.form.get("passw") 
     user=Registration.query.filter(and_(Registration.username==uname,Registration.password==passw)).first()   
     #print(user) 
     if not user:
        return render_template("index.html",msg="invalid credentials") 
     else:
        return redirect(url_for('dashboard',uname=uname))
@app.route("/dashboard/<uname>",methods=["GET","POST"])   
def dashboard(uname): 
  if request.method=='GET':
      track=Tracker.query.filter_by(uname=uname).all()  
      user=Registration.query.filter_by(username=uname).first()
      print(track)   
      d=[]
      for i in track:
         rec_log=db.session.query(Log.timestamp,func.max(Log.timestamp)).filter(Log.trackerid.in_([i.id])).group_by(Log.trackerid).first() 
         print(rec_log)  
         if not rec_log:
           d.append(" ") 
         else: 
           d.append(get_past_date(str(rec_log.timestamp))) 
      return render_template("dashboard1.html",user=user,track=track,rec_log=d) 

@app.route("/signup",methods=["GET","POST"]) 
def signup():
  if request.method=='GET':
    return  render_template("signup.html",error='',fno=0,name="name",uname="username",passw="password") 
  if request.method=='POST':
      name=request.form.get("name")
      uname=request.form.get("uname")
      passw=request.form.get("passw")  
      fno,error=validate(name,uname,passw)  
      print(fno,error,name,uname,passw)
      if error!="NULL":
        return  render_template("signup.html",error=error,fno=fno,name=name,uname=uname,passw=passw) 
      nuser=Registration(name=name,username=uname,password=passw) 
      db.session.add(nuser) 
      db.session.commit()
      return render_template("index.html")

@app.route('/<username>/tracker/create',methods=["GET","POST"])
def tracker_create(username):
  if request.method=='GET': 
    nam=Registration.query.filter_by(username=username).first()
    return render_template("addtracker.html",nam=nam,user=username)
  if request.method=='POST': 
     tname=request.form.get("tname")
     desc=request.form.get("desc")
     type=request.form.get("vtype")
     if type=="mcq":
       sett=request.form.get("sett") 
     else:
       sett="null"   
     t=Tracker(name=tname,description=desc,setting=sett,uname=username) 
     db.session.add(t)
     db.session.commit() 
     return redirect(url_for('dashboard',uname=username)) 

@app.route("/tracker/<int:tracker_id>/<uname>/update",methods=["GET","POST"])
def update(tracker_id , uname):
   if request.method=='GET':
     i =Tracker.query.filter( and_(Tracker.id==tracker_id , Tracker.uname==uname)).first() 
     print(i.name) 
     nam=Registration.query.filter_by(username=i.uname).first()
     return render_template("updatetracker.html",nam=nam,i=i)
   if request.method=='POST':  
     tname=request.form.get("tname")
     desc=request.form.get("desc")
     type=request.form.get("vtype")
     if type=="mcq":
       sett=request.form.get("sett") 
     else:
       sett="null"  
     t= Tracker.query.filter( and_(Tracker.id==tracker_id , Tracker.uname==uname)).first()  
     t.name=tname
     t.description=desc
     t.setting=sett
     db.session.commit() 
     return redirect(url_for('dashboard',uname=t.uname)) 

@app.route("/tracker/<int:tracker_id>/<uname>/delete",methods=["GET","POST"])
def trackerdelete(tracker_id , uname): 
   if request.method=='GET':
     user=Registration.query.filter_by(username=uname).first()  
     l=Log.query.filter_by(trackerid=tracker_id).all() 
     for i in l: 
       db.session.delete(i)
       db.session.commit()  
     i =Tracker.query.filter( and_(Tracker.id==tracker_id , Tracker.uname==uname)).first()  
     db.session.delete(i)
     db.session.commit()   
     return redirect(url_for('dashboard',uname=uname))

@app.route('/log/<username>/<int:id>/create',methods=["GET","POST"])     
def log_creater(username,id): 
  if request.method=="GET":  
    t=str(datetime.now())  
    print(t)
    t=t[0:10]+'T'+t[11:16]
    print(t)  
    i =Tracker.query.filter( and_(Tracker.id==id , Tracker.uname==username)).first() 
    nam=Registration.query.filter_by(username=i.uname).first()
    return render_template("log1.html",uname=username,nam=nam,id=id,t=t,i=i) 
  if request.method=="POST":
    logt=request.form.get("logt")
    val=request.form.get("val")   
    print(val) 
    note=request.form.get("note")   
    logt=datetime.strptime(logt,'%Y-%m-%dT%H:%M')
    print(type(logt))
    l=Log(trackerid=id,value=val,timestamp=logt,note=note)  
    db.session.add(l) 
    db.session.commit()  
    return redirect(url_for('dashboard',uname=username))   

@app.route('/<int:id>/log/detail',methods=["GET","POST"])
def log_detail(id):
  if request.method=='GET':  
    l=Log.query.filter(Log.trackerid==id).all() 
    t=Tracker.query.filter_by(id=id).first()  
    nam=Registration.query.filter_by(username=t.uname).first() 
    y=[]
    x=[]  
    cor=[]
    temp=[]
    for i in l: 
       s=str(i.timestamp)  
       res=period(s)
       if res in ["today","week","month"]:
         cor.append((i.timestamp,i.value,res)) 
       d=s[0:10]
       s=s[11:16]     
       h=int(s[0:2])
       m=int(s[3:]) 
       tg=" am"
       if(h>11): 
         h=h%12 
         tg=" pm" 
       s="At "+str(h)+":"+str(m)+tg  
       temp.append((d,s)) 
    cor.sort()
    print(cor)
    m=0
    w=0 
    d=0
    if t.setting=="null":
       for i in cor: 
           x.append(i[0]) 
           y.append(int(i[1]))  
       cntr=cor[0][2]  
       print(x,y)
       for i in range(len(cor)): 
         if cor[i][2]=="month" and m==0: 
           m=1 
           plt.subplots_adjust(bottom=0.2)
           plt.xticks( rotation=25 )
           ax=plt.gca()  
           xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
           ax.xaxis.set_major_formatter(xfmt)    
           print(x,y)
           plt.plot_date(x,y,linestyle='solid') 
           plt.gcf().autofmt_xdate() 
           plt.savefig('static/month.png')  
           plt.close()
         elif cor[i][2]=="week" and w==0 : 
           w=1
           plt.subplots_adjust(bottom=0.2)
           plt.xticks( rotation=25 )
           ax=plt.gca()
           xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
           ax.xaxis.set_major_formatter(xfmt) 
           plt.plot_date(x[i:],y[i:],linestyle='solid')   
           plt.gcf().autofmt_xdate()  
           plt.savefig('static/week.png') 
           if m==0:  
             m=1
             plt.savefig('static/month.png') 
           plt.close() 
         elif cor[i][2]=="today" and d==0: 
           d=1
           plt.subplots_adjust(bottom=0.2)
           plt.xticks( rotation=25 )
           ax=plt.gca()
           xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
           ax.xaxis.set_major_formatter(xfmt) 
           plt.plot_date(x[i:],y[i:],linestyle='solid')  
           plt.gcf().autofmt_xdate()     
           plt.savefig('static/today.png') 
           if m==0:  
             m=1
             plt.savefig('static/month.png')  
           if w==0:
             w=1 
             plt.savefig('static/week.png') 
           plt.close() 
    return render_template("log_detail1.html" ,l=l,t=temp,nam=nam,trac=t,u=url_for('static',filename='month.png'))

@app.route('/log/<int:id>/delete',methods=["GET","POST"])  
def log_delete(id):
  if request.method=='GET':
     i =Log.query.filter_by( id=id).first() 
     tid=i.trackerid  
     db.session.delete(i) 
     db.session.commit() 
     return redirect(url_for('log_detail',id=tid))


@app.route("/log/<int:id>/update",methods=["GET","POST"])
def logupdate(id):
   if request.method=='GET':
     i =Log.query.filter_by(id=id).first()  
     t=Tracker.query.filter_by(id=i.trackerid).first() 
     nam=Registration.query.filter_by(username=t.uname).first() 
     st=str(i.timestamp)  
     st=st[0:10]+'T'+st[11:16]
     return render_template("updatelog.html",nam=nam,i=i,t=t,st=st)
   if request.method=='POST':  
     logt=request.form.get("logt")
     val=request.form.get("val")
     note=request.form.get("note")  
     logt=datetime.strptime(logt,'%Y-%m-%dT%H:%M')
     i =Log.query.filter_by(id=id).first() 
     i.timestamp=logt
     i.value=val
     i.note=note 
     db.session.commit() 
     return redirect(url_for('log_detail',id=i.trackerid))
      

if __name__ == '__main__':
  app.debug=True
  app.run()