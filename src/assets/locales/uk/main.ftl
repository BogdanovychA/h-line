# Main titles
app-title = Гаряча лінія Держенергонагляду (H-Line)
application-title = Фіксація звернення

# Form fields
applicant-name = ПІБ громадянина *
applicant-name-hint = Прізвище, ім'я, по батькові
applicant-address = Адреса проживання громадянина *
applicant-address-hint = 01001, м. Київ, вулиця Хрещатик, буд. 1
applicant-telephone = Номер телефону громадянина
applicant-telephone-hint = +380441234567
applicant-email = Електронна пошта громадянина
applicant-email-hint = example@domain.com
appeal-content = Зміст звернення громадянина
appeal-content-hint = Опишіть суть звернення громадянина...

# Appeal content default value
appeal-content-default =
    Суть звернення:

    Чи звертався громадянин до ОСР, місцевої влади, керуючої компанії тощо:

    Якщо так, який результат:

    Що громадянин просить у Держенергонагляду:

# Validation messages
error-enter-name = Введіть ПІБ громадянина
error-enter-address = Введіть адресу громадянина
error-enter-phone = Введіть коректний телефон
error-enter-email = Введіть коректний email
error-enter-content = Введіть текст звернення
error-select-category = Оберіть категорію
error-select-social-status = Оберіть соціальний стан
error-create-appeal = Помилка при створенні звернення: {$error}
error-generate-application = Помилка при створенні звернення...
error-create-email = Помилка при створенні email...
error-send-email = Помилка при надсиланні email...
error-save-file = Помилка при збереженні файлу...

# Success messages
success-appeal-fixed = Звернення зафіксовано! Можна фіксувати наступне.
default-message-text = Введіть інформацію

# Selectors
not-selected = Не обрано
applicant-category-label = Категорія громадянина *
applicant-social-status-label = Соціальний стан громадянина *

# Categories
cat-war-participant = Учасник війни
cat-disabled-child = Дитина з інвалідністю
cat-single-mother = Одинока мати
cat-mother-heroine = Мати-героїня
cat-large-family = Багатодітна сім'я
cat-chernobyl-victim = Особа, що потерпіла від Чорнобильської катастрофи
cat-vpo = Внутрішньо переміщена особа
cat-chernobyl-liquidator = Учасник ліквідації наслідків аварії на Чорнобильській АЕС
cat-hero-ukraine = Герой України
cat-hero-soviet = Герой Радянського Союзу
cat-hero-socialist = Герой Соціалістичної Праці
cat-child = Дитина
cat-child-war = Дитина війни
cat-disabled-ww2 = Особа з інвалідністю внаслідок Другої світової війни
cat-disabled-war = Особа з інвалідністю внаслідок війни
cat-combat-participant = Учасник бойових дій
cat-veteran-military = Ветеран військової служби
cat-veteran-labor = Ветеран праці
cat-disabled-1 = Особа з інвалідністю I групи
cat-disabled-2 = Особа з інвалідністю II групи
cat-disabled-3 = Особа з інвалідністю III групи
cat-other = Інші категорії

# Social status
status-pensioner = Пенсіонер
status-pensioner-military = Пенсіонер з числа військовослужбовців
status-religious = Служитель релігійної організації
status-journalist = Журналіст
status-prisoner = Особа, що позбавлена волі; особа, воля якої обмежена
status-worker = Робітник
status-peasant = Селянин
status-budget-worker = Працівник бюджетної сфери
status-civil-servant = Державний службовець
status-military = Військовослужбовець
status-entrepreneur = Підприємець
status-unemployed = Безробітний
status-student = Учень, студент
status-other = Інші

# Main view strings
error-enter-last-name = Введіть прізвище
error-enter-position = Введіть посаду
entering-message = Вхід...
main-view-instruction = Введіть ваші ПІБ, посаду та електронну пошту
officer-name-label = Прізвище, ім'я та по батькові
officer-name-hint = Шевченко Тарас Григорович
officer-position-label = Посада (повністю, з назвою структурного підрозділу)
officer-position-hint = Директор департаменту...
officer-email-label = Електронна пошта
officer-email-hint = ShevchenkoT@sies.gov.ua

# Email strings
email-subject = Звернення на гарячу лінію: {$filename}
email-body =
    Звернення на "гарячу лінію" Держенергонагляду у додатку до цього листа.

    Назва файлу: {$filename}

# About and Author views
about-title = Про застосунок
author-title = Про автора
version = Версія: {$version}
license = Ліцензія: {$license}
github = GitHub
sies = Держенергонагляд
author-name = Андрій БОГДАНОВИЧ
home-page = Домашня сторінка
other-apps = Інші застосунки автора
# Error 404
error-404-title = Сторінка не знайдена
target-page = Цільова сторінка: {$route}

# Footer and buttons
required-fields = * — обов'язкові поля
officer-data = Ваші дані: {$name}; {$position}; {$email}
back = Назад
