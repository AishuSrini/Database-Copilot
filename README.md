# Database-Copilot
The Database-Copilot is a Python application developed with Flask, allowing users to create SQL queries based on natural language text. Leveraging the Azure OpenAI language model, the application establishes a connection to a designated database, interprets user prompts to generate SQL queries, executes them, and delivers a concise summary that elucidates and justifies the user's initial question or prompt.

With the Database-Copilot, you don't need to be a SQL expert to understand what's going on in your database, or to write SQL queries. You can simply type in your query in natural language and get the corresponding SQL code and summary of the result( human-readable translation).This project is 100% free and open source.

# 🌟   Features    

* Flask API: Utilizes Flask to create a web API for generating SQL queries.
* Azure OpenAI Integration: Connects to the Azure OpenAI API to generate SQL queries based on user prompts.
* Database Connectivity: Establishes a connection to the specified database to execute generated queries.
* Query Summarization: Provides a summarized response to explain and justify the user's original question or prompt.
* POST Method Support: Allows handling POST requests, facilitating interaction via tools like Postman.

# 🛠️   Installation  

Clone the repository:   
```
git clone https://github.com/your-username/API-Query-Generator.git   

cd API-Query-Generator   
```
Install dependencies:    
```
pip install -r requirements.txt    
```
Configure OpenAI API key:    

Add your OpenAI API key to the config.py file:   
```
OPENAI_API_KEY = 'your_openai_api_key_here'    
```
Configure database connection:   

Update the config.py file with your database connection detail    
```
DATABASE_CONFIG = {  

    'host': 'your_database_host',   
    
    'user': 'your_database_user',    
    
    'password': 'your_database_password',    
    
    'database': 'your_database_name',    
    
}   

```
# 🖥️   Usage   

Run the Flask application:
```
python app.py
```
Access the API at http://localhost:5000 and use it to generate SQL queries.
POST /generate-query: Generates a SQL query based on user input.

Example using Postman:

Set the HTTP method to POST.
Enter the API endpoint: http://localhost:5000/generate-query.
In the request body, provide a JSON object with the user prompt:
```
{
   "prompt": "i want to find last 5 customer sales data"
}
```
Response:
```
{
    "query": "SELECT TOP 5 *\nFROM SalesLT.SalesOrderHeader\nWHERE CustomerID IN (\n    SELECT TOP 5 CustomerID\n    FROM SalesLT.Customer\n    ORDER BY ModifiedDate DESC\n)\nORDER BY OrderDate DESC;",
    "selected_rows": [],
    "summary": "The SQL query aims to retrieve the most recent sales data for the last 5 customers. It does this by selecting the top 5 rows from the SalesLT.SalesOrderHeader table, where the associated CustomerID is among the top 5 customers from the SalesLT.Customer table, sorted by their latest modification date, and finally, the result is ordered by the order date in descending order."
}
```
# 👥   Contributing   

Contributions to Database-Copilot are welcome and encouraged! To contribute, please follow these steps:

* Fork the repository  

* Create a new branch   

* Make your changes    

* Push your changes to your fork    

* Submit a pull request  

# 📜   License  

Database-Copilot is released under the MIT License.
