from flask import Flask, render_template, request
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


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


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
    hiredate = request.form['hiredate']
    department = request.form['department']
    payRoll = request.form['payRoll']
    workinghours = request.form['workinghours']
    photo = request.files['photo']

    insert_sql = "INSERT INTO assDatabase VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if photo.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (employeeid, name, dob, gender, address, phone, email, jobstatus, hiredate, department, payRoll, workinghours))
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


if __name__ == '_main_':
    app.run(host='0.0.0.0', port=80, debug=True)
    
