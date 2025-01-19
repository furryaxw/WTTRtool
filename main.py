import os
import re
from idlelib.pyparse import trans

location1 = "D:\Desktop\WTTRtool\langt"
location2 = "lang"
location3 = "lang_test"


# 死妈BVVD写的逆天翻译文件让我用了4个小时写读取

def read_f(f):
    # pattern = re.compile(';\n((?:[a-zA-Z0-9_\n]+/[a-zA-Z0-9_\n]+)+;)')
    pattern = re.compile('\n"([a-zA-Z0-9_\n]+(?:/[a-zA-Z0-9_\n]+)+)"')
    tr_key = []
    tr_array = []
    rows = []
    with open(f, 'r', encoding='utf-8') as file:
        try:
            f_row = str(file.readline()).split(";")
            cn_loc = f_row.index('"<Chinese>"')
        except ValueError:
            return
        reader = file.readlines()
        # reader = ''.join(reader).replace('"', '').replace('\'', '') \
        #     .replace('\\t', '').replace('\\', '')
        # reader = ';\n' + reader
    reader = ''.join(reader)
    reader = '\n' + reader
    tr_key = pattern.findall(reader)
    print(tr_key)
    reader = re.split(pattern, reader)
    for i in range(len(reader)):
        if i % 2 == 1:
            rows.append(reader[i] + reader[i + 1])
    for row in rows:
        t_row = row.split(";")
        tr_array.append(str(t_row[cn_loc]).replace("\n", "\\n").replace('\\t', '').strip('"'))
    return dict(zip(tr_key, tr_array))


def export(path, original, fname="output"):
    with open(f"{fname}.atrf", "wt", encoding='utf-8') as atr:
        atr.write("[WTTRtool Axw Translate File v1.0]\n")
    files = [entry for entry in os.listdir(path) if
             os.path.isfile(os.path.join(path, entry)) and entry.endswith(".csv")]
    for f in files:
        print(f)
        tr_ = read_f(path + '/' + f)
        otr_ = read_f(original + '/' + f)
        cache = f'[{f}]\n'
        try:
            for key in tr_.keys():
                try:
                    if tr_.get(key) != otr_.get(key) and tr_.get(key) != "" and otr_.get(key) is not None:
                        cache += f'"{key}": "{otr_.get(key)}": "{tr_.get(key)}"\n'
                except KeyError:
                    pass
        except AttributeError:
            pass
        if cache != f'[{f}]\n':
            with open(f"{fname}.atrf", "at", encoding='utf-8') as atr:
                atr.write(cache)


def write_f(f, d):
    with open(f, "r", encoding='utf-8') as f:
        f_row = str(f.readline()).split(";")
        cn_loc = f_row.index('"<Chinese>"')
        r_data = f.readlines()
    for line in range(len(r_data)):
        r_data[line] = re.findall("\"[^;]*\"", r_data[line])
        print(r_data[line])
    for trans in d:
        quit()


def inport(f, path):
    with open(f, "r", encoding='utf-8') as atr:
        art = re.findall('(\[.*\.csv\])(\n[^\[]*)?', atr.read())
    # print(art[0][1])
    for file in art:
        this_file = file[0][1:-1]
        trans = file[1].strip('\n')
        trans = trans.split('\n')
        for line in range(len(trans)):
            if trans[line] == '':
                pass
            else:
                trans[line] = re.findall('"(.*?)"', trans[line])
                trans[line][0] = trans[line][0].strip('"')
                trans[line][1] = trans[line][1].strip('"')
                trans[line][2] = trans[line][2].strip('"')
        if not path.endswith('/'):
            path = path + '/'
        write_f(path+this_file, trans)
    return


export(location1, location2)
# inport("output.atrf", location3)
# test1 = "lang_test/benchmark.csv"
test1 = "test.csv"
test2 = [['controls/controlsDamaged', '飞行操控受损', 'Flight control damaged'], ['controls/weaponControlsDamaged', '航电设备损毁，无法操控武器', 'Avionics damaged, weapon countrol systems cannot be use'], ['controls/guidanceDamaged', '航电设备损毁，无法操控制导武器', 'Avionics damaged, guidance weapon countrol systems cannot be use'], ['controls/sensorsDamaged', '传感器受损', 'Sensors damaged'], ['controls/radarDamaged', '雷达受损', 'Radar damaged'], ['controls/rwrDamaged', '红外干扰系统受损', 'IRCM damaged'], ['controls/twsDamaged', '扫描跟踪损坏', 'TWS damaged'], ['controls/opticsDamaged', '瞄准设备受损', 'Targeting optic damaged'], ['controls/targetingPodDamaged', '制导吊舱受损', 'Targeting Pod damaged'], ['controls/countermeasuresDamaged', '红外干扰系统受损', 'IRCM damaged'], ['controls/nightVisionDamaged', '航电设备损毁，无法使用夜视系统', 'Avionics damaged, NVD systems cannot be use'], ['controls/indicatorsDamaged', '航电设备损毁，多功能显示器/平视显示器无法使用', 'Avionics damaged, MFD/HUD systems cannot be use']]
# write_f(test1, test2)
# print(read_f(test1))
