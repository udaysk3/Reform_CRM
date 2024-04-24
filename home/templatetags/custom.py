from django import template
from datetime import datetime
register = template.Library()

@register.filter(name='split')
def split(value, arg):
    print(arg, value)
    return value.split(arg)

@register.filter(name='date')
def date(value):
    return value.strftime("%Y-%m-%d" )

@register.filter(name='cities')
def cities(value):
    return [
  "Aberdeen",
  "Armagh",
  "Bangor",
  "Bangor",
  "Bath",
  "Belfast",
  "Birmingham",
  "Bradford",
  "Brighton & Hove",
  "Bristol",
  "Cambridge",
  "Canterbury",
  "Cardiff",
  "Carlisle",
  "Chelmsford",
  "Chester",
  "Chichester",
  "City of Gibraltar",
  "Colchester",
  "Coventry",
  "Derby",
  "Doncaster",
  "Douglas",
  "Dundee",
  "Dunfermline",
  "Durham",
  "Ely",
  "Edinburgh",
  "Exeter",
  "Glasgow",
  "Gloucester",
  "Hamilton",
  "Hereford",
  "Inverness",
  "Jamestown",
  "Kingston-upon-Hull",
  "Lancaster",
  "Leeds",
  "Leicester",
  "Lichfield",
  "Lincoln",
  "Lisburn",
  "Londonderry",
  "London",
  "Manchester",
  "Milton Keynes",
  "Newcastle-upon-Tyne",
  "Newport",
  "Newry",
  "Norwich",
  "Nottingham",
  "Oxford",
  "Perth",
  "Peterborough",
  "Plymouth",
  "Portsmouth",
  "Preston",
  "Ripon",
  "Salford",
  "Salisbury",
  "Sheffield",
  "Southampton",
  "Southend-on-Sea",
  "St Albans",
  "St Asaph",
  "St Davids",
  "Stanley",
  "Stirling",
  "Stoke on Trent",
  "Sunderland",
  "Swansea",
  "Truro",
  "Wakefield",
  "Wells",
  "Westminster",
  "Wolverhampton",
  "Worcester",
  "Wrexham",
  "York"
]

