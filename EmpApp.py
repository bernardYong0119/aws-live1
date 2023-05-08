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
    employeeid = request.args.get('employeeid')
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM assDatabse WHERE employeeid = %s", (employeeid,))
    employee_data = cursor.fetchall()
    if employee_data:
        emp_data = {}
        emp_data['employeeid'] = employee_data[0]
        emp_data['name'] = employee_data[1]
        emp_data['dob'] = employee_data[2]
        emp_data['gender'] = employee_data[3]
        emp_data['address'] = employee_data[4]
        emp_data['phone'] = employee_data[5]
        emp_data['email'] = employee_data[6]
        emp_data['jobstatus'] = employee_data[7]
        emp_data['jobtitle'] = employee_data[8]
        emp_data['hiredate'] = employee_data[9]
        emp_data['department'] = employee_data[10]
        emp_data['payRoll'] = employee_data[11]
        emp_data['workinghours'] = employee_data[12]
        
        #get employee image file
        emp_image_file_name_in_s3 = "emp-id-" + str(employee_data[0]) + "_image_file"
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
        emp_data['photo'] = object_url
        return render_template('employeeInfo.html',emp_data=employee_data)
    else:
        return "Employee not found"
    cursor.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
