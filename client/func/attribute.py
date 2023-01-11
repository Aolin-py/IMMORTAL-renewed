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
                str(attribute["HP"]) + "/" + str(attribute["HP_MAX"]) + ' ' + str(round((int(attribute['HP'])/int(attribute['HP_MAX'])*100))) + '%',
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
                str(attribute["LV"][0]),
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
        print(B,"≡", Y, "------------------------信息栏------------------------", B, "≡", N)
        print(AttributeTable)
        print(B,"≡", Y, "------------------------------------------------------", B, "≡", N)
    except Exception as e:
        print(BR, "Error! %s" % e)
        print(N)

if __name__ == "__main__":
    import time
    # 此处仅供演示，不代表最终架构
    # 此处仅供演示，不代表最终架构
    equipment = {"Head": "头盔", "Body": "胸甲", "Leg": "护膝", "Feet": "靴子", "Hand": "剑"}
    equipment_attribute = {'头盔' : 10, '胸甲' : 10, '护膝' : 10, '靴子' : 10, '剑' : 10}
    attribute = {
        "HP": 93408,
        "HP_MAX": 100000,
        "AT": equipment_attribute[equipment["Hand"]],
        "DF": equipment_attribute[equipment["Head"]]
        + equipment_attribute[equipment["Body"]]
        + equipment_attribute[equipment["Leg"]]
        + equipment_attribute[equipment["Feet"]],
        "POT": 1,
        "LV": ['宗师',100],
        "EXP": 154654,
        "EXP_MAX": 6465665463,
        "Coin": 1,
        # 以上为基本属性
    }
    name = '晓梦'
    user = 'xiao_dream'

    a = time.time()
    PrintAttribute(attribute, equipment, user, name)
    b = time.time()
    print('用时：', round(b - a, 5), '秒')
