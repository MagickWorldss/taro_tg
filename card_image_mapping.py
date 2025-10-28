"""
Маппинг русских названий карт к файлам изображений
"""

# Маппинг: Русское название → Путь к файлу изображения
CARD_TO_IMAGE_PATH = {
    # Старшие арканы
    "Дурак": "images/tarot_images/major/00_fool.jpg",
    "Маг": "images/tarot_images/major/01_magician.jpg",
    "Жрица": "images/tarot_images/major/02_high_priestess.jpg",
    "Императрица": "images/tarot_images/major/03_empress.jpg",
    "Император": "images/tarot_images/major/04_emperor.jpg",
    "Иерофант": "images/tarot_images/major/05_hierophant.jpg",
    "Влюбленные": "images/tarot_images/major/06_lovers.jpg",
    "Колесница": "images/tarot_images/major/07_chariot.jpg",
    "Сила": "images/tarot_images/major/08_strength.jpg",
    "Отшельник": "images/tarot_images/major/09_hermit.jpg",
    "Колесо Фортуны": "images/tarot_images/major/10_wheel_of_fortune.jpg",
    "Справедливость": "images/tarot_images/major/11_justice.jpg",
    "Повешенный": "images/tarot_images/major/12_hanged_man.jpg",
    "Смерть": "images/tarot_images/major/13_death.jpg",
    "Умеренность": "images/tarot_images/major/14_temperance.jpg",
    "Дьявол": "images/tarot_images/major/15_devil.jpg",
    "Башня": "images/tarot_images/major/16_tower.jpg",
    "Звезда": "images/tarot_images/major/17_star.jpg",
    "Луна": "images/tarot_images/major/18_moon.jpg",
    "Солнце": "images/tarot_images/major/19_sun.jpg",
    "Суд": "images/tarot_images/major/20_judgement.jpg",
    "Мир": "images/tarot_images/major/21_world.jpg",
    
    # Жезлы
    "Туз Жезлов": "images/tarot_images/wands/01_ace_of_wands.jpg",
    "Двойка Жезлов": "images/tarot_images/wands/02_two_of_wands.jpg",
    "Тройка Жезлов": "images/tarot_images/wands/03_three_of_wands.jpg",
    "Четверка Жезлов": "images/tarot_images/wands/04_four_of_wands.jpg",
    "Пятерка Жезлов": "images/tarot_images/wands/05_five_of_wands.jpg",
    "Шестерка Жезлов": "images/tarot_images/wands/06_six_of_wands.jpg",
    "Семерка Жезлов": "images/tarot_images/wands/07_seven_of_wands.jpg",
    "Восьмерка Жезлов": "images/tarot_images/wands/08_eight_of_wands.jpg",
    "Девятка Жезлов": "images/tarot_images/wands/09_nine_of_wands.jpg",
    "Десятка Жезлов": "images/tarot_images/wands/10_ten_of_wands.jpg",
    "Паж Жезлов": "images/tarot_images/wands/11_page_of_wands.jpg",
    "Рыцарь Жезлов": "images/tarot_images/wands/12_knight_of_wands.jpg",
    "Королева Жезлов": "images/tarot_images/wands/13_queen_of_wands.jpg",
    "Король Жезлов": "images/tarot_images/wands/14_king_of_wands.jpg",
    
    # Кубки
    "Туз Кубков": "images/tarot_images/cups/01_ace_of_cups.jpg",
    "Двойка Кубков": "images/tarot_images/cups/02_two_of_cups.jpg",
    "Тройка Кубков": "images/tarot_images/cups/03_three_of_cups.jpg",
    "Четверка Кубков": "images/tarot_images/cups/04_four_of_cups.jpg",
    "Пятерка Кубков": "images/tarot_images/cups/05_five_of_cups.jpg",
    "Шестерка Кубков": "images/tarot_images/cups/06_six_of_cups.jpg",
    "Семерка Кубков": "images/tarot_images/cups/07_seven_of_cups.jpg",
    "Восьмерка Кубков": "images/tarot_images/cups/08_eight_of_cups.jpg",
    "Девятка Кубков": "images/tarot_images/cups/09_nine_of_cups.jpg",
    "Десятка Кубков": "images/tarot_images/cups/10_ten_of_cups.jpg",
    "Паж Кубков": "images/tarot_images/cups/11_page_of_cups.jpg",
    "Рыцарь Кубков": "images/tarot_images/cups/12_knight_of_cups.jpg",
    "Королева Кубков": "images/tarot_images/cups/13_queen_of_cups.jpg",
    "Король Кубков": "images/tarot_images/cups/14_king_of_cups.jpg",
    
    # Мечи
    "Туз Мечей": "images/tarot_images/swords/01_ace_of_swords.jpg",
    "Двойка Мечей": "images/tarot_images/swords/02_two_of_swords.jpg",
    "Тройка Мечей": "images/tarot_images/swords/03_three_of_swords.jpg",
    "Четверка Мечей": "images/tarot_images/swords/04_four_of_swords.jpg",
    "Пятерка Мечей": "images/tarot_images/swords/05_five_of_swords.jpg",
    "Шестерка Мечей": "images/tarot_images/swords/06_six_of_swords.jpg",
    "Семерка Мечей": "images/tarot_images/swords/07_seven_of_swords.jpg",
    "Восьмерка Мечей": "images/tarot_images/swords/08_eight_of_swords.jpg",
    "Девятка Мечей": "images/tarot_images/swords/09_nine_of_swords.jpg",
    "Десятка Мечей": "images/tarot_images/swords/10_ten_of_swords.jpg",
    "Паж Мечей": "images/tarot_images/swords/11_page_of_swords.jpg",
    "Рыцарь Мечей": "images/tarot_images/swords/12_knight_of_swords.jpg",
    "Королева Мечей": "images/tarot_images/swords/13_queen_of_swords.jpg",
    "Король Мечей": "images/tarot_images/swords/14_king_of_swords.jpg",
    
    # Пентакли
    "Туз Пентаклей": "images/tarot_images/pentacles/01_ace_of_pentacles.jpg",
    "Двойка Пентаклей": "images/tarot_images/pentacles/02_two_of_pentacles.jpg",
    "Тройка Пентаклей": "images/tarot_images/pentacles/03_three_of_pentacles.jpg",
    "Четверка Пентаклей": "images/tarot_images/pentacles/04_four_of_pentacles.jpg",
    "Пятерка Пентаклей": "images/tarot_images/pentacles/05_five_of_pentacles.jpg",
    "Шестерка Пентаклей": "images/tarot_images/pentacles/06_six_of_pentacles.jpg",
    "Семерка Пентаклей": "images/tarot_images/pentacles/07_seven_of_pentacles.jpg",
    "Восьмерка Пентаклей": "images/tarot_images/pentacles/08_eight_of_pentacles.jpg",
    "Девятка Пентаклей": "images/tarot_images/pentacles/09_nine_of_pentacles.jpg",
    "Десятка Пентаклей": "images/tarot_images/pentacles/10_ten_of_pentacles.jpg",
    "Паж Пентаклей": "images/tarot_images/pentacles/11_page_of_pentacles.jpg",
    "Рыцарь Пентаклей": "images/tarot_images/pentacles/12_knight_of_pentacles.jpg",
    "Королева Пентаклей": "images/tarot_images/pentacles/13_queen_of_pentacles.jpg",
    "Король Пентаклей": "images/tarot_images/pentacles/14_king_of_pentacles.jpg",
}


def get_card_image_path(card_name: str) -> str:
    """
    Получить путь к изображению карты
    
    Args:
        card_name: Название карты на русском
        
    Returns:
        Путь к файлу изображения
    """
    return CARD_TO_IMAGE_PATH.get(card_name, None)


def get_card_image_url(card_name: str, is_reversed: bool = False) -> str:
    """
    Получить URL для изображения карты
    
    Для Railway нужно использовать абсолютные пути или загрузить на GitHub
    """
    path = get_card_image_path(card_name)
    
    if not path:
        return None
    
    # Для локальной разработки
    if os.path.exists(path):
        return path
    
    # Для Railway/GitHub - используем GitHub CDN
    base_url = os.getenv("GITHUB_RAW_URL", "https://raw.githubusercontent.com")
    repo = "YOUR_USERNAME/taro_tg"  # Замените на ваш репозиторий
    return f"{base_url}/{repo}/main/{path}"

