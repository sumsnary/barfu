import pickle  # Библиотека для сохранения данных в файл
import os  # Библиотека для работы с файлами
import streamlit as st  # Библиотека для создания веб-приложений

# Имя файла, в котором будем хранить схемы
SCHEMAS_FILE = "schemas.pickle"

# 1. Функция для загрузки схем
def load_schemas():
    """
    Загружает словарь схем из pickle-файла.
    Возвращает пустой словарь, если файл не существует.
    """
    if os.path.exists(SCHEMAS_FILE):  # Проверяем, есть ли файл
        with open(SCHEMAS_FILE, "rb") as f:  # Открываем файл для чтения (rb - read binary)
            return pickle.load(f)  # Загружаем данные из файла
    else:
        return {}  # Возвращаем пустой словарь, если файла нет

# 2. Функция для сохранения схем
def save_schema(name, schema, schemas):
    """
    Сохраняет схему в существующий словарь схем.
    Обновляет или добавляет новую схему.
    Сериализует и записывает в pickle-файл.
    """
    schemas[name] = schema  # Добавляем или обновляем схему в словаре
    with open(SCHEMAS_FILE, "wb") as f:  # Открываем файл для записи (wb - write binary)
        pickle.dump(schemas, f)  # Сохраняем словарь в файл

# 3. Функция для удаления схемы (НОВОЕ!)
def delete_schema(name, schemas):
    """
    Удаляет схему по имени.
    Обрабатывает случай отсутствия схемы.
    Сохраняет обновленный список схем.
    """
    if name in schemas:  # Проверяем, есть ли схема с таким именем
        del schemas[name]  # Удаляем схему из словаря
        with open(SCHEMAS_FILE, "wb") as f:
            pickle.dump(schemas, f)  # Сохраняем обновленный словарь
        st.success(f"Схема '{name}' успешно удалена!")
    else:
        st.error(f"Схема '{name}' не найдена.")

# 4. Функция для слияния схем (НОВОЕ!)
def merge_schemas(files, schemas):
     """
    Объединяет схемы из нескольких файлов.
    Разрешает конфликты при совпадении имен.
    Опциональное переименование конфликтных схем.
    Сохранение объединенных схем.
    """
     merged_schemas = schemas.copy()  # Копируем существующие схемы

     for uploaded_file in files:
         try:
            loaded_data = pickle.load(uploaded_file)
            if not isinstance(loaded_data, dict):
               st.error(f"Файл '{uploaded_file.name}' не содержит словарь схем.")
               continue

            for name, schema in loaded_data.items():
                 if name in merged_schemas:
                    new_name = st.text_input(f"Конфликт имени '{name}'. Введите новое имя:", value=f"{name}_merged")
                    if new_name:
                        merged_schemas[new_name] = schema
                    else:
                        st.error(f"Необходимо ввести новое имя для '{name}'.")
                        continue
                 else:
                     merged_schemas[name] = schema

         except Exception as e:
            st.error(f"Ошибка при загрузке файла '{uploaded_file.name}': {e}")
            continue

     with open(SCHEMAS_FILE, "wb") as f:
          pickle.dump(merged_schemas, f)

     st.success("Схемы успешно объединены!")

# 5. Streamlit-приложение
def main():
    st.title("Редактор Barfi-схем")
    schemas = load_schemas() # Загружаем схемы при запуске приложения

    # Sidebar для навигации
    menu = st.sidebar.radio("Меню", [
        "Создание схемы",
        "Список схем",
        "Просмотр схемы",
        "Удаление схемы",
        "Слияние схем"
    ])

    if menu == "Создание схемы":
        st.header("Создание схемы")
        name = st.text_input("Название схемы")
        schema_data = st.text_area("Данные схемы")
        if st.button("Сохранить"):
            try:
               #Преобразование введенного текста в словарь
               schema = eval(schema_data)
               save_schema(name, schema, schemas)
               st.success(f"Схема '{name}' успешно сохранена!")
            except Exception as e:
                st.error(f"Ошибка при сохранении схемы: {e}. Проверьте правильность ввода данных.")

    elif menu == "Список схем":
        st.header("Список схем")
        if schemas:
            for name, schema in schemas.items():
                st.write(f"**{name}**")
        else:
            st.write("Нет сохраненных схем.")

    elif menu == "Просмотр схемы":
        st.header("Просмотр схемы")
        if schemas:
            selected_name = st.selectbox("Выберите схему для просмотра:", list(schemas.keys()))
            if selected_name:
              st.write(schemas[selected_name])
        else:
            st.write("Нет сохраненных схем для просмотра.")

    elif menu == "Удаление схемы":
        st.header("Удаление схемы")
        if schemas:
             name_to_delete = st.selectbox("Выберите схему для удаления:", list(schemas.keys()))
             if st.button("Удалить"):
                delete_schema(name_to_delete, schemas)
                schemas = load_schemas()
        else:
            st.write("Нет сохраненных схем для удаления.")

    elif menu == "Слияние схем":
        st.header("Слияние схем")
        uploaded_files = st.file_uploader("Загрузите файлы со схемами", accept_multiple_files=True)
        if uploaded_files:
            if st.button("Объединить схемы"):
                 merge_schemas(uploaded_files, schemas)
                 schemas = load_schemas()

if __name__ == "__main__":
    main()
