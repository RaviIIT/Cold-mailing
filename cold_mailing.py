# -*- coding: utf-8 -*-
"""Cold Mailing.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Dlib_Sj_yWZM-BhHRXGk2jrklOiWtRR7
"""

# Install the required libraries (if not already installed)
!pip install gspread google-auth

# Import libraries
import gspread
from google.colab import auth
from oauth2client.client import GoogleCredentials
from google.auth import default
import threading # for multiple proccess
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Authenticate and create a client
auth.authenticate_user()
creds, _ = default()
gc = gspread.authorize(creds)

#  Open the Google Sheets file (replace 'Email Id' with your actual file name)
spreadsheet = gc.open("Email Id")

# Select the worksheet you want to work with (replace 'Sheet1' with your actual sheet name)
worksheet = spreadsheet.sheet1

# mail function to send invitation mail to friends with client_file code
def send_invitation_mail(fromaddr, frompasswd, toaddr, msg_subject, msg_body, file_path):
    # try block for error handling
    try:
        msg = MIMEMultipart()
        print("[+] Message Object Created")
    except:
        print("[-] Error in Creating Message Object")
        return

    msg['From'] = fromaddr

    msg['To'] = toaddr

    msg['Subject'] = msg_subject

    body = msg_body

    msg.attach(MIMEText(body, 'plain'))

    filename = file_path
    attachment = open(filename, "rb")

    p = MIMEBase('application', 'octet-stream')

    p.set_payload((attachment).read())

    encoders.encode_base64(p)
    custom_filename = 'Ravi Kumar_SDE_Resume.pdf'
    p.add_header('Content-Disposition', f'attachment; filename={custom_filename}')

    # try block for error handling
    try:
        msg.attach(p)
        print("[+] File Attached")
    except:
        print("[-] Error in Attaching file")
        return

    # try block for error handling
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        # s = smtplib.SMTP('stud.iitp.ac.in', 587)
        print("[+] SMTP Session Created")
    except:
        print("[-] Error in creating SMTP session")
        return

    s.starttls()
    print(toaddr)
    # try block for error handling
    try:
        s.login(fromaddr, frompasswd)
        print("[+] Login Successful")
    except:
        print("[-] Login Failed")

    text = msg.as_string()

    # try block for error handling
    try:
        s.sendmail(fromaddr, toaddr, text)
        print("[+] Mail Sent successfully")
    except:
        print('[-] Mail not sent')

    s.quit()



row_number_start = 2
row_number_end = 14
row_number = row_number_start

date_cells = []

# Iterate over specified rows
while(row_number <= row_number_end):
    employee_data = []
    # Fetch data from the worksheet
    row_data = worksheet.row_values(row_number)

    if len(row_data) < 3:
        row_number = row_number+2
        continue  # Skip rows where there's not enough data

    domain_name = row_data[1]  # 2nd column is domain name
    employee_names = row_data[2:]  # From 3rd column onwards are employee names

    # Filter out empty employee names
    valid_employee_names = [name for name in employee_names if name.strip()]
    print(valid_employee_names)
    # Filter out empty employee names and update date cells
    for col_index, name in enumerate(employee_names):
        if name.strip():  # Check if name is not empty
            # Store the cell reference for the row just below the name
            date_cells.append(worksheet.cell(row_number+1, col_index + 3).address)  # +3 for the 3rd column onward

    # Append data to list
    employee_data.append({
        'domain_name': domain_name,
        'employee_names': valid_employee_names
    })
    row_number = row_number+2

    fromaddr = 'ravikumar.work.new@gmail.com'
    frompasswd = 'gwvbljjajzorhlgu'
    msg_subject = 'Invitation'
    msg_body = 'You are invited!'
    file_path = '/content/sample_data/Ravi Kumar-Resume.pdf'

    print(employee_data)
    for data in employee_data:
        domain_name = data['domain_name']
        for full_name in data['employee_names']:
            name_parts = full_name.split()
            if len(name_parts) == 1:
                email = f"{name_parts[0]}.{domain_name}"
            elif len(name_parts) > 1:
                email = f"{name_parts[0]}.{name_parts[1]}.{domain_name}"
            send_invitation_mail(fromaddr, frompasswd, email, msg_subject, msg_body, file_path)

# Write the current date and time below each name in the collected cells
current_datetime = datetime.now().strftime("%d-%m-%y")
for cell in date_cells:
    worksheet.update_acell(cell, current_datetime)