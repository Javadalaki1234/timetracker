"""
برنامه ثبت ساعات کاری - نسخه موبایل اندروید
ساخته‌شده با Kivy + KivyMD برای ظاهر مناسب موبایل
"""

import json
import os
from datetime import datetime, timedelta

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon, MDIconButton
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
)
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    MDList,
    MDListItem,
    MDListItemHeadlineText,
    MDListItemSupportingText,
    MDListItemTrailingCheckbox,
)
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem, MDNavigationItemIcon, MDNavigationItemLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText


# ---------- KV Layout ----------
KV = """
#:import dp kivy.metrics.dp

MDScreenManager:
    id: screen_manager

    # ===== صفحه تایمر =====
    MDScreen:
        name: "timer"
        md_bg_color: app.theme_cls.backgroundColor

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(12)

            MDLabel:
                text: "تایمر جلسه"
                font_style: "Headline"
                role: "small"
                halign: "center"
                size_hint_y: None
                height: dp(40)

            MDCard:
                style: "elevated"
                padding: dp(20)
                size_hint_y: None
                height: dp(140)
                radius: [16]

                MDLabel:
                    id: timer_label
                    text: "0:00:00"
                    font_style: "Display"
                    role: "medium"
                    halign: "center"
                    bold: True

            MDLabel:
                id: active_project_label
                text: "پروژه: —"
                font_style: "Title"
                role: "medium"
                halign: "center"
                size_hint_y: None
                height: dp(36)

            MDTextField:
                id: remark_field
                mode: "outlined"
                hint_text: "توضیحات جلسه (اختیاری)"
                multiline: True
                size_hint_y: None
                height: dp(80)

            MDBoxLayout:
                orientation: "horizontal"
                spacing: dp(10)
                size_hint_y: None
                height: dp(56)
                adaptive_height: True

                MDButton:
                    id: start_btn
                    style: "filled"
                    on_release: app.start_timer()
                    size_hint_x: 1
                    MDButtonText:
                        text: "▶ شروع"
                        pos_hint: {"center_x": .5, "center_y": .5}

                MDButton:
                    id: stop_btn
                    style: "filled"
                    on_release: app.stop_timer()
                    disabled: True
                    size_hint_x: 1
                    MDButtonText:
                        text: "■ توقف و ذخیره"
                        pos_hint: {"center_x": .5, "center_y": .5}

            MDButton:
                style: "outlined"
                on_release: app.reset_timer()
                size_hint_y: None
                height: dp(48)
                MDButtonText:
                    text: "بازنشانی"
                    pos_hint: {"center_x": .5, "center_y": .5}

            Widget:
                size_hint_y: 1

    # ===== صفحه پروژه‌ها =====
    MDScreen:
        name: "projects"
        md_bg_color: app.theme_cls.backgroundColor

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(12)
            spacing: dp(8)

            MDLabel:
                text: "مدیریت پروژه‌ها"
                font_style: "Headline"
                role: "small"
                halign: "center"
                size_hint_y: None
                height: dp(40)

            MDBoxLayout:
                orientation: "horizontal"
                spacing: dp(8)
                size_hint_y: None
                height: dp(56)

                MDTextField:
                    id: project_name_field
                    mode: "outlined"
                    hint_text: "نام پروژه جدید"
                    size_hint_x: 0.7

                MDButton:
                    style: "filled"
                    on_release: app.add_project()
                    size_hint_x: 0.3
                    MDButtonText:
                        text: "افزودن"
                        pos_hint: {"center_x": .5, "center_y": .5}

            MDLabel:
                id: selected_project_label
                text: "پروژه انتخاب‌شده: —"
                font_style: "Body"
                role: "large"
                halign: "right"
                size_hint_y: None
                height: dp(32)

            MDScrollView:
                MDList:
                    id: project_list
                    spacing: dp(4)

            MDButton:
                style: "tonal"
                on_release: app.delete_project()
                size_hint_y: None
                height: dp(48)
                MDButtonText:
                    text: "حذف پروژه و تمام سوابق آن"
                    pos_hint: {"center_x": .5, "center_y": .5}

    # ===== صفحه تاریخچه =====
    MDScreen:
        name: "history"
        md_bg_color: app.theme_cls.backgroundColor

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(12)
            spacing: dp(8)

            MDLabel:
                text: "تاریخچه جلسات"
                font_style: "Headline"
                role: "small"
                halign: "center"
                size_hint_y: None
                height: dp(40)

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: dp(48)
                spacing: dp(8)

                MDButton:
                    style: "tonal"
                    on_release: app.delete_selected_sessions()
                    size_hint_x: 1
                    MDButtonText:
                        text: "حذف جلسات انتخاب‌شده"
                        pos_hint: {"center_x": .5, "center_y": .5}

            MDScrollView:
                MDList:
                    id: history_list
                    spacing: dp(4)

    # ===== صفحه گزارش =====
    MDScreen:
        name: "report"
        md_bg_color: app.theme_cls.backgroundColor

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(12)
            spacing: dp(10)

            MDLabel:
                text: "گزارش ساعات"
                font_style: "Headline"
                role: "small"
                halign: "center"
                size_hint_y: None
                height: dp(40)

            MDBoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: dp(48)
                spacing: dp(8)

                MDButton:
                    id: period_btn
                    style: "outlined"
                    on_release: app.open_period_menu()
                    size_hint_x: 0.45
                    MDButtonText:
                        id: period_btn_text
                        text: "روز"
                        pos_hint: {"center_x": .5, "center_y": .5}

                MDLabel:
                    id: total_all_label
                    text: "کل: 0:00:00"
                    font_style: "Title"
                    role: "medium"
                    halign: "right"
                    size_hint_x: 0.55

            MDLabel:
                id: period_total_label
                text: "مجموع بازه: 0:00:00"
                font_style: "Title"
                role: "large"
                halign: "center"
                bold: True
                size_hint_y: None
                height: dp(40)

            MDScrollView:
                MDList:
                    id: report_list
                    spacing: dp(4)

# نوار پایین ناوبری
MDBoxLayout:
    orientation: "vertical"

    MDScreenManager:
        id: content_manager

    MDNavigationBar:
        id: nav_bar
        on_switch_tabs: app.on_switch_tabs(*args)

        MDNavigationItem:
            active: True
            MDNavigationItemIcon:
                icon: "timer-outline"
            MDNavigationItemLabel:
                text: "تایمر"

        MDNavigationItem:
            MDNavigationItemIcon:
                icon: "folder-outline"
            MDNavigationItemLabel:
                text: "پروژه‌ها"

        MDNavigationItem:
            MDNavigationItemIcon:
                icon: "history"
            MDNavigationItemLabel:
                text: "تاریخچه"

        MDNavigationItem:
            MDNavigationItemIcon:
                icon: "chart-bar"
            MDNavigationItemLabel:
                text: "گزارش"
"""


class TimeTrackerApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "ثبت ساعات کاری"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        self.projects = []
        self.sessions = []
        self.running = False
        self.start_time = None
        self.selected_project = None
        self.period = "روز"
        self._selected_history_iids = set()

        # مسیر ذخیره داده (روی اندروید در پوشه خصوصی اپ)
        if platform == "android":
            from android.storage import app_storage_path
            self.data_dir = app_storage_path()
        else:
            self.data_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(self.data_dir, "time_tracker_data.json")

    def build(self):
        self.root = Builder.load_string(KV)
        # ساخت ساختار اصلی با ناوبری پایین
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
        from kivymd.uix.navigationbar import MDNavigationItemIcon, MDNavigationItemLabel

        main = MDBoxLayout(orientation="vertical")
        self.sm = MDScreenManager()

        # اضافه کردن صفحات
        timer_screen = self.root.get_screen("timer") if hasattr(self.root, "get_screen") else None

        # چون KV بالا یک ScreenManager است، آن را مستقیماً استفاده می‌کنیم
        # اما برای ناوبری پایین ساختار را دوباره می‌چینیم
        return self._build_ui()

    def _build_ui(self):
        """ساخت رابط کاربری اصلی با ناوبری پایین"""
        from kivy.uix.floatlayout import FloatLayout

        root = MDBoxLayout(orientation="vertical")

        self.sm = MDScreenManager()
        self.sm.add_widget(self._create_timer_screen())
        self.sm.add_widget(self._create_projects_screen())
        self.sm.add_widget(self._create_history_screen())
        self.sm.add_widget(self._create_report_screen())

        root.add_widget(self.sm)

        # نوار ناوبری پایین
        nav = MDNavigationBar(on_switch_tabs=self.on_switch_tabs)
        for icon, text, name in [
            ("timer-outline", "تایمر", "timer"),
            ("folder-outline", "پروژه‌ها", "projects"),
            ("history", "تاریخچه", "history"),
            ("chart-bar", "گزارش", "report"),
        ]:
            item = MDNavigationItem()
            item.add_widget(MDNavigationItemIcon(icon=icon))
            item.add_widget(MDNavigationItemLabel(text=text))
            if name == "timer":
                item.active = True
            nav.add_widget(item)

        root.add_widget(nav)
        self.nav_bar = nav
        return root

    def _create_timer_screen(self):
        screen = MDScreen(name="timer")
        box = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        title = MDLabel(
            text="تایمر جلسه",
            font_style="Headline",
            role="small",
            halign="center",
            size_hint_y=None,
            height=dp(40),
        )
        box.add_widget(title)

        card = MDCard(style="elevated", padding=dp(20), size_hint_y=None, height=dp(140), radius=[16])
        self.timer_label = MDLabel(
            text="0:00:00",
            font_style="Display",
            role="medium",
            halign="center",
            bold=True,
        )
        card.add_widget(self.timer_label)
        box.add_widget(card)

        self.active_project_label = MDLabel(
            text="پروژه: —",
            font_style="Title",
            role="medium",
            halign="center",
            size_hint_y=None,
            height=dp(36),
        )
        box.add_widget(self.active_project_label)

        self.remark_field = MDTextField(
            mode="outlined",
            hint_text="توضیحات جلسه (اختیاری)",
            multiline=True,
            size_hint_y=None,
            height=dp(80),
        )
        box.add_widget(self.remark_field)

        btn_row = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(56))

        self.start_btn = MDButton(style="filled", on_release=lambda x: self.start_timer(), size_hint_x=1)
        self.start_btn.add_widget(MDButtonText(text="▶ شروع", pos_hint={"center_x": 0.5, "center_y": 0.5}))
        btn_row.add_widget(self.start_btn)

        self.stop_btn = MDButton(style="filled", on_release=lambda x: self.stop_timer(), disabled=True, size_hint_x=1)
        self.stop_btn.add_widget(MDButtonText(text="■ توقف و ذخیره", pos_hint={"center_x": 0.5, "center_y": 0.5}))
        btn_row.add_widget(self.stop_btn)

        box.add_widget(btn_row)

        reset_btn = MDButton(style="outlined", on_release=lambda x: self.reset_timer(), size_hint_y=None, height=dp(48))
        reset_btn.add_widget(MDButtonText(text="بازنشانی", pos_hint={"center_x": 0.5, "center_y": 0.5}))
        box.add_widget(reset_btn)

        # فضای خالی
        from kivy.uix.widget import Widget
        box.add_widget(Widget(size_hint_y=1))

        screen.add_widget(box)
        return screen

    def _create_projects_screen(self):
        screen = MDScreen(name="projects")
        box = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        title = MDLabel(
            text="مدیریت پروژه‌ها",
            font_style="Headline",
            role="small",
            halign="center",
            size_hint_y=None,
            height=dp(40),
        )
        box.add_widget(title)

        add_row = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(56))
        self.project_name_field = MDTextField(mode="outlined", hint_text="نام پروژه جدید", size_hint_x=0.7)
        add_row.add_widget(self.project_name_field)

        add_btn = MDButton(style="filled", on_release=lambda x: self.add_project(), size_hint_x=0.3)
        add_btn.add_widget(MDButtonText(text="افزودن", pos_hint={"center_x": 0.5, "center_y": 0.5}))
        add_row.add_widget(add_btn)
        box.add_widget(add_row)

        self.selected_project_label = MDLabel(
            text="پروژه انتخاب‌شده: —",
            font_style="Body",
            role="large",
            halign="right",
            size_hint_y=None,
            height=dp(32),
        )
        box.add_widget(self.selected_project_label)

        scroll = MDScrollView()
        self.project_list = MDList(spacing=dp(4))
        scroll.add_widget(self.project_list)
        box.add_widget(scroll)

        del_btn = MDButton(style="tonal", on_release=lambda x: self.delete_project(), size_hint_y=None, height=dp(48))
        del_btn.add_widget(MDButtonText(text="حذف پروژه و تمام سوابق آن", pos_hint={"center_x": 0.5, "center_y": 0.5}))
        box.add_widget(del_btn)

        screen.add_widget(box)
        return screen

    def _create_history_screen(self):
        screen = MDScreen(name="history")
        box = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        title = MDLabel(
            text="تاریخچه جلسات",
            font_style="Headline",
            role="small",
            halign="center",
            size_hint_y=None,
            height=dp(40),
        )
        box.add_widget(title)

        del_btn = MDButton(style="tonal", on_release=lambda x: self.delete_selected_sessions(), size_hint_y=None, height=dp(48))
        del_btn.add_widget(MDButtonText(text="حذف جلسات انتخاب‌شده", pos_hint={"center_x": 0.5, "center_y": 0.5}))
        box.add_widget(del_btn)

        scroll = MDScrollView()
        self.history_list = MDList(spacing=dp(4))
        scroll.add_widget(self.history_list)
        box.add_widget(scroll)

        screen.add_widget(box)
        return screen

    def _create_report_screen(self):
        screen = MDScreen(name="report")
        box = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))

        title = MDLabel(
            text="گزارش ساعات",
            font_style="Headline",
            role="small",
            halign="center",
            size_hint_y=None,
            height=dp(40),
        )
        box.add_widget(title)

        top_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(8))
        self.period_btn = MDButton(style="outlined", on_release=lambda x: self.open_period_menu(), size_hint_x=0.4)
        self.period_btn_text = MDButtonText(text="روز", pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.period_btn.add_widget(self.period_btn_text)
        top_row.add_widget(self.period_btn)

        self.total_all_label = MDLabel(
            text="کل: 0:00:00",
            font_style="Title",
            role="medium",
            halign="right",
            size_hint_x=0.6,
        )
        top_row.add_widget(self.total_all_label)
        box.add_widget(top_row)

        self.period_total_label = MDLabel(
            text="مجموع بازه: 0:00:00",
            font_style="Title",
            role="large",
            halign="center",
            bold=True,
            size_hint_y=None,
            height=dp(40),
        )
        box.add_widget(self.period_total_label)

        scroll = MDScrollView()
        self.report_list = MDList(spacing=dp(4))
        scroll.add_widget(self.report_list)
        box.add_widget(scroll)

        screen.add_widget(box)
        return screen

    def on_start(self):
        self.load_data()
        self.refresh_projects()
        self.update_summary()
        Clock.schedule_interval(self.update_timer_display, 0.25)

        # منوی بازه زمانی
        self.period_menu = MDDropdownMenu(
            caller=self.period_btn,
            items=[
                {"text": "روز", "on_release": lambda: self.set_period("روز")},
                {"text": "هفته", "on_release": lambda: self.set_period("هفته")},
                {"text": "ماه", "on_release": lambda: self.set_period("ماه")},
            ],
            width=dp(160),
        )

    def on_switch_tabs(self, bar, item, item_icon, item_text):
        mapping = {"تایمر": "timer", "پروژه‌ها": "projects", "تاریخچه": "history", "گزارش": "report"}
        name = mapping.get(item_text, "timer")
        self.sm.current = name
        if name == "history":
            self.refresh_history()
        elif name == "report":
            self.update_summary()
        elif name == "projects":
            self.refresh_projects()

    # ---------- داده ----------
    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.projects = data.get("projects", [])
                self.sessions = data.get("sessions", [])
                self.projects = list(dict.fromkeys(
                    p for p in self.projects if isinstance(p, str) and p.strip()
                ))
                self.sessions = [
                    s for s in self.sessions
                    if isinstance(s, dict) and s.get("project")
                ]
        except Exception as e:
            self.show_snackbar(f"خطا در بارگذاری: {e}")
            self.projects, self.sessions = [], []

    def save_data(self):
        data = {"projects": self.projects, "sessions": self.sessions}
        temp = self.data_file + ".tmp"
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(temp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(temp, self.data_file)
            return True
        except Exception as e:
            self.show_snackbar(f"خطا در ذخیره: {e}")
            try:
                if os.path.exists(temp):
                    os.remove(temp)
            except OSError:
                pass
            return False

    # ---------- پروژه‌ها ----------
    def add_project(self):
        name = self.project_name_field.text.strip()
        if not name:
            self.show_snackbar("نام پروژه را وارد کنید")
            return
        if name in self.projects:
            self.show_snackbar("این پروژه قبلاً اضافه شده")
            return
        self.projects.append(name)
        if self.save_data():
            self.project_name_field.text = ""
            self.refresh_projects()
            self.select_project(name)

    def refresh_projects(self):
        self.project_list.clear_widgets()
        for project in self.projects:
            seconds = sum(
                self.time_to_seconds(s.get("duration", "0:00:00"))
                for s in self.sessions if s.get("project") == project
            )
            item = MDListItem(
                on_release=lambda x, p=project: self.select_project(p),
            )
            item.add_widget(MDListItemHeadlineText(text=project))
            item.add_widget(MDListItemSupportingText(text=f"مجموع: {self.seconds_to_time(seconds)}"))
            self.project_list.add_widget(item)

        if self.selected_project and self.selected_project in self.projects:
            self.selected_project_label.text = f"پروژه انتخاب‌شده: {self.selected_project}"
        else:
            self.selected_project = None
            self.selected_project_label.text = "پروژه انتخاب‌شده: —"

    def select_project(self, name):
        if name not in self.projects:
            return
        self.selected_project = name
        self.selected_project_label.text = f"پروژه انتخاب‌شده: {name}"
        if not self.running:
            self.active_project_label.text = f"پروژه: {name}"

    def delete_project(self):
        project = self.selected_project
        if not project:
            self.show_snackbar("ابتدا پروژه‌ای را انتخاب کنید")
            return
        if self.running:
            self.show_snackbar("ابتدا تایمر را متوقف کنید")
            return
        count = sum(1 for s in self.sessions if s.get("project") == project)

        def confirm_delete(*args):
            self.projects = [p for p in self.projects if p != project]
            self.sessions = [s for s in self.sessions if s.get("project") != project]
            self.selected_project = None
            if self.save_data():
                self.refresh_projects()
                self.selected_project_label.text = "پروژه انتخاب‌شده: —"
                self.active_project_label.text = "پروژه: —"
                self.show_snackbar("پروژه حذف شد")
            dialog.dismiss()

        dialog = MDDialog(
            MDDialogHeadlineText(text="تأیید حذف پروژه"),
            MDDialogSupportingText(
                text=f"پروژه «{project}» و تمام {count} جلسه آن حذف شوند؟\nاین عمل قابل بازگشت نیست."
            ),
            MDDialogButtonContainer(
                MDButton(style="text", on_release=lambda x: dialog.dismiss(),
                         children=[MDButtonText(text="انصراف")]),
                MDButton(style="text", on_release=confirm_delete,
                         children=[MDButtonText(text="حذف")]),
                spacing="8dp",
            ),
        )
        dialog.open()

    # ---------- تایمر ----------
    def start_timer(self):
        if self.running:
            return
        if not self.selected_project:
            self.show_snackbar("ابتدا یک پروژه انتخاب کنید")
            return
        self.running = True
        self.start_time = datetime.now()
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.active_project_label.text = f"در حال ثبت: {self.selected_project}"

    def stop_timer(self):
        if not self.running or not self.start_time:
            return
        end_time = datetime.now()
        seconds = max(0, int((end_time - self.start_time).total_seconds()))
        duration = self.seconds_to_time(seconds)
        session = {
            "project": self.selected_project,
            "date": self.start_time.strftime("%Y-%m-%d"),
            "time": self.start_time.strftime("%H:%M:%S"),
            "duration": duration,
            "remark": self.remark_field.text.strip(),
            "datetime": self.start_time.isoformat(),
        }
        self.sessions.append(session)
        if self.save_data():
            self.show_snackbar(f"ذخیره شد — مدت: {duration}")
        self.running = False
        self.start_time = None
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.remark_field.text = ""
        self.timer_label.text = "0:00:00"
        self.refresh_projects()
        self.active_project_label.text = f"پروژه: {self.selected_project or '—'}"

    def reset_timer(self):
        if self.running:
            def do_reset(*args):
                self.running = False
                self.start_time = None
                self.timer_label.text = "0:00:00"
                self.start_btn.disabled = False
                self.stop_btn.disabled = True
                self.remark_field.text = ""
                self.active_project_label.text = f"پروژه: {self.selected_project or '—'}"
                dialog.dismiss()

            dialog = MDDialog(
                MDDialogHeadlineText(text="تأیید"),
                MDDialogSupportingText(text="تایمر فعال متوقف شود و زمان ثبت‌نشده از بین برود؟"),
                MDDialogButtonContainer(
                    MDButton(style="text", on_release=lambda x: dialog.dismiss(),
                             children=[MDButtonText(text="خیر")]),
                    MDButton(style="text", on_release=do_reset,
                             children=[MDButtonText(text="بله")]),
                    spacing="8dp",
                ),
            )
            dialog.open()
            return

        self.timer_label.text = "0:00:00"
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.remark_field.text = ""
        self.active_project_label.text = f"پروژه: {self.selected_project or '—'}"

    def update_timer_display(self, dt):
        if self.running and self.start_time:
            seconds = int((datetime.now() - self.start_time).total_seconds())
            self.timer_label.text = self.seconds_to_time(max(0, seconds))

    # ---------- تاریخچه ----------
    def refresh_history(self):
        self.history_list.clear_widgets()
        self._selected_history_iids = set()
        sorted_sessions = sorted(
            enumerate(self.sessions),
            key=lambda pair: pair[1].get("datetime", ""),
            reverse=True,
        )
        for index, session in sorted_sessions:
            headline = f"{session.get('project', '')}  •  {session.get('duration', '')}"
            support = f"{session.get('date', '')}  {session.get('time', '')}"
            if session.get("remark"):
                support += f"  |  {session.get('remark')[:40]}"

            item = MDListItem()
            item.add_widget(MDListItemHeadlineText(text=headline))
            item.add_widget(MDListItemSupportingText(text=support))

            # چک‌باکس برای انتخاب
            checkbox = MDListItemTrailingCheckbox()
            checkbox.bind(active=lambda cb, val, idx=index: self._on_history_check(idx, val))
            item.add_widget(checkbox)
            self.history_list.add_widget(item)

    def _on_history_check(self, index, active):
        if active:
            self._selected_history_iids.add(index)
        else:
            self._selected_history_iids.discard(index)

    def delete_selected_sessions(self):
        if not self._selected_history_iids:
            self.show_snackbar("یک یا چند جلسه را انتخاب کنید")
            return
        count = len(self._selected_history_iids)

        def confirm(*args):
            indexes = self._selected_history_iids
            self.sessions = [s for i, s in enumerate(self.sessions) if i not in indexes]
            if self.save_data():
                self.refresh_projects()
                self.refresh_history()
                self.show_snackbar(f"{count} جلسه حذف شد")
            dialog.dismiss()

        dialog = MDDialog(
            MDDialogHeadlineText(text="تأیید حذف"),
            MDDialogSupportingText(text=f"{count} جلسه انتخاب‌شده حذف شود؟"),
            MDDialogButtonContainer(
                MDButton(style="text", on_release=lambda x: dialog.dismiss(),
                         children=[MDButtonText(text="انصراف")]),
                MDButton(style="text", on_release=confirm,
                         children=[MDButtonText(text="حذف")]),
                spacing="8dp",
            ),
        )
        dialog.open()

    # ---------- گزارش ----------
    def open_period_menu(self):
        self.period_menu.open()

    def set_period(self, period):
        self.period = period
        self.period_btn_text.text = period
        self.period_menu.dismiss()
        self.update_summary()

    def update_summary(self):
        total_seconds = sum(self.time_to_seconds(s.get("duration", "0:00:00")) for s in self.sessions)
        self.total_all_label.text = f"کل: {self.seconds_to_time(total_seconds)}"

        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())

        def in_period(session):
            try:
                d = datetime.strptime(session.get("date", ""), "%Y-%m-%d").date()
            except (ValueError, TypeError):
                return False
            if self.period == "روز":
                return d == today
            if self.period == "هفته":
                return week_start <= d <= today
            return d.year == today.year and d.month == today.month

        filtered = [s for s in self.sessions if in_period(s)]
        period_seconds = sum(self.time_to_seconds(s.get("duration", "0:00:00")) for s in filtered)
        self.period_total_label.text = f"مجموع {self.period}: {self.seconds_to_time(period_seconds)}"

        self.report_list.clear_widgets()
        for project in self.projects:
            seconds = sum(
                self.time_to_seconds(s.get("duration", "0:00:00"))
                for s in filtered if s.get("project") == project
            )
            if seconds == 0 and not filtered:
                continue
            item = MDListItem()
            item.add_widget(MDListItemHeadlineText(text=project))
            item.add_widget(MDListItemSupportingText(text=self.seconds_to_time(seconds)))
            self.report_list.add_widget(item)

    # ---------- ابزار ----------
    def show_snackbar(self, text):
        MDSnackbar(
            MDSnackbarText(text=text),
            y=dp(72),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            duration=2.5,
        ).open()

    @staticmethod
    def time_to_seconds(time_str):
        try:
            parts = str(time_str).split(":")
            if len(parts) != 3:
                return 0
            h, m, s = map(int, parts)
            return max(0, h * 3600 + m * 60 + s)
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def seconds_to_time(seconds):
        seconds = max(0, int(seconds))
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h}:{m:02d}:{s:02d}"


if __name__ == "__main__":
    # روی دسکتاپ اندازه شبیه‌سازی موبایل
    if platform != "android":
        Window.size = (400, 700)
    TimeTrackerApp().run()
