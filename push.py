if user.login:
    answer = request_to_yaklass(message.from_user.id)
    if answer == Text.return_text_jaklass:
        user.place = 'menu'
        # text = [f"{NADO_YDALIT}", f"К радости у вас нет работ."]
        text = [Text.return_text_jaklass]
        return bot.send_message(message.from_user.id, "\n".join(text),
                                reply_markup=buttons_creator(Buttons.update))
    elif type(answer) is list:
        text = [Text.bad_news, ""]
        # user.place = 'menu'
        min_time = answer[0]["time(d)"]
        utcmoment_naive = datetime.datetime.utcnow()
        utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)
        time_now = utcmoment.astimezone(pytz.timezone(timezones[0]))
        k = InlineKeyboardMarkup(row_width=1)
        for i in answer:
            text.append(f"Название: {i['name']}")
            text.append(f"Оставшееся время: {i['time']}")
            text.append(f"Ссылка: {i['href']}")
            text.append("")
            k.add(
                InlineKeyboardButton(i['name'] if len(i['name']) <= 30 else i['name'][: 30] + "...",
                                     url=i['href']))
        text = text[: -1]
        k.add(InlineKeyboardButton('Обновить', callback_data="update"))
        bot.send_message(user.tg_id, "\n".join(text),
                         reply_markup=k)
        bot.send_message(user.tg_id, Text.main_menu, reply_markup=keyboard_creator(Keyboard.main_menu))
        user.last_time = time_now
        session.commit()
        update_yandex_disk()
else:
    user.place = 'login'
    session.commit()
    return bot.send_message(message.from_user.id, Text.start, reply_markup=ReplyKeyboardRemove())