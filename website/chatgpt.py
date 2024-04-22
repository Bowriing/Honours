from openai import OpenAI
import os
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, flash, redirect, url_for, session

gpt = Blueprint('gpt', __name__)

client = OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],
)

@gpt.route('/response', methods=['POST'])
@login_required
def response():
    csv_data = current_user.csv_data
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",  # Make sure to specify the latest model you have access to
        messages=[{"role": "system", "content": "You will get an input of, device name, device type. Return ONLY an integer representing an accurate power rating for the device in watts"},
                  {"role": "user", "content": "4090 PC, Computer"}],
        max_tokens=100,
        temperature=0.9,
        top_p=0.9,
        )
    
    response_text = response.choices[0].message.content

    return render_template("home.html", csv_data=csv_data, gpt_response=response_text)
