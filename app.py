import json

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
db = SQLAlchemy(app)


class ServiceFee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(3))
    amount = db.Column(db.Integer)
    events = db.relationship("Event", back_populates="service_fee")
    products = db.relationship("Product", back_populates="service_fee")


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    products = db.relationship("Product", back_populates="event")
    service_fee = db.relationship("ServiceFee", back_populates="events")
    service_fee_id = db.Column(db.Integer, db.ForeignKey("service_fee.id"))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    event = db.relationship("Event", back_populates="products")
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    service_fee = db.relationship("ServiceFee", back_populates="products")
    service_fee_id = db.Column(db.Integer, db.ForeignKey("service_fee.id"))


def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


# this is for pretty printing the database results
def print_as_json(obj):
    if obj is None:
        return print("<None>")
    if(type(obj) is list):
        class_name = type(obj[0]).__name__ + "[]"
        s = json.dumps(list(map(lambda o: to_dict(o), obj)), indent=2)
    else:
        class_name = type(obj).__name__
        s = json.dumps(to_dict(obj), indent=2)

    print(class_name, s, "\n")


def format_currency(n):
    return f'{(n / 100): .2f}'


# test data
db.drop_all()
db.create_all()
service_fee_100 = ServiceFee(currency="EUR", amount=100)
service_fee_150 = ServiceFee(currency="EUR", amount=150)
service_fee_200 = ServiceFee(currency="EUR", amount=200)
event_rage_against_the_machine = Event(name='Rage Against The Machine', service_fee=service_fee_150)
event_red_hot_chili = Event(name='Red Hot Chili Peppers', service_fee=service_fee_150)
event_nirvana = Event(name='Nirvana', service_fee=service_fee_150)
product_early_bird = Product(name='Early Bird', service_fee=service_fee_100, event=event_rage_against_the_machine)
product_regular = Product(name='Regular', service_fee=None, event=event_nirvana)
product_children = Product(name='Children', service_fee=service_fee_200, event=event_red_hot_chili)
product_old_people = Product(name='Senior', service_fee=service_fee_200, event=event_red_hot_chili)
db.session.add_all([service_fee_100, service_fee_150, service_fee_200, event_rage_against_the_machine, event_red_hot_chili, event_nirvana, product_early_bird, product_regular, product_children, product_old_people])
db.session.commit()

print("\n################## TEST DATA ###################\n")
print_as_json(Product.query.all())
print_as_json(Event.query.all())
print_as_json(ServiceFee.query.all())
print("################################################")


@app.route("/events")
def events():
    events = Event.query.all()
    return {
        "events": list(map(lambda o: {
            "name": o.name,
            "id": o.id
        }, events))
    }


@app.route("/products/<event_id>")
def products(event_id):
    products = Product.query.filter_by(event_id=event_id)

    return {
        "products": list(map(lambda o: {
            "name": o.name,
            "id": o.id
        }, products))
    }


@app.route("/total_service_fee/<event_id>")
def total_service_fee(event_id):
    event = Event.query.get(event_id)
    products = request.json["products"]
    event_service_fee = ServiceFee.query.get(event.service_fee_id)

    total_amount = 0
    product_fees_table = f"\n\n--- Tickets for '{event.name}' ---\n"

    for data in products:
        quantity = data["quantity"]
        product_id = data["id"]
        product = Product.query.get(product_id)
        product_name = product.name

        if(product.service_fee_id):
            product_service_fee = ServiceFee.query.get(product.service_fee_id)
            selected_fee = product_service_fee
            fee_type = "product"
        else:
            selected_fee = event_service_fee
            fee_type = "event"

        fee_per_product = format_currency(selected_fee.amount)
        fee_for_all = format_currency(selected_fee.amount * quantity)
        product_fees_table += f'\n{quantity}x {fee_per_product} {selected_fee.currency} {product_name} ({fee_type} fee)\n = {fee_for_all} {selected_fee.currency}'

        total_amount += selected_fee.amount * quantity

    product_fees_table += f"\n\nTOTAL: {format_currency(total_amount)} {event_service_fee.currency}\n----------------------------------------------\n"
    print(product_fees_table)

    # i won't check here if all service fees have the same currency
    return f'{product_fees_table}\nYou have to pay a service fee of {format_currency(total_amount)} {event_service_fee.currency}'
