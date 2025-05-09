



from code_.bots import Bots
from code_.users import Users
from code_.ask import Ask
from code_.requests import Requests
from code_.plan import Plan









default_response = """Привет)
(Напишите /help чтобы увидеть список доступных действий)"""
lack_of_rights_response = """Извините, но это команда админа, вы не можете ей пользоваться"""
unathorized_response = """Извините, данной командой можно пользоваться только если вы вошли в систему"""
cant_use_command_response = """Вы пытаетесь воспользоваться командой во время выполнения другой команды. 

Если вы хотите отменить выполнение текущей команды можете написать /cancel"""
useless_use_response = """Эту команду можно использовать только для того, чтобы отменить выпоняемое действие. В данный момент вы не выполняете никаких действий"""
canceled_response = """Выполнение команды отменено"""

def start_handler(args, user):
    return """Привет! Это бот ОСС. Он может отвечать на ваши вопросы и ещё много чего. 

Напишите /help чтобы увидеть список доступных действий. Для большинства из них вам понадобиться войти в систему. Сделайте это с помощью команды /login. 

Чтобы войти вам понадобится логин и пароль. Их вам должен сообщить человек, который добавил вас в систему""", True

def help_handler(args, user):
    reply = "Вот список доступных комманд:\n"
    for command, description in bots.descriptions.items():
        if (user.login is None or user.is_admin == False) and bots.handler_map[command].require_admin:
            continue
        if command == "/help":
            continue
        reply += f" • {' (Админ)' if bots.handler_map[command].require_admin else ''} {command}: {description}\n"
    return reply, True

def login_handler(args, user):
    if user.login:
        return "Вы и так в системе", True
    
    if user.aux:
        login, password = Bots.parse_args(args, 2)
        if login is None:
            return "Вы ввели свои данные неверно. Пожалуйста введите свои данные в формате: ЛОГИН ПАРОЛЬ", False
        new_user = users.get_user_by_login(login)
        if new_user is None:
            return "Пользователя с таким логином нет. Проверьте не сделали ли вы ошибку и попробуйте ещё раз", False
        if users.check_password(password, new_user.password_hash) == False:
            return "Неверный пароль, попробуйте ещё раз", False
        users.add_chat_id(login, user.cur_chat_id)
        return "Вы успешно вошли в систему", True
    else:
        user.aux = 1
        return "Пожалуйста введите свои данные в формате: ЛОГИН ПАРОЛЬ", False

def logout_handler(args, user):
    users.remove_chat_id(user.login, user.cur_chat_id)
    return "Вы успешно вышли из аккаутна", True

def me_handler(args, user):
    if (contract_number := user.contract_number) and len(contract_number) > 4:
        contract_number = f"<code>{contract_number}</code>"        
    return \
        f"Вот информация о вас:\n" \
        f" • Логин: {user.login}\n" \
        f" • Количество чатов, в которых вы авторизованы: {len(user.chat_ids)}\n" \
        f" • Вы {'админ' if user.is_admin else 'пользователь'}\n" \
        f" • Номер договора: {contract_number or 'не указан'}\n" \
        f" • Общежитие: {user.dorm or 'не указано'}\n" \
        f" • Номер комнаты: {user.room_number or 'не указан'}\n", \
        True

user_info_request = "Введите логин пользователя, информацию о котором вы хотите получить"
def user_info_handler(args, user):
    login, = Bots.parse_args(args, 1)
    if login is None:
        return "Вы ввели данные неверно. Попробуйте ещё раз", False
    user_info = users.get_user_by_login(login)
    if user_info is None:
        return "Такого пользователя нет в системе. Попробуйте ещё раз", False
    if (contract_number := user_info.contract_number) and len(contract_number) > 4:
        contract_number = f"<code>{contract_number}</code>"        
    return \
        f"Вот информация о пользователе:\n" \
        f" • Логин: {user_info.login}\n" \
        f" • Количество чатов, в которых он(-а) авторизован(-а): {len(user_info.chat_ids)}\n" \
        f" • {'Админ' if user_info.is_admin else 'Пользователь'}\n" \
        f" • Номер договора: {contract_number or 'не указан'}\n" \
        f" • Общежитие: {user_info.dorm or 'не указано'}\n" \
        f" • Номер комнаты: {user_info.room_number or 'не указан'}\n", \
        True

def list_users_handler(args, user):
    users_, count = users.get_all(100)
    
    if count == 0:
        return "В настоящий момент в системе нет пользователей", True
    
    reply = "Пользователи:\n"
    for cur_user in users_:
        reply += f" • <code>{cur_user.login}</code>, {'Админ' if cur_user.is_admin else 'Пользователь'}, Кол-во чатов: {len(cur_user.chat_ids)}\n"
    if count - 100 > 0:
        reply += f"   И ещё {count - 100}..."
    
    return reply, True

delete_user_request = "Напишите логин пользователя, которого хотите удалить"
def delete_user_handler(args, user):
    if user.aux is None:
        login, = Bots.parse_args(args, 1)

        if login is None:
            return "Вы ввели данные неверно. Попробуйте ещё раз", False

        if users.get_user_by_login(login) is None:
            return "Пользователя с таким логином нет в системе. Попробуйте ещё раз", False
        
        if user.login == login:
            return "Вы пытаетесь удалить самого себя. Вы не можете этого сделать", True
        
        user.aux = login
        return f"Вы уверены, что хотите удалить пользователя {login}?\n(Напишите /yes или /no)", False
    else:
        login = user.aux
        confirm, = Bots.parse_args(args, 1)
        confirm = confirm.lower()
        if confirm[0] == '/':
            confirm = confirm[1:]
        options = {"yes": True, "no": False, "n": False, "y": True}

        if confirm not in options:
            return "Напишите /yes или /no", False
        if options[confirm] == False:
            return "Добавление пользователя отменено", True

        bots.notify("Извините, вы были удалены из системы", login)
        bots.clear_user_next_steps(login)
        users.delete_user(login)
        ask.delete_by_login(login)
        requests.delete_by_login(login)
        return f"Пользователь {login} успешно удалён", True

register_request = "Вы собираетесь зарегистрировать нового пользователя. \nПожалуйста введите его данные в формате:\n  ЛОГИН\n  ПАРОЛЬ\n  АДМИН(1)/ПОЛЬЗОВЕТЕЛЬ(0)\n  НОМЕР_ДОГОВОРА\n  ОБЩЕЖИТИЕ\n  НОМЕР_КОМНАТЫ"
def register_handler(args, user):
    if user.aux is None:
        login, password, is_admin, contract_number, dorm, room_number = Bots.parse_args(args, 6)

        if login is None:
            login, password, is_admin = Bots.parse_args(args, 3)

        if login is None:
            return "Вы ввели данные неверно. Попробуйте ещё раз", False
        
        is_admin = is_admin.lower()
        options = {"админ": True, "пользователь": False, "0": False, "1": True}
        if is_admin not in options:
            return "Вы неправильно ввели информацию о том, должен ли пользователь быть админом или пользователем. Пожалуйста введите данные в формате:\n ЛОГИН\n  ПАРОЛЬ\n  АДМИН(1)/ПОЛЬЗОВЕТЕЛЬ(0)\n  НОМЕР_ДОГОВОРА\n  ОБЩЕЖИТИЕ\n  НОМЕР_КОМНАТЫ\nНапример:\n user qwerty пользователь", False
        is_admin = options[is_admin]

        if users.get_user_by_login(login):
            return "Пользователь с таким логином уже существует. Попробуйте ввести данные ещё раз.", False

        if room_number:
            try:
                room_number = int(room_number)
            except ValueError:
                return "Вы ввели невозможный номер комнаты. Попробуйте ещё раз", False
        
        if is_admin:
            user.aux = login, password, is_admin, contract_number, dorm, room_number
            return "Вы собираетесь создать пользователя с правами админа, вы уверены? Пользователь с правами админа имеет доступ ко всем командам бота.\n(Напишите /yes или /no). ", False
    else:
        login, password, is_admin, contract_number, dorm, room_number = user.aux
        confirm, = Bots.parse_args(args, 1)
        if confirm[0] == '/':
            confirm = confirm[1:]
        confirm = confirm.lower()
        options = {"yes": True, "no": False, "n": False, "y": True}

        if confirm not in options:
            return "Напишите /yes или /no", False
        if options[confirm] == False:
            return "Добавление пользователя отменено", True

    users.add_user(login, password, is_admin, contract_number, dorm, room_number)
    return f"Пользователь {login} успешно добавлен", True

ask_request = "Задайте ваш вопрос"
def ask_handler(args, user):
    exact_answer = ask.get_answer(args)
    if exact_answer:
        return exact_answer, True
    
    similar_answers = ask.get_similar_answer(args)
    if len(similar_answers) == 0:
        return f"На ваш запрос не найден не один ответ. Можете добавить свой вопрос с помощью команды /asknew. \n(Ваш вопрос: <code>{args}</code>)", True 
    
    reply = "На ваш запрос найдены следующие ответы:\n\n"
    for question_str, answer_str in similar_answers:
        reply += f'   • {question_str}: {answer_str}\n'
    reply += "\nЕсли среди этих вопросов нет подходящего, можете попробовать задать вопрос ещё раз или добавить его с помощью команды /asknew"
    return reply, True
    
ask_new_request = "Напишите что вы хотите спросить"
def ask_new_handler(args, user):
    if ask.question_exists(args):
        answer = ask.get_answer(args)
        return "Вопрос, который вы пытаетесь добавить уже существует, ответ на него:\n" + answer, True

    question_str = ask.add_question(args, user.login)
    return f"Ваш вопрос ({question_str}) был добавлен", True
    
def list_questions(questions, count):
    reply = ""
    for index, (question_str, asked_login) in enumerate(questions):
        reply += f"   {index + 1}) <code>{asked_login}</code>: {question_str}\n"
    if count - 30 > 0:
        reply += f"   И ещё {count - 30}..."
    reply += "Чтобы ответить на один из вопросов нипишите данные в формате: НОМЕР ОТВЕТ или НОМЕР delete, чтобы удалить. Также можете перестать просматривать список вопросов, написав /cancel"
    return reply
def answer_handler(args: str, user):
    if args is None:
        questions, count = ask.get_unanswered(30)

        if count == 0:
            return "В настоящий момент нет неотвеченных вопросов", True
    
        user.aux = questions, count

        return "Вот список вопросов, на которые ещё нет ответа:\n" + list_questions(questions, count), False
    else:
        num, *answer = args.split(" ", 1)
        if len(answer) == 0:
            return "Вы не ввели ответ на вопрос, пожалуйста попробуйте ещё раз", False
        answer, = answer
        try:
            num = int(num) - 1
        except ValueError:
            return "Номер вопроса, который вы ввели недействителен. Пожалуйста попробуйте ещё раз", False
        questions, count = user.aux

        if (0 <= num < len(questions)) == False:
            return "Номер вопроса, который вы ввели недействителен. Пожалуйста попробуйте ещё раз", False

        question_str, asked_login = questions[num]
        questions.pop(num)

        if answer.lstrip().rstrip().lower() == "delete":
            success = ask.delete(question_str)
            if success == False:
                return "Ошибка при удалении вопроса, возможно другой админ уже сделал что-то с этим вопросом", True
            reply = f"Вопрос \"{question_str}\" от пользователя \"{asked_login}\" был успешно удалён\n"
        else:
            success = ask.answer(question_str, answer)
            if success == False:
                return "Ошибка при добавлении ответа на вопрос, возможно другой админ уже сделал что-то с этим вопросом", True
            reply = f"Ответ \"{answer}\" на вопрос \"{question_str}\" успешно добавлен\n"
            notify_user = users.get_user_by_login(asked_login)
            if notify_user:
                bots.notify(f"Администрация ответила на ваш вопрос ({question_str}):\n{answer}", notify_user.login)

        if len(questions) == 0:
            return "Больше нет вопросов, на которые нет ответа", True

        return reply + "Список вопросов:\n" + list_questions(questions, count), False
    
notify_request = "Введите логин пользователя, которому хотите отослать оповещение"
def notify_handler(args: str, user):
    if user.aux is None:
        login, = Bots.parse_args(args, 1)
        if login is None:
            return "Вы ввели данные неверно. Попробуйте ещё раз", False
        if user.login == login:
            return "Вы пытаетесь отправить оповещение самому себе. Вы не можете этого сделать", True
        notify_user = users.get_user_by_login(login)
        if notify_user is None:
            return "Извините, такого пользователя нет в системе", True
        if len(notify_user.chat_ids) == 0:
            return "Пользователь, которому вы хотите отправить оповещение не вошёл в систему не с одного устройства. Оповестить его не получится", True
        user.aux = login 
        return "Введите сообщение, которое хотите отправить", False
    else:
        bots.notify(f"Сообщение от администрации:\n{args}", user.aux)
        return f'Оповещение пользователю "{user.aux}" успешно отправлено', True

with open("assets/examples/schedule.txt", "r", encoding="utf-8") as file:
    schedule_text = file.read()
def schedule_handler(args: str, user):
    return "Вот расписание мест общего пользования:\n" + schedule_text, True

regevent_request = "Пожалуйста введите свой запрос на проведение мероприятия"
def regevent_handler(args: str, user):
    requests.add(args, "event", user.login)
    return f"Ваш запрос на проведение мероприятия ({args}) успешно сохранён", True

def list_requests(requests_, count):
    reply = ""
    for index, (_, req_str, asked_login) in enumerate(requests_):
        reply += f"   /{index + 1} <code>{asked_login}</code>: {req_str}\n"
    if count - 30 > 0:
        reply += f"   И ещё {count - 30}..."
    reply += "Чтобы удалить один из запросов нипишите его номер. Можете перестать просматривать список запросов, написав /cancel. Также можете написать сообщение пользователю, который создал запрос с помощью команды /notify"
    return reply
def events_handler(args: str, user):
    if args is None:
        reqs, count = requests.get(30, "event")

        if count == 0:
            return "В настоящий момент нет запросов на проведение мероприятий", True
    
        user.aux = reqs, count

        return "Вот список запросов на проведение мероприятий:\n" + list_requests(reqs, count), False
    else:
        num, = Bots.parse_args(args, 1)
        if num[0] == "/":
            num = num[1:]

        try:
            num = int(num) - 1
        except ValueError:
            return "Номер запроса, который вы ввели недействителен. Пожалуйста попробуйте ещё раз", False
        reqs, count = user.aux

        if (0 <= num < len(reqs)) == False:
            return "Номер запроса, который вы ввели недействителен. Пожалуйста попробуйте ещё раз", False

        id, req_str, asked_login = reqs[num]
        reqs.pop(num)

        requests.delete(id)
        reply = f"Запрос \"{req_str}\" от пользователя \"{asked_login}\" был успешно удалён\n"

        if len(reqs) == 0:
            return "Больше нет запросов на проведение мероприятий", True

        return reply + "Список запросов:\n" + list_requests(reqs, count), False
        
regissue_request = "Пожалуйста напишите о проблеме, о которой вы хотите оповестить администрацию"
def regissue_handler(args: str, user):
    requests.add(args, "issue", user.login)
    return f"Ваш проблема ({args}) была успешно добавленна", True

def list_issues(issues_, count):
    reply = ""
    for index, (_, issue_str, asked_login) in enumerate(issues_):
        reply += f"   /{index + 1} <code>{asked_login}</code>: {issue_str}\n"
    if count - 30 > 0:
        reply += f"   И ещё {count - 30}..."
    reply += "Чтобы удалить одну из проблем, напишите её номер. Можете перестать просматривать список проблем, написав /cancel. Также можете написать сообщение пользователю, который добавил проблему с помощью команды /notify"
    return reply
def issues_handler(args: str, user):
    if args is None:
        issues, count = requests.get(30, "issue")

        if count == 0:
            return "В настоящий момент нет проблем, о которых было бы известно", True
    
        user.aux = issues, count

        return "Вот список проблем, о которых сообщали пользователи:\n" + list_issues(issues, count), False
    else:
        num, = Bots.parse_args(args, 1)

        if num[0] == "/":
            num = num[1:]

        try:
            num = int(num) - 1
        except ValueError:
            return "Номер проблемы, который вы ввели недействителен. Пожалуйста попробуйте ещё раз", False
        issues, count = user.aux

        if (0 <= num < len(issues)) == False:
            return "Номер проблемы, который вы ввели недействителен. Пожалуйста попробуйте ещё раз", False

        id, issue_str, asked_login = issues[num]
        issues.pop(num)

        requests.delete(id)
        reply = f"Пролема \"{issue_str}\" от пользователя \"{asked_login}\" была успешно удалёна\n"

        if len(issues) == 0:
            return "Больше нет проблем, о которых было бы известно", True

        return reply + "Список проблем:\n" + list_issues(issues, count), False

with open("assets\examples\sanitizing_instruction.txt", "r", encoding="utf-8") as file:
    san_instruction_text = file.read()
sanitizing_request = "Напишите /plan чтобы узнать график травли тараканов или /instruction, чтобы получить инструкцию по подготовке комнаты"
def sanitizing_handler(args: str, user):
    command, = Bots.parse_args(args, 1)
    match command:
        case "/plan":
            cur_plan = plan.get()
            if len(cur_plan) == 0:
                return "В настоящий момент нет графика травли тараканов", True
            reply = "Вот график травли тараканов по комнатам:\n"
            for date, room in cur_plan:
                if room != user.room_number:
                    reply += f"   • {date} - {room}\n"
                else:
                    reply += f"   <b>• <ins>{date} - {room}</ins></b>\n"
            return reply, True
        case "/instruction":
            return "Вот инструкцию по подготовке комнаты к травле тараканов:\n" + san_instruction_text, True
        case _:
            return "Вы ввели что-то не то. " + sanitizing_request, False

plansanitizing_request = "Введите график травли тараканов по комнатам в формате:\nДАТА КОМНАТА\nДАТА КОМНАТА\n...\nИли введите delete для удаления нынешнегго графика"
def plansanitizing_handler(args: str, user):
    if Bots.parse_args(args, 1)[0] == "delete":
        plan.unset()
        return "График травли тараканов удалён", True
    if plan.set(args) == False:
        return "Вы ввели данные неверное. Попробуйте ещё раз", False
    return "Новый график травли тараканов сохранён", True


        



ask = Ask("assets/ask.db")

users = Users("assets/users.db")

requests = Requests("assets/requests.db")

plan = Plan("assets/plan.db")

bots = Bots(
    "7837561850:AAF6NI8auEnS6IpuVpULMC-VYzfY0mFbGjE", 
    "vk1.a.5e7Qf-wv7-KLbCcpn0zoLpG-gKY7E5rcdsDrPfWKIx2_hxTWDw_hJLvT_5f5zJ-v-6-yW1grwJSX6Cwqs0TY9IBdq2Cq5gDZznRQJ_gKwbamRK_K1E0KCSy2HHR2xIlUBAgbK_GXHwrY7YiYrV7xbSuoEDNSbgKA_LKihSDG9CBC2113GtEKbGMn0eCR9XLoM7Ks2ivcZ21VFbt-RjwoRA", 
    users,
    default_response, 
    lack_of_rights_response, 
    unathorized_response,
    cant_use_command_response
)






bots.add_handler("/start", start_handler, unauthorized=True, description="Начните работу с ботом")
bots.add_handler("/help", help_handler, unauthorized=True, description="Получение списка доступных действий")
bots.add_handler("/login", login_handler, unauthorized=True, description="Вход в систему")
bots.add_handler("/logout", logout_handler, description="Выход из системы")
bots.add_handler("/me", me_handler, description="Получение информации о себе")


bots.add_handler("/reg", register_handler, require_admin=True, require_argument=register_request, description="Регистрация нового пользователя")
bots.add_handler("/unreg", delete_user_handler, require_admin=True, require_argument=delete_user_request, description="Удаление пользователя из системы")
bots.add_handler("/userinfo", user_info_handler, require_admin=True, require_argument=user_info_request, description="Получение информации о пользователе")
bots.add_handler("/listusers", list_users_handler, require_admin=True, description="Получение списка пользователей")
bots.add_handler("/notify", notify_handler, require_admin=True, require_argument=notify_request, description="Отправить оповещение пользователю")


bots.add_handler("/ask", ask_handler, require_argument=ask_request, description="Задать вопрос")
bots.add_handler("/asknew", ask_new_handler, require_argument=ask_new_request, description="Добавить вопрос")
bots.add_handler("/answer", answer_handler, require_admin=True, description="Ответить на вопросы")


bots.add_handler("/schedule", schedule_handler, description="Получение расписания мест общего пользования")


bots.add_handler("/regevent", regevent_handler, require_argument=regevent_request, description="Добавить запрос на проведение мероприятия")
bots.add_handler("/events", events_handler, require_admin=True, description="Посмотреть список запросов на проведение мероприятий")


bots.add_handler("/regissue", regissue_handler, require_argument=regissue_request, description="Сообщить о проблеме")
bots.add_handler("/issues", issues_handler, require_admin=True, description="Посмотреть список проблем")


bots.add_handler("/sanitizing", sanitizing_handler, require_argument=sanitizing_request, description="Информация о травле тараканов")
bots.add_handler("/plansanitizing", plansanitizing_handler, require_argument=plansanitizing_request, description="Загрузить график травли тараканов")


bots.add_cancel_handler("/cancel", description="Отменить текущее действие", useless_use=useless_use_response, cancel_text=canceled_response)









print("Bots are running now")
bots.run()






  
