# Import necessary libraries
from flask import Flask, render_template, flash, redirect, url_for, request
import mysql.connector

# Create Flask app and configure MySQL
app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Manasbir27',
    'database': 'PlacementDatabase'
}

db = mysql.connector.connect(**db_config)
cursor = db.cursor()


@app.route('/')
def home():
    try:
        # Assuming you have a list of image URLs
        image_urls = [
            '1.jpg',
            '2.jpg',
            '3.jpg',
            # Add more image URLs as needed
        ]
        return render_template('home.html', image_urls=image_urls)
    except Exception as e:
        # Handle the exception (log it, display an error page, etc.)
        print(f"Error: {e}")
        flash("An error occurred. Please try again later.", "error")
        return redirect(url_for('index'))



# Modify the '/companies' route as follows
@app.route('/companies')
def companies():
    try:
        # Fetch data including participation and selection counts
        cursor.execute("SELECT CompanyInfo.*, "
                       "SUM(PlacementProcess.Participation) AS TotalParticipation, "
                       "SUM(PlacementProcess.Selection) AS TotalSelection "
                       "FROM CompanyInfo "
                       "LEFT JOIN PlacementProcess ON CompanyInfo.CompanyName = PlacementProcess.CompanyName "
                       "GROUP BY CompanyInfo.CompanyName")
        companies_data = cursor.fetchall()

        return render_template('companies.html', companies=companies_data)
    except Exception as e:
        flash(f"Error fetching data: {str(e)}", 'error')
        return render_template('companies.html', companies=None)


# ...
def fetch_filter_options(table, column):
    try:
        cursor.execute(f"SELECT DISTINCT {column} FROM {table}")
        options = [row[0] for row in cursor.fetchall()]
        return options
    except Exception as e:
        flash(f"Error fetching filter options: {str(e)}", 'error')
        return []

@app.route('/selected_students')
def selected_students():
    try:
        # Fetch filter parameters from the request
        company_name = request.args.get('company_name', '')
        year = request.args.get('year', '')
        round_number = request.args.get('round_number', '')
        internship = request.args.get('internship', '')

        # Build the SQL query based on filters
        sql_query = "SELECT * FROM SelectedStudents WHERE 1=1"

        conditions = []

        if company_name and company_name.lower() != 'all':
            conditions.append(f"CompanyName = '{company_name}'")
        if year and year.lower() != 'all':
            conditions.append(f"Year = {year}")
        if round_number and round_number.lower() != 'all':
            conditions.append(f"RoundNumber = {round_number}")
        if internship and internship.lower() != 'all':
            conditions.append(f"Internship = '{internship}'")

        if conditions:
            sql_query += " AND " + " AND ".join(conditions)

        # Fetch selected students data from MySQL
        cursor.execute(sql_query)
        students_data = cursor.fetchall()

        # Fetch distinct options for populating the filter dropdowns
        companies = fetch_filter_options("SelectedStudents", "CompanyName")
        years = fetch_filter_options("SelectedStudents", "Year")
        rounds = fetch_filter_options("SelectedStudents", "RoundNumber")

        # Get the count of selected students
        selected_students_count = len(students_data)

        return render_template('selected_students.html', students_data=students_data,
                               company_name=company_name, year=year,
                               round_number=round_number, internship=internship,
                               companies=companies, years=years,
                               rounds=rounds, selected_students_count=selected_students_count)
    except Exception as e:
        flash(f"Error fetching data: {str(e)}", 'error')
        return render_template('selected_students.html', students_data=None)



# Modify the '/previous_year_questions' route as follows
@app.route('/previous_year_questions')
def previous_year_questions():
    try:
        # Fetch filter parameters from the request
        company_name = request.args.get('company_name')
        year = request.args.get('year')
        round_number = request.args.get('round_number')
        question_type = request.args.get('question_type')

        # Build the SQL query based on filters
        sql_query = "SELECT * FROM PreviousYearQuestions WHERE 1=1"
        if company_name:
            sql_query += f" AND CompanyName = '{company_name}'"
        if year:
            sql_query += f" AND Year = {year}"
        if round_number:
            sql_query += f" AND RoundNumber = {round_number}"
        if question_type:
            sql_query += f" AND QuestionType = '{question_type}'"

        # Fetch questions data from MySQL
        cursor.execute(sql_query)
        questions_data = cursor.fetchall()

        # Fetch distinct years, companies, and rounds for populating the filter dropdowns
        cursor.execute("SELECT DISTINCT Year FROM PreviousYearQuestions")
        years = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT CompanyName FROM PreviousYearQuestions")
        companies = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT RoundNumber FROM PreviousYearQuestions")
        rounds = [row[0] for row in cursor.fetchall()]

        # Pass the questions data, filter parameters, and filter options to the template
        return render_template('previous_year_questions.html', questions=questions_data,
                               company_name=company_name, year=year, round_number=round_number,
                               question_type=question_type, years=years, companies=companies, rounds=rounds)
    except Exception as e:
        flash(f"Error fetching data: {str(e)}", 'error')
        return render_template('previous_year_questions.html', questions=None)

# Python code in your Flask app
@app.route('/calculate_cgpa', methods=['GET', 'POST'])
def calculate_cgpa():
    if request.method == 'POST':
        current_cgpa = float(request.form.get('current_cgpa'))
        completed_semesters = int(request.form.get('completed_semesters'))
        desired_company = request.form.get('desired_company')
        completed_credits = int(request.form.get('completed_credits'))
        credits_left = int(request.form.get('credits_left'))

        # Call the CalculateRequiredCGPA function in the database
        cursor.execute(
            "SELECT CalculateRequiredCGPA(%s, %s, %s, %s, %s) AS result",
            (current_cgpa, completed_semesters, desired_company, completed_credits, credits_left)
        )
        result = cursor.fetchone()[0]

        return render_template('calculator.html', result=result)

    return render_template('calculator.html')
# Add this route in your Flask app

@app.route('/job_descriptions')
def job_descriptions():
    try:
        # Fetch job descriptions data from MySQL
        cursor.execute("SELECT * FROM JobDescriptions")
        job_descriptions_data = cursor.fetchall()

        # Print the data for debugging
        print(job_descriptions_data)

        return render_template('job_descriptions.html', job_descriptions=job_descriptions_data)
    except Exception as e:
        flash(f"Error fetching data: {str(e)}", 'error')
        return render_template('job_descriptions.html', job_descriptions=None)



@app.route('/candidates')
def candidates():
    try:
        # Fetch candidate data from MySQL (modify this query based on your needs)
        cursor.execute("SELECT * FROM Candidate")
        candidates_data = cursor.fetchall()

        # Fetch total and selected counts from PlacementProcess
        cursor.execute("SELECT SUM(Participation) AS TotalParticipation, SUM(Selection) AS TotalSelection FROM PlacementProcess")
        counts_data = cursor.fetchone()
        total_participation = counts_data[0] if counts_data[0] is not None else 0
        total_selection = counts_data[1] if counts_data[1] is not None else 0

        # Print the data for debugging
        print(candidates_data)

        return render_template('candidates.html', candidates=candidates_data,
                               total_participation=total_participation,
                               total_selection=total_selection)
    except Exception as e:
        flash(f"Error fetching candidates data: {str(e)}", 'error')
        return render_template('candidates.html', candidates=None)


@app.route('/cdc', methods=['GET', 'POST'])
def cdc():
    if request.method == 'POST':
        # Retrieve form data
        student_name = request.form.get('student_name')
        question_text = request.form.get('question')

        # Insert the question into the database
        cursor.execute("INSERT INTO StudentQuestions (StudentName, QuestionText) VALUES (%s, %s)",
                       (student_name, question_text))
        db.commit()

        flash('Your question has been submitted successfully!', 'success')
    
    return render_template('cdc.html')


if __name__ == '__main__':
    app.run(debug=True)