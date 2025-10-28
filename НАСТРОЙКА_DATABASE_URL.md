# 🔧 Настройка DATABASE_URL для PostgreSQL

## 🐛 Проблема

В логах видно:
```
INFO - База данных SQLite создана
```

Это значит, что бот **НЕ видит PostgreSQL** и использует SQLite!

---

## ✅ Решение

Нужно **вручную** добавить переменную `DATABASE_URL` в Railway.

---

## 📋 Шаг за шагом

### 1. Откройте Railway Dashboard

1. Перейдите на [railway.app](https://railway.app)
2. Выберите ваш проект
3. Откройте вкладку **"Variables"** (боковое меню)

### 2. Найдите DATABASE_URL

Railway **должен** автоматически создать эту переменную когда вы добавляете PostgreSQL.

**Проверьте:**
- Есть ли в списке переменная `DATABASE_URL`?
- Если да → всё OK!
- Если нет → читайте дальше

### 3. Если переменной НЕТ

Добавьте её вручную:

1. В Railway → **"Variables"** → **"+ New Variable"**
2. **Ключ:** `DATABASE_URL`
3. **Значение:** Нажмите **"Reference"** → выберите **"postgres.DATABASE_URL"**
4. **Или:** Скопируйте значение из Postgres сервиса

### 4. Получить URL вручную

Если не работает **"Reference"**:

1. Откройте **Postgres** сервис в Railway
2. Нажмите **"Data"** или **"Connect"**
3. Там будет **Connection string** - скопируйте его
4. Добавьте как переменную `DATABASE_URL`

### 5. Перезапустите бота

После добавления переменной:

1. Railway автоматически перезапустит бота
2. Или вручную: **"Deployments"** → **"..."** → **"Redeploy"**

### 6. Проверьте логи

Теперь в логах должно быть:

**До (SQLite):**
```
INFO - База данных SQLite создана
```

**После (PostgreSQL):**
```
INFO - Используется PostgreSQL из Railway
INFO - Инициализация PostgreSQL...
INFO - База данных PostgreSQL инициализирована  
INFO - PostgreSQL готов к работе
```

---

## 🎯 Альтернативный способ

Если `DATABASE_URL` не работает, используйте подключение напрямую:

1. Откройте **Postgres** сервис
2. Там есть **"Connection info"**
3. Соберите URL вручную:

```
postgresql://username:password@host:port/dbname
```

Где:
- username - из Connection info
- password - из Connection info  
- host - из Connection info
- port - из Connection info
- dbname - обычно `postgres`

4. Добавьте как переменную `DATABASE_URL`

---

## ✅ Проверка

После добавления переменной:

1. **Подождите 2-3 минуты** - Railway перезапустит бот
2. **Откройте логи** в Railway
3. **Должно быть:** "Используется PostgreSQL из Railway"
4. **Отправьте `/start`** - должно работать

---

## 📝 Пример URL

DATABASE_URL должен выглядеть так:

```
postgresql://postgres:пароль@container.railway.app:5432/railway
```

Или:

```
postgresql://username:password@host.railway.app:port/railway
```

---

## 🆘 Если ничего не работает

### Временное решение:

Пока `DATABASE_URL` не настроен, бот использует **SQLite**.

Это нормально для начала! Позже можно переключиться на PostgreSQL.

**Бот работает и так!** ✅

---

**Главное сейчас** - протестируйте что бот отвечает на команды и показывает меню!

