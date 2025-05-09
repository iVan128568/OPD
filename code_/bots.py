


from code_.users import Users
import asyncio
import vkbottle.bot
import telebot
import telebot.async_telebot
from types import SimpleNamespace as nspace
import bs4



import nest_asyncio
nest_asyncio.apply()




class Bot:

    def __init__(
            self, token: str, 
            users_management: Users, 
            default_response = "Default response", 
            lack_of_rights_response = 'No rights to use this command',
            unathorized_response = 'Log in to use commands',
            cant_use_command_response = 'You cant use commands here. To cancel use cancel command'
        ) -> None:
        
        self.bot = self.create_bot(token)
        self.users_management = users_management

        self.default_response = default_response
        self.lack_of_rights_response = lack_of_rights_response
        self.unathorized_response = unathorized_response
        self.cant_use_command_response = cant_use_command_response

        self.handler_map = {}
        self.descriptions = {}
        self.process_on_next_step = {}

        self.unathorized_handlers = {}
        self.cancel_command = None

        self.bind_main_handler()

    
    async def main_handler(self, text: str, user_id: str, aux_for_sending):
        command, *_ = text.lstrip(" ").split(" ", 1)

        user = self.users_management.get_user_by_id(user_id)
        if user is None:
            user = nspace(login = None)
        user.cur_chat_id = user_id
        user.aux = None
        handler = self.handler_map.get(command) 

        if user_id in self.process_on_next_step:
            if self.cancel_command and command == self.cancel_command:
                await self.send_message(self.cancel_text, aux_for_sending)
                del self.process_on_next_step[user_id]
                return
            if command in self.handler_map:
                await self.send_message(self.cant_use_command_response, aux_for_sending)
                return
            await self.process_handler(text, user_id, aux_for_sending)
            return
        
        if handler is None:
            await self.send_message(self.default_response, aux_for_sending)
            return
        
        if user.login is None and handler.unauthorized == False:
            await self.send_message(self.unathorized_response, aux_for_sending)
            return
        
        if handler.require_admin and user.is_admin == False:
            await self.send_message(self.lack_of_rights_response, aux_for_sending)
            return
        
        self.process_on_next_step[user_id] = handler.handler, user

        if handler.require_argument:
            await self.send_message(handler.require_argument, aux_for_sending)
            return 
        
        await self.process_handler(None, user_id, aux_for_sending)


    async def process_handler(self, text: str, user_id: str, aux_for_sending):
        handler, user = self.process_on_next_step[user_id]
        response, break_ = handler(text, user)
        await self.send_message(response, aux_for_sending)
        if break_:
            del self.process_on_next_step[user_id]


    def clear_user_next_steps(self, login: str):
        user = self.users_management.get_user_by_login(login)
        if user is None:
            raise KeyError("There no such user")
        for id in user.chat_ids:
            if id in self.process_on_next_step:
                del self.process_on_next_step[id]


    def add_handler(self, command: str, handler, require_admin = False, require_argument: str = None, description: str = "Default description", unauthorized = False):
        if description.strip() == "":
            description = "Default description"

        if command in self.handler_map:
            raise KeyError("this command already got a handler")
        
        self.handler_map[command] = nspace(handler = handler, require_admin = require_admin, require_argument = require_argument, unauthorized = unauthorized)
        self.descriptions[command] = description

    
    def add_cancel_handler(self, command, description: str = "Default description", useless_use: str = "You cant use this here", cancel_text = "Canceled"):
        def dummy_handler(args, user):
            return useless_use, True
        self.add_handler(command, dummy_handler, description=description, unauthorized=True)
        self.cancel_command = command
        self.cancel_text = cancel_text


    def create_bot(self, token):
        raise NotImplementedError("This func should only be called in child class")
    
    def bind_main_handler(self):
        raise NotImplementedError("This func should only be called in child class")
    
    async def send_message(self, text, aux_for_sending):
        raise NotImplementedError("This func should only be called in child class")
    
    async def run(self):
        raise NotImplementedError("This func should only be called in child class")




class TG_bot(Bot):

    def create_bot(self, token):
        return telebot.async_telebot.AsyncTeleBot(token, parse_mode="HTML")
    
    def bind_main_handler(self):
        @self.bot.message_handler(content_types=['text'])
        async def handler(message: telebot.types.Message):
            await self.main_handler(message.text, "tg" + str(message.from_user.id), message.from_user.id)

    async def send_message(self, text, aux_for_sending):
        await self.bot.send_message(aux_for_sending, text)

    def notify(self, text: str, login: str):
        user = self.users_management.get_user_by_login(login)
        if user is None:
            raise KeyError("There no such user")
        for id in user.chat_ids:
            tag, id = id[:2], id[2:]
            if tag == "tg":
                asyncio.run(self.bot.send_message(id, text))

    async def run(self):
        await self.set_commands()
        await self.bot.infinity_polling(logger_level=telebot.logging.DEBUG)

    async def set_commands(self):
        commands_list = []
        for command, description in self.descriptions.items():
            if command[0] == '/':
                command = command[1:]
            commands_list.append(telebot.types.BotCommand(command, description))
        await self.bot.set_my_commands(commands_list)



class VK_bot(Bot):

    def create_bot(self, token):
        return vkbottle.bot.Bot(token)
    
    def bind_main_handler(self):
        @self.bot.on.private_message(text='<message>')
        async def handler(message_data: vkbottle.bot.Message, message: str):
            await self.main_handler(message, "vk" + str(message_data.from_id), message_data)

    async def send_message(self, text, aux_for_sending: vkbottle.bot.Message):
        await aux_for_sending.answer(self.parse_message(text))

    def notify(self, text: str, login: str):
        user = self.users_management.get_user_by_login(login)
        if user is None:
            raise KeyError("There no such user")
        for id in user.chat_ids:
            tag, id = id[:2], id[2:]
            if tag == "vk":
                self.bot: vkbottle.bot.Bot # /////////////////////////////////////////////
                asyncio.run(self.bot.api.messages.send(user_id=id, message=self.parse_message(text), random_id=0))

    async def run(self):
        await self.bot.run_polling()

    @staticmethod
    def parse_message(text: str):
        if '<' in text or '>' in text:
            text = bs4.BeautifulSoup(text, "html.parser").get_text()
        return text

    










class Bots:

    def __init__(
            self, 
            tg_token: str, 
            vk_token: str, 
            users_management: Users, 
            default_response = "Default response", 
            lack_of_rights_response = 'No rights to use this command',
            unathorized_response = 'Log in to use commands',
            cant_use_command_response = 'You cant use commands here. To cancel use cancel command'
        ) -> None:

        self.tg_bot = TG_bot(tg_token, users_management, default_response, lack_of_rights_response, unathorized_response, cant_use_command_response)
        self.vk_bot = VK_bot(vk_token, users_management, default_response, lack_of_rights_response, unathorized_response, cant_use_command_response)
        self.descriptions = self.tg_bot.descriptions
        self.handler_map = self.tg_bot.handler_map


    def clear_user_next_steps(self, login: str):
        self.tg_bot.clear_user_next_steps(login)
        self.vk_bot.clear_user_next_steps(login)


    def add_handler(self, command: str, handler, require_admin = False, require_argument: str = None, description: str = "Default description", unauthorized = False):
        self.tg_bot.add_handler(command, handler, require_admin, require_argument, description, unauthorized)
        self.vk_bot.add_handler(command, handler, require_admin, require_argument, description, unauthorized)


    def add_cancel_handler(self, command, description: str = "Default description", useless_use: str = "You cant use this here", cancel_text = "Canceled"):
        self.tg_bot.add_cancel_handler(command, description, useless_use, cancel_text)
        self.vk_bot.add_cancel_handler(command, description, useless_use, cancel_text)


    def notify(self, text: str, login: str):
        self.tg_bot.notify(text, login)
        self.vk_bot.notify(text, login)


    def run(self):   # //////////////////////////
        async def launch():
            await asyncio.gather(
                self.tg_bot.run(), 
                self.vk_bot.run()
            )

        try:
            asyncio.run(launch())
        except RuntimeError as e:
            if e.args[0] != "Cannot close a running event loop":
                raise e
        except KeyboardInterrupt:
            pass
        
        
    @staticmethod
    def parse_args(args: str, amount: int):
        result = [arg.lstrip().rstrip() for arg in args.replace("\n", " ").split(" ")]
        result = tuple(filter(lambda arg: arg != "", result))
        return result if len(result) == amount else (None,) * amount

        



