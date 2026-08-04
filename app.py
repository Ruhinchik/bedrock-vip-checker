import streamlit as st
import sqlite3
from datetime import datetime

# Настройка страницы
st.set_page_config(page_title="Bedrock Player Checker", page_icon="🔍", layout="centered")

st.title("🔍 Bedrock VIP Player Checker (База Данных)")
st.write("Поиск игроков по никнейму, история заходов, IP-адреса и статистика.")

# Подключаем локальную базу данных SQLite
conn = sqlite3.connect("players_database.db", check_same_thread=False)
cursor = conn.cursor()

# Создаем таблицу, если её ещё нет
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    ip_address TEXT,
    last_server TEXT,
    visit_year TEXT
)
""")
conn.commit()

# --- ТЕСТОВЫЕ ДАННЫЕ (УДАЛИ ИЛИ ИЗМЕНИ ИХ ПОД СЕБЯ) ---
# Наполним базу парочкой примеров, чтобы ты сразу мог проверить поиск
sample_data = [
    ("Steve_Mine", "178.234.55.91", "Bedrock-Survival PE", "2024"),
    ("Alex_Gamer", "94.20.115.244", "HyperDrop Network", "2025"),
    ("Gamer_AZ_01", "85.132.66.12", "Baku_Craft_PE", "2026"),
]
for user, ip, srv, yr in sample_data:
    try:
        cursor.execute("INSERT INTO players (username, ip_address, last_server, visit_year) VALUES (?, ?, ?, ?)", (user, ip, srv, yr))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
# ----------------------------------------------------

# Меню выбора режима на сайте
action = st.radio("Выберите действие:", ["🔎 Найти игрока в базе", "➕ Добавить/Обновить игрока (Логгер)"])

# ================= РЕЖИМ 1: ПОИСК ПО НИКНЕЙМУ =================
if action == "🔎 Найти игрока в базе":
    st.subheader("🔎 Поиск информации по никнейму")
    search_name = st.text_input("Введите точный никнейм игрока для проверки:", placeholder="Например: Alex_Gamer")
    
    if st.button("🚀 НАЧАТЬ ПОИСК", use_container_width=True):
        if not search_name:
            st.error("Пожалуйста, укажите ник!")
        else:
            with st.spinner("Проверяю архивы базы данных..."):
                # Ищем игрока в нашей SQL-базе (без учета регистра букв)
                cursor.execute("SELECT ip_address, last_server, visit_year FROM players WHERE LOWER(username) = LOWER(?)", (search_name,))
                result = cursor.fetchone()
                
                if result:
                    st.balloons()
                    st.success(f"🎯 Игрок **{search_name}** найден в системе!")
                    
                    # Красиво выводим информацию в карточках
                    st.markdown("---")
                    st.markdown(f"🌐 **Последний известный IP-адрес:** `{result[0]}`")
                    st.markdown(f"🎮 **Где был замечен (Сервер):** {result[1]}")
                    st.markdown(f"📅 **Год активности:** {result[2]} год")
                else:
                    st.error(f"❌ Игрок '{search_name}' не найден в нашей базе данных. Заходов на контролируемые сервера не зафиксировано.")

# ================= РЕЖИМ 2: ДОБАВЛЕНИЕ В БАЗУ (ДЛЯ АДМИНА) =================
elif action == "➕ Добавить/Обновить игрока (Логгер)":
    st.subheader("📝 Панель ручного добавления (Имитация логгера сервера)")
    st.write("Сюда ты можешь заносить данные игроков, которых ты встретил, или настроить интеграцию с логами.")
    
    new_user = st.text_input("Никнейм игрока:")
    new_ip = st.text_input("IP-адрес:")
    new_server = st.text_input("Название сервера, где он играл:")
    current_year = str(datetime.now().year)
    
    if st.button("💾 СОХРАНИТЬ В БАЗУ ДАННЫХ", use_container_width=True):
        if not new_user or not new_ip or not new_server:
            st.error("Заполните все три поля!")
        else:
            # Записываем или обновляем данные в SQLite
            cursor.execute("""
            INSERT INTO players (username, ip_address, last_server, visit_year) 
            VALUES (?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET 
                ip_address=excluded.ip_address, 
                last_server=excluded.last_server, 
                visit_year=excluded.visit_year
            """, (new_user, new_ip, new_server, current_year))
            conn.commit()
            st.success(f"✅ Данные игрока {new_user} успешно записаны в архив базы данных!")

# Подвал
st.markdown("---")
st.write("👨‍💻 Bedrock VIP Checker | База данных игроков")
