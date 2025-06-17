import pandas as pd
import re
from pathlib import Path

class FinalCourseGenerator:
    def __init__(self, template_path, data_path):
        """
        Инициализация генератора
        
        Args:
            template_path (str): Путь к HTML шаблону
            data_path (str): Путь к CSV/Excel файлу с данными
        """
        self.template_path = template_path
        self.data_path = data_path
        self.template_content = ""
        self.courses_data = []
        
    def load_template(self):
        """Загружает HTML шаблон"""
        with open(self.template_path, 'r', encoding='utf-8') as file:
            self.template_content = file.read()
        print(f"✅ Шаблон загружен: {self.template_path}")
        
    def load_data(self):
        """Загружает данные из CSV/Excel"""
        file_extension = Path(self.data_path).suffix.lower()
        
        if file_extension == '.csv':
            df = pd.read_csv(self.data_path, encoding='utf-8')
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(self.data_path)
        else:
            raise ValueError("Поддерживаются только CSV и Excel файлы")
        
        print(f"✅ Данные загружены: {self.data_path}")
        print(f"📊 Строк: {len(df)}, Колонок: {len(df.columns)}")
        
        return df
    
    def process_data(self, df):
        """Обрабатывает данные и группирует по курсам"""
        # Получаем направление (берем первое не-null значение)
        direction = df['Направление'].dropna().iloc[0] if not df['Направление'].dropna().empty else "Направление"
        
        # Группируем курсы
        courses = []
        current_course = None
        
        for _, row in df.iterrows():
            course_name = row['Курс']
            hours = row['Длительность (ч)']
            skill = row['Навык']
            
            # Если есть название курса и часы - это новый курс
            if pd.notna(course_name) and pd.notna(hours):
                current_course = {
                    'name': course_name,
                    'hours': int(hours),
                    'skills': [skill] if pd.notna(skill) else []
                }
                courses.append(current_course)
            # Иначе это дополнительный навык для текущего курса
            elif current_course and pd.notna(skill):
                current_course['skills'].append(skill)
        
        # Считаем общую длительность
        total_hours = sum(course['hours'] for course in courses)
        
        self.courses_data = {
            'direction': direction,
            'total_hours': total_hours,
            'courses': courses
        }
        
        print(f"🎯 Направление: {direction}")
        print(f"⏱️ Общая длительность: {total_hours} часов")
        print(f"📚 Количество курсов: {len(courses)}")
        
        return self.courses_data
    
    def generate_course_html(self, course):
        """Генерирует HTML для одного курса"""
        # НОВОЕ УСЛОВИЕ: Если у курса только один навык и он совпадает с названием курса,
        # то не добавляем раскрывающийся блок
        has_dropdown = True
        if len(course['skills']) == 1 and course['skills'][0].strip() == course['name'].strip():
            has_dropdown = False
            print(f"⚠️ Курс '{course['name']}' - навык совпадает с названием, убираем раскрывашку")
        
        if has_dropdown:
            # Генерируем HTML для навыков
            skills_html = ""
            for skill in course['skills']:
                skills_html += f'<li>{skill}</li>'
            
            # Курс с раскрывающимся блоком
            course_html = f'''<li class="program__item program__accordion"><div class="program__accordion-button js-accordion-button"><div class="program__item-row"><span class="tag tag_blue-gray">{course['hours']} часов</span><div class="program__item-title">{course['name']}</div></div><div class="program__item-icon"><svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"> <path clip-rule="evenodd" d="M18.5879 9.46761C18.792 9.67198 18.9067 9.94902 18.9067 10.2379C18.9067 10.5267 18.792 10.8037 18.5879 11.0081L12.7747 16.8213C12.5703 17.0254 12.2933 17.1401 12.0044 17.1401C11.7156 17.1401 11.4386 17.0254 11.2342 16.8213L5.42101 11.0081C5.31392 10.9083 5.22803 10.788 5.16845 10.6543C5.10888 10.5206 5.07685 10.3762 5.07427 10.2299C5.07168 10.0835 5.09861 9.93818 5.15343 9.80245C5.20825 9.66673 5.28984 9.54345 5.39334 9.43994C5.49684 9.33644 5.62013 9.25485 5.75585 9.20003C5.89157 9.14521 6.03695 9.11828 6.1833 9.12087C6.32965 9.12345 6.47398 9.15548 6.60768 9.21506C6.74139 9.27463 6.86172 9.36052 6.96151 9.46761L12.0044 14.5106L17.0474 9.46761C17.2518 9.2635 17.5288 9.14885 17.8176 9.14885C18.1065 9.14885 18.3835 9.2635 18.5879 9.46761Z" fill="#3C3E41" fill-rule="evenodd"></path> </svg></div></div><div class="program__accordion-content js-accordion-content"><div class="program__accordion-inner"><ul class="list">{skills_html}</ul></div></div></li>'''
        else:
            # Курс БЕЗ раскрывающегося блока (только название и часы)
            course_html = f'''<li class="program__item"><div class="program__item-row"><span class="tag tag_blue-gray">{course['hours']} часов</span><div class="program__item-title">{course['name']}</div></div></li>'''
        
        return course_html
    
    def replace_placeholders(self):
        """Заменяет плейсхолдеры в шаблоне на реальные данные"""
        html_content = self.template_content
        
        # 1. Заменяем направление в заголовке
        html_content = html_content.replace(
            'Направление&quot;Яндекс Грейд&quot;',
            f'{self.courses_data["direction"]} "Яндекс Грейд"'
        )
        
        # 2. Заменяем общее количество часов
        html_content = html_content.replace(
            'Сумм по столбцу &quot;Длительность (ч)&quot;',
            f'{self.courses_data["total_hours"]} часов'
        )
        
        # 3. Генерируем HTML для всех курсов
        courses_html = ""
        for course in self.courses_data['courses']:
            courses_html += self.generate_course_html(course)
        
        # 4. ПОЛНАЯ замена блока курсов
        # Ищем начало блока курсов
        start_marker = '<ul class="program__list">'
        end_marker = '</ul></div></div></section>'
        
        start_pos = html_content.find(start_marker)
        if start_pos == -1:
            raise ValueError("Не найден блок с курсами в шаблоне")
        
        # Ищем конец всего блока программы обучения
        end_pos = html_content.find(end_marker, start_pos)
        if end_pos == -1:
            raise ValueError("Не найден конец блока программы обучения")
        
        # Заменяем ВЕСЬ блок от <ul class="program__list"> до </ul></div></div></section>
        new_program_block = f'{start_marker}{courses_html}</ul></div></div></section>'
        
        new_content = (
            html_content[:start_pos] +
            new_program_block +
            html_content[end_pos + len(end_marker):]
        )
        
        return new_content
    
    def generate(self, output_path=None):
        """Основной метод генерации"""
        print("🚀 Начинаем генерацию HTML...")
        
        # Загружаем шаблон
        self.load_template()
        
        # Загружаем и обрабатываем данные
        df = self.load_data()
        self.process_data(df)
        
        # Заменяем плейсхолдеры
        final_html = self.replace_placeholders()
        
        # Сохраняем результат
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(final_html)
            print(f"✅ HTML сохранен: {output_path}")
        
        return final_html
    
    def debug_template_structure(self):
        """Отладочный метод для анализа структуры шаблона"""
        self.load_template()
        
        # Ищем ключевые блоки
        program_list_start = self.template_content.find('<ul class="program__list">')
        program_list_end = self.template_content.find('</ul>', program_list_start)
        
        print("🔍 Анализ структуры шаблона:")
        print(f"Позиция <ul class=\"program__list\">: {program_list_start}")
        print(f"Позиция </ul>: {program_list_end}")
        
        if program_list_start != -1 and program_list_end != -1:
            courses_block = self.template_content[program_list_start:program_list_end + 5]
            print(f"Найденный блок курсов ({len(courses_block)} символов):")
            print(courses_block[:200] + "..." if len(courses_block) > 200 else courses_block)

# Пример использования
if __name__ == "__main__":
    # Пути к файлам
    template_file = "html.html"  # Ваш новый шаблон
    data_file = "data.csv"  # CSV файл с данными
    output_file = "perfect_result.html"  # Результат
    
    try:
        # Создаем генератор
        generator = FinalCourseGenerator(template_file, data_file)
        
        # Отладка структуры (опционально)
        print("🔍 Анализируем структуру шаблона...")
        generator.debug_template_structure()
        print()
        
        # Генерируем HTML
        result_html = generator.generate(output_file)
        
        print("\n🎉 Генерация завершена успешно!")
        print(f"📁 Результат сохранен в: {output_file}")
        print("\n📋 Что было сделано:")
        print("✅ Заменено направление в заголовке")
        print("✅ Посчитана общая сумма часов")
        print("✅ Сгенерированы все курсы с умными аккордеонами")
        print("✅ Курсы с одинаковыми названиями и навыками показаны без раскрывашки")
        print("✅ Сохранена структура нижних секций")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

# Функция для быстрого использования
def generate_perfect_course_page(template_path, data_path, output_path):
    """Быстрая генерация идеальной страницы курса"""
    generator = FinalCourseGenerator(template_path, data_path)
    return generator.generate(output_path)