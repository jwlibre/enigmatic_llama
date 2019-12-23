from flask import Flask, jsonify, render_template, request
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="{USERNAME}",
  password="{PASSWORD}",
  database="employees"
)

mycursor = mydb.cursor()

app = Flask(__name__)

# function to retrieve parameters from URL, used in GET and DELETE requests
# (do not allow searches by birth date or hire date)
def retrieve_params():
    data = {}

    ### Retrieve parameters
    # Trivial case where no parameters are supplied - return all data from table
    if len(request.args) == 0:
        return data

    else:
        emp_no = request.args.get('emp_no')
        data['emp_no'] = emp_no

        first_name = request.args.get('first_name')
        data['first_name'] = first_name

        last_name = request.args.get('last_name')
        data['last_name'] = last_name

        gender = request.args.get('gender')
        data['gender'] = gender

        data_parsed = {}

        for key in data.keys():
            if data[key] != None:
                data_parsed[key] = data[key]

        # error handling - return ERROR if no valid parameter name is specified
        if len(data_parsed) == 0:
            data_parsed = "ERROR"

        return data_parsed


# INDEX
@app.route('/')
def index():
    return render_template("index.html")

# POST (ADD)
@app.route('/api/add', methods=['POST'])
def add_employee():

    if request.content_type != "application/json":
        return jsonify('No valid JSON payload found. Body must be of JSON format.'), 400

    elif request.json == None:
        return jsonify('No body found.'), 400

    else:
        try:
            _json = request.json
            emp_no = _json['emp_no']
            first_name = _json['first_name']
            last_name = _json['last_name']
            birth_date = _json['birth_date']
            gender = _json['gender']
            hire_date = _json['hire_date']
        except:
            return jsonify("ERROR: All fields must contain values specified in the request body."), 400

        try:
            sql = "INSERT INTO employees.employees(emp_no, first_name, last_name, birth_date, gender, hire_date) VALUES(%s, %s, %s, %s, %s, %s)"
            data = (emp_no, first_name, last_name, birth_date, gender, hire_date)
            mycursor.execute(sql, data)
            mydb.commit()
            return jsonify('Employee added successfully!'), 201
        except:
            sql = "SELECT * FROM employees.employees WHERE emp_no = {};".format(emp_no)
            mycursor.execute(sql)
            result = mycursor.fetchall()
            if len(result) > 0:
                return jsonify('Bad request - entry with emp_no {} already exists. Select another emp_no or make an update or delete request.'.format(emp_no)), 400
            else:
                return jsonify('Server error.'), 500

# PUT (UPDATE): allows update of profiles based on emp_no
@app.route('/api/update', methods=['PUT'])
def update():

    if request.content_type != "application/json":
        return jsonify('No valid JSON payload found. Body must be of JSON format.'), 400

    elif request.json == None:
        return jsonify('No body found.'), 400

    else:
        try:
            _json = request.json
            emp_no = _json['emp_no']
            new_first_name = _json['first_name']
            new_last_name = _json['last_name']
            new_birth_date = _json['birth_date']
            new_gender = _json['gender']
            new_hire_date = _json['hire_date']
        except:
            return jsonify("ERROR: All fields must contain values specified in the request body."), 400

        # investigate whether entry exists already
        sql = "SELECT * FROM employees.employees WHERE emp_no = {};".format(emp_no)
        mycursor.execute(sql)
        result = mycursor.fetchall()
        if len(result) == 0:
            return jsonify('Bad request - no entry with emp_no {} found. Select another emp_no or make an add request.'.format(emp_no)), 400

        else:
            try:
                sql = "UPDATE employees.employees SET first_name=%s, last_name=%s, birth_date=%s, gender=%s, hire_date=%s WHERE emp_no=%s;"
                data = (new_first_name, new_last_name, new_birth_date, new_gender, new_hire_date, emp_no)
                mycursor.execute(sql, data)
                mydb.commit()
                return jsonify('Employee updated successfully!'), 200

            except:
                return jsonify('Server error.'), 500

# GET
@app.route('/api/get', methods=['GET'])
def get_employee():
    data = retrieve_params()
    if data == "ERROR":
        return jsonify('Error! No valid parameters selected.'), 400
    else:
        # Build SQL
        if len(data) == 0:
            sql = "SELECT * FROM employees.employees LIMIT 20;"
        else:
            sql = "SELECT * FROM employees.employees WHERE"
            i = 1
            for parameter in data.keys():
                sql = sql + " {} = '{}' ".format(parameter, data[parameter])
                if i != len(data):
                    sql = sql + "AND"
                else:
                    sql = sql + "LIMIT 20;"
                i += 1
        # Execute query
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        return jsonify(myresult), 200

# DELETE
@app.route('/api/delete', methods=['DELETE'])
def delete_employee():
    data = retrieve_params()

    if len(data) == 0:
        return jsonify("ERROR: no parameters supplied."), 400
    elif data == 'ERROR':
        return jsonify("Error! No valid parameters selected."), 400

    else:
        # investigate whether entry exists already
        sql = "SELECT * FROM employees.employees WHERE emp_no = {};".format(data['emp_no'])
        mycursor.execute(sql)
        result = mycursor.fetchall()
        if len(result) == 0:
            return jsonify('Bad request - no entry with emp_no {} found. Select another emp_no or make an add request.'.format(data['emp_no'])), 400
        else:  # Build SQL
            sql = "DELETE FROM employees.employees WHERE"
            i = 1
            for parameter in data.keys():
                sql = sql + " {} = '{}' ".format(parameter, data[parameter])
                if i != len(data):
                    sql = sql + "AND"
                else:
                    sql = sql + ";"
                i += 1

            # Execute query
            mycursor.execute(sql)
            mydb.commit()
            return jsonify("Employee(s) deleted successfully"), 200


if __name__ == '__main__':
    app.run(debug=True)
