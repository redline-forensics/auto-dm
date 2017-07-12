import ConfigParser


def build_prefs_file():
    pix4d = "Pix4D"
    add_section(pix4d)
    set(pix4d, "Email", "")
    set(pix4d, "Password", "")

    write()


def add_section(section):
    config.add_section(section)


def set(section, option, value):
    config.set(section, option, value)


def write():
    with open(prefs_file, "wb") as config_file:
        config.write(config_file)


prefs_file = "preferences.cfg"

config = ConfigParser.SafeConfigParser()
successful = config.read(prefs_file)
if not successful:
    build_prefs_file()

print(config)
