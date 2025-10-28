@echo off
echo ===============================================
echo    Отправка бота на GitHub и Railway
echo ===============================================
echo.

echo [1/4] Проверка статуса...
git status
echo.

echo [2/4] Добавление файлов...
git add .
echo Файлы добавлены!
echo.

echo [3/4] Создание коммита...
git commit -m "Обновление: поддержка PostgreSQL"
echo Коммит создан!
echo.

echo [4/4] Отправка на GitHub...
git push
echo.

echo ===============================================
echo    ГОТОВО!
echo ===============================================
echo.
echo Теперь:
echo 1. Открой Railway Dashboard
echo 2. Посмотри вкладку Deployments  
echo 3. Подожди 2-3 минуты
echo 4. Проверь логи
echo.

pause

