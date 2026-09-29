"""坐骑皮肤与染色系统 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mount.skin import MountSkinSystem, MountSkin, DyeScheme

class TestSkinSource:
    def test_unlock_records_source(self):
        mss = MountSkinSystem()
        mss.skins["s1"] = MountSkin("s1", "fire", "legendary")
        mss.unlock_skin("s1", "cash_shop")
        assert mss.skins["s1"].source == "cash_shop"  # bug1: 空

class TestDyeLayers:
    def test_dye_applies_all_layers(self):
        mss = MountSkinSystem()
        scheme = DyeScheme(primary="#FF0000", secondary="#00FF00", pattern="#0000FF")
        mss.apply_dye("m1", scheme)
        applied = mss.dye_schemes["m1"]
        assert applied.secondary == "#00FF00"  # bug2: 还是默认
        assert applied.pattern == "#0000FF"

class TestStatsRequireEquip:
    def test_unequipped_skin_no_stats(self):
        mss = MountSkinSystem()
        mss.skins["s1"] = MountSkin("s1", "fire", "legendary", stats={"speed": 10}, equipped=False)
        stats = mss.get_skin_stats("s1")
        assert stats == {}  # bug3: 返回speed:10

class TestSaveScheme:
    def test_dye_schemes_saved(self):
        mss = MountSkinSystem()
        scheme = DyeScheme(primary="#FF0000")
        mss.save_scheme("red", scheme)
        assert len(mss.saved_schemes) > 0  # bug4: 0

class TestAcquisitionHint:
    def test_locked_skin_has_hint(self):
        mss = MountSkinSystem()
        mss.skins["s1"] = MountSkin("s1", "fire", "legendary", source="world_boss")
        hint = mss.get_acquisition_hint("s1")
        assert hint != ""  # bug5: 空

class TestDuplicateCompensation:
    def test_duplicate_unlock_gives_compensation(self):
        mss = MountSkinSystem()
        mss.skins["s1"] = MountSkin("s1", "fire", "legendary", unlocked=True)
        result = mss.handle_duplicate_unlock("s1")
        assert result != "already owned"  # bug6: 无补偿
        assert "compensation" in result or "points" in result
