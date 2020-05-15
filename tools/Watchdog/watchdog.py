import yaml
import smtplib, ssl
import platform    # For getting the operating system name
import subprocess  # For executing a shell command


def main():
    # Initialization
    config = parse_config()

    # SMTP server
    smtp_server = config["smtp_server"]["servername"]
    port = config["smtp_server"]["port"]
    sender_email = config["smtp_server"]["sender_email"]
    password = config["smtp_server"]["password"]

    # Receivers and targets
    receiver_email_list = config["receivers"]
    target_server = config["target_server"]

    connection_err_list = []

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Ping each server
    for server in target_server:
        if not ping(server["ip"]):
            server_str = server["name"] + ':' + server["ip"]
            connection_err_list.append(server_str)
    
    # Send notification if any connection error occurs
    if connection_err_list:
        message = generate_message(connection_err_list)

        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender_email, password)
            for receiver_email in receiver_email_list:
                server.sendmail(sender_email, receiver_email, message)
    return


def parse_config() -> object:
    """
    Read configuration file
    """
    cfg = []
    try:
        with open('./config.yml', 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        return cfg
    except Exception as err:
        print(err)


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0


def generate_message(connection_err_list):
    if len(connection_err_list) == 1:
        be = "is"
        server = "Server: "
    else:
        be = "are"
        server = "Servers:"

    hoststr = ", ".join([str(host) for host in connection_err_list])

    message = """\
Subject: MonSTer Watchdog Notification

%s %s %s unreachable!

This message is sent from MonSTer watchdog.""" % (server, hoststr, be)

    return message

if __name__ == '__main__':
    main()