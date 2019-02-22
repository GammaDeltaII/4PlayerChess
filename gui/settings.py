from PyQt5.QtCore import QSettings

COM = '4pc'
APP = '4PlayerChess'


class Settings(QSettings):
    def __init__(self):
        super(Settings, self).__init__(COM, APP)

    def checkSetting(self, param, default=False):
        v = self.value(param, default)
        if v in [False, True]:
            return v
        if v == 'false':
            return False
        elif v == 'true':
            return True
        else:
            return v
