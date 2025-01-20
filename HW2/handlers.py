from aiogram import Router
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states import Form
from func import *

router=Router()

#Обработчик команды /start
@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.reply(
        'Это Telegram-бот, который может рассчитать дневные нормы воды и калорий, а также отслеживать тренировки и питание.\n'
        'Доступные команды:\n'
        '/set_profile - Настройка профиля пользователя\n'
        '/log_water <количество> - Логирование воды\n'
        '/log_food <название продукта> - Логирование еды\n'
        '/log_workout <время (мин)> - Логирование тренировок\n'
        '/check_progress - Прогресс по воде и калориям'
    )

#Обработчик команды /set_profile
profile = {'weight' : 0,
            'height' : 0,
            'age' : 0,
            'activity' : 0,
            'city' : 0,
            'water_goal' : 0,
            'calorie_goal' : 0,
            'water' : 0,
            'calories' : 0,
            'workout' : 0,
           'burned_calories' : 0}

@router.message(Command('set_profile'))
async def start_form(message: Message, state: FSMContext):
    await message.reply('Введите ваш вес (в кг)?')
    await state.set_state(Form.weight)

@router.message(Form.weight)
async def process_weight(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await message.reply('Введите ваш рост (в см)?')
    await state.set_state(Form.height)

@router.message(Form.height)
async def process_height(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await message.reply('Введите ваш возраст?')
    await state.set_state(Form.age)

@router.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply('Сколько минут активности у вас в день?')
    await state.set_state(Form.activity)

@router.message(Form.activity)
async def process_activity(message: Message, state: FSMContext):
    await state.update_data(activity=message.text)
    await message.reply('В каком городе вы находитесь?')
    await state.set_state(Form.city)

@router.message(Form.city)
async def process_city(message: Message, state: FSMContext):
    data = await state.get_data()
    profile['weight'] = float(data.get('weight'))
    profile['height'] = float(data.get('height'))
    profile['age'] = float(data.get('age'))
    profile['activity'] = float(data.get('activity'))
    profile['city'] = message.text
    await state.clear()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Всё верно', callback_data='Yes')],
            [InlineKeyboardButton(text='Надо исправить', callback_data='No')]
        ]
    )
    await message.reply('Проверьте введенные данные:\n'
                        f'Вес: {profile["weight"]} кг\n'
                        f'Рост: {profile["height"]} см\n'
                        f'Возраст: {profile["age"]} лет\n'
                        f'Активность: {profile["activity"]} мин в день\n'
                        f'Город: {profile["city"]}\n',
                        reply_markup=keyboard)

@router.callback_query()
async def handle_callback(callback_query):
    if callback_query.data == 'Yes':
        response = await weather_in_city(profile['city'])
        profile['water_goal']=profile['weight']*30+(profile['activity']//30)*500+(response['main']['temp']//25)*500

        profile['calorie_goal']=10*profile['weight']+6.25*profile['height']-5*profile['age']+300*(profile['activity']//30)
        await callback_query.message.reply(f"Сегодня Ваша норма воды: {profile['water_goal']} мл\n"
                            f"Норма калорий: {profile['calorie_goal']} ккал")
    else:
        await callback_query.message.reply('Введите /set_profile и начните заполнение заново')


#Обработчик команды /log_water
@router.message(Command('log_water'))
async def log_water(message: Message, command: CommandObject):
    water=float(command.args)
    if not water:
        await message.reply("Укажите количество выпитой воды (в мл)  через пробел после команды /log_water")
        return
    profile['water']+=water
    await message.reply(f"Сегодня вы выпили {profile['water']} мл воды. Выпейте еще {profile['water_goal'] - profile['water']} мл, чтобы выполнить норму")


#Обработчик команды /log_food
@router.message(Command('log_food'))
async def log_food(message: Message, command: CommandObject):
    food=command.args
    if not food:
        await message.reply("Укажите название продукта через пробел после команды /log_food")
        return
    calories=float(get_food_info(food)['calories'])
    profile['calories']+=calories
    await message.reply(f"Сегодня вы уже получили {profile['calories']} ккал. До выполнения нормы осталось еще {profile['calorie_goal'] - profile['calories']} ккал")


#Обработчик команды /log_workout
@router.message(Command('log_workout'))
async def log_workout(message: Message, command: CommandObject):
    workout=float(command.args)
    if not workout:
        await message.reply("Укажите время тренировки (в мин) через пробел после команды /log_workout")
        return
    profile['workout']+=workout
    calories=workout*10
    profile['burned_calories']=calories
    water=(workout//30)*200
    profile['water_goal']+=water
    await message.reply(f"Записана тренировка {workout} минут. Вы сожгли {calories} ккал, выпейте дополнительно {water} мл воды")


#Обработчик команды /check_progress
@router.message(Command('check_progress'))
async def check_progress(message: Message):
    await message.reply('Вода:\n'
                        f'-Выпито: {profile["water"]} мл из {profile["water_goal"]} мл\n'
                        f'-Осталось: {profile["water_goal"]-profile["water"]} мл\n'
                        'Калории:\n'
                        f'- Потреблено: {profile["calories"]} ккал из {profile["calorie_goal"]} ккал\n'
                        f'- Сожжено: {profile["burned_calories"]} ккал\n'
                        f'- Баланс: {profile["calories"]-profile["burned_calories"]} ккал')

