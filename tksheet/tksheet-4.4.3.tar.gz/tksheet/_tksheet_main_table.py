from ._tksheet_vars import *
from ._tksheet_other_classes import *

from collections import defaultdict, deque
from itertools import islice, repeat, accumulate, chain, product
from math import floor, ceil
from tkinter import ttk
import bisect
import csv as csv_module
import io
import pickle
import re
import tkinter as tk
import zlib
# for mac bindings
from platform import system as get_os


class MainTable(tk.Canvas):
    def __init__(self,
                 parentframe = None,
                 column_width = None,
                 column_headers_canvas = None,
                 row_index_canvas = None,
                 headers = None,
                 header_height = None,
                 row_height = None,
                 data_reference = None,
                 total_cols = None,
                 total_rows = None,
                 row_index = None,
                 font = None,
                 header_font = None,
                 popup_menu_font = ("Arial", 11, "normal"),
                 popup_menu_fg = "gray10",
                 popup_menu_bg = "white",
                 popup_menu_highlight_bg = "#f1f3f4",
                 popup_menu_highlight_fg = "gray10",
                 align = None,
                 width = None,
                 height = None,
                 table_background = "white",
                 grid_color = "gray15",
                 text_color = "black",
                 show_selected_cells_border = True,
                 selected_cells_border_color = "#1a73e8",
                 selected_cells_background = "#e7f0fd",
                 selected_cells_foreground = "black",
                 selected_rows_border_color = "#1a73e8",
                 selected_rows_background = "#e7f0fd",
                 selected_rows_foreground = "black",
                 selected_columns_border_color = "#1a73e8",
                 selected_columns_background = "#e7f0fd",
                 selected_columns_foreground = "black",
                 displayed_columns = [],
                 all_columns_displayed = True,
                 max_undos = 20):
        tk.Canvas.__init__(self,
                           parentframe,
                           width = width,
                           height = height,
                           background = table_background,
                           highlightthickness = 0)
        self.min_rh = 0
        self.hdr_min_rh = 0
        self.beingDrawnSelRect = None
        self.beingDrawnSelBorder = None
        self.extra_motion_func = None
        self.extra_b1_press_func = None
        self.extra_b1_motion_func = None
        self.extra_b1_release_func = None
        self.extra_double_b1_func = None
        self.extra_rc_func = None
        self.extra_ctrl_c_func = None
        self.extra_ctrl_x_func = None
        self.extra_ctrl_v_func = None
        self.extra_ctrl_z_func = None
        self.extra_delete_key_func = None
        self.extra_edit_cell_func = None
        self.extra_del_rows_rc_func = None
        self.extra_del_cols_rc_func = None
        self.extra_insert_cols_rc_func = None
        self.extra_insert_rows_rc_func = None
        self.selection_binding_func = None # function to run when a spreadsheet selection event occurs
        self.deselection_binding_func = None # function to run when a spreadsheet deselection event occurs
        self.drag_selection_binding_func = None # function to run when a spreadsheet mouse drag selection event occurs
        self.shift_selection_binding_func = None # function to run when a spreadsheet shift click selection event occurs
        self.select_all_binding_func = None
        self.single_selection_enabled = False
        self.drag_selection_enabled = False
        self.toggle_selection_enabled = False # with this mode every left click adds the cell to selected cells, work ongoing with this...
        self.arrowkeys_enabled = False
        self.undo_enabled = False
        self.cut_enabled = False
        self.copy_enabled = False
        self.paste_enabled = False
        self.delete_key_enabled = False
        self.rc_select_enabled = False
        self.rc_delete_column_enabled = False
        self.rc_insert_column_enabled = False
        self.rc_delete_row_enabled = False
        self.rc_insert_row_enabled = False
        self.rc_popup_menus_enabled = False
        self.show_selected_cells_border = show_selected_cells_border # probably best to turn off if using toggle_selection_enabled
        self.new_row_width = 0
        self.new_header_height = 0
        self.parentframe = parentframe
        self.row_width_resize_bbox = tuple()
        self.header_height_resize_bbox = tuple()
        self.CH = column_headers_canvas
        self.CH.MT = self
        self.CH.RI = row_index_canvas
        self.RI = row_index_canvas
        self.RI.MT = self
        self.RI.CH = column_headers_canvas
        self.TL = None                # is set from within TopLeftRectangle() __init__
        self.data_ref = data_reference
        if isinstance(self.data_ref, list):
            self.data_ref = data_reference
        else:
            self.data_ref = []
        if not self.data_ref:
            if isinstance(total_rows, int) and isinstance(total_cols, int) and total_rows > 0 and total_cols > 0:
                self.data_ref = [list(repeat("", total_cols)) for r in range(total_rows)]
        self.displayed_columns = displayed_columns
        self.all_columns_displayed = all_columns_displayed

        self.grid_color = grid_color
        self.text_color = text_color
        self.selected_cells_border_col = selected_cells_border_color
        self.selected_cells_background = selected_cells_background
        self.selected_cells_foreground = selected_cells_foreground
        self.selected_rows_border_color = selected_rows_border_color
        self.selected_rows_bg = selected_rows_background
        self.selected_rows_fg = selected_rows_foreground
        self.selected_cols_border_color = selected_columns_border_color
        self.selected_cols_bg = selected_columns_background
        self.selected_cols_fg = selected_columns_foreground
        self.table_background = table_background
        
        self.align = align
        self.my_font = font
        self.fnt_fam = font[0]
        self.fnt_sze = font[1]
        self.fnt_wgt = font[2]
        self.my_hdr_font = header_font
        self.hdr_fnt_fam = header_font[0]
        self.hdr_fnt_sze = header_font[1]
        self.hdr_fnt_wgt = header_font[2]

        self.txt_measure_canvas = tk.Canvas(self)
        self.table_dropdown = None
        self.table_dropdown_id = None
        self.table_dropdown_value = None
        self.text_editor = None
        self.text_editor_id = None
        self.default_cw = column_width
        self.default_rh = int(row_height)
        self.default_hh = int(header_height)
        self.set_fnt_help()
        self.set_hdr_fnt_help()

        self.popup_menu_font = popup_menu_font
        self.popup_menu_fg = popup_menu_fg
        self.popup_menu_bg = popup_menu_bg
        self.popup_menu_highlight_bg = popup_menu_highlight_bg
        self.popup_menu_highlight_fg = popup_menu_highlight_fg

        if isinstance(headers, int):
            self.my_hdrs = headers
        else:
            if headers:
                self.my_hdrs = headers
            else:
                self.my_hdrs = []
        
        if isinstance(row_index, int):
            self.my_row_index = row_index
        else:
            if row_index:
                self.my_row_index = row_index
            else:
                self.my_row_index = []

        self.col_positions = [0]
        self.row_positions = [0]
        self.reset_col_positions()
        self.reset_row_positions()

        self.highlighted_cells = {}
        self.max_undos = max_undos
        self.undo_storage = deque(maxlen = max_undos)

        self.bind("<Motion>", self.mouse_motion)
        self.bind("<Shift-ButtonPress-1>",self.shift_b1_press)
        self.bind("<ButtonPress-1>", self.b1_press)
        self.bind("<B1-Motion>", self.b1_motion)
        self.bind("<ButtonRelease-1>", self.b1_release)
        self.bind("<Double-Button-1>", self.double_b1)
        self.bind("<Configure>", self.refresh)
        self.bind("<MouseWheel>", self.mousewheel)
        self.bind(get_rc_binding(), self.rc)
        self.CH.bind(get_rc_binding(), self.CH.rc)
        self.RI.bind(get_rc_binding(), self.RI.rc)
        self.create_rc_menus()
        
    def refresh(self, event = None):
        self.main_table_redraw_grid_and_text(True, True)

    def basic_bindings(self, enable = True):
        if enable:
            self.bind("<Motion>", self.mouse_motion)
            self.bind("<ButtonPress-1>", self.b1_press)
            self.bind("<B1-Motion>", self.b1_motion)
            self.bind("<ButtonRelease-1>", self.b1_release)
            self.bind("<Double-Button-1>", self.double_b1)
            self.bind("<MouseWheel>", self.mousewheel)
            self.bind(get_rc_binding(), self.rc)
        else:
            self.unbind("<Motion>")
            self.unbind("<ButtonPress-1>")
            self.unbind("<B1-Motion>")
            self.unbind("<ButtonRelease-1>")
            self.unbind("<Double-Button-1>")
            self.unbind("<MouseWheel>")
            self.unbind(get_rc_binding())

    def show_ctrl_outline(self, canvas = "table", start_cell = (0, 0), end_cell = (0, 0)):
        self.create_rectangle(self.col_positions[start_cell[0]] + 1,
                              self.row_positions[start_cell[1]] + 1,
                              self.col_positions[end_cell[0]],
                              self.row_positions[end_cell[1]],
                              fill = "",
                              dash = (25, 5),
                              width = 2,
                              outline = self.selected_cells_border_col,
                              tag = "ctrl")
        self.tag_raise("ctrl")
        self.after(1000, self.del_ctrl_outline)

    def del_ctrl_outline(self, event = None):
        self.delete("ctrl")

    def ctrl_c(self, event = None):
        currently_selected = self.currently_selected()
        if currently_selected:
            s = io.StringIO()
            writer = csv_module.writer(s, dialect = csv_module.excel_tab, lineterminator = "\n")
            if isinstance(currently_selected[0], int) or currently_selected[0] == "column":
                boxes, maxrows = self.get_ctrl_x_c_boxes()
                if self.all_columns_displayed:
                    for rn in range(maxrows):
                        row = []
                        for r1, c1, r2, c2 in boxes:
                            if r2 - r1 < maxrows:
                                continue
                            data_ref_rn = r1 + rn
                            for c in range(c1, c2):
                                try:
                                    row.append(self.data_ref[data_ref_rn][c])
                                except:
                                    row.append("")
                        writer.writerow(row)
                else:
                    for rn in range(maxrows):
                        row = []
                        for r1, c1, r2, c2 in boxes:
                            if r2 - r1 < maxrows:
                                continue
                            data_ref_rn = r1 + rn
                            for c in range(c1, c2):
                                try:
                                    row.append(self.data_ref[data_ref_rn][self.displayed_columns[c]])
                                except:
                                    row.append("")
                        writer.writerow(row)
            elif currently_selected[0] == "row":
                boxes = self.get_ctrl_x_c_boxes()
                if self.all_columns_displayed:
                    for r1, c1, r2, c2 in boxes:
                        for rn in range(r2 - r1):
                            row = []
                            data_ref_rn = r1 + rn
                            for c in range(c1, c2):
                                try:
                                    row.append(self.data_ref[data_ref_rn][c])
                                except:
                                    row.append("")
                            writer.writerow(row)
                else:
                    for r1, c1, r2, c2 in boxes:
                        for rn in range(r2 - r1):
                            row = []
                            data_ref_rn = r1 + rn
                            for c in range(c1, c2):
                                try:
                                    row.append(self.data_ref[data_ref_rn][self.displayed_columns[c]])
                                except:
                                    row.append("")
                            writer.writerow(row)
            for r1, c1, r2, c2 in boxes:
                self.show_ctrl_outline(canvas = "table", start_cell = (c1, r1), end_cell = (c2, r2))
            self.clipboard_clear()
            s = s.getvalue().rstrip()
            if self.extra_ctrl_c_func is not None:
                self.extra_ctrl_c_func(s)
            self.clipboard_append(s)
            self.update()

    def get_ctrl_x_c_boxes(self):
        currently_selected = self.currently_selected()
        boxes = {}
        if isinstance(currently_selected[0], int) or currently_selected[0] == "column":
            for item in chain(self.find_withtag("CellSelectFill"), self.find_withtag("Current_Outside"), self.find_withtag("ColSelectFill")):
                alltags = self.gettags(item)
                if alltags[0] == "CellSelectFill" or alltags[0] == "Current_Outside":
                    boxes[tuple(int(e) for e in alltags[1].split("_") if e)] = "cells"
                elif alltags[0] == "ColSelectFill":
                    boxes[tuple(int(e) for e in alltags[1].split("_") if e)] = "cols"
            maxrows = 0
            for r1, c1, r2, c2 in boxes:
                if r2 - r1 > maxrows:
                    maxrows = r2 - r1
            for r1, c1, r2, c2 in tuple(boxes):
                if r2 - r1 < maxrows:
                    del boxes[(r1, c1, r2, c2)]
            return boxes, maxrows
        elif currently_selected[0] == "row":
            for item in self.find_withtag("RowSelectFill"):
                boxes[tuple(int(e) for e in self.gettags(item)[1].split("_") if e)] = "rows"
            return boxes
            
    def ctrl_x(self, event = None):
        if self.anything_selected():
            if self.undo_enabled:
                undo_storage = {}
            s = io.StringIO()
            writer = csv_module.writer(s, dialect = csv_module.excel_tab, lineterminator = "\n")
            currently_selected = self.currently_selected()         
            if isinstance(currently_selected[0], int) or currently_selected[0] == "column":
                boxes, maxrows = self.get_ctrl_x_c_boxes()
                if self.all_columns_displayed:
                    for rn in range(maxrows):
                        row = []
                        for r1, c1, r2, c2 in boxes:
                            if r2 - r1 < maxrows:
                                continue
                            data_ref_rn = r1 + rn
                            for c in range(c1, c2):
                                try:
                                    sx = f"{self.data_ref[data_ref_rn][c]}"
                                    row.append(sx)
                                    if self.undo_enabled:
                                        undo_storage[(data_ref_rn, c)] = sx
                                except:
                                    row.append("")
                        writer.writerow(row)
                    for rn in range(maxrows):
                        for r1, c1, r2, c2 in boxes:
                            if r2 - r1 < maxrows:
                                continue
                            for c in range(c1, c2):
                                try:
                                    self.data_ref[r1 + rn][c] = ""
                                except:
                                    continue
                else:
                    for rn in range(maxrows):
                        row = []
                        for r1, c1, r2, c2 in boxes:
                            if r2 - r1 < maxrows:
                                continue
                            data_ref_rn = r1 + rn
                            for c in range(c1, c2):
                                try:
                                    sx = f"{self.data_ref[data_ref_rn][self.displayed_columns[c]]}"
                                    row.append(sx)
                                    if self.undo_enabled:
                                        undo_storage[(data_ref_rn, self.displayed_columns[c])] = sx
                                except:
                                    row.append("")
                        writer.writerow(row)
                    for rn in range(maxrows):
                        for r1, c1, r2, c2 in boxes:
                            if r2 - r1 < maxrows:
                                continue
                            for c in range(c1, c2):
                                try:
                                    self.data_ref[r1 + rn][self.displayed_columns[c]] = ""
                                except:
                                    continue
            elif currently_selected[0] == "row":
                boxes = self.get_ctrl_x_c_boxes()
                if self.all_columns_displayed:
                    for r1, c1, r2, c2 in boxes:
                        for rn in range(r2 - r1):
                            row = []
                            data_ref_rn = r1 + rn
                            for c in range(c1, c2):
                                try:
                                    sx = f"{self.data_ref[data_ref_rn][c]}"
                                    row.append(sx)
                                    if self.undo_enabled:
                                        undo_storage[(data_ref_rn, c)] = sx
                                except:
                                    row.append("")
                            writer.writerow(row)
                    for r1, c1, r2, c2 in boxes:
                        for rn in range(r2 - r1):
                            for c in range(c1, c2):
                                try:
                                    self.data_ref[r1 + rn][c] = ""
                                except:
                                    continue
                else:
                    for r1, c1, r2, c2 in boxes:
                        for rn in range(r2 - r1):
                            row = []
                            data_ref_rn = r1 + rn
                            for c in range(c1, c2):
                                try:
                                    sx = f"{self.data_ref[data_ref_rn][self.displayed_columns[c]]}"
                                    row.append(sx)
                                    if self.undo_enabled:
                                        undo_storage[(data_ref_rn, self.displayed_columns[c])] = sx
                                except:
                                    row.append("")
                            writer.writerow(row)
                    for r1, c1, r2, c2 in boxes:
                        for rn in range(r2 - r1):
                            for c in range(c1, c2):
                                try:
                                    self.data_ref[r1 + rn][self.displayed_columns[c]] = ""
                                except:
                                    continue
            if self.undo_enabled:
                self.undo_storage.append(zlib.compress(pickle.dumps(("edit_cells", undo_storage, tuple(boxes.items()), currently_selected))))
            self.clipboard_clear()
            s = s.getvalue().rstrip()
            self.clipboard_append(s)
            self.update()
            self.refresh()
            for r1, c1, r2, c2 in boxes:
                self.show_ctrl_outline(canvas = "table", start_cell = (c1, r1), end_cell = (c2, r2))
            if self.extra_ctrl_x_func is not None:
                self.extra_ctrl_x_func()

    def ctrl_v(self, event = None):
        currently_selected = self.currently_selected()
        if currently_selected:
            try:
                data = self.clipboard_get()
            except:
                return
            nd = []
            for r in csv_module.reader(io.StringIO(data), delimiter = "\t", quotechar = '"', skipinitialspace = True):
                try:
                    nd.append(r[:len(r) - next(i for i, c in enumerate(reversed(r)) if c)])
                except:
                    continue
            if not nd:
                return
            data = nd
            numcols = len(max(data, key = len))
            numrows = len(data)
            for rn, r in enumerate(data):
                if len(r) < numcols:
                    data[rn].extend(list(repeat("", numcols - len(r))))
            if self.undo_enabled:
                undo_storage = {}
            if currently_selected[0] == "column":
                x1 = currently_selected[1]
                y1 = 0
            elif currently_selected[0] == "row":
                y1 = currently_selected[1]
                x1 = 0
            elif isinstance(currently_selected[0], int):
                y1 = currently_selected[0]
                x1 = currently_selected[1]
            if x1 + numcols > len(self.col_positions) - 1:
                numcols = len(self.col_positions) - 1 - x1
            if y1 + numrows > len(self.row_positions) - 1:
                numrows = len(self.row_positions) - 1 - y1
            if self.all_columns_displayed:
                for ndr, r in enumerate(range(y1, y1 + numrows)):
                    for ndc, c in enumerate(range(x1, x1 + numcols)):
                        s = f"{self.data_ref[r][c]}"
                        if self.undo_enabled:
                            undo_storage[(r, c)] = s
                        self.data_ref[r][c] = data[ndr][ndc]
            else:
                for ndr, r in enumerate(range(y1, y1 + numrows)):
                    for ndc, c in enumerate(range(x1, x1 + numcols)):
                        s = f"{self.data_ref[r][self.displayed_columns[c]]}"
                        if self.undo_enabled:
                            undo_storage[(r, self.displayed_columns[c])] = s
                        self.data_ref[r][self.displayed_columns[c]] = data[ndr][ndc]
            self.deselect("all")
            if self.undo_enabled:
                self.undo_storage.append(zlib.compress(pickle.dumps(("edit_cells", undo_storage, (((y1, x1, y1 + numrows, x1 + numcols), "cells"), ), currently_selected))))
            self.create_selected(y1, x1, y1 + numrows, x1 + numcols, "cells")
            self.create_current(y1, x1, type_ = "cell", inside = True if numrows > 1 or numcols > 1 else False)
            self.see(r = y1, c = x1, keep_yscroll = False, keep_xscroll = False, bottom_right_corner = False, check_cell_visibility = True, redraw = False)
            self.refresh()
            if self.extra_ctrl_v_func is not None:
                self.extra_ctrl_v_func()

    def delete_key(self, event = None):
        if self.anything_selected():
            currently_selected = self.currently_selected()
            if self.undo_enabled:
                undo_storage = {}
                boxes = []
            if self.all_columns_displayed:    
                for item in chain(self.find_withtag("CellSelectFill"), self.find_withtag("RowSelectFill"), self.find_withtag("ColSelectFill"), self.find_withtag("Current_Outside")):
                    alltags = self.gettags(item)
                    box = tuple(int(e) for e in alltags[1].split("_") if e)
                    if self.undo_enabled:
                        if alltags[0] in ("CellSelectFill", "Current_Outside"):
                            boxes.append((box, "cells"))
                        elif alltags[0] == "ColSelectFill":
                            boxes.append((box, "cols"))
                        elif alltags[0] == "RowSelectFill":
                            boxes.append((box, "rows"))
                    r1, c1, r2, c2 = box
                    for r in range(r1, r2):
                        for c in range(c1, c2):
                            if self.undo_enabled:
                                undo_storage[(r, c)] = f"{self.data_ref[r][c]}"
                            self.data_ref[r][c] = ""
            else:
                for item in chain(self.find_withtag("CellSelectFill"), self.find_withtag("RowSelectFill"), self.find_withtag("ColSelectFill"), self.find_withtag("Current_Outside")):
                    alltags = self.gettags(item)
                    box = tuple(int(e) for e in alltags[1].split("_") if e)
                    if self.undo_enabled:
                        if alltags[0] in ("CellSelectFill", "Current_Outside"):
                            boxes.append((box, "cells"))
                        elif alltags[0] == "ColSelectFill":
                            boxes.append((box, "cols"))
                        elif alltags[0] == "RowSelectFill":
                            boxes.append((box, "rows"))
                    r1, c1, r2, c2 = box
                    for r in range(r1, r2):
                        for c in range(c1, c2):
                            if self.undo_enabled:
                                undo_storage[(r, self.displayed_columns[c])] = f"{self.data_ref[r][self.displayed_columns[c]]}"
                            self.data_ref[r][self.displayed_columns[c]] = ""
            if self.undo_enabled:
                self.undo_storage.append(zlib.compress(pickle.dumps(("edit_cells", undo_storage, boxes, currently_selected))))
            self.refresh()
            if self.extra_delete_key_func is not None:
                self.extra_delete_key_func()

    def ctrl_z(self, event = None):
        if self.undo_storage:
            undo_storage = pickle.loads(zlib.decompress(self.undo_storage.pop()))
            self.deselect("all")
            if undo_storage[0] == "edit_cells":
                for (r, c), v in undo_storage[1].items():
                    self.data_ref[r][c] = v
                start_row = float("inf")
                start_col = float("inf")
                for box in undo_storage[2]:
                    r1, c1, r2, c2 = box[0]
                    self.create_selected(r1, c1, r2, c2, box[1])
                    if r1 < start_row:
                        start_row = r1
                    if c1 < start_col:
                        start_col = c1
                if isinstance(undo_storage[3][0], int):
                    self.create_current(undo_storage[3][0], undo_storage[3][1], type_ = "cell", inside = True if self.is_cell_selected(undo_storage[3][0], undo_storage[3][1]) else False)
                elif undo_storage[3][0] == "column":
                    self.create_current(0, undo_storage[3][1], type_ = "col", inside = True)
                elif undo_storage[3][0] == "row":
                    self.create_current(undo_storage[3][1], 0, type_ = "row", inside = True)
                self.see(r = start_row, c = start_col, keep_yscroll = False, keep_xscroll = False, bottom_right_corner = False, check_cell_visibility = True, redraw = False)
            elif undo_storage[0] == "move_rows":
                rhs = [int(b - a) for a, b in zip(self.row_positions, islice(self.row_positions, 1, len(self.row_positions)))]
                ins_row = undo_storage[1]
                orig_ins_row = int(ins_row)
                rm1start = undo_storage[2][0]
                rm1end = undo_storage[2][1] + 1
                rm2start = rm1start + (rm1end - rm1start)
                rm2end = rm1end + (rm1end - rm1start)
                totalrows = rm1end - rm1start
                if rm1start < ins_row:
                    ins_row += totalrows
                if rm1start > ins_row:
                    try:
                        self.data_ref[ins_row:ins_row] = self.data_ref[rm1start:rm1end]
                        self.data_ref[rm2start:rm2end] = []
                    except:
                        pass
                    if self.my_row_index:
                        try:
                            self.my_row_index[ins_row:ins_row] = self.my_row_index[rm1start:rm1end]
                            self.my_row_index[rm2start:rm2end] = []
                        except:
                            pass
                else:
                    try:
                        self.data_ref[ins_row:ins_row] = self.data_ref[rm1start:rm1end]
                        self.data_ref[rm1start:rm1end] = []
                    except:
                        pass
                    if self.my_row_index:
                        try:
                            self.my_row_index[ins_row:ins_row] = self.my_row_index[rm1start:rm1end]
                            self.my_row_index[rm1start:rm1end] = []
                        except:
                            pass
                if rm1start > ins_row:
                    rhs[ins_row:ins_row] = rhs[rm1start:rm1end]
                    rhs[rm2start:rm2end] = []
                    self.row_positions = list(accumulate(chain([0], (height for height in rhs))))
                    self.create_current(ins_row, 0, type_ = "row", inside = True)
                    self.create_selected(ins_row, 0, ins_row + totalrows, len(self.col_positions) - 1, "rows")
                else:
                    rhs[ins_row:ins_row] = rhs[rm1start:rm1end]
                    rhs[rm1start:rm1end] = []
                    self.row_positions = list(accumulate(chain([0], (height for height in rhs))))
                    self.create_current(ins_row - totalrows, 0, type_ = "row", inside = True)
                    self.create_selected(ins_row - totalrows, 0, ins_row, len(self.col_positions) - 1, "rows")
                self.see(r = orig_ins_row, c = 0, keep_yscroll = False, keep_xscroll = True, bottom_right_corner = False, check_cell_visibility = True, redraw = False)
            elif undo_storage[0] == "move_cols":
                cws = [int(b - a) for a, b in zip(self.col_positions, islice(self.col_positions, 1, len(self.col_positions)))]
                ins_col = undo_storage[1]
                orig_ins_col = int(ins_col)
                rm1start = undo_storage[2][0]
                rm1end = undo_storage[2][1] + 1
                rm2start = rm1start + (rm1end - rm1start)
                rm2end = rm1end + (rm1end - rm1start)
                totalcols = rm1end - rm1start
                if rm1start < ins_col:
                    ins_col += totalcols
                if self.all_columns_displayed:
                    if rm1start > ins_col:
                        for rn in range(len(self.data_ref)):
                            try:
                                self.data_ref[rn][ins_col:ins_col] = self.data_ref[rn][rm1start:rm1end]
                                self.data_ref[rn][rm2start:rm2end] = []
                            except:
                                continue
                        if self.my_hdrs:
                            try:
                                self.my_hdrs[ins_col:ins_col] = self.my_hdrs[rm1start:rm1end]
                                self.my_hdrs[rm2start:rm2end] = []
                            except:
                                pass
                    else:
                        for rn in range(len(self.data_ref)):
                            try:
                                self.data_ref[rn][ins_col:ins_col] = self.data_ref[rn][rm1start:rm1end]
                                self.data_ref[rn][rm1start:rm1end] = []
                            except:
                                continue
                        if self.my_hdrs:
                            try:
                                self.my_hdrs[ins_col:ins_col] = self.my_hdrs[rm1start:rm1end]
                                self.my_hdrs[rm1start:rm1end] = []
                            except:
                                pass
                else:
                    if rm1start > ins_col:
                        self.displayed_columns[ins_col:ins_col] = self.displayed_columns[rm1start:rm1end]
                        self.displayed_columns[rm2start:rm2end] = []
                    else:
                        self.displayed_columns[ins_col:ins_col] = self.displayed_columns[rm1start:rm1end]
                        self.displayed_columns[rm1start:rm1end] = []
                if rm1start > ins_col:
                    cws[ins_col:ins_col] = cws[rm1start:rm1end]
                    cws[rm2start:rm2end] = []
                    self.col_positions = list(accumulate(chain([0], (width for width in cws))))
                    self.create_current(0, ins_col, type_ = "col", inside = True)
                    self.create_selected(0, ins_col, len(self.row_positions) - 1, ins_col + totalcols, "cols")
                else:
                    cws[ins_col:ins_col] = cws[rm1start:rm1end]
                    cws[rm1start:rm1end] = []
                    self.col_positions = list(accumulate(chain([0], (width for width in cws))))
                    self.create_current(0, ins_col - totalcols, type_ = "col", inside = True)
                    self.create_selected(0, ins_col - totalcols, len(self.row_positions) - 1, ins_col, "cols")
                self.see(r = 0, c = orig_ins_col, keep_yscroll = True, keep_xscroll = False, bottom_right_corner = False, check_cell_visibility = True, redraw = False)
            elif undo_storage[0] == "insert_row":
                del self.data_ref[undo_storage[1]['data_row_num']]
                try:
                    del self.my_row_index[undo_storage[1]['data_row_num']]
                except:
                    pass
                self.del_row_position(undo_storage[1]['sheet_row_num'],
                                      deselect_all = False,
                                      preserve_other_selections = False)
                if len(self.row_positions) > 1:
                    start_row = undo_storage[1]['sheet_row_num'] if undo_storage[1]['sheet_row_num'] < len(self.row_positions) - 1 else undo_storage[1]['sheet_row_num'] - 1
                    self.RI.select_row(start_row)
                    self.see(r = start_row, c = 0, keep_yscroll = False, keep_xscroll = False, bottom_right_corner = False, check_cell_visibility = True, redraw = False)
            elif undo_storage[0] == "insert_col":
                qx = undo_storage[1]['data_col_num']
                for rn in range(len(self.data_ref)):
                    del self.data_ref[rn][qx]
                try:
                    del self.my_hdrs[qx]
                except:
                    pass
                self.del_col_position(undo_storage[1]['sheet_col_num'],
                                      deselect_all = False,
                                      preserve_other_selections = False)
                if len(self.col_positions) > 1:
                    start_col = undo_storage[1]['sheet_col_num'] if undo_storage[1]['sheet_col_num'] < len(self.col_positions) - 1 else undo_storage[1]['sheet_col_num'] - 1
                    self.CH.select_col(start_col)
                    self.see(r = 0, c = start_col, keep_yscroll = False, keep_xscroll = False, bottom_right_corner = False, check_cell_visibility = True, redraw = False)
            elif undo_storage[0] == "delete_rows":
                start_row = float("inf")
                for rn, r, h in reversed(undo_storage[1]['deleted_rows']):
                    self.data_ref.insert(rn, r)
                    self.insert_row_position(idx = rn, height = h)
                    if rn < start_row:
                        start_row = rn
                for rn, r in reversed(undo_storage[1]['deleted_index_values']):
                    try:
                        self.my_row_index.insert(rn, r)
                    except:
                        continue
                self.reselect_from_get_boxes(undo_storage[1]['selection_boxes'])
            elif undo_storage[0] == "delete_cols":
                start_col = float("inf")
                for cn, w in reversed(undo_storage[1]['colwidths'].items()):
                    self.insert_col_position(idx = cn, width = w)
                    if cn < start_col:
                        start_col = cn
                for cn, rowdict in reversed(undo_storage[1]['deleted_cols'].items()):
                    for rn, v in rowdict.items():
                        try:
                            self.data_ref[rn].insert(cn, v)
                        except:
                            continue
                for cn, v in reversed(tuple(undo_storage[1]['deleted_hdr_values'].items())):
                    try:
                        self.my_hdrs.insert(cn, v)
                    except:
                        continue
                self.reselect_from_get_boxes(undo_storage[1]['selection_boxes'])
            self.refresh()
            if self.extra_ctrl_z_func is not None:
                self.extra_ctrl_z_func()
            
    def bind_arrowkeys(self, event = None):
        self.arrowkeys_enabled = True
        for canvas in (self, self.CH, self.RI, self.TL):
            canvas.bind("<Up>", self.arrowkey_UP)
            canvas.bind("<Right>", self.arrowkey_RIGHT)
            canvas.bind("<Down>", self.arrowkey_DOWN)
            canvas.bind("<Left>", self.arrowkey_LEFT)
            canvas.bind("<Prior>", self.page_UP)
            canvas.bind("<Next>", self.page_DOWN)

    def unbind_arrowkeys(self, event = None):
        self.arrowkeys_enabled = False
        for canvas in (self, self.CH, self.RI, self.TL):
            canvas.unbind("<Up>")
            canvas.unbind("<Right>")
            canvas.unbind("<Down>")
            canvas.unbind("<Left>")
            canvas.unbind("<Prior>")
            canvas.unbind("<Next>")

    def see(self, r = None, c = None, keep_yscroll = False, keep_xscroll = False, bottom_right_corner = False, check_cell_visibility = True,
            redraw = True):
        need_redraw = False
        if check_cell_visibility:
            visible = self.cell_is_completely_visible(r = r, c = c)
        else:
            visible = False
        if not visible:
            if bottom_right_corner:
                if r is not None and not keep_yscroll:
                    y = self.row_positions[r + 1] + 1 - self.winfo_height()
                    args = ("moveto", y / (self.row_positions[-1] + 100))
                    self.yview(*args)
                    self.RI.yview(*args)
                    if redraw:
                        need_redraw = True
                if c is not None and not keep_xscroll:
                    x = self.col_positions[c + 1] + 1 - self.winfo_width()
                    args = ("moveto",x / (self.col_positions[-1] + 150))
                    self.xview(*args)
                    self.CH.xview(*args)
                    if redraw:
                        need_redraw = True
            else:
                if r is not None and not keep_yscroll:
                    args = ("moveto", self.row_positions[r] / (self.row_positions[-1] + 100))
                    self.yview(*args)
                    self.RI.yview(*args)
                    if redraw:
                        need_redraw = True
                if c is not None and not keep_xscroll:
                    args = ("moveto", self.col_positions[c] / (self.col_positions[-1] + 150))
                    self.xview(*args)
                    self.CH.xview(*args)
                    if redraw:
                        need_redraw = True
        if redraw and need_redraw:
            self.main_table_redraw_grid_and_text(redraw_header = True, redraw_row_index = True)

    def cell_is_completely_visible(self, r = 0, c = 0, cell_coords = None):
        cx1, cy1, cx2, cy2 = self.get_canvas_visible_area()
        if cell_coords is None:
            x1, y1, x2, y2 = self.GetCellCoords(r = r, c = c, sel = True)
        else:
            x1, y1, x2, y2 = cell_coords
        if cx1 > x1 or cy1 > y1 or cx2 < x2 or cy2 < y2:
            return False
        return True

    def cell_is_visible(self,r = 0, c = 0, cell_coords = None):
        cx1, cy1, cx2, cy2 = self.get_canvas_visible_area()
        if cell_coords is None:
            x1, y1, x2, y2 = self.GetCellCoords(r = r, c = c, sel = True)
        else:
            x1, y1, x2, y2 = cell_coords
        if x1 <= cx2 or y1 <= cy2 or x2 >= cx1 or y2 >= cy1:
            return True
        return False

    def select_all(self, redraw = True, run_binding_func = True):
        self.deselect("all")
        if len(self.row_positions) > 1 and len(self.col_positions) > 1:
            self.create_current(0, 0, type_ = "cell", inside = True)
            self.create_selected(0, 0, len(self.row_positions) - 1, len(self.col_positions) - 1)
            if redraw:
                self.main_table_redraw_grid_and_text(redraw_header = True, redraw_row_index = True)
            if self.select_all_binding_func is not None and run_binding_func:
                self.select_all_binding_func(("select_all_cells", ) + (0, 0, len(self.row_positions) - 1, len(self.col_positions) - 1))

    def select_cell(self, r, c, redraw = False, keep_other_selections = False):
        r = int(r)
        c = int(c)
        ignore_keep = False
        if keep_other_selections:
            if self.is_cell_selected(r, c):
                self.create_current(r, c, type_ = "cell", inside = True)
            else:
                ignore_keep = True
        if ignore_keep or not keep_other_selections:
            self.delete_selection_rects()
            self.create_current(r, c, type_ = "cell", inside = False)
        if redraw:
            self.main_table_redraw_grid_and_text(redraw_header = True, redraw_row_index = True)
        if self.selection_binding_func is not None:
            self.selection_binding_func(("select_cell", ) + tuple((r, c)))

    def add_selection(self, r, c, redraw = False, run_binding_func = True, set_as_current = False):
        r = int(r)
        c = int(c)
        if set_as_current:
            items = self.find_withtag("Current_Outside")
            if items:
                alltags = self.gettags(items[0])
                if alltags[2] == "cell":
                    r1, c1, r2, c2 = tuple(int(e) for e in alltags[1].split("_") if e)
                    add_sel = (r1, c1)
                else:
                    add_sel = tuple()
            else:
                add_sel = tuple()
            self.create_current(r, c, type_ = "cell", inside = True if self.is_cell_selected(r, c) else False)
            if add_sel:
                self.add_selection(add_sel[0], add_sel[1], redraw = False, run_binding_func = False, set_as_current = False)
        else:
            self.create_selected(r, c, r + 1, c + 1)
        if redraw:
            self.main_table_redraw_grid_and_text(redraw_header = True, redraw_row_index = True)
        if self.selection_binding_func is not None and run_binding_func:
            self.selection_binding_func(("select_cell", ) + tuple((r, c)))

    def toggle_select_cell(self, row, column, add_selection = True, redraw = True, run_binding_func = True, set_as_current = True):
        if add_selection:
            if self.is_cell_selected(row, column, inc_rows = True, inc_cols = True):
                self.deselect(r = row, c = column, redraw = redraw)
            else:
                self.add_selection(r = row, c = column, redraw = redraw, run_binding_func = run_binding_func, set_as_current = set_as_current)
        else:
            if self.is_cell_selected(row, column, inc_rows = True, inc_cols = True):
                self.deselect(r = row, c = column, redraw = redraw)
            else:
                self.select_cell(row, column, redraw = redraw)

    def highlight_cells(self, r = 0, c = 0, cells = tuple(), bg = None, fg = None, redraw = False):
        if bg is None and fg is None:
            return
        if cells:
            self.highlighted_cells = {t: (bg, fg) for t in cells}
        else:
            self.highlighted_cells[(r, c)] = (bg, fg)
        if redraw:
            self.main_table_redraw_grid_and_text()

    def deselect(self, r = None, c = None, cell = None, redraw = True):
        deselected = tuple()
        deleted_boxes = {}
        if r == "all":
            deselected = ("deselect_all", tuple(self.delete_selection_rects().items()))
        elif r == "allrows":
            for item in self.find_withtag("RowSelectFill"):
                alltags = self.gettags(item)
                if alltags:
                    r1, c1, r2, c2 = tuple(int(e) for e in alltags[1].split("_") if e)
                    deleted_boxes[r1, c1, r2, c2] = "rows"
                    self.delete(alltags[1])
                    self.RI.delete(alltags[1])
                    self.CH.delete(alltags[1])
            current = self.currently_selected()
            if current and current[0] == "row":
                deleted_boxes[tuple(int(e) for e in self.get_tags_of_current()[1].split("_") if e)] = "cell"
                self.delete_current()
            deselected = ("deselect_all_rows", tuple(deleted_boxes.items()))
        elif r == "allcols":
            for item in self.find_withtag("ColSelectFill"):
                alltags = self.gettags(item)
                if alltags:
                    r1, c1, r2, c2 = tuple(int(e) for e in alltags[1].split("_") if e)
                    deleted_boxes[r1, c1, r2, c2] = "cols"
                    self.delete(alltags[1])
                    self.RI.delete(alltags[1])
                    self.CH.delete(alltags[1])
            current = self.currently_selected()
            if current and current[0] == "column":
                deleted_boxes[tuple(int(e) for e in self.get_tags_of_current()[1].split("_") if e)] = "cell"
                self.delete_current()
            deselected = ("deselect_all_cols", tuple(deleted_boxes.items()))
        elif r is not None and c is None and cell is None:
            current = self.find_withtag("Current_Inside") + self.find_withtag("Current_Outside")
            current_tags = self.gettags(current[0]) if current else tuple()
            if current:
                curr_r1, curr_c1, curr_r2, curr_c2 = tuple(int(e) for e in current_tags[1].split("_") if e)
            reset_current = False
            for item in self.find_withtag("RowSelectFill"):
                alltags = self.gettags(item)
                if alltags:
                    r1, c1, r2, c2 = tuple(int(e) for e in alltags[1].split("_") if e)
                    if r >= r1 and r < r2:
                        self.delete(f"{r1}_{c1}_{r2}_{c2}")
                        self.RI.delete(f"{r1}_{c1}_{r2}_{c2}")
                        self.CH.delete(f"{r1}_{c1}_{r2}_{c2}")
                    if not reset_current and current and curr_r1 >= r1 and curr_r1 < r2:
                        reset_current = True
                        deleted_boxes[curr_r1, curr_c1, curr_r2, curr_c2] = "cell"
                    deleted_boxes[r1, c1, r2, c2] = "rows"
            if reset_current:
                self.delete_current()
                self.set_current_to_last()
            deselected = ("deselect_row", tuple(deleted_boxes.items()))
        elif c is not None and r is None and cell is None:
            current = self.find_withtag("Current_Inside") + self.find_withtag("Current_Outside")
            current_tags = self.gettags(current[0]) if current else tuple()
            if current:
                curr_r1, curr_c1, curr_r2, curr_c2 = tuple(int(e) for e in current_tags[1].split("_") if e)
            reset_current = False
            for item in self.find_withtag("ColSelectFill"):
                alltags = self.gettags(item)
                if alltags:
                    r1, c1, r2, c2 = tuple(int(e) for e in alltags[1].split("_") if e)
                    if c >= c1 and c < c2:
                        self.delete(f"{r1}_{c1}_{r2}_{c2}")
                        self.RI.delete(f"{r1}_{c1}_{r2}_{c2}")
                        self.CH.delete(f"{r1}_{c1}_{r2}_{c2}")
                    if not reset_current and current and curr_c1 >= c1 and curr_c1 < c2:
                        reset_current = True
                        deleted_boxes[curr_r1, curr_c1, curr_r2, curr_c2] = "cell"
                    deleted_boxes[r1, c1, r2, c2] = "cols"
            if reset_current:
                self.delete_current()
                self.set_current_to_last()
            deselected = ("deselect_column", tuple(deleted_boxes.items()))
        elif (r is not None and c is not None and cell is None) or cell is not None:
            set_curr = False
            if cell is not None:
                r, c = cell[0], cell[1]
            for item in chain(self.find_withtag("CellSelectFill"),
                              self.find_withtag("RowSelectFill"),
                              self.find_withtag("ColSelectFill"),
                              self.find_withtag("Current_Outside"),
                              self.find_withtag("Current_Inside")):
                alltags = self.gettags(item)
                if alltags:
                    r1, c1, r2, c2 = tuple(int(e) for e in alltags[1].split("_") if e)
                    if (r >= r1 and
                        c >= c1 and
                        r < r2 and
                        c < c2):
                        current = self.currently_selected()
                        if (not set_curr and
                            current and
                            r2 - r1 == 1 and
                            c2 - c1 == 1 and
                            r == current[0] and
                            c == current[1]):
                            set_curr = True
                        if current and not set_curr:
                            if isinstance(current[0], int):
                                if (current[0] >= r1 and
                                    current[0] < r2 and
                                    current[1] >= c1 and
                                    current[1] < c2):
                                    set_curr = True
                            elif current[0] == "column":
                                if (current[1] >= c1 and
                                    current[1] < c2):
                                    set_curr = True
                            elif current[0] == "row":
                                if (current[1] >= r1 and
                                    current[1] < r2):
                                    set_curr = True
                        self.delete(f"{r1}_{c1}_{r2}_{c2}")
                        self.RI.delete(f"{r1}_{c1}_{r2}_{c2}")
                        self.CH.delete(f"{r1}_{c1}_{r2}_{c2}")
                        deleted_boxes[(r1, c1, r2, c2)] = "cells"
            if set_curr:
                try:
                    deleted_boxes[tuple(int(e) for e in self.get_tags_of_current()[1].split("_") if e)] = "cells"
                except:
                    pass
                self.delete_current()
                self.set_current_to_last()
            deselected = ("deselect_cell", tuple(deleted_boxes.items()))
        if redraw:
            self.main_table_redraw_grid_and_text(redraw_header = True, redraw_row_index = True)
        if self.deselection_binding_func is not None:
            self.deselection_binding_func(deselected)

    def page_UP(self, event = None):
        if not self.arrowkeys_enabled:
            return
        height = self.winfo_height()
        top = self.canvasy(0)
        scrollto = top - height
        if scrollto < 0:
            scrollto = 0
        args = ("moveto", scrollto / (self.row_positions[-1] + 100))
        self.yview(*args)
        self.RI.yview(*args)
        self.main_table_redraw_grid_and_text(redraw_row_index = True)

    def page_DOWN(self, event = None):
        if not self.arrowkeys_enabled:
            return
        height = self.winfo_height()
        top = self.canvasy(0)
        scrollto = top + height
        end = self.row_positions[-1]
        if scrollto > end  + 100:
            scrollto = end
        args = ("moveto", scrollto / (end + 100))
        self.yview(*args)
        self.RI.yview(*args)
        self.main_table_redraw_grid_and_text(redraw_row_index = True)
        
    def arrowkey_UP(self, event = None):
        currently_selected = self.currently_selected()
        if not currently_selected or not self.arrowkeys_enabled:
            return
        if currently_selected[0] == "row":
            r = currently_selected[1]
            if r != 0 and self.RI.row_selection_enabled:
                if self.cell_is_completely_visible(r = r - 1, c = 0):
                    self.RI.select_row(r - 1, redraw = True)
                else:
                    self.RI.select_row(r - 1)
                    self.see(r - 1, 0, keep_xscroll = True, check_cell_visibility = False)
        elif isinstance(currently_selected[0],int):
            r = currently_selected[0]
            c = currently_selected[1]
            if r == 0 and self.CH.col_selection_enabled:
                if self.cell_is_completely_visible(r = r, c = 0):
                    self.CH.select_col(c, redraw = True)
                else:
                    self.CH.select_col(c)
                    self.see(r, c, keep_xscroll = True, check_cell_visibility = False)
            elif r != 0 and (self.single_selection_enabled or self.toggle_selection_enabled):
                if self.cell_is_completely_visible(r = r - 1, c = c):
                    self.select_cell(r - 1, c, redraw = True)
                else:
                    self.select_cell(r - 1, c)
                    self.see(r - 1, c, keep_xscroll = True, check_cell_visibility = False)
                
    def arrowkey_RIGHT(self, event = None):
        currently_selected = self.currently_selected()
        if not currently_selected or not self.arrowkeys_enabled:
            return
        if currently_selected[0] == "row":
            r = currently_selected[1]
            if self.single_selection_enabled or self.toggle_selection_enabled:
                if self.cell_is_completely_visible(r = r, c = 0):
                    self.select_cell(r, 0, redraw = True)
                else:
                    self.select_cell(r, 0)
                    self.see(r, 0, keep_yscroll = True, bottom_right_corner = True, check_cell_visibility = False)
        elif currently_selected[0] == "column":
            c = currently_selected[1]
            if c < len(self.col_positions) - 2 and self.CH.col_selection_enabled:
                if self.cell_is_completely_visible(r = 0, c = c + 1):
                    self.CH.select_col(c + 1, redraw = True)
                else:
                    self.CH.select_col(c + 1)
                    self.see(0, c + 1, keep_yscroll = True, bottom_right_corner = True, check_cell_visibility = False)
        elif isinstance(currently_selected[0], int):
            r = currently_selected[0]
            c = currently_selected[1]
            if c < len(self.col_positions) - 2 and (self.single_selection_enabled or self.toggle_selection_enabled):
                if self.cell_is_completely_visible(r = r, c = c + 1):
                    self.select_cell(r, c + 1, redraw =True)
                else:
                    self.select_cell(r, c + 1)
                    self.see(r, c + 1, keep_yscroll = True, bottom_right_corner = True, check_cell_visibility = False)

    def arrowkey_DOWN(self, event = None):
        currently_selected = self.currently_selected()
        if not currently_selected or not self.arrowkeys_enabled:
            return
        if currently_selected[0] == "row":
            r = currently_selected[1]
            if r < len(self.row_positions) - 2 and self.RI.row_selection_enabled:
                if self.cell_is_completely_visible(r = r + 1, c = 0):
                    self.RI.select_row(r + 1, redraw = True)
                else:
                    self.RI.select_row(r + 1)
                    self.see(r + 1, 0, keep_xscroll = True, bottom_right_corner = True, check_cell_visibility = False)
        elif currently_selected[0] == "column":
            c = currently_selected[1]
            if self.single_selection_enabled or self.toggle_selection_enabled:
                if self.cell_is_completely_visible(r = 0, c = c):
                    self.select_cell(0, c, redraw = True)
                else:
                    self.select_cell(0, c)
                    self.see(0, c, keep_xscroll = True, bottom_right_corner = True, check_cell_visibility = False)
        elif isinstance(currently_selected[0],int):
            r = currently_selected[0]
            c = currently_selected[1]
            if r < len(self.row_positions) - 2 and (self.single_selection_enabled or self.toggle_selection_enabled):
                if self.cell_is_completely_visible(r = r + 1, c = c):
                    self.select_cell(r + 1, c, redraw = True)
                else:
                    self.select_cell(r + 1, c)
                    self.see(r + 1, c, keep_xscroll = True, bottom_right_corner = True, check_cell_visibility = False)
                    
    def arrowkey_LEFT(self, event = None):
        currently_selected = self.currently_selected()
        if not currently_selected or not self.arrowkeys_enabled:
            return
        if currently_selected[0] == "column":
            c = currently_selected[1]
            if c != 0 and self.CH.col_selection_enabled:
                if self.cell_is_completely_visible(r = 0, c = c - 1):
                    self.CH.select_col(c - 1, redraw = True)
                else:
                    self.CH.select_col(c - 1)
                    self.see(0, c - 1, keep_yscroll = True, bottom_right_corner = True, check_cell_visibility = False)
        elif isinstance(currently_selected[0], int):
            r = currently_selected[0]
            c = currently_selected[1]
            if c == 0 and self.RI.row_selection_enabled:
                if self.cell_is_completely_visible(r = r, c = 0):
                    self.RI.select_row(r, redraw = True)
                else:
                    self.RI.select_row(r)
                    self.see(r, c, keep_yscroll = True, check_cell_visibility = False)
            elif c != 0 and (self.single_selection_enabled or self.toggle_selection_enabled):
                if self.cell_is_completely_visible(r = r, c = c - 1):
                    self.select_cell(r, c - 1, redraw = True)
                else:
                    self.select_cell(r, c - 1)
                    self.see(r, c - 1, keep_yscroll = True, check_cell_visibility = False)

    def edit_bindings(self, enable = True, key = None):
        if key is None or key == "copy":
            if enable:
                self.bind("<Control-c>", self.ctrl_c)
                self.bind("<Control-C>", self.ctrl_c)
                self.RI.bind("<Control-c>", self.ctrl_c)
                self.RI.bind("<Control-C>", self.ctrl_c)
                self.CH.bind("<Control-c>", self.ctrl_c)
                self.CH.bind("<Control-C>", self.ctrl_c)
                self.copy_enabled = True
            else:
                self.unbind("<Control-c>")
                self.unbind("<Control-C>")
                self.RI.unbind("<Control-c>")
                self.RI.unbind("<Control-C>")
                self.CH.unbind("<Control-c>")
                self.CH.unbind("<Control-C>")
                self.copy_enabled = False
        if key is None or key == "cut":
            if enable:
                self.bind("<Control-x>", self.ctrl_x)
                self.bind("<Control-X>", self.ctrl_x)
                self.RI.bind("<Control-x>", self.ctrl_x)
                self.RI.bind("<Control-X>", self.ctrl_x)
                self.CH.bind("<Control-x>", self.ctrl_x)
                self.CH.bind("<Control-X>", self.ctrl_x)
                self.cut_enabled = True
            else:
                self.unbind("<Control-x>")
                self.unbind("<Control-X>")
                self.RI.unbind("<Control-x>")
                self.RI.unbind("<Control-X>")
                self.CH.unbind("<Control-x>")
                self.CH.unbind("<Control-X>")
                self.cut_enabled = False
        if key is None or key == "paste":
            if enable:
                self.bind("<Control-v>", self.ctrl_v)
                self.bind("<Control-V>", self.ctrl_v)
                self.RI.bind("<Control-v>", self.ctrl_v)
                self.RI.bind("<Control-V>", self.ctrl_v)
                self.CH.bind("<Control-v>", self.ctrl_v)
                self.CH.bind("<Control-V>", self.ctrl_v)
                self.paste_enabled = True
            else:
                self.unbind("<Control-v>")
                self.unbind("<Control-V>")
                self.RI.unbind("<Control-v>")
                self.RI.unbind("<Control-V>")
                self.CH.unbind("<Control-v>")
                self.CH.unbind("<Control-V>")
                self.paste_enabled = False
        if key is None or key == "undo":
            if enable:
                self.undo_enabled = True
                self.bind("<Control-z>", self.ctrl_z)
                self.bind("<Control-Z>", self.ctrl_z)
                self.RI.bind("<Control-z>", self.ctrl_z)
                self.RI.bind("<Control-Z>", self.ctrl_z)
                self.CH.bind("<Control-z>", self.ctrl_z)
                self.CH.bind("<Control-Z>", self.ctrl_z)
            else:
                self.undo_enabled = False
                self.unbind("<Control-z>")
                self.unbind("<Control-Z>")
                self.RI.unbind("<Control-z>")
                self.RI.unbind("<Control-Z>")
                self.CH.unbind("<Control-z>")
                self.CH.unbind("<Control-Z>")
        if key is None or key == "delete":
            if enable:
                self.bind("<Delete>", self.delete_key)
                self.RI.bind("<Delete>", self.delete_key)
                self.CH.bind("<Delete>", self.delete_key)
                self.delete_key_enabled = True
            else:
                self.unbind("<Delete>")
                self.RI.unbind("<Delete>")
                self.CH.unbind("<Delete>")
                self.delete_key_enabled = False
        if key is None or key == "edit_cell":
            if enable:
                self.bind_cell_edit(True)
            else:
                self.bind_cell_edit(False)

    def create_rc_menus(self):
        self.rc_popup_menu = tk.Menu(self, tearoff = 0, background = self.popup_menu_bg)
        self.CH.ch_rc_popup_menu = tk.Menu(self.CH, tearoff = 0, background = self.popup_menu_bg)
        self.RI.ri_rc_popup_menu = tk.Menu(self.RI, tearoff = 0, background = self.popup_menu_bg)
        if self.cut_enabled:
            self.rc_popup_menu.add_command(label = "Cut Ctrl+X",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                           command = self.ctrl_x)
            #self.rc_popup_menu.add_separator()
            self.CH.ch_rc_popup_menu.add_command(label = "Cut Contents Ctrl+X",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                               command = self.ctrl_x)
            #self.CH.ch_rc_popup_menu.add_separator()
            self.RI.ri_rc_popup_menu.add_command(label = "Cut Contents Ctrl+X",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                                 command = self.ctrl_x)
            #self.RI.ri_rc_popup_menu.add_separator()
        if self.copy_enabled:
            self.rc_popup_menu.add_command(label = "Copy Ctrl+C",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                           command = self.ctrl_c)
            #self.rc_popup_menu.add_separator()
            self.CH.ch_rc_popup_menu.add_command(label = "Copy Contents Ctrl+C",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                                 command = self.ctrl_c)
            #self.CH.ch_rc_popup_menu.add_separator()
            self.RI.ri_rc_popup_menu.add_command(label = "Copy Contents Ctrl+C",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                                 command = self.ctrl_c)
            #self.RI.ri_rc_popup_menu.add_separator()
        if self.paste_enabled:
            self.rc_popup_menu.add_command(label = "Paste Ctrl+V",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                           command = self.ctrl_v)
            #self.rc_popup_menu.add_separator()
            self.CH.ch_rc_popup_menu.add_command(label = "Paste Ctrl+V",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                                 command = self.ctrl_v)
            #self.CH.ch_rc_popup_menu.add_separator()
            self.RI.ri_rc_popup_menu.add_command(label = "Paste Ctrl+V",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                                 command = self.ctrl_v)
            #self.RI.ri_rc_popup_menu.add_separator()
        if self.delete_key_enabled:
            self.rc_popup_menu.add_command(label = "Delete",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                           command = self.delete_key)
            self.CH.ch_rc_popup_menu.add_command(label = "Clear Contents",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                                 command = self.delete_key)
            #self.CH.ch_rc_popup_menu.add_separator()
            self.RI.ri_rc_popup_menu.add_command(label = "Clear Contents",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                               command = self.delete_key)
            #self.RI.ri_rc_popup_menu.add_separator()
        if self.rc_delete_column_enabled:
            self.CH.ch_rc_popup_menu.add_command(label = "Delete Columns",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                                 command = self.del_cols_rc)
            #self.CH.ch_rc_popup_menu.add_separator()
        if self.rc_insert_column_enabled:
            self.CH.ch_rc_popup_menu.add_command(label = "Insert Column",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                                 command = self.insert_col_rc)
        if self.rc_delete_row_enabled:
            self.RI.ri_rc_popup_menu.add_command(label = "Delete Rows",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                                 command = self.del_rows_rc)
            #self.RI.ri_rc_popup_menu.add_separator()
        if self.rc_insert_row_enabled:
            self.RI.ri_rc_popup_menu.add_command(label = "Insert Row",
                                           font = self.popup_menu_font,
                                           foreground = self.popup_menu_fg,
                                           background = self.popup_menu_bg,
                                           activebackground = self.popup_menu_highlight_bg,
                                           activeforeground = self.popup_menu_highlight_fg,
                                                 command = self.insert_row_rc)

    def bind_cell_edit(self, enable = True):
        if enable:
            for c in chain(lowercase_letters, uppercase_letters):
                self.bind(f"<{c}>", self.edit_cell_)
            for c in chain(numbers, symbols, other_symbols):
                self.bind(c, self.edit_cell_)
            self.bind("<F2>", self.edit_cell_)
            self.bind("<Double-Button-1>", self.edit_cell_)
            self.bind("<Return>", self.edit_cell_)
        else:
            for c in chain(lowercase_letters, uppercase_letters):
                self.unbind(f"<{c}>")
            for c in chain(numbers, symbols, other_symbols):
                self.unbind(c)
            self.unbind("<F2>")
            self.unbind("<Double-Button-1>")
            self.unbind("<Return>")

    def enable_bindings(self, bindings):
        if isinstance(bindings,(list, tuple)):
            for binding in bindings:
                self.enable_bindings_internal(binding.lower())
        elif isinstance(bindings, str):
            self.enable_bindings_internal(bindings.lower())

    def enable_bindings_internal(self, binding):
        if binding == "enable_all":
            self.single_selection_enabled = True
            self.toggle_selection_enabled = False
            self.drag_selection_enabled = True
            self.bind("<Control-a>", self.select_all)
            self.bind("<Control-A>", self.select_all)
            self.RI.bind("<Control-a>", self.select_all)
            self.RI.bind("<Control-A>", self.select_all)
            self.CH.bind("<Control-a>", self.select_all)
            self.CH.bind("<Control-A>", self.select_all)
            self.CH.enable_bindings("column_width_resize")
            self.CH.enable_bindings("column_select")
            self.CH.enable_bindings("column_height_resize")
            self.CH.enable_bindings("drag_and_drop")
            self.CH.enable_bindings("double_click_column_resize")
            self.RI.enable_bindings("row_height_resize")
            self.RI.enable_bindings("double_click_row_resize")
            self.RI.enable_bindings("row_width_resize")
            self.RI.enable_bindings("row_select")
            self.RI.enable_bindings("drag_and_drop")
            self.bind_arrowkeys()
            self.edit_bindings(True)
            self.rc_delete_column_enabled = True
            self.rc_delete_row_enabled = True
            self.rc_insert_column_enabled = True
            self.rc_insert_row_enabled = True
            self.rc_popup_menus_enabled = True
            self.rc_select_enabled = True
        elif binding in ("single", "single_selection_mode", "single_select"):
            self.single_selection_enabled = True
            self.toggle_selection_enabled = False
        elif binding in ("toggle", "toggle_selection_mode", "toggle_select"):
            self.toggle_selection_enabled = True
            self.single_selection_enabled = False
        elif binding == "drag_select":
            self.drag_selection_enabled = True
            self.bind("<Control-a>", self.select_all)
            self.bind("<Control-A>", self.select_all)
            self.RI.bind("<Control-a>", self.select_all)
            self.RI.bind("<Control-A>", self.select_all)
            self.CH.bind("<Control-a>", self.select_all)
            self.CH.bind("<Control-A>", self.select_all)
        elif binding == "column_width_resize":
            self.CH.enable_bindings("column_width_resize")
        elif binding == "column_select":
            self.CH.enable_bindings("column_select")
        elif binding == "column_height_resize":
            self.CH.enable_bindings("column_height_resize")
        elif binding == "column_drag_and_drop":
            self.CH.enable_bindings("drag_and_drop")
        elif binding == "double_click_column_resize":
            self.CH.enable_bindings("double_click_column_resize")
        elif binding == "row_height_resize":
            self.RI.enable_bindings("row_height_resize")
        elif binding == "double_click_row_resize":
            self.RI.enable_bindings("double_click_row_resize")
        elif binding == "row_width_resize":
            self.RI.enable_bindings("row_width_resize")
        elif binding == "row_select":
            self.RI.enable_bindings("row_select")
        elif binding == "row_drag_and_drop":
            self.RI.enable_bindings("drag_and_drop")
        elif binding == "arrowkeys":
            self.bind_arrowkeys()
        elif binding == "edit_bindings":
            self.edit_bindings(True)
        elif binding == "rc_delete_column":
            self.rc_delete_column_enabled = True
            self.rc_popup_menus_enabled = True
            self.rc_select_enabled = True
        elif binding == "rc_delete_row":
            self.rc_delete_row_enabled = True
            self.rc_popup_menus_enabled = True
            self.rc_select_enabled = True
        elif binding == "rc_insert_column":
            self.rc_insert_column_enabled = True
            self.rc_popup_menus_enabled = True
            self.rc_select_enabled = True
        elif binding == "rc_insert_row":
            self.rc_insert_row_enabled = True
            self.rc_popup_menus_enabled = True
            self.rc_select_enabled = True
        elif binding == "copy":
            self.edit_bindings(True, "copy")
        elif binding == "cut":
            self.edit_bindings(True, "cut")
        elif binding == "paste":
            self.edit_bindings(True, "paste")
        elif binding == "delete":
            self.edit_bindings(True, "delete")
        elif binding in ("right_click_popup_menu", "rc_popup_menu"):
            self.rc_popup_menus_enabled = True
            self.rc_select_enabled = True
        elif binding in ("right_click_select", "rc_select"):
            self.rc_select_enabled = True
        elif binding == "undo":
            self.edit_bindings(True, "undo")
        elif binding == "edit_cell":
            self.edit_bindings(True, "edit_cell")
        self.create_rc_menus()
        
    def disable_bindings(self, bindings):
        if isinstance(bindings,(list, tuple)):
            for binding in bindings:
                self.disable_bindings_internal(binding)
        elif isinstance(bindings, str):
            self.disable_bindings_internal(bindings)

    def disable_bindings_internal(self, binding):
        if binding == "disable_all":
            self.single_selection_enabled = False
            self.toggle_selection_enabled = False
            self.drag_selection_enabled = False
            self.unbind("<Control-a>")
            self.unbind("<Control-A>")
            self.RI.unbind("<Control-a>")
            self.RI.unbind("<Control-A>")
            self.CH.unbind("<Control-a>")
            self.CH.unbind("<Control-A>")
            self.CH.disable_bindings("column_width_resize")
            self.CH.disable_bindings("column_select")
            self.CH.disable_bindings("column_height_resize")
            self.CH.disable_bindings("drag_and_drop")
            self.CH.disable_bindings("double_click_column_resize")
            self.RI.disable_bindings("row_height_resize")
            self.RI.disable_bindings("double_click_row_resize")
            self.RI.disable_bindings("row_width_resize")
            self.RI.disable_bindings("row_select")
            self.RI.disable_bindings("drag_and_drop")
            self.unbind_arrowkeys()
            self.edit_bindings(False)
            self.rc_delete_column_enabled = False
            self.rc_delete_row_enabled = False
            self.rc_insert_column_enabled = False
            self.rc_insert_row_enabled = False
            self.rc_popup_menus_enabled = False
            self.rc_select_enabled = False
        elif binding in ("single", "single_selection_mode", "single_select"):
            self.single_selection_enabled = False
        elif binding in ("toggle", "toggle_selection_mode", "toggle_select"):
            self.toggle_selection_enabled = False
        elif binding == "drag_select":
            self.drag_selection_enabled = False
            self.unbind("<Control-a>")
            self.unbind("<Control-A>")
            self.RI.unbind("<Control-a>")
            self.RI.unbind("<Control-A>")
            self.CH.unbind("<Control-a>")
            self.CH.unbind("<Control-A>")
        elif binding == "column_width_resize":
            self.CH.disable_bindings("column_width_resize")
        elif binding == "column_select":
            self.CH.disable_bindings("column_select")
        elif binding == "column_height_resize":
            self.CH.disable_bindings("column_height_resize")
        elif binding == "column_drag_and_drop":
            self.CH.disable_bindings("drag_and_drop")
        elif binding == "double_click_column_resize":
            self.CH.disable_bindings("double_click_column_resize")
        elif binding == "row_height_resize":
            self.RI.disable_bindings("row_height_resize")
        elif binding == "double_click_row_resize":
            self.RI.disable_bindings("double_click_row_resize")
        elif binding == "row_width_resize":
            self.RI.disable_bindings("row_width_resize")
        elif binding == "row_select":
            self.RI.disable_bindings("row_select")
        elif binding == "row_drag_and_drop":
            self.RI.disable_bindings("drag_and_drop")
        elif binding == "arrowkeys":
            self.unbind_arrowkeys()
        elif binding == "rc_delete_column":
            self.rc_delete_column_enabled = False
        elif binding == "rc_delete_row":
            self.rc_delete_row_enabled = False
        elif binding == "rc_insert_column":
            self.rc_insert_column_enabled = False
        elif binding == "rc_insert_row":
            self.rc_insert_row_enabled = False
        elif binding == "edit_bindings":
            self.edit_bindings(False)
        elif binding == "copy":
            self.edit_bindings(False, "copy")
        elif binding == "cut":
            self.edit_bindings(False, "cut")
        elif binding == "paste":
            self.edit_bindings(False, "paste")
        elif binding == "delete":
            self.edit_bindings(False, "delete")
        elif binding in ("right_click_popup_menu", "rc_popup_menu"):
            self.rc_popup_menus_enabled = False
        elif binding in ("right_click_select", "rc_select"):
            self.rc_select_enabled = False
        elif binding == "undo":
            self.edit_bindings(False, "undo")
        elif binding == "edit_cell":
            self.edit_bindings(False, "edit_cell")
        self.create_rc_menus()

    def reset_mouse_motion_creations(self, event = None):
        self.config(cursor = "")
        self.RI.config(cursor = "")
        self.CH.config(cursor = "")
        self.RI.rsz_w = None
        self.RI.rsz_h = None
        self.CH.rsz_w = None
        self.CH.rsz_h = None
    
    def mouse_motion(self, event):
        if (
            not self.RI.currently_resizing_height and
            not self.RI.currently_resizing_width and
            not self.CH.currently_resizing_height and
            not self.CH.currently_resizing_width
            ):
            mouse_over_resize = False
            x = self.canvasx(event.x)
            y = self.canvasy(event.y)
            if self.RI.width_resizing_enabled and not mouse_over_resize:
                try:
                    x1, y1, x2, y2 = self.row_width_resize_bbox[0], self.row_width_resize_bbox[1], self.row_width_resize_bbox[2], self.row_width_resize_bbox[3]
                    if x >= x1 and y >= y1 and x <= x2 and y <= y2:
                        self.config(cursor = "sb_h_double_arrow")
                        self.RI.config(cursor = "sb_h_double_arrow")
                        self.RI.rsz_w = True
                        mouse_over_resize = True
                except:
                    pass
            if self.CH.height_resizing_enabled and not mouse_over_resize:
                try:
                    x1, y1, x2, y2 = self.header_height_resize_bbox[0], self.header_height_resize_bbox[1], self.header_height_resize_bbox[2], self.header_height_resize_bbox[3]
                    if x >= x1 and y >= y1 and x <= x2 and y <= y2:
                        self.config(cursor = "sb_v_double_arrow")
                        self.CH.config(cursor = "sb_v_double_arrow")
                        self.CH.rsz_h = True
                        mouse_over_resize = True
                except:
                    pass
            if not mouse_over_resize:
                self.reset_mouse_motion_creations()
        if self.extra_motion_func is not None:
            self.extra_motion_func(event)

    def rc(self, event = None):
        self.focus_set()
        if self.identify_col(x = event.x, allow_end = False) is None or self.identify_row(y = event.y, allow_end = False) is None:
            self.deselect("all")
        elif self.single_selection_enabled and all(v is None for v in (self.RI.rsz_h, self.RI.rsz_w, self.CH.rsz_h, self.CH.rsz_w)):
            r = self.identify_row(y = event.y)
            c = self.identify_col(x = event.x)
            if r < len(self.row_positions) - 1 and c < len(self.col_positions) - 1:
                if self.is_col_selected(c) and self.rc_popup_menus_enabled:
                    self.CH.ch_rc_popup_menu.tk_popup(event.x_root, event.y_root)
                elif self.is_row_selected(r) and self.rc_popup_menus_enabled:
                    self.RI.ri_rc_popup_menu.tk_popup(event.x_root, event.y_root)
                elif self.is_cell_selected(r, c) and self.rc_popup_menus_enabled:
                    self.rc_popup_menu.tk_popup(event.x_root, event.y_root)
                else:
                    if self.rc_select_enabled:
                        self.select_cell(r, c, redraw = True)
                    if self.rc_popup_menus_enabled:
                        self.rc_popup_menu.tk_popup(event.x_root, event.y_root)
        elif self.toggle_selection_enabled and all(v is None for v in (self.RI.rsz_h, self.RI.rsz_w, self.CH.rsz_h, self.CH.rsz_w)):
            r = self.identify_row(y = event.y)
            c = self.identify_col(x = event.x)
            if r < len(self.row_positions) - 1 and c < len(self.col_positions) - 1:
                if self.is_col_selected(c) and self.rc_popup_menus_enabled:
                    self.CH.ch_rc_popup_menu.tk_popup(event.x_root, event.y_root)
                elif self.is_row_selected(r) and self.rc_popup_menus_enabled:
                    self.RI.ri_rc_popup_menu.tk_popup(event.x_root, event.y_root)
                elif self.is_cell_selected(r, c) and self.rc_popup_menus_enabled:
                    self.rc_popup_menu.tk_popup(event.x_root, event.y_root)
                else:
                    if self.rc_select_enabled:
                        self.toggle_select_cell(r, c, redraw = True)
                    if self.rc_popup_menus_enabled:
                        self.rc_popup_menu.tk_popup(event.x_root, event.y_root)
        if self.extra_rc_func is not None:
            self.extra_rc_func(event)

    def b1_press(self, event = None):
        self.focus_set()
        x1, y1, x2, y2 = self.get_canvas_visible_area()
        if self.identify_col(x = event.x, allow_end = False) is None or self.identify_row(y = event.y, allow_end = False) is None:
            self.deselect("all")
        if self.single_selection_enabled and all(v is None for v in (self.RI.rsz_h, self.RI.rsz_w, self.CH.rsz_h, self.CH.rsz_w)):
            r = self.identify_row(y = event.y)
            c = self.identify_col(x = event.x)
            if r < len(self.row_positions) - 1 and c < len(self.col_positions) - 1:
                self.select_cell(r, c, redraw = True)
        elif self.toggle_selection_enabled and all(v is None for v in (self.RI.rsz_h, self.RI.rsz_w, self.CH.rsz_h, self.CH.rsz_w)):
            r = self.identify_row(y = event.y)
            c = self.identify_col(x = event.x)
            if r < len(self.row_positions) - 1 and c < len(self.col_positions) - 1:
                self.toggle_select_cell(r, c, redraw = True)
        elif self.RI.width_resizing_enabled and self.RI.rsz_h is None and self.RI.rsz_w == True:
            self.RI.currently_resizing_width = True
            self.new_row_width = self.RI.current_width + event.x
            x = self.canvasx(event.x)
            self.create_line(x, y1, x, y2, width = 1, fill = self.RI.resizing_line_color, tag = "rwl")
        elif self.CH.height_resizing_enabled and self.CH.rsz_w is None and self.CH.rsz_h == True:
            self.CH.currently_resizing_height = True
            self.new_header_height = self.CH.current_height + event.y
            y = self.canvasy(event.y)
            self.create_line(x1, y, x2, y, width = 1, fill = self.RI.resizing_line_color, tag = "rhl")
        if self.extra_b1_press_func is not None:
            self.extra_b1_press_func(event)

    def shift_b1_press(self, event = None):
        if self.drag_selection_enabled and all(v is None for v in (self.RI.rsz_h, self.RI.rsz_w, self.CH.rsz_h, self.CH.rsz_w)):
            rowsel = int(self.identify_row(y = event.y))
            colsel = int(self.identify_col(x = event.x))
            if rowsel < len(self.row_positions) - 1 and colsel < len(self.col_positions) - 1:
                currently_selected = self.currently_selected()
                if currently_selected and isinstance(currently_selected[0], int):
                    min_r = currently_selected[0]
                    min_c = currently_selected[1]
                    self.delete_selection_rects(delete_current = False)
                    if rowsel >= min_r and colsel >= min_c:
                        self.create_selected(min_r, min_c, rowsel + 1, colsel + 1)
                    elif rowsel >= min_r and min_c >= colsel:
                        self.create_selected(min_r, colsel, rowsel + 1, min_c + 1)
                    elif min_r >= rowsel and colsel >= min_c:
                        self.create_selected(rowsel, min_c, min_r + 1, colsel + 1)
                    elif min_r >= rowsel and min_c >= colsel:
                        self.create_selected(rowsel, colsel, min_r + 1, min_c + 1)
                else:
                    self.select_cell(rowsel, colsel, redraw = False)
                self.main_table_redraw_grid_and_text(redraw_header = True, redraw_row_index = True)
                if self.shift_selection_binding_func is not None:
                    self.shift_selection_binding_func(("shift_select_cells", ) + tuple(int(e) for e in self.gettags(self.find_withtag("CellSelectFill"))[1].split("_") if e))
        
    def b1_motion(self, event):
        x1, y1, x2, y2 = self.get_canvas_visible_area()
        if self.drag_selection_enabled and all(v is None for v in (self.RI.rsz_h, self.RI.rsz_w, self.CH.rsz_h, self.CH.rsz_w)):
            end_row = self.identify_row(y = event.y)
            end_col = self.identify_col(x = event.x)
            currently_selected = self.currently_selected()
            if end_row < len(self.row_positions) - 1 and end_col < len(self.col_positions) - 1 and currently_selected and isinstance(currently_selected[0], int):
                start_row = currently_selected[0]
                start_col = currently_selected[1]
                self.delete_selection_rects(delete_current = False)
                if end_row >= start_row and end_col >= start_col:
                    self.create_selected(start_row, start_col, end_row + 1, end_col + 1)
                elif end_row >= start_row and end_col < start_col:
                    self.create_selected(start_row, end_col, end_row + 1, start_col + 1)
                elif end_row < start_row and end_col >= start_col:
                    self.create_selected(end_row, start_col, start_row + 1, end_col + 1)
                elif end_row < start_row and end_col < start_col:
                    self.create_selected(end_row, end_col, start_row + 1, start_col + 1)
                if self.drag_selection_binding_func is not None:
                    self.drag_selection_binding_func(("drag_select_cells", ) + tuple(int(e) for e in self.gettags(self.find_withtag("CellSelectFill"))[1].split("_") if e))
            if event.x > self.winfo_width():
                try:
                    self.xview_scroll(1, "units")
                    self.CH.xview_scroll(1, "units")
                except:
                    pass
            elif event.x < 0:
                try:
                    self.xview_scroll(-1, "units")
                    self.CH.xview_scroll(-1, "units")
                except:
                    pass
            if event.y > self.winfo_height():
                try:
                    self.yview_scroll(1, "units")
                    self.RI.yview_scroll(1, "units")
                except:
                    pass
            elif event.y < 0:
                try:
                    self.yview_scroll(-1, "units")
                    self.RI.yview_scroll(-1, "units")
                except:
                    pass
            self.main_table_redraw_grid_and_text(redraw_header = True, redraw_row_index = True)
        elif self.RI.width_resizing_enabled and self.RI.rsz_w is not None and self.RI.currently_resizing_width:
            self.RI.delete("rwl")
            self.delete("rwl")
            if event.x >= 0:
                x = self.canvasx(event.x)
                self.new_row_width = self.RI.current_width + event.x
                self.create_line(x, y1, x, y2, width = 1, fill = self.RI.resizing_line_color, tag = "rwl")
            else:
                x = self.RI.current_width + event.x
                if x < self.min_cw:
                    x = int(self.min_cw)
                self.new_row_width = x
                self.RI.create_line(x, y1, x, y2, width = 1, fill = self.RI.resizing_line_color, tag = "rwl")
        elif self.CH.height_resizing_enabled and self.CH.rsz_h is not None and self.CH.currently_resizing_height:
            self.CH.delete("rhl")
            self.delete("rhl")
            if event.y >= 0:
                y = self.canvasy(event.y)
                self.new_header_height = self.CH.current_height + event.y
                self.create_line(x1, y, x2, y, width = 1, fill = self.RI.resizing_line_color, tag = "rhl")
            else:
                y = self.CH.current_height + event.y
                if y < self.hdr_min_rh:
                    y = int(self.hdr_min_rh)
                self.new_header_height = y
                self.CH.create_line(x1, y, x2, y, width = 1, fill = self.RI.resizing_line_color, tag = "rhl")
        if self.extra_b1_motion_func is not None:
            self.extra_b1_motion_func(event)
        
    def b1_release(self, event = None):
        if self.RI.width_resizing_enabled and self.RI.rsz_w is not None and self.RI.currently_resizing_width:
            self.delete("rwl")
            self.RI.delete("rwl")
            self.RI.currently_resizing_width = False
            self.RI.set_width(self.new_row_width, set_TL = True)
            self.main_table_redraw_grid_and_text(redraw_header = True, redraw_row_index = True)
        elif self.CH.height_resizing_enabled and self.CH.rsz_h is not None and self.CH.currently_resizing_height:
            self.delete("rhl")
            self.CH.delete("rhl")
            self.CH.currently_resizing_height = False
            self.CH.set_height(self.new_header_height, set_TL = True)
            self.main_table_redraw_grid_and_text(redraw_header = True, redraw_row_index = True)
        self.RI.rsz_w = None
        self.CH.rsz_h = None
        self.mouse_motion(event)
        if self.extra_b1_release_func is not None:
            self.extra_b1_release_func(event)

    def double_b1(self, event = None):
        self.focus_set()
        x1, y1, x2, y2 = self.get_canvas_visible_area()
        if self.identify_col(x = event.x, allow_end = False) is None or self.identify_row(y = event.y, allow_end = False) is None:
            self.deselect("all")
        elif self.single_selection_enabled and all(v is None for v in (self.RI.rsz_h, self.RI.rsz_w, self.CH.rsz_h, self.CH.rsz_w)):
            r = self.identify_row(y = event.y)
            c = self.identify_col(x = event.x)
            if r < len(self.row_positions) - 1 and c < len(self.col_positions) - 1:
                self.select_cell(r, c, redraw = True)
        elif self.toggle_selection_enabled and all(v is None for v in (self.RI.rsz_h, self.RI.rsz_w, self.CH.rsz_h, self.CH.rsz_w)):
            r = self.identify_row(y = event.y)
            c = self.identify_col(x = event.x)
            if r < len(self.row_positions) - 1 and c < len(self.col_positions) - 1:
                self.toggle_select_cell(r, c, redraw = True)
        if self.extra_double_b1_func is not None:
            self.extra_double_b1_func(event)

    def identify_row(self, event = None, y = None, allow_end = True):
        if event is None:
            y2 = self.canvasy(y)
        elif y is None:
            y2 = self.canvasy(event.y)
        r = bisect.bisect_left(self.row_positions, y2)
        if r != 0:
            r -= 1
        if not allow_end:
            if r >= len(self.row_positions) - 1:
                return None
        return r

    def identify_col(self, event = None, x = None, allow_end = True):
        if event is None:
            x2 = self.canvasx(x)
        elif x is None:
            x2 = self.canvasx(event.x)
        c = bisect.bisect_left(self.col_positions, x2)
        if c != 0:
            c -= 1
        if not allow_end:
            if c >= len(self.col_positions) - 1:
                return None
        return c

    def GetCellCoords(self, event = None, r = None, c = None, sel = False):
        # event takes priority as parameter
        if event is not None:
            r = self.identify_row(event)
            c = self.identify_col(event)
        elif r is not None and c is not None:
            if sel:
                return self.col_positions[c] + 1,self.row_positions[r] + 1, self.col_positions[c + 1], self.row_positions[r + 1]
            else:
                return self.col_positions[c], self.row_positions[r], self.col_positions[c + 1], self.row_positions[r + 1]

    def set_xviews(self, *args):
        self.xview(*args)
        self.CH.xview(*args)
        self.main_table_redraw_grid_and_text(redraw_header = True)

    def set_yviews(self, *args):
        self.yview(*args)
        self.RI.yview(*args)
        self.main_table_redraw_grid_and_text(redraw_row_index = True)

    def set_view(self, x_args, y_args):
        self.xview(*x_args)
        self.CH.xview(*x_args)
        self.yview(*y_args)
        self.RI.yview(*y_args)
        self.main_table_redraw_grid_and_text(redraw_row_index = True, redraw_header = True)

    def mousewheel(self, event = None):
        if event.num == 5 or event.delta == -120:
            self.yview_scroll(1, "units")
            self.RI.yview_scroll(1, "units")
        if event.num == 4 or event.delta == 120:
            if self.canvasy(0) <= 0:
                return
            self.yview_scroll(-1, "units")
            self.RI.yview_scroll(-1, "units")
        self.main_table_redraw_grid_and_text(redraw_row_index = True)

    def GetWidthChars(self, width):
        char_w = self.GetTextWidth("_")
        return int(width / char_w)

    def GetTextWidth(self, txt):
        x = self.txt_measure_canvas.create_text(0, 0, text = txt, font = self.my_font)
        b = self.txt_measure_canvas.bbox(x)
        self.txt_measure_canvas.delete(x)
        return b[2] - b[0]

    def GetTextHeight(self, txt):
        x = self.txt_measure_canvas.create_text(0, 0, text = txt, font = self.my_font)
        b = self.txt_measure_canvas.bbox(x)
        self.txt_measure_canvas.delete(x)
        return b[3] - b[1]

    def GetHdrTextWidth(self, txt):
        x = self.txt_measure_canvas.create_text(0, 0, text = txt, font = self.my_hdr_font)
        b = self.txt_measure_canvas.bbox(x)
        self.txt_measure_canvas.delete(x)
        return b[2] - b[0]

    def GetHdrTextHeight(self, txt):
        x = self.txt_measure_canvas.create_text(0, 0, text = txt, font = self.my_hdr_font)
        b = self.txt_measure_canvas.bbox(x)
        self.txt_measure_canvas.delete(x)
        return b[3] - b[1]

    def set_min_cw(self):
        w1 = self.GetHdrTextWidth("XXXX")
        w2 = self.GetTextWidth("XXXX")
        if w1 >= w2:
            self.min_cw = w1
        else:
            self.min_cw = w2
        if self.min_cw > self.CH.max_cw:
            self.CH.max_cw = self.min_cw * 2
        if self.min_cw > self.default_cw:
            self.default_cw = self.min_cw * 2

    def font(self, newfont = None):
        if newfont:
            if (
                not isinstance(newfont, tuple) or
                not isinstance(newfont[0], str) or
                not isinstance(newfont[1], int)
                ):
                raise ValueError("Parameter must be tuple e.g. ('Arial',12,'normal')")
            if len(newfont) > 2:
                raise ValueError("Parameter must be three-tuple")
            else:
                self.my_font = newfont
            self.fnt_fam = newfont[0]
            self.fnt_sze = newfont[1]
            self.fnt_wgt = newfont[2]
            self.set_fnt_help()
        else:
            return self.my_font

    def set_fnt_help(self):
        self.txt_h = self.GetTextHeight("|ZXj*'^")
        self.half_txt_h = ceil(self.txt_h / 2)
        if self.half_txt_h % 2 == 0:
            self.fl_ins = self.half_txt_h + 2
        else:
            self.fl_ins = self.half_txt_h + 3
        self.xtra_lines_increment = int(self.txt_h)
        self.min_rh = self.txt_h + 5
        if self.min_rh < 12:
            self.min_rh = 12
        self.set_min_cw()
        
    def header_font(self, newfont = None):
        if newfont:
            if (
                not isinstance(newfont, tuple) or
                not isinstance(newfont[0], str) or
                not isinstance(newfont[1], int)
                ):
                raise ValueError("Parameter must be tuple e.g. ('Arial',12,'bold')")
            if len(newfont) == 3:
                if not isinstance(newfont[2], str):
                    raise ValueError("Parameter must be tuple e.g. ('Arial',12,'bold')")
            if len(newfont) > 3:
                raise ValueError("Parameter must be three tuple")
            else:
                self.my_hdr_font = newfont
            self.hdr_fnt_fam = newfont[0]
            self.hdr_fnt_sze = newfont[1]
            self.hdr_fnt_wgt = newfont[2]
            self.set_hdr_fnt_help()
        else:
            return self.my_hdr_font

    def set_hdr_fnt_help(self):
        self.hdr_txt_h = self.GetHdrTextHeight("|ZXj*'^")
        self.hdr_half_txt_h = ceil(self.hdr_txt_h / 2)
        if self.hdr_half_txt_h % 2 == 0:
            self.hdr_fl_ins = self.hdr_half_txt_h + 2
        else:
            self.hdr_fl_ins = self.hdr_half_txt_h + 3
        self.hdr_xtra_lines_increment = self.hdr_txt_h
        self.hdr_min_rh = self.hdr_txt_h + 5
        self.set_min_cw()
        self.CH.set_height(self.GetHdrLinesHeight(self.default_hh))

    def data_reference(self, newdataref = None, reset_col_positions = True, reset_row_positions = True, redraw = False, return_id = True):
        if isinstance(newdataref, (list, tuple)):
            self.data_ref = newdataref
            self.undo_storage = deque(maxlen = self.max_undos)
            if reset_col_positions:
                self.reset_col_positions()
            if reset_row_positions:
                self.reset_row_positions()
            if redraw:
                self.main_table_redraw_grid_and_text(redraw_header = True, redraw_row_index = True)
        if return_id:
            return id(self.data_ref)
        else:
            return self.data_ref

    def set_all_cell_sizes_to_text(self):
        min_cw = self.min_cw
        min_rh = self.min_rh
        rhs = defaultdict(lambda: int(min_rh))
        cws = []
        x = self.txt_measure_canvas.create_text(0, 0, text = "", font = self.my_font)
        x2 = self.txt_measure_canvas.create_text(0, 0, text = "", font = self.my_hdr_font)
        itmcon = self.txt_measure_canvas.itemconfig
        itmbbx = self.txt_measure_canvas.bbox
        if self.all_columns_displayed:
            iterable = range(self.total_data_cols())
        else:
            iterable = self.displayed_columns
        if isinstance(self.my_row_index, list):
            for rn in range(self.total_data_rows()):
                try:
                    if isinstance(self.my_row_index[rn], str):
                        txt = self.my_row_index[rn]
                    else:
                        txt = f"{self.my_row_index[rn]}"
                except:
                    txt = ""
                if txt:
                    itmcon(x, text = txt)
                    b = itmbbx(x)
                    h = b[3] - b[1] + 5
                else:
                    h = min_rh
                if h < min_rh:
                    h = int(min_rh)
                elif h > self.RI.max_rh:
                    h = int(self.RI.max_rh)
                if h > rhs[rn]:
                    rhs[rn] = h
        for cn in iterable:
            try:
                txt = self.my_hdrs[cn]
                if txt:
                    itmcon(x2, text = txt)
                    b = itmbbx(x2)
                    w = b[2] - b[0] + 5
                else:
                    w = self.min_cw
            except:
                if self.CH.default_hdr:
                    itmcon(x2, text = f"{num2alpha(cn)}")
                else:
                    itmcon(x2, text = f"{cn}")
                b = itmbbx(x2)
                w = b[2] - b[0] + 5
            for rn, r in enumerate(self.data_ref):
                try:
                    if isinstance(r[cn], str):
                        txt = r[cn]
                    else:
                        txt = f"{r[cn]}"
                except:
                    txt = ""
                if txt:
                    itmcon(x, text = txt)
                    b = itmbbx(x)
                    tw = b[2] - b[0] + 5
                    h = b[3] - b[1] + 5
                else:
                    tw = min_cw
                    h = min_rh
                if tw > w:
                    w = tw
                if h < min_rh:
                    h = int(min_rh)
                elif h > self.RI.max_rh:
                    h = int(self.RI.max_rh)
                if h > rhs[rn]:
                    rhs[rn] = h
            if w < min_cw:
                w = int(min_cw)
            elif w > self.CH.max_cw:
                w = int(self.CH.max_cw)
            cws.append(w)
        self.txt_measure_canvas.delete(x)
        self.txt_measure_canvas.delete(x2)
        self.row_positions = list(accumulate(chain([0], (height for height in rhs.values()))))
        self.col_positions = list(accumulate(chain([0], (width for width in cws))))
        self.recreate_all_selection_boxes()

    def reset_col_positions(self):
        colpos = int(self.default_cw)
        if self.all_columns_displayed:
            self.col_positions = list(accumulate(chain([0], (colpos for c in range(self.total_data_cols())))))
        else:
            self.col_positions = list(accumulate(chain([0], (colpos for c in range(len(self.displayed_columns))))))

    def del_col_position(self, idx, deselect_all = False, preserve_other_selections = False):
        # WORK NEEDED FOR PRESERVE SELECTIONS ?
        if deselect_all:
            self.deselect("all", redraw = False)
        if idx == "end" or len(self.col_positions) <= idx + 1:
            del self.col_positions[-1]
        else:
            w = self.col_positions[idx + 1] - self.col_positions[idx]
            idx += 1
            del self.col_positions[idx]
            self.col_positions[idx:] = [e - w for e in islice(self.col_positions, idx, len(self.col_positions))]

    def insert_col_position(self, idx, width = None, deselect_all = False, preserve_other_selections = False):
        # WORK NEEDED FOR PRESERVE SELECTIONS ?
        if deselect_all:
            self.deselect("all", redraw = False)
        if width is None:
            w = self.default_cw
        else:
            w = width
        if idx == "end" or len(self.col_positions) == idx + 1:
            self.col_positions.append(self.col_positions[-1] + w)
        else:
            idx += 1
            self.col_positions.insert(idx, self.col_positions[idx - 1] + w)
            idx += 1
            self.col_positions[idx:] = [e + w for e in islice(self.col_positions, idx, len(self.col_positions))]

    def insert_col_rc(self, event = None):
        if self.anything_selected(exclude_rows = True, exclude_cells = True):
            stidx = min(self.get_selected_cols())
            if stidx is None:
                return
            posidx = int(stidx)
            if not self.all_columns_displayed:
                stidx = int(self.displayed_columns[posidx])
                self.displayed_columns = [e + 1 if i >= posidx else e for i, e in enumerate(self.displayed_columns)]
                self.displayed_columns.insert(posidx, int(stidx))
        else:
            stidx = self.total_data_cols()
            posidx = len(self.col_positions) - 1
            if not self.all_columns_displayed:
                stidx = self.displayed_columns[-1] + 1
                self.displayed_columns = [e + 1 if i >= self.displayed_columns[-1] else e for i, e in enumerate(self.displayed_columns)]
                self.displayed_columns.append(int(self.displayed_columns[-1]) + 1)
        self.insert_col_position(idx = posidx,
                                 width = int(self.default_cw),
                                 deselect_all = True,
                                 preserve_other_selections = False)
        if self.my_hdrs and isinstance(self.my_hdrs, list):
            try:
                self.my_hdrs.insert(stidx, "")
            except:
                pass
        if self.row_positions == [0] and not self.data_ref:
            self.insert_row_position(idx = "end",
                                     height = int(self.min_rh),
                                     deselect_all = False,
                                     preserve_other_selections = False)
            self.data_ref.append([""])
        else:
            for rn in range(len(self.data_ref)):
                self.data_ref[rn].insert(stidx, "")
        self.CH.select_col(c = posidx)
        if self.undo_enabled:
            self.undo_storage.append(zlib.compress(pickle.dumps(("insert_col", {"data_col_num": stidx,
                                                                                "sheet_col_num": posidx}))))
        self.refresh()
        if self.extra_insert_cols_rc_func is not None:
            self.extra_insert_cols_rc_func((stidx, posidx))

    def insert_row_rc(self, event = None): #subset of rows
        if self.anything_selected(exclude_columns = True, exclude_cells = True):
            stidx = min(self.get_selected_rows())
            posidx = int(stidx)
        else:
            stidx = self.total_data_rows()
            posidx = len(self.row_positions) - 1
        self.insert_row_position(idx = posidx,
                                 height = self.GetLinesHeight(self.default_rh),
                                 deselect_all = True,
                                 preserve_other_selections = False)
        if self.my_row_index and isinstance(self.my_row_index, list):
            try:
                self.my_row_index.insert(stidx, "")
            except:
                pass
        if self.col_positions == [0] and not self.data_ref:
            self.insert_col_position(idx = "end",
                                     width = int(self.default_cw),
                                     deselect_all = False,
                                     preserve_other_selections = False)
            self.data_ref.append([""])
        else:
            self.data_ref.insert(stidx, list(repeat("", self.total_data_cols())))
        self.RI.select_row(r = posidx)
        if self.undo_enabled:
            self.undo_storage.append(zlib.compress(pickle.dumps(("insert_row", {"data_row_num": stidx,
                                                                                "sheet_row_num": posidx}))))
        self.refresh()
        if self.extra_insert_rows_rc_func is not None:
            self.extra_insert_rows_rc_func((stidx, posidx))
            
    def del_cols_rc(self, event = None):
        seld_cols = sorted(self.get_selected_cols())
        if seld_cols:
            if self.undo_enabled:
                undo_storage = {'deleted_cols': {},
                                'colwidths': {},
                                'deleted_hdr_values': {},
                                'selection_boxes': self.get_boxes()}
            if self.all_columns_displayed:
                if self.undo_enabled:
                    for c in reversed(seld_cols):
                        undo_storage['colwidths'][c] = self.col_positions[c + 1] - self.col_positions[c]
                        for rn in range(len(self.data_ref)):
                            if c not in undo_storage['deleted_cols']:
                                undo_storage['deleted_cols'][c] = {}
                            try:
                                undo_storage['deleted_cols'][c][rn] = self.data_ref[rn].pop(c)
                            except:
                                continue
                    if self.my_hdrs and isinstance(self.my_hdrs, list):
                        for c in reversed(seld_cols):
                            try:
                                undo_storage['deleted_hdr_values'][c] = self.my_hdrs.pop(c)
                            except:
                                continue
                else:
                    for rn in range(len(self.data_ref)):
                        for c in reversed(seld_cols):
                            del self.data_ref[rn][c]
                    if self.my_hdrs and isinstance(self.my_hdrs, list):
                        for c in reversed(seld_cols):
                            try:
                                del self.my_hdrs[c]
                            except:
                                continue
            else:
                if self.undo_enabled:
                    for c in reversed(seld_cols):
                        undo_storage['colwidths'][c] = self.col_positions[c + 1] - self.col_positions[c]
                        for rn in range(len(self.data_ref)):
                            if self.displayed_columns[c] not in undo_storage['deleted_cols']:
                                undo_storage['deleted_cols'][self.displayed_columns[c]] = {}
                            try:
                                undo_storage['deleted_cols'][self.displayed_columns[c]][rn] = self.data_ref[rn].pop(self.displayed_columns[c])
                            except:
                                continue
                    if self.my_hdrs and isinstance(self.my_hdrs, list):
                        for c in reversed(seld_cols):
                            try:
                                undo_storage['deleted_hdr_values'][self.displayed_columns[c]] = self.my_hdrs.pop(self.displayed_columns[c])
                            except:
                                continue
                else:
                    for rn in range(len(self.data_ref)):
                        for c in reversed(seld_cols):
                            del self.data_ref[rn][self.displayed_columns[c]]
                    if self.my_hdrs and isinstance(self.my_hdrs, list):
                        for c in reversed(seld_cols):
                            try:
                                del self.my_hdrs[self.displayed_columns[c]]
                            except:
                                continue
            for c in reversed(seld_cols):
                self.del_col_position(c,
                                      deselect_all = False,
                                      preserve_other_selections = False)
            if self.undo_enabled:
                self.undo_storage.append(zlib.compress(pickle.dumps(("delete_cols", undo_storage))))
            self.deselect("allcols", redraw = False)
            self.set_current_to_last()
            self.refresh()
            if self.extra_del_cols_rc_func is not None:
                self.extra_del_cols_rc_func(tuple(seld_cols))

    def del_rows_rc(self, event = None):
        seld_rows = sorted(self.get_selected_rows())
        if seld_rows:
            if self.undo_enabled:
                undo_storage = {'deleted_rows': [],
                                'deleted_index_values': [],
                                'selection_boxes': self.get_boxes()}                                                       
                for r in reversed(seld_rows):
                    undo_storage['deleted_rows'].append((r, self.data_ref.pop(r), self.row_positions[r + 1] - self.row_positions[r]))
            else:
                for r in reversed(seld_rows):
                    del self.data_ref[r]
            if self.my_row_index and isinstance(self.my_row_index, list):
                if self.undo_enabled:
                    for r in reversed(seld_rows):
                        try:
                            undo_storage['deleted_index_values'].append((r, self.my_row_index.pop(r)))
                        except:
                            continue
                else:
                    for r in reversed(seld_rows):
                        try:
                            del self.my_row_index[r]
                        except:
                            continue
            if self.undo_enabled:
                self.undo_storage.append(zlib.compress(pickle.dumps(("delete_rows", undo_storage))))
            for r in reversed(seld_rows):
                self.del_row_position(r,
                                      deselect_all = False,
                                      preserve_other_selections = False)
            self.deselect("allrows", redraw = False)
            self.set_current_to_last()
            self.refresh()
            if self.extra_del_rows_rc_func is not None:
                self.extra_del_rows_rc_func(tuple(seld_rows))

    def reset_row_positions(self):
        rowpos = self.GetLinesHeight(self.default_rh)
        self.row_positions = list(accumulate(chain([0], (rowpos for r in range(self.total_data_rows())))))

    def del_row_position(self, idx, deselect_all = False, preserve_other_selections = False):
        # WORK NEEDED FOR PRESERVE SELECTIONS ?
        if deselect_all:
            self.deselect("all", redraw = False)
        if idx == "end" or len(self.row_positions) <= idx + 1:
            del self.row_positions[-1]
        else:
            w = self.row_positions[idx + 1] - self.row_positions[idx]
            idx += 1
            del self.row_positions[idx]
            self.row_positions[idx:] = [e - w for e in islice(self.row_positions, idx, len(self.row_positions))]

    def insert_row_position(self, idx, height = None, deselect_all = False, preserve_other_selections = False):
        # WORK NEEDED FOR PRESERVE SELECTIONS ?
        if deselect_all:
            self.deselect("all", redraw = False)
        if height is None:
            h = self.GetLinesHeight(self.default_rh)
        else:
            h = height
        if idx == "end" or len(self.row_positions) == idx + 1:
            self.row_positions.append(self.row_positions[-1] + h)
        else:
            idx += 1
            self.row_positions.insert(idx, self.row_positions[idx - 1] + h)
            idx += 1
            self.row_positions[idx:] = [e + h for e in islice(self.row_positions, idx, len(self.row_positions))]

    def move_row_position(self, idx1, idx2):
        if not len(self.row_positions) <= 2:
            if idx1 < idx2:
                height = self.row_positions[idx1 + 1] - self.row_positions[idx1]
                self.row_positions.insert(idx2 + 1, self.row_positions.pop(idx1 + 1))
                for i in range(idx1 + 1, idx2 + 1):
                    self.row_positions[i] -= height
                self.row_positions[idx2 + 1] = self.row_positions[idx2] + height
            else:
                height = self.row_positions[idx1 + 1] - self.row_positions[idx1]
                self.row_positions.insert(idx2 + 1, self.row_positions.pop(idx1 + 1))
                for i in range(idx2 + 2, idx1 + 2):
                    self.row_positions[i] += height
                self.row_positions[idx2 + 1] = self.row_positions[idx2] + height

    def move_col_position(self, idx1, idx2):
        if not len(self.col_positions) <= 2:
            if idx1 < idx2:
                width = self.col_positions[idx1 + 1] - self.col_positions[idx1]
                self.col_positions.insert(idx2 + 1, self.col_positions.pop(idx1 + 1))
                for i in range(idx1 + 1, idx2 + 1):
                    self.col_positions[i] -= width
                self.col_positions[idx2 + 1] = self.col_positions[idx2] + width
            else:
                width = self.col_positions[idx1 + 1] - self.col_positions[idx1]
                self.col_positions.insert(idx2 + 1, self.col_positions.pop(idx1 + 1))
                for i in range(idx2 + 2, idx1 + 2):
                    self.col_positions[i] += width
                self.col_positions[idx2 + 1] = self.col_positions[idx2] + width

    def GetLinesHeight(self, n, old_method = False):
        if old_method:
            if n == 1:
                return int(self.min_rh)
            else:
                return int(self.fl_ins) + (self.xtra_lines_increment * n) - 2
        else:
            x = self.txt_measure_canvas.create_text(0, 0,
                                                    text = "\n".join(["j^|" for lines in range(n)]) if n > 1 else "j^|",
                                                    font = self.my_font)
            b = self.txt_measure_canvas.bbox(x)
            h = b[3] - b[1] + 5
            self.txt_measure_canvas.delete(x)
            return h

    def GetHdrLinesHeight(self, n, old_method = False):
        if old_method:
            if n == 1:
                return int(self.hdr_min_rh)
            else:
                return int(self.hdr_fl_ins) + (self.hdr_xtra_lines_increment * n) - 2
        else:
            x = self.txt_measure_canvas.create_text(0, 0,
                                                    text = "\n".join(["j^|" for lines in range(n)]) if n > 1 else "j^|",
                                                    font = self.my_hdr_font)
            b = self.txt_measure_canvas.bbox(x)
            h = b[3] - b[1] + 5
            self.txt_measure_canvas.delete(x)
            return h

    def display_columns(self, indexes = None, enable = None, reset_col_positions = True, set_col_positions = True, deselect_all = True):
        if deselect_all:
            self.deselect("all")
        if indexes is None and enable is None:
            return tuple(self.displayed_columns)
        if indexes is not None and indexes != self.displayed_columns:
            self.undo_storage = deque(maxlen = self.max_undos)
        if indexes is not None:
            self.displayed_columns = indexes
        used_to_be_enabled = bool(not self.all_columns_displayed)
        if enable != used_to_be_enabled:
            self.undo_storage = deque(maxlen = self.max_undos)  
        if enable:
            self.all_columns_displayed = False
        else:
            self.all_columns_displayed = True
        if enable and set_col_positions:
            if indexes and len(self.col_positions) > max(indexes) and not used_to_be_enabled:
                self.col_positions = list(accumulate(chain([0], (self.col_positions[c + 1] - self.col_positions[c] for c in indexes))))
            elif reset_col_positions: #doesnt have existing col widths to maintain
                self.reset_col_positions()
        elif enable and reset_col_positions:
            self.reset_col_positions()
                
    def headers(self, newheaders = None, index = None, reset_col_positions = False, show_headers_if_not_sheet = True):
        if newheaders is not None:
            if isinstance(newheaders, (list, tuple)):
                self.my_hdrs = list(newheaders) if isinstance(newheaders, tuple) else newheaders
            elif isinstance(newheaders, int):
                self.my_hdrs = int(newheaders)
            elif isinstance(index, int):
                self.my_hdrs[index] = f"{newheaders}"
            elif not isinstance(newheaders, (list, tuple, int)) and index is None:
                try:
                    self.my_hdrs = list(newheaders)
                except:
                    raise ValueError("New header must be iterable or int (use int to use a row as the header")
            if reset_col_positions:
                self.reset_col_positions()
            elif show_headers_if_not_sheet and isinstance(self.my_hdrs, list) and (self.col_positions == [0] or not self.col_positions):
                colpos = int(self.default_cw)
                if self.all_columns_displayed:
                    self.col_positions = list(accumulate(chain([0], (colpos for c in range(len(self.my_hdrs))))))
                else:
                    self.col_positions = list(accumulate(chain([0], (colpos for c in range(len(self.displayed_columns))))))
        else:
            if index is not None:
                if isinstance(index, int):
                    return self.my_hdrs[index]
            else:
                return self.my_hdrs

    def row_index(self, newindex = None, index = None, reset_row_positions = False, show_index_if_not_sheet = True):
        if newindex is not None:
            if isinstance(newindex, (list, tuple)):
                self.my_row_index = list(newindex) if isinstance(newindex, tuple) else newindex
            elif isinstance(newindex, int):
                self.my_row_index = int(newindex)
            elif isinstance(index, int):
                self.my_row_index[index] = f"{newindex}"
            elif not isinstance(newindex, (list, tuple, int)) and index is None:
                try:
                    self.my_row_index = list(newindex)
                except:
                    raise ValueError("New index must be iterable or int (use int to use a column as the index")
            if reset_row_positions:
                self.reset_row_positions()
            elif show_index_if_not_sheet and isinstance(self.my_row_index, list) and (self.row_positions == [0] or not self.row_positions):
                rowpos = self.GetLinesHeight(self.default_rh)
                self.row_positions = list(accumulate(chain([0], (rowpos for c in range(len(self.my_row_index))))))
        else:
            if index is not None:
                if isinstance(index, int):
                    return self.my_row_index[index]
            else:
                return self.my_row_index

    def total_data_cols(self):
        h_total = 0
        d_total = 0
        if isinstance(self.my_hdrs, list):
            h_total = len(self.my_hdrs)
        try:
            d_total = len(max(self.data_ref, key = len))
        except:
            pass
        return h_total if h_total > d_total else d_total

    def total_data_rows(self):
        i_total = 0
        d_total = 0
        if isinstance(self.my_row_index, list):
            i_total = len(self.my_row_index)
        d_total = len(self.data_ref)
        return i_total if i_total > d_total else d_total

    def data_dimensions(self, total_rows = None, total_columns = None):
        if total_rows is None and total_columns is None:
            return self.total_data_rows(), self.total_data_cols()
        if total_rows is not None:
            if len(self.data_ref) < total_rows:
                if total_columns is None:
                    total_data_cols = self.total_data_cols()
                    self.data_ref.extend([list(repeat("", total_data_cols)) for r in range(total_rows - len(self.data_ref))])
                else:
                    self.data_ref.extend([list(repeat("", total_columns)) for r in range(total_rows - len(self.data_ref))])
            else:
                self.data_ref[total_rows:] = []
        if total_columns is not None:
            self.data_ref[:] = [r[:total_columns] if len(r) > total_columns else r + list(repeat("", total_columns - len(r))) for r in self.data_ref]

    def equalize_data_row_lengths(self):
        total_columns = self.total_data_cols()
        self.data_ref[:] = [r + list(repeat("", total_columns - len(r))) if total_columns > len(r) else r for r in self.data_ref]
        return total_columns

    def get_canvas_visible_area(self):
        return self.canvasx(0), self.canvasy(0), self.canvasx(self.winfo_width()), self.canvasy(self.winfo_height())

    def get_visible_rows(self, y1, y2):
        start_row = bisect.bisect_left(self.row_positions, y1)
        end_row = bisect.bisect_right(self.row_positions, y2)
        if not y2 >= self.row_positions[-1]:
            end_row += 1
        return start_row, end_row

    def get_visible_columns(self, x1, x2):
        start_col = bisect.bisect_left(self.col_positions, x1)
        end_col = bisect.bisect_right(self.col_positions, x2)
        if not x2 >= self.col_positions[-1]:
            end_col += 1
        return start_col, end_col

    def main_table_redraw_grid_and_text(self, redraw_header = False, redraw_row_index = False):
        try:
            last_col_line_pos = self.col_positions[-1] + 1
            last_row_line_pos = self.row_positions[-1] + 1
            self.configure(scrollregion=(0, 0, last_col_line_pos + 150, last_row_line_pos + 100))
            self.delete("t", "g", "hi")
            x1 = self.canvasx(0)
            y1 = self.canvasy(0)
            x2 = self.canvasx(self.winfo_width())
            y2 = self.canvasy(self.winfo_height())
            self.row_width_resize_bbox = (x1, y1, x1 + 5, y2)
            self.header_height_resize_bbox = (x1 + 6, y1, x2, y1 + 3)
            start_row = bisect.bisect_left(self.row_positions, y1)
            end_row = bisect.bisect_right(self.row_positions, y2)
            if not y2 >= self.row_positions[-1]:
                end_row += 1
            start_col = bisect.bisect_left(self.col_positions, x1)
            end_col = bisect.bisect_right(self.col_positions, x2)
            if not x2 >= self.col_positions[-1]:
                end_col += 1
            if last_col_line_pos > x2:
                x_stop = x2
            else:
                x_stop = last_col_line_pos
            if last_row_line_pos > y2:
                y_stop = y2
            else:
                y_stop = last_row_line_pos
            cr_ = self.create_rectangle
            ct_ = self.create_text
            sb = y2 + 2
            for r in range(start_row - 1, end_row):
                y = self.row_positions[r]
                self.create_line(x1, y, x_stop, y, fill= self.grid_color, width = 1, tag = "g")
            for c in range(start_col - 1, end_col):
                x = self.col_positions[c]
                self.create_line(x, y1, x, y_stop, fill = self.grid_color, width = 1, tag = "g")
            if start_row > 0:
                start_row -= 1
            if start_col > 0:
                start_col -= 1
            end_row -= 1
            c_2 = self.selected_cells_background if self.selected_cells_background.startswith("#") else Color_Map_[self.selected_cells_background]
            c_2_ = (int(c_2[1:3], 16), int(c_2[3:5], 16), int(c_2[5:], 16))
            c_3 = self.selected_cols_bg if self.selected_cols_bg.startswith("#") else Color_Map_[self.selected_cols_bg]
            c_3_ = (int(c_3[1:3], 16), int(c_3[3:5], 16), int(c_3[5:], 16))
            c_4 = self.selected_rows_bg if self.selected_rows_bg.startswith("#") else Color_Map_[self.selected_rows_bg]
            c_4_ = (int(c_4[1:3], 16), int(c_4[3:5], 16), int(c_4[5:], 16))
            rows_ = tuple(range(start_row, end_row))
            selected_cells, selected_rows, selected_cols, actual_selected_rows, actual_selected_cols = self.get_redraw_selections((start_row, start_col, end_row, end_col - 1))
            if self.all_columns_displayed:
                if self.align == "w":
                    for c in range(start_col, end_col - 1):
                        fc = self.col_positions[c]
                        sc = self.col_positions[c + 1]
                        x = fc + 5
                        mw = sc - fc - 5
                        for r in rows_:
                            fr = self.row_positions[r]
                            sr = self.row_positions[r + 1]
                            if sr > sb:
                                sr = sb
                            if (r, c) in self.highlighted_cells and c in actual_selected_cols:
                                c_1 = self.highlighted_cells[(r, c)][0] if self.highlighted_cells[(r, c)][0].startswith("#") else Color_Map_[self.highlighted_cells[(r, c)][0]]
                                cr_(fc + 1,
                                    fr + 1,
                                    sc,
                                    sr,
                                    fill = (f"#{int((int(c_1[1:3], 16) + c_3_[0]) / 2):02X}" +
                                            f"{int((int(c_1[3:5], 16) + c_3_[1]) / 2):02X}" +
                                            f"{int((int(c_1[5:], 16) + c_3_[2]) / 2):02X}"),
                                    outline = "", tag = "hi")
                                tf = self.selected_cols_fg if self.highlighted_cells[(r, c)][1] is None else self.highlighted_cells[(r, c)][1]
                            elif (r, c) in self.highlighted_cells and r in actual_selected_rows:
                                c_1 = self.highlighted_cells[(r, c)][0] if self.highlighted_cells[(r, c)][0].startswith("#") else Color_Map_[self.highlighted_cells[(r, c)][0]]
                                cr_(fc + 1,
                                    fr + 1,
                                    sc,
                                    sr,
                                    fill = (f"#{int((int(c_1[1:3], 16) + c_4_[0]) / 2):02X}" +
                                            f"{int((int(c_1[3:5], 16) + c_4_[1]) / 2):02X}" +
                                            f"{int((int(c_1[5:], 16) + c_4_[2]) / 2):02X}"),
                                    outline = "", tag = "hi")
                                tf = self.selected_rows_fg if self.highlighted_cells[(r, c)][1] is None else self.highlighted_cells[(r, c)][1]
                            elif (r, c) in self.highlighted_cells and (r, c) in selected_cells:
                                c_1 = self.highlighted_cells[(r, c)][0] if self.highlighted_cells[(r, c)][0].startswith("#") else Color_Map_[self.highlighted_cells[(r, c)][0]]
                                cr_(fc + 1,
                                    fr + 1,
                                    sc,
                                    sr,
                                    fill = (f"#{int((int(c_1[1:3], 16) + c_2_[0]) / 2):02X}" +
                                            f"{int((int(c_1[3:5], 16) + c_2_[1]) / 2):02X}" +
                                            f"{int((int(c_1[5:], 16) + c_2_[2]) / 2):02X}"),
                                    outline = "", tag = "hi")
                                tf = self.selected_cells_foreground if self.highlighted_cells[(r, c)][1] is None else self.highlighted_cells[(r, c)][1]
                            elif c in actual_selected_cols:
                                tf = self.selected_cols_fg
                            elif r in actual_selected_rows:
                                tf = self.selected_rows_fg
                            elif (r, c) in selected_cells:
                                tf = self.selected_cells_foreground
                            elif (r, c) in self.highlighted_cells and r not in actual_selected_rows and c not in actual_selected_cols:
                                cr_(fc + 1, fr + 1, sc, sr, fill = self.highlighted_cells[(r, c)][0], outline = "", tag = "hi")
                                tf = self.text_color if self.highlighted_cells[(r, c)][1] is None else self.highlighted_cells[(r, c)][1]
                            else:
                                tf = self.text_color
                            if x > x2:
                                continue
                            try:
                                lns = self.data_ref[r][c]
                                if isinstance(lns, str):
                                    lns = lns.split("\n")
                                else:
                                    lns = (f"{lns}",)
                                y = fr + self.fl_ins
                                if y + self.half_txt_h > y1:
                                    fl = lns[0]
                                    t = ct_(x, y, text = fl, fill = tf, font = self.my_font, anchor = "w", tag = "t")
                                    wd = self.bbox(t)
                                    wd = wd[2] - wd[0]
                                    if wd > mw:
                                        nl = int(len(fl) * (mw / wd)) - 1
                                        self.itemconfig(t, text = fl[:nl])
                                        wd = self.bbox(t)
                                        while wd[2] - wd[0] > mw:
                                            nl -= 1
                                            self.dchars(t, nl)
                                            wd = self.bbox(t)
                                if len(lns) > 1:
                                    stl = int((y1 - y) / self.xtra_lines_increment) - 1
                                    if stl < 1:
                                        stl = 1
                                    y += (stl * self.xtra_lines_increment)
                                    if y + self.half_txt_h < sr:
                                        for i in range(stl, len(lns)):
                                            txt = lns[i]
                                            t = ct_(x, y, text = txt, fill = tf, font = self.my_font, anchor = "w", tag = "t")
                                            wd = self.bbox(t)
                                            wd = wd[2] - wd[0]
                                            if wd > mw:
                                                nl = int(len(txt) * (mw / wd)) - 1
                                                self.itemconfig(t, text = txt[:nl])
                                                wd = self.bbox(t)
                                                while wd[2] - wd[0] > mw:
                                                    nl -= 1
                                                    self.dchars(t, nl)
                                                    wd = self.bbox(t)
                                            y += self.xtra_lines_increment
                                            if y + self.half_txt_h > sr:
                                                break
                            except:
                                continue
                elif self.align == "center":
                    for c in range(start_col, end_col - 1):
                        fc = self.col_positions[c]
                        stop = fc + 5
                        sc = self.col_positions[c + 1]
                        mw = sc - fc - 5
                        x = fc + floor((sc - fc) / 2)
                        for r in rows_:
                            fr = self.row_positions[r]
                            sr = self.row_positions[r + 1]
                            if sr > sb:
                                sr = sb
                            if (r, c) in self.highlighted_cells and c in actual_selected_cols:
                                c_1 = self.highlighted_cells[(r, c)][0] if self.highlighted_cells[(r, c)][0].startswith("#") else Color_Map_[self.highlighted_cells[(r, c)][0]]
                                cr_(fc + 1,
                                    fr + 1,
                                    sc,
                                    sr,
                                    fill = (f"#{int((int(c_1[1:3], 16) + c_3_[0]) / 2):02X}" +
                                            f"{int((int(c_1[3:5], 16) + c_3_[1]) / 2):02X}" +
                                            f"{int((int(c_1[5:], 16) + c_3_[2]) / 2):02X}"),
                                    outline = "", tag = "hi")
                                tf = self.selected_cols_fg if self.highlighted_cells[(r, c)][1] is None else self.highlighted_cells[(r, c)][1]
                            elif (r, c) in self.highlighted_cells and r in actual_selected_rows:
                                c_1 = self.highlighted_cells[(r, c)][0] if self.highlighted_cells[(r, c)][0].startswith("#") else Color_Map_[self.highlighted_cells[(r, c)][0]]
                                cr_(fc + 1,
                                    fr + 1,
                                    sc,
                                    sr,
                                    fill = (f"#{int((int(c_1[1:3], 16) + c_4_[0]) / 2):02X}" +
                                            f"{int((int(c_1[3:5], 16) + c_4_[1]) / 2):02X}" +
                                            f"{int((int(c_1[5:], 16) + c_4_[2]) / 2):02X}"),
                                    outline = "", tag = "hi")
                                tf = self.selected_rows_fg if self.highlighted_cells[(r, c)][1] is None else self.highlighted_cells[(r, c)][1]
                            elif (r, c) in self.highlighted_cells and (r, c) in selected_cells:
                                c_1 = self.highlighted_cells[(r, c)][0] if self.highlighted_cells[(r, c)][0].startswith("#") else Color_Map_[self.highlighted_cells[(r, c)][0]]
                                cr_(fc + 1,
                                    fr + 1,
                                    sc,
                                    sr,
                                    fill = (f"#{int((int(c_1[1:3], 16) + c_2_[0]) / 2):02X}" +
                                            f"{int((int(c_1[3:5], 16) + c_2_[1]) / 2):02X}" +
                                            f"{int((int(c_1[5:], 16) + c_2_[2]) / 2):02X}"),
                                    outline = "", tag = "hi")
                                tf = self.selected_cells_foreground if self.highlighted_cells[(r, c)][1] is None else self.highlighted_cells[(r, c)][1]
                            elif c in actual_selected_cols:
                                tf = self.selected_cols_fg
                            elif r in actual_selected_rows:
                                tf = self.selected_rows_fg
                            elif (r, c) in selected_cells:
                                tf = self.selected_cells_foreground
                            elif (r, c) in self.highlighted_cells and r not in actual_selected_rows and c not in actual_selected_cols:
                                cr_(fc + 1, fr + 1, sc, sr, fill = self.highlighted_cells[(r, c)][0], outline = "", tag = "hi")
                                tf = self.text_color if self.highlighted_cells[(r, c)][1] is None else self.highlighted_cells[(r, c)][1]
                            else:
                                tf = self.text_color
                            if stop > x2:
                                continue
                            try:
                                lns = self.data_ref[r][c]
                                if isinstance(lns, str):
                                    lns = lns.split("\n")
                                else:
                                    lns = (f"{lns}", )
                                fl = lns[0]
                                y = fr + self.fl_ins
                                if y + self.half_txt_h > y1:
                                    t = ct_(x, y, text = fl, fill = tf, font = self.my_font, anchor = "center", tag = "t")
                                    wd = self.bbox(t)
                                    wd = wd[2] - wd[0]
                                    if wd > mw:
                                        tl = len(fl)
                                        slce = tl - floor(tl * (mw / wd))
                                        if slce % 2:
                                            slce += 1
                                        else:
                                            slce += 2
                                        slce = int(slce / 2)
                                        fl = fl[slce:tl - slce]
                                        self.itemconfig(t, text = fl)
                                        wd = self.bbox(t)
                                        while wd[2] - wd[0] > mw:
                                            fl = fl[1: - 1]
                                            self.itemconfig(t, text = fl)
                                            wd = self.bbox(t)
                                if len(lns) > 1:
                                    stl = int((y1 - y) / self.xtra_lines_increment) - 1
                                    if stl < 1:
                                        stl = 1
                                    y += (stl * self.xtra_lines_increment)
                                    if y + self.half_txt_h < sr:
                                        for i in range(stl,len(lns)):
                                            txt = lns[i]
                                            t = ct_(x, y, text = txt, fill = tf, font = self.my_font, anchor = "center", tag = "t")
                                            wd = self.bbox(t)
                                            wd = wd[2] - wd[0]
                                            if wd > mw:
                                                tl = len(txt)
                                                slce = tl - floor(tl * (mw / wd))
                                                if slce % 2:
                                                    slce += 1
                                                else:
                                                    slce += 2
                                                slce = int(slce / 2)
                                                txt = txt[slce:tl - slce]
                                                self.itemconfig(t, text = txt)
                                                wd = self.bbox(t)
                                                while wd[2] - wd[0] > mw:
                                                    txt = txt[1: - 1]
                                                    self.itemconfig(t, text = txt)
                                                    wd = self.bbox(t)
                                            y += self.xtra_lines_increment
                                            if y + self.half_txt_h > sr:
                                                break
                            except:
                                continue
            else:
                if self.align == "w":
                    for c in range(start_col, end_col - 1):
                        fc = self.col_positions[c]
                        sc = self.col_positions[c + 1]
                        x = fc + 5
                        mw = sc - fc - 5
                        for r in rows_:
                            fr = self.row_positions[r]
                            sr = self.row_positions[r + 1]
                            if sr > sb:
                                sr = sb
                            if (r, self.displayed_columns[c]) in self.highlighted_cells and c in actual_selected_cols:
                                c_1 = self.highlighted_cells[(r, self.displayed_columns[c])][0] if self.highlighted_cells[(r, self.displayed_columns[c])][0].startswith("#") else Color_Map_[self.highlighted_cells[(r, self.displayed_columns[c])][0]]
                                cr_(fc + 1,
                                    fr + 1,
                                    sc,
                                    sr,
                                    fill = (f"#{int((int(c_1[1:3], 16) + c_3_[0]) / 2):02X}" +
                                            f"{int((int(c_1[3:5], 16) + c_3_[1]) / 2):02X}" +
                                            f"{int((int(c_1[5:], 16) + c_3_[2]) / 2):02X}"),
                                    outline = "", tag = "hi")
                                tf = self.selected_cols_fg if self.highlighted_cells[(r, self.displayed_columns[c])][1] is None else self.highlighted_cells[(r, self.displayed_columns[c])][1]
                            elif (r, self.displayed_columns[c]) in self.highlighted_cells and r in actual_selected_rows:
                                c_1 = self.highlighted_cells[(r, self.displayed_columns[c])][0] if self.highlighted_cells[(r, self.displayed_columns[c])][0].startswith("#") else Color_Map_[self.highlighted_cells[(r, self.displayed_columns[c])][0]]
                                cr_(fc + 1,
                                    fr + 1,
                                    sc,
                                    sr,
                                    fill = (f"#{int((int(c_1[1:3], 16) + c_4_[0]) / 2):02X}" +
                                            f"{int((int(c_1[3:5], 16) + c_4_[1]) / 2):02X}" +
                                            f"{int((int(c_1[5:], 16) + c_4_[2]) / 2):02X}"),
                                    outline = "", tag = "hi")
                                tf = self.selected_rows_fg if self.highlighted_cells[(r, self.displayed_columns[c])][1] is None else self.highlighted_cells[(r, self.displayed_columns[c])][1]
                            elif (r, self.displayed_columns[c]) in self.highlighted_cells and (r, c) in selected_cells:
                                c_1 = self.highlighted_cells[(r, self.displayed_columns[c])][0] if self.highlighted_cells[(r, self.displayed_columns[c])][0].startswith("#") else Color_Map_[self.highlighted_cells[(r, self.displayed_columns[c])][0]]
                                cr_(fc + 1,
                                    fr + 1,
                                    sc,
                                    sr,
                                    fill = (f"#{int((int(c_1[1:3], 16) + c_2_[0]) / 2):02X}" +
                                            f"{int((int(c_1[3:5], 16) + c_2_[1]) / 2):02X}" +
                                            f"{int((int(c_1[5:], 16) + c_2_[2]) / 2):02X}"),
                                    outline = "", tag = "hi")
                                tf = self.selected_cells_foreground if self.highlighted_cells[(r, self.displayed_columns[c])][1] is None else self.highlighted_cells[(r, self.displayed_columns[c])][1]
                            elif c in actual_selected_cols:
                                tf = self.selected_cols_fg
                            elif r in actual_selected_rows:
                                tf = self.selected_rows_fg
                            elif (r, c) in selected_cells:
                                tf = self.selected_cells_foreground
                            elif (r, self.displayed_columns[c]) in self.highlighted_cells and r not in actual_selected_rows and c not in actual_selected_cols:
                                cr_(fc + 1, fr + 1, sc, sr, fill = self.highlighted_cells[(r, self.displayed_columns[c])][0], outline = "", tag = "hi")
                                tf = self.text_color if self.highlighted_cells[(r, self.displayed_columns[c])][1] is None else self.highlighted_cells[(r, self.displayed_columns[c])][1]
                            else:
                                tf = self.text_color
                            if x > x2:
                                continue
                            try:
                                lns = self.data_ref[r][self.displayed_columns[c]]
                                if isinstance(lns, str):
                                    lns = lns.split("\n")
                                else:
                                    lns = (f"{lns}", )
                                y = fr + self.fl_ins
                                if y + self.half_txt_h > y1:
                                    fl = lns[0]
                                    t = ct_(x, y, text = fl, fill = tf, font = self.my_font, anchor = "w", tag = "t")
                                    wd = self.bbox(t)
                                    wd = wd[2] - wd[0]
                                    if wd > mw:
                                        nl = int(len(fl) * (mw / wd)) - 1
                                        self.itemconfig(t, text = fl[:nl])
                                        wd = self.bbox(t)
                                        while wd[2] - wd[0] > mw:
                                            nl -= 1
                                            self.dchars(t, nl)
                                            wd = self.bbox(t)
                                if len(lns) > 1:
                                    stl = int((y1 - y) / self.xtra_lines_increment) - 1
                                    if stl < 1:
                                        stl = 1
                                    y += (stl * self.xtra_lines_increment)
                                    if y + self.half_txt_h < sr:
                                        for i in range(stl, len(lns)):
                                            txt = lns[i]
                                            t = ct_(x, y, text = txt, fill = tf, font = self.my_font, anchor = "w", tag = "t")
                                            wd = self.bbox(t)
                                            wd = wd[2] - wd[0]
                                            if wd > mw:
                                                nl = int(len(txt) * (mw / wd)) - 1
                                                self.itemconfig(t, text = txt[:nl])
                                                wd = self.bbox(t)
                                                while wd[2] - wd[0] > mw:
                                                    nl -= 1
                                                    self.dchars(t, nl)
                                                    wd = self.bbox(t)
                                            y += self.xtra_lines_increment
                                            if y + self.half_txt_h > sr:
                                                break
                            except:
                                continue
                elif self.align == "center":
                    for c in range(start_col, end_col - 1):
                        fc = self.col_positions[c]
                        stop = fc + 5
                        sc = self.col_positions[c + 1]
                        mw = sc - fc - 5
                        x = fc + floor((sc - fc) / 2)
                        for r in rows_:
                            fr = self.row_positions[r]
                            sr = self.row_positions[r + 1]
                            if sr > sb:
                                sr = sb
                            if (r, self.displayed_columns[c]) in self.highlighted_cells and c in actual_selected_cols:
                                c_1 = self.highlighted_cells[(r, self.displayed_columns[c])][0] if self.highlighted_cells[(r, self.displayed_columns[c])][0].startswith("#") else Color_Map_[self.highlighted_cells[(r, self.displayed_columns[c])][0]]
                                cr_(fc + 1,
                                    fr + 1,
                                    sc,
                                    sr,
                                    fill = (f"#{int((int(c_1[1:3], 16) + c_3_[0]) / 2):02X}" +
                                            f"{int((int(c_1[3:5], 16) + c_3_[1]) / 2):02X}" +
                                            f"{int((int(c_1[5:], 16) + c_3_[2]) / 2):02X}"),
                                    outline = "", tag = "hi")
                                tf = self.selected_cols_fg if self.highlighted_cells[(r, self.displayed_columns[c])][1] is None else self.highlighted_cells[(r, self.displayed_columns[c])][1]
                            elif (r, self.displayed_columns[c]) in self.highlighted_cells and r in actual_selected_rows:
                                c_1 = self.highlighted_cells[(r, self.displayed_columns[c])][0] if self.highlighted_cells[(r, self.displayed_columns[c])][0].startswith("#") else Color_Map_[self.highlighted_cells[(r, self.displayed_columns[c])][0]]
                                cr_(fc + 1,
                                    fr + 1,
                                    sc,
                                    sr,
                                    fill = (f"#{int((int(c_1[1:3], 16) + c_4_[0]) / 2):02X}" +
                                            f"{int((int(c_1[3:5], 16) + c_4_[1]) / 2):02X}" +
                                            f"{int((int(c_1[5:], 16) + c_4_[2]) / 2):02X}"),
                                    outline = "", tag = "hi")
                                tf = self.selected_rows_fg if self.highlighted_cells[(r, self.displayed_columns[c])][1] is None else self.highlighted_cells[(r, self.displayed_columns[c])][1]
                            elif (r, self.displayed_columns[c]) in self.highlighted_cells and (r, c) in selected_cells:
                                c_1 = self.highlighted_cells[(r, self.displayed_columns[c])][0] if self.highlighted_cells[(r, self.displayed_columns[c])][0].startswith("#") else Color_Map_[self.highlighted_cells[(r, self.displayed_columns[c])][0]]
                                cr_(fc + 1,
                                    fr + 1,
                                    sc,
                                    sr,
                                    fill = (f"#{int((int(c_1[1:3], 16) + c_2_[0]) / 2):02X}" +
                                            f"{int((int(c_1[3:5], 16) + c_2_[1]) / 2):02X}" +
                                            f"{int((int(c_1[5:], 16) + c_2_[2]) / 2):02X}"),
                                    outline = "", tag = "hi")
                                tf = self.selected_cells_foreground if self.highlighted_cells[(r, self.displayed_columns[c])][1] is None else self.highlighted_cells[(r, self.displayed_columns[c])][1]
                            elif c in actual_selected_cols:
                                tf = self.selected_cols_fg
                            elif r in actual_selected_rows:
                                tf = self.selected_rows_fg
                            elif (r, c) in selected_cells:
                                tf = self.selected_cells_foreground
                            elif (r, self.displayed_columns[c]) in self.highlighted_cells and r not in actual_selected_rows and c not in actual_selected_cols:
                                cr_(fc + 1, fr + 1, sc, sr, fill = self.highlighted_cells[(r, self.displayed_columns[c])][0], outline = "", tag = "hi")
                                tf = self.text_color if self.highlighted_cells[(r, self.displayed_columns[c])][1] is None else self.highlighted_cells[(r, self.displayed_columns[c])][1]
                            else:
                                tf = self.text_color
                            if stop > x2:
                                continue
                            try:
                                lns = self.data_ref[r][self.displayed_columns[c]]
                                if isinstance(lns, str):
                                    lns = lns.split("\n")
                                else:
                                    lns = (f"{lns}", )
                                fl = lns[0]
                                y = fr + self.fl_ins
                                if y + self.half_txt_h > y1:
                                    t = ct_(x, y, text = fl, fill = tf, font = self.my_font, anchor = "center", tag = "t")
                                    wd = self.bbox(t)
                                    wd = wd[2] - wd[0]
                                    if wd > mw:
                                        tl = len(fl)
                                        slce = tl - floor(tl * (mw / wd))
                                        if slce % 2:
                                            slce += 1
                                        else:
                                            slce += 2
                                        slce = int(slce / 2)
                                        fl = fl[slce:tl - slce]
                                        self.itemconfig(t, text = fl)
                                        wd = self.bbox(t)
                                        while wd[2] - wd[0] > mw:
                                            fl = fl[1:-1]
                                            self.itemconfig(t, text = fl)
                                            wd = self.bbox(t)
                                if len(lns) > 1:
                                    stl = int((y1 - y) / self.xtra_lines_increment) - 1
                                    if stl < 1:
                                        stl = 1
                                    y += (stl * self.xtra_lines_increment)
                                    if y + self.half_txt_h < sr:
                                        for i in range(stl, len(lns)):
                                            txt = lns[i]
                                            t = ct_(x, y, text = txt, fill = tf, font = self.my_font, anchor = "center", tag = "t")
                                            wd = self.bbox(t)
                                            wd = wd[2] - wd[0]
                                            if wd > mw:
                                                tl = len(txt)
                                                slce = tl - floor(tl * (mw / wd))
                                                if slce % 2:
                                                    slce += 1
                                                else:
                                                    slce += 2
                                                slce = int(slce / 2)
                                                txt = txt[slce:tl - slce]
                                                self.itemconfig(t, text = txt)
                                                wd = self.bbox(t)
                                                while wd[2] - wd[0] > mw:
                                                    txt = txt[1:-1]
                                                    self.itemconfig(t, text = txt)
                                                    wd = self.bbox(t)
                                            y += self.xtra_lines_increment
                                            if y + self.half_txt_h > sr:
                                                break
                            except:
                                continue
        except:
            return
        if redraw_header:
            self.CH.redraw_grid_and_text(last_col_line_pos, x1, x_stop, start_col, end_col, selected_cols, actual_selected_rows, actual_selected_cols)
        if redraw_row_index:
            self.RI.redraw_grid_and_text(last_row_line_pos, y1, y_stop, start_row, end_row + 1, y2, x1, x_stop, selected_rows, actual_selected_cols, actual_selected_rows)
        if self.show_selected_cells_border:
            self.tag_raise("CellSelectBorder")
            self.tag_raise("Current_Inside")
            self.tag_raise("Current_Outside")
            self.tag_raise("RowSelectBorder")
            self.tag_raise("ColSelectBorder")

    def get_all_selection_items(self):
        return sorted(self.find_withtag("CellSelectFill") + self.find_withtag("RowSelectFill") + self.find_withtag("ColSelectFill") + self.find_withtag("Current_Inside") + self.find_withtag("Current_Outside"))

    def get_boxes(self):
        boxes = {}
        for item in self.get_all_selection_items():
            alltags = self.gettags(item)
            if alltags[0] == "CellSelectFill":
                boxes[tuple(int(e) for e in alltags[1].split("_") if e)] = "cells"
            elif alltags[0] == "RowSelectFill":
                boxes[tuple(int(e) for e in alltags[1].split("_") if e)] = "rows"
            elif alltags[0] == "ColSelectFill":
                boxes[tuple(int(e) for e in alltags[1].split("_") if e)] = "cols"
            elif alltags[0] == "Current_Inside":
                boxes[tuple(int(e) for e in alltags[1].split("_") if e)] = f"{alltags[2]}_inside"
            elif alltags[0] == "Current_Outside":
                boxes[tuple(int(e) for e in alltags[1].split("_") if e)] = f"{alltags[2]}_outside"
        return boxes

    def reselect_from_get_boxes(self, boxes):
        for k, v in boxes.items():
            if v == "cells":
                self.create_selected(k[0], k[1], k[2], k[3], "cells")
            elif v == "rows":
                self.create_selected(k[0], k[1], k[2], k[3], "rows")
            elif v == "cols":
                self.create_selected(k[0], k[1], k[2], k[3], "cols")
            elif v in ("cell_inside", "cell_outside", "row_inside", "row_outside", "col_outside", "col_inside"): #currently selected
                x = v.split("_")
                self.create_current(k[0], k[1], type_ = x[0], inside = True if x[1] == "inside" else False)

    def delete_selection_rects(self, cells = True, rows = True, cols = True, delete_current = True):
        deleted_boxes = {}
        if cells:
            for item in self.find_withtag("CellSelectFill"):
                alltags = self.gettags(item)
                if alltags:
                    deleted_boxes[tuple(int(e) for e in alltags[1].split("_") if e)] = "cells"
            self.delete("CellSelectFill", "CellSelectBorder")
            self.RI.delete("CellSelectFill", "CellSelectBorder")
            self.CH.delete("CellSelectFill", "CellSelectBorder")
        if rows:
            for item in self.find_withtag("RowSelectFill"):
                alltags = self.gettags(item)
                if alltags:
                    deleted_boxes[tuple(int(e) for e in alltags[1].split("_") if e)] = "rows"
            self.delete("RowSelectFill", "RowSelectBorder")
            self.RI.delete("RowSelectFill", "RowSelectBorder")
            self.CH.delete("RowSelectFill", "RowSelectBorder")
        if cols:
            for item in self.find_withtag("ColSelectFill"):
                alltags = self.gettags(item)
                if alltags:
                    deleted_boxes[tuple(int(e) for e in alltags[1].split("_") if e)] = "cols"
            self.delete("ColSelectFill", "ColSelectBorder")
            self.RI.delete("ColSelectFill", "ColSelectBorder")
            self.CH.delete("ColSelectFill", "ColSelectBorder")
        if delete_current:
            for item in chain(self.find_withtag("Current_Inside"), self.find_withtag("Current_Outside")):
                alltags = self.gettags(item)
                if alltags:
                    deleted_boxes[tuple(int(e) for e in alltags[1].split("_") if e)] = "cells"
            self.delete("Current_Inside", "Current_Outside")
            self.RI.delete("Current_Inside", "Current_Outside")
            self.CH.delete("Current_Inside", "Current_Outside")
        return deleted_boxes

    def currently_selected(self):
        items = self.find_withtag("Current_Inside") + self.find_withtag("Current_Outside")
        if not items:
            return tuple()
        alltags = self.gettags(items[0])
        box = tuple(int(e) for e in alltags[1].split("_") if e)
        if alltags[2] == "cell":
            return (box[0], box[1])
        elif alltags[2] == "col":
            return ("column", box[1])
        elif alltags[2] == "row":
            return ("row", box[0])

    def get_tags_of_current(self):
        items = self.find_withtag("Current_Inside") + self.find_withtag("Current_Outside")
        if items:
            return self.gettags(items[0])
        else:
            return tuple()

    def create_current(self, r, c, type_ = "cell", inside = False): # cell, col or row
        r1, c1, r2, c2 = r, c, r + 1, c + 1
        self.delete("Current_Inside", "Current_Outside")
        self.RI.delete("Current_Inside", "Current_Outside")
        self.CH.delete("Current_Inside", "Current_Outside")
        if self.col_positions == [0]:
            c1 = 0
            c2 = 0
        if self.row_positions == [0]:
            r1 = 0
            r2 = 0
        if inside:
            tagr = ("Current_Inside", f"{r1}_{c1}_{r2}_{c2}", type_)
        else:
            tagr = ("Current_Outside", f"{r1}_{c1}_{r2}_{c2}", type_)
        if self.show_selected_cells_border:
            b = self.create_rectangle(self.col_positions[c1] + 1, self.row_positions[r1] + 1, self.col_positions[c2], self.row_positions[r2],
                                      fill = "",
                                      outline = self.selected_cells_border_col,
                                      width = 2,
                                      tags = tagr)
            self.tag_raise(f"{r1}_{c1}_{r2}_{c2}")
        else:
            b = self.create_rectangle(self.col_positions[c1], self.row_positions[r1], self.col_positions[c2], self.row_positions[r2],
                                      fill = self.selected_cells_background,
                                      outline = "",
                                      tags = tagr)
            self.tag_lower(f"{r1}_{c1}_{r2}_{c2}")
        if not inside:
            self.RI.create_rectangle(0, self.row_positions[r1], self.RI.current_width - 1, self.row_positions[r2],
                                      fill = self.RI.selected_cells_background,
                                      outline = "",
                                      tags = tagr)
            self.CH.create_rectangle(self.col_positions[c1], 0, self.col_positions[c2], self.CH.current_height - 1,
                                      fill = self.CH.selected_cells_background,
                                      outline = "",
                                      tags = tagr)
            self.RI.tag_lower(f"{r1}_{c1}_{r2}_{c2}")
            self.CH.tag_lower(f"{r1}_{c1}_{r2}_{c2}")
        return b

    def set_current_to_last(self):
        if not self.currently_selected():
            items = sorted(self.find_withtag("CellSelectFill") + self.find_withtag("RowSelectFill") + self.find_withtag("ColSelectFill"))
            if items:
                last = self.gettags(items[-1])
                r1, c1, r2, c2 = tuple(int(e) for e in last[1].split("_") if e)
                if last[0] == "CellSelectFill":
                    return self.gettags(self.create_current(r1, c1, "cell", inside = True))
                elif last[0] == "RowSelectFill":
                    return self.gettags(self.create_current(r1, c1, "row", inside = True))
                elif last[0] == "ColSelectFill":
                    return self.gettags(self.create_current(r1, c1, "col", inside = True))
        return tuple()
   
    def delete_current(self):
        self.delete("Current_Inside", "Current_Outside")
        self.RI.delete("Current_Inside", "Current_Outside")
        self.CH.delete("Current_Inside", "Current_Outside")
            
    def create_selected(self, r1 = None, c1 = None, r2 = None, c2 = None, type_ = "cells", taglower = True):
        currently_selected = self.currently_selected()
        if currently_selected and isinstance(currently_selected[0], int):
            if (currently_selected[0] >= r1 and
                currently_selected[1] >= c1 and
                currently_selected[0] < r2 and
                currently_selected[1] < c2):
                self.create_current(currently_selected[0], currently_selected[1], type_ = "cell", inside = True)
        if type_ == "cells":
            tagr = ("CellSelectFill", f"{r1}_{c1}_{r2}_{c2}")
            tagb = ("CellSelectBorder", f"{r1}_{c1}_{r2}_{c2}")
            taglower = "CellSelectFill"
            MT_bg = self.selected_cells_background
            MT_border_col = self.selected_cells_border_col
        elif type_ == "rows":
            tagr = ("RowSelectFill", f"{r1}_{c1}_{r2}_{c2}")
            tagb = ("RowSelectBorder", f"{r1}_{c1}_{r2}_{c2}")
            taglower = "RowSelectFill"
            MT_bg = self.selected_rows_bg
            MT_border_col = self.selected_rows_border_color
        elif type_ == "cols":
            tagr = ("ColSelectFill", f"{r1}_{c1}_{r2}_{c2}")
            tagb = ("ColSelectBorder", f"{r1}_{c1}_{r2}_{c2}")
            taglower = "ColSelectFill"
            MT_bg = self.selected_cols_bg
            MT_border_col = self.selected_cols_border_color
        r = self.create_rectangle(self.col_positions[c1], self.row_positions[r1], self.col_positions[c2], self.row_positions[r2],
                                  fill = MT_bg,
                                  outline = "",
                                  tags = tagr)
        self.RI.create_rectangle(0, self.row_positions[r1], self.RI.current_width - 1, self.row_positions[r2],
                                 fill = self.RI.selected_rows_bg if type_ == "rows" else self.RI.selected_cells_background,
                                 outline = "",
                                 tags = tagr)
        self.CH.create_rectangle(self.col_positions[c1], 0, self.col_positions[c2], self.CH.current_height - 1,
                                 fill = self.CH.selected_cols_bg if type_ == "cols" else self.CH.selected_cells_background,
                                 outline = "",
                                 tags = tagr)
        if self.show_selected_cells_border:
            b = self.create_rectangle(self.col_positions[c1], self.row_positions[r1], self.col_positions[c2], self.row_positions[r2],
                                      fill = "",
                                      outline = MT_border_col,
                                      tags = tagb)
        else:
            b = None
        if taglower:
            self.tag_lower(taglower)
            self.RI.tag_lower(taglower)
            self.RI.tag_lower("Current_Inside")
            self.RI.tag_lower("Current_Outside")
            self.RI.tag_lower("CellSelectFill")
            self.CH.tag_lower(taglower)
            self.CH.tag_lower("Current_Inside")
            self.CH.tag_lower("Current_Outside")
            self.CH.tag_lower("CellSelectFill")
        return r, b

    def recreate_all_selection_boxes(self):
        for item in chain(self.find_withtag("CellSelectFill"),
                          self.find_withtag("RowSelectFill"),
                          self.find_withtag("ColSelectFill"),
                          self.find_withtag("Current_Inside"),
                          self.find_withtag("Current_Outside")):
            full_tags = self.gettags(item)
            if full_tags:
                type_ = full_tags[0]
                r1, c1, r2, c2 = tuple(int(e) for e in full_tags[1].split("_") if e)
                self.delete(f"{r1}_{c1}_{r2}_{c2}")
                self.RI.delete(f"{r1}_{c1}_{r2}_{c2}")
                self.CH.delete(f"{r1}_{c1}_{r2}_{c2}")
                if type_.startswith("CellSelect"):
                    self.create_selected(r1, c1, r2, c2, "cells")
                elif type_.startswith("RowSelect"):
                    self.create_selected(r1, c1, r2, c2, "rows")
                elif type_.startswith("ColSelect"):
                    self.create_selected(r1, c1, r2, c2, "cols")
                elif type_.startswith("Current"):
                    if type_ == "Current_Inside":
                        self.create_current(r1, c1, full_tags[2], inside = True)
                    elif type_ == "Current_Outside":
                        self.create_current(r1, c1, full_tags[2], inside = False)
        self.tag_lower("CellSelectFill")
        self.RI.tag_lower("CellSelectFill")
        self.CH.tag_lower("CellSelectFill")
        self.tag_lower("RowSelectFill")
        self.RI.tag_lower("RowSelectFill")
        self.CH.tag_lower("RowSelectFill")
        self.tag_lower("ColSelectFill")
        self.RI.tag_lower("ColSelectFill")
        self.CH.tag_lower("ColSelectFill")
        if not self.show_selected_cells_border:
            self.tag_lower("Current_Outside")

    def GetColCoords(self, c, sel = False):
        last_col_line_pos = self.col_positions[-1] + 1
        last_row_line_pos = self.row_positions[-1] + 1
        x1 = self.col_positions[c]
        x2 = self.col_positions[c + 1]
        y1 = self.canvasy(0)
        y2 = self.canvasy(self.winfo_height())
        if last_row_line_pos < y2:
            y2 = last_col_line_pos
        if sel:
            return x1, y1 + 1, x2, y2
        else:
            return x1, y1, x2, y2

    def GetRowCoords(self, r, sel = False):
        last_col_line_pos = self.col_positions[-1] + 1
        x1 = self.canvasx(0)
        x2 = self.canvasx(self.winfo_width())
        if last_col_line_pos < x2:
            x2 = last_col_line_pos
        y1 = self.row_positions[r]
        y2 = self.row_positions[r + 1]
        if sel:
            return x1, y1 + 1, x2, y2
        else:
            return x1, y1, x2, y2

    def get_redraw_selections(self, within_range):
        scells = set()
        srows = set()
        scols = set()
        ac_srows = set()
        ac_scols = set()
        within_r1 = within_range[0]
        within_c1 = within_range[1]
        within_r2 = within_range[2]
        within_c2 = within_range[3]
        for item in self.find_withtag("RowSelectFill"):
            r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
            if (r1 >= within_r1 or
                r2 <= within_r2) or (within_r1 >= r1 and within_r2 <= r2):
                if r1 > within_r1:
                    start_row = r1
                else:
                    start_row = within_r1
                if r2 < within_r2:
                    end_row = r2
                else:
                    end_row = within_r2
                srows.update(set(range(start_row, end_row)))
                ac_srows.update(set(range(start_row, end_row)))
        for item in self.find_withtag("Current_Outside"):
            r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
            if (r1 >= within_r1 or
                r2 <= within_r2):
                if r1 > within_r1:
                    start_row = r1
                else:
                    start_row = within_r1
                if r2 < within_r2:
                    end_row = r2
                else:
                    end_row = within_r2
                srows.update(set(range(start_row, end_row)))
        for item in self.find_withtag("ColSelectFill"): 
            r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
            if (c1 >= within_c1 or
                c2 <= within_c2) or (within_c1 >= c1 and within_c2 <= c2):
                if c1 > within_c1:
                    start_col = c1
                else:
                    start_col = within_c1
                if c2 < within_c2:
                    end_col = c2
                else:
                    end_col = within_c2
                scols.update(set(range(start_col, end_col)))
                ac_scols.update(set(range(start_col, end_col)))
        for item in self.find_withtag("Current_Outside"):
            r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
            if (c1 >= within_c1 or
                c2 <= within_c2):
                if c1 > within_c1:
                    start_col = c1
                else:
                    start_col = within_c1
                if c2 < within_c2:
                    end_col = c2
                else:
                    end_col = within_c2
                scols.update(set(range(start_col, end_col)))
        if not self.show_selected_cells_border:
            iterable = chain(self.find_withtag("CellSelectFill"), self.find_withtag("Current_Outside"))
        else:
            iterable = self.find_withtag("CellSelectFill")
        for item in iterable:
            tags = self.gettags(item)
            r1, c1, r2, c2 = tuple(int(e) for e in tags[1].split("_") if e)
            if (r1 >= within_r1 or
                c1 >= within_c1 or
                r2 <= within_r2 or
                c2 <= within_c2) or (within_c1 >= c1 and within_c2 <= c2) or (within_r1 >= r1 and within_r2 <= r2):
                if r1 > within_r1:
                    start_row = r1
                else:
                    start_row = within_r1
                if c1 > within_c1:
                    start_col = c1
                else:
                    start_col = within_c1
                if r2 < within_r2:
                    end_row = r2
                else:
                    end_row = within_r2
                if c2 < within_c2:
                    end_col = c2
                else:
                    end_col = within_c2
                colsr = tuple(range(start_col, end_col))
                rowsr = tuple(range(start_row, end_row))
                scells.update(set(product(rowsr, colsr)))
                srows.update(set(range(start_row, end_row)))
                scols.update(set(range(start_col, end_col)))
        return scells, srows, scols, ac_srows, ac_scols

    def get_selected_min_max(self):
        min_x = float("inf")
        min_y = float("inf")
        max_x = 0
        max_y = 0
        for item in chain(self.find_withtag("CellSelectFill"),
                          self.find_withtag("RowSelectFill"),
                          self.find_withtag("ColSelectFill"),
                          self.find_withtag("Current_Inside"),
                          self.find_withtag("Current_Outside")):
            r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
            if r1 < min_y:
                min_y = r1
            if c1 < min_x:
                min_x = c1
            if r2 > max_y:
                max_y = r2
            if c2 > max_x:
                max_x = c2
        if min_x != float("inf") and min_y != float("inf") and max_x > 0 and max_y > 0:
            return min_y, min_x, max_y, max_x
        else:
            return None, None, None, None

    def get_selected_rows(self, get_cells = False, within_range = None, get_cells_as_rows = False):
        s = set()
        if within_range is not None:
            within_r1 = within_range[0]
            within_r2 = within_range[1]
        if get_cells:
            if within_range is None:
                for item in self.find_withtag("RowSelectFill"):
                    r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
                    s.update(set(product(range(r1, r2), range(0, len(self.col_positions) - 1))))
                if get_cells_as_rows:
                    s.update(self.get_selected_cells())
            else:
                for item in self.find_withtag("RowSelectFill"):
                    r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
                    if (r1 >= within_r1 or
                        r2 <= within_r2):
                        if r1 > within_r1:
                            start_row = r1
                        else:
                            start_row = within_r1
                        if r2 < within_r2:
                            end_row = r2
                        else:
                            end_row = within_r2
                        s.update(set(product(range(start_row, end_row), range(0, len(self.col_positions) - 1))))
                if get_cells_as_rows:
                    s.update(self.get_selected_cells(within_range = (within_r1, 0, within_r2, len(self.col_positions) - 1)))
        else:
            if within_range is None:
                for item in self.find_withtag("RowSelectFill"):
                    r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
                    s.update(set(range(r1, r2)))
                if get_cells_as_rows:
                    s.update(set(tup[0] for tup in self.get_selected_cells()))
            else:
                for item in self.find_withtag("RowSelectFill"):
                    r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
                    if (r1 >= within_r1 or
                        r2 <= within_r2):
                        if r1 > within_r1:
                            start_row = r1
                        else:
                            start_row = within_r1
                        if r2 < within_r2:
                            end_row = r2
                        else:
                            end_row = within_r2
                        s.update(set(range(start_row, end_row)))
                if get_cells_as_rows:
                    s.update(set(tup[0] for tup in self.get_selected_cells(within_range = (within_r1, 0, within_r2, len(self.col_positions) - 1))))
        return s

    def get_selected_cols(self, get_cells = False, within_range = None, get_cells_as_cols = False):
        s = set()
        if within_range is not None:
            within_c1 = within_range[0]
            within_c2 = within_range[1]
        if get_cells:
            if within_range is None:
                for item in self.find_withtag("ColSelectFill"):
                    r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
                    s.update(set(product(range(c1, c2), range(0, len(self.row_positions) - 1))))
                if get_cells_as_cols:
                    s.update(self.get_selected_cells())
            else:
                for item in self.find_withtag("ColSelectFill"):
                    r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
                    if (c1 >= within_c1 or
                        c2 <= within_c2):
                        if c1 > within_c1:
                            start_col = c1
                        else:
                            start_col = within_c1
                        if c2 < within_c2:
                            end_col = c2
                        else:
                            end_col = within_c2
                        s.update(set(product(range(start_col, end_col), range(0, len(self.row_positions) - 1))))
                if get_cells_as_cols:
                    s.update(self.get_selected_cells(within_range = (0, within_c1, len(self.row_positions) - 1, within_c2)))
        else:
            if within_range is None:
                for item in self.find_withtag("ColSelectFill"):
                    r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
                    s.update(set(range(c1, c2)))
                if get_cells_as_cols:
                    s.update(set(tup[1] for tup in self.get_selected_cells()))
            else:
                for item in self.find_withtag("ColSelectFill"):
                    r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
                    if (c1 >= within_c1 or
                        c2 <= within_c2):
                        if c1 > within_c1:
                            start_col = c1
                        else:
                            start_col = within_c1
                        if c2 < within_c2:
                            end_col = c2
                        else:
                            end_col = within_c2
                        s.update(set(range(start_col, end_col)))
                if get_cells_as_cols:
                    s.update(set(tup[0] for tup in self.get_selected_cells(within_range = (0, within_c1, len(self.row_positions) - 1, within_c2))))
        return s

    def get_selected_cells(self, get_rows = False, get_cols = False, within_range = None):
        s = set()
        if within_range is not None:
            within_r1 = within_range[0]
            within_c1 = within_range[1]
            within_r2 = within_range[2]
            within_c2 = within_range[3]
        if get_cols and get_rows:
            iterable = chain(self.find_withtag("CellSelectFill"), self.find_withtag("RowSelectFill"), self.find_withtag("ColSelectFill"), self.find_withtag("Current_Outside"))
        elif get_rows and not get_cols:
            iterable = chain(self.find_withtag("CellSelectFill"), self.find_withtag("RowSelectFill"), self.find_withtag("Current_Outside"))
        elif get_cols and not get_rows:
            iterable = chain(self.find_withtag("CellSelectFill"), self.find_withtag("ColSelectFill"), self.find_withtag("Current_Outside"))
        else:
            iterable = chain(self.find_withtag("CellSelectFill"), self.find_withtag("Current_Outside"))
        if within_range is None:
            for item in iterable:
                r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
                s.update(set(product(range(r1, r2), range(c1, c2))))
        else:
            for item in iterable:
                r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
                if (r1 >= within_r1 or
                    c1 >= within_c1 or
                    r2 <= within_r2 or
                    c2 <= within_c2):
                    if r1 > within_r1:
                        start_row = r1
                    else:
                        start_row = within_r1
                    if c1 > within_c1:
                        start_col = c1
                    else:
                        start_col = within_c1
                    if r2 < within_r2:
                        end_row = r2
                    else:
                        end_row = within_r2
                    if c2 < within_c2:
                        end_col = c2
                    else:
                        end_col = within_c2
                    s.update(set(product(range(start_row, end_row), range(start_col, end_col))))
        return s

    def get_all_selection_boxes(self):
        return tuple(tuple(int(e) for e in self.gettags(item)[1].split("_") if e) for item in chain(self.find_withtag("CellSelectFill"),
                                                                                                    self.find_withtag("RowSelectFill"),
                                                                                                    self.find_withtag("ColSelectFill"),
                                                                                                    self.find_withtag("Current_Outside")))

    def get_all_selection_boxes_with_types(self):
        boxes = []
        for item in sorted(self.find_withtag("CellSelectFill") + self.find_withtag("RowSelectFill") + self.find_withtag("ColSelectFill") + self.find_withtag("Current_Outside")):
            tags = self.gettags(item)
            if tags:
                if tags[0].startswith(("Cell", "Current")):
                    boxes.append((tuple(int(e) for e in tags[1].split("_") if e), "cells"))
                elif tags[0].startswith("Row"):
                    boxes.append((tuple(int(e) for e in tags[1].split("_") if e), "rows"))
                elif tags[0].startswith("Col"):
                    boxes.append((tuple(int(e) for e in tags[1].split("_") if e), "cols"))
        return boxes
    
    def is_cell_selected(self, r, c, inc_cols = False, inc_rows = False):
        if not inc_cols and not inc_rows:
            iterable = chain(self.find_withtag("CellSelectFill"), self.find_withtag("Current_Inside"), self.find_withtag("Current_Outside"))
        elif inc_cols and not inc_rows:
            iterable = chain(self.find_withtag("ColSelectFill"), self.find_withtag("CellSelectFill"), self.find_withtag("Current_Inside"), self.find_withtag("Current_Outside"))
        elif not inc_cols and inc_rows:
            iterable = chain(self.find_withtag("RowSelectFill"), self.find_withtag("CellSelectFill"), self.find_withtag("Current_Inside"), self.find_withtag("Current_Outside"))
        elif inc_cols and inc_rows:
            iterable = chain(self.find_withtag("RowSelectFill"), self.find_withtag("ColSelectFill"), self.find_withtag("CellSelectFill"), self.find_withtag("Current_Inside"), self.find_withtag("Current_Outside"))
        for item in iterable:
            r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
            if r1 <= r and c1 <= c and r2 > r and c2 > c:
                return True
        return False

    def is_col_selected(self, c):
        for item in self.find_withtag("ColSelectFill"):
            r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
            if c1 <= c and c2 > c:
                return True
        return False

    def is_row_selected(self, r):
        for item in self.find_withtag("RowSelectFill"):
            r1, c1, r2, c2 = tuple(int(e) for e in self.gettags(item)[1].split("_") if e)
            if r1 <= r and r2 > r:
                return True
        return False

    def anything_selected(self, exclude_columns = False, exclude_rows = False, exclude_cells = False):
        if exclude_columns and exclude_rows and not exclude_cells:
            if self.find_withtag("CellSelectFill") or self.find_withtag("Current_Outside"):
                return True
        elif exclude_columns and exclude_cells and not exclude_rows:
            if self.find_withtag("RowSelectFill"):
                return True
        elif exclude_rows and exclude_cells and not exclude_columns:
            if self.find_withtag("ColSelectFill"):
                return True
            
        elif exclude_columns and not exclude_rows and not exclude_cells:
            if self.find_withtag("CellSelectFill") or self.find_withtag("RowSelectFill") or self.find_withtag("Current_Outside"):
                return True
        elif exclude_rows and not exclude_columns and not exclude_cells:
            if self.find_withtag("CellSelectFill") or self.find_withtag("ColSelectFill") or self.find_withtag("Current_Outside"):
                return True
        elif exclude_cells and not exclude_columns and not exclude_rows:
            if self.find_withtag("RowSelectFill") or self.find_withtag("ColSelectFill"):
                return True
            
        elif not exclude_columns and not exclude_rows and not exclude_cells:
            if self.find_withtag("CellSelectFill") or self.find_withtag("RowSelectFill") or self.find_withtag("ColSelectFill") or self.find_withtag("Current_Outside"):
                return True
        return False

    def hide_current(self):
        items = self.find_withtag("Current_Inside") + self.find_withtag("Current_Outside")
        for item in items:
            self.itemconfig(item, state = "hidden")

    def show_current(self):
        items = self.find_withtag("Current_Inside") + self.find_withtag("Current_Outside")
        for item in items:
            self.itemconfig(item, state = "normal")

    def edit_cell_(self, event = None):
        if not self.anything_selected(exclude_columns = True, exclude_rows = True) or self.text_editor_id is not None:
            return
        currently_selected = self.currently_selected()
        y1 = int(currently_selected[0])
        x1 = int(currently_selected[1])
        if event.char in all_chars:
            text = event.char
        else:
            text = self.data_ref[y1][x1]
        self.select_cell(r = y1, c = x1, keep_other_selections = True)
        self.see(r = y1, c = x1, keep_yscroll = False, keep_xscroll = False, bottom_right_corner = False, check_cell_visibility = True)
        self.RI.set_row_height(y1, only_set_if_too_small = True)
        self.CH.set_col_width(x1, only_set_if_too_small = True)
        self.refresh()
        self.create_text_editor(r = y1, c = x1, text = text, set_data_ref_on_destroy = True)
        
    def create_text_editor(self, r = 0, c = 0, text = None, state = "normal", see = True, set_data_ref_on_destroy = False):
        if see:
            self.see(r = r, c = c, check_cell_visibility = True)
        x = self.col_positions[c]
        y = self.row_positions[r]
        w = self.col_positions[c + 1] - x + 1
        h = self.row_positions[r + 1] - y + 6
        if text is None:
            text = ""
        self.hide_current()
        if self.text_editor_id is not None:
            self.destroy_text_editor()
        self.text_editor = TextEditor(self, text = text, font = self.my_font, state = state, width = w, height = h, border_color = self.selected_cells_border_col, show_border = self.show_selected_cells_border)
        self.text_editor_id = self.create_window((x, y), window = self.text_editor, anchor = "nw")
        self.text_editor.textedit.bind("<Alt-Return>", self.text_editor_newline_binding)
        if set_data_ref_on_destroy:
            self.text_editor.textedit.bind("<Return>", lambda x: self.get_text_editor_value((r, c)))
            self.text_editor.textedit.bind("<FocusOut>", lambda x: self.get_text_editor_value((r, c)))
            self.text_editor.textedit.focus_set()
        self.text_editor.scroll_to_bottom()

    def bind_text_editor_destroy(self, binding, r, c):
        self.text_editor.textedit.bind("<Return>", lambda x: binding((r, c)))
        self.text_editor.textedit.bind("<FocusOut>", lambda x: binding((r, c)))
        self.text_editor.textedit.focus_set()

    def destroy_text_editor(self):
        try:
            self.delete(self.text_editor_id)
        except:
            pass
        try:
            self.text_editor.destroy()
        except:
            pass
        try:
            self.text_editor_id = None
        except:
            pass
        try:
            self.text_editor = None
        except:
            pass

    def text_editor_newline_binding(self, event = None):
        self.text_editor.config(height = self.text_editor.winfo_height() + self.xtra_lines_increment)

    def get_text_editor_value(self, destroy_tup = None, r = None, c = None, set_data_ref_on_destroy = True, event = None, destroy = True, move_down = True, redraw = True, recreate = True):
        self.show_current()
        if self.text_editor is not None:
            self.text_editor_value = self.text_editor.get()
        if destroy:
            self.destroy_text_editor()
        if set_data_ref_on_destroy:
            if r is None and c is None and destroy_tup:
                r, c = destroy_tup[0], destroy_tup[1]
            if r > len(self.data_ref) - 1:
                self.data_ref.extend([list(repeat("", c + 1)) for r in range((r + 1) - len(self.data_ref))])
            elif c > len(self.data_ref[r]) - 1:
                self.data_ref[r].extend(list(repeat("", (c + 1) - len(self.data_ref[r]))))
            if self.undo_enabled:
                if self.all_columns_displayed:
                    self.undo_storage.append(zlib.compress(pickle.dumps(("edit_cells", {(r, c): f"{self.data_ref[r][c]}"}, (((r, c, r + 1, c + 1), "cells"), ), self.currently_selected()))))
                else:
                    self.undo_storage.append(zlib.compress(pickle.dumps(("edit_cells",
                                                                         {(r, self.displayed_columns[c]): f"{self.data_ref[r][self.displayed_columns[c]]}"},
                                                                         (((r, c, r + 1, c + 1), "cells"), ),
                                                                         self.currently_selected()))))
            if self.all_columns_displayed:
                self.data_ref[r][c] = self.text_editor_value
            else:
                self.data_ref[r][self.displayed_columns[c]] = self.text_editor_value
            self.RI.set_row_height(r, recreate = False)
            self.CH.set_col_width(c, only_set_if_too_small = True)
            if self.extra_edit_cell_func is not None:
                self.extra_edit_cell_func((r, c))
        if move_down:
            if r is None and c is None and destroy_tup:
                r, c = destroy_tup[0], destroy_tup[1]
            currently_selected = self.currently_selected()
            if r is not None and c is not None:
                if (
                    currently_selected and
                    r == currently_selected[0] and
                    c == currently_selected[1] and
                    r < len(self.row_positions) - 2 and
                    (self.single_selection_enabled or self.toggle_selection_enabled)
                    ):
                    self.select_cell(r + 1, c)
                    self.see(r + 1, c, keep_xscroll = True, bottom_right_corner = True, check_cell_visibility = True)
        if redraw:
            self.refresh()
        if recreate:
            self.recreate_all_selection_boxes()
        self.focus_set()
        return self.text_editor_value

    def create_dropdown(self, r = 0, c = 0, values = [], set_value = None, state = "readonly", see = True, destroy_on_select = True, current = False):
        if see:
            if not self.cell_is_completely_visible(r = r, c = c):
                self.see(r = r, c = c, check_cell_visibility = False)
        x = self.col_positions[c]
        y = self.row_positions[r]
        w = self.GetWidthChars(self.col_positions[c + 1] - x)
        self.table_dropdown = TableDropdown(self, font = self.my_font, state = state, values = values, set_value = set_value, width = w)
        self.table_dropdown_id = self.create_window((x, y), window = self.table_dropdown, anchor = "nw")
        if destroy_on_select:
            self.table_dropdown.bind("<<ComboboxSelected>>", lambda event: self.get_dropdown_value(current = current))

    def get_dropdown_value(self, event = None, current = False, destroy = True):
        if self.table_dropdown is not None:
            if current:
                self.table_dropdown_value = self.table_dropdown.current()
            else:
                self.table_dropdown_value = self.table_dropdown.get_my_value()
        if destroy:
            try:
                self.delete(self.table_dropdown_id)
                self.table_dropdown.destroy()
            except:
                pass
            self.table_dropdown = None
        return self.table_dropdown_value
    

