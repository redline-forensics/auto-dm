# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'views/qt/settings_view.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_settings_view(object):
    def setupUi(self, settings_view):
        settings_view.setObjectName("settings_view")
        settings_view.resize(400, 443)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/icons8-Traffic Jam-80.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        settings_view.setWindowIcon(icon)
        self.settings_layout = QtWidgets.QVBoxLayout(settings_view)
        self.settings_layout.setObjectName("settings_layout")
        self.scroll_area = QtWidgets.QScrollArea(settings_view)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area_contents = QtWidgets.QWidget()
        self.scroll_area_contents.setGeometry(QtCore.QRect(0, 0, 382, 394))
        self.scroll_area_contents.setObjectName("scroll_area_contents")
        self.scroll_area_contents_layout = QtWidgets.QVBoxLayout(self.scroll_area_contents)
        self.scroll_area_contents_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area_contents_layout.setObjectName("scroll_area_contents_layout")
        self.basecamp_grp = QtWidgets.QGroupBox(self.scroll_area_contents)
        self.basecamp_grp.setObjectName("basecamp_grp")
        self.basecamp_layout = QtWidgets.QFormLayout(self.basecamp_grp)
        self.basecamp_layout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.basecamp_layout.setObjectName("basecamp_layout")
        self.basecamp_email_lbl = QtWidgets.QLabel(self.basecamp_grp)
        self.basecamp_email_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.basecamp_email_lbl.setObjectName("basecamp_email_lbl")
        self.basecamp_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.basecamp_email_lbl)
        self.basecamp_email_edit = QtWidgets.QLineEdit(self.basecamp_grp)
        self.basecamp_email_edit.setObjectName("basecamp_email_edit")
        self.basecamp_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.basecamp_email_edit)
        self.basecamp_password_lbl = QtWidgets.QLabel(self.basecamp_grp)
        self.basecamp_password_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.basecamp_password_lbl.setObjectName("basecamp_password_lbl")
        self.basecamp_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.basecamp_password_lbl)
        self.basecamp_password_edit = QtWidgets.QLineEdit(self.basecamp_grp)
        self.basecamp_password_edit.setObjectName("basecamp_password_edit")
        self.basecamp_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.basecamp_password_edit)
        self.scroll_area_contents_layout.addWidget(self.basecamp_grp)
        self.pix4d_grp = QtWidgets.QGroupBox(self.scroll_area_contents)
        self.pix4d_grp.setObjectName("pix4d_grp")
        self.pix4d_layout = QtWidgets.QFormLayout(self.pix4d_grp)
        self.pix4d_layout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.pix4d_layout.setObjectName("pix4d_layout")
        self.pix4d_email_lbl = QtWidgets.QLabel(self.pix4d_grp)
        self.pix4d_email_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.pix4d_email_lbl.setObjectName("pix4d_email_lbl")
        self.pix4d_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.pix4d_email_lbl)
        self.pix4d_email_edit = QtWidgets.QLineEdit(self.pix4d_grp)
        self.pix4d_email_edit.setObjectName("pix4d_email_edit")
        self.pix4d_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.pix4d_email_edit)
        self.pix4d_password_lbl = QtWidgets.QLabel(self.pix4d_grp)
        self.pix4d_password_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.pix4d_password_lbl.setObjectName("pix4d_password_lbl")
        self.pix4d_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.pix4d_password_lbl)
        self.pix4d_password_edit = QtWidgets.QLineEdit(self.pix4d_grp)
        self.pix4d_password_edit.setObjectName("pix4d_password_edit")
        self.pix4d_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.pix4d_password_edit)
        self.scroll_area_contents_layout.addWidget(self.pix4d_grp)
        self.scene_grp = QtWidgets.QGroupBox(self.scroll_area_contents)
        self.scene_grp.setObjectName("scene_grp")
        self.scene_layout = QtWidgets.QFormLayout(self.scene_grp)
        self.scene_layout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.scene_layout.setObjectName("scene_layout")
        self.scene_exe_path_lbl = QtWidgets.QLabel(self.scene_grp)
        self.scene_exe_path_lbl.setObjectName("scene_exe_path_lbl")
        self.scene_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.scene_exe_path_lbl)
        self.scene_exe_path_edit = QtWidgets.QLineEdit(self.scene_grp)
        self.scene_exe_path_edit.setObjectName("scene_exe_path_edit")
        self.scene_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.scene_exe_path_edit)
        self.scroll_area_contents_layout.addWidget(self.scene_grp)
        self.google_maps_grp = QtWidgets.QGroupBox(self.scroll_area_contents)
        self.google_maps_grp.setObjectName("google_maps_grp")
        self.google_maps_layout = QtWidgets.QFormLayout(self.google_maps_grp)
        self.google_maps_layout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.google_maps_layout.setObjectName("google_maps_layout")
        self.google_maps_js_api_key_lbl = QtWidgets.QLabel(self.google_maps_grp)
        self.google_maps_js_api_key_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.google_maps_js_api_key_lbl.setObjectName("google_maps_js_api_key_lbl")
        self.google_maps_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.google_maps_js_api_key_lbl)
        self.google_maps_js_api_key_edit = QtWidgets.QLineEdit(self.google_maps_grp)
        self.google_maps_js_api_key_edit.setObjectName("google_maps_js_api_key_edit")
        self.google_maps_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.google_maps_js_api_key_edit)
        self.google_maps_static_api_key_lbl = QtWidgets.QLabel(self.google_maps_grp)
        self.google_maps_static_api_key_lbl.setObjectName("google_maps_static_api_key_lbl")
        self.google_maps_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.google_maps_static_api_key_lbl)
        self.google_maps_static_api_key_edit = QtWidgets.QLineEdit(self.google_maps_grp)
        self.google_maps_static_api_key_edit.setObjectName("google_maps_static_api_key_edit")
        self.google_maps_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.google_maps_static_api_key_edit)
        self.scroll_area_contents_layout.addWidget(self.google_maps_grp)
        self.google_earth_grp = QtWidgets.QGroupBox(self.scroll_area_contents)
        self.google_earth_grp.setObjectName("google_earth_grp")
        self.formLayout = QtWidgets.QFormLayout(self.google_earth_grp)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.formLayout.setObjectName("formLayout")
        self.google_earth_exe_path_lbl = QtWidgets.QLabel(self.google_earth_grp)
        self.google_earth_exe_path_lbl.setObjectName("google_earth_exe_path_lbl")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.google_earth_exe_path_lbl)
        self.google_earth_exe_path_edit = QtWidgets.QLineEdit(self.google_earth_grp)
        self.google_earth_exe_path_edit.setObjectName("google_earth_exe_path_edit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.google_earth_exe_path_edit)
        self.scroll_area_contents_layout.addWidget(self.google_earth_grp)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.scroll_area_contents_layout.addItem(spacerItem)
        self.scroll_area.setWidget(self.scroll_area_contents)
        self.settings_layout.addWidget(self.scroll_area)
        self.controls_layout = QtWidgets.QHBoxLayout()
        self.controls_layout.setObjectName("controls_layout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.controls_layout.addItem(spacerItem1)
        self.ok_btn = QtWidgets.QPushButton(settings_view)
        self.ok_btn.setAutoDefault(False)
        self.ok_btn.setDefault(True)
        self.ok_btn.setObjectName("ok_btn")
        self.controls_layout.addWidget(self.ok_btn)
        self.cancel_btn = QtWidgets.QPushButton(settings_view)
        self.cancel_btn.setObjectName("cancel_btn")
        self.controls_layout.addWidget(self.cancel_btn)
        self.apply_btn = QtWidgets.QPushButton(settings_view)
        self.apply_btn.setObjectName("apply_btn")
        self.controls_layout.addWidget(self.apply_btn)
        self.settings_layout.addLayout(self.controls_layout)

        self.retranslateUi(settings_view)
        QtCore.QMetaObject.connectSlotsByName(settings_view)

    def retranslateUi(self, settings_view):
        _translate = QtCore.QCoreApplication.translate
        settings_view.setWindowTitle(_translate("settings_view", "Settings"))
        self.basecamp_grp.setTitle(_translate("settings_view", "Basecamp"))
        self.basecamp_email_lbl.setText(_translate("settings_view", "Email:"))
        self.basecamp_password_lbl.setText(_translate("settings_view", "Password:"))
        self.pix4d_grp.setTitle(_translate("settings_view", "Pix4D"))
        self.pix4d_email_lbl.setText(_translate("settings_view", "Email:"))
        self.pix4d_password_lbl.setText(_translate("settings_view", "Password:"))
        self.scene_grp.setTitle(_translate("settings_view", "SCENE"))
        self.scene_exe_path_lbl.setText(_translate("settings_view", "EXE Path:"))
        self.google_maps_grp.setTitle(_translate("settings_view", "Google Maps"))
        self.google_maps_js_api_key_lbl.setText(_translate("settings_view", "JS API Key:"))
        self.google_maps_static_api_key_lbl.setText(_translate("settings_view", "Static API Key:"))
        self.google_earth_grp.setTitle(_translate("settings_view", "Google Earth"))
        self.google_earth_exe_path_lbl.setText(_translate("settings_view", "EXE Path:"))
        self.ok_btn.setText(_translate("settings_view", "OK"))
        self.cancel_btn.setText(_translate("settings_view", "Cancel"))
        self.apply_btn.setText(_translate("settings_view", "Apply"))

import resources.resources_rc
