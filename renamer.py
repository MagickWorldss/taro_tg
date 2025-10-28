"""
Скрипт для переименования карт таро в нужный формат
"""
import os
from pathlib import Path

# Маппинг имен карт
CARD_MAPPING = {
    # Major Arcana
    "major/Major00.jpg": "major/00_fool.jpg",  # Дурак
    "major/Major01.jpg": "major/01_magician.jpg",  # Маг
    "major/Major02.jpg": "major/02_high_priestess.jpg",  # Жрица
    "major/Major03.jpg": "major/03_empress.jpg",  # Императрица
    "major/Major04.jpg": "major/04_emperor.jpg",  # Император
    "major/Major05.jpg": "major/05_hierophant.jpg",  # Иерофант
    "major/Major06.jpg": "major/06_lovers.jpg",  # Влюбленные
    "major/Major07.jpg": "major/07_chariot.jpg",  # Колесница
    "major/Major08.jpg": "major/08_strength.jpg",  # Сила
    "major/Major09.jpg": "major/09_hermit.jpg",  # Отшельник
    "major/Major10.jpg": "major/10_wheel_of_fortune.jpg",  # Колесо Фортуны
    "major/Major11.jpg": "major/11_justice.jpg",  # Справедливость
    "major/Major12.jpg": "major/12_hanged_man.jpg",  # Повешенный
    "major/Major13.jpg": "major/13_death.jpg",  # Смерть
    "major/Major14.jpg": "major/14_temperance.jpg",  # Умеренность
    "major/Major15.jpg": "major/15_devil.jpg",  # Дьявол
    "major/Major16.jpg": "major/16_tower.jpg",  # Башня
    "major/Major17.jpg": "major/17_star.jpg",  # Звезда
    "major/Major18.jpg": "major/18_moon.jpg",  # Луна
    "major/Major19.jpg": "major/19_sun.jpg",  # Солнце
    "major/Major20.jpg": "major/20_judgement.jpg",  # Суд
    "major/Major21.jpg": "major/21_world.jpg",  # Мир
    
    # Cups (Кубки)
    "cups/Cups01.jpg": "cups/01_ace_of_cups.jpg",  # Туз Кубков
    "cups/Cups02.jpg": "cups/02_two_of_cups.jpg",
    "cups/Cups03.jpg": "cups/03_three_of_cups.jpg",
    "cups/Cups04.jpg": "cups/04_four_of_cups.jpg",
    "cups/Cups05.jpg": "cups/05_five_of_cups.jpg",
    "cups/Cups06.jpg": "cups/06_six_of_cups.jpg",
    "cups/Cups07.jpg": "cups/07_seven_of_cups.jpg",
    "cups/Cups08.jpg": "cups/08_eight_of_cups.jpg",
    "cups/Cups09.jpg": "cups/09_nine_of_cups.jpg",
    "cups/Cups10.jpg": "cups/10_ten_of_cups.jpg",
    "cups/Cups11.jpg": "cups/11_page_of_cups.jpg",  # Паж
    "cups/Cups12.jpg": "cups/12_knight_of_cups.jpg",  # Рыцарь
    "cups/Cups13.jpg": "cups/13_queen_of_cups.jpg",  # Королева
    "cups/Cups14.jpg": "cups/14_king_of_cups.jpg",  # Король
    
    # Wands (Жезлы)
    "wands/Wands01.jpg": "wands/01_ace_of_wands.jpg",  # Туз Жезлов
    "wands/Wands02.jpg": "wands/02_two_of_wands.jpg",
    "wands/Wands03.jpg": "wands/03_three_of_wands.jpg",
    "wands/Wands04.jpg": "wands/04_four_of_wands.jpg",
    "wands/Wands05.jpg": "wands/05_five_of_wands.jpg",
    "wands/Wands06.jpg": "wands/06_six_of_wands.jpg",
    "wands/Wands07.jpg": "wands/07_seven_of_wands.jpg",
    "wands/Wands08.jpg": "wands/08_eight_of_wands.jpg",
    "wands/Wands09.jpg": "wands/09_nine_of_wands.jpg",
    "wands/Wands10.jpg": "wands/10_ten_of_wands.jpg",
    "wands/Wands11.jpg": "wands/11_page_of_wands.jpg",
    "wands/Wands12.jpg": "wands/12_knight_of_wands.jpg",
    "wands/Wands13.jpg": "wands/13_queen_of_wands.jpg",
    "wands/Wands14.jpg": "wands/14_king_of_wands.jpg",
    
    # Swords (Мечи)
    "swords/Swords01.jpg": "swords/01_ace_of_swords.jpg",
    "swords/Swords02.jpg": "swords/02_two_of_swords.jpg",
    "swords/Swords03.jpg": "swords/03_three_of_swords.jpg",
    "swords/Swords04.jpg": "swords/04_four_of_swords.jpg",
    "swords/Swords05.jpg": "swords/05_five_of_swords.jpg",
    "swords/Swords06.jpg": "swords/06_six_of_swords.jpg",
    "swords/Swords07.jpg": "swords/07_seven_of_swords.jpg",
    "swords/Swords08.jpg": "swords/08_eight_of_swords.jpg",
    "swords/Swords09.jpg": "swords/09_nine_of_swords.jpg",
    "swords/Swords10.jpg": "swords/10_ten_of_swords.jpg",
    "swords/Swords11.jpg": "swords/11_page_of_swords.jpg",
    "swords/Swords12.jpg": "swords/12_knight_of_swords.jpg",
    "swords/Swords13.jpg": "swords/13_queen_of_swords.jpg",
    "swords/Swords14.jpg": "swords/14_king_of_swords.jpg",
    
    # Pentacles (Пентакли/Монеты)
    "pentacles/Coins01.jpg": "pentacles/01_ace_of_pentacles.jpg",
    "pentacles/Coins02.jpg": "pentacles/02_two_of_pentacles.jpg",
    "pentacles/Coins03.jpg": "pentacles/03_three_of_pentacles.jpg",
    "pentacles/Coins04.jpg": "pentacles/04_four_of_pentacles.jpg",
    "pentacles/Coins05.jpg": "pentacles/05_five_of_pentacles.jpg",
    "pentacles/Coins06.jpg": "pentacles/06_six_of_pentacles.jpg",
    "pentacles/Coins07.jpg": "pentacles/07_seven_of_pentacles.jpg",
    "pentacles/Coins08.jpg": "pentacles/08_eight_of_pentacles.jpg",
    "pentacles/Coins09.jpg": "pentacles/09_nine_of_pentacles.jpg",
    "pentacles/Coins10.jpg": "pentacles/10_ten_of_pentacles.jpg",
    "pentacles/Coins11.jpg": "pentacles/11_page_of_pentacles.jpg",
    "pentacles/Coins12.jpg": "pentacles/12_knight_of_pentacles.jpg",
    "pentacles/Coins13.jpg": "pentacles/13_queen_of_pentacles.jpg",
    "pentacles/Coins14.jpg": "pentacles/14_king_of_pentacles.jpg",
}


def rename_images():
    """Переименовать карты таро"""
    base_path = Path("images/tarot_images")
    
    for old_name, new_name in CARD_MAPPING.items():
        old_path = base_path / old_name
        new_path = base_path / new_name
        
        # Создаем директорию если нужно
        new_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Переименовываем
        if old_path.exists():
            old_path.rename(new_path)
            print(f"✅ {old_name} → {new_name}")
        else:
            print(f"❌ Файл не найден: {old_name}")
    
    print("\n🎉 Переименование завершено!")


if __name__ == "__main__":
    print("🔄 Начинаю переименование карт таро...")
    rename_images()

