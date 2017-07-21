import json
import urllib2

from prefs import preferences


def get_basecamp_page(job_num):
    name = "J{:d}".format(job_num)
    email = preferences.get_basecamp_email()
    password = preferences.get_basecamp_password()

    print(email)
    print(password)

    mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    mgr.add_password(None, "https://basecamp.com/2103842", email, password)
    opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler(mgr),
                         urllib2.HTTPDigestAuthHandler(mgr))
    urllib2.install_opener(opener)
    jobs = json.load(urllib2.urlopen("https://basecamp.com/2103842/api/v1/projects.json"))

    for job in jobs:
        if name in job["name"]:
            return job["app_url"]


if __name__ == "__main__":
    print(get_basecamp_page(4086))
