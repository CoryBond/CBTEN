from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as ec
import os
import smtplib
import pickle
import os.path
from email.mime.text import MIMEText


#Configurations


website = "http://www.theaterextras.com"
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
email = "example@gmail.com"
app_name = "CBTheaterExtrasNotifier"
source_email = app_name+"@no_reply.com"
google_stmp_server = "smtp.gmail.com:###"
password = "####"


#Globals
RED = '#ff0000'
OLDRED = '#CC3232'
GREEN = '#458B00'


#Classes


class Notification:

    default_color = '#000000'

    def __init__(self, show, arg_color=default_color):
        self.show = show
        self.name_color = arg_color
        self.description_color = arg_color
        self.location_color = arg_color
        self.times_color = arg_color


class Show:

    def __init__(self, name = '', description = '', location = '', times = ''):
        self.name = name
        self.description = description
        self.location = location
        self.times = times

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other): return not self.__eq__(other)

    def __str__(self): return 'Show: %s, %s, %s, %s' % (self.name, self.description, self.location, self.times)

    """Needed for the pickling library to understand how to pickle this object... in this case pickle entire dict"""

    def __getstate__(self): return self.__dict__

    def __setstate__(self, d): self.__dict__.update(d)


#Functions


def connection_established():
    #Requires that PhanotmJS is setup on PATH for your machine.
    #os.environ["webdriver.chrome.driver"] = phantom_driver_exe
    chrome_driver = webdriver.PhantomJS()
    ui.WebDriverWait(chrome_driver,10)
    chrome_driver.get(website)

    return chrome_driver


def get_web_content(connected_driver):
    WebDriverWait(connected_driver, 10).until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, '#Form1 > center > div.splash_login > div:nth-child(1) > a'))
    )

    connected_driver.find_element_by_css_selector('#Form1 > center > div.splash_login > div:nth-child(1) '
                                                  '> input:nth-child(2)').send_keys(email)
    connected_driver.find_element_by_css_selector('#Form1 > center > div.splash_login > div:nth-child(1) '
                                                  '> input:nth-child(3)').send_keys(password)
    connected_driver.find_element_by_css_selector('#Form1 > center > div.splash_login '
                                                  '> div:nth-child(1) > a').click()
    WebDriverWait(connected_driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, './/*[@id="td_Listings"]/table/tbody/tr'))
    )
    theaters = connected_driver.find_elements_by_xpath('.//*[@id="td_Listings"]/table/tbody/tr')

    new_show = True
    got_shows = {}
    for theater in theaters:
        #Every Two Entries in theater represent different data for the same show. For what we want, the first entry
        #gives the name of the event and the seond entry gives all the details (such as description and time)
        if new_show:
            #msg+=str(theater.text)+'\n'
            show = Show(theater.text)
            new_show = False
        else:
            #Here just save the whole columns\n
            t_details = theater.find_elements_by_xpath('./td')
            show.location = t_details[0].get_attribute('innerHTML')
            show.description = t_details[1].get_attribute('innerHTML')
            show.times = t_details[2].get_attribute('innerHTML')
            got_shows[show.name] = show
            #for t_detail in t_details:
            #    print(t_detail.get_attribute('HTML'))
            #msg+=str(theater.get_attribute('HTML'))+'\n'
            new_show = True
    return got_shows


def merge_pickle(got_shows):
    if not os.path.isfile('saved_shows.p'):
        file = open('saved_shows.p', 'wb')
        file.close()
    file = open('saved_shows.p', 'rb')
    try:
        saved_shows = pickle.load(file)
    except EOFError:
        saved_shows = {}
    file.close()
    shows_to_save = {}
    shows_to_notify = []
    for show_name, show in got_shows.items():
        if show_name in saved_shows:
            saved_show = saved_shows.get(show_name)
            if saved_show == show:
                #logic if show was previously saved and equal : NO UPDATE AND KEEP OLD SHOW DATA : NO NOTIFY
                shows_to_save[show_name] = show
                print("FOUND SAME: ", show)
                saved_shows.pop(show_name)
            elif saved_show != show:
                #logic if show was previously saved but not equal : UPDATE NEW SHOW DATE : NOTIFY AND COLOR SOME
                shows_to_save[show_name] = show
                show_to_notify = Notification(show)
                if show.location != saved_show.location:
                    show_to_notify.location_color = GREEN
                if show.description != saved_show.description:
                    show_to_notify.description_color = GREEN
                if show.times != saved_show.times:
                    show_to_notify.times_color = GREEN
                shows_to_notify.append(show_to_notify)
                print("UPDATED: ", show)
                saved_shows.pop(show_name)
        else:
            #logic if show retrieved from web doesn't exist in saved file : ADD NEW SHOW : NOTIFY AND COLOR GREEN
            shows_to_save[show_name] = show
            shows_to_notify.append(Notification(show, GREEN))
            print("NEW: ", show)

    for saved_show_name, saved_show in saved_shows.items():
        #Whatever saved shows are left must mean they were deleted : REMOVE OLD SHOWS : NOTIFY AND COLOR RED
        shows_to_notify.append(Notification(saved_show, RED))
        print("DELETING: ", saved_show)

    file = open('saved_shows.p', 'wb')
    pickle.dump(shows_to_save, file)
    file.close()
    shows_to_notify.sort(key=lambda x: x.show.name, reverse=True)
    return shows_to_notify


def notifications_to_html(notifications_to_html):
    background_color = ""
    itr = 0
    html_msg = """\
        <html>
          <head></head>
          <body>
          <table border="4" style="width:100%">"""
    for notification_to_html in notifications_to_html:
        if itr % 2 == 0: background_color = "#C86432"
        else: background_color = "#D2B48C"
        itr += 1
        inner_show = notification_to_html.show
        html_msg += """\
            <tr>
                <td width="20%" bgcolor=""" + background_color + """></td>
                <td style="font-weight:bold; font-size:20pt;" width="65%" bgcolor=""" + background_color + """>
                    <FONT COLOR=""" + notification_to_html.description_color + """>""" + inner_show.name + """</FONT>
                </td>
                <td width="15% "bgcolor=""" + background_color + """></td>
            </tr>
            <tr>
                <td width="20%" bgcolor=""" + background_color + """> <FONT COLOR=""" \
                    + notification_to_html.location_color + """>""" + inner_show.location + """</FONT>
                </td>
                <td width="65%" bgcolor=""" + background_color + """>
                    <FONT COLOR=""" \
                    + notification_to_html.description_color + """>""" + inner_show.description + """</FONT>
                </td>
                <td width="15%" bgcolor=""" + background_color + """>
                    <FONT COLOR=""" \
                    + notification_to_html.times_color + """>""" + inner_show.times + """</FONT>
                </td>
            </tr>
        """
    html_msg += """\
            <body>
        <html>"""

    #persist html file for debuging
    file = open('example.html', 'w')
    file.write(html_msg)
    file.close()

    return html_msg


def send_notification_msg_email(html):
    text = """<font size="6">TheaterExtras Has Recently Updated New or Existing Shows.<br> Check em out anytime,
        anywhere, even if your BROKE!</font>"""
    mail = MIMEText(text + html, 'html')
    mail['Subject'] = app_name
    mail['From'] = source_email
    mail['To'] = email

    server = smtplib.SMTP(google_stmp_server)
    server.ehlo()
    server.starttls()
    server.login(email,password)
    server.sendmail(source_email, email, mail.as_string())
    server.quit()

#Init/Entry_Point

driver = connection_established()
if driver is not None:
    print("Connected to theater extras.")
    shows = get_web_content(driver)
    driver.quit()
    notifications = merge_pickle(shows)
    #Don't Send Any Emails If There Is Nothing To Notify
    if len(notifications) != 0:
        notification_html = notifications_to_html(notifications)
        send_notification_msg_email(notification_html)
else:
    print("Could not connect to the internet.")



















"""command = "javascript:Login(document.forms[0].f1_email.value,document.forms[0].f1_password.value);
    try:
        data = urllib_parse.urlencode(values)
        data = data.encode('ascii')
        req = urllib.Request(website, data, headers)
        with urllib.urlopen(req,timeout=20) as response:
            html = response.read()
            js = spidermonkey.Runtime()
            print(html)
        return True
    except urllib.URLError as err: pass
    return a"""