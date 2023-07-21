import os

from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, EmailField, MultipleFileField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, InputRequired

from zammad_py import ZammadAPI
from dotenv import load_dotenv
load_dotenv()
client = ZammadAPI(url=os.getenv('ZAMMAD_URL'), username=os.getenv('ZAMMAD_USER'), password=os.getenv('ZAMMAD_PASSWORD'))

app = Flask(__name__)
app.secret_key = os.getenv('APP_KEY')

# Bootstrap-Flask requires this line
bootstrap = Bootstrap(app)
# Flask-WTF requires this line
csrf = CSRFProtect(app)


class HelpForm(FlaskForm):
    name = StringField('Как Вас зовут?', validators=[DataRequired()])
    email = EmailField('Ваша электронная почта?', validators=[DataRequired(), Email()])
    subject = StringField('Тема обращения', validators=[DataRequired()])
    category = RadioField('Какая помощь Вам нужна?', validators=[InputRequired(message=None)],
                          choices=[('Legal', 'Юридическая'),
                                   ('Psychological', 'Психологическая'),
                                   ('Funding', 'Финансовая')])
    text = TextAreaField('Текст обращения')
    attachment = MultipleFileField('Файлы')
    submit = SubmitField('Отправить')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = HelpForm()
    if form.validate_on_submit():
        params = {
            "title": form.subject.data,
            "group": "test",
            "customer_id": "guess:" + form.email.data,
            "abc": form.category.data
        }
        newticket = client.ticket.create(params=params)
        newuser_id = newticket['customer_id']
        client.user.update(id=newuser_id, params={'firstname': form.name.data})
        client.ticket.update(id=newticket['id'], params={
            "article": {
                "from": form.email.data,
                "body": form.text.data,
                "type": "note",
                "internal": False
            }
        })
        # sl_file_obj = open(d['attachment'], "rb").read()
        # message_files = {'attachment': sl_file_obj}
        # response = requests.request("PUT", ticket_url, headers=zammad_headers, json=update_params, files=message_files)
    return render_template('index.html', form=form)
