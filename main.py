import os
import re
import git
from config import Config

key_pattern = re.compile(';\n"([a-zA-Z0-9_\n]+(?:/[a-zA-Z0-9_\n]+)+)"')


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


def wt_export(path, original, fname="output"):
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


def write_f(f, d, raw=None):
    rows = []
    if raw is None:
        raw = f
    with open(raw, "r", encoding='utf-8') as file:
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


def wt_import(f, path, use_local=False):
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
        if use_local:
            write_f(path + this_file, trans)
        else:
            write_f(path + this_file, trans, "./lang_raw/" + this_file)
    return


def main():
    default = {
        "check_update": True,
        "lang_path": 'WTTR-lang',
        "use_git": 'https://gitee.com/furryaxw/WTTR-lang.git',

        "use_auto": "None",
        "artf_path": "",
        "warthunder_path": ""
    }
    config = Config('WTTR', default)
    try:
        conf = config.read()
        check_update = conf["check_update"]
        lang_path = conf["lang_path"]
        git_url = conf["use_git"]
        wt_dict = conf["warthunder_path"]
    except KeyError:
        print("检测到更老的配置文件，正在重置......")
        config.write(default)
        conf = config.read()
        check_update = conf["check_update"]
        lang_path = conf["lang_path"]
        git_url = conf["use_git"]
        wt_dict = conf["warthunder_path"]

    if check_update:
        print("正在检查更新，请稍后......")
        try:
            if os.path.exists(lang_path):
                git.repo.Repo(lang_path).git.pull()
            else:
                git.repo.Repo.clone_from(git_url, to_path=lang_path)
        except git.exc.InvalidGitRepositoryError:
            try:
                print("更新失败，无效的git目录")
                input("按enter重试更新")
                os.remove(lang_path)
                return main()
            except PermissionError:
                print(f"无法删除目录：{lang_path}，请手动删除后重试")
                if input("输入C无视错误继续程序: ") != "C":
                    return -1
        except Exception as e:
            print("发生未知错误：" + str(e))
    while 1:
        inp = input('操作：').split(" ")
        match inp[0]:
            case "导出":
                if wt_dict == "":
                    wt_dict = input("输入战争雷霆翻译文件目录：")
                atrf_name = input("输入atrf翻译文件名（默认output）：")
                wt_export(wt_dict, "./lang_raw", atrf_name)
            case "导入":
                if wt_dict == "":
                    wt_dict = input("输入战争雷霆游戏翻译文件目录：")
                atrf_name = input("输入atrf翻译文件：")
                if input("是否使用联网语言更新（Y/n）").lower() == 'n':
                    use_local = True
                else:
                    use_local = False
                wt_import(atrf_name, wt_dict, use_local)
            case "设置":
                match inp[1]:
                    case "战雷":
                        inp_t = ' '.join(inp[2:])
                        if inp_t == "" or not os.path.exists(inp_t + "/localization.blk"):
                            print("无效的文件夹，不做任何操作")
                        else:
                            config.write({"warthunder_path": inp_t})
                            wt_dict = inp_t
                            print(f"战争雷霆文件夹已更新为{inp_t}后续使用会自动填入")
                    case "git":
                        inp_t = ''.join(inp[2:])
                        if inp_t == "":
                            git_url = "https://gitee.com/furryaxw/WTTR-lang.git"
                            print("git仓库已恢复默认")
                        elif re.match("(https?://\w+\.(com|cn|edu|hk)+(/[\w-_:@&?=+,.!/~*'%$]+)+.git|\w+/\w+$)", inp_t):
                            git_url = inp_t
                            print(f"git仓库已设置为{git_url}")
                        else:
                            print("无效的git地址，不做任何操作")
                        config.write({"use_git": git_url})
                    case _:
                        print("未知指令\n战雷/git")
            case _:
                print("未知指令\n导出/导入/设置")


if __name__ == "__main__":
    main()
