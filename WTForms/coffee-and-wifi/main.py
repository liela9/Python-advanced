from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, URLField
from wtforms.validators import DataRequired, URL
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


class CafeForm(FlaskForm):
    cafe = StringField(label='Cafe name', validators=[DataRequired()])
    location = URLField(label='Cafe Location On Google Maps (URL)', validators=[DataRequired(), URL()])
    open_time = StringField(label='Opening Time e.g. 8AM', validators=[DataRequired()])
    closing_time = StringField(label='Closing Time e.g. 8PM', validators=[DataRequired()])
    coffee_rating = SelectField(choices=['✘', '☕️', '☕️☕️', '☕️☕️☕️', '☕️☕️☕️☕️', '☕️☕️☕️☕️☕️'], label='Coffe Rating', validators=[DataRequired()])
    wifi_rating = SelectField(choices=['✘', '💪', '💪💪', '💪💪💪', '💪💪💪💪', '💪💪💪💪💪'], label='Wifi Strength Rating', validators=[DataRequired()])
    power_socket_rating = SelectField(choices=['✘', '🔌', '🔌🔌', '🔌🔌🔌', '🔌🔌🔌🔌', '🔌🔌🔌🔌🔌'], label='Power Socket Availability', validators=[DataRequired()])
    submit = SubmitField(label='Submit')


# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")

@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        with open('coffee-and-wifi/cafe-data.csv', 'a', encoding="utf8") as csv_file:
            csv_file.write(f"\n{form.cafe.data},{form.location.data},{form.open_time.data},{form.closing_time.data},{form.coffee_rating.data},{form.wifi_rating.data},{form.power_socket_rating.data}")
    return render_template('add.html', form=form)

@app.route('/cafes')
def cafes():
    with open('coffee-and-wifi/cafe-data.csv', newline='', encoding="utf8") as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in csv_data:
            list_of_rows.append(row)
    return render_template('cafes.html', cafes=list_of_rows, num_of_rows=len(list_of_rows))

if __name__ == '__main__':
    app.run(debug=True)