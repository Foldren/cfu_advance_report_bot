from aiogram_dialog.widgets.text import Jinja

jinja_check_report = Jinja("""
📝 Сверьте данные отчетов:
{% for p in dialog_data.projects %}
\n🔹 <u>{{p.name}}</u>
Статья затрат: <b>{{p.expense}}</b>
Комментарий: <b>{{p.comment}}</b>
Сумма: <b>{{p.amount}}</b>
Валюта: <b>{{p.currency}}</b>
{% endfor %}
{% if not dialog_data.attach_is_passed %}
\n📄 Прикрепленные файлы:
<i>{{ dialog_data.files_names|join(", ") }}</i>
{% endif %}
""")

jinja_approval_notify = Jinja("""
<b>🟢 Новый запрос на согласование АО: (От {{start_data.current_fstr_date}})</b>\n
📃<u> Список отчетов:</u>
{% for p in start_data.projects %}
\n🔹 <u>{{p.name}}</u>
Статья затрат: <b>{{p.expense}}</b>
Комментарий: <b>{{p.comment}}</b>
Сумма: <b>{{p.amount}}</b>
Валюта: <b>{{p.currency}}</b>
{% endfor %}
""")
