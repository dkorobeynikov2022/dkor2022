from blockchain_funclib import  send_money_by_queue
from main_config import connect_par

try:
    send_money_by_queue(connect_par)

except Exception as err:
    print(err)

