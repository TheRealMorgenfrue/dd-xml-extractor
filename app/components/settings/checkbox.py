from qfluentwidgets import CheckBox
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtBoundSignal

from typing import Any, Optional

from app.common.signal_bus import signalBus
from app.components.settings.base_setting import BaseSetting

from module.tools.types.config import AnyConfig


class CheckBox_(BaseSetting):
    def __init__(self, config: AnyConfig, configkey: str, configname: str,
                 ui_disable: Optional[bool]=None, parent: Optional[QWidget]=None) -> None:
        """Check box widget connected to a config key.

        Parameters
        ----------
        config : AnyConfig
            Config from which to get values used for this setting.

        configkey : str
            The option key in the config which should be associated with this setting.

        configname : str
            The name of the config.

        ui_disable: bool, optional
            The value which disables this setting.

        parent : QWidget, optional
            Parent of this class, by default None.
        """
        try:
            super().__init__(
                config=config,
                configkey=configkey,
                configname=configname,
                parent=parent
            )
            self.checkbox = CheckBox()
            self.currentValue = self.__convertBool(self.config.getValue(self.configkey, self.configname))
            self.defaultValue = self.__convertBool(self.config.getValue(self.configkey, self.configname, use_internal_config=True))
            self.disableValue = self.__convertBool(ui_disable) if ui_disable is not None else None
            self.backupValue = self.currentValue
            self.isDisabled = False
            self.notifyDisabled = True

            # Set disabled status
            if self.currentValue == ui_disable:
                self.__setDisableWidget(isDisabled=True, saveValue=False)

            # Set value of switch
            self.checkbox.setChecked(self.currentValue)

            # Add Switch to layout
            self.buttonlayout.addWidget(self.checkbox)

            self.__connectSignalToSlot()
            signalBus.configUpdated.emit(self.configkey, (self.currentValue,))
        except Exception:
            self.deleteLater()
            raise

    def __connectSignalToSlot(self) -> None:
        self.checkbox.stateChanged.connect(self.setValue)
        self.notifySetting.connect(self.__onParentNotification)
        signalBus.updateConfigSettings.connect(self.__onUpdateConfigSettings)

    def __onUpdateConfigSettings(self, configkey: str, value: tuple[Any,]) -> None:
        if self.configkey == configkey:
            self.setValue(value[0])

    def __onParentNotification(self, values: tuple) -> None:
        type = values[0]
        value = values[1]
        if type == "disable":
            self.notifyDisabled = False
            self.__setDisableWidget(value[0], value[1])
            self.notifyDisabled = True
        elif type == "canGetDisabled":
            self.notifyParent.emit(("canGetDisabled", self._canGetDisabled()))

    def __convertBool(self, value: str | bool, reverse: bool=False) -> bool | str:
        value = self.__parseBool(value)
        if reverse:
            if value:
                value = "y"     # This is a hack designed only for 1 usecase. TODO: Fix this
            else:
                value = "n"
        return value

    def __parseBool(self, value: str | bool) -> bool:
        if isinstance(value, bool):
            return value
        truthy = ["y", "true"]
        if value in truthy:
            return True
        return False

    def __setDisableWidget(self, isDisabled: bool, saveValue: bool) -> None:
        if self.isDisabled != isDisabled:
            self.isDisabled = isDisabled
            self.checkbox.setDisabled(self.isDisabled)

            if self.isDisabled:
                self.backupValue = self.currentValue
                value = self.disableValue
            else:
                value = not self.disableValue if self._canGetDisabled() else self.backupValue
            if self.disableValue is not None and saveValue:
                self.setValue(value)

    def _canGetDisabled(self) -> bool:
        if self.disableValue is not None:
            return True
        return False

    def getSwitchpyqtSignal(self) -> pyqtBoundSignal:
        """ Used for all value synchronizations """
        return self.checkbox.stateChanged

    def setValue(self, value: bool) -> None:
        if self.configkey == "defaultSketchOption":
            value = self.__convertBool(value, reverse=True)

        if self.currentValue != value or self.backupValue == value:
            if self.config.setValue(self.configkey, value, self.configname):
                self.currentValue = value
                self.checkbox.setChecked(value)
                if self._canGetDisabled() and self.disableValue == value and self.notifyDisabled:
                    self.notifyParent.emit(("disable", value))

    def resetValue(self) -> None:
        self.setValue(self.defaultValue)

    def setValueSync(self, value: bool) -> None:
        """ Used for synchronized parent/child widgets (see "sync_children" in template_docs.txt) """
        self.setValue(value)

    def setValueDesync(self, value: bool) -> None:
        """ Used for desynchonized parent/child widgets (see "desync_children" in template_docs.txt) """
        self.setValue(not value)

    def setValueDesyncTrue(self, value: bool) -> None:
        """ Used for desynchonized parent/child widgets (see "desync_true_children" in template_docs.txt) """
        if value:
            self.setValue(value)