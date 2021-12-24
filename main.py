from flask import Flask, render_template, request, abort
from flask_mail import Mail, Message
from config import ADMINS, access_token, telegram_token
import random

from multiprocessing import Process
from generate_pdf import generate_vk_pdf
from delete_file import delete_file
from email_validator import validate_email, EmailNotValidError

from vk_graph import resolve_url_to_id
import vk_api

import telebot


app = Flask(__name__)
app.config.from_object('config')


mail = Mail(app)

from custom_logger import logger


def create_and_send_message(user_name: str, id_link: int, email: str, telegram_id: str, pdf_name: str, option_downloading_vk: str) -> None:
    """
    Creates pdf and send message to a given email
    
    Parameters
    ----------
    user_name: str
        User name
    id_link: int
        id in vk.com
    email: str
        given email
    pdf_name: str
        name of the PDF file to create
    option_downloading_vk: str
        either "fast" or "slow" - type of creating friend's graph
    """
    logger.info('start creating pdf file')
    generate_vk_pdf(pdf_name, id_link, user_name, option_downloading_vk)
    logger.info('PDF created')
    if email:
        message = Message('VK statistics', sender = ADMINS[0], recipients = [email])
        message.body = f'Sending informatin to {user_name}.\nvk id = {id_link}.\n\n\n\nBest wishes, Daniil Konstantinov'
        #msg.html = '<b> hello ></b> Daniil'
        with app.open_resource(pdf_name) as fp:
            message.attach(filename=f"{user_name}.pdf", disposition="attachment", content_type="application/pdf", data=fp.read())

        with app.app_context():
            mail.send(message)
        logger.info(f'Sent to email')

    if telegram_id:
        try:
            bot = telebot.TeleBot(telegram_token)
            document = open(pdf_name, 'rb')
            bot.send_document(telegram_id, document)
            document.close()
            logger.info(f'Sent to telegram')
        except Exception as e:
            logger.error(f'Problem with telegram ID: {str(e)}')

    
    delete_file(pdf_name)


    logger.info('End of work')
    return


@app.route("/")
def root():
    """
    Main page with all information
    """
    return render_template('root.html')



@app.route('/badrequest400')
def bad_request():
    """ error """
    return abort(400)


@app.route("/vk_statistics", methods=['GET', 'POST'])
def main_form():
    """
    On this page you can specify data for analysis
    """

    if request.method == 'POST':
        logger.info('POST smth')
        email = request.form.get('email')
        user_name = request.form.get('user_name')
        vk_link = request.form.get('vk_link')
        telegram_id = request.form.get('telegram_link')

        option_downloading_vk = request.form.get('download_option')
        
        logger.info(f'user name: {user_name}')
        logger.info(f'vk id: {vk_link}')
        logger.info(f'email: {email}')
        logger.info(f'telegram ID: {telegram_id}')
        logger.info(f'option: {option_downloading_vk}')

        try:
            if email:
                email = validate_email(email).email
            vk = vk_api.VkApi(token=random.choice(access_token))
            vk_id, is_closed, can_access_closed = resolve_url_to_id(vk, vk_link)
        except EmailNotValidError as e:
            logger.error(f'Wrong email. {str(e)}')
            return f'<p>Wrong email. {str(e)}</p>'
        except vk_api.vk_api.ApiError as e:
            logger.error(f'Wrong link for vk profile. {str(e)}')
            return f'<p>Wrong link for vk profile. {str(e)}</p>'
        except:
            logger.error('Unknown error')
            return f'<p>Unknown error</p>'

        if telegram_id and not telegram_id.isdecimal():
                logger.error('Wrong telegram ID')
                return f'<p>Wrong telegram ID</p>'
        if not email and not telegram_id:
            logger.error('Contacts not specified')
            return f'<p>Contacts (email or telegram ID) not specified</p>'
        
        if is_closed and not can_access_closed:
            logger.error('Account is closed, no access to information')
            return f'<p>Account is closed, no access to information</p>'

        if option_downloading_vk not in ['fast', 'slow']:
            logger.error('Wrong option')
            return f'<p>Wrong option</p>'
        if telegram_id:
            try:
                bot = telebot.TeleBot(telegram_token)
                bot.send_message(telegram_id, "Hi! We check your account.")
            except Exception as e:
                logger.error(f'Wrong telegram ID: {str(e)}')
                return f'<p>Wrong telegram ID: {str(e)}</p>'
            
        pdf_name = "generated_docs/" + user_name + ".pdf"

        process_creating_message = Process(
            target=create_and_send_message,
            args=(user_name, vk_id, email, telegram_id, pdf_name, option_downloading_vk),
            daemon=True
        )
        process_creating_message.start()
        
        return f'<p>Sent. Email: {email}. Telegram ID: {telegram_id}</p>'

    return render_template('vk_stat.html')
