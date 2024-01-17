
import getpass
import sys, os
import os.path
import pandas as pd
import datetime
# cpapi is a library that handles the communication with the Check Point management server.
from cpapi import APIClient, APIClientArgs



def remove(string): 
    return string.replace(" ", "").replace("\t", "").replace("\n", "")

def main():

    api_server = input("Enter ip mgmt checkpoint: ")
    username = input("Enter username: ")
    if username == '' or api_server =='':
        exit(1)

    if sys.stdin.isatty():
        password = getpass.getpass("Enter password: ")
    else:
        print("Attention! Your password will be shown on the screen!")
        password = input("Enter password: ")

    date = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    MY_PATH = os.path.abspath(os.path.dirname(__file__))
    INPUT_EXCEL = os.path.join(MY_PATH, 'input.xlsx')
    OUTPUT_FILE = "UserVPN_" + date + "_.csv"
    OUTPUT_EXCEL = os.path.join(MY_PATH, OUTPUT_FILE)
    INPUT = pd.read_excel(INPUT_EXCEL, sheet_name='Sheet1')
    count = INPUT['Name'].count()
    
    client_args = APIClientArgs(server=api_server)
    with APIClient(client_args) as client:

        # create debug file. The debug file will hold all the communication between the python script and
        # Check Point's management server.    

        # The API client, would look for the server's certificate SHA1 fingerprint in a file.
        # If the fingerprint is not found on the file, it will ask the user if he accepts the server's fingerprint.
        # In case the user does not accept the fingerprint, exit the program.
        if client.check_fingerprint() is False:
            print("Could not get the server's fingerprint - Check connectivity with the server.")
            input("Enter to exit [Enter]")
            exit(1)

        # login to server:
        login_res = client.login(username, password)

        if login_res.success is False:
            print("Login failed:\n{}".format(login_res.error_message))
            input("Enter to exit [Enter]")
            exit(1)
        print("Connected to Server ",api_server)
        #show_user_res = client.api_call("show-users")
        #print(show_user_res)
        user_list = []
        for x in range(0, count):
            user_dict = {}
            name = str(INPUT["Name"][x]).strip()
            show_user_res = client.api_call("show-user",{"name" : name})
            if show_user_res.status_code == 200:
                user_dict['name'] = name
                
                try:
                    user_dict['phone-number'] = show_user_res.data['phone-number']
                except KeyError:
                    user_dict['phone-number'] = ""
                
                try:
                    user_dict['email'] = show_user_res.data['email']
                except KeyError:
                    user_dict['email'] = ""

                user_list.append(user_dict)
        
        #print(user_list)
        file = open(OUTPUT_EXCEL, 'a', encoding='utf-8') 
        file.write('name,phone-number,email\n')
        for user in user_list:
            file.write(str(user["name"]) + ','+ str(user["phone-number"]) +','+str(user["email"])+'\n')
        file.close()
        print('Success! You can find your file  in the subfolder '+OUTPUT_EXCEL+'!')

    # test gitpush
if __name__ == "__main__":
    # This script doesn't take command line arguments.  If any are passed in,
    # then print out the script's docstring and exit.
    if len(sys.argv) != 1:
        print(__doc__)
    else:
        # No CLI args, so run the main function.
        main()