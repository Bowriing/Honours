from openai import OpenAI
import os
from flask import Blueprint, flash, jsonify, request, redirect, url_for
from flask_login import login_required, current_user

gpt = Blueprint('gpt', __name__)

client = OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],
)

@gpt.route('/fetch-power-rating', methods=['POST'])
@login_required
def fetch_power_rating():
    device_name = request.json.get('deviceName')
    device_type = request.json.get('deviceType')

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "system", "content": "Input contains: device name and device type,ONLY OUTPUT A 3/4 DIGIT INTEGER!!! representing average wattage for this device"},
                  {"role": "user", "content": f"Device Name: {device_name}, Type Of Device: {device_type}"}],
        max_tokens=100,
        temperature=0.9,
        top_p=0.9,
    )
    
    power_rating = response.choices[0].message.content
    return jsonify({'power_rating' : power_rating})