from __future__ import division, print_function
# coding=utf-8
import sys
import os
import glob
import re
from flask.json import load
import numpy as np
import tensorflow as tf
import tensorflow as tf
import cv2
import mysql.connector
import uuid
from flask.helpers import flash


from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Flask utils
from flask import Flask, redirect, url_for, request, render_template, jsonify, session  
from flask_mail import Mail, Message

from werkzeug.utils import secure_filename
#from gevent.pywsgi import WSGIServer

# Define a flask app
app = Flask(__name__)




app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "soulmenacing@gmail.com"
app.config['MAIL_PASSWORD'] = "soul0484287"
###
###
###gmail ar password lagbo email pathaner leiga
###
###
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail=Mail(app)


app.secret_key=os.urandom(24)
conn = mysql.connector.connect(host="remotemysql.com",user="OQmAQgAGIs",password="OTh3lb0dWY",database="OQmAQgAGIs")
cursor = conn.cursor()

# Model saved with Keras model.save()
MODEL_PATH ='all_models/tomato_model_inception.h5'
MODEL_PATH2 = 'all_models/apple_model.h5'
MODEL_PATH3 = 'all_models/potato_model.h5'
MODEL_PATH4 = 'all_models/rice_model2.h5'
ERROR_MODEL = 'all_models/error_model.h5'
ERROR_MODEL_2 = 'all_models/error_model_2222.h5'


# Load your trained model
model = load_model(MODEL_PATH)
model2 = load_model(MODEL_PATH2)
model3 = load_model(MODEL_PATH3)
model4 = load_model(MODEL_PATH4)
error_model = load_model(ERROR_MODEL)
error_model_2 = load_model(ERROR_MODEL_2)






#===========================================================================================================================================================
#===========================================================================================================================================================


def unique(list1):
    x = np.array(list1)
    print(np.unique(x))


def get_filepaths(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths


def get_dirpaths(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in directories:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths


def final_fun(directory,true_predict_value,model,predict_function,want_csv = False):
    my_array = []
    get_csv = []
    get_files = get_filepaths(directory)
    for img in get_files:
        tmp = []
        tmp.append(img)
        gg = predict_function(img,model)
        my_array.append(gg)
        tmp.append(gg)
        get_csv.append(tmp)
    if want_csv:
        return my_array,get_csv
    else:
        return my_array


def preditc_in_dir(my_path,actual_val,model,predict_function,show_count=False,want_csv=False,csv_name='untitiled.csv'):
    print("Predic Value : {}\nDir Path ==> {}\n".format(actual_val,my_path))
    if want_csv:
        ss,ss2 = final_fun(my_path,actual_val,model,predict_function,want_csv=True)
    else:
        ss = final_fun(my_path,actual_val,model,predict_function,want_csv)
    print("correct prediction : \t{}\ntotal element : \t{}\nAccuracy partial : \t{}\n".format(ss.count(actual_val),len(ss),ss.count(actual_val)/len(ss)))    
    
    if show_count:
        print("Printing Counts : \n")
        for i in range(0,10):
            print("{} ==>> {}".format(i,ss.count(i)))
    print("\n============================================================================\n")
    if want_csv:
        df = pd.DataFrame(ss2)
        df.to_csv(csv_name, index=False, header=['Name',"Pred"])
        mm = pd.read_csv(csv_name)
        return ss.count(actual_val)/len(ss),mm
    else:
        return ss.count(actual_val)/len(ss)


def accuracy(path_of_the_dir,values,model,predict_function,show_count=False):
    get_dir = get_dirpaths(path_of_the_dir)
    gg = 0
    pp = 0
    for the_dir in get_dir:
        gg += preditc_in_dir(the_dir,values[pp],model,predict_function,show_count)
        pp += 1
    print("PREDICTED RESULT ACCURACY ==>> {}\n".format(gg/len(get_dir)))
    return gg/len(get_dir)



#===========================================================================================================================================================
#===========================================================================================================================================================






def error_model_predict(img_path, model):
    load_image = cv2.imread(img_path)
    img = cv2.resize(load_image,(256,256))
    x = image.img_to_array(img)
    x=x/255
    x = np.expand_dims(x, axis=0)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    
    return preds



def model_predict(img_path, model):
    # print(img_path)
    # img = image.load_img(img_path, target_size=(224, 224))
    # img = image.load_img(img_path)
    load_image = cv2.imread(img_path)
    
    val = error_model_predict(img_path,error_model_2)
    if(val == 2):
        img = cv2.resize(load_image,(224,224))


        x = image.img_to_array(img)
        x=x/255
        x = np.expand_dims(x, axis=0)

        preds = model.predict(x)
        preds=np.argmax(preds, axis=1)
        if preds==0:
            preds="The Disease is Tomato_Bacterial_Spot"
        elif preds==1:
            preds="The Disease is Tomato_Early_Blight"
        elif preds==2:
            preds="The Disease is Tomato_Late_Blight"
        elif preds==3:
            preds="Te Disease is Tomato_Leaf_Mold"
        elif preds==4:
            preds="The Disease is Tomato_Septoria_leaf"
        elif preds==5:
            preds="The Disease is Tomato_Two_spotted_spider_mite"
        elif preds==6:
            preds="The Disease is Tomato_Target_Spot"
        elif preds==7:
            preds="The Disease is Tomato_YellowLeaf_Curl_virus"
        elif preds==8:
            preds="The Disease is Tomato_Mossaic_virus"
        else:
            preds="Great....!!! Tomato is Healthy !!!"
    else:
        preds = "Wrong Picture....Not tomato"

    return preds

def model_predict_admin(img_path, model_ad):
    # print(img_path)
    # img = image.load_img(img_path, target_size=(224, 224))
    # img = image.load_img(img_path)
    load_image = cv2.imread(img_path)
    img = cv2.resize(load_image,(224,224))


    x = image.img_to_array(img)
    x=x/255
    x = np.expand_dims(x, axis=0)

    preds = model_ad.predict(x)
    preds=np.argmax(preds, axis=1)

    
    return preds[0]











def model_predict2(img_path, model):
    # print(img_path)
    val = error_model_predict(img_path,error_model_2)
    if(val == 0):
        img = image.load_img(img_path, target_size=(256, 256))

        x = image.img_to_array(img)
        x=x/255
        x = np.expand_dims(x, axis=0)

        preds = model.predict(x)
        preds=np.argmax(preds, axis=1)
        
        if preds == 0:
            preds = "Apple has 'Apple-Scab Disease'"
        elif preds == 1:
            preds = "Apple has 'Apple-Black-rot Disease'"
        elif preds == 2:
            preds = "Apple has 'Cedar-Apple-rust Disease'"
        else:
            preds = "Great !!! Apple has no Disease.. Healthy !!! ... "
    else:
        preds = "Wrong..... This is not apple"
    
    return preds


def model_predict2_admin(img_path, model_ad):
    # print(img_path)
    # img = image.load_img(img_path, target_size=(224, 224))
    # img = image.load_img(img_path)
    load_image = cv2.imread(img_path)
    img = cv2.resize(load_image,(256,256))


    x = image.img_to_array(img)
    x=x/255
    x = np.expand_dims(x, axis=0)

    preds = model_ad.predict(x)
    preds=np.argmax(preds, axis=1)

    
    return preds[0]














def model_predict3(img_path, model):
    # print(img_path)
    val = error_model_predict(img_path,error_model_2)

    if(val == 1):
        img = image.load_img(img_path, target_size=(256, 256))

        x = image.img_to_array(img)
        x=x/255
        x = np.expand_dims(x, axis=0)

        preds = model.predict(x)
        preds=np.argmax(preds, axis=1)
        
        if preds == 0:
            preds = "Potato has 'Potato Early-Blight Disease'"
        elif preds == 1:
            preds = "Great !!! Potato is Healthy !"
        else:
            preds = "Potato has 'Potato Late-Blight Disease'"
    else:
        preds = "Wrong.....This is not potato"
    return preds


def model_predict3_admin(img_path, model_ad):
    # print(img_path)
    # img = image.load_img(img_path, target_size=(224, 224))
    # img = image.load_img(img_path)
    load_image = cv2.imread(img_path)
    img = cv2.resize(load_image,(256,256))


    x = image.img_to_array(img)
    x=x/255
    x = np.expand_dims(x, axis=0)

    preds = model_ad.predict(x)
    preds=np.argmax(preds, axis=1)

    
    return preds[0]














def model_predict4(img_path, model):
    print(img_path)
    val = error_model_predict(img_path,error_model)
    if(val == 2):
        img = image.load_img(img_path, target_size=(1282, 1282))

        x = image.img_to_array(img)
        x=x/255
        x = np.expand_dims(x, axis=0)

        preds = model.predict(x)
        preds=np.argmax(preds, axis=1)
        
        if preds == 0:
            preds = "The disease is 'Brown Spot'"
            # preds = "Potato has 'Potato Early-Blight Disease'"
        elif preds == 1:
            preds = "Rice is Healthy !!!!"
            # preds = "Great !!! Potato is Healthy !"
        elif preds == 2:
            preds = "The disease is 'Hispa'"
            # preds = "Potato has 'Potato Late-Blight Disease'"
        else:
            preds = "The disease is 'Leaf Blast'"
    else:
        preds = "Wrong.....This is not Rice"
    return preds


def model_predict4_admin(img_path, model_ad):
    # print(img_path)
    # img = image.load_img(img_path, target_size=(224, 224))
    # img = image.load_img(img_path)
    load_image = cv2.imread(img_path)
    img = cv2.resize(load_image,(1282,1282))


    x = image.img_to_array(img)
    x=x/255
    x = np.expand_dims(x, axis=0)

    preds = model_ad.predict(x)
    preds=np.argmax(preds, axis=1)

    
    return preds[0]













# //////////////////////////////////////// all the routes start here /////////////////////////////////////////////////////////////

@app.route("/")
def ho():
    if 'user_id' in session:
        return render_template("ppp.html",name=session['name'])
    return render_template("login.html")

@app.route("/ppp.html")
def ho2():
    if 'user_id' not in session:
        return render_template("login.html")
    return render_template("ppp.html",name=session['name'])


@app.route("/apple.html")
def apple_fun():
    if 'user_id' not in session:
        return render_template("login.html")
    if session['name'] == "admin":
        return render_template("apple_a.html")
    return render_template("apple.html")

@app.route("/tomato.html")
def tomato_fun():
    if 'user_id' not in session:
        return render_template("login.html")
    if session['name'] == "admin":
        return render_template("tomato_a.html")
    return render_template("tomato.html")

@app.route("/potato.html")
def potato_fun():
    if 'user_id' not in session:
        return render_template("login.html")
    if session['name'] == "admin":
        return render_template("potato_a.html")
    return render_template("potato.html")

@app.route("/rice.html")
def rice_fun():
    if 'user_id' not in session:
        return render_template("login.html")
    if session['name'] == "admin":
        return render_template("rice_a.html")
    return render_template("rice.html")    












@app.route('/user_profile')
def user_profile():
    return render_template("user_profile.html",name=session['name'],email=session['email'],count=session['count'])

@app.route('/change_password_page')
def change_pass_page():
    return render_template("change_password.html")


@app.route('/trial_page')
def trial_page():
    return render_template("trial.html")

# ///////////////////////////////////////////// render route ends here //////////////////////////////////////////////////////////////





#///////////////////////////////////////////// login and Logout and register/////////////////////////////////////////////////////////////////



@app.route("/registation")
def register_user():
    return render_template("reg.html")






@app.route("/login_validation",methods=['post'])
def login_validation():
    email = str(request.form.get('email'))
    password = str(request.form.get('password'))

    cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}' AND `password` LIKE '{}'"""
                    .format(email,password))
    users=cursor.fetchall()
    # print(users)
    if len(users) > 0:
        session['user_id']=users[0][0]
        session['name']=users[0][1]

        #edited later
        session['password']=users[0][4]
        session['count']=int(users[0][5])
        session['email']=users[0][2]

        ########


        return render_template('ppp.html',name=session['name'])
    else:
        return render_template('login.html')
    return "ll"



@app.route("/reg_user",methods=['post'])
def registration():
    name = str(request.form.get('uname'))
    email = str(request.form.get('uemail'))
    password = str(request.form.get('upassword'))
    cursor.execute("""INSERT INTO `user` (`user_id`,`name`,`email`,`password`) VALUES (NULL,'{}','{}','{}')""".format(name,email,password))
    conn.commit()
    cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}'""".format(email))
    myuser=cursor.fetchall()
    session['user_id']=myuser[0][0]
    session['name']=myuser[0][1]
    #edited later
    session['password']=myuser[0][4]
    session['count']=int(myuser[0][5])
    session['email']=myuser[0][2]

    ########
    return redirect("ppp.html")




@app.route('/logout')
def logout():
    cursor.execute("""UPDATE user SET count=%s WHERE email=%s""",(str(session['count']),session['email']))

    session.pop('user_id')
    session.pop('name')
    #edited later
    session.pop('password')
    session.pop('count')

    ########
    return redirect('/')



@app.route('/forgot_page')
def forgot_page():
    return render_template("forgot.html")








@app.route('/forgot',methods=['POST',"GET"])
def forgot():
    if 'user_id' in session:
        return redirect("login.html")
    if request.method == "POST":
        email = str(request.form.get('email'))
        token = str(uuid.uuid4())
        print(token+"----------------------------------------------------------------------------")
        print(email+"-------------------------------------------------------------------------------")
        cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}'""".format(email))
        result = cursor.fetchall()
        print(len(result))
        if len(result) > 0:
            cursor.execute("""UPDATE user SET token=%s WHERE email=%s""",(token,email))
            conn.commit()

            msg = Message("Token",sender="soulmenacing@gmail.com",recipients=[email])
            msg.body = token
            mail.send(msg)

            flash("Email ALready sent")
            kk="/reset/"+token
            # return render_template("reset.html",linkk=kk)
            return redirect('/reset')
        else:
            print("=========================================================\n")

            flash("Email do not match")
    return render_template("forgot.html")

@app.route('/reset',methods=['GET','POST'])
def go_rest():
    return render_template("reset.html")

@app.route('/reset_fun',methods=['POST','GET'])
def reset():
    token = str(request.form.get('token'))    
    password = str(request.form.get('password'))
    cpassword = str(request.form.get('cpassword'))
    print("Password is : "+password+"cpassword is : "+cpassword)    
    if password != cpassword:
        return "password didnt match"
    token1 = str(uuid.uuid4())
    cursor.execute("""SELECT * FROM `user` WHERE `token` LIKE '{}'""".format(token))
    result = cursor.fetchall()
    if len(result) > 0:
        cursor.execute("""UPDATE user SET token=%s, password=%s WHERE token=%s""",(token1,cpassword,token))
        conn.commit()
        return redirect('/ppp.html')
    else:
        return "token invalid"



@app.route('/change_password',methods=['POST','GET'])
def change_pass():
    main_password = str(request.form.get('main_password'))    
    new_password = str(request.form.get('new_password'))
    con_password = str(request.form.get('con_password'))
    
    cur_password = str(session['password'])
    if cur_password != main_password:
        return "Password Invalid"
    if new_password != con_password:
        return "Password Mismatched"
    email = session['email']
    cursor.execute("""UPDATE user SET password=%s WHERE email=%s""",(new_password,email))
    conn.commit()
    return redirect('/user_profile')



@app.route('/check_token',methods=['GET','POST'])
def check_token():
    if 'user_id' not in session:
        return render_template("login.html")
    token = str(request.form.get('token_val'))
    cursor.execute("""SELECT * FROM `user` WHERE `email` LIKE '{}'""".format(session['email']))
    user = cursor.fetchall()
    new_token = user[0][6]

    if token != new_token:
        return "Token mismatched"
    
    token_to_set = str(uuid.uuid4())

    cursor.execute("""UPDATE user SET count=%s, count_token=%s WHERE email=%s""",(str(1000),token_to_set,session['email']))
    conn.commit()
    session['count']=1000
    return redirect('/user_profile')


@app.route('/increase_token')
def increase_token():
    token = str(uuid.uuid4())
    cursor.execute("""UPDATE user SET count_token=%s WHERE email=%s""",(token,session['email']))
    conn.commit()
    msg = Message("Token Increase",sender="soulmenacing@gmail.com",recipients=[session['email']])
    msg.body = token
    mail.send(msg)
    return redirect("/get_token_inc_page")


@app.route('/get_token_inc_page')
def get_token_inc_page():
    return render_template("get_token.html")


# ////////////////////////////////////////////// prediction route starts here //////////////////////////////////////////////////////////

# -------------------------------------------------------------- model2
@app.route("/apple-predict",methods=['GET','POST'])
def apple():
    f=request.files.get('image')
    if f:
        session['count'] -= 1
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath,'uploads' ,secure_filename(f.filename))
        f.save(file_path)
        newName = model_predict2(file_path,model2)
        # newName = f.filename
    else:
        newName = "You Haven't Choose anything YET !!!"

    return jsonify({'name' : newName})
 


@app.route("/apple-predict-admin",methods=['GET','POST'])
def apple_admin():
    dir_pos = str(request.form.get('dir'))
    pred_val = int(request.form.get('val'))
    print(dir_pos)
    print(pred_val)
    kk = preditc_in_dir(dir_pos,pred_val,model2,model_predict2_admin,show_count=True)
    print(kk)
    # return "dir-> {} & pred_val-> {} & accu-> {}".format(dir_pos,pred_val,kk*100)
    return render_template("show_result.html",dir_name=dir_pos,disease_name=pred_val,acc=kk)




# ---------------------------------------------------------------- model
@app.route("/tomato-predict",methods=['GET','POST'])
def tomato():
    f=request.files.get('image')
    if f:
        session['count'] -= 1
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath,'uploads' ,secure_filename(f.filename))
        f.save(file_path)
        newName = model_predict(file_path,model)
        print(newName)
        # newName = f.filename
    else:
        newName = "You Haven't Choose anything YET !!!"

    return jsonify({'name' : newName})

@app.route("/tomato-predict-admin",methods=['GET','POST'])
def tomato_admin():
    dir_pos = str(request.form.get('dir'))
    pred_val = int(request.form.get('val'))
    print(dir_pos)
    print(pred_val)
    kk = preditc_in_dir(dir_pos,pred_val,model,model_predict_admin,show_count=True)
    print(kk)
    # return "dir-> {} & pred_val-> {} & accu-> {}".format(dir_pos,pred_val,kk*100)
    return render_template("show_result.html",dir_name=dir_pos,disease_name=pred_val,acc=kk)





# -------------------------------------------------------------- model3

@app.route("/potato-predict",methods=['GET','POST'])
def potato():
    f=request.files.get('image')
    if f:
        session['count'] -= 1
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath,'uploads' ,secure_filename(f.filename))
        f.save(file_path)
        newName = model_predict3(file_path,model3)
        # newName = f.filename
    else:
        newName = "You Haven't Choose anything YET !!!"

    return jsonify({'name' : newName})


@app.route("/potato-predict-admin",methods=['GET','POST'])
def potato_admin():
    dir_pos = str(request.form.get('dir'))
    pred_val = int(request.form.get('val'))
    print(dir_pos)
    print(pred_val)
    kk = preditc_in_dir(dir_pos,pred_val,model3,model_predict3_admin,show_count=True)
    print(kk)
    # return "dir-> {} & pred_val-> {} & accu-> {}".format(dir_pos,pred_val,kk*100)
    return render_template("show_result.html",dir_name=dir_pos,disease_name=pred_val,acc=kk)


# -------------------------------------------------------------- model4

@app.route("/rice-predict",methods=['GET','POST'])
def rice():
    f=request.files.get('image')
    if f:
        session['count'] -= 1
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath,'uploads' ,secure_filename(f.filename))
        f.save(file_path)
        newName = model_predict4(file_path,model4)
        # newName = f.filename
    else:
        newName = "You Haven't Choose anything YET !!!"

    return jsonify({'name' : newName})


@app.route("/rice-predict-admin",methods=['GET','POST'])
def rice_admin():
    dir_pos = str(request.form.get('dir'))
    pred_val = int(request.form.get('val'))
    print(dir_pos)
    print(pred_val)
    kk = preditc_in_dir(dir_pos,pred_val,model4,model_predict4_admin,show_count=True)
    print(kk)
    # return "dir-> {} & pred_val-> {} & accu-> {}".format(dir_pos,pred_val,kk*100)
    return render_template("show_result.html",dir_name=dir_pos,disease_name=pred_val,acc=kk)


# ///////////////////////////////////////////////// prediction routes ends here //////////////////////////////////////////////////////////

if __name__ == '__main__':
    app.run(port=5001,debug=True)
