from flask import Flask, render_template, request, jsonify
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'assDatabase'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route("/icon", methods=['GET', 'POST'])
def icon():
    return render_template('home.jpeg')

@app.route("/addempPage", methods=['GET', 'POST'])
def addempPage():
    return render_template('addEmployee.html')

@app.route("/searchempPage", methods=['GET', 'POST'])
def searchempPage():
    return render_template('searchEmployee.html')

@app.route("/searchForEditPage", methods=['GET', 'POST'])
def searchForEditPage():
    return render_template('searchForEdit.html')

@app.route("/editempPage", methods=['GET', 'POST'])
def EditEmpPage():
    return render_template('EditEmployee.html')

@app.route("/LeaveAppPage", methods=['GET', 'POST'])
def LeaveAppPage():
    return render_template('LeaveApplication.html')

@app.route("/addemp", methods=['POST'])
def AddEmp():
    employeeid = request.form['employeeid']
    name = request.form['name']
    dob = request.form['dob']
    gender = request.form['gender']
    address = request.form['address']
    phone = request.form['phone']
    email = request.form['email']
    jobstatus = request.form['jobstatus']
    jobtitle = request.form['jobtitle']
    hiredate = request.form['hiredate']
    department = request.form['department']
    payRoll = request.form['payRoll']
    workinghours = request.form['workinghours']
    photo = request.files['photo']

    insert_sql = "INSERT INTO assDatabase VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if photo.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (employeeid, name, dob, gender, address, phone, email, jobstatus, jobtitle, hiredate, department, payRoll, workinghours))
        db_conn.commit()
        
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(employeeid) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=photo)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('OutpuPage.html', employeeid=employeeid, name= name, phone= phone, department= department )

@app.route('/fetchdata', methods=['POST'])
def searchEmp():
    employeeid = request.form.get('employeeid')
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT * FROM assDatabase WHERE employeeid = %s", (employeeid,))
        data = cursor.fetchone()
        if data:
            employee_data = {}
            employee_data['employeeid'] = data[0]
            employee_data['name'] = data[1]
            employee_data['dob'] = data[2]
            employee_data['gender'] = data[3]
            employee_data['address'] = data[4]
            employee_data['phone'] = data[5]
            employee_data['email'] = data[6]
            employee_data['jobstatus'] = data[7]
            employee_data['jobtitle'] = data[8]
            employee_data['hiredate'] = data[9]
            employee_data['department'] = data[10]
            employee_data['payRoll'] = data[11]
            employee_data['workinghours'] = data[12]
        
            #get employee image file
            emp_image_file_name_in_s3 = "emp-id-" + str(data[0]) + "_image_file"
            s3 = boto3.resource('s3')
        
            try:
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])
                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    emp_image_file_name_in_s3)

            except Exception as e:
                return str(e)
            employee_data['photo'] = object_url
            return render_template('employeeInfo.html',employee_data=employee_data)
        else:
            return "Employee not found"
    except Exception as e:
        return str(e)
    finally:
        cursor.close()

@app.route('/editdatabyid', methods=['POST'])
def editEmpdatbyid():
    employeeid = request.form.get('employeeid')
    cursor = db_conn.cursor()
    try:
        cursor.execute("SELECT * FROM assDatabase WHERE employeeid = %s", (employeeid,))
        data = cursor.fetchone()
        if data:
            employee_data = {}
            employee_data['employeeid'] = data[0]
            employee_data['name'] = data[1]
            employee_data['dob'] = data[2]
            employee_data['gender'] = data[3]
            employee_data['address'] = data[4]
            employee_data['phone'] = data[5]
            employee_data['email'] = data[6]
            employee_data['jobstatus'] = data[7]
            employee_data['jobtitle'] = data[8]
            employee_data['hiredate'] = data[9]
            employee_data['department'] = data[10]
            employee_data['payRoll'] = data[11]
            employee_data['workinghours'] = data[12]
        
            #get employee image file
            emp_image_file_name_in_s3 = "emp-id-" + str(data[0]) + "_image_file"
            s3 = boto3.resource('s3')
        
            try:
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])
                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    emp_image_file_name_in_s3)

            except Exception as e:
                return str(e)
            employee_data['photo'] = object_url
            return render_template('EditEmployee.html',employee_data=employee_data)
        else:
            return "Employee not found"
    except Exception as e:
        return str(e)
    finally:
        cursor.close()


@app.route("/editemp", methods=['POST'])
def EditEmp():
    employeeid = request.form['employeeid']
    name = request.form['name']
    dob = request.form['dob']
    gender = request.form['gender']
    address = request.form['address']
    phone = request.form['phone']
    email = request.form['email']
    jobstatus = request.form['jobstatus']
    jobtitle = request.form['jobtitle']
    hiredate = request.form['hiredate']
    department = request.form['department']
    payRoll = request.form['payRoll']
    workinghours = request.form['workinghours']
    photo = request.files['photo']


    update_sql = "UPDATE assDatabase \
                  SET name = %s, dob = %s, gender = %s, address = %s, phone = %s, email = %s, \
                    jobstatus = %s, jobtitle = %s, hiredate = %s, department = %s, payRoll = %s, workinghours = %s \
                  WHERE employeeid = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql, (name, dob, gender, address, phone, email, jobstatus, jobtitle, hiredate, department, payRoll, workinghours, employeeid))
        db_conn.commit()

        # Update image file in S3 #
        if photo.filename != "":
            emp_image_file_name_in_s3 = "emp-id-" + str(employeeid) + "_image_file"
            s3 = boto3.resource('s3')

            try:
                print("Data updated in MySQL RDS... uploading new image to S3...")
                s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=photo)
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])

                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    emp_image_file_name_in_s3)

            except Exception as e:
                return str(e)
        
        print("all modification done...")
        return render_template('OutputEdit.html', employeeid=employeeid,  name=name,  dob=dob,  gender=gender,  address=address,  phone=phone,  email=email,  jobstatus=jobstatus,  jobtitle=jobtitle,  hiredate=hiredate,  department=department,  payRoll=payRoll,  workinghours=workinghours,  photo=photo)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
