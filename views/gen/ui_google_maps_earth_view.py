# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/google_maps_earth_view.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_google_maps_earth_view(object):
    def setupUi(self, google_maps_earth_view):
        google_maps_earth_view.setObjectName("google_maps_earth_view")
        google_maps_earth_view.resize(657, 360)
        google_maps_earth_view.setWindowTitle("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/icons8-Traffic Jam-80.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        google_maps_earth_view.setWindowIcon(icon)
        self.google_maps_earth_layout = QtWidgets.QVBoxLayout(google_maps_earth_view)
        self.google_maps_earth_layout.setObjectName("google_maps_earth_layout")
        self.controls_layout = QtWidgets.QHBoxLayout()
        self.controls_layout.setObjectName("controls_layout")
        self.latitude_lbl = QtWidgets.QLabel(google_maps_earth_view)
        self.latitude_lbl.setObjectName("latitude_lbl")
        self.controls_layout.addWidget(self.latitude_lbl)
        self.latitude_edit = QtWidgets.QLineEdit(google_maps_earth_view)
        self.latitude_edit.setMinimumSize(QtCore.QSize(75, 0))
        self.latitude_edit.setObjectName("latitude_edit")
        self.controls_layout.addWidget(self.latitude_edit)
        self.longitude_lbl = QtWidgets.QLabel(google_maps_earth_view)
        self.longitude_lbl.setObjectName("longitude_lbl")
        self.controls_layout.addWidget(self.longitude_lbl)
        self.longitude_edit = QtWidgets.QLineEdit(google_maps_earth_view)
        self.longitude_edit.setMinimumSize(QtCore.QSize(75, 0))
        self.longitude_edit.setObjectName("longitude_edit")
        self.controls_layout.addWidget(self.longitude_edit)
        self.go_btn = QtWidgets.QPushButton(google_maps_earth_view)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/icons8-Map Pin-16.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.go_btn.setIcon(icon1)
        self.go_btn.setObjectName("go_btn")
        self.controls_layout.addWidget(self.go_btn)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.controls_layout.addItem(spacerItem)
        self.overlap_lbl = QtWidgets.QLabel(google_maps_earth_view)
        self.overlap_lbl.setObjectName("overlap_lbl")
        self.controls_layout.addWidget(self.overlap_lbl)
        self.overlap_spn = QtWidgets.QSpinBox(google_maps_earth_view)
        self.overlap_spn.setMinimum(0)
        self.overlap_spn.setProperty("value", 70)
        self.overlap_spn.setObjectName("overlap_spn")
        self.controls_layout.addWidget(self.overlap_spn)
        self.interval_lbl = QtWidgets.QLabel(google_maps_earth_view)
        self.interval_lbl.setObjectName("interval_lbl")
        self.controls_layout.addWidget(self.interval_lbl)
        self.interval_spn = QtWidgets.QDoubleSpinBox(google_maps_earth_view)
        self.interval_spn.setMinimum(1.0)
        self.interval_spn.setSingleStep(0.5)
        self.interval_spn.setObjectName("interval_spn")
        self.controls_layout.addWidget(self.interval_spn)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.controls_layout.addItem(spacerItem1)
        self.start_btn = QtWidgets.QPushButton(google_maps_earth_view)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/icons/icons8-Play-16.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.start_btn.setIcon(icon2)
        self.start_btn.setObjectName("start_btn")
        self.controls_layout.addWidget(self.start_btn)
        self.controls_layout.setStretch(1, 10)
        self.controls_layout.setStretch(3, 10)
        self.controls_layout.setStretch(5, 30)
        self.google_maps_earth_layout.addLayout(self.controls_layout)

        self.retranslateUi(google_maps_earth_view)
        QtCore.QMetaObject.connectSlotsByName(google_maps_earth_view)

    def retranslateUi(self, google_maps_earth_view):
        _translate = QtCore.QCoreApplication.translate
        self.latitude_lbl.setText(_translate("google_maps_earth_view", "Latitude:"))
        self.longitude_lbl.setText(_translate("google_maps_earth_view", "Longitude:"))
        self.go_btn.setText(_translate("google_maps_earth_view", "Go"))
        self.overlap_lbl.setText(_translate("google_maps_earth_view", "Overlap:"))
        self.overlap_spn.setSuffix(_translate("google_maps_earth_view", "%"))
        self.interval_lbl.setText(_translate("google_maps_earth_view", "Interval:"))
        self.interval_spn.setSuffix(_translate("google_maps_earth_view", " sec"))
        self.start_btn.setText(_translate("google_maps_earth_view", "Start"))

import resources.resources_rc
