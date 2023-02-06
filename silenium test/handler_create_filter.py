import os
from datetime import datetime as datatime_datatime
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.filters import Command
from config_reader import config
from keyboards import multi_row_keyboard
from b_logic.parse_asynch_av_by_json import count_cars_av, parse_main
from b_logic.do_pdf import do_pdf
from b_logic.get_url import all_get_url
from b_logic.constant_fu import (s_b, get_years, get_cost, get_dimension, get_brands, get_models, columns_cost,
                                 columns_years, columns_dimension, columns_motor, motor, transmission,
                                 decode_filter_short, code_filter_short,)


router = Router()
bot = Bot(token=config.bot_token.get_secret_value())


class CreateCar(StatesGroup):
    brand_choosing = State()
    model_choosing = State()
    motor_choosing = State()
    transmission_choosing = State()
    year_choosing = State()
    yearm_choosing = State()
    cost_choosing = State()
    costm_choosing = State()
    dimension_choosing = State()
    dimensionm_choosing = State()
    finish_choosing = State()


@router.message(F.text.startswith('filter='))
async def cooking_pdf(message: Message):
    if message.text[0:7] == 'filter=':
        cars = message.text.replace('filter=', '')
        await message.answer("Фильтр принят\n"
                             "дождитесь ответа", reply_markup=ReplyKeyboardRemove())
        av_link, abw_link = await all_get_url(cars)
        all_cars_av = count_cars_av(av_link)
        await message.answer(f"Найдено: \n"
                             f"Действует ограничение до 125 объявлений с 1 ресурса.\n"
                             f"<a href='{av_link}'>av.by</a> - {all_cars_av}.\n",
                             disable_web_page_preview=True,
                             parse_mode="HTML",
                             )
        if all_cars_av == 0:
            return await message.answer("По вашему запросу ничего не найдено,\n"
                                        "или запрашиваемый сервер перегружен")
        else:
            name_time_stump = (str(datatime_datatime.now())).replace(':', '.')
            try:
                parse_main(av_link, message=message.from_user.id, name=name_time_stump)
            except:
                print('Ошибка в parse_main')
                return await message.answer("Ошибка при сборе данных.\n"
                                            "Повторите попытку /search.")
            await message.answer(f"Сбор данных.")
            try:
                try:
                    await do_pdf(
                        message=message.from_user.id,
                        av_by_link=av_link,
                        name=name_time_stump,
                        filter_full=decode_filter_short(cars),
                        filter_short=message.text)
                    os.remove(f'b_logic/buffer/{message.from_user.id}{name_time_stump}.npy')
                except Exception as error:
                    os.remove(f'b_logic/buffer/{message.from_user.id}{name_time_stump}.npy')
                    print(error, "<--> Ошибка при формировании отчета")
                    return await message.answer("Ошибка при создании pdf")
                if os.path.exists(f'b_logic/buffer/{name_time_stump}.pdf'):
                    file = FSInputFile(f'b_logic/buffer/{name_time_stump}.pdf')
                    await bot.send_document(message.chat.id, document=file)
                    os.remove(f'b_logic/buffer/{name_time_stump}.pdf')

                else:
                    print(f'{name_time_stump}.pdf не найден')
            except Exception as error:
                print(error)


@router.message(Command(commands=["search"]))
@router.message(F.text.casefold() == "search")
async def get_rusult(message: Message, state: FSMContext):
    await state.set_state('finish_choosing')
    data = await state.get_data()
    c = []
    for item in data:
        c.append(data[item])
    cc = c.copy()
    if len(c) > 0 and c[0] != s_b:
        await message.answer(
            text=decode_filter_short(lists=c),
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(
            text='подтвердите фильтр:',
            reply_markup=multi_row_keyboard([code_filter_short(cc)])
        )
        await cooking_pdf(message=message)
    else:
        await message.answer(
            text=f"Фильтр пуст. Воспользуйтесь командой /car",
            reply_markup=ReplyKeyboardRemove()
        )


@router.message(Command(commands=["car"]))
@router.message(F.text.casefold() == "car")
async def brand_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_brand=s_b,
                            chosen_model=s_b,
                            chosen_motor=s_b,
                            chosen_transmission=s_b,
                            chosen_year_from=s_b,
                            chosen_year_to=s_b,
                            chosen_cost_min=s_b,
                            chosen_cost_max=s_b,
                            chosen_dimension_min=s_b,
                            chosen_dimension_max=s_b,
                            )
    await message.answer(
        text="Выберите бренд автомобиля:",
        reply_markup=multi_row_keyboard(
            await get_brands(),
            input_field_placeholder='имя бренда',
            )
    )
    await state.set_state(CreateCar.brand_choosing)


@router.message(CreateCar.brand_choosing)
async def model_chosen(message: Message, state: FSMContext):
    if message.text in await get_brands():
        await state.update_data(chosen_brand=message.text)
        await message.answer(
            text="Теперь, выберите модель:",
            reply_markup=multi_row_keyboard(
                await get_models(message.text),
                input_field_placeholder='имя модели')
            )
    else:
        await message.answer(
            text="Я не знаю такого бренда.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_brands(),
                input_field_placeholder='имя бренда')
        )
        return model_chosen
    await state.set_state(CreateCar.model_choosing)


@router.message(CreateCar.model_choosing)
async def motor_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text in await get_models(user_data['chosen_brand']):
        await state.update_data(chosen_model=message.text)
        await message.answer(
            text="Теперь, выберите тип топлива:",
            reply_markup=multi_row_keyboard(
                motor,
                input_field_placeholder='тип топлива',
                columns=columns_motor,
            )
        )
    else:
        await message.answer(
            text="Я не знаю такой модели.\n"
                 "Пожалуйста, выберите один из вариантов из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_models(user_data['chosen_brand']),
                input_field_placeholder='имя модели'
            )
        )
        return motor_chosen
    await state.set_state(CreateCar.motor_choosing)


@router.message(CreateCar.motor_choosing)
async def transmission_chosen(message: Message, state: FSMContext):
    if message.text in motor:
        await state.update_data(chosen_motor=message.text)
        await message.answer(
            text="Теперь, выберите тип трансмиссии:",
            reply_markup=multi_row_keyboard(
                transmission,
                input_field_placeholder='тип трансмиссии'
            )
        )
    else:
        await message.answer(
            text="Я не знаю такого топлива.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                motor,
                input_field_placeholder='тип топлива',
                columns=columns_motor,
            )
        )
        return transmission_chosen
    await state.set_state(CreateCar.transmission_choosing)


@router.message(CreateCar.transmission_choosing)
async def from_year_chosen(message: Message, state: FSMContext):
    if message.text in transmission:
        await state.update_data(chosen_transmission=message.text)
        await message.answer(
            text="Теперь, выберите с какого года:",
            reply_markup=multi_row_keyboard(
                get_years(),
                input_field_placeholder='год от',
                columns=columns_years,
            )
        )
    else:
        await message.answer(
            text="Я не знаю такой трансмиссии.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                transmission,
                input_field_placeholder='тип трансмиссии'
            )
        )
        return from_year_chosen
    await state.set_state(CreateCar.year_choosing)


@router.message(CreateCar.year_choosing)
async def to_year_chosen(message: Message, state: FSMContext):
    if message.text in get_years():
        year = get_years()[1] if message.text == s_b else message.text
        await state.update_data(chosen_year_from=message.text)
        await message.answer(
            text="Теперь, выберите по какой год:",
            reply_markup=multi_row_keyboard(
                get_years(from_year=int(year)),
                input_field_placeholder='год по',
                columns=columns_years,
            )
        )
    else:
        await message.answer(
            text="Год от введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_years(),
                input_field_placeholder='год от',
                columns=columns_years,
            )
        )
        return to_year_chosen
    await state.set_state(CreateCar.yearm_choosing)


@router.message(CreateCar.yearm_choosing)
async def min_cost_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    year = get_years()[1] if s_b == user_data['chosen_year_from'] else user_data['chosen_year_from']
    if message.text in get_years(from_year=int(year)):
        await state.update_data(chosen_year_to=message.text)
        await message.answer(
            text="Теперь, выберите начальную цену:",
            reply_markup=multi_row_keyboard(
                get_cost(),
                input_field_placeholder='стоимость от',
                columns=columns_cost,
            )
        )
    else:
        await message.answer(
            text="Год до введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_years(from_year=int(year)),
                input_field_placeholder='год по',
                columns=columns_years,
            )
        )
        return min_cost_chosen
    await state.set_state(CreateCar.cost_choosing)


@router.message(CreateCar.cost_choosing)
async def max_cost_chosen(message: Message, state: FSMContext):
    if message.text in get_cost():
        cost = get_cost()[1] if message.text == s_b else message.text
        await state.update_data(chosen_cost_min=message.text)
        await message.answer(
            text="Теперь, выберите максимальную цену:",
            reply_markup=multi_row_keyboard(
                get_cost(from_cost=int(cost)),
                input_field_placeholder='стоимость до',
                columns=columns_cost,
            )
        )
    else:
        await message.answer(
            text="Цена введена не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_cost(),
                input_field_placeholder='стоимость от',
                columns=columns_cost,
            )
        )
        return max_cost_chosen
    await state.set_state(CreateCar.dimension_choosing)


@router.message(CreateCar.dimension_choosing)
async def min_dimension_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    cost = get_cost()[1] if s_b == user_data['chosen_cost_min'] else user_data['chosen_cost_min']
    if message.text in get_cost(from_cost=int(cost)):
        await state.update_data(chosen_cost_max=message.text)
        await message.answer(
            text="Теперь, выберите минимальный объем двигателя:",
            reply_markup=multi_row_keyboard(
                get_dimension(),
                input_field_placeholder='объем двигателя от',
                columns=columns_dimension,
            )
        )
    else:
        await message.answer(
            text="Цена введена не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_cost(from_cost=int(user_data['chosen_cost_min'])),
                input_field_placeholder='стоимость до',
                columns=columns_cost,
            )
        )
        return min_dimension_chosen
    await state.set_state(CreateCar.dimensionm_choosing)


@router.message(CreateCar.dimensionm_choosing)
async def max_dimension_chosen(message: Message, state: FSMContext):
    if message.text in get_dimension():
        dimension = get_dimension()[1] if message.text == s_b else message.text
        await state.update_data(chosen_dimension_min=message.text)
        await message.answer(
            text="Теперь, выберите максимальный объем двигателя:",
            reply_markup=multi_row_keyboard(
                get_dimension(from_dim=float(dimension)),
                input_field_placeholder='объем двигателя до',
                columns=columns_dimension,
            )
        )
    else:
        await message.answer(
            text="Объем введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_dimension(),
                input_field_placeholder='объем двигателя от',
                columns=columns_dimension,
            )
        )
        return max_dimension_chosen
    await state.set_state(CreateCar.finish_choosing)


@router.message(CreateCar.finish_choosing)
async def finish_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    dimension = get_dimension()[1] if s_b == user_data['chosen_dimension_min'] \
        else user_data['chosen_dimension_min']
    if message.text in get_dimension(from_dim=float(dimension)):
        await state.update_data(chosen_dimension_max=message.text)
    else:
        await message.answer(
            text="Объем введен не верно.\n"
                 "Пожалуйста, выберите одно из названий из списка ниже:",
            reply_markup=multi_row_keyboard(
                get_dimension(from_dim=float(user_data['chosen_dimension_min'])),
                input_field_placeholder='объем до',
            )
        )
        return finish_chosen
    await get_rusult(message=message, state=state)
