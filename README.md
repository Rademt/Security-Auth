Захист REST API за допомогою JWT (JSON Web Tokens)
Цей репозиторій містить демонстраційний додаток на Flask (Python), реалізований як REST API, який використовує JWT для автентифікації (@require_auth) та авторизації на основі ролей (@check_role).

 1. Встановлення та Запуск
Для запуску API локально вам потрібен Python 3.x.

1.1. Встановлення (Windows PowerShell)
Клонуйте репозиторій та перейдіть у папку:

PowerShell
git clone <ваше_посилання>
cd auth-workshop # Або назва вашої папки
Створіть та активуйте віртуальне середовище:

PowerShell
python -m venv .venv
# Активація (зазвичай не потрібна, якщо використовуєте повний шлях до python.exe)
Встановіть залежності:

PowerShell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
1.2. Запуск Сервера
Перед запуском необхідно встановити секретний ключ для підпису JWT:

PowerShell
# 1. Встановіть секретний ключ
$env:JWT_SECRET="dev_secret_change_me"

# 2. Запустіть додаток
.\.venv\Scripts\python.exe app.py
Сервер буде доступний за адресою http://127.0.0.1:3000.

 2. Приклади Запитів (PowerShell)
Для тестування ми будемо використовувати Invoke-RestMethod та Invoke-WebRequest у PowerShell.

2.1. Отримання Токена (POST /login)
Для подальших запитів спершу потрібно отримати валідний токен.

PowerShell
# Логін як звичайний користувач
$body = '{"email":"user@example.com","password":"user123"}'
$user_login_response = Invoke-RestMethod -Uri http://127.0.0.1:3000/login -Method Post -Body $body -ContentType "application/json"
$USER_T = $user_login_response.access_token

Write-Host "Отриманий токен користувача: $USER_T"

Автентифікація (AuthN) за Допомогою JWT
У цьому розділі ми перевірили, чи коректно працює захист маршруту /profile за допомогою декоратора @require_auth.

3.1. Перевірка Захисту (Без Токена)
Сценарій: Спроба отримати доступ до /profile без передачі заголовка Authorization.

Використана команда: Invoke-WebRequest -Uri http://127.0.0.1:3000/profile -Method Get

Отриманий результат: 401 Unauthorized.

Висновок: Middleware @require_auth працює коректно, блокуючи неавтентифіковані запити.

3.2. Перевірка Успішної Автентифікації (З Валідним Токеном)
Сценарій: Доступ до /profile з валідним токеном користувача ($USER_T).

Очікуваний результат: 200 OK та JSON-дані користувача.

Використана команда (Приклад):

PowerShell
$headers = @{"Authorization"="Bearer $USER_T"}
Invoke-RestMethod -Uri http://127.0.0.1:3000/profile -Method Get -Headers $headers
Фактичний результат: Отримано {"error": "Invalid token"}.

Пояснення: Хоча очікуваним результатом був 200 OK, фактично було отримано помилку "Invalid token". Це підтверджує, що термін дії токена (EXP), незважаючи на встановлені 15 хвилин у коді, ставав невалідним миттєво, унеможливлюючи практичну перевірку.

4. Крок 3: Авторизація (AuthZ) на Основі Ролей (RBAC)
Цей розділ демонструє, як функція @check_role(["admin"]) контролює доступ до маршруту DELETE /users/:id залежно від ролі користувача.

4.1. Сценарій: Відмова у Доступі (User → 403 Forbidden)
Роль: Звичайний користувач ("user") — не має прав адміністратора.

Мета: Перевірити, чи блокується доступ до ресурсу, призначеного лише для адміністраторів.

Очікуваний результат: 403 Forbidden.

Обґрунтування: Middleware @check_role перевіряє, чи містить payload токена необхідну роль (admin). Оскільки токен містить роль "user", доступ блокується.

Використана команда (Приклад):

PowerShell
$headers = @{"Authorization"="Bearer $USER_T"}
try { Invoke-WebRequest -Uri http://127.0.0.1:3000/users/5 -Method Delete -Headers $headers } catch { Write-Host "Status: $($_.Exception.Response.StatusCode)" }
4.2. Сценарій: Успішний Доступ (Admin → 200 OK)
Роль: Адміністратор ("admin") — має необхідні права.

Мета: Перевірити, чи дозволяється доступ до ресурсу з правильною роллю.

Очікуваний результат: 200 OK та повідомлення про успішне видалення.

Обґрунтування: Токен містить роль "admin", що відповідає вимозі @check_role(["admin"]), тому доступ дозволено.

Використана команда (Приклад):

PowerShell
$headers = @{"Authorization"="Bearer $ADMIN_T"}
Invoke-RestMethod -Uri http://127.0.0.1:3000/users/5 -Method Delete -Headers $headers
