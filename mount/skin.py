"""坐骑皮肤与染色系统"""
from dataclasses import dataclass, field
import time


@dataclass
class DyeScheme:
    primary: str = "#FFFFFF"
    secondary: str = "#CCCCCC"
    pattern: str = "#000000"


@dataclass
class MountSkin:
    sid: str
    name: str
    rarity: str
    source: str = ""
    stats: dict = field(default_factory=dict)
    unlocked: bool = False
    equipped: bool = False
    unlocked_at: float = 0.0       # 解锁时间戳
    available_until: float = 0.0   # 限时皮肤截止时间戳，0 表示永久


class MountSkinSystem:
    def __init__(self):
        self.skins: dict[str, MountSkin] = {}
        self.dye_schemes: dict[str, DyeScheme] = {}   # mount_id -> 当前染色方案
        self.saved_schemes: list = []                 # 服务器保存的命名方案
        self.skin_points: int = 0                     # 皮肤积分（重复解锁转化）

    def unlock_skin(self, sid: str, source: str):
        """解锁皮肤并记录来源与时间；重复解锁转化为积分补偿，不重复扣费。"""
        skin = self.skins.get(sid)
        if skin is None:
            return False
        if skin.unlocked:
            return self.handle_duplicate_unlock(sid)
        skin.unlocked = True
        skin.source = source
        skin.unlocked_at = time.time()
        return True

    def apply_dye(self, mount_id: str, scheme: DyeScheme):
        """应用多层染色方案：主色/辅色/花纹色各自独立。"""
        self.dye_schemes[mount_id] = DyeScheme(
            primary=scheme.primary,
            secondary=scheme.secondary,
            pattern=scheme.pattern,
        )

    def equip_skin(self, sid: str) -> bool:
        """装备皮肤，同时只能装备一个。"""
        skin = self.skins.get(sid)
        if skin is None or not skin.unlocked:
            return False
        for other in self.skins.values():
            other.equipped = False
        skin.equipped = True
        return True

    def unequip_skin(self, sid: str) -> bool:
        skin = self.skins.get(sid)
        if skin is None:
            return False
        skin.equipped = False
        return True

    def get_skin_stats(self, sid: str) -> dict:
        """属性仅在皮肤装备时生效。"""
        skin = self.skins.get(sid)
        if skin is not None and skin.equipped:
            return dict(skin.stats)
        return {}

    def save_scheme(self, name: str, scheme: DyeScheme):
        """将染色方案保存到服务器，支持多套命名方案，同名覆盖。"""
        entry = {
            "name": name,
            "scheme": DyeScheme(
                primary=scheme.primary,
                secondary=scheme.secondary,
                pattern=scheme.pattern,
            ),
        }
        for saved in self.saved_schemes:
            if saved["name"] == name:
                saved.update(entry)
                return
        self.saved_schemes.append(entry)

    def list_schemes(self) -> list:
        return [saved["name"] for saved in self.saved_schemes]

    def load_scheme(self, name: str):
        """读取已保存的命名方案，用于切换。"""
        for saved in self.saved_schemes:
            if saved["name"] == name:
                scheme = saved["scheme"]
                return DyeScheme(
                    primary=scheme.primary,
                    secondary=scheme.secondary,
                    pattern=scheme.pattern,
                )
        return None

    def get_acquisition_hint(self, sid: str) -> str:
        """未解锁皮肤显示稀有度与获取途径，限时皮肤额外显示剩余时间。"""
        skin = self.skins.get(sid)
        if skin is None:
            return ""
        if skin.unlocked:
            hint = f"{skin.rarity} skin owned"
        else:
            source = skin.source or "unknown"
            hint = f"{skin.rarity} skin, obtain from: {source}"
        if skin.available_until:
            remaining = skin.available_until - time.time()
            if remaining > 0:
                hint += f", limited time remaining: {int(remaining // 3600)}h"
            else:
                hint += ", limited time expired"
        return hint

    def handle_duplicate_unlock(self, sid: str) -> str:
        """重复解锁不重复扣费，自动转化为皮肤积分补偿。"""
        skin = self.skins.get(sid)
        if skin is None or not skin.unlocked:
            return "ok"
        compensation = 100
        self.skin_points += compensation
        return f"converted to {compensation} skin points"
