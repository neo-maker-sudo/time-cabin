import os
import logging
from importlib import import_module


if not (setting_module := os.getenv("SETTING_MODULE")):
    logger = logging.getLogger("uvicorn.warn")
    logger.warn(
        f"Could not find setting_module in global environment: {setting_module}, setdefault: app.config.dev"
    )
    # https://stackoverflow.com/questions/27785375/testing-flask-oauthlib-locally-without-https
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    setting_module = os.environ.setdefault("SETTING_MODULE", "app.config.dev")


class ConfigSetting():
    def __init__(self, setting_module):
        self.SETTING_MODULE = setting_module
        self.use_module = None

    def __repr__(self) -> str:
        if self.use_module is None:
            return "<ConfigSetting [Unevaluated]>"

        return '<ConfigSetting "{}">'.format(self.SETTING_MODULE)

    def _setup(self):
        if self.use_module:
            return self.use_module

        try:
            module = import_module(self.SETTING_MODULE)

        except AttributeError as exc:
            raise ImportError(
                f"Config Module import error: value:{self.SETTING_MODULE!r}"
            ) from exc

        except Exception as e:
            raise e
         
        self.use_module = module

    def __getattr__(self, name):
        if not self.use_module:
            self._setup()

        val = getattr(self.use_module, name)

        self.__dict__[name] = val
        return val


setting = ConfigSetting(setting_module=setting_module)
