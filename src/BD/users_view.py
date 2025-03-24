import asyncio
import aiosqlite

DB_PATH = "/root/company_new_server/src/BD/users.db"


async def view_all_users(db):
    cursor = await db.execute("SELECT user_id, user_name, is_excluded FROM users")
    rows = await cursor.fetchall()
    if not rows:
        print("База данных пуста.")
        return
    print(f"{'User ID':<15} {'User Name':<20} {'Is Excluded':<10}")
    print("-" * 45)
    for row in rows:
        print(f"{row[0]:<15} {row[1]:<20} {'Yes' if row[2] else 'No':<10}")
    print("-" * 45)


async def view_database():
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            while True:
                print("\nКоманды:")
                print("1. Показать всех пользователей")
                print("2. Показать только доступных пользователей")
                print("3. Выход")
                choice = input("Выберите действие (1-3): ")

                if choice == "1":
                    await view_all_users(db)
                elif choice == "2":
                    cursor = await db.execute(
                        "SELECT user_id, user_name FROM users WHERE is_excluded = 0"
                    )
                    rows = await cursor.fetchall()
                    if not rows:
                        print("Нет доступных пользователей.")
                    else:
                        print(f"{'User ID':<15} {'User Name':<20}")
                        print("-" * 35)
                        for row in rows:
                            print(f"{row[0]:<15} {row[1]:<20}")
                        print("-" * 35)
                elif choice == "3":
                    print("Выход.")
                    break
                else:
                    print("Неверный выбор, попробуйте снова.")

    except aiosqlite.Error as e:
        print(f"Ошибка при подключении к базе данных: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(view_database())
