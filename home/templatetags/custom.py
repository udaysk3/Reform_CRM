from django import template
import ast
import os
import pandas as pd
from datetime import datetime
register = template.Library()


@register.filter(name="index")
def index(sequence, position):
    try:
        return sequence[position]
    except IndexError:
        return None

@register.filter(name='split')
def split(value, arg):
    return value.split(arg)


@register.filter(name='firstsplitconvert')
def firstsplitconvert(value, arg):
    return ast.literal_eval(value.split(arg, 1)[1])


@register.filter(name='firstsplit')
def firstsplit(value, arg):
    return value.split(arg, 1)


@register.filter(name='date')
def date(value):
    return value.strftime("%Y-%m-%d" )

@register.filter(name='cities')
def cities(value):
    csv_filename = os.path.join(os.path.dirname(__file__), '../cities.csv')
    data = pd.read_csv(csv_filename)
    return data['City/Town/Village'].tolist()

@register.filter(name='countries')
def countries(value):
    return [

'England',

'Scotland',

'Wales',

'Northern Ireland'
]

@register.filter(name='countys')
def countys(value):
    return [
  "Aberdeenshire",
  "Anglesey",
  "Angus (Forfarshire)",
  "Antrim",
  "Argyllshire",
  "Armagh",
  "Ayrshire",
  "Banffshire",
  "Bedfordshire",
  "Berkshire",
  "Berwickshire",
  "Breconshire",
  "Buckinghamshire",
  "Buteshire",
  "Caernarvonshire",
  "Caithness",
  "Cambridgeshire",
  "Cardiganshire",
  "Carmarthenshire",
  "Cheshire",
  "Clackmannanshire",
  "Cornwall",
  "Cumberland",
  "Denbighshire",
  "Derbyshire",
  "Devon",
  "Dorset",
  "Down",
  "Dumfriesshire",
  "Dunbartonshire",
  "Durham",
  "East Lothian",
  "East Riding of Yorkshire",
  "East Sussex",
  "Essex",
  "Fermanagh",
  "Fife",
  "Flintshire",
  "Glamorgan",
  "Gloucestershire",
  "Greater London",
  "Greater Manchester",
  "Hampshire",
  "Herefordshire",
  "Hertfordshire",
  "Huntingdonshire",
  "Inverness-shire",
  "Isle of Wight",
  "Kent",
  "Kincardineshire",
  "Kinross-shire",
  "Kirkcudbrightshire",
  "Lanarkshire",
  "Lancashire",
  "Leicestershire",
  "Lincolnshire",
  "Londonderry",
  "Merionethshire",
  "Merseyside",
  "Midlothian",
  "Monmouthshire",
  "Montgomeryshire",
  "Morayshire",
  "Nairnshire",
  "Norfolk",
  "Northamptonshire",
  "Northumberland",
  "Nottinghamshire",
  "Orkney",
  "Oxfordshire",
  "Peeblesshire",
  "Pembrokeshire",
  "Perthshire",
  "Radnorshire",
  "Renfrewshire",
  "Ross & Cromarty",
  "Roxburghshire",
  "Rutland",
  "Selkirkshire",
  "Shetland",
  "Shropshire",
  "Somerset",
  "Staffordshire",
  "Stirlingshire",
  "Suffolk",
  "Surrey",
  "Sutherland",
  "Tyne & Wear",
  "Tyrone",
  "Warwickshire",
  "West Lothian",
  "West Midlands",
  "West Riding of Yorkshire",
  "West Sussex",
  "Westmorland",
  "Wigtownshire",
  "Wiltshire",
  "Worcestershire",
  "Yorkshire"
]
