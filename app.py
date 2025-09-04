import streamlit as st
import sqlite3
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")
# Configure Gemini API
genai.configure(api_key=gemini_key)  # Replace with your actual API key
# Function: Prompt Gemini to generate SQL
def get_gemini_sql(question, prompt):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content([prompt[0], question])
    sql_query = response.text.strip()
    sql_query = sql_query.replace("```sql", "").replace("```", "")
    return sql_query

# Function: Optional SQL explanation
def explain_sql_query(query):
    explain_prompt = f"Explain this SQL query step-by-step in simple terms:\n{query}"
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(explain_prompt)
    return response.text.strip()

# Function: Run SQL on SQLite and return rows + column names
def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        if(cur.description):
           col_names = [desc[0] for desc in cur.description]  # dynamic column names
           conn.close()
           return rows, col_names
        else:
            conn.commit()
            conn.close()
            return [], []
    except sqlite3.Error as e:
        return [("SQL Error", str(e))], ["Error"]

# Professional 6-Part Prompt for Gemini
prompt = ["""
# 1. Context:
You are helping a user interact with a SQLite database using natural language.

# 2. Role:
You are an expert SQL assistant who converts English questions into SQLite queries.

# 3. Constraints:
- Use only SQLite syntax.
- Target database: employees.
- Table: employees.
- Columns: employee_name (text), employee_role (text), employee_salary (float).
- Do not use backticks (`), triple quotes (```), or semicolons.
- Keep SQL readable and correct.

# 4. Instructions:
- Translate the user's question into a valid SQL query.
- Be precise in filtering, grouping, or sorting.
- Make sure the column names and logic match the schema.

# 5. Few-shot Examples:

Q: How many employees are there?
A: SELECT COUNT(*) FROM employees

Q: Show all Data Engineers
A: SELECT * FROM employees WHERE employee_role = 'Data Engineer'

Q: Who earns more than 60000?
A: SELECT * FROM employees WHERE employee_salary > 60000

Q: Who earns the highest salary?
A: SELECT * FROM employees ORDER BY employee_salary DESC LIMIT 1

# 6. Chain of Thought:
First, understand the user’s question and identify relevant filters or conditions.  
Then map to the appropriate SQL clause (e.g., SELECT, WHERE, GROUP BY, ORDER BY).  
Finally, return the correct and clean SQL query.

Now generate the SQL query for this question:
"""]

# Streamlit App UI
st.markdown("""
                   <style>
                   .title {
                       font-size: 40px;
                       font-weight: bold;
                       text-align: center;
                       color: #ffffff;
                       text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffcc, 0 0 30px #00ff99;
                   }
                   .subtitle {
                       font-size: 20px;
                       text-align: center;
                       color: #f5f5f5;
                       margin-bottom: 20px;
                   }
                   .stTextInput>div>div>input {
                       border: 2px solid #00ffcc;
                       border-radius: 10px;
                       background-color: #111111;
                       color: white;
                       font-size: 18px;
                       padding: 10px;
                   }
                   .stButton>button {
                       background: linear-gradient(90deg, #ff00cc, #3333ff);
                       color: white;
                       border-radius: 12px;
                       padding: 10px 20px;
                       font-size: 18px;
                       font-weight: bold;
                       border: none;
                       box-shadow: 0px 0px 15px #ff00cc;
                       transition: all 0.3s ease-in-out;
                   }
                   .stButton>button:hover {
                       transform: scale(1.05);
                       box-shadow: 0px 0px 25px #00ffff;
                   }
                   .section-title {
        font-size: 28px;
        font-weight: bold;
        margin-top: 25px;
        color: #ffffff;
        text-shadow: 0 0 10px #ff00ff, 0 0 20px #00ffff;
    }
    .section1-title {
        font-size: 28px;
        font-weight: bold;
        margin-top: 25px;
        color: #ffffff;
        text-shadow: 0 0 20px yellow, 0 0 20px yellow;
    }

    /* SQL Query Box */
    .sql-box {
        background-color: #1e1e2f;
        border: 2px solid #00ffff;
        padding: 12px;
        border-radius: 12px;
        font-family: 'Courier New', monospace;
        font-size: 16px;
        color: #00ffcc;
        text-shadow: 0 0 5px #00ffff;
        margin-bottom: 20px;
    }

    /* DataFrame Table Styling */
    .stDataFrame {
        border: 2px solid #00ffff !important;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0px 0px 20px #00ffff88;
    }
    
                   </style>
               """, unsafe_allow_html=True)
st.set_page_config(page_title="LLM SQL Assistant")
st.markdown('<div class="title">💎 Gemini SQL Assistant (Employee DB)📊</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">✨ Ask questions in English → Get SQL queries + results instantly! 🚀</div>', unsafe_allow_html=True)

# User input
question = st.text_input("🔍 Enter your question:")

# Sample suggestions
with st.expander("💡Try These Examples"):
    st.markdown("""
    👉 List all employees.\n
    👉 Show only Data Scientists.\n
    👉 Who earns more than 60,000?\n
    👉 Count of Data Engineers?\n
    👉 Highest salary employee?\n
    👉 Provide the average salary based on job role.
    """)

# Submit
if st.button("⚡ Run Query"):
    if question.strip() == "":
        st.warning("⚠️ Please enter a question.")
    else:
        # Generate SQL
        sql_query = get_gemini_sql(question, prompt)
        st.markdown("<div class='section-title'>📝 Generated SQL Query:</div>", unsafe_allow_html=True)
        st.code(sql_query, language="sql")

        # Run SQL query
        result, columns = read_sql_query(sql_query, "my_db.db")

        # st.write(result)
        # st.write(columns)




        # Show result
        if result and "SQL Error" in result[0]:
            st.error(f"Error: {result[0][1]}")
        else:
            st.markdown('<div class="section-title">📊 Query Result:</div>', unsafe_allow_html=True)
            if(not result and not columns):
                st.success("✅ Employees table updated successfully (No records returned)")
            else:
                df = pd.DataFrame(result, columns=columns)
                st.dataframe(df, use_container_width=True)
            # Explanation
            st.markdown("<div class='section1-title'>💡 Query Explanation</div>", unsafe_allow_html=True)
            with st.expander("Gemini Explains the SQL"):
                explanation = explain_sql_query(sql_query)
                st.write(explanation)





