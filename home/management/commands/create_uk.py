from django.core.management.base import BaseCommand
from home.models import Councils
from user.models import User

class Command(BaseCommand):
    help = "Create postcode only once"

    def handle(self, *args, **options):
        try:

            admin_user = User.objects.get(email="admin@gmail.com")
            Councils.objects.create(
                name="UK",
                postcodes="""
                                    WR5,WD24,WF17,WA11,UB8,TS3,TR14,TN15,TN31,TA24,SW19,ST6,ST16,SR3,SO53,SM6,SO21,SN4,SE9,SE18,SA3,SA7,S9,RM1,RH12,S10,RG42,RG2,PO7,PO21,PO1,PL20,PE30,PE16,OX3,OX12,OL15,NW5,NR21,NR6,NP7,NN17,NG7,NG23,NE61,NE33,N21,MK9,MK17,ME19,M8,M33,M21,LS27,LS13,LL32,LL12,LE3,LA18,L37,L18,KY13,KT22,KA7,IV52,IP16,IP33,IG11,HU6,HR6,HP21,HA7,GU21,GU52,GL6,GL2,G78,G63,G32,FY4,FK1,EX31,EX10,EH7,EH36,E2,EH11,DY8,DT9,DN41,DN2,DL5,DH9,DG7,DE1,DA7,CW6,CV47,CV2,CT20,CR5,CO4,CM7,CM15,CH61,CH2,CF46,CB22,CA16,BS48,BS23,BR8,BN41,BN16,BL6,AB10,AB41,BH6,BH12,BD21,BB8,BA9,BA13,B63,B32,AB15,BT27,BT30,BT38,BT70,TN25,LE10,OL16,SN7,KY11,EX17,JE4,CT6,BB7,DN6,CT4,TW9,CT7,B50
                                    """,
            )

            self.stdout.write(self.style.SUCCESS("Completed processing"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Unexpected error: {e}"))
