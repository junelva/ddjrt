import json
from itertools import combinations

'''
parse source text
'''

chapters = [None] * 81
current_chapter = 0
in_source = True

with open( "wikisource-ttc.txt", 'r', encoding="utf-8" ) as f:
    for line in f.readlines():
        if line.startswith("Chapter "):
            current_chapter += 1
            in_source = True
            chapters[current_chapter - 1] = {
                "title":line.strip(),
                "ch":[],
                "en":[]
            }
            continue
        if not line.strip():
            in_source = not in_source
            continue
        chapters[current_chapter - 1]["ch" if in_source else "en"].append(line.strip())
print(f"collected {len(chapters)} chapters")

for chapter in chapters:
    chapter["lines"] = []
    for i, line in enumerate(chapter["ch"]):
        chapter["lines"].append({
            "ch": line,
            "en": chapter["en"][i]
        })

'''
parse CEDICT
'''

definitions = {}

with open( "cedict_ts.u8", 'r', encoding="utf-8" ) as f:
    for line in f.readlines():
        if line.startswith("#"):
            continue
        
        line = line.rstrip("/\n\r")
        ch_en = line.split("/", 1)
        
        en = ch_en[1]
        if en.count("/") < 1 and ("surname" in en or "abbr." in en):
            continue
        
        en = en.replace("/", "; ")

        tradsimp_pin = ch_en[0].rstrip("] ").split("[")
        trad, simp = tradsimp_pin[0].strip().split()
        pin = tradsimp_pin[1]

        definition = {
            "traditional": trad,
            "simplified": simp,
            "pinyin": pin,
            "english": en
        }

        if trad not in definitions.keys():
            definitions[trad] = definition
        else:
            # already have this word, let's get a better definition.
            orig = definitions[trad]["english"]
            if orig.startswith("surname") or orig[0].isupper() or orig.startswith("see ") or orig.startswith("the Americas") or "surname Ji" in orig:
                definitions[trad]["english"] = definition["english"]
            elif not en.startswith("surname") and not en[0].isupper() and not en.startswith("see ") and not en.startswith("the Americas"):
                # print(trad, definitions[trad]["english"], " !!TO!! ", definition["english"])
                definitions[trad]["english"] += f". alternatively [{definition['pinyin']}]: {definition['english']}"
print(f"parsed {len(definitions.keys())} definitions")

'''
determine required word definitions
'''

required_definitions = {}

for chapter in chapters:
    chapter["words"] = []
    for line in chapter["lines"]:
        line["words"] = []
        text = line["ch"].replace("；", " ").replace("，", " ").replace("。", " ").replace("？", " ").replace("！", " ").replace("(", " ").replace(")", " ")
        segments = text.split()
        for segment in segments:
            possible_words = [segment[i: j] for i in range(len(segment)) for j in range(i + 1, len(segment) + 1)]
            for word in possible_words:
                if word not in definitions.keys():
                    continue
                
                if word not in required_definitions.keys():
                    required_definitions[word] = definitions[word]
                if word not in line["words"]:
                    line["words"].append(word)
                if definitions[word]["english"].startswith("see"):
                    # we have a definition that just says "see this word" so we add that word too
                    definition = definitions[word]["english"]
                    variant = definition.split("[")[0].split()[1].split("|")[0]
                    required_definitions[variant] = definitions[variant]
                    line["words"].append(variant)
                if "variant of" in definitions[word]["english"]:
                    # we have a variant definition, so include that definition in required words for this line.
                    definition = definitions[word]["english"]
                    variant = definition.rsplit("variant of ")[1].replace(",", " ").replace("[", " ").replace("|", " ").split(" ", 1)[0]
                    required_definitions[variant] = definitions[variant]
                    line["words"].append(variant)
                if "abbr. for" in definitions[word]["english"]:
                    # it's an abbreviation for something, so let's pull in that definition.
                    definition = definitions[word]["english"]
                    variants = definition.split("abbr.")
                    for variant in variants:
                        if variant.startswith(" for "):
                            v = variant.split("[")[0].rsplit(" ", 1)[1].split("|")[0]
                            if v in definitions.keys():
                                required_definitions[v] = definitions[v]
                                line["words"].append(v)
        
        # post-process words list so multi-character words appear inline after their individual characters
        '''
        processed_list = sorted(line["words"], \
            key=lambda x: line["ch"].index(x) + len(set(x)) + 1 + \
                [y for y in line["words"] if len(y) > 1].index(x) \
                    if (x in line["ch"] and len(x) > 1) else line["words"].index(x))
        line["words"] = processed_list
        '''

        # longest_word = 0
        # for word in line["words"]:
        #     if len(word) > longest_word:
        #         longest_word = len(word)
        
        # line["words"] = sorted(line["words"], key=lambda x: line["ch"].index(x) + len(set(x)) - 1 if x in line["ch"] else line["words"].index(x))

        debug = "The myriad things, plants and trees, are born tender and crisp"

        if line["en"].startswith(debug):
            print(line["ch"], line["words"])
        '''
        scores = []
        inserted_count = 0
        for word in line["words"]:
            if word in line["ch"] and len(word) > 1:
                score = line["ch"].index(word) + len(set(word)) + max(inserted_count * 2, 1) + len(set(word)) * 0.1
                scores.append([word, score])
                if line["en"].startswith(debug):
                    print(word, line["ch"].index(word), len(set(word)) - 1, inserted_count, score)
                inserted_count += 1
            else:
                try:
                    score = line["ch"].index(word[0]) + inserted_count
                except:
                    score = line["words"].index(word) + inserted_count
                scores.append([word, score])
                if line["en"].startswith(debug):
                    print(word, score)
            if word not in line["ch"]:
                if line["en"].startswith(debug):
                    print("inserting word not in line")
                inserted_count += 1
        line["words"] = [scored[0] for scored in sorted(scores, key=lambda sc: sc[1])]
        
        if line["en"].startswith(debug):
            print(line["ch"], line["words"])

        # if len([y for y in line["words"] if len(y) > 1]) > 2:
        #     print(line["ch"], line["en"])
        #     print(line["words"])
        '''

print("parsed every line and found possible words")

'''
save data to files
'''

for i, chapter in enumerate(chapters):
    chapters[i] = chapter["lines"]

with open("ttc.json", 'w', encoding="utf-8") as f:
    f.write(json.dumps(chapters, indent=True))
print("wrote chapters to ttc.json")

with open("definitions.json", 'w', encoding="utf-8") as f:
    f.write(json.dumps(required_definitions, indent=True))
print("wrote required definitions to definitions.json")

with open("data.js", 'w', encoding="utf-8") as f:
    text = f"chapters = {json.dumps(chapters, indent=True)}\n\ndefinitions = {json.dumps(required_definitions, indent=True)}\n"
    f.write(text)
print("wrote everything to data.js")
