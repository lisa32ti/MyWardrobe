import os
import sqlite3
from typing import Optional

from constants import DB_PATH


class DatabaseManager:

    def __init__(self, db_path: str = DB_PATH) -> None:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self._create_tables()
        self._seed_if_empty()

    def _create_tables(self) -> None:
        cursor = self.connection.cursor()
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS clothes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                color TEXT NOT NULL,
                season TEXT NOT NULL,
                image TEXT,
                favorite INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS outfits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                favorite INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS outfit_clothes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                outfit_id INTEGER NOT NULL,
                clothes_id INTEGER NOT NULL,
                FOREIGN KEY (outfit_id) REFERENCES outfits(id) ON DELETE CASCADE,
                FOREIGN KEY (clothes_id) REFERENCES clothes(id) ON DELETE CASCADE
            );
            """
        )
        self.connection.commit()

    def _seed_if_empty(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM clothes")
        if cursor.fetchone()[0] > 0:
            return

        demo = [
            ("Джинсовая куртка", "Верхняя одежда", "Синий", "Осень"),
            ("Белая футболка", "Футболки и топы", "Белый", "Лето"),
            ("Чёрные джинсы", "Брюки и джинсы", "Чёрный", "Всесезон"),
            ("Кроссовки", "Обувь", "Белый", "Всесезон"),
            ("Сумка", "Аксессуары", "Бежевый", "Всесезон"),
        ]
        cursor.executemany(
            "INSERT INTO clothes (name, category, color, season) VALUES (?, ?, ?, ?)",
            demo,
        )
        self.connection.commit()

    def add_clothes(self, name: str, category: str, color: str,
                    season: str, image: str = "") -> int:
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO clothes (name, category, color, season, image) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, category, color, season, image),
        )
        self.connection.commit()
        return cursor.lastrowid

    def update_clothes(self, clothes_id: int, name: str, category: str,
                       color: str, season: str, image: str) -> None:
        self.connection.execute(
            "UPDATE clothes SET name=?, category=?, color=?, season=?, image=? "
            "WHERE id=?",
            (name, category, color, season, image, clothes_id),
        )
        self.connection.commit()

    def delete_clothes(self, clothes_id: int) -> None:
        self.connection.execute("DELETE FROM clothes WHERE id=?", (clothes_id,))
        self.connection.commit()

    def get_clothes(self, clothes_id: int) -> Optional[sqlite3.Row]:
        cursor = self.connection.execute(
            "SELECT * FROM clothes WHERE id=?", (clothes_id,)
        )
        return cursor.fetchone()

    def get_all_clothes(self) -> list[sqlite3.Row]:
        cursor = self.connection.execute(
            "SELECT * FROM clothes ORDER BY created_at DESC"
        )
        return cursor.fetchall()

    def search_clothes(self, query: str = "", category: str = "") -> list[sqlite3.Row]:
        sql = "SELECT * FROM clothes WHERE 1=1"
        params: list = []
        if query:
            sql += " AND name LIKE ?"
            params.append(f"%{query}%")
        if category:
            sql += " AND category = ?"
            params.append(category)
        sql += " ORDER BY created_at DESC"
        return self.connection.execute(sql, params).fetchall()

    def toggle_clothes_favorite(self, clothes_id: int) -> None:
        self.connection.execute(
            "UPDATE clothes SET favorite = 1 - favorite WHERE id=?", (clothes_id,)
        )
        self.connection.commit()

    def get_favorite_clothes(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            "SELECT * FROM clothes WHERE favorite=1 ORDER BY created_at DESC"
        ).fetchall()

    def add_outfit(self, name: str, description: str,
                   clothes_ids: list[int]) -> int:
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO outfits (name, description) VALUES (?, ?)",
            (name, description),
        )
        outfit_id = cursor.lastrowid
        cursor.executemany(
            "INSERT INTO outfit_clothes (outfit_id, clothes_id) VALUES (?, ?)",
            [(outfit_id, cid) for cid in clothes_ids],
        )
        self.connection.commit()
        return outfit_id

    def delete_outfit(self, outfit_id: int) -> None:
        self.connection.execute("DELETE FROM outfits WHERE id=?", (outfit_id,))
        self.connection.commit()

    def get_all_outfits(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            "SELECT * FROM outfits ORDER BY created_at DESC"
        ).fetchall()

    def get_outfit(self, outfit_id: int) -> Optional[sqlite3.Row]:
        return self.connection.execute(
            "SELECT * FROM outfits WHERE id=?", (outfit_id,)
        ).fetchone()

    def get_outfit_clothes(self, outfit_id: int) -> list[sqlite3.Row]:
        return self.connection.execute(
            "SELECT c.* FROM clothes c "
            "JOIN outfit_clothes oc ON oc.clothes_id = c.id "
            "WHERE oc.outfit_id = ?",
            (outfit_id,),
        ).fetchall()

    def toggle_outfit_favorite(self, outfit_id: int) -> None:
        self.connection.execute(
            "UPDATE outfits SET favorite = 1 - favorite WHERE id=?", (outfit_id,)
        )
        self.connection.commit()

    def get_random_outfit(self) -> Optional[sqlite3.Row]:
        return self.connection.execute(
            "SELECT * FROM outfits ORDER BY RANDOM() LIMIT 1"
        ).fetchone()

    def get_count_by_category(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            "SELECT category, COUNT(*) AS cnt FROM clothes "
            "GROUP BY category ORDER BY cnt DESC"
        ).fetchall()

    def get_count_by_season(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            "SELECT season, COUNT(*) AS cnt FROM clothes "
            "GROUP BY season ORDER BY cnt DESC"
        ).fetchall()

    def get_count_by_color(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            "SELECT color, COUNT(*) AS cnt FROM clothes "
            "GROUP BY color ORDER BY cnt DESC"
        ).fetchall()

    def get_total_counts(self) -> tuple[int, int]:
        clothes = self.connection.execute("SELECT COUNT(*) FROM clothes").fetchone()[0]
        outfits = self.connection.execute("SELECT COUNT(*) FROM outfits").fetchone()[0]
        return clothes, outfits

    def close(self) -> None:
        self.connection.close()