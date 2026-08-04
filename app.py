import streamlit as st
import sqlite3
import requests
from datetime import datetime

# Настройка страницы
st.set_page_config(page_title="Bedrock Авто-Чекер", page_icon="🔍", layout="centered")

st.title("🔍 Bedrock VIP Player Checker v2.0")
st.write("Автоматический поиск игроков по базам данных Microsoft и локальным архивам серверов!")

# Инициализируем локальную базу для IP-адресов
conn = sqlite3.connect("players_database.db", check_same_thread=False)
cursor = conn.cursor()
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

# Меню выбора режима
action = st.radio("Выберите действие:", ["🔎 Умный Авто-Поиск игрока", "➕ Добавить IP/Логи вручную"])

# ================= РЕЖИМ 1: УМНЫЙ АВТО-ПОИСК =================
if action == "🔎 Умный Авто-Поиск игрока":
    st.subheader("🌐 Автоматический пробив по базам данных")
    search_name = st.text_input("Введите никнейм игрока для авто-поиска:", placeholder="Например: Steve")
    
    if st.button("🚀 НАЧАТЬ АВТО-ПОИСК", use_container_width=True):
        if not search_name:
            st.error("Пожалуйста, укажите никнейм!")
        else:
            # 1. ШАГ: Автоматический запрос к серверам Minecraft/Microsoft в реальном времени
            with st.spinner("📡 Подключаюсь к базам данных Mojang/Microsoft..."):
                try:
                    # Делаем запрос к открытому API профилей
                    response = requests.get(f"https://ashcon.app{search_name}", timeout=8)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.balloons()
                        st.success(f"🎯 Игрок **{search_name}** успешно найден в глобальной сети!")
                        
                        # Вытаскиваем официальные данные
                        uuid = data.get("uuid", "Неизвестно")
                        created_at = data.get("created_at", "Давно")
                        
                        # Показываем аватарку скина, которую сайт нашел САМ
                        st.image(f"https://minotar.net{search_name}/100.png", width=100, caption="Текущий скин")
                        
                        st.markdown("---")
                        st.write("### 📋 Глобальные данные аккаунта:")
                        st.write(f"🆔 **Уникальный UUID (Защищенный ID):** `{uuid}`")
                        
                        # Показываем историю прошлых никнеймов, если они есть
                        if "username_history" in data:
                            st.write("📝 **История прошлых никнеймов (как шифровался):**")
                            for old_name in data["username_history"]:
                                st.write(f"• {old_name.get('username')}")
                    else:
                        st.warning("ℹ️ Глобальный лицензионный аккаунт не найден (возможно, это пиратский ник или мобильный Bedrock-аккаунт без привязки к Java).")
                
                except Exception:
                    st.warning("⚠️ Глобальные сервера заняты. Перехожу к поиску по локальным логам...")

            # 2. ШАГ: Поиск по твоей личной базе данных (IP-адреса и сервера)
            with st.spinner("🔎 Проверяю локальные архивы серверов..."):
                cursor.execute("SELECT ip_address, last_server, visit_year FROM players WHERE LOWER(username) = LOWER(?)", (search_name,))
                local_result = cursor.fetchone()
                
                if local_result:
                    st.info("🚨 Найдено совпадение в локальной базе данных нарушителей!")
                    st.markdown(f"🌐 **Скрытый IP-адрес:** `{local_result[0]}`")
                    st.markdown(f"🎮 **Где играл:** {local_result[1]}")
                    st.markdown(f"📅 **Год фиксации:** {local_result[2]} год")
                else:
                    st.error(f"❌ В твоих личных логах IP-адрес для '{search_name}' пока не зарегистрирован.")

# ================= РЕЖИМ 2: ДОБАВЛЕНИЕ В БАЗУ ДАННЫХ =================
elif action == "➕ Добавить IP/Логи вручную":
    st.subheader("📝 Панель ручного добавления логов")
    new_user = st.text_input("Никнейм игрока:")
    new_ip = st.text_input("IP-адрес:")
    new_server = st.text_input("Название сервера:")
    current_year = str(datetime.now().year)
    
    if st.button("💾 СОХРАНИТЬ В АРХИВ", use_container_width=True):
        if not new_user or not new_ip or not new_server:
            st.error("Заполните все поля!")
        else:
            cursor.execute("""
            INSERT INTO players (username, ip_address, last_server, visit_year) 
            VALUES (?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET ip_address=excluded.ip_address, last_server=excluded.last_server, visit_year=excluded.visit_year
            """, (new_user, new_ip, new_server, current_year))
            conn.commit()
            st.success(f"✅ Игрок {new_user} занесен в базу данных пробива!")

# Подвал
st.markdown("---")
st.write("👨‍💻 Bedrock VIP Checker v2.0 | Глобальный авто-поиск")
