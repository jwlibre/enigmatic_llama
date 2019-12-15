from flask import Flask, jsonify
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="PASSWORD",
  database="employees"
)

mycursor = mydb.cursor()

app = Flask(__name__)

@app.route('/')
def index():
    text = "/api/employees = GET all employees"
    return text

@app.route('/api/employees', methods=['GET'])
def get_employees():
    employees = mycursor.execute("SELECT * FROM employees.employees LIMIT 10;")
    myresult = mycursor.fetchall()
    employees = myresult
    return jsonify(employees)

# INCOMPLETE! OUT OF TIME!
# @app.route('/api/add_employee/firstname=', methods=['POST'])
# def post_employees():
#     max_id = mycursor.execute("select emp_no from employees order by emp_no desc limit 1;")
#     new_id = int(max_id.fetchall()) + 1
#


if __name__ == '__main__':
    app.run(debug=True)
