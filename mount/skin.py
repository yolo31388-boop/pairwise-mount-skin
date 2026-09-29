"""坐骑皮肤与染色系统"""
import time
from dataclasses import dataclass, field

# 稀有度 -> 重复解锁补偿积分
RARITY_COMPENSATION = {
    "common": 10,
    "rare": 30,
    "epic": 80,
    "legendary": 200,
}

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
    unlock_time: float = 0.0
    limited: bool = False
    expire_time: float = 0.0  # 限时皮肤到期时间戳

class MountSkinSystem:
    def __init__(self):
        self.skins: dict[str, MountSkin] = {}
        self.dye_schemes: dict[str, DyeScheme] = {}  # mount_id -> 当前方案
        self.saved_schemes: dict[str, DyeScheme] = {}  # 方案名 -> 方案（保存到服务器）
        self.skin_points: int = 0  # 皮肤积分（重复解锁补偿）
        self.equipped_sid: str = ""  # 同时只能装备一个皮肤

    # bug1: 解锁记录来源和时间
    def unlock_skin(self, sid: str, source: str):
        if sid not in self.skins:
            return "unknown skin"
        skin = self.skins[sid]
        if skin.unlocked:
            return self.handle_duplicate_unlock(sid)
        skin.unlocked = True
        skin.source = source
        skin.unlock_time = time.time()
        return "ok"

    # bug2: 染色应用全部层（主色/辅色/花纹色）
    def apply_dye(self, mount_id: str, scheme: DyeScheme):
        self.dye_schemes[mount_id] = DyeScheme(
            primary=scheme.primary,
            secondary=scheme.secondary,
            pattern=scheme.pattern,
        )

    # bug3: 属性仅装备时生效
    def get_skin_stats(self, sid: str) -> dict:
        skin = self.skins.get(sid)
        if skin and skin.unlocked and skin.equipped:
            return dict(skin.stats)
        return {}

    def equip_skin(self, sid: str) -> bool:
        skin = self.skins.get(sid)
        if not skin or not skin.unlocked:
            return False
        if self.equipped_sid and self.equipped_sid in self.skins:
            self.skins[self.equipped_sid].equipped = False
        skin.equipped = True
        self.equipped_sid = sid
        return True

    def unequip_skin(self, sid: str):
        skin = self.skins.get(sid)
        if skin and skin.equipped:
            skin.equipped = False
            if self.equipped_sid == sid:
                self.equipped_sid = ""

    # bug4: 染色方案保存到服务器，支持命名与切换
    def save_scheme(self, name: str, scheme: DyeScheme):
        self.saved_schemes[name] = DyeScheme(
            primary=scheme.primary,
            secondary=scheme.secondary,
            pattern=scheme.pattern,
        )

    def load_scheme(self, mount_id: str, name: str) -> bool:
        scheme = self.saved_schemes.get(name)
        if scheme is None:
            return False
        self.apply_dye(mount_id, scheme)
        return True

    def delete_scheme(self, name: str) -> bool:
        return self.saved_schemes.pop(name, None) is not None

    # bug5: 未解锁皮肤显示获取途径/稀有度，限时皮肤显示剩余时间
    def get_acquisition_hint(self, sid: str) -> str:
        skin = self.skins.get(sid)
        if skin is None:
            return ""
        parts = [f"[{skin.rarity}] {skin.name}"]
        if skin.unlocked:
            parts.append("已解锁")
        else:
            source = skin.source or "未知途径"
            parts.append(f"获取途径: {source}")
        if skin.limited and skin.expire_time > 0:
            remaining = max(0, int(skin.expire_time - time.time()))
            parts.append(f"剩余时间: {remaining}秒")
        return " | ".join(parts)

    # bug6: 重复解锁转化为皮肤积分补偿，不扣两次钱
    def handle_duplicate_unlock(self, sid: str) -> str:
        skin = self.skins.get(sid)
        if skin is None:
            return "unknown skin"
        if not skin.unlocked:
            return "ok"
        points = RARITY_COMPENSATION.get(skin.rarity, 10)
        self.skin_points += points
        return f"compensation: {points} skin points"
