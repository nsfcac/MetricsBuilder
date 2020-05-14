import smtplib, ssl
import platform    # For getting the operating system name
import subprocess  # For executing a shell command

smtp_server = "smtp.gmail.com"
port = 587
password = "watchmonster"
sender_email = "watchdog4monster@gmail.com"

receiver_email_list = ["jie.li@ttu.edu", "username0416@gmail.com"]
hostlist = [{"ip": "10.10.1.3", "server": "Influx"}, {"ip": "10.10.1.4", "server": "Nagios"}]

connection_err_list = []

# Create a secure SSL context
context = ssl.create_default_context()


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '3', host]

    return subprocess.call(command) == 0


for service in hostlist:
    if not ping(service["ip"]):
        connection_err_list.append(service["server"])

if connection_err_list:
    if len(connection_err_list) == 1:
        be = "is"
    else:
        be = "are"

    hoststr = ", ".join([str(host) for host in connection_err_list])

    message = """\
Subject: MonSTer Watchdog Notification
            
Server %s %s unreachable!

This message is sent from MonSTer watchdog.""" % (hoststr, be)

    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        for receiver_email in receiver_email_list:
            server.sendmail(sender_email, receiver_email, message)
