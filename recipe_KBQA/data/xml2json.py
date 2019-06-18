#! /usr/bin/env python
# -*- coding:utf-8 -*-
# File: xml2json.py
# Author: zjw
# Date: 19-5-25

from xml.parsers.expat import ParserCreate
import json
from bs4 import BeautifulSoup
import os  
import os.path  
import re


class Xml2Json:

    def is_chinese(self, uchar):
        if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
            return True
        else:
            return False

    def is_number(self, uchar):
        if uchar >= u'\u0030' and uchar <= u'\u0039':
            return True
        else:
            return False

    def is_alphabet(self, uchar):
        """判断一个unicode是否是英文字母"""
        if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
            return True
        else:
            return False

    def format_str(self, content):
        #content = unicode(content,'utf-8')
        content_str = ''
        for i in content:
            if i in {':',';','；','：','|','_',',','。','.','，','[',']','【','】','#','%','$','*','&','？','?','<','>','《','》','、','/','"','\'','(',')','（','）','=','-','{','}',' '}:
                content_str = content_str+i
            elif i == '\\':
                content_str = content_str+'/'
            elif self.is_chinese(i) or self.is_number(i) or self.is_alphabet(i):
                content_str = content_str+i
        return content_str


    def transfer(self,xml_doc):
        soup = BeautifulSoup(xml_doc, 'html.parser')
        keyword = ['uri','foodname','score','heat','author','mate','quantity','steps','tips','tags'] #关键词list
        res = "{ "
        for j in range(len(keyword)):
            res = res + "\"" + str(keyword[j]) + "\" : "  #tags
            tags = []
            info_list = []

            if keyword[j] == 'uri':
                for se in soup.find_all(keyword[j]):
                    info = se.get_text()
                    info = self.format_str(info)
                    info.replace("[","")
                    info.replace("]","")
                    info.replace("CDATA","")
                    info.replace("!","")
                    res = res + "{ \"" + str(keyword[j]) + "\" : \"" + info + "\" }, "
                
                continue

            for se in soup.find_all(keyword[j]):
                info = se.get_text()
                info = self.format_str(info)
                if keyword[j] == 'tags':
                    for tag in (info.split('    ')):
                        tag = tag.replace(" ","")
                        tag = tag.replace("\n","")
                        if tag is not "":
                            tags.append(tag)

                info = info.replace(" ","")
                info = info.replace("\n","")
                info = info.replace("\"","”") 
                info_list.append(info) #找出所有对应标签内的text组成list
            #print(info_list)

            if keyword[j] == 'tags':
                l = tags
            else:
                l = info_list

            if len(l) == 1  and (keyword[j] is not 'tags') and (keyword[j] is not 'mate') and (keyword[j] is not 'quantity'):
                res = res + "\"" + l[0] + "\" "
            
            else:
                res = res + " [ "
                for i in range(len(l)):
                    # 处理材料
                    tmp = l[i]
                    if keyword[j] == 'mate':
                        flag = 0

                        for n, c in enumerate(tmp):
                            if c >= u'\u4e00' and c <= u'\u9fa5':
                                flag = 1
                            if c == '.' :
                                if (n == 0):
                                    tmp = tmp[ (n+1) : ]
                                elif ((n < (len(tmp)-1)) and ((tmp[n-1] >= u'\u0030') and (tmp[n-1] <= u'\u0039'))):
                                    tmp = tmp[ (n+1) : ]

                            if (c == ':') or (c == '：'):
                                tmp = tmp[ (n+1) : ]

                        if (flag == 0) or tmp.replace(' ','') == '':
                            continue
                        tmp = tmp.replace('.','')

                        #tmp = re.sub(u"\\(.*?\\)|\\{.*?}|\\[.*?]", "", tmp)

                    if i is not (len(l)-1):
                        res = res + "\"" + tmp + "\", "
                    else:
                        res = res + "\"" + tmp + "\" "

                res = res + " ] "
                print(res)

            if j is not (len(keyword)-1):
                res = res + ", "

        res = res + " }\n"

        return res

if __name__ == '__main__':
    path = "food_detail_page/"
    files = os.listdir(path)  #得到文件夹下所有文件名称 
    resultlist = set()
    for xmlFile in files:
        print(xmlFile)
        if (not os.path.isdir(xmlFile)) and (xmlFile[0] is not ".") :
            xml = open( os.path.join(path,xmlFile), 'r', encoding='UTF-8').read()
            result = Xml2Json().transfer(xml)
            if result not in resultlist:
                outputfile = open("recipe.json", 'a', encoding='UTF-8')
                outputfile.write(result)
                outputfile.close()
                resultlist.add(result)


    