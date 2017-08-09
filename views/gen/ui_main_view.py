# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/main_view.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_main_view(object):
    def setupUi(self, main_view):
        main_view.setObjectName("main_view")
        main_view.resize(621, 241)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/icons8-Traffic Jam-80.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        main_view.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(main_view)
        self.gridLayout.setObjectName("gridLayout")
        self.job_num_label = QtWidgets.QLabel(main_view)
        self.job_num_label.setObjectName("job_num_label")
        self.gridLayout.addWidget(self.job_num_label, 0, 0, 1, 1)
        self.job_num_edit = QtWidgets.QLineEdit(main_view)
        self.job_num_edit.setObjectName("job_num_edit")
        self.gridLayout.addWidget(self.job_num_edit, 0, 1, 1, 1)
        self.add_job_btn = QtWidgets.QPushButton(main_view)
        self.add_job_btn.setObjectName("add_job_btn")
        self.gridLayout.addWidget(self.add_job_btn, 0, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(219, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.settings_btn = QtWidgets.QPushButton(main_view)
        self.settings_btn.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/icons8-Settings-16.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.settings_btn.setIcon(icon1)
        self.settings_btn.setObjectName("settings_btn")
        self.gridLayout.addWidget(self.settings_btn, 0, 4, 1, 1)
        self.jobs_tab_widget = QtWidgets.QTabWidget(main_view)
        self.jobs_tab_widget.setTabsClosable(True)
        self.jobs_tab_widget.setMovable(True)
        self.jobs_tab_widget.setObjectName("jobs_tab_widget")
        self.gridLayout.addWidget(self.jobs_tab_widget, 1, 0, 1, 5)

        self.retranslateUi(main_view)
        self.jobs_tab_widget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(main_view)

    def retranslateUi(self, main_view):
        _translate = QtCore.QCoreApplication.translate
        main_view.setWindowTitle(_translate("main_view", "AutoDM"))
        self.job_num_label.setText(_translate("main_view", "Job #:"))
        self.add_job_btn.setText(_translate("main_view", "Add Job"))

import resources.resources_rc
