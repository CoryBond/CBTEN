To connect to your gmails stmp server you may need to go to your google account and turn on "less secure apps" settting for your account.
You can do this at the link here: https://www.google.com/settings/security/lesssecureapps

This project uses a combination of PhantomJS and Selenium to execute javascript and browse the net. PhantomJS is a headless gui-less WebKit engine easily automated by Selenium.
PhantomJS provides many of the features of popular browsers but for a more programmatic and efficient environment.
Selenium is a browser automater, in that it mimicks commands to a browser/WebKit-engine for using such a program. Selenium supports PhantomJS as of 3/2/2016.
























OLD:
For this project you need to use pyv8 which uses v8 javascript engine in order to call on javascript functions.

Refere to this page here for more up to date instructions for setting up v8: https://developers.google.com/v8/build

Best way to checkout and build v8: git clone depot_tools from google. Depot_tools are a series of tools that are used by Chrome, including v8.
Use cmd (can't use cygwin for this because depot_tools python files are in dos and not unix... its dumb yes) to call command gclient and update all dependencies of depot_tools.
At this point you may need to use git checkout * to make sure the version of all your files are up to date. If they are not calling fetch v8 might not work.
Use command fetch v8 to get the latest instal of v8 then make it for your local machine. fetch v8 will do the intial checkout.

After v8 is checkedout then use cygwin to make the project. Make sure your cygwin has make installed.
Call make using the instructions here: https://github.com/v8/v8/wiki/Using%20Git
