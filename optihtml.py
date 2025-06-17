import pandas as pd
from pathlib import Path
import os

class CourseGenerator:
    def __init__(self, template_path, data_path):
        self.template_path = template_path
        self.data_path = data_path
        
    def load_template(self):
        with open(self.template_path, 'r', encoding='utf-8') as file:
            return file.read()
        
    def load_data(self):
        file_ext = Path(self.data_path).suffix.lower()
        if file_ext == '.csv':
            return pd.read_csv(self.data_path, encoding='utf-8')
        elif file_ext in ['.xlsx', '.xls']:
            return pd.read_excel(self.data_path)
        else:
            raise ValueError("Поддерживаются только CSV и Excel файлы")
    
    def process_data(self, df):
        direction = df['Направление'].dropna().iloc[0] if not df['Направление'].dropna().empty else "Направление"
        courses = []
        current_course = None
        
        for _, row in df.iterrows():
            course_name, hours, skill = row['Курс'], row['Длительность (ч)'], row['Навык']
            
            if pd.notna(course_name) and pd.notna(hours):
                try:
                    hours_float = float(str(hours).replace(',', '.')) if isinstance(hours, str) else float(hours)
                except (ValueError, TypeError):
                    continue
                
                current_course = {
                    'name': course_name,
                    'hours': hours_float,
                    'skills': [skill] if pd.notna(skill) else []
                }
                courses.append(current_course)
            elif current_course and pd.notna(skill):
                current_course['skills'].append(skill)
        
        return {
            'direction': direction,
            'total_hours': sum(c['hours'] for c in courses),
            'courses': courses
        }
    
    def generate_course_html(self, course):
        if len(course['skills']) == 1 and course['skills'][0].strip() == course['name'].strip():
            return f'''<li class="program__item"><div class="program__item-row"><span class="tag tag_blue-gray">{course['hours']} часов</span><div class="program__item-title">{course['name']}</div></div></li>'''
        
        skills_html = ''.join(f'<li>{skill}</li>' for skill in course['skills'])
        return f'''<li class="program__item program__accordion"><div class="program__accordion-button js-accordion-button"><div class="program__item-row"><span class="tag tag_blue-gray">{course['hours']} часов</span><div class="program__item-title">{course['name']}</div></div><div class="program__item-icon"><svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><path clip-rule="evenodd" d="M18.5879 9.46761C18.792 9.67198 18.9067 9.94902 18.9067 10.2379C18.9067 10.5267 18.792 10.8037 18.5879 11.0081L12.7747 16.8213C12.5703 17.0254 12.2933 17.1401 12.0044 17.1401C11.7156 17.1401 11.4386 17.0254 11.2342 16.8213L5.42101 11.0081C5.31392 10.9083 5.22803 10.788 5.16845 10.6543C5.10888 10.5206 5.07685 10.3762 5.07427 10.2299C5.07168 10.0835 5.09861 9.93818 5.15343 9.80245C5.20825 9.66673 5.28984 9.54345 5.39334 9.43994C5.49684 9.33644 5.62013 9.25485 5.75585 9.20003C5.89157 9.14521 6.03695 9.11828 6.1833 9.12087C6.32965 9.12345 6.47398 9.15548 6.60768 9.21506C6.74139 9.27463 6.86172 9.36052 6.96151 9.46761L12.0044 14.5106L17.0474 9.46761C17.2518 9.2635 17.5288 9.14885 17.8176 9.14885C18.1065 9.14885 18.3835 9.2635 18.5879 9.46761Z" fill="#3C3E41" fill-rule="evenodd"></path></svg></div></div><div class="program__accordion-content js-accordion-content"><div class="program__accordion-inner"><ul class="list">{skills_html}</ul></div></div></li>'''
    
    def replace_placeholders(self, template_content, data):
        html_content = template_content.replace(
            'Направление&quot;Яндекс Грейд&quot;',
            f'{data["direction"]} "Яндекс Грейд"'
        ).replace(
            'Сумм по столбцу &quot;Длительность (ч)&quot;',
            f'{data["total_hours"]} часов'
        )
        
        courses_html = ''.join(self.generate_course_html(course) for course in data['courses'])
        
        start_marker = '<ul class="program__list">'
        end_marker = '</ul></div></div></section>'
        start_pos = html_content.find(start_marker)
        end_pos = html_content.find(end_marker, start_pos)
        
        if start_pos == -1 or end_pos == -1:
            raise ValueError("Не найден блок с курсами в шаблоне")
        
        return (html_content[:start_pos] + 
                f'{start_marker}{courses_html}</ul></div></div></section>' +
                html_content[end_pos + len(end_marker):])
    
    def generate(self, output_path=None):
        template_content = self.load_template()
        df = self.load_data()
        data = self.process_data(df)
        final_html = self.replace_placeholders(template_content, data)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(final_html)
        
        return final_html

def process_all_csv_files(template_path, csv_folder_path, html_folder_path):
    os.makedirs(html_folder_path, exist_ok=True)
    csv_files = list(Path(csv_folder_path).glob("*.csv"))
    
    if not csv_files:
        return [], [("No CSV files found", "")]
    
    successful, failed = [], []
    
    for csv_file in csv_files:
        try:
            html_output_path = Path(html_folder_path) / f"{csv_file.stem}.html"
            generator = CourseGenerator(template_path, str(csv_file))
            generator.generate(str(html_output_path))
            successful.append(csv_file.name)
        except Exception as e:
            failed.append((csv_file.name, str(e)))
    
    return successful, failed

def generate_course_page(template_path, data_path, output_path):
    """Быстрая генерация страницы курса"""
    generator = CourseGenerator(template_path, data_path)
    return generator.generate(output_path)

# Использование
if __name__ == "__main__":
    # Одиночный файл
    # generate_course_page("html.html", "data.csv", "result.html")
    
    # Массовая обработка
    template_path = "html.html"
    csv_folder = "csv"
    html_folder = "html"
    
    print(f"Ищем CSV файлы в папке: {csv_folder}")
    print(f"Шаблон: {template_path}")
    
    successful, failed = process_all_csv_files(template_path, csv_folder, html_folder)
    
    print(f"Обработано: {len(successful)}, Ошибок: {len(failed)}")
    
    if failed:
        print("\nОшибки:")
        for filename, error in failed:
            print(f"  {filename}: {error}")
    
    if successful:
        print(f"\nУспешно обработаны:")
        for filename in successful:
            print(f"  {filename}")