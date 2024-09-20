Проект Booking

    Возможности:
    - Управление квартирами: создание, просмотр, обновление и удаление.
    - Управление бронированиями: создание, просмотр, обновление и удаление.
    - Управление пользователями: регистрация, аутентификация, просмотр профиля.
    - Оценка бронирований: добавление отзывов и рейтингов.

    Эндпоинты:
    - /apartments/ [GET, POST]: Получение списка квартир, создание новой квартиры.
    - /apartments/{id}/ [GET, PUT, DELETE]: Получение, обновление, удаление конкретной квартиры.
    - /reservations/ [GET, POST]: Получение списка бронирований, создание нового бронирования.
    - /reservations/{id}/ [GET, PUT, DELETE]: Получение, обновление, удаление конкретного бронирования, добавление отзыва по завершении бронирования.
    - /apartments/{id}/ratings/ [GET]: Просмотр отзывов на апартаменты.
    - /users/register/ [POST]: Регистрация нового пользователя.
    - /users/login/ [POST]: Аутентификация пользователя.
    - /users/profile/ [GET]: Получение профиля текущего пользователя.
    - /ratings/ [GET, POST]: Получение списка отзывов, добавление нового отзыва.
    - /ratings/{id}/ [GET, PUT, DELETE]: Получение, обновление, удаление конкретного отзыва.
