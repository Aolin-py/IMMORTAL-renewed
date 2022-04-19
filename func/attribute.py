from prettytable import *
from color import *


def PrintAttribute(attribute, equipment, user, name):
    try:
        AttributeTable = PrettyTable()
        AttributeTable.set_style(PLAIN_COLUMNS)  # 样式为无边框
        AttributeTable.field_names = ["", user, name, " "]
        AttributeTable.add_row(
            [
                R+"「气血」",
                str(attribute["HP"]) + "/" + str(attribute["HP_MAX"]),
                B+"「头部」",
                str(equipment["Head"]),
            ]
        )
        AttributeTable.add_row(
            [
                P+"「臂力」",
                str(attribute["AT"]),
                B+"「身体」",
                str(equipment["Body"]),
            ]
        )
        AttributeTable.add_row(
            [
                G+"「潜力」",
                str(attribute["POT"]),
                B+"「腿部」",
                str(equipment["Leg"]),
            ]
        )
        AttributeTable.add_row(
            [
                G+"「境界」",
                str(attribute["LV"]),
                B+"「脚部」",
                str(equipment["Feet"]),
            ]
        )
        AttributeTable.add_row(
            [
                G+"「经验」",
                str(attribute["EXP"]) + "/" + str(attribute["EXP_MAX"]),
                B+"「手部」",
                str(equipment["Hand"]),
            ]
        )
        AttributeTable.add_row(
            [
                Y+"「金钱」",
                str(attribute["Coin"]),
                GR+"「防御」",
                str(attribute["DF"])
            ]
        )
        print(B,"≡", Y, "---------------------------------------------------", B, "≡", N)
        print(AttributeTable)
        print(B,"≡", Y, "---------------------------------------------------", B, "≡", N)
    except Exception as e:
        print(BR, "Error! %s" % e)
        print(N)

if __name__ == "__main__":
    import time
    equipment = {"Head": "黄巾", "Body": "黄金锁子甲", "Leg": "黄金护膝", "Feet": "军靴", "Hand": "倚天屠龙剑"}
    attribute = {
        "HP": 100000,
        "HP_MAX": 100000,
        "AT": equipment["Hand"],
        "DF": equipment["Head"]
        + equipment["Body"]
        + equipment["Leg"]
        + equipment["Feet"],
        "POT": 1,
        "LV": ['宗师',100],
        "EXP": 1,
        "EXP_MAX": 6465665463,
        "Coin": 1,
        # 以上为基本属性
    }
    name = '晓梦'
    user = 'xiao_dream'

    a = time.time()
    PrintAttribute(attribute, equipment, user, name)
    b = time.time()
    print('用时：', b - a, '秒')
