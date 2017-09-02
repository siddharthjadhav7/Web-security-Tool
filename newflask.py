from flask import Flask, render_template,request,session
import os
import pymysql
import re
import hashlib, uuid
from pymongo import MongoClient

myconn= MongoClient("mongodb://sid:apple@ds119748.mlab.com:19748/starlord")
test=myconn.starlord
test.authenticate("sid","apple")

app = Flask(__name__)
app.secret_key="mynameissid"

salt = uuid.uuid4().hex


HOST = "ec2-35-164-233-57.us-west-2.compute.amazonaws.com"

@app.route('/')
def hello_world():
        if 'username' in session:
			return render_template('First.html')
		else:	
			return render_template('login.html')

@app.route('/reg', methods=['POST','GET'])
def reg():
        return render_template('register.html')



@app.route('/upload', methods=['POST','GET'])
def upload():
        print "In function:"
        file_upload = request.files.get('myFilename')
        output_file = file_upload.filename
        file_type=output_file.split('.')
        main_file= file_upload.read()
        print "Name is:"
        if(file_type[1] == 'py'):

                var_name = "pylint "+output_file+">"+output_file
                print var_name
        elif (file_type[1] == 'c'):
                var_name = "flawfinder "+output_file+">"+output_file
                print var_name
        result = os.system(var_name)
        fileptr = open(output_file, 'r')
        contents = fileptr.read()
		uname= session['username']
        print "table created"
        item_doc = {
            'name': output_file,
            'file_content': main_file,
            'result': contents,
			'username': uname
        }
        test.file_table.insert_one(item_doc)
        return render_template('First.html')

@app.route('/display_result', methods=['POST','GET'])
def display_result():
        name_of_file = request.form['input_file']
        if (re.match(r'[\w,\s-]+\.[A-Za-z]{1}', name_of_file)):
                print name_of_file
                my_list = []
                for entry in test.file_table.find({'name':name_of_file}):
                        my_dict = {}
                        file_content = entry['file_content']
                        file_result = entry['result']
                        my_dict['name'] = name_of_file
                        my_dict['content'] = file_content
                        my_dict['result'] = file_result
                        my_list.append(my_dict)
                        print file_result

                print my_list
                return render_template('result_page.html',mydict=my_list)
        else:
                return "Invalid Name"

@app.route('/First', methods=['POST','GET'])
def hello_myworld():
        username=request.form['username']
        password=request.form['password']
		password = hashlib.sha512(password + salt).hexdigest()
        if (re.match(r'[A-Za-z0-9@#$%^&+=]{5,}', username)):
                if (re.match(r'[A-Za-z0-9@#$%^&+=]{3,}', password)):
                        entry = test.table_name.find({'password':password,'username':username}).count()>0
               #else:
                #       return "Invalid Entry"

                        if(entry) :
                                print "Logged in successfully"
								session['username']=username
                        else:
                                print "Login unsuccessfully"
                        return render_template('First.html')
                else:
                        return "Invalid password "
        else:
                return "Invalid username"


				
@app.route('/registration', methods=['POST','GET'])
def registration():
        username=request.form['username']
        password=request.form['password']

        if (re.match(r'[A-Za-z0-9@#$%^&+=]{5,}', username)):
                if (re.match(r'[A-Za-z0-9@#$%^&+=]{3,}', password)):
                        password = hashlib.sha512(password + salt).hexdigest()
						my_d = {
                                'username': username,
                                'password': password
                        }

                        test.table_name.insert_one(my_d)
                        return render_template('login.html')
                else:
                        return "Invalid password "
        else:
                return "Invalid username"
				
				
				
@app.route('/logout', methods=['POST','GET'])
def logout():	
        session.pop('username',None)			
		return render_template('login.html')	

@app.route('/showFiles', methods=['POST','GET'])
def showFiles():		
		my_list = []
		for entry in test.file_table.find({'username':session['username']}):
			my_dict = {}
			file_name = entry['name']
			my_dict['filename'] = file_name
			my_list.append(my_dict)
		return render_template('view_page.html',mydict=my_list)

if __name__ == '__main__':
        app.run(host=HOST)
		
		
		
		

                      