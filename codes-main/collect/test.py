import os
import sys
import inspect
import re
import codecs
from datetime import datetime
import csv
from thirdparty import six
from core.settings import UNICODE_ENCODING
from core.settings import IS_WIN

def _chown(filepath):
    if not IS_WIN and os.path.exists(filepath):
        try:
            os.chown(filepath, int(os.environ.get("SUDO_UID", -1)), int(os.environ.get("SUDO_GID", -1)))
        except Exception as ex:
            print("[!] chown problem with '%s' ('%s')" % (filepath, ex))
def _fopen(filepath, mode="rb", opener=open):
    retval = opener(filepath, mode)
    if "w+" in mode:
        _chown(filepath)
    return retval
LOW_PRIORITY_INFO_KEYWORDS = ("reputation", "attacker", "spammer", "abuser", "malicious", "dnspod", "nicru", "crawler", "compromised", "bad history")
HIGH_PRIORITY_INFO_KEYWORDS = ("mass scanner", "ipinfo")
HIGH_PRIORITY_REFERENCES = ("bambenekconsulting.com", "github.com/stamparm/blackbook", "(static)", "(custom)")
trails = {}
duplicates = {}
exclude = set(['__pycache__'])
for root,dirs,filenames in os.walk("feeds",topdown=True):
    dirs[:] = [d for d in dirs if d not in exclude]
    print(filenames)
    print(root)
_ = os.path.abspath(root)
if _ not in sys.path:
    sys.path.append(_)
filenames = [_ for _ in filenames if "__init__.py" not in _]
for i in range(len(filenames)):
    filename = filenames[i]
    # try:
    module = __import__(filename.split(".py")[0])
    # except (ImportError, SyntaxError) as ex:
    #     print("[x] something went wrong during import of feed file '%s' ('%s')" % (filename, ex))
    #     continue
    print(module)
    #    以上一般没问题
    #    以下是调用模块部分测试了一部分没问题但是可能存在问题
    #    数据获取
    for name, function in inspect.getmembers(module, inspect.isfunction):
        if name == "fetch":
            url = module.__url__  # Note: to prevent "SyntaxError: can not delete variable 'module' referenced in nested scope"

            print(" [o] '%s'%s" % (url, " " * 20 if len(url) < 20 else ""))
            sys.stdout.write("[?] progress: %d/%d (%d%%)\r" % (i, len(filenames), i * 100 // len(filenames)))
            sys.stdout.flush()

            # if config.DISABLED_TRAILS_INFO_REGEX and re.search(config.DISABLED_TRAILS_INFO_REGEX,
            #                                                    getattr(module, "__info__", "")):
            #     continue

            try:
                results = function()
                for item in results.items():
                    if item[0].startswith("www.") and '/' not in item[0]:
                        item = [item[0][len("www."):], item[1]]
                    if item[0] in trails:
                        if item[0] not in duplicates:
                            duplicates[item[0]] = set((trails[item[0]][1],))
                        duplicates[item[0]].add(item[1][1])
                    if not (item[0] in trails and (
                            any(_ in item[1][0] for _ in LOW_PRIORITY_INFO_KEYWORDS) or trails[item[0]][
                        1] in HIGH_PRIORITY_REFERENCES)) or (
                            item[1][1] in HIGH_PRIORITY_REFERENCES and "history" not in item[1][0]) or any(
                            _ in item[1][0] for _ in HIGH_PRIORITY_INFO_KEYWORDS):
                        trails[item[0]] = item[1]
                if not results and not any(_ in url for _ in ("abuse.ch", "cobaltstrike")):
                    print("[x] something went wrong during remote data retrieval ('%s')" % url)
            except Exception as ex:
                print("[x] something went wrong during processing of feed file '%s' ('%s')" % (filename, ex))

    try:
        sys.modules.pop(module.__name__)
        del module
    except Exception:
        pass
    #    数据处理和储存，每一次循环获得的内容在trails变量中

for key in list(trails.keys()):
    if key not in trails:
        continue

    try:
        _key = key.decode(UNICODE_ENCODING) if isinstance(key, bytes) else key
        _key = _key.encode("idna")
        if six.PY3:
            _key = _key.decode(UNICODE_ENCODING)
        if _key != key:  # for domains with non-ASCII letters (e.g. phishing)
            trails[_key] = trails[key]
            del trails[key]
            key = _key
    except:
        pass

    if not key or re.search(r"\A(?i)\.?[a-z]+\Z", key) and not any(
            _ in trails[key][1] for _ in ("custom", "static")):
        del trails[key]
        continue
    if re.search(r"\A\d+\.\d+\.\d+\.\d+\Z", key):
        if any(_ in trails[key][0] for _ in ("parking site",
                                             "sinkhole")) and key in duplicates:  # Note: delete (e.g.) junk custom trails if static trail is a sinkhole
            del duplicates[key]
        if trails[key][0] == "malware":
            trails[key] = ("potential malware site", trails[key][1])
    if trails[key][0] == "ransomware":
        trails[key] = ("ransomware (malware)", trails[key][1])
    if key.startswith("www.") and '/' not in key:
        _ = trails[key]
        del trails[key]
        key = key[len("www."):]
        if key:
            trails[key] = _
    if '?' in key and not key.startswith('/'):
        _ = trails[key]
        del trails[key]
        key = key.split('?')[0]
        if key:
            trails[key] = _
    if '//' in key:
        _ = trails[key]
        del trails[key]
        key = key.replace('//', '/')
        trails[key] = _
    if key != key.lower():
        _ = trails[key]
        del trails[key]
        key = key.lower()
        trails[key] = _
    if key in duplicates:
        _ = trails[key]
        others = sorted(duplicates[key] - set((_[1],)))
        if others and " (+" not in _[1]:
            trails[key] = (_[0], "%s (+%s)" % (_[1], ','.join(others)))
success = False;

os.mknod(os.path.join(os.path.join(os.path.expanduser("~"), "%s" % "mytest".lower()), datetime.now().date().isoformat()+'.csv'))
try:
    if trails:
        with _fopen(os.path.join(os.path.join(os.path.expanduser("~"), "%s" % "mytest".lower()), datetime.now().date().isoformat()+'.csv'), "w+b" if six.PY2 else "w+", open if six.PY2 else codecs.open) as f:
            writer = csv.writer(f, delimiter=',', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
            for trail in trails:
                row = (trail, trails[trail][0], trails[trail][1])
                writer.writerow(row)

        success = True
except Exception as ex:
    print("[x] something went wrong during trails file write '%s' ('%s')" % (os.path.join(os.path.join(os.path.expanduser("~"), "%s" % "mytest".lower()), datetime.now().date().isoformat()+'.csv'), ex))

print("[i] update finished%s" % (40 * " "))

if success:
    print("[i] trails stored to '%s'" % os.path.join(os.path.join(os.path.expanduser("~"), "%s" % "mytest".lower()), datetime.now().date().isoformat()+'.csv'))


