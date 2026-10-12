from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash, session, jsonify
import google.generativeai as genai
import pymysql
import json
import os

app = Flask(__name__)

# ── Flask session secret ───────────────────────────────────────────────────
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-dev-secret")

# ── Gemini AI Configuration ────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


# ── Database connection helper ─────────────────────────────────────────────
def get_db_connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME"),
        ssl={"ssl_verify_cert": False},
        connect_timeout=10
    )


# ═══════════════════════════════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/courses')
def Courses():
    return render_template('courses.html')

@app.route('/career_compass')
def career_compass():
    return render_template('career_compass.html')

@app.route('/gallery')
def Gallery():
    return render_template('gallery.html')

@app.route('/introduction')
def introduction():
    return render_template('introduction.html')

@app.route('/DSAIML')
def DSAIML():
    return render_template('DSAIML.html')

@app.route('/RPA')
def RPA():
    return render_template('RPA.html')

@app.route('/fullstackdevelopment')
def fullstackdevelopment():
    return render_template('fullstackdevelopment.html')

@app.route('/dbmstools')
def dbmstools():
    return render_template('dbmstools.html')

@app.route('/aitools')
def aitools():
    return render_template('aitools.html')

@app.route('/DSA')
def DSA():
    return render_template('DSA.html')

@app.route('/dataanalytics')
def Data_Analytics():
    return render_template('dataanalytics.html')

@app.route('/FYProject')
def FYProject():
    return render_template('FYProject.html')

@app.route('/achievements')
def achievements():
    return render_template('achievements.html')


# ── CONTACT FORM ───────────────────────────────────────────────────────────
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        try:
            Name          = request.form["name"]
            Email_Address = request.form["email"]
            Mobile_NO     = request.form["mobile"]
            Select_stream = request.form["stream"]
            Education     = request.form["education"]
            Help          = request.form["help"]

            conn   = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contact_requests
                (full_name, email, mobile, stream, education, help_message)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (Name, Email_Address, Mobile_NO, Select_stream, Education, Help))
            conn.commit()
            cursor.close()
            conn.close()
            return render_template('contact.html', message="Submitted successfully!")

        except Exception as e:
            return render_template('contact.html', error=str(e))

    return render_template('contact.html')


# ── CAREER COMPASS — roadmap route ────────────────────────────────────────
@app.route('/generate-roadmap', methods=['POST'])
def generate_roadmap():
    try:
        data      = request.get_json()
        stream    = data.get("stream", "")
        interest  = data.get("interest", "")
        studyMode = data.get("studyMode", "")
        goal      = data.get("goal", "")

        prompt = f"""
You are a professional IT Career Counsellor from WE Institute Mumbai.

Student Details:
Stream: {stream}
Interest: {interest}
Study Path: {studyMode}
Goal: {goal}

Generate a personalized career roadmap.

Return in this exact format:

Career:
Salary:
Demand:

Skills:
- skill 1
- skill 2
- skill 3
- skill 4
- skill 5

Roadmap:
1. Step one
2. Step two
3. Step three
4. Step four

Recommended Courses:
- course 1
- course 2

Motivation:
one motivational sentence
"""
        response = model.generate_content(prompt)
        return jsonify({"success": True, "roadmap": response.text})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# ── CAREER COMPASS — chatbot widget route ─────────────────────────────────
@app.route('/api/career-compass', methods=['POST'])
def api_career_compass():
    try:
        data      = request.get_json()
        stream    = data.get("stream", "")
        interest  = data.get("interest", "")
        studyMode = data.get("studyMode", "")
        goal      = data.get("goal", "")

        prompt = f"""You are a career counsellor at WE Institute, Mumbai — a premier IT training institute.

Student profile:
- 12th stream: {stream}
- Tech interest: {interest}
- Study preference: {studyMode}
- Primary goal: {goal}

WE Institute courses available:
Introduction to Programming (Python/C/C++/Java), Data Science + AI + ML, RPA Development (UiPath/UiRPA),
Data Structures & Algorithms, Data Analytics (Excel/SQL/Tableau/Power BI), AI Tools,
Full Stack Development (HTML/CSS/JS/React/Node), DBMS Tools & Query Languages, Final Year Project Guidance.

Return ONLY a valid JSON object (no markdown, no backticks, no extra text) with exactly this structure:
{{
  "emoji": "single emoji",
  "primaryCareer": "Job title",
  "salaryRange": "₹X – ₹Y LPA (fresher to 3 yrs exp)",
  "demand": "Very High",
  "technicalSkills": ["skill1","skill2","skill3","skill4","skill5"],
  "academicPath": ["Step 1","Step 2","Step 3"],
  "recommendedCourses": ["WE Institute course 1","WE Institute course 2"],
  "motivationalLine": "One short inspiring sentence for this student"
}}"""

        response = model.generate_content(prompt)
        raw = response.text.strip().replace("```json", "").replace("```", "").strip()

        start  = raw.find("{")
        end    = raw.rfind("}") + 1
        result = json.loads(raw[start:end])
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── CHATBOT — follow-up chat route ────────────────────────────────────────
@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        data     = request.get_json()
        messages = data.get("messages", [])

        system = """You are a helpful, friendly AI assistant for WE Institute, a premier IT training institute in Mumbai, India.
Help students with course information, career guidance, admissions, fees, and duration.

WE Institute courses:
- Introduction to Programming (Python/C/C++/Java)
- Full Stack Development (HTML, CSS, JavaScript, React, Node.js)
- Data Science + AI + ML
- Data Analytics (Excel, SQL, Tableau, Power BI)
- RPA Development (UiPath/UiRPA)
- AI Tools
- Data Structures & Algorithms
- DBMS Tools & Query Languages
- Final Year Project Guidance

Keep responses concise and helpful. For specific fees or batch dates, ask them to contact WE Institute at weinstitute.in or +91 9819740122."""

        history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})

        chat        = model.start_chat(history=history)
        last_msg    = messages[-1]["content"] if messages else ""
        full_prompt = f"{system}\n\nStudent: {last_msg}"
        response    = chat.send_message(full_prompt)

        return jsonify({"reply": response.text.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── RUN ───────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
