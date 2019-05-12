# Contains Function for extraction of Title from the URL , these modules are interlinked and help in Extraction specific to URL
def removeExtraCharacter(string):
    ret = string[0:len(string) - 2]
    return ret

# reverse a string
def reverse(text):
    rev = ''
    cnt = 0
    for i in range(len(text), -1, -1):
            rev += text[i-1]
    return rev

# Extracting Link tile from back to front , Required no of '/ ' back and '-' used to seperate words
def getLinkTitle(link):
    str = ""
    cnt = 0
    for c in reversed(link):
        if c == '/':
            cnt = cnt + 1
        if cnt == 1:
            if c == '-' or c == '/':
                str = str + ' '
            else:
                str = str + c
    return removeExtraCharacter(reverse(str))

# Extracting Link title from Back to front in case title lies 2 / back and '-' used to seperate words
def getLinkTitle2(link):
    str = ""
    cnt = 0
    for c in reversed(link):
        if c == '/':
            cnt = cnt + 1
        if cnt == 2:
            if c == '-' or c == '/':
                str = str + ' '
            else:
                str = str + c
    return removeExtraCharacter(reverse(str))
