"""
Dwarf - Copyright (C) 2019 Giovanni Rocca (iGio90)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
"""
import json
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt5.QtWidgets import QHeaderView, QTabWidget, QMenu

from lib import utils
from ui.list_view import DwarfListView


class ContextPanel(QTabWidget):
    # consts
    CONTEXT_TYPE_NATIVE = 0
    CONTEXT_TYPE_JAVA = 1
    CONTEXT_TYPE_EMULATOR = 2

    onShowMemoryRequest = pyqtSignal(str, name='onShowMemoryRequest')

    def __init__(self, parent=None):
        super(ContextPanel, self).__init__(parent=parent)

        self._app_window = parent
        self.setAutoFillBackground(True)

        self._nativectx_model = QStandardItemModel(0, 4)
        self._nativectx_model.setHeaderData(0, Qt.Horizontal, 'Reg')
        self._nativectx_model.setHeaderData(0, Qt.Horizontal, Qt.AlignCenter,
                                            Qt.TextAlignmentRole)
        self._nativectx_model.setHeaderData(1, Qt.Horizontal, 'Value')
        self._nativectx_model.setHeaderData(1, Qt.Horizontal, Qt.AlignCenter, Qt.TextAlignmentRole)
        self._nativectx_model.setHeaderData(2, Qt.Horizontal, 'Decimal')
        #self._nativectx_model.setHeaderData(2, Qt.Horizontal, Qt.AlignCenter, Qt.TextAlignmentRole)
        self._nativectx_model.setHeaderData(3, Qt.Horizontal, 'Telescope')

        self._nativectx_list = DwarfListView()
        self._nativectx_list.setModel(self._nativectx_model)

        self._nativectx_list.header().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self._nativectx_list.header().setSectionResizeMode(
            1, QHeaderView.ResizeToContents)
        self._nativectx_list.header().setSectionResizeMode(
            2, QHeaderView.ResizeToContents)

        self._nativectx_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._nativectx_list.customContextMenuRequested.connect(
            self._on_native_contextmenu)

        self._emulatorctx_model = QStandardItemModel(0, 3)
        self._emulatorctx_model.setHeaderData(0, Qt.Horizontal, 'Reg')
        self._emulatorctx_model.setHeaderData(0, Qt.Horizontal, Qt.AlignCenter,
                                              Qt.TextAlignmentRole)
        self._emulatorctx_model.setHeaderData(1, Qt.Horizontal, 'Value')
        self._emulatorctx_model.setHeaderData(1, Qt.Horizontal, Qt.AlignCenter, Qt.TextAlignmentRole)
        self._emulatorctx_model.setHeaderData(2, Qt.Horizontal, 'Decimal')

        self._emulatorctx_list = DwarfListView()
        self._emulatorctx_list.setModel(self._emulatorctx_model)

        self._emulatorctx_list.header().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self._emulatorctx_list.header().setSectionResizeMode(
            1, QHeaderView.ResizeToContents)

        self._emulatorctx_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._emulatorctx_list.customContextMenuRequested.connect(
            self._on_emulator_contextmenu)

        self._javactx_model = QStandardItemModel(0, 3)
        self._javactx_model.setHeaderData(0, Qt.Horizontal, 'Argument')
        self._javactx_model.setHeaderData(0, Qt.Horizontal, Qt.AlignCenter,
                                          Qt.TextAlignmentRole)
        self._javactx_model.setHeaderData(1, Qt.Horizontal, 'Class')
        #self._javactx_model.setHeaderData(1, Qt.Horizontal, Qt.AlignCenter, Qt.TextAlignmentRole)
        self._javactx_model.setHeaderData(2, Qt.Horizontal, 'Value')

        self._javactx_list = DwarfListView()
        self._javactx_list.setModel(self._javactx_model)

        self._javactx_list.header().setSectionResizeMode(
            0, QHeaderView.ResizeToContents)
        self._javactx_list.header().setSectionResizeMode(
            1, QHeaderView.ResizeToContents)
        self._javactx_list.header().setSectionResizeMode(
            2, QHeaderView.ResizeToContents)

        self._javactx_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._javactx_list.customContextMenuRequested.connect(
            self._on_java_contextmenu)

        self.addTab(self._nativectx_list, 'Native')
        self.show_context_tab('Native')

    # ************************************************************************
    # **************************** Functions *********************************
    # ************************************************************************
    def clear(self):
        self._nativectx_list.clear()
        self._emulatorctx_list.clear()
        self._javactx_list.clear()

    def set_context(self, ptr, context_type, context):
        if isinstance(context, str):
            context = json.loads(context)

        if context_type == ContextPanel.CONTEXT_TYPE_NATIVE:
            self._nativectx_list.clear()
            self._set_native_context(ptr, context)
        elif context_type == ContextPanel.CONTEXT_TYPE_JAVA:
            self._javactx_list.clear()
            self._set_java_context(ptr, context)
        elif context_type == ContextPanel.CONTEXT_TYPE_EMULATOR:
            self._emulatorctx_list.clear()
            self._set_emulator_context(ptr, context)
        else:
            raise Exception('unknown context type')

    def have_context(self):
        return self.count() > 0

    def show_context_tab(self, tab_name):
        index = 0
        tab_name = tab_name.join(tab_name.split()).lower()
        if tab_name == 'native':
            index = self.indexOf(self._nativectx_list)
        elif tab_name == 'emulator':
            index = self.indexOf(self._emulatorctx_list)
        elif tab_name == 'java':
            index = self.indexOf(self._javactx_list)

        if self.count() > 0:
            self.setCurrentIndex(index)

    def _set_native_context(self, ptr, context):
        if self.indexOf(self._nativectx_list) == -1:
            self.addTab(self._nativectx_list, 'Native')
            self.show_context_tab('Native')
        else:
            self.show_context_tab('Native')

        context_ptr = ptr

        reg_order = []
        if self._app_window.dwarf.arch == 'arm':  # arm
            reg_order = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14',
                         'r15', 'sp', 'lr', 'sb', 'sl', 'fp', 'ip', 'pc']
        elif self._app_window.dwarf.arch == 'arm64':
            reg_order = ['x0', 'x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8', 'x9', 'x10', 'x11', 'x12', 'x13', 'x14',
                         'x15', 'x16', 'x17', 'x18', 'x19', 'x20', 'x21', 'x22', 'x23', 'x24', 'x25', 'x26', 'x27',
                         'x28', 'x29', 'x30', 'w0', 'w1', 'w2', 'w3', 'w4', 'w5', 'w6', 'w7', 'w8', 'w9', 'w10', 'w11',
                         'w12', 'w13', 'w14', 'w15', 'w16', 'w17', 'w18', 'w19', 'w20', 'w21', 'w22', 'w23', 'w24',
                         'w25', 'w26', 'w27', 'w28', 'w29', 'w30', 'sp', 'lr', 'fp', 'wsp', 'wzr', 'xzr', 'nzcv',
                         'ip0', 'ip1', 's0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 's12',
                         's13', 's14', 's15', 's16', 's17', 's18', 's19', 's20', 's21', 's22', 's23', 's24', 's25',
                         's26', 's27', 's28', 's29', 's30', 's31', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7',
                         'd8', 'd9', 'd10', 'd11', 'd12', 'd13', 'd14', 'd15', 'd16', 'd17', 'd18', 'd19', 'd20',
                         'd21', 'd22', 'd23', 'd24', 'd25', 'd26', 'd27', 'd28', 'd29', 'd30', 'd31', 'q0', 'q1', 'q2',
                         'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q11', 'q12', 'q13', 'q14', 'q15', 'q16',
                         'q17', 'q18', 'q19', 'q20', 'q21', 'q22', 'q23', 'q24', 'q25', 'q26', 'q27', 'q28', 'q29',
                         'q30', 'q31', 'sp', 'lr', 'sb', 'sl', 'fp', 'ip', 'pc']
        elif self._app_window.dwarf.arch == 'ia32':
            reg_order = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'esp', 'r8d', 'r9d', 'r10d', 'r11d', 'r12d', 'r13d',
                         'r14d', 'r15d', 'ebp', 'eip', 'sp', 'pc']
        elif self._app_window.dwarf.arch == 'x64':  # x64
            reg_order = ['rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'rbp', 'rsp', 'r8', 'r9', 'r10', 'r11', 'r12',
                         'r13', 'r14', 'r15', 'esp', 'ebp', 'rip', 'eip', 'sp', 'pc']

        sorted_regs = {b: i for i, b in enumerate(reg_order)}

        for register in sorted(context, key=lambda x: sorted_regs[x]):
            reg_name = QStandardItem()
            reg_name.setTextAlignment(Qt.AlignCenter)
            if context[register]['isValidPointer']:
                reg_name.setForeground(Qt.red)
                reg_name.setData(context_ptr)

            value_x = QStandardItem()
            # value_x.setTextAlignment(Qt.AlignCenter)
            value_dec = QStandardItem()
            # value_dec.setTextAlignment(Qt.AlignCenter)
            telescope = QStandardItem()

            reg_name.setText(register)

            if context[register] is not None:
                str_fmt = '0x{0:x}'
                if self._nativectx_list.uppercase_hex:
                    str_fmt = '0x{0:X}'

                value_x.setText(
                    str_fmt.format(int(context[register]['value'], 16)))

                value_dec.setText('{0:d}'.format(
                    int(context[register]['value'], 16)))

                if context[register]['isValidPointer']:
                    if 'telescope' in context[register] and context[register][
                            'telescope'] is not None:
                        telescope = QStandardItem()
                        telescope.setText(
                            str(context[register]['telescope'][1]))
                        if context[register]['telescope'][0] == 2:
                            telescope.setData(
                                context[register]['telescope'][1],
                                Qt.UserRole + 1)

                        if context[register]['telescope'][0] == 0:
                            telescope.setForeground(Qt.darkGreen)
                        elif context[register]['telescope'][0] == 2:
                            telescope.setForeground(Qt.white)
                        elif context[register]['telescope'][0] != 1:
                            telescope.setForeground(Qt.darkGray)

            self._nativectx_model.appendRow([reg_name, value_x, value_dec, telescope])
            self._nativectx_list.resizeColumnToContents(0)

    def _set_emulator_context(self, ptr, context):
        if self.indexOf(self._emulatorctx_list) == -1:
            self.addTab(self._emulatorctx_list, 'Emulator')
            self.show_context_tab('Emulator')
        else:
            self.show_context_tab('Emulator')

        context_ptr = ptr

        context = context.__dict__

        for register in sorted(context):
            # todo: ???
            if register.startswith('_'):
                continue

            reg_name = QStandardItem()
            reg_name.setTextAlignment(Qt.AlignCenter)
            reg_name.setForeground(QColor('#39c'))
            value_x = QStandardItem()
            # value_x.setTextAlignment(Qt.AlignCenter)
            value_dec = QStandardItem()
            # value_dec.setTextAlignment(Qt.AlignCenter)

            reg_name.setText(register)
            reg_name.setData(context_ptr)

            if context[register] is not None:
                if isinstance(context[register], int):
                    str_fmt = '0x{0:x}'
                    if self._emulatorctx_list.uppercase_hex:
                        str_fmt = '0x{0:X}'

                    value_x.setText(str_fmt.format(context[register]))

                    value_dec.setText('{0:d}'.format(context[register]))

            self._emulatorctx_model.appendRow([reg_name, value_x, value_dec])
            self._emulatorctx_list.resizeColumnToContents(0)
            self._emulatorctx_list.resizeColumnToContents(1)

    def _set_java_context(self, ptr, context):
        if self.indexOf(self._javactx_list) == -1:
            self.addTab(self._javactx_list, 'Java')
            self.show_context_tab('Java')
        else:
            self.show_context_tab('Java')

        for arg in context:
            _arg = QStandardItem()
            _arg.setText(arg)

            _class = QStandardItem()
            _class.setText(context[arg]['className'])
            if isinstance(context[arg]['handle'], str):
                _class.setForeground(Qt.lightGray)

            _value = QStandardItem()
            if context[arg] is not None:
                _value.setText('null')
                _value.setForeground(Qt.gray)

            self._javactx_model.appendRow([_arg, _class, _value])
            self._javactx_list.resizeColumnToContents(0)
            self._javactx_list.resizeColumnToContents(1)

    # ************************************************************************
    # **************************** Handlers **********************************
    # ************************************************************************
    def _on_native_contextmenu(self, pos):
        index = self._nativectx_list.indexAt(pos).row()
        glbl_pt = self._nativectx_list.mapToGlobal(pos)
        context_menu = QMenu(self)
        if index != -1:
            context_menu.addAction(
                'Copy address', lambda: utils.copy_hex_to_clipboard(
                    self._nativectx_model.item(index, 1).text()))
            context_menu.addAction(
                'Jump to address', lambda: self.onShowMemoryRequest.emit(
                    self._nativectx_model.item(index, 1).text()))
        context_menu.exec_(glbl_pt)

    def _on_emulator_contextmenu(self, pos):
        index = self._emulatorctx_list.indexAt(pos).row()
        glbl_pt = self._emulatorctx_list.mapToGlobal(pos)
        context_menu = QMenu(self)
        if index != -1:
            pass
        context_menu.exec_(glbl_pt)

    def _on_java_contextmenu(self, pos):
        index = self._javactx_list.indexAt(pos).row()
        glbl_pt = self._javactx_list.mapToGlobal(pos)
        context_menu = QMenu(self)
        if index != -1:
            pass
        context_menu.exec_(glbl_pt)
