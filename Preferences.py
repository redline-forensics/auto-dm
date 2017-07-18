import ConfigParser


def _build_prefs_file():
    _add_section(_pix4d_section)
    _set(_pix4d_section, _pix4d_email_pref)
    _set(_pix4d_section, _pix4d_password_pref)

    _add_section(_basecamp_section)
    _set(_basecamp_section, _basecamp_email_pref)
    _set(_basecamp_section, _basecamp_password_pref)


def _add_section(section):
    _config.add_section(section)
    _write()


def _set(section, option, value=None):
    if value is None:
        _config.set(section, option, "")
    else:
        _config.set(section, option, value)
    _write()


def _write():
    with open(_prefs_file, "wb") as config_file:
        _config.write(config_file)


# region Convenience Methods
def get_pix4d_email():
    return _config.get(_pix4d_section, _pix4d_email_pref)


def set_pix4d_email(email):
    _set(_pix4d_section, _pix4d_email_pref, email)


def get_pix4d_password():
    return _config.get(_pix4d_section, _pix4d_password_pref)


def set_pix4d_password(password):
    _set(_pix4d_section, _pix4d_password_pref, password)


def get_basecamp_email():
    return _config.get(_basecamp_section, _basecamp_email_pref)


def set_basecamp_email(email):
    _set(_basecamp_section, _basecamp_email_pref, email)


def get_basecamp_password():
    return _config.get(_basecamp_section, _basecamp_password_pref)


def set_basecamp_password(password):
    _set(_basecamp_section, _basecamp_password_pref, password)


# endregion


_prefs_file = "preferences.cfg"

_pix4d_section = "Pix4D"
_pix4d_email_pref = "Email"
_pix4d_password_pref = "Password"

_basecamp_section = "Basecamp"
_basecamp_email_pref = "Email"
_basecamp_password_pref = "Password"

_config = ConfigParser.SafeConfigParser()
_successful = _config.read(_prefs_file)
if not _successful:
    _build_prefs_file()

print(_config)
