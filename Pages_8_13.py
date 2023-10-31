import sys
sys.path.append('C:/Users/sarah/Desktop/git_folder/DataScienceProject/transkribus')
from transkribus_1 import Transkribus_API

new_client = Transkribus_API()
session_id = new_client.login("a12110417@unet.univie.ac.at", "=b@gMi4}:9;P?b'")

colId = 240344
docId = 1620944

##############################

