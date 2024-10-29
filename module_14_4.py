import os
from aiogram import Bot, executor
from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from keywboards import *
from crud_functions import *
from config import *

try:
    bot = Bot(token=user_token)
    dp = Dispatcher(bot, storage=MemoryStorage())
except NameError:
    user_token = input('Введите ваш токен: ')
    bot = Bot(token=user_token)
    dp = Dispatcher(bot, storage=MemoryStorage())

genders = 5
activ = 1
set_weights = 1
set_growths_ = 1
set_ages = 1
calories = 0
get_index = ''
get_title = ''
get_price = 0
get_description = ''
get_photo = ''
list_img = []
images = './img'
list_img += [each for each in os.listdir(images) if each.endswith('.jpg')]
list_cat = []


class UserState(StatesGroup):
    global set_weights
    global set_growths_
    global set_ages
    global get_index, get_title, get_description, get_price, get_photo
    age = State()
    growth = State()
    weight = State()
    calories = State()


# Выбор принадлежности к полу человека для расчета калорий
@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    text = ('Для мужчин:\n(10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5) x активность'
            '\n\nДля женщин:\n(10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) -161) x активность')
    await call.message.answer(text)
    await call.answer()


# Информация
@dp.message_handler(text='info')
async def inform(message):
    text = ('Домашнее задание по теме "План написания админ панели"'
            '\nЦель: написать простейшие CRUD функции для взаимодействия с базой данных.'
            '\nЗадача "Продуктовая база":'
            '\nСтудент Крылов Эдуард Васильевич.'
            '\nДата работы над заданием: 29.10.2024г.')
    await message.answer(text)


# Расчет по гендерной принадлежности к формуле расчета калорий
@dp.callback_query_handler(text=['5'])
@dp.callback_query_handler(text=['-161'])
async def start_message(call):
    global genders
    genders = float(call.data)
    await call.answer()
    await call.message.answer('Выберите опцию:', reply_markup=key_setting)
    await call.answer()
    return genders


# Ввод возраста для расчета калорий
@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст (число, от 0 до 100):')
    await call.answer()
    await UserState.age.set()


# Ввод роста для расчета калорий
@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    global set_ages
    await state.update_data(age=message.text)
    counting = await state.get_data()
    rep_age = str(counting['age']).replace(",", ".")
    try:
        set_ages = float(rep_age)
        if set_ages <= 100:
            await state.update_data(age=set_ages)
            await message.answer('Введите свой рост (число):')
            await UserState.growth.set()
        else:
            await message.answer(err_age)
            return set_age()
    except ValueError:
        await message.answer(err_age)
        return set_age()


# Ввод веса для расчета калорий
@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    counting = await state.get_data()
    rep_growth = str(counting['growth']).replace(",", ".")
    try:
        set_growths = float(rep_growth)
        await state.update_data(growth=set_growths)
        await message.answer('Введите свой вес (число):')
        await UserState.weight.set()
    except ValueError:
        await message.answer(err_number)
        return set_growth()


# Расчет по степени активности для расчета калорий
@dp.callback_query_handler(text='1.2')
@dp.callback_query_handler(text='1.375')
@dp.callback_query_handler(text='1.55')
@dp.callback_query_handler(text='1.7')
@dp.callback_query_handler(text='1.9')
async def get_active(call):
    global calories
    global set_ages
    global set_growths_
    global set_weights
    global activ
    await call.answer()
    activ = float(call.data)
    calories = float((10 * set_weights + 6.25 * set_growths_ - 5 * set_ages + genders) * activ)
    await call.message.answer(f'Ваша норма калорий: {round(calories, 2)}')
    return calories


# Выбор степени активности
@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    global calories
    global set_ages
    global set_growths_
    global set_weights
    global activ
    await state.update_data(weight=message.text)
    counting = await state.get_data()
    rep_weight = str(counting['weight']).replace(",", ".")
    try:
        set_weights = float(rep_weight)
        await state.update_data(weight=set_weights)
        counting = await state.get_data()
        set_growths_ = counting['growth']
        set_ages = counting['age']
        await message.answer('Выберите свою активность:', reply_markup=key_activ)
        await state.finish()
    except ValueError:
        await message.answer(err_number)
        return set_weight()


# Вывод выбранной покупки из таблицы SQL
@dp.callback_query_handler(text='product_buying')
async def get_product_buying(call):
    global get_index, get_title, get_price, get_description, get_photo
    name_set = str(call.message.caption)
    cursor.execute(f'SELECT * FROM {base_names}')
    products = cursor.fetchall()
    commit()
    for product in products:
        get_index = product[1]
        get_title = product[2]
        get_price = product[4]
        name_set1 = name_set[:name_set.find(' -')] if ' -' in name_set else name_set
        if name_set1 == get_index:
            print(f'\033[31mПоздравляю с покупкой!\n{get_title} по цене: {get_price} руб.\033[0m')
            await call.message.answer(f'Поздравляю с покупкой!\n{get_title} по цене: {get_price} руб.')
    await call.answer()


# Заполнение таблицы SQL данными
@dp.message_handler(text=['Купить'])
async def get_all_products(message):
    global get_index, get_title, get_price, get_description, get_photo
    print(f'\033[31mНаполнение таблицы данными\033[0m')
    text = 'Выберите товар:'
    print(text)
    check_product_list()
    await message.answer(text)
    cursor.execute(f'SELECT * FROM {base_names}')
    products = cursor.fetchall()
    commit()
    for product in products:
        get_index = product[1]
        get_title = product[2]
        get_description = product[3]
        get_price = product[4]
        get_photo = images + '/' + product[5]
        with open(f'{get_photo}', 'rb') as img:
            text = f'{get_index} - № каталога.\nНаименование: {get_title}\nОписание: {get_description}'
            key_shop = InlineKeyboardMarkup(resize_keyboard=True)
            bt = InlineKeyboardButton(text=f'Купить за: {get_price} руб.', callback_data='product_buying')
            key_shop.add(bt)
            await message.answer_photo(img, text, reply_markup=key_shop)


# Приветствие при выборе расчета калорий
@dp.message_handler(text=['Калории'])
async def menu_calories(message):
    text = 'Привет, я бот помогающий твоему здоровью!\nВыберите ваш пол:'
    await message.answer(text, reply_markup=key_gender)


# Старт
@dp.message_handler(text='start')
async def start(message):
    text = f'Здравствуйте, {message.from_user.username}!\nВыберите нужный пункт:'
    await message.answer(text, reply_markup=key_menu)


# Действие при вводе любого символа
@dp.message_handler()
async def all_message(message):
    await message.answer('Нажмите кнопку "start", или "info" чтобы начать общение.', reply_markup=key_start)


# Заполнение таблицы SQL из данных картинок
def check_product_list():
    delete_table()
    for i in range(len(list_img)):
        with open(f'{images}/{list_img[i]}', 'rb'):
            full_img = list_img[i].replace(".jpg", "")
            j = full_img.split('_')
            index_img = str(j[0])
            name_img = str(j[1])
            description_img = f'Описание {i + 1}'
            price_img = int(j[2])
            pfoto_img = list_img[i]
            fill_in_the_table(index_img, name_img, description_img, price_img, pfoto_img)
    screen()


# Управление процессами
if __name__ == '__main__':
    initiate_db(base_names, 'Catalog', 'Title',
                'Description', 'Price', 'Photo')

    # initiate_db(base_names, 'Каталог', 'Название',
    #             'Описание', 'Цена', 'Фотография')
    executor.start_polling(dp, skip_updates=True)
