"""坐骑皮肤与染色系统 - 含6个bug"""
from dataclasses import dataclass, field

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

class MountSkinSystem:
    def __init__(self):
        self.skins: dict[str, MountSkin] = {}
        self.dye_schemes: dict[str, DyeScheme] = {}  # mount_id -> scheme
        self.saved_schemes: list = []  # bug4: 不保存方案

    def unlock_skin(self, sid: str, source: str):
        # bug1: 不记录来源
        if sid in self.skins:
            self.skins[sid].unlocked = True

    def apply_dye(self, mount_id: str, scheme: DyeScheme):
        # bug2: 只改主色
        self.dye_schemes[mount_id] = DyeScheme(primary=scheme.primary)

    def get_skin_stats(self, sid: str) -> dict:
        # bug3: 不装备也生效
        if sid in self.skins:
            return self.skins[sid].stats
        return {}

    def save_scheme(self, name: str, scheme: DyeScheme):
        # bug4: 不保存
        pass

    def get_acquisition_hint(self, sid: str) -> str:
        # bug5: 无获取提示
        return ""

    def handle_duplicate_unlock(self, sid: str) -> str:
        # bug6: 重复解锁无补偿
        if sid in self.skins and self.skins[sid].unlocked:
            return "already owned"
        return "ok"
