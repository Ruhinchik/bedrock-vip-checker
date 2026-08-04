import streamlit as st
import sqlite3
import requests
from datetime import datetime

# Настройка страницы
st.set_page_config(page_title="Bedrock & Xbox Чекер", page_icon="🔍", layout="centered")

st.title("🔍 Bedrock & Xbox VIP Чекер v3.0")
st.write("Автоматический поиск игроков по официальным базам Microsoft Xbox Live и локальным архивам!")

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
action = st.radio("Выберите действие:", ["🔎 Умный Авто-Поиск игрока Bedrock", "➕ Добавить IP/Логи вручную"])

# ================= РЕЖИМ 1: УМНЫЙ АВТО-ПОИСК С ПОДДЕРЖКОЙ BEDROCK =================
if action == "🔎 Умный Авто-Поиск игрока Bedrock":
    st.subheader("🌐 Глобальный пробив Microsoft & Xbox Live")
    search_name = st.text_input("Введите точный никнейм игрока Bedrock:", placeholder="Например: Steve")
    
    if st.button("🚀 НАЧАТЬ АВТО-ПОИСК", use_container_width=True):
        if not search_name:
            st.error("Пожалуйста, укажите никнейм!")
        else:
            # 1. ШАГ: Автоматический запрос к официальной базе Microsoft Xbox Live (Bedrock)
            with st.spinner("📡 Пробиваю никнейм по базам Microsoft Xbox Live..."):
                try:
                    # Используем специальный эндпоинт для Bedrock Edition
                    response = requests.get(f"https://playerdb.co{search_name}", timeout=8)
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        if res_data.get("success") == True:
                            st.balloons()
                            st.success(f"🎯 Игрок **{search_name}** найден в глобальной сети Microsoft!")
                            
                            player_info = res_data["data"]["player"]
                            
                            # Выводим аватарку скина, которую сайт нашел САМ
                            avatar_url = player_info.get("avatar", f"https://minotar.net{search_name}/100.png")
                            st.image(avatar_url, width=100, caption="Официальный аватар игрока")
                            
                            st.markdown("---")
                            st.write("### 📋 Данные аккаунта Microsoft:")
                            st.write(f"🎮 **Официальный ник (GamerTag):** `{player_info.get('username')}`")
                            st.write(f"🆔 **Секретный вечный ID (XUID):** `{player_info.get('id')}`")
                            st.write(f"🌍 **Тип аккаунта:** `Microsoft Bedrock (PE / Xbox / Windows)`")
                        else:
                            st.warning("ℹ️ Игрок с таким никнеймом не зарегистрирован в официальной системе Xbox Live.")
                    else:
                        st.warning("ℹ️ Игрок не найден в глобальной базе Microsoft. Проверьте правильность написания ника (большие и маленькие буквы).")
                
                except Exception as e:
                    st.warning("⚠️ Глобальные сервера Microsoft заняты. Перехожу к поиску по локальным логам...")

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
st.write("👨‍💻 Bedrock & Xbox VIP Checker v3.0 | Полный пробив Microsoft")
