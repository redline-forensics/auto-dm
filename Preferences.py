import ConfigParser


def build_prefs_file():
    add_section(pix4d_section)
    set(pix4d_section, pix4d_email_pref)
    set(pix4d_section, pix4d_password_pref)


def add_section(section):
    config.add_section(section)
    write()


def set(section, option, value=None):
    if value is None:
        config.set(section, option, "")
    else:
        config.set(section, option, value)
    write()


def write():
    with open(prefs_file, "wb") as config_file:
        config.write(config_file)


prefs_file = "preferences.cfg"

pix4d_section = "Pix4D"
pix4d_email_pref = "Email"
pix4d_password_pref = "Password"

config = ConfigParser.SafeConfigParser()
successful = config.read(prefs_file)
if not successful:
    build_prefs_file()

print(config)
