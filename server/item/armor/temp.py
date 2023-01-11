from color import *
import prettytable

class CArmor:
    def __init__(self, name, defensive, cost, weight, description, special):
        self.name = name
        self.defensive = defensive
        self.cost = cost
        self.weight = weight
        self.description = description
        self.special = special

    def defense(self, damage):
        return damage - self.defensive

    def __str__(self):
        ArmorTable = prettytable.PrettyTable()
        ArmorTable.set_style(prettytable.PLAIN_COLUMNS)  # 样式为无边框
        ArmorTable.field_names = ["", " ", "  ", "   "]
        ArmorTable.add_row([C + "「防御」", self.defensive, GR + "「重量」", self.weight])
        ArmorTable.add_row([Y + "「价格」", self.cost, B + "「特殊」", self.special])
        return "「" + self.name + "」" + "\n" + self.description + "\n" + ArmorTable.get_string() + N

    def GetName(self):
        return self.name

    def GetDes(self):
        return self.description

    def GetCost(self):
        return self.cost
    
    def GetWeight(self):
        return self.weight
    
    def GetSpecial(self):
        return self.special

    def GetDefensive(self):
        return self.defensive

if __name__ == "__main__":
    armor1 = CArmor(Y + "铠甲" + N, 10, 100, 10, "阿巴阿巴阿巴阿巴", "无")
    print(armor1)
    damage = 20
    print("原伤害:", damage)
    print("防御后伤害:", armor1.defense(damage))