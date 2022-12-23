import re
from Levenshtein import distance as lev

__all__ = ['censure_filter']

sensitiveness = 0.32

# from datetime import datetime

# words = ["банан", "помидор"]


d = {'щ': ['щ', 'sch'],
     'ш': ['ш', 'sh'],
     'ч': ['ч', 'ch'],
     'ж': ['ж', 'zh', '*'],
     'л': ['л', 'l', 'ji'],
     'ы': ['ы', 'bi', 'b|'],
     'ю': ['ю', 'io'],
     'я': ['я', 'ya'],
     'х': ['х', 'x', 'h', '}{'],
     'к': ['к', 'k', 'i{', '|{'],
     'ц': ['ц', 'c', 'u,'],
     'а': ['а', 'a', '@'],
     'б': ['б', '6', 'b'],
     'в': ['в', 'b', 'v'],
     'г': ['г', 'r', 'g'],
     'д': ['д', 'd'],
     'е': ['е', 'e'],
     'ё': ['ё', 'e'],
     'з': ['з', '3', 'z'],
     'и': ['и', 'u', 'i'],
     'й': ['й', 'u', 'i'],

     'м': ['м', 'm'],
     'н': ['н', 'h', 'n'],
     'о': ['о', 'o', '0'],
     'п': ['п', 'n', 'p'],
     'р': ['р', 'r', 'p'],
     'с': ['с', 'c', 's'],
     'т': ['т', 'm', 't'],
     'у': ['у', 'y', 'u'],
     'ф': ['ф', 'f'],
     'ь': ['ь', 'b'],
     'ъ': ['ъ'],
     'э': ['э', 'e']}


# читает файл в список
def read2list(file):
    # открываем файл в режиме чтения utf-8
    file = open(file, 'r', encoding='utf-8')

    # читаем все строки и удаляем переводы строк
    lines = file.readlines()
    lines = [line.rstrip('\n') for line in lines]

    file.close()

    return lines


words = read2list('censure/censure.txt')


async def clear_text(word):
    word = word.lower()
    re_not_word = r'[^\w\s]'
    word = re.sub(re_not_word, '', word)
    return word


async def remake_transcript(word):
    for key, value in d.items():
        # Проходимся по каждой букве в значении словаря. То есть по вот этим спискам ['а', 'a', '@'].
        for letter in value:
            word = word.replace(letter, key)
    return word


async def text_match(word):
    c_text = await clear_text(word)
    for filthy_language in words:
        difference = lev(c_text, filthy_language) / len(filthy_language)
        # if c_text.find(filthy_language) != -1:
        #     print(filthy_language)
        #     return True

        if difference <= sensitiveness:
            print(filthy_language)
            return True
    return False


async def censure_filter(text):
    phrase = text.split(' ')
    for word in phrase:
        transcript = await remake_transcript(word)
        if await text_match(word) or await text_match(transcript):
            text = text.replace(word, '***')
            # print('мат', word)
        # print(text_match(word))
    return text
