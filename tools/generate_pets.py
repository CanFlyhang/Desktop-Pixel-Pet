import json
import os

def grid_to_pixels(grid_str, char_map, width=32, height=32):
    """
    将 ASCII 网格转换为像素名称矩阵
    - 支持水平/垂直居中填充到 32x32
    - 网格字符由 char_map 映射到调色板键名
    """
    lines = [line.rstrip("\n") for line in grid_str.strip().split("\n") if line]
    lines = lines[:height]
    top_pad = (height - len(lines)) // 2
    out = []
    for _ in range(top_pad):
        out.append(["bg"] * width)
    for line in lines:
        left_pad = (width - len(line)) // 2
        row = ["bg"] * left_pad
        for ch in line:
            row.append(char_map.get(ch, "bg"))
        while len(row) < width:
            row.append("bg")
        out.append(row[:width])
    while len(out) < height:
        out.append(["bg"] * width)
    return out

def save_pet(filename, data):
    """
    保存单个宠物资源 JSON 到 assets/pets 目录
    """
    path = os.path.join("assets", "pets", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Generated {path}")

def upsert_pet_config(pets_cfg_path, items):
    """
    将多款宠物写入 data/pets.json 配置
    items: [{name, description, frames, price, unlock_type}]
    """
    if os.path.exists(pets_cfg_path):
        with open(pets_cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {}
    for it in items:
        entry = {
            "price": it.get("price", 0),
            "description": it.get("description", ""),
            "pixel_size": "32x32",
            "frames": it["frames"],
        }
        if it.get("unlock_type"):
            entry["unlock_type"] = it["unlock_type"]
        cfg[it["name"]] = entry
    with open(pets_cfg_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    print(f"Updated {pets_cfg_path}")

def make_pet(filename, palette, char_map, f1, f2, frame_names=("idle1","idle2")):
    """
    生成单宠物资源数据结构
    - filename: 输出文件名
    - palette: 调色板字典，RGBA 列表
    - char_map: 字符映射到调色板键
    - f1, f2: 两帧 ASCII 网格字符串
    """
    return {
        "size": [32, 32],
        "palette": palette,
        "frames": [
            {"name": frame_names[0], "pixels": grid_to_pixels(f1, char_map)},
            {"name": frame_names[1], "pixels": grid_to_pixels(f2, char_map)},
        ],
    }

def main():
    """
    批量生成 16 款潮流像素桌宠资源并更新 pets.json
    """
    pets_cfg_path = os.path.join("data", "pets.json")

    base_map = {
        " ": "bg",
        "P": "primary",
        "S": "secondary",
        "A": "accent",
        "E": "eye",
        "O": "outline",
        "H": "highlight",
    }

    items_meta = []

    def save(name, slug, palette, f1, f2, price=1800, desc="", unlock_type=None):
        data = make_pet(f"pixel_{slug}.json", palette, base_map, f1, f2)
        save_pet(f"pixel_{slug}.json", data)
        items_meta.append({
            "name": name,
            "description": desc,
            "frames": os.path.join("assets", "pets", f"pixel_{slug}.json"),
            "price": price,
            "unlock_type": unlock_type,
        })

    # 1 霓虹小狐狸
    palette_neon_fox = {
        "bg": [0,0,0,0],
        "primary": [255, 64, 129, 255],
        "secondary": [124, 77, 255, 255],
        "accent": [3, 218, 198, 255],
        "eye": [0,0,0,255],
        "outline": [40, 40, 40, 255],
        "highlight": [255, 255, 255, 255],
    }
    fox_f1 = """
          OOOOOOO
         OPPPPPPPO
        OPPHPPPPEO
        OPPPPPPPEO
        OPPSSPPPAO
         OPPPPPAO
          OOOOEO
    """
    fox_f2 = """
          OOOOOOO
         OPPPPPPPO
        OPPPPHPEEO
        OPPPPPPPEO
        OPPSSPPPAO
         OPPPPPAO
          OOOOEO
    """
    save("霓虹小狐狸","neon_fox",palette_neon_fox,fox_f1,fox_f2,price=2400,desc="霓虹渐变与赛博光晕的俏皮狐狸")

    # 2 赛博小猫
    palette_cyber_cat = {
        "bg": [0,0,0,0],
        "primary": [0, 229, 255, 255],
        "secondary": [255, 0, 255, 255],
        "accent": [0, 200, 83, 255],
        "eye": [0,0,0,255],
        "outline": [35,35,35,255],
        "highlight": [255,255,255,255],
    }
    cat_f1 = """
        OOO   OOO
        OPPPPPPOO
        OPEEPEPOO
        OPPPPPPPO
        OPSSPPAPO
         OPPPPO
    """
    cat_f2 = """
        OOO   OOO
        OPPPPPPOO
        OPEHPEPOO
        OPPPPPPPO
        OPSSPPAPO
         OPPPPO
    """
    save("赛博小猫","cyber_cat",palette_cyber_cat,cat_f1,cat_f2,price=2400,desc="高饱和赛博配色与猫耳闪光")

    # 3 樱桃小兔
    palette_cherry_bunny = {
        "bg": [0,0,0,0],
        "primary": [255, 128, 171, 255],
        "secondary": [255, 205, 210, 255],
        "accent": [244, 67, 54, 255],
        "eye": [62,39,35,255],
        "outline": [80, 80, 80, 255],
        "highlight": [255,255,255,255],
    }
    bun_f1 = """
        OOO  OOO
         OPPPO
        OPPPPPO
        OPEEEPO
        OPSSPPO
         OPPPO
    """
    bun_f2 = """
        OOO  OOO
         OPPPO
        OPPPPPO
        OPEH EPO
        OPSSPPO
         OPPPO
    """
    save("樱桃小兔","cherry_bunny",palette_cherry_bunny,bun_f1,bun_f2,price=1800,desc="樱粉配色与圆润可爱造型")

    # 4 抹茶小熊
    palette_matcha_bear = {
        "bg": [0,0,0,0],
        "primary": [165, 214, 167, 255],
        "secondary": [129, 199, 132, 255],
        "accent": [56, 142, 60, 255],
        "eye": [27,94,32,255],
        "outline": [60,60,60,255],
        "highlight": [255,255,255,255],
    }
    bear_f1 = """
        OOO   OOO
         OPPPPPO
        OPPSEPPO
        OPPPPPPO
         OPSAPO
          OPPO
    """
    bear_f2 = """
        OOO   OOO
         OPPPPPO
        OPPHEPPO
        OPPPPPPO
         OPSAPO
          OPPO
    """
    save("抹茶小熊","matcha_bear",palette_matcha_bear,bear_f1,bear_f2,price=2000,desc="清新抹茶与软糯体型")

    # 5 冰蓝企鹅
    palette_ice_penguin = {
        "bg": [0,0,0,0],
        "primary": [144, 202, 249, 255],
        "secondary": [227, 242, 253, 255],
        "accent": [100, 181, 246, 255],
        "eye": [13,71,161,255],
        "outline": [70,70,70,255],
        "highlight": [255,255,255,255],
    }
    pen_f1 = """
         OPPPPPO
        OPEESEPO
        OPPPPPPO
        OPSAAPOO
         OPPPPO
    """
    pen_f2 = """
         OPPPPPO
        OPEHSEPO
        OPPPPPPO
        OPSAAPOO
         OPPPPO
    """
    save("冰蓝企鹅","ice_penguin",palette_ice_penguin,pen_f1,pen_f2,price=2200,desc="冰蓝渐变与圆滚造型")

    # 6 彩虹独角兽（密钥）
    palette_rainbow_unicorn = {
        "bg": [0,0,0,0],
        "primary": [255, 255, 255, 255],
        "secondary": [255, 171, 64, 255],
        "accent": [126, 87, 194, 255],
        "eye": [0,0,0,255],
        "outline": [90,90,90,255],
        "highlight": [255, 64, 129, 255],
    }
    uni_f1 = """
        OOOOP
        OPPPPP
        OPEEPP
        OPASPP
         OPPP
    """
    uni_f2 = """
        OOOOP
        OPPPPP
        OPEHPP
        OPASPP
         OPPP
    """
    save("彩虹独角兽","rainbow_unicorn",palette_rainbow_unicorn,uni_f1,uni_f2,price=0,desc="白金身躯与彩虹角，限密钥解锁",unlock_type="key")

    # 7 泡泡史莱姆
    palette_slime = {
        "bg": [0,0,0,0],
        "primary": [128, 222, 234, 255],
        "secondary": [178, 235, 242, 255],
        "accent": [0, 184, 212, 255],
        "eye": [0,0,0,255],
        "outline": [50,50,50,255],
        "highlight": [255,255,255,255],
    }
    sli_f1 = """
        OPPPPP
        OPSEAP
        OPPPPP
         OOOO
    """
    sli_f2 = """
        OPPPPP
        OPHEAP
        OPPPPP
         OOOO
    """
    save("泡泡史莱姆","bubble_slime",palette_slime,sli_f1,sli_f2,price=1500,desc="半透明果冻感与水光高光")

    # 8 软萌水豚
    palette_capy = {
        "bg": [0,0,0,0],
        "primary": [198, 160, 135, 255],
        "secondary": [160, 120, 90, 255],
        "accent": [121, 85, 72, 255],
        "eye": [62,39,35,255],
        "outline": [70,70,70,255],
        "highlight": [255,255,255,255],
    }
    capy_f1 = """
        OPPPPPO
        OPEEEPO
        OPPSSPO
         OPPPO
    """
    capy_f2 = """
        OPPPPPO
        OPEH EPO
        OPPSSPO
         OPPPO
    """
    save("软萌水豚","capybara",palette_capy,capy_f1,capy_f2,price=2400,desc="治愈系软糯水豚")

    # 9 草莓奶牛
    palette_straw_cow = {
        "bg": [0,0,0,0],
        "primary": [255, 204, 188, 255],
        "secondary": [255, 129, 170, 255],
        "accent": [255, 87, 34, 255],
        "eye": [0,0,0,255],
        "outline": [80,80,80,255],
        "highlight": [255,255,255,255],
    }
    cow_f1 = """
        OPPPPPO
        OPEEPEO
        OPSAPPO
         OPPPO
    """
    cow_f2 = """
        OPPPPPO
        OPEHPEO
        OPSAPPO
         OPPPO
    """
    save("草莓奶牛","strawberry_cow",palette_straw_cow,cow_f1,cow_f2,price=2100,desc="甜甜草莓斑点奶牛")

    # 10 幸运锦鲤
    palette_koi = {
        "bg": [0,0,0,0],
        "primary": [255, 224, 178, 255],
        "secondary": [255, 112, 67, 255],
        "accent": [255, 171, 64, 255],
        "eye": [66,66,66,255],
        "outline": [90,90,90,255],
        "highlight": [255,255,255,255],
    }
    koi_f1 = """
        OPPPP
        OPSAP
        OPPPP
        OOOO 
    """
    koi_f2 = """
        OPPPP
        OPHAP
        OPPPP
        OOOO 
    """
    save("幸运锦鲤","lucky_koi",palette_koi,koi_f1,koi_f2,price=1800,desc="橘白锦鲤寓意好运")

    # 11 元气小鸭
    palette_duck = {
        "bg": [0,0,0,0],
        "primary": [255, 241, 118, 255],
        "secondary": [255, 183, 77, 255],
        "accent": [255, 111, 0, 255],
        "eye": [0,0,0,255],
        "outline": [90,90,90,255],
        "highlight": [255,255,255,255],
    }
    duck_f1 = """
        OPPPP
        OPEEP
        OPSAP
         OPP
    """
    duck_f2 = """
        OPPPP
        OPHEP
        OPSAP
         OPP
    """
    save("元气小鸭","energetic_duck",palette_duck,duck_f1,duck_f2,price=1600,desc="亮黄嘴橙的元气萌鸭")

    # 12 星河小龙（密钥）
    palette_star_dragon = {
        "bg": [0,0,0,0],
        "primary": [121, 134, 203, 255],
        "secondary": [26, 35, 126, 255],
        "accent": [179, 157, 219, 255],
        "eye": [255,255,255,255],
        "outline": [70,70,100,255],
        "highlight": [255, 255, 255, 255],
    }
    sdrag_f1 = """
        OPPPPPO
        OPEE PPO
        OPPSSPO
         OPA PO
          OOOO
    """
    sdrag_f2 = """
        OPPPPPO
        OPEH PPO
        OPPSSPO
         OPA PO
          OOOO
    """
    save("星河小龙","star_dragon",palette_star_dragon,sdrag_f1,sdrag_f2,price=0,desc="深蓝银河鳞片，限密钥解锁",unlock_type="key")

    # 13 复古机器人
    palette_robot = {
        "bg": [0,0,0,0],
        "primary": [189, 189, 189, 255],
        "secondary": [120, 144, 156, 255],
        "accent": [0, 230, 118, 255],
        "eye": [33,33,33,255],
        "outline": [97,97,97,255],
        "highlight": [255,255,255,255],
    }
    rob_f1 = """
        OPPPPPO
        OPEE EPO
        OPSSAPO
         OPPPO
    """
    rob_f2 = """
        OPPPPPO
        OPEH EPO
        OPSSAPO
         OPPPO
    """
    save("复古机器人","retro_robot",palette_robot,rob_f1,rob_f2,price=2000,desc="复古金属与绿灯显示屏")

    # 14 像素仙人掌
    palette_cactus = {
        "bg": [0,0,0,0],
        "primary": [174, 213, 129, 255],
        "secondary": [139, 195, 74, 255],
        "accent": [76, 175, 80, 255],
        "eye": [0,0,0,255],
        "outline": [85, 139, 47, 255],
        "highlight": [255,255,255,255],
    }
    cac_f1 = """
        OOPPPPO
        OPPSSPO
        OPEEEPO
         OPPPO
    """
    cac_f2 = """
        OOPPPPO
        OPPSSPO
        OPEH EPO
         OPPPO
    """
    save("像素仙人掌","pixel_cactus",palette_cactus,cac_f1,cac_f2,price=1400,desc="绿意盎然的桌面植物萌宠")

    # 15 奶茶波波
    palette_boba = {
        "bg": [0,0,0,0],
        "primary": [215, 161, 123, 255],
        "secondary": [188, 124, 85, 255],
        "accent": [121, 85, 72, 255],
        "eye": [0,0,0,255],
        "outline": [97, 67, 50, 255],
        "highlight": [255,255,255,255],
    }
    boba_f1 = """
        OPPPPPO
        OPSSSAPO
        OPEEE EPO
         OPPPPO
    """
    boba_f2 = """
        OPPPPPO
        OPSSSAPO
        OPEH  EPO
         OPPPPO
    """
    save("奶茶波波","boba_tea",palette_boba,boba_f1,boba_f2,price=1700,desc="奶茶杯与黑糖珍珠的点点萌")

    # 16 清新小羊
    palette_lamb = {
        "bg": [0,0,0,0],
        "primary": [245, 245, 245, 255],
        "secondary": [176, 190, 197, 255],
        "accent": [255, 183, 77, 255],
        "eye": [69, 90, 100, 255],
        "outline": [120, 144, 156, 255],
        "highlight": [255,255,255,255],
    }
    lamb_f1 = """
        OPPPPPO
        OPEEEPO
        OPSSAPO
         OPPPO
    """
    lamb_f2 = """
        OPPPPPO
        OPEH EPO
        OPSSAPO
         OPPPO
    """
    save("清新小羊","fresh_lamb",palette_lamb,lamb_f1,lamb_f2,price=1900,desc="白绵绵毛与温柔配色")

    upsert_pet_config(pets_cfg_path, items_meta)

if __name__ == "__main__":
    main()

