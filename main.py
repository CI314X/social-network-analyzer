from flask import Flask, render_template, request, jsonify, abort, redirect, Response
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_mail import Mail, Message
from config import ADMINS, access_token
import random
# from flask import copy_current_request_context
from multiprocessing import Process
from generate_pdf import generate_vk_pdf
from delete_file import delete_file
from email_validator import validate_email, EmailNotValidError

from vk_graph import resolve_url_to_id
import vk_api

app = Flask(__name__)
app.config.from_object('config')


mail = Mail(app)


class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])

class MainForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    link = StringField('link', validators=[DataRequired()])


def create_and_send_message(user_name: str, id_link: int, email: str, pdf_name: str) -> None:

    generate_vk_pdf(pdf_name, id_link, user_name)

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
        try:
            valid = validate_email(email)
            email = valid.email
            vk = vk_api.VkApi(token=random.choice(access_token))
            vk_id, is_closed = resolve_url_to_id(vk, id_link)
        except EmailNotValidError as e:
            return f'<p>Wrong email. {str(e)}</p>'
        except vk_api.vk_api.ApiError as e:
            return f'<p>Wrong link for vk profile. {str(e)}</p>'
        except:
            return f'<p>Unknown error</p>'

        if is_closed:
            return f'<p>Account is closed, no access to information</p>'

        if option_downloading_vk not in ['fast', 'slow']:
            return f'<p>Wrong option</p>'

        pdf_name = "generated_docs/" + user_name + ".pdf"

        process_creating_message = Process(
            target=create_and_send_message,
            args=(user_name, vk_id, email, pdf_name),
            daemon=True
        )
        # process_creating_message.start()
        
        return f'<p>Sent to {email}</p>'

    return render_template('main_form_2.html')



@app.route('/main_form', methods=['GET', 'POST'])
def main_form():
    form = MainForm()
    if form.validate_on_submit():

        msg = Message('Sending file', sender = ADMINS[0], recipients = [form.email.data])
        msg.body = f'Sending pdf to {form.email.data}'
        with app.open_resource("generated_docs/hello.pdf") as fp:
            msg.attach(filename="hello.pdf", disposition="attachment", content_type="application/pdf", data=fp.read())
        
        with app.app_context():
            mail.send(msg)
        # form.email.data
        # form.link.data
        delete_file("generated_docs/hello.pdf")
        return '<p>Submitted</p>'

    return render_template('main_form.html', form=form)



# форма с одним полем
@app.route('/submit', methods=['GET', 'POST'])
def submit(): 
    form = MyForm()
    
    if form.validate_on_submit():
        print(form.name.data)
        return '<img src="/static/asd.jpg" alt="micropenis">'
        #return redirect('/hello/oleg')
    return render_template('submit.html', form=form)

@app.route("/")
def hello_world():
    return "<p>Hello, root</p>"



@app.route('/badrequest400')
def bad_request():
    """ error """
    return abort(400)

# try:
# except:
# return redirect(url_for('bad_request'))
# you can add to all



#if __name__ == '__main__':
#    app.run()