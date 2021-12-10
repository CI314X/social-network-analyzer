from flask import Flask, render_template, request, jsonify, abort, redirect, Response
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_mail import Mail, Message
from config import ADMINS, access_token
import random

from multiprocessing import Process
from generate_pdf import generate_vk_pdf
from delete_file import delete_file
from email_validator import validate_email, EmailNotValidError

from vk_graph import resolve_url_to_id
import vk_api

import sys
import logging

app = Flask(__name__)
app.config.from_object('config')


mail = Mail(app)

from custom_logger import logger


def create_and_send_message(user_name: str, id_link: int, email: str, pdf_name: str, option_downloading_vk: str) -> None:

    generate_vk_pdf(pdf_name, id_link, user_name, option_downloading_vk)

    message = Message('VK statistics', sender = ADMINS[0], recipients = [email])
    message.body = f'Sending informatin to {user_name}.\nvk id = {id_link}.\n\n\n\nBest wishes, Daniil Konstantinov'
    #msg.html = '<b> hello ></b> Daniil'
    with app.open_resource(pdf_name) as fp:
        message.attach(filename=f"{user_name}.pdf", disposition="attachment", content_type="application/pdf", data=fp.read())
    delete_file(pdf_name)

    with app.app_context():
            mail.send(message)
    return


@app.route('/vk_statistics', methods=['GET', 'POST'])
def main_form_vl_statistics():
    if request.method == 'POST':
        email = request.form.get('email')
        user_name = request.form.get('user_name')
        id_link = request.form.get('link')
        option_downloading_vk = request.form.get('option_download')

        logger.info(f'email: {email}')
        logger.info(f'user name: {user_name}')
        logger.info(f'vk id: {id_link}')
        logger.info(f'option: {option_downloading_vk}')

        try:
            valid = validate_email(email)
            email = valid.email
            vk = vk_api.VkApi(token=random.choice(access_token))
            vk_id, is_closed, can_access_closed = resolve_url_to_id(vk, id_link)
        except EmailNotValidError as e:
            logger.error(f'Wrong email. {str(e)}')
            return f'<p>Wrong email. {str(e)}</p>'
        except vk_api.vk_api.ApiError as e:
            logger.error(f'Wrong link for vk profile. {str(e)}')
            return f'<p>Wrong link for vk profile. {str(e)}</p>'
        except:
            logger.error('Unknown error')
            return f'<p>Unknown error</p>'

        if is_closed and not can_access_closed:
            logger.error('Account is closed, no access to information')
            return f'<p>Account is closed, no access to information</p>'

        if option_downloading_vk not in ['fast', 'slow']:
            logger.error('Wrong option')
            return f'<p>Wrong option</p>'

        pdf_name = "generated_docs/" + user_name + ".pdf"

        process_creating_message = Process(
            target=create_and_send_message,
            args=(user_name, vk_id, email, pdf_name, option_downloading_vk),
            daemon=True
        )
        process_creating_message.start()
        
        return f'<p>Sent to {email}</p>'

    return render_template('vk_statistics.html')


@app.route("/")
def hello_world():
    return render_template('root.html')


@app.route('/badrequest400')
def bad_request():
    """ error """
    return abort(400)
