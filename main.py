import os
import re
import subprocess

key_pattern = re.compile(';\n"([a-zA-Z0-9_\n]+(?:/[a-zA-Z0-9_\n]+)+)"')
checkupdate = False


def read_f(f):
    tr_array = []
    rows = []
    try:
        with open(f, 'r', encoding='utf-8') as file:
            try:
                f_row = str(file.readline()).split(';')
                cn_loc = f_row.index('"<Chinese>"')
            except ValueError:
                return -1
            reader = file.readlines()
    except FileNotFoundError:
        return -1
    reader = ''.join(reader)
    reader = ';;\n' + reader
    tr_key = key_pattern.findall(reader)
    reader = re.split(key_pattern, reader)
    for i in range(len(reader)):
        if i % 2 == 1:
            rows.append(reader[i] + reader[i + 1])
    for row in rows:
        t_row = row.split(";")
        tr_array.append(str(t_row[cn_loc]).replace("\n", "\\n").replace('\\t', '').strip('"'))
    return dict(zip(tr_key, tr_array))


def export(path, original, fname="output"):
    with open(f"{fname}.atrf", "wt", encoding='utf-8') as atr:
        atr.write("[WTTRtool Translate File v1.0 Key/Original/New]\n")
    files = [entry for entry in os.listdir(path) if
             os.path.isfile(os.path.join(path, entry)) and entry.endswith(".csv")]
    for f in files:
        tr_ = read_f(path.rstrip('\\').rstrip('/') + '/' + f)
        otr_ = read_f(original.rstrip('\\').rstrip('/') + '/' + f)
        if tr_ == -1 or otr_ == -1:
            print(f"{f}文件异常，无法比对，已跳过该文件")
            continue
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
        print(f)


def write_f(f, d):
    rows = []
    with open(f, "r", encoding='utf-8') as file:
        f_row = str(file.readline()).split(';')
        try:
            cn_loc = f_row.index('"<Chinese>"')
        except ValueError:
            return
        reader = file.readlines()

    reader = ''.join(reader)
    reader = ';;\n' + reader
    tr_key = key_pattern.findall(reader)
    tr_row = dict.fromkeys(tr_key)
    reader = re.split(key_pattern, reader)
    for i in range(len(reader)):
        if i % 2 == 1:
            rows.append(reader[i] + '"' + reader[i + 1])
    for row in rows:
        if re.search(r"\"[;\d]{2,}", row):
            t_row = re.split(key_pattern, ";\n\"" + row)[1:]
            tr_row[t_row[0]] = t_row[1][1:]
        else:
            t_row = row.split("\";\"")
            t_row[cn_loc] = t_row[cn_loc].replace("\n", "\\n").replace('\\t', '')
            tr_row[t_row[0]] = t_row[1:]

    for trans in d:
        t_trans = trans[2]
        for index in range(len(trans[2]) - 1, -1, -1):
            # if re.match(r"[^\x00-\xff]{2}", trans[2][index:index+2]):  # 全角匹配
            if re.match(r"[\u4e00-\u9fa5]{2}", trans[2][index:index + 2]):  # 汉字匹配
                t_trans = t_trans[:index + 1] + '\\t' + t_trans[index + 1:]
        if type(tr_row[trans[0]]) is not str:
            tr_row[trans[0]][cn_loc - 1] = t_trans

    data = ''
    for key in tr_row.keys():
        line = '";"'.join(tr_row[key])
        data = f"{data}\n\"{key}\";\"{line};"
    with open(f, "w", encoding='utf-8') as file:
        file.write(data)


def inport(f, path):
    with open(f, "r", encoding='utf-8') as atr:
        art = re.findall(r'(\[.*\.csv\])(\n[^\[]*)?', atr.read())
    for file in art:
        print(file[0])
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
        path = path.rstrip('\\').rstrip('/') + '/'
        write_f(path + this_file, trans)
    return


def main():
    # if checkupdate:
    #     print("正在检查更新，请稍后......")
    #     subprocess.run('git pull', shell=True)
    # inp = input('选择操作"导出"到atrf/"导入"到战争雷霆：')
    # match inp:
    #     case "导出":
    #         wt_dict = input("输入战争雷霆翻译文件目录：")
    #         export(wt_dict, "./lang_raw")
    #     case "导入":
    #         wt_dict = input("输入战争雷霆游戏翻译文件目录：")
    #         atrf = input("输入atrf翻译文件：")
    #         inport(atrf, wt_dict)
    #     case _:
    #         print("未知指令")
    export('lang', "./lang_raw")

if __name__ == "__main__":
    main()
