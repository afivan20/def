from vk_maria import Vk, types
from vk_maria.dispatcher import Dispatcher
from vk_maria.types import KeyboardMarkup, Button, Color
from vk_maria.dispatcher.fsm import StatesGroup, State, MemoryStorage, FSMContext
from vk_maria.upload import Upload
from dotenv import dotenv_values

import pathlib
import os

from templates import CATEGORIES_TEMPLATE
from db import DB


BACK = 'НАЗАД'
DIR = pathlib.Path(__file__).parent.resolve()
MEDIA_DIR = os.path.join(DIR, 'media')
ENV = dotenv_values(os.path.join(DIR, '.env'))
TOKEN = ENV['access_token']


vk = Vk(access_token=TOKEN, api_version='5.131')
upload = Upload(vk)
dp = Dispatcher(vk, MemoryStorage())


class Form(StatesGroup):
    waiting_for_category: State
    waiting_for_item: State


def get_keyboard(category):
    markup = KeyboardMarkup(one_time=True)
    for item in DB['categories'][category]['items']:
        markup.add_button(Button.Text(Color.PRIMARY, item))
    markup.add_button(Button.Text(Color.NEGATIVE, BACK))
    return markup

@dp.message_handler(commands=['start'])
def cmd_start(event: types.Message):
    event.answer(
        message='Добро пожаловать! Выберите интересующую вас категорию.', 
        template=CATEGORIES_TEMPLATE
        )
    Form.waiting_for_category.set()


@dp.message_handler(state=Form.waiting_for_category,)
def process_category(event: types.Message, state: FSMContext):
    if event.message.text not in DB['categories']:
        return event.reply(
            'Неизвестная категория. Пожалуйста, используйте кнопки управления для выбора названия категории.',
            template=CATEGORIES_TEMPLATE
            )
    state.update_data(category=event.message.text)
    markup = get_keyboard(event.message.text)
    event.reply('Выберите товар, используйте кнопки', keyboard=markup)
    Form.next()


@dp.message_handler(state=Form.waiting_for_item)
def process_item(event: types.Message, state: FSMContext):
    category = state.get_data()['category']
    if event.message.text == BACK:
        event.reply('Выберите интересующую вас категория.', template=CATEGORIES_TEMPLATE)
        return Form.waiting_for_category.set()
    elif event.message.text not in DB['categories'][category]['items']:
        markup = get_keyboard(category)
        return event.reply(
            'Неизвестный товар. Пожалуйста, используйте кнопки управления для выбора названия товара.',
            keyboard=markup
            )

    description = DB['categories'][category]['items'][event.message.text][1]
    file = DB['categories'][category]['items'][event.message.text][0]
    path = os.path.join(MEDIA_DIR, f'{file}')
    photo = upload.photo(open(path, 'rb'))
    event.reply(f'{description}', attachment=photo)
    Form.finish()


dp.start_polling(debug=True)
