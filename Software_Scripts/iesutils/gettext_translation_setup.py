import iesve
import gettext


def setup_gettext_translation():
    lang, region = iesve.VEProject.get_current_project().get_language_code()

    if len(region) == 0:
        code = lang
    else:
        code = "_".join([lang, region])

    print(f"Language & locale code: {code}")
    tr = gettext.translation('messages', localedir='locale', languages=[code], fallback=True)
    # install assigns the translation object's gettext to _ and puts it in
    # builtins, this needs to be done before importing any other local
    # scripts to ensure it works
    tr.install()