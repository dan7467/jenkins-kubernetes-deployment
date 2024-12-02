from mailjet_rest import Client
from hashlib import md5
from bcrypt import hashpw
from tokens_handler import get_credentials

credentials = get_credentials('mailjet')
client = Client(auth=(credentials['api_key'], credentials['secret_key']), version='v3.1')

def send(to_mail, to_name, subject, html_content):
    data = {
        'Messages': [
                        {
                                "From": {
                                        "Email": "danbendr@post.bgu.ac.il",
                                        "Name": "JobHaven"
                                },
                                "To": [
                                        {
                                                "Email": to_mail,
                                                "Name": to_name
                                        }
                                ],
                                "Subject": subject,
                                "TextPart": "",
                                "HTMLPart": html_content
                        }
                ]
    }
    return client.send.create(data=data)

def send_verification_mail(to_mail, to_name, verification_code):
    random_code = ' '.join(verification_code)
    data = {
        'Messages': [
                        {
                                "From": {
                                        "Email": "danbendr@post.bgu.ac.il",
                                        "Name": "JobHaven"
                                },
                                "To": [
                                        {
                                                "Email": to_mail,
                                                "Name": to_name
                                        }
                                ],
                                "Subject": "Verify your E-mail address",
                                "TextPart": "",
                                "HTMLPart": f"""
                                                <head>
                                                    <style>
                                                        .container {{
                                                            font-family: Arial, sans-serif;
                                                            max-width: 600px;
                                                            margin: auto;
                                                            padding: 20px;
                                                            border: 1px solid #ccc;
                                                            border-radius: 5px;
                                                        }}
                                                        .button {{
                                                            display: inline-block;
                                                            margin-top: 20px;
                                                            padding: 10px 20px;
                                                            font-size: 16px;
                                                            color: #ffffff;
                                                            background-color: #BFCFE7;
                                                            text-decoration: none;
                                                            border-radius: 5px;
                                                        }}
                                                        .secret_code{{
                                                            text-align: center;
                                                        }}
                                                    </style>
                                                </head>
                                                <body>
                                                    <div class="container">
                                                        <h2>JobHaven - Email Verification</h2>
                                                        <p>Hello,</p>
                                                        <p>Thank you for signing up! Please verify your email address by using the code below:</p>
                                                        <div class="secret_code"><h2>{random_code}</h2></div>
                                                        <p>If you did not create this account, please ignore this email.</p>
                                                        <p>Thank you,<br>JobHaven Team</p>
                                                    </div>
                                                </body>
                                                """
                        }
                ]
    }
    return client.send.create(data=data).json()