# main.py
# سیستم حسابگر پیشرفته طلا - نسخه Android
# ساخته شده بر اساس نسخه Windows/Tkinter

import os
import ast
import operator as op
from datetime import datetime

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView


# ============================================================
# تنظیمات اصلی
# ============================================================

Window.clearcolor = (0.043, 0.071, 0.125, 1)

TOLA_GRAM = 12.15
MITHQAL_GRAM = 4.6875
TROY_OUNCE_GRAM = 31.1034768
COMMON_PURITY = 23.88


# ============================================================
# رنگ‌ها
# ============================================================

BG_DARK = (0.043, 0.071, 0.125, 1)
BG_DEEP = (0.027, 0.051, 0.094, 1)
CARD = (0.082, 0.122, 0.200, 1)
CARD2 = (0.106, 0.161, 0.251, 1)
INPUT = (0.039, 0.071, 0.129, 1)

GOLD = (0.961, 0.722, 0.239, 1)
BLUE = (0.302, 0.553, 1, 1)
GREEN = (0.157, 0.820, 0.486, 1)
RED = (1, 0.361, 0.424, 1)

WHITE = (0.973, 0.980, 0.988, 1)
GRAY = (0.569, 0.627, 0.722, 1)
MUTED = (0.400, 0.459, 0.561, 1)


# ============================================================
# محاسبه امن ماشین حساب
# ============================================================

_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def safe_eval(expression):
    """
    محاسبه امن عبارت ریاضی
    بدون استفاده مستقیم از eval
    """

    expression = expression.replace("%", "/100").strip()

    if not expression:
        raise ValueError("عبارت خالی است")

    tree = ast.parse(expression, mode="eval")

    def calculate(node):

        if isinstance(node, ast.Expression):
            return calculate(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("عدد نامعتبر")

        if isinstance(node, ast.Num):
            return node.n

        if isinstance(node, ast.BinOp):
            if type(node.op) not in _ALLOWED_OPERATORS:
                raise ValueError("عملگر غیرمجاز")

            left = calculate(node.left)
            right = calculate(node.right)

            if isinstance(node.op, ast.Div) and right == 0:
                raise ValueError("تقسیم بر صفر")

            return _ALLOWED_OPERATORS[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp):
            if type(node.op) not in _ALLOWED_OPERATORS:
                raise ValueError("عملگر غیرمجاز")

            return _ALLOWED_OPERATORS[type(node.op)](
                calculate(node.operand)
            )

        raise ValueError("عبارت غیرمجاز")

    return calculate(tree)


# ============================================================
# ابزارهای عمومی
# ============================================================

def make_label(text="", size=14, color=WHITE, bold=False):
    label = Label(
        text=text,
        font_size=dp(size),
        color=color,
        bold=bold,
        halign="right",
        valign="middle",
    )
    label.bind(
        size=lambda instance, value:
        setattr(instance, "text_size", value)
    )
    return label


def make_input(value=""):
    field = TextInput(
        text=str(value),
        multiline=False,
        font_size=dp(15),
        foreground_color=WHITE,
        background_color=INPUT,
        cursor_color=GOLD,
        halign="center",
        padding=[dp(8), dp(8)],
    )
    return field


def make_button(text, background=GOLD, color=BG_DEEP, height=48):
    return Button(
        text=text,
        font_size=dp(14),
        bold=True,
        background_normal="",
        background_color=background,
        color=color,
        size_hint_y=None,
        height=dp(height),
    )


# ============================================================
# برنامه اصلی
# ============================================================

class GoldApp(App):

    def build(self):

        self.title = "سیستم حسابگر پیشرفته طلا"

        self.current_tab_name = "ماشین‌حساب"

        root = BoxLayout(
            orientation="vertical",
            spacing=0,
        )

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(82),
            padding=[dp(15), dp(8)],
            spacing=dp(10),
        )

        header.background_color = BG_DEEP

        title_box = BoxLayout(
            orientation="vertical",
        )

        title_box.add_widget(
            make_label(
                "سیستم حسابگر پیشرفته طلا",
                20,
                WHITE,
                True
            )
        )

        title_box.add_widget(
            make_label(
                "زرگری بیژن",
                11,
                GRAY,
                True
            )
        )

        header.add_widget(title_box)

        save_btn = make_button(
            "💾 ذخیره TXT",
            GREEN,
            BG_DEEP,
            48
        )
        save_btn.size_hint_x = None
        save_btn.width = dp(125)
        save_btn.bind(on_release=lambda x: self.save_current_tab())

        header.add_widget(save_btn)

        print_btn = make_button(
            "🖨 چاپ / اشتراک",
            GOLD,
            BG_DEEP,
            48
        )
        print_btn.size_hint_x = None
        print_btn.width = dp(135)
        print_btn.bind(on_release=lambda x: self.print_current_tab())

        header.add_widget(print_btn)

        root.add_widget(header)

        # ----------------------------------------------------
        # Tabs
        # ----------------------------------------------------

        self.tabs = TabbedPanel(
            do_default_tab=False,
            tab_width=dp(150),
            background_color=BG_DARK,
        )

        # ماشین حساب
        self.tab_calc = TabbedPanelItem(
            text="ماشین‌حساب"
        )
        self.tab_calc.content = self.build_calculator()
        self.tabs.add_widget(self.tab_calc)

        # خرید و فروش
        self.tab_trade = TabbedPanelItem(
            text="خرید و فروش"
        )
        self.tab_trade.content = self.build_trade()
        self.tabs.add_widget(self.tab_trade)

        # مبدل عیار
        self.tab_rates = TabbedPanelItem(
            text="مبدل عیار"
        )
        self.tab_rates.content = self.build_rates()
        self.tabs.add_widget(self.tab_rates)

        # تحلیل تبدیل
        self.tab_conversion = TabbedPanelItem(
            text="تحلیل تبدیل"
        )
        self.tab_conversion.content = self.build_conversion()
        self.tabs.add_widget(self.tab_conversion)

        # خمس دولتی
        self.tab_gov = TabbedPanelItem(
            text="خمس دولتی"
        )
        self.tab_gov.content = self.build_gov_khums()
        self.tabs.add_widget(self.tab_gov)

        self.tabs.bind(
            current_tab=self.on_tab_changed
        )

        root.add_widget(self.tabs)

        # ----------------------------------------------------
        # Footer
        # ----------------------------------------------------

        footer = BoxLayout(
            size_hint_y=None,
            height=dp(30),
        )

        footer.add_widget(
            make_label(
                "طلا | عیار 23.88 | 1 Tola = 12.15 g",
                9,
                MUTED,
                True
            )
        )

        root.add_widget(footer)

        return root


    # ========================================================
    # تغییر تب
    # ========================================================

    def on_tab_changed(self, instance, tab):

        if tab == self.tab_calc:
            self.current_tab_name = "ماشین‌حساب"

        elif tab == self.tab_trade:
            self.current_tab_name = "خرید و فروش طلا"

        elif tab == self.tab_rates:
            self.current_tab_name = "مبدل عیار طلا"

        elif tab == self.tab_conversion:
            self.current_tab_name = "تحلیل تبدیل طلا"

        elif tab == self.tab_gov:
            self.current_tab_name = "خمس دولتی"


    # ========================================================
    # ماشین حساب
    # ========================================================

    def build_calculator(self):

        root = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(10),
        )

        root.add_widget(
            make_label(
                "ماشین‌حساب",
                22,
                WHITE,
                True
            )
        )

        self.calc_entry = TextInput(
            text="",
            multiline=False,
            font_size=dp(28),
            foreground_color=WHITE,
            background_color=INPUT,
            cursor_color=GOLD,
            halign="right",
            size_hint_y=None,
            height=dp(65),
            padding=[dp(12), dp(10)],
        )

        root.add_widget(self.calc_entry)

        grid = GridLayout(
            cols=4,
            spacing=dp(6),
        )

        buttons = [
            "%",
            "C",
            "DEL",
            "/",

            "7",
            "8",
            "9",
            "*",

            "4",
            "5",
            "6",
            "-",

            "1",
            "2",
            "3",
            "+",

            "+/-",
            "0",
            ".",
            "=",
        ]

        for key in buttons:

            if key == "=":
                color = GOLD
                text_color = BG_DEEP

            elif key in ["/", "*", "-", "+"]:
                color = BLUE
                text_color = WHITE

            elif key in ["C", "DEL"]:
                color = RED if key == "C" else CARD2
                text_color = WHITE

            else:
                color = CARD2
                text_color = WHITE

            btn = make_button(
                key,
                color,
                text_color,
                58
            )

            btn.bind(
                on_release=lambda btn, k=key:
                self.calc_press(k)
            )

            grid.add_widget(btn)

        root.add_widget(grid)

        return root


    def calc_press(self, key):

        current = self.calc_entry.text

        if key == "C":

            self.calc_entry.text = ""

            return

        if key == "DEL":

            self.calc_entry.text = current[:-1]

            return

        if key == "=":

            try:

                result = safe_eval(current)

                if isinstance(result, float) and result.is_integer():
                    result = int(result)

                self.calc_entry.text = str(result)

            except Exception:

                self.calc_entry.text = "Error"

            return

        if current == "Error":
            current = ""

        if key == "+/-":

            if current.startswith("-"):
                current = current[1:]

            elif current:
                current = "-" + current

            else:
                current = "-"

        else:

            if current == "0" and key not in [
                ".", "/", "*", "-", "+", "%"
            ]:
                current = ""

            current += key

        self.calc_entry.text = current


    # ========================================================
    # خرید و فروش طلا
    # ========================================================

    def build_trade(self):

        scroll = ScrollView()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12),
            size_hint_y=None,
        )

        root.bind(
            minimum_height=root.setter("height")
        )

        root.add_widget(
            make_label(
                "خرید و فروش طلا",
                21,
                WHITE,
                True
            )
        )

        self.trade_tola_rate = make_input("0")
        self.trade_ex_rate = make_input("0")
        self.trade_purity = make_input("23.88")
        self.trade_gram_weight = make_input("1")
        self.trade_tola_weight = make_input("1")

        self.add_field(
            root,
            "نرخ یک طوله در بازار (USD)",
            self.trade_tola_rate
        )

        self.add_field(
            root,
            "نرخ دالر به افغانی",
            self.trade_ex_rate
        )

        self.add_field(
            root,
            "عیار طلا",
            self.trade_purity
        )

        self.add_field(
            root,
            "وزن طلا به گرام",
            self.trade_gram_weight
        )

        self.add_field(
            root,
            "وزن طلا به طوله",
            self.trade_tola_weight
        )

        btn = make_button(
            "محاسبه نهایی خرید و فروش",
            GOLD,
            BG_DEEP,
            55
        )

        btn.bind(
            on_release=lambda x:
            self.calculate_trade()
        )

        root.add_widget(btn)

        self.trade_result = make_label(
            "",
            14,
            WHITE,
            False
        )

        root.add_widget(
            self.trade_result
        )

        scroll.add_widget(root)

        return scroll


    def calculate_trade(self):

        try:

            tola = float(
                self.trade_tola_rate.text
            )

            ex = float(
                self.trade_ex_rate.text
            )

            purity = float(
                self.trade_purity.text
            )

            wg = float(
                self.trade_gram_weight.text
            )

            wt = float(
                self.trade_tola_weight.text
            )

            if (
                tola < 0
                or ex <= 0
                or not (0 < purity <= COMMON_PURITY)
                or wg < 0
                or wt < 0
            ):
                raise ValueError

        except Exception:

            self.show_error(
                "لطفاً اعداد معتبر وارد کنید."
            )

            return

        gram24 = tola / TOLA_GRAM

        gram = (
            gram24 *
            (purity / COMMON_PURITY)
        )

        gram_afn = gram * ex

        tg = wg * gram

        tg_afn = tg * ex

        tt = (
            wt *
            tola *
            (purity / COMMON_PURITY)
        )

        tt_afn = tt * ex

        self.trade_result.text = (
            "📊 نتیجه محاسبه\n\n"

            "محاسبه برویت طوله:\n"
            f"نرخ یک گرام به دالر: "
            f"${gram:,.2f}\n"
            f"نرخ یک گرام به افغانی: "
            f"{gram_afn:,.1f} AFN\n"
            f"نرخ مجموعی دالری: "
            f"${tt:,.2f}\n"
            f"نرخ مجموعی افغانی: "
            f"{tt_afn:,.0f} AFN\n\n"

            "محاسبه برویت گرام:\n"
            f"نرخ یک گرام به دالر: "
            f"${gram:,.2f}\n"
            f"نرخ یک گرام به افغانی: "
            f"{gram_afn:,.1f} AFN\n"
            f"نرخ مجموعی دالری: "
            f"${tg:,.2f}\n"
            f"نرخ مجموعی افغانی: "
            f"{tg_afn:,.0f} AFN"
        )


    # ========================================================
    # مبدل عیار و نرخ‌ها
    # ========================================================

    def build_rates(self):

        scroll = ScrollView()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12),
            size_hint_y=None,
        )

        root.bind(
            minimum_height=root.setter("height")
        )

        root.add_widget(
            make_label(
                "مبدل عیار طلا",
                21,
                WHITE,
                True
            )
        )

        self.rate_tola_entry = make_input("0")
        self.rate_calc_purity = make_input("23.88")

        self.add_field(
            root,
            "نرخ یک طوله",
            self.rate_tola_entry
        )

        self.add_field(
            root,
            "عیار برای محاسبه",
            self.rate_calc_purity
        )

        btn = make_button(
            "محاسبه نرخ‌ها",
            BLUE,
            WHITE,
            55
        )

        btn.bind(
            on_release=lambda x:
            self.calculate_tola_rates()
        )

        root.add_widget(btn)

        self.rate_result = make_label(
            "",
            14,
            WHITE
        )

        root.add_widget(
            self.rate_result
        )

        scroll.add_widget(root)

        return scroll


    def calculate_tola_rates(self):

        try:

            tola_rate = float(
                self.rate_tola_entry.text
            )

            rate_purity = float(
                self.rate_calc_purity.text
            )

            if (
                tola_rate < 0
                or not (0 < rate_purity <= COMMON_PURITY)
            ):
                raise ValueError

        except Exception:

            self.show_error(
                "لطفاً نرخ معتبر برای طوله و عیار وارد کنید."
            )

            return

        base_gram_rate = (
            tola_rate / TOLA_GRAM
        )

        gram_rate = (
            base_gram_rate *
            (rate_purity / COMMON_PURITY)
        )

        mithqal_rate = (
            gram_rate *
            MITHQAL_GRAM
        )

        troy_ounce_rate = (
            gram_rate *
            TROY_OUNCE_GRAM
        )

        self.rate_result.text = (
            "نتایج تبدیل نرخ طوله\n\n"

            f"نرخ یک طوله: "
            f"{tola_rate:,.2f}\n\n"

            f"عیار برای محاسبه: "
            f"{rate_purity}\n\n"

            f"نرخ یک گرم: "
            f"{gram_rate:,.4f}\n\n"

            f"نرخ یک مثقال: "
            f"{mithqal_rate:,.4f}\n\n"

            f"نرخ یک انس: "
            f"{troy_ounce_rate:,.4f}"
        )


    # ========================================================
    # تحلیل تبدیل طلا
    # ========================================================

    def build_conversion(self):

        scroll = ScrollView()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12),
            size_hint_y=None,
        )

        root.bind(
            minimum_height=root.setter("height")
        )

        root.add_widget(
            make_label(
                "تحلیل تبدیل طلا به طلا",
                21,
                WHITE,
                True
            )
        )

        self.conv_cur_weight = make_input("0")
        self.conv_cur_purity = make_input("18")
        self.conv_target_weight = make_input("0")
        self.conv_target_purity = make_input("23.88")
        self.conv_add_purity = make_input("23.88")

        self.add_field(
            root,
            "وزن طلای مشتری",
            self.conv_cur_weight
        )

        self.add_field(
            root,
            "عیار طلای مشتری",
            self.conv_cur_purity
        )

        self.add_field(
            root,
            "وزن طلای ضرورت شما",
            self.conv_target_weight
        )

        self.add_field(
            root,
            "عیار ضرورت شما",
            self.conv_target_purity
        )

        self.add_field(
            root,
            "عیار مروجی",
            self.conv_add_purity
        )

        btn = make_button(
            "تحلیل تبدیل",
            GOLD,
            BG_DEEP,
            55
        )

        btn.bind(
            on_release=lambda x:
            self.analyze_gold_conversion()
        )

        root.add_widget(btn)

        self.conv_result = make_label(
            "",
            14,
            WHITE
        )

        root.add_widget(
            self.conv_result
        )

        scroll.add_widget(root)

        return scroll


    def analyze_gold_conversion(self):

        try:

            w_cur = float(
                self.conv_cur_weight.text
            )

            p_cur = float(
                self.conv_cur_purity.text
            )

            w_tgt = float(
                self.conv_target_weight.text
            )

            p_tgt = float(
                self.conv_target_purity.text
            )

            p_add = float(
                self.conv_add_purity.text
            )

            if any(
                x < 0
                for x in [
                    w_cur,
                    p_cur,
                    w_tgt,
                    p_tgt,
                    p_add
                ]
            ):
                raise ValueError

            if not (
                0 < p_cur <= COMMON_PURITY
                and
                0 < p_tgt <= COMMON_PURITY
                and
                0 < p_add <= COMMON_PURITY
            ):
                raise ValueError

        except Exception:

            self.show_error(
                "لطفاً مقادیر معتبر وارد کنید."
            )

            return

        pure_cur = (
            w_cur *
            (p_cur / COMMON_PURITY)
        )

        pure_tgt = (
            w_tgt *
            (p_tgt / COMMON_PURITY)
        )

        diff_pure = (
            pure_tgt -
            pure_cur
        )

        result = (
            "نتایج تحلیل طلا به طلا\n\n"
            f"طلای مشتری در عیار 23.88: "
            f"{pure_cur:,.4f} g\n\n"
            f"طلای ضرورت شما در عیار 23.88: "
            f"{pure_tgt:,.4f} g\n\n"
        )

        if abs(diff_pure) < 1e-9:

            result += (
                "شما دقیقاً به مقدار هدف رسیده‌اید.\n"
                "نیازی به تغییر وزن یا عیار نیست."
            )

            self.conv_result.text = result
            return

        if diff_pure > 0:

            weight_add = (
                diff_pure *
                COMMON_PURITY /
                p_add
            )

            result += (
                f"مقدار طلای خالص مورد ضرورت: "
                f"{diff_pure:,.4f} g\n\n"

                f"مقدار طلای عیار {p_add} "
                f"که باید اضافه شود:\n"
                f"{weight_add:,.4f} g\n\n"
            )

            new_total_weight = (
                w_cur + weight_add
            )

            result += (
                f"وزن نهایی تقریبی: "
                f"{new_total_weight:,.4f} g\n"
            )

            if abs(
                new_total_weight - w_tgt
            ) <= 1e-6:

                result += (
                    "\nوزن نهایی دقیقاً به وزن هدف می‌رسد."
                )

            else:

                result += (
                    f"\nوزن هدف: {w_tgt:,.4f} g\n"
                    "توجه: وزن هدف و مقدار عیار هدف "
                    "با مقدار اضافه‌شده باید جداگانه بررسی شود."
                )

            # محاسبه جایگزینی برای حفظ وزن هدف

            if abs(
                p_add - p_cur
            ) > 1e-9:

                A = p_cur / COMMON_PURITY
                B = p_tgt / COMMON_PURITY
                C = p_add / COMMON_PURITY

                x = (
                    w_tgt *
                    (B - A) /
                    (C - A)
                )

                y = (
                    w_cur +
                    x -
                    w_tgt
                )

                if x >= 0 and y >= 0:

                    result += (
                        "\n\nبرای حفظ وزن نهایی:\n"
                        f"افزودن حدود {x:,.4f} g "
                        f"از عیار {p_add}\n"
                        f"و خارج کردن حدود {y:,.4f} g "
                        f"از آلیاژ فعلی."
                    )

        else:

            need_remove_pure = -diff_pure

            weight_remove = (
                need_remove_pure *
                COMMON_PURITY /
                p_cur
            )

            result += (
                f"مقدار طلای خالص اضافه برداشت‌شده: "
                f"{need_remove_pure:,.4f} g\n\n"

                f"مقدار طلای عیار فعلی که باید "
                f"مسترد شود:\n"
                f"{weight_remove:,.4f} g\n\n"

                f"وزن نهایی تقریبی:\n"
                f"{w_cur - weight_remove:,.4f} g"
            )

        result += (
            "\n\nتذکر:\n"
            "محاسبات بر اساس فرمول ریاضی انجام شده "
            "و ضایعات یا تغییرات عملی در نظر گرفته نشده است."
        )

        self.conv_result.text = result


    # ========================================================
    # خمس دولتی
    # ========================================================

    def build_gov_khums(self):

        scroll = ScrollView()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12),
            size_hint_y=None,
        )

        root.bind(
            minimum_height=root.setter("height")
        )

        root.add_widget(
            make_label(
                "خمس دولتی",
                21,
                WHITE,
                True
            )
        )

        self.gov_tola_rate = make_input("0")
        self.gov_ex_rate = make_input("0")
        self.gov_weight = make_input("0")

        self.add_field(
            root,
            "نرخ یک طوله",
            self.gov_tola_rate
        )

        self.add_field(
            root,
            "نرخ دالر به افغانی",
            self.gov_ex_rate
        )

        self.add_field(
            root,
            "وزن طلا به گرام",
            self.gov_weight
        )

        btn = make_button(
            "محاسبه خمس دولتی",
            BLUE,
            WHITE,
            55
        )

        btn.bind(
            on_release=lambda x:
            self.calculate_gov_khums()
        )

        root.add_widget(btn)

        self.gov_result = make_label(
            "",
            14,
            WHITE
        )

        root.add_widget(
            self.gov_result
        )

        scroll.add_widget(root)

        return scroll


    def calculate_gov_khums(self):

        try:

            tola_rate = float(
                self.gov_tola_rate.text
            )

            ex_rate = float(
                self.gov_ex_rate.text
            )

            weight = float(
                self.gov_weight.text
            )

            if (
                tola_rate < 0
                or ex_rate <= 0
                or weight < 0
            ):
                raise ValueError

        except Exception:

            self.show_error(
                "لطفاً مقادیر معتبر وارد کنید."
            )

            return

        gram_rate = (
            tola_rate /
            TOLA_GRAM
        )

        commission = (
            (30.0 / ex_rate) *
            weight
        )

        delivery_usd = (
            weight *
            gram_rate +
            commission
        )

        delivery_afn = (
            delivery_usd *
            ex_rate
        )

        self.gov_result.text = (
            "نتایج خمس دولتی\n\n"

            f"نرخ یک گرام:\n"
            f"{gram_rate:,.2f}\n\n"

            f"کمیشن خمس دولتی "
            f"(30 افغانی در هر گرام):\n"
            f"{commission:,.2f} USD\n\n"

            f"جمله تحویلی دالری:\n"
            f"${delivery_usd:,.2f}\n\n"

            f"جمله تحویلی افغانی:\n"
            f"{delivery_afn:,.0f} AFN"
        )


    # ========================================================
    # اضافه کردن فیلد
    # ========================================================

    def add_field(self, parent, title, field):

        box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(75),
            spacing=dp(5),
        )

        box.add_widget(
            make_label(
                title,
                12,
                GRAY,
                True
            )
        )

        box.add_widget(field)

        parent.add_widget(box)


    # ========================================================
    # پیام خطا
    # ========================================================

    def show_error(self, message):

        content = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(15),
        )

        content.add_widget(
            make_label(
                message,
                14,
                WHITE
            )
        )

        btn = make_button(
            "باشه",
            GOLD,
            BG_DEEP,
            45
        )

        content.add_widget(btn)

        popup = Popup(
            title="خطا",
            content=content,
            size_hint=(0.85, None),
            height=dp(220),
        )

        btn.bind(
            on_release=popup.dismiss
        )

        popup.open()


    # ========================================================
    # ساخت گزارش TXT
    # ========================================================

    def build_report(self):

        title = self.current_tab_name

        lines = []

        lines.append(
            "========================================"
        )

        lines.append(
            "سیستم حسابگر پیشرفته طلا - زرگری بیژن"
        )

        lines.append(title)

        lines.append(
            "تاریخ و زمان: "
            + datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        lines.append(
            "========================================"
        )

        lines.append("")

        if title == "ماشین‌حساب":

            lines.append(
                "عبارت / نتیجه:"
            )

            lines.append(
                self.calc_entry.text
            )

        elif title == "خرید و فروش طلا":

            lines.extend([
                f"نرخ طوله: {self.trade_tola_rate.text}",
                f"نرخ دالر: {self.trade_ex_rate.text}",
                f"عیار: {self.trade_purity.text}",
                f"وزن گرام: {self.trade_gram_weight.text}",
                f"وزن طوله: {self.trade_tola_weight.text}",
                "",
                "نتایج:",
                self.trade_result.text,
            ])

        elif title == "مبدل عیار طلا":

            lines.extend([
                f"نرخ طوله: {self.rate_tola_entry.text}",
                f"عیار: {self.rate_calc_purity.text}",
                "",
                "نتایج:",
                self.rate_result.text,
            ])

        elif title == "تحلیل تبدیل طلا":

            lines.extend([
                f"وزن مشتری: {self.conv_cur_weight.text}",
                f"عیار مشتری: {self.conv_cur_purity.text}",
                f"وزن هدف: {self.conv_target_weight.text}",
                f"عیار هدف: {self.conv_target_purity.text}",
                f"عیار مروجی: {self.conv_add_purity.text}",
                "",
                "نتایج:",
                self.conv_result.text,
            ])

        elif title == "خمس دولتی":

            lines.extend([
                f"نرخ طوله: {self.gov_tola_rate.text}",
                f"نرخ دالر: {self.gov_ex_rate.text}",
                f"وزن: {self.gov_weight.text}",
                "",
                "نتایج:",
                self.gov_result.text,
            ])

        lines.extend([
            "",
            "========================================",
            "طلا | 23.88 | 1 Tola = 12.15 g",
            "========================================",
        ])

        return "\n".join(lines)


    # ========================================================
    # ذخیره TXT
    # ========================================================

    def save_current_tab(self):

        text = self.build_report()

        filename = (
            self.current_tab_name
            .replace("/", "-")
            .replace("\\", "-")
            + "_"
            + datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S"
            )
            + ".txt"
        )

        try:

            path = os.path.join(
                self.user_data_dir,
                filename
            )

            with open(
                path,
                "w",
                encoding="utf-8-sig"
            ) as file:

                file.write(text)

            self.show_info(
                "فایل با موفقیت ذخیره شد.\n\n"
                f"محل فایل:\n{path}"
            )

        except Exception as e:

            self.show_error(
                f"ذخیره فایل انجام نشد:\n{e}"
            )


    # ========================================================
    # اطلاعات
    # ========================================================

    def show_info(self, message):

        content = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(15),
        )

        content.add_widget(
            make_label(
                message,
                13,
                WHITE
            )
        )

        btn = make_button(
            "باشه",
            GOLD,
            BG_DEEP,
            45
        )

        content.add_widget(btn)

        popup = Popup(
            title="اطلاعات",
            content=content,
            size_hint=(0.9, None),
            height=dp(300),
        )

        btn.bind(
            on_release=popup.dismiss
        )

        popup.open()


    # ========================================================
    # چاپ / اشتراک گذاری
    # ========================================================

    def print_current_tab(self):

        text = self.build_report()

        try:

            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            Intent = autoclass(
                "android.content.Intent"
            )

            String = autoclass(
                "java.lang.String"
            )

            intent = Intent(
                Intent.ACTION_SEND
            )

            intent.setType(
                "text/plain"
            )

            intent.putExtra(
                Intent.EXTRA_SUBJECT,
                String(self.current_tab_name)
            )

            intent.putExtra(
                Intent.EXTRA_TEXT,
                String(text)
            )

            chooser = Intent.createChooser(
                intent,
                String("انتخاب برنامه برای چاپ یا ارسال")
            )

            PythonActivity.mActivity.startActivity(
                chooser
            )

        except Exception:

            self.show_info(
                "اشتراک‌گذاری مستقیم Android "
                "در این محیط فعال نیست.\n\n"
                "ابتدا گزارش را با دکمه «ذخیره TXT» "
                "ذخیره کنید."
            )


# ============================================================
# اجرای برنامه
# ============================================================

if __name__ == "__main__":
    GoldApp().run()