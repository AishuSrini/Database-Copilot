# Flask Application for Generating Text using OpenAI's Chat Completion API.

# This application exposes an endpoint '/generate_text' that accepts POST requests
# with a JSON payload containing a 'prompt'. It utilizes OpenAI's Chat Completion API
# to generate text based on the given prompt.

# Dependencies:
#    - Flask: Web framework for creating the application.
#    - openai: Python client for interacting with OpenAI's API.
#    - os: Provides a way to interact with the operating system.
#    - json: Library for working with JSON data.

# Usage:
#    - Ensure that the required dependencies are installed.
#    - Start the Flask application using '__name__' as the root.

# Endpoints:
#    - '/generate_text' (POST): Generates text based on the provided prompt.

# Configuration:
#    - The application expects a 'config.json' file containing configuration details.
#      Example configuration:
#        {
#          "CHATGPT_MODEL": "gpt-3.5-turbo",
#          "OPENAI_API_BASE": "https://api.openai.com/v1/",
#          "OPENAI_API_VERSION": "2023-03-15-preview"
#        }

# Note: Ensure that the 'OPENAI_API_KEY' environment variable is set with the API key.

# Import necessary modules
from flask import Flask, jsonify, request
import openai
import os
import json
import pypyodbc as odbc
import pandas as pd
import os

# Creates an instance of the Flask class
app = Flask(__name__)


# Endpoint for generating text based on the provided prompt.
@app.route("/generate_text", methods=["POST"])
def generate_text():
    """
    Endpoint for generating text based on the provided prompt.

    Accepts a POST request with a JSON payload containing a 'prompt'.
    Utilizes OpenAI's Chat Completion API to generate text.

    Returns:
        JSON response containing the generated text.

    Raises:
        openai.error.APIError: If there is an error with the OpenAI API.
        openai.error.AuthenticationError: If there is an authentication error.
        openai.error.APIConnectionError: If there is a connection error with the API.
        openai.error.InvalidRequestError: If the API request is invalid.
        openai.error.RateLimitError: If the API request exceeds the rate limit.
        openai.error.ServiceUnavailableError: If the OpenAI service is unavailable.
        openai.error.Timeout: If the API request times out.
        Exception: Handles all other exceptions.
    """
    try:
        # Extract prompt from JSON payload
        prompt = request.json.get("prompt", "")

        # Read SQL script from file
        script_file_path = os.path.join(os.path.dirname(__file__), "sql.yaml")
        with open(script_file_path, "r") as script_file:
            sql_script = script_file.read()

        finalprompt = f"""Given an input question, use sql server syntax to generate a sql query by choosing 
                    one or multiple of the following tables. Write query in proper SQL format and just return that.

                    For this Problem you can use the following table Schema:
                    Script:\n {sql_script}

                    Please provide the SQL query for this question: 
                    Question: {prompt} """

        # Load config values from 'config.json'
        with open(r"config.json") as config_file:
            config_details = json.load(config_file)

        # Setting up the deployment name
        chatgpt_model_name = config_details["CHATGPT_MODEL"]

        # Set OpenAI API type to 'azure'
        openai.api_type = config_details["API_TYPE"]

        # Set OpenAI API key from environment variable
        openai.api_key = os.getenv("OpenAI_Key")

        # Set OpenAI API base URL from config
        openai.api_base = config_details["OPENAI_API_BASE"]

        # Set OpenAI API version from config
        openai.api_version = config_details["OPENAI_API_VERSION"]

        # Call OpenAI's Chat Completion API
        response = openai.ChatCompletion.create(
            engine=chatgpt_model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a SQL query generator assistant.",
                },
                {
                    "role": "user",
                    "content": finalprompt,
                },
            ],
        )

        # Extract and return the generated text
        generated_sql = response["choices"][0]["message"]["content"]

        DRIVER_NAME = config_details["DRIVER_NAME"]
        SERVER_NAME = os.getenv("SERVER_NAME")
        DATABASE_NAME = os.getenv("DATABASE_NAME")
        Uid = os.getenv("USER_ID")
        Pwd = os.getenv("PASS")

        connection_string = f"""
            DRIVER={{{DRIVER_NAME}}};
            SERVER={SERVER_NAME};
            DATABASE={DATABASE_NAME};
            Uid={Uid};
            Pwd={Pwd};
            Trust_connection=yes;
        """

        conn = odbc.connect(connection_string)
        cursor = conn.cursor()
        print(conn)
        select_query = f"{generated_sql}"
        cursor.execute(select_query)
        selected_rows = cursor.fetchall()
        # print(select_query)
        # print(selected_rows)
        # Get column names from cursor description
        column_names = [column[0] for column in cursor.description]
        # Convert selected_rows to a list of dictionaries
        json_selected_rows = [dict(zip(column_names, row)) for row in selected_rows]

        summary = generate_summary(json_selected_rows, generated_sql)

        return jsonify(
            {
                "selected_rows": json_selected_rows,
                "query": generated_sql,
                "summary": summary,
            }
        )

    except openai.error.APIError as e:
        # Handle API error here, e.g., retry or log
        print(f"OpenAI API returned an API Error: {e}")

    except openai.error.AuthenticationError as e:
        # Handle Authentication error here, e.g., an invalid API key
        print(f"OpenAI API returned an Authentication Error: {e}")

    except openai.error.APIConnectionError as e:
        # Handle connection error here
        print(f"Failed to connect to the OpenAI API: {e}")

    except openai.error.InvalidRequestError as e:
        # Handle connection error here
        print(f"Invalid Request Error: {e}")

    except openai.error.RateLimitError as e:
        # Handle rate limit error
        print(f"OpenAI API request exceeded the rate limit: {e}")

    except openai.error.ServiceUnavailableError as e:
        # Handle Service Unavailable error
        print(f"Service Unavailable: {e}")

    except openai.error.Timeout as e:
        # Handle request timeout
        print(f"Request timed out: {e}")

    except TypeError as e:
        print(f"Type error: {e}")

    except Exception as e:
        # Handles all other exceptions
        print(f"An exception has occurred: {e}")


def generate_summary(json_selected_rows, generated_sql):
    try:
        summarization_prompt = "\n".join([str(row) for row in json_selected_rows])

        with open(r"config.json") as config_file:
            config_details = json.load(config_file)

        # Setting up the deployment name
        chatgpt_model_name = config_details["CHATGPT_MODEL"]

        # Set OpenAI API type to 'azure'
        openai.api_type = config_details["API_TYPE"]

        # Set OpenAI API key from the environment variable
        openai.api_key = os.getenv("OpenAI_Key")

        # Set OpenAI API base URL from config
        openai.api_base = config_details["OPENAI_API_BASE"]

        # Set OpenAI API version from config
        openai.api_version = config_details["OPENAI_API_VERSION"]

        response = openai.ChatCompletion.create(
            engine=chatgpt_model_name,
            messages=[
                {
                    "role": "system",
                    "content": "Given an input question,answer that question in simple and easily understandable English language alone without explaing the query.Provide a combined summary of this in 3 lines alone",
                },
                {
                    "role": "user",
                    "content": summarization_prompt,
                },
            ],
        )

        # Extract and return the generated text
        summary = response["choices"][0]["message"]["content"]

        return summary

    except openai.error.APIError as e:
        # Handle API error here, e.g., retry or log
        print(f"OpenAI API returned an API Error: {e}")

    except openai.error.AuthenticationError as e:
        # Handle Authentication error here, e.g., an invalid API key
        print(f"OpenAI API returned an Authentication Error: {e}")

    except openai.error.APIConnectionError as e:
        # Handle connection error here
        print(f"Failed to connect to the OpenAI API: {e}")

    except openai.error.InvalidRequestError as e:
        # Handle connection error here
        print(f"Invalid Request Error: {e}")

    except openai.error.RateLimitError as e:
        # Handle rate limit error
        print(f"OpenAI API request exceeded the rate limit: {e}")

    except openai.error.ServiceUnavailableError as e:
        # Handle Service Unavailable error
        print(f"Service Unavailable: {e}")

    except openai.error.Timeout as e:
        # Handle request timeout
        print(f"Request timed out: {e}")

    except TypeError as e:
        print(f"Type error: {e}")

    except Exception as e:
        # Handles all other exceptions
        print(f"An exception has occurred: {e}")


if __name__ == "__main__":
    # Run the Flask application in debug mode
    app.run(port=8080, debug=True)
# if some_error_condition:
#     print("Error: Some error occurred.")
#     sys.exit(3)
